# Integrantes: Fabio Durán; Gustavo Reyes; Ezequiel Muñoz
# Objetivo: seleccionar Redis o FAISS, persistir índices y recuperar documentos por similitud.
# fecha_hora_creacion: 20261027_1815
# fecha_hora_modificacion: 20261027_2015

"""Almacenamiento intercambiable. FAISS persiste sin deserializar pickle."""

import json
import shutil

import faiss
from redis import Redis as RedisClient
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore
from langchain_redis import RedisConfig, RedisVectorStore

from .config import ROOT, get_settings, validate_prefix
from .embeddings import embedding_identity, get_embeddings


def get_vector_store(prefijo: str, *, in_memory: bool = False) -> VectorStore:
    """Obtiene el backend; in_memory evita cargar índices FAISS persistidos."""
    validate_prefix(prefijo)
    settings = get_settings()
    embeddings = get_embeddings()
    if settings.vector_store == "redis":
        return RedisVectorStore(
            embeddings=embeddings,
            config=RedisConfig(
                index_name=f"{prefijo}_rag",
                key_prefix=f"{prefijo}:rag",
                redis_url=settings.redis_url,
                distance_metric="COSINE",
                metadata_schema=[
                    {"name": "source", "type": "text"},
                    {"name": "page", "type": "numeric"},
                    {"name": "fragment", "type": "numeric"},
                ],
            ),
        )

    directory = ROOT / "data" / prefijo
    index_file, metadata_file = directory / "index.faiss", directory / "documents.json"
    if not in_memory and index_file.exists() != metadata_file.exists():
        raise ValueError("Índice FAISS incompleto. Restaura sus dos archivos o usa otro PREFIJO.")
    if not in_memory and index_file.exists():
        payload = json.loads(metadata_file.read_text(encoding="utf-8"))
        if payload["embedding_model"] != embeddings.model:
            raise ValueError("El índice usa otro modelo de embeddings. Usa otro PREFIJO y reingesta.")
        if "embedding_identity" in payload and payload["embedding_identity"] != embedding_identity(embeddings):
            raise ValueError("El índice usa otro modelo o proveedor de embeddings. Usa otro PREFIJO y reingesta.")
        index = faiss.read_index(str(index_file))
        documents = {key: Document(**value) for key, value in payload["documents"].items()}
        mapping = {int(key): value for key, value in payload["mapping"].items()}
        if index.ntotal != len(mapping) or not set(mapping.values()) <= documents.keys():
            raise ValueError("Índice FAISS y documentos inconsistentes.")
    else:
        dimension = len(embeddings.embed_query("dimensión del índice"))
        index, documents, mapping = faiss.IndexFlatL2(dimension), {}, {}
    return FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=InMemoryDocstore(documents),
        index_to_docstore_id=mapping,
        normalize_L2=True,
    )


def reset_vector_store(prefijo: str) -> bool:
    """Borra el índice del prefijo. Devuelve True si había algo que borrar.

    Redis elimina el índice y sus claves con ese prefijo; FAISS elimina la
    carpeta data/PREFIJO/. No toca otros prefijos ni volúmenes.
    """
    validate_prefix(prefijo)
    settings = get_settings()
    if settings.vector_store == "redis":
        client = RedisClient.from_url(settings.redis_url, socket_connect_timeout=5, socket_timeout=30)
        try:
            client.ping()
            index_name = f"{prefijo}_rag"
            key_prefix = f"{prefijo}:rag"
            indexes = client.execute_command("FT._LIST")
            existed = index_name.encode() in indexes
            if existed:
                # DD borra los HASH asociados junto con el índice.
                try:
                    client.execute_command("FT.DROPINDEX", index_name, "DD")
                except Exception:
                    client.execute_command("FT.DROPINDEX", index_name)
                    for key in client.scan_iter(match=f"{key_prefix}:*"):
                        client.delete(key)
            else:
                for key in client.scan_iter(match=f"{key_prefix}:*"):
                    client.delete(key)
            return existed
        finally:
            client.close()

    directory = ROOT / "data" / prefijo
    if not directory.exists():
        return False
    for name in ("index.faiss", "documents.json"):
        (directory / name).unlink(missing_ok=True)
    shutil.rmtree(directory, ignore_errors=True)
    return True


def persist_vector_store(store: VectorStore, prefijo: str) -> None:
    """Redis persiste en el servidor; FAISS guarda vectores y documentos JSON."""
    validate_prefix(prefijo)
    if not isinstance(store, FAISS):
        return
    directory = ROOT / "data" / prefijo
    directory.mkdir(parents=True, exist_ok=True)
    documents = {}
    for key in store.index_to_docstore_id.values():
        document = store.docstore.search(key)
        if not isinstance(document, Document):
            raise ValueError(f"Documento ausente del índice: {key}")
        documents[key] = document.model_dump(mode="json")
    payload = {
        "embedding_model": store.embeddings.model,
        "embedding_identity": embedding_identity(store.embeddings),
        "mapping": store.index_to_docstore_id,
        "documents": documents,
    }
    faiss.write_index(store.index, str(directory / "index.faiss"))
    (directory / "documents.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def search_with_similarity(question: str) -> list[tuple[Document, float]]:
    """TOP_K fragmentos con su similitud coseno, sin filtrar por UMBRAL.

    La decisión de aceptar o rechazar la evidencia la toma el grafo con
    `mejor_parecido >= UMBRAL`, no el almacenamiento.
    """
    settings = get_settings()
    store = get_vector_store(settings.prefijo)
    results = store.similarity_search_with_score(question, k=settings.top_k)
    scored = []
    for document, distance in results:
        # FAISS: distancia L2 al cuadrado sobre vectores normalizados.
        # Redis: distancia coseno. Ambos se convierten a similitud coseno.
        similarity = 1 - float(distance) / 2 if isinstance(store, FAISS) else 1 - float(distance)
        scored.append((document, similarity))
    return scored


def search_documents(question: str) -> list[Document]:
    """Fragmentos por encima de UMBRAL; conservado para las demos existentes."""
    settings = get_settings()
    return [document for document, similarity in search_with_similarity(question)
            if similarity >= settings.umbral]
