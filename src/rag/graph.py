# Integrantes: Fabio Durán; Gustavo Reyes; Ezequiel Muñoz
# Objetivo: construir el grafo RAG con reformulación, búsqueda, respuesta y no-se con memoria por hilo.
# fecha_hora_creacion: 20261027_1815
# fecha_hora_modificacion: 20261028_1927

from typing import Annotated, TypedDict

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from . import tools
from .config import get_settings
from .prompts import NO_CONTEXT


class RagState(TypedDict, total=False):
    pregunta: str
    pregunta_original: str
    pregunta_reformulada: str
    fragmentos: list[dict]
    mejor_parecido: float
    respuesta: str
    messages: Annotated[list, add_messages]


def reformular(state: RagState) -> dict:
    """Prepara una consulta para recuperación y conserva la pregunta original."""
    original = state["pregunta"]
    reescrita = tools.reformular(original) or original
    return {
        "pregunta_original": original,
        "pregunta_reformulada": reescrita,
    }


def buscar(state: RagState) -> dict:
    """Embebe la pregunta, consulta get_vector_store(PREFIJO) y trae TOP_K fragmentos."""
    consulta = state.get("pregunta_reformulada") or state["pregunta"]
    fragmentos = tools.buscar(consulta)
    mejor = max((f["parecido"] for f in fragmentos), default=0.0)
    return {
        "fragmentos": fragmentos,
        "mejor_parecido": mejor,
        "messages": [HumanMessage(content=state["pregunta"])],
    }


def responder(state: RagState) -> dict:
    respuesta = tools.responder(state["pregunta"], state["fragmentos"])
    # Guarda la respuesta en la memoria del hilo para conversaciones siguientes.
    return {"respuesta": respuesta, "messages": [AIMessage(content=respuesta)]}


def no_se(state: RagState) -> dict:
    """Responde sin llamar al modelo cuando no hay evidencia suficiente."""
    return {"respuesta": NO_CONTEXT}


def evidencia(state: RagState) -> str:
    """Arista condicional: mejor_parecido >= UMBRAL decide el siguiente nodo."""
    settings = get_settings()
    return "responder" if state.get("mejor_parecido", 0.0) >= settings.umbral else "no_se"


def build_graph():
    graph = StateGraph(RagState)
    graph.add_node("reformular", reformular)
    graph.add_node("buscar", buscar)
    graph.add_node("responder", responder)
    graph.add_node("no_se", no_se)
    graph.add_edge(START, "reformular")
    graph.add_edge("reformular", "buscar")
    graph.add_conditional_edges("buscar", evidencia, {
        "responder": "responder", "no_se": "no_se",
    })
    graph.add_edge("responder", END)
    graph.add_edge("no_se", END)
    # MemorySaver conserva el estado (incluidos messages) por thread_id.
    return graph.compile(checkpointer=MemorySaver())
