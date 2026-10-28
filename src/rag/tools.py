# Integrantes: Fabio Durán; Gustavo Reyes; Ezequiel Muñoz
# Objetivo: recuperar fragmentos con su parecido y generar respuestas citadas con el proveedor configurado.
# fecha_hora_creacion: 20261027_1815
# fecha_hora_modificacion: 20261027_2015

from pathlib import Path

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage

from .llm import get_chat_model
from .prompts import SYSTEM_PROMPT, USER_PROMPT
from .storage import search_with_similarity


def buscar(pregunta: str) -> list[dict]:
    """TOP_K fragmentos con texto, fuente, página y parecido coseno."""
    fragmentos = []
    for document, similarity in search_with_similarity(pregunta):
        fuente = document.metadata.get("filename") or Path(
            document.metadata.get("source", "desconocida")
        ).name
        fragmentos.append({
            "texto": document.page_content,
            "fuente": fuente,
            "pagina": document.metadata.get("page", "n/a"),
            "parecido": similarity,
        })
    return fragmentos


def responder(pregunta: str, fragmentos: list[dict]) -> str:
    """Responde citando [archivo p.N] usando solo el contexto recuperado."""
    contexto = "\n\n".join(
        f"[{i}] archivo={fragmento['fuente']} p.{fragmento['pagina']} "
        f"parecido={fragmento['parecido']:.4f}\n{fragmento['texto']}"
        for i, fragmento in enumerate(fragmentos, 1)
    )
    model = get_chat_model()
    response = model.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=USER_PROMPT.format(contexto=contexto, pregunta=pregunta)),
    ])
    if isinstance(response.content, str):
        return response.content
    return "\n".join(
        block["text"] for block in response.content
        if isinstance(block, dict) and block.get("type") == "text"
    )


def documents_from_fragments(fragmentos: list[dict]) -> list[Document]:
    """Convierte los fragmentos del estado en Document, para demos y pruebas."""
    return [
        Document(page_content=fragmento["texto"], metadata={
            "source": fragmento["fuente"], "page": fragmento["pagina"],
        })
        for fragmento in fragmentos
    ]
