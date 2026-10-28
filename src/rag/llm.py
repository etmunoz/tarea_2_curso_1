# Integrantes: Fabio Durán; Gustavo Reyes; Ezequiel Muñoz
# Objetivo: construir el modelo de chat configurado sin exigir claves para Ollama local.
# fecha_hora_creacion: 20261027_1938
# fecha_hora_modificacion: 20261027_1938

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama

from .config import get_settings, require_api_key


def get_chat_model() -> BaseChatModel:
    settings = get_settings()
    if settings.model_provider == "ollama":
        return ChatOllama(
            model=settings.modelo, base_url=settings.ollama_base_url,
            temperature=0, reasoning=False, num_ctx=settings.ollama_num_ctx,
            num_predict=settings.ollama_num_predict,
            client_kwargs={"timeout": settings.ollama_timeout},
        )
    return ChatGoogleGenerativeAI(
        model=settings.modelo, google_api_key=require_api_key(), temperature=0,
    )
