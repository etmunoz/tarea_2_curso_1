# Integrantes: Fabio Durán; Gustavo Reyes; Ezequiel Muñoz
# Objetivo: centralizar el modelo, proveedor e identidad de los embeddings de Ollama o Google.
# fecha_hora_creacion: 20261027_1815
# fecha_hora_modificacion: 20261027_1938

"""Único lugar donde se lee y construye el modelo de embeddings."""

import os
import hashlib
import json

from langchain_core.embeddings import Embeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_ollama import OllamaEmbeddings

from .config import ROOT, get_settings, require_api_key
from dotenv import load_dotenv


def get_embeddings() -> Embeddings:
    load_dotenv(ROOT / ".env", override=False)
    settings = get_settings()
    model = os.getenv(
        "EMBEDDING_MODEL", "bge-m3" if settings.model_provider == "ollama" else "models/gemini-embedding-001"
    ).strip()
    if not model:
        raise ValueError("EMBEDDING_MODEL no puede estar vacío.")
    if settings.model_provider == "ollama":
        return OllamaEmbeddings(
            model=model, base_url=settings.ollama_base_url,
            client_kwargs={"timeout": settings.ollama_timeout},
        )
    return GoogleGenerativeAIEmbeddings(model=model, google_api_key=require_api_key())


def embedding_identity(embeddings: Embeddings) -> dict:
    """Identidad no secreta para evitar mezclar proveedores, modelos y servidores."""
    if isinstance(embeddings, OllamaEmbeddings):
        provider = "ollama"
    elif isinstance(embeddings, GoogleGenerativeAIEmbeddings):
        provider = "google"
    else:
        provider = f"{type(embeddings).__module__}.{type(embeddings).__qualname__}"
    return {
        "provider": provider, "model": embeddings.model,
        "base_url": str(getattr(embeddings, "base_url", None) or ""),
        "output_dimensionality": getattr(embeddings, "output_dimensionality", None),
    }


def embedding_fingerprint(embeddings: Embeddings) -> str:
    return hashlib.sha256(
        json.dumps(embedding_identity(embeddings), sort_keys=True).encode("utf-8")
    ).hexdigest()[:16]
