# Integrantes: Fabio Durán; Gustavo Reyes; Ezequiel Muñoz
# Objetivo: comparar barrido coseno e índice vectorial con los mismos datos y embeddings cacheados.
# fecha_hora_creacion: 20261027_1920
# fecha_hora_modificacion: 20261027_1946

"""Ejecutar desde la raíz: python scripts/indice_vs_coseno.py --n 2000."""

import argparse
import hashlib
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from statistics import median
from time import perf_counter, sleep

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import faiss
import numpy as np
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_core.documents import Document
from redis import Redis
from redis.commands.search.field import NumericField, VectorField
from redis.commands.search.index_definition import IndexDefinition, IndexType

from scripts.demo_common import report_failure
from src.rag.config import ROOT, get_settings
from src.rag.embeddings import embedding_fingerprint, embedding_identity, get_embeddings

QUESTIONS = (
    "¿Cómo recupero la conexión a internet si el router no funciona?",
    "¿Cómo preparo una comida casera con verduras?",
    "¿Qué hábitos ayudan a cuidar la salud y descansar?",
    "¿Cómo organizo un viaje y reservo alojamiento?",
    "¿Cómo pruebo y depuro un programa en Python?",
)
TOPICS = (
    ("internet", ("reiniciar el router", "revisar el cable de red", "configurar el wifi", "comprobar el módem"),
     ("recuperar la conexión", "mejorar la señal", "resolver un corte de internet", "conectar el ordenador")),
    ("cocina", ("cortar verduras frescas", "cocinar arroz", "preparar una sopa", "hornear patatas"),
     ("preparar el almuerzo", "hacer una cena casera", "acompañar la ensalada", "organizar el menú")),
    ("salud", ("caminar cada día", "mantener horarios de sueño", "beber agua", "hacer ejercicios suaves"),
     ("cuidar la salud", "descansar mejor", "mantener hábitos saludables", "mejorar el bienestar")),
    ("viajes", ("reservar un hotel", "consultar los horarios del tren", "preparar el equipaje", "comparar vuelos"),
     ("organizar unas vacaciones", "planificar un viaje", "visitar otra ciudad", "preparar el itinerario")),
    ("programación", ("escribir pruebas en Python", "revisar los errores del programa", "depurar una función", "validar los datos"),
     ("corregir el código", "comprobar el software", "detectar fallos", "mejorar el programa")),
)
CONTEXTS = ("en casa", "por la mañana", "durante la semana", "con tiempo disponible", "paso a paso")


