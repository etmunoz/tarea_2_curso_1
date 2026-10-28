# Integrantes: Fabio Durán; Gustavo Reyes; Ezequiel Muñoz
# Objetivo: probar conexión, inserción y búsqueda vectorial con documentos de demostración.
# fecha_hora_creacion: 20261027_1829
# fecha_hora_modificacion: 20261027_1858

"""Prueba operativa del almacenamiento configurado, sin tocar el corpus RAG."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from langchain_core.documents import Document
from redis import Redis

from scripts.demo_common import demo_parser, report_failure, validate_texts
from src.rag.config import get_settings
from src.rag.storage import get_vector_store


def main(argv: list[str] | None = None) -> int:
    parser = demo_parser("Prueba de inserción y búsqueda en FAISS o Redis")
    args = parser.parse_args(argv)
    try:
        validate_texts(args.frases, args.pregunta)
    except ValueError as exc:
        parser.error(str(exc))
    stage = "configuración"
    client = None
    try:
        settings = get_settings()
        # Un espacio de nombres independiente evita consultar o modificar el corpus real.
        prefijo = f"{settings.prefijo}_demo"
        print(f"Backend: {settings.vector_store}; prefijo de demostración: {prefijo}")
        if settings.vector_store == "redis":
            if not os.getenv("REDIS_URL", "").strip():
                print(
                    "FALLO: falta REDIS_URL. Añade REDIS_URL=redis://localhost:6379 "
                    "a .env (o la URL de tu servidor Redis con Search).", file=sys.stderr,
                )
                return 1
            stage = "PING de Redis"
            client = Redis.from_url(
                settings.redis_url, socket_connect_timeout=5, socket_timeout=10,
            )
            if not client.ping():
                raise RuntimeError("Redis no respondió al PING.")
            print("PING Redis: OK")

        stage = "creación del índice Redis" if settings.vector_store == "redis" else "creación de FAISS en memoria"
        store = get_vector_store(prefijo, in_memory=True)
        print("Índice listo (creado si no existía).")
        stage = "inserción de los documentos"
        documents = [Document(page_content=phrase, metadata={"fuente": "demo"}) for phrase in args.frases]
        # Redis sobrescribe las mismas tres claves en las ejecuciones siguientes.
        store.add_documents(documents, ids=[f"demo-{i}" for i in range(1, 4)])
        stage = "búsqueda vectorial"
        results = store.similarity_search_with_score(args.pregunta, k=2)
        if len(results) != 2:
            raise RuntimeError("La búsqueda no devolvió los dos fragmentos esperados.")
        print(f"\nPregunta: {args.pregunta}")
        print("Puntaje = distancia; menor es mejor (FAISS: L2² normalizada; Redis: coseno).")
        for i, (document, score) in enumerate(results, 1):
            if document.metadata.get("fuente") != "demo":
                raise RuntimeError("No se recuperó la metadata fuente=demo.")
            print(f"{i}. Puntaje: {float(score):.6f} | {document.page_content}")
            print(f"   Metadata: {document.metadata}")
        print(f"OK: inserción y búsqueda en {settings.vector_store} completadas.")
        return 0
    except Exception as exc:
        return report_failure(stage, exc)
    finally:
        if client is not None:
            client.close()


if __name__ == "__main__":
    raise SystemExit(main())
