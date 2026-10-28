# Integrantes: Fabio Durán; Gustavo Reyes; Ezequiel Muñoz
# Objetivo: cargar PDF o TXT, dividirlos en fragmentos con solape e indexarlos en Redis o FAISS.
# fecha_hora_creacion: 20261027_1815
# fecha_hora_modificacion: 20261027_2337

"""Ingesta de PDF/TXT; ejecutar desde la raíz.

Uso: python scripts/ingest.py ruta/al/archivo.pdf [--reset]

- PDF con PyPDFLoader: un Document por página.
- Corta con RecursiveCharacterTextSplitter usando CHUNK_SIZE y CHUNK_OVERLAP
  del .env y los separadores EXPLÍCITOS de la instrucción.
- Fusiona los fragmentos menores que CHUNK_SIZE//4 con un vecino de la MISMA
  página (ver merge_small_fragments): el splitter deja colas cortas que
  compiten en la búsqueda sin traer el contenido que completan.
- Metadatos por fragmento: fuente (archivo), página y número de fragmento.
- Embebe con EMBEDDING_MODEL y guarda en get_vector_store(PREFIJO):
  Redis crea el índice PREFIJO_rag con claves PREFIJO:rag; FAISS guarda en
  data/PREFIJO/. --reset borra el índice antes de guardar; sin él, agrega.
"""

import argparse
import hashlib
import sys
from pathlib import Path

# Permite `python scripts/ingest.py ...` sin instalar el proyecto como paquete.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.rag.config import get_settings
from src.rag.storage import get_vector_store, persist_vector_store, reset_vector_store

# Separadores exigidos por la instrucción, de mayor a menor granularidad.
SEPARATORS = ["\n\n", ". ", " ", ""]


def load_documents(path: Path) -> list[Document]:
    """Un Document por página de PDF; un Document por archivo TXT."""
    if not path.exists():
        raise ValueError(f"La ruta indicada no existe: {path}")
    files = sorted(path.rglob("*")) if path.is_dir() else [path]
    documents = []
    for file in files:
        if not file.is_file():
            continue
        if file.suffix.lower() == ".pdf":
            # mode='page' entrega un Document por página; la página viene 0-based.
            for page in PyPDFLoader(str(file)).load():
                if page.page_content.strip():
                    documents.append(Document(page_content=page.page_content, metadata={
                        "source": str(file.resolve()), "filename": file.name,
                        "page": int(page.metadata.get("page", 0)) + 1,
                    }))
        elif file.suffix.lower() == ".txt":
            text = file.read_text(encoding="utf-8")
            if text.strip():
                documents.append(Document(page_content=text, metadata={
                    "source": str(file.resolve()), "filename": file.name, "page": 1,
                }))
    if not documents:
        raise ValueError(
            "No se extrajo texto de la ruta indicada. Si es un PDF escaneado, "
            "requiere OCR externo: el extractor solo lee texto embebido."
        )
    return documents


def overlap_length(left: str, right: str) -> int:
    """Mayor longitud de solape: sufijo de `left` que también es prefijo de `right`."""
    maximum = min(len(left), len(right))
    for size in range(maximum, 0, -1):
        if left[-size:] == right[:size]:
            return size
    return 0


def merge_small_fragments(
    chunks: list[Document], minimum: int, maximum: int
) -> list[Document]:
    """Funde fragmentos < `minimum` con un vecino de la MISMA página.

    El RecursiveCharacterTextSplitter corta en los separadores y deja colas
    cortas: encabezados de ítem, cabeceras de ley, restos de página. Esas
    colas compiten en la búsqueda sin traer el contenido que completan, y el
    contenido queda en el fragmento vecino sin su encabezado.

    Dos pasadas, sin cruzar nunca una página ni superar `maximum` caracteres:

    - hacia delante: si el acumulado quedó corto, se lleva el siguiente;
      así el encabezado "c) Principio de proporcionalidad" vuelve a quedar
      junto a su texto.
    - hacia atrás: lo que siga corto (normalmente el cierre de una página)
      se funde con el anterior.

    `maximum` evita que dos fragmentos ya largos se concatenen.
    """
    if minimum <= 0:
        return list(chunks)

    def can_merge(left: Document, right: Document) -> bool:
        return (
            left.metadata["page"] == right.metadata["page"]
            and len(left.page_content) + len(right.page_content) <= maximum
        )

    forward: list[Document] = []
    for chunk in chunks:
        previous = forward[-1] if forward else None
        if previous is not None and len(previous.page_content) < minimum and can_merge(
            previous, chunk
        ):
            forward.pop()
            forward.append(Document(
                page_content=previous.page_content + chunk.page_content,
                metadata=dict(previous.metadata),
            ))
        else:
            forward.append(chunk)

    merged: list[Document] = []
    for chunk in forward:
        previous = merged[-1] if merged else None
        short = len(chunk.page_content) < minimum or (
            previous is not None and len(previous.page_content) < minimum
        )
        if previous is not None and short and can_merge(previous, chunk):
            merged.pop()
            merged.append(Document(
                page_content=previous.page_content + chunk.page_content,
                metadata=dict(previous.metadata),
            ))
        else:
            merged.append(chunk)
    return merged