def generate_fragments(n: int) -> list[str]:
    texts = []
    for i in range(n):
        topic, actions, purposes = TOPICS[i % len(TOPICS)]
        variant = i // len(TOPICS)
        action = actions[variant % len(actions)]
        purpose = purposes[(variant // len(actions)) % len(purposes)]
        context = CONTEXTS[(variant // (len(actions) * len(purposes))) % len(CONTEXTS)]
        texts.append(f"Caso {i + 1:05d}, {topic}: conviene {action} {context} para {purpose}.")
    return texts


def sample_sizes(n: int) -> list[int]:
    return sorted({n, *(size for size in (200, 2000, 20000) if size <= n)})


def normalize(vectors: np.ndarray) -> np.ndarray:
    matrix = np.asarray(vectors, dtype=np.float32)
    if not np.isfinite(matrix).all():
        raise ValueError("Los vectores contienen números no finitos.")
    norms = np.linalg.norm(matrix, axis=-1, keepdims=True)
    if np.any(norms == 0):
        raise ValueError("No se puede calcular coseno con vectores nulos.")
    return np.ascontiguousarray(matrix / norms, dtype=np.float32)


def save_metadata(path: Path, metadata: dict) -> None:
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def embed_with_retry(embeddings, texts: list[str], query: bool):
    """Reintenta cuotas temporales, pero no insiste ante una cuota diaria agotada."""
    for attempt in range(4):
        try:
            return [embeddings.embed_query(texts[0])] if query else embeddings.embed_documents(texts)
        except Exception as exc:
            current, rate_limited, daily, delay = exc, False, False, 65.0
            while current is not None:
                rate_limited |= getattr(current, "code", None) == 429
                payload = getattr(current, "response_json", {})
                if isinstance(payload, dict):
                    for detail in payload.get("error", {}).get("details", []):
                        for violation in detail.get("violations", []):
                            quota = str(violation.get("quotaId", "")).lower()
                            daily |= "perday" in quota or "daily" in quota
                        retry = detail.get("retryDelay", "")
                        if isinstance(retry, str) and retry.endswith("s"):
                            try:
                                delay = max(1.0, min(float(retry[:-1]) + 2, 120.0))
                            except ValueError:
                                pass
                current = current.__cause__
            if not rate_limited or daily or attempt == 3:
                if rate_limited:
                    print("Cuota Google agotada o reintentos terminados; el progreso anterior queda en caché.", flush=True)
                raise
            print(f"Google limitó solicitudes (429); reintento {attempt + 1}/3 en {delay:.0f} s, sin repetir lotes guardados.", flush=True)
            sleep(delay)


def cached_vectors(embeddings, texts: list[str], *, query: bool = False,
                   directory: Path | None = None) -> np.ndarray:
    """Guarda progreso por lote; permite ampliar n sin reembebir el prefijo válido."""
    # Los archivos Gemini originales de data/ quedan intactos para su recuperación.
    directory = directory if directory is not None else ROOT / "data" / "embeddings" / embedding_fingerprint(embeddings)
    directory.mkdir(parents=True, exist_ok=True)
    stem = "preguntas_demo" if query else "vectores_demo"
    vector_file, meta_file = directory / f"{stem}.npy", directory / f"{stem}.json"
    identity = {**embedding_identity(embeddings),
                "kind": "query" if query else "document", "version": 2}
    print(f"Archivo de caché: {vector_file.relative_to(ROOT) if vector_file.is_relative_to(ROOT) else vector_file}", flush=True)
    completed, existing = 0, None
    if vector_file.exists() or meta_file.exists():
        if not (vector_file.exists() and meta_file.exists()):
            raise ValueError(f"Caché incompleta en data/{stem}; conserva o restaura ambos archivos.")
        metadata = json.loads(meta_file.read_text(encoding="utf-8"))
        if any(metadata.get(key) != value for key, value in identity.items()):
            raise ValueError(f"Caché incompatible en data/{stem}; usa una copia separada para otro modelo.")
        shared = min(len(texts), len(metadata["texts"]))
        if texts[:shared] != metadata["texts"][:shared]:
            raise ValueError(f"Los textos de data/{stem} cambiaron; no se reutiliza una caché incorrecta.")
        existing = np.load(vector_file, allow_pickle=False)
        completed = metadata["completed"]
        if (existing.ndim != 2 or not 0 <= completed <= len(existing)
                or len(metadata["texts"]) != len(existing)):
            raise ValueError(f"Caché inconsistente en data/{stem}.")
        normalize(existing[:completed])
        if completed >= len(texts):
            print(f"Caché {stem}: {len(texts)}/{len(texts)} reutilizados; 0 embeddings nuevos.", flush=True)
            return existing[:len(texts)].copy()

    print(f"Caché {stem}: {completed} reutilizados; {len(texts) - completed} embeddings nuevos.", flush=True)
    batch_size = 1 if query else 100
    for start in range(completed, len(texts), batch_size):
        end = min(start + batch_size, len(texts))
        batch = texts[start:end]
        raw = embed_with_retry(embeddings, batch, query)
        vectors = np.asarray(raw, dtype=np.float32)
        if vectors.ndim != 2 or len(vectors) != len(batch):
            raise ValueError("El proveedor no devolvió un vector por texto.")
        normalize(vectors)
        if existing is None or len(existing) < len(texts):
            expanded = np.zeros((len(texts), vectors.shape[1]), dtype=np.float32)
            if existing is not None:
                if existing.shape[1] != vectors.shape[1]:
                    raise ValueError("La dimensión del modelo cambió; no se mezcla la caché.")
                expanded[:start] = existing[:start]
            temporary = vector_file.with_suffix(".npy.tmp")
            with temporary.open("wb") as stream:
                np.save(stream, expanded, allow_pickle=False)
            temporary.replace(vector_file)
            existing = expanded
        if existing.shape[1] != vectors.shape[1]:
            raise ValueError("La dimensión del proveedor no coincide con la caché.")
        mapped = np.lib.format.open_memmap(vector_file, mode="r+")
        mapped[start:end] = vectors
        mapped.flush()
        del mapped
        existing[start:end] = vectors
        save_metadata(meta_file, {**identity, "texts": texts, "completed": end})
        print(f"  {stem}: {end}/{len(texts)} guardados.", flush=True)
    return existing[:len(texts)].copy()


def rank_cosine(vectors: np.ndarray, query: np.ndarray, top_k: int) -> list[tuple[int, float]]:
    scores = normalize(vectors) @ normalize(query)
    order = np.lexsort((np.arange(len(scores)), -scores))[:top_k]
    return [(int(i), float(scores[i])) for i in order]


class FaissComparison:
    def __init__(self, texts, vectors, embeddings, **kwargs):
        self.vectors = [vector.copy() for vector in vectors]
        index = faiss.IndexFlatIP(vectors.shape[1])
        index.add(normalize(vectors))
        documents = {str(i): Document(page_content=text, metadata={"id": i})
                     for i, text in enumerate(texts)}
        self.store = FAISS(embeddings, index, InMemoryDocstore(documents),
                           {i: str(i) for i in range(len(texts))},
                           distance_strategy=DistanceStrategy.MAX_INNER_PRODUCT)

    def manual(self, query, top_k):
        # La lista ya reside en RAM; la conversión y el cálculo sí se cronometran.
        return rank_cosine(np.asarray(self.vectors, dtype=np.float32), query, top_k)

    def indexed(self, query, top_k):
        results = self.store.similarity_search_with_score_by_vector(normalize(query).tolist(), k=top_k)
        return [(int(document.metadata["id"]), float(score)) for document, score in results]

    def close(self):
        pass


class RedisComparison:
    def __init__(self, texts, vectors, embeddings, *, redis_url, prefix):
        self.client = Redis.from_url(redis_url, socket_connect_timeout=5, socket_timeout=30)
        self.keys = []
        try:
            self.client.ping()
            # Espacio independiente, ligado al contenido y modelo; nunca borra índices ajenos.
            digest = hashlib.sha256(
                (embeddings.model + json.dumps(texts, ensure_ascii=False)).encode("utf-8")
                + np.ascontiguousarray(vectors).tobytes()
            ).hexdigest()[:16]
            self.index = f"{prefix}_coseno_{len(texts)}_{digest}"
            key_prefix = f"{self.index}:doc:"
            self.keys = [f"{key_prefix}{i}" for i in range(len(texts))]
            indexes = self.client.execute_command("FT._LIST")
            if self.index.encode() not in indexes:
                self.client.ft(self.index).create_index([
                    NumericField("id"),
                    VectorField("vector", "FLAT", {
                        "TYPE": "FLOAT32", "DIM": vectors.shape[1], "DISTANCE_METRIC": "COSINE",
                    }),
                ], definition=IndexDefinition(prefix=[key_prefix], index_type=IndexType.HASH))
            for start in range(0, len(texts), 100):
                with self.client.pipeline(transaction=False) as pipe:
                    for i in range(start, min(start + 100, len(texts))):
                        pipe.hset(self.keys[i], mapping={
                            "id": i, "text": texts[i],
                            "vector": np.asarray(vectors[i], dtype=np.float32).tobytes(),
                        })
                    pipe.execute()
            info = self.client.ft(self.index).info()
            if int(info["num_docs"]) != len(texts):
                raise ValueError("Redis no terminó de indexar todos los documentos; repite con la caché.")
            if int(info.get("hash_indexing_failures", 0)):
                raise ValueError("Redis notificó errores de indexación vectorial.")
            print(f"Índice Redis: {self.index}; HASH e índice comparten los mismos vectores.", flush=True)
        except Exception:
            self.client.close()
            raise

    def manual(self, query, top_k):
        raw = []
        # Incluye el viaje completo de todos los vectores a Python en cada consulta.
        for start in range(0, len(self.keys), 200):
            with self.client.pipeline(transaction=False) as pipe:
                for key in self.keys[start:start + 200]:
                    pipe.hget(key, "vector")
                raw.extend(pipe.execute())
        if any(vector is None for vector in raw):
            raise ValueError("Faltan vectores en los HASH de Redis.")
        vectors = np.stack([np.frombuffer(vector, dtype=np.float32) for vector in raw])
        return rank_cosine(vectors, query, top_k)

    def indexed(self, query, top_k):
        response = self.client.execute_command(
            "FT.SEARCH", self.index, f"*=>[KNN {top_k} @vector $query AS distance]",
            "PARAMS", 2, "query", np.asarray(query, dtype=np.float32).tobytes(),
            "SORTBY", "distance", "ASC", "RETURN", 2, "id", "distance",
            "LIMIT", 0, top_k, "DIALECT", 2,
        )
        results = parse_search_response(response)
        if len(results) != top_k:
            raise ValueError("El índice no devolvió el número solicitado de vecinos.")
        return results

    def close(self):
        self.client.close()


def parse_search_response(response):
    """Interpreta FT.SEARCH en RESP2 (lista plana) o RESP3 (diccionario con results).

    redis-py usa RESP3 por defecto con servidores compatibles; en RESP3 cada
    resultado trae sus campos en extra_attributes en lugar de una lista plana.
    """
    if isinstance(response, dict):
        records = [
            {b"key": item[b"id"], **item.get(b"extra_attributes", {})}
            for item in response.get(b"results", [])
        ]
    else:
        records = [
            dict(zip(response[offset + 1][::2], response[offset + 1][1::2]))
            for offset in range(1, len(response), 2)
        ]
    results = []
    for record in records:
        # RESP2 trae el id en RETURN; RESP3 lo trae también en extra_attributes.
        identifier = record.get(b"id") or record[b"key"].rsplit(b":", 1)[-1]
        results.append((int(identifier), 1 - float(record[b"distance"])))
    return results


@dataclass
class Measurement:
    n: int
    question: str
    manual: list[tuple[int, float]]
    indexed: list[tuple[int, float]]
    manual_ms: float
    indexed_ms: float

    @property
    def matches(self):
        return [i for i, _ in self.manual] == [i for i, _ in self.indexed]


def measure(backend, query, top_k: int, repeats: int):
    # Una consulta de calentamiento por método, excluida de los tiempos.
    backend.manual(query, top_k)
    backend.indexed(query, top_k)
    manual_times, indexed_times = [], []
    for repeat in range(repeats):
        # Alternar evita beneficiar sistemáticamente al método ejecutado segundo.
        methods = ("manual", "indexed") if repeat % 2 == 0 else ("indexed", "manual")
        for method in methods:
            start = perf_counter()
            result = getattr(backend, method)(query, top_k)
            elapsed = (perf_counter() - start) * 1000
            if method == "manual":
                manual_result = result
                manual_times.append(elapsed)
            else:
                indexed_result = result
                indexed_times.append(elapsed)
    return manual_result, indexed_result, median(manual_times), median(indexed_times)


def format_top(results) -> str:
    return ", ".join(f"F{i + 1:05d}:{score:.4f}" for i, score in results)


def conclusions(measurements: list[Measurement]) -> list[str]:
    sizes = sorted({row.n for row in measurements})
    summaries = {n: (median(row.manual_ms for row in measurements if row.n == n),
                     median(row.indexed_ms for row in measurements if row.n == n)) for n in sizes}
    first_a, first_b = summaries[sizes[0]]
    last_a, last_b = summaries[sizes[-1]]
    wins = sum(row.indexed_ms < row.manual_ms for row in measurements)
    matches = sum(row.matches for row in measurements)
    return [
        f"Coincidieron los top-3 ordenados en {matches}/{len(measurements)} consultas; "
        f"B fue más rápido en {wins}/{len(measurements)}. Con n={sizes[-1]}, "
        f"A/B={last_a / max(last_b, 1e-9):.2f}x (medianas).",
        (f"Al pasar de n={sizes[0]} a {sizes[-1]}, el tiempo mediano de A cambió "
         f"{last_a / max(first_a, 1e-9):.2f}x y el de B {last_b / max(first_b, 1e-9):.2f}x; "
         "los tiempos excluyen embeddings e inserción y no demuestran por sí solos complejidad asintótica.")
        if len(sizes) > 1 else
        f"Solo se midió n={sizes[0]}: A={last_a:.3f} ms y B={last_b:.3f} ms; no hay evidencia de crecimiento entre tamaños.",
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Coseno a mano frente a índice vectorial con datos idénticos")
    parser.add_argument("--n", type=int, default=2000, help="Máximo de fragmentos; incluye escalas 200, 2000 y 20000 si caben")
    parser.add_argument("--repeticiones", type=int, default=3, help="Repeticiones cronometradas por pregunta y método")
    args = parser.parse_args(argv)
    if args.n < 3 or args.repeticiones < 1:
        parser.error("--n debe ser al menos 3 y --repeticiones al menos 1.")
    stage = "configuración"
    try:
        settings = get_settings()
        if settings.vector_store == "redis" and not os.getenv("REDIS_URL", "").strip():
            print("FALLO: añade REDIS_URL=redis://localhost:16379 a .env.", file=sys.stderr)
            return 1
        sizes = sample_sizes(args.n)
        print(f"Backend: {settings.vector_store}; tamaños: {sizes}; top-k: 3; repeticiones: {args.repeticiones}", flush=True)
        print("A y B reciben el MISMO vector de pregunta y los MISMOS vectores de documentos.", flush=True)
        stage = "embeddings y caché"
        embeddings = get_embeddings()
        print(f"Modelo: {embeddings.model}", flush=True)
        texts = generate_fragments(args.n)
        vectors = cached_vectors(embeddings, texts)
        queries = cached_vectors(embeddings, list(QUESTIONS), query=True)
        print(f"Dimensión: {vectors.shape[1]}; los tamaños menores reutilizan el prefijo de la misma matriz.", flush=True)
        print("Puntajes mostrados: similitud coseno, mayor es mejor. IDs F00001... identifican fragmentos.", flush=True)
        print("Vectores A→Python: Redis = n vectores completos por red; FAISS = n vectores ya en RAM (sin red).", flush=True)
        print("Vectores B→Python = 0: solo vuelven IDs/documentos y puntajes, no embeddings. No incluye el vector de consulta enviado.", flush=True)
        print("Tiempos: mediana de repeticiones por pregunta, con calentamiento; sin embeddings ni construcción del índice.", flush=True)
        measurements = []
        for n in sizes:
            stage = f"preparación de {settings.vector_store} con n={n}"
            backend_type = RedisComparison if settings.vector_store == "redis" else FaissComparison
            backend = backend_type(texts[:n], vectors[:n], embeddings,
                                   redis_url=settings.redis_url, prefix=settings.prefijo)
            try:
                print(f"\nn={n}", flush=True)
                print("Pregunta | Top-3 A (ID:coseno) | Top-3 B (ID:coseno) | ¿Coinciden? | A ms | B ms | Vectores A→Python | Vectores B→Python", flush=True)
                print("--- | --- | --- | --- | ---: | ---: | ---: | ---:", flush=True)
                for question, query in zip(QUESTIONS, queries, strict=True):
                    stage = f"búsqueda con n={n}"
                    a, b, a_ms, b_ms = measure(backend, query, 3, args.repeticiones)
                    row = Measurement(n, question, a, b, a_ms, b_ms)
                    measurements.append(row)
                    agreement = "sí" if row.matches else "no (revisar orden/empates)"
                    print(f"{question} | {format_top(a)} | {format_top(b)} | {agreement} | {a_ms:.3f} | {b_ms:.3f} | {n} | 0", flush=True)
            finally:
                backend.close()
        print("\nCrecimiento (mediana entre las cinco preguntas):", flush=True)
        print("n | A ms | B ms | A/B", flush=True)
        print("---: | ---: | ---: | ---:", flush=True)
        for n in sizes:
            a_ms = median(row.manual_ms for row in measurements if row.n == n)
            b_ms = median(row.indexed_ms for row in measurements if row.n == n)
            print(f"{n} | {a_ms:.3f} | {b_ms:.3f} | {a_ms / max(b_ms, 1e-9):.2f}x", flush=True)
        print("\nConclusión calculada:", flush=True)
        for line in conclusions(measurements):
            print(line, flush=True)
        print("OK: comparación terminada; caché conservada para repetir sin nuevos embeddings.", flush=True)
        return 0
    except Exception as exc:
        return report_failure(stage, exc)


if __name__ == "__main__":
    raise SystemExit(main())