def describe_fragments(chunks: list[Document], merged: int, minimum: int) -> str:
    """Informe de páginas, fragmentos, tamaño medio y fragmentos 1 y 2 lado a lado."""
    lengths = [len(chunk.page_content) for chunk in chunks]
    average = sum(lengths) / len(lengths)
    lines = [
        f"Tamaño de fragmento configurado: CHUNK_SIZE del .env; solape: CHUNK_OVERLAP del .env.",
        f"Separadores: {SEPARATORS}",
        f"Fragmentos generados: {len(chunks)}",
        f"Tamaño promedio de fragmento: {average:.1f} caracteres "
        f"(mínimo {min(lengths)}, máximo {max(lengths)}).",
        f"Fragmentos fusionados por debajo de {minimum} caracteres: {merged}.",
    ]
    if len(chunks) >= 2:
        first, second = chunks[0], chunks[1]
        shared = overlap_length(first.page_content, second.page_content)
        lines += [
            "",
            "Fragmento 1 y 2 lado a lado (se resalta el texto en común):",
            f"  Fragmento 1 (página {first.metadata['page']}, {len(first.page_content)} car.)",
            f"    {first.page_content}",
            f"  Fragmento 2 (página {second.metadata['page']}, {len(second.page_content)} car.)",
            f"    {second.page_content}",
            f"  Solape real entre 1 y 2: {shared} caracteres "
            f"(CHUNK_OVERLAP del .env = {get_settings().chunk_overlap}).",
        ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingesta de PDF/TXT en Redis o FAISS")
    parser.add_argument("ruta", type=Path, help="Archivo PDF/TXT o carpeta")
    parser.add_argument(
        "--reset", action="store_true",
        help="Borra el índice del PREFIJO antes de guardar; sin él, agrega",
    )
    args = parser.parse_args(argv)

    # Fallos claros y sin rastros de pila para rutas ausentes o PDFs escaneados.
    if not args.ruta.exists():
        print(f"La ruta indicada no existe: {args.ruta}", file=sys.stderr)
        return 1

    try:
        settings = get_settings()
        pages = load_documents(args.ruta)
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap,
            separators=SEPARATORS,
        )
        chunks = splitter.split_documents(pages)
        if not chunks:
            print("No se generaron fragmentos con el CHUNK_SIZE configurado.", file=sys.stderr)
            return 1
        # Fusiona las colas cortas que deja el splitter antes de numerar.
        # El tope es 1.5·CHUNK_SIZE: permite que una cola corta se lleve un
        # fragmento casi completo (125 + 704 = 829 en la página 5) sin que dos
        # fragmentos ya llenos se concatenen.
        minimum = settings.chunk_size // 4
        maximum = int(settings.chunk_size * 1.5)
        total_before = len(chunks)
        chunks = merge_small_fragments(chunks, minimum, maximum)
        merged = total_before - len(chunks)
        # Número de fragmento 1-based; recién agregado, no forma parte de la identidad.
        for number, chunk in enumerate(chunks, 1):
            chunk.metadata["fragment"] = number

        pages_read = len({(doc.metadata["source"], doc.metadata["page"]) for doc in pages})
        print(f"Páginas leídas: {pages_read}", flush=True)

        if args.reset:
            removed = reset_vector_store(settings.prefijo)
            print(f"--reset: índice '{settings.prefijo}' "
                  f"{'borrado antes de guardar' if removed else 'no existía; nada que borrar'}.", flush=True)

        # IDs estables por contenido: repetir una ingesta idéntica no duplica fragmentos.
        unique = {}
        for chunk in chunks:
            identity = f"{chunk.metadata['source']}\0{chunk.metadata['page']}\0{chunk.page_content}"
            unique[hashlib.sha256(identity.encode("utf-8")).hexdigest()] = chunk

        store = get_vector_store(settings.prefijo)
        existing = set(getattr(store, "index_to_docstore_id", {}).values())
        pending = {key: value for key, value in unique.items() if key not in existing}
        if pending:
            store.add_documents(list(pending.values()), ids=list(pending))
            persist_vector_store(store, settings.prefijo)
        destino = "Redis" if settings.vector_store == "redis" else f"FAISS en data/{settings.prefijo}/"
        print(f"Guardado en {destino} con PREFIJO '{settings.prefijo}': "
              f"{len(pending)} fragmentos nuevos ({len(chunks) - len(pending)} ya existían).", flush=True)
        print(describe_fragments(chunks, merged, minimum), flush=True)
    except ValueError as exc:
        print(f"Error de ingesta: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(
            f"Error de ingesta ({type(exc).__name__}). Revisa el proveedor de embeddings "
            "y la conexión (Ollama local o Google con clave), y para Redis la URL y los permisos.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
