# Integrantes: Fabio Durán; Gustavo Reyes; Ezequiel Muñoz
# Objetivo: cargar y validar la configuración compartida sin incluir secretos en el código.
# fecha_hora_creacion: 20261027_1815
# fecha_hora_modificacion: 20261028_1602

"""Configuración compartida, relativa a la raíz del proyecto."""

import os
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    vector_store: str
    redis_url: str
    modelo: str
    prefijo: str
    chunk_size: int
    chunk_overlap: int
    top_k: int
    umbral: float
    model_provider: str
    ollama_base_url: str
    ollama_timeout: float
    ollama_num_ctx: int
    ollama_num_predict: int


def validate_prefix(prefijo: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_-]+", prefijo):
        raise ValueError("PREFIJO solo admite letras ASCII, números, guiones y guiones bajos.")
    return prefijo


def get_settings() -> Settings:
    load_dotenv(ROOT / ".env", override=False)
    provider = os.getenv("MODEL_PROVIDER", "ollama").strip().lower()
    if provider not in {"ollama", "google"}:
        raise ValueError("MODEL_PROVIDER debe ser ollama o google.")
    settings = Settings(
        vector_store=os.getenv("VECTOR_STORE", "faiss").strip().lower(),
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
        modelo=os.getenv("MODELO", "qwen3:8b" if provider == "ollama" else "gemini-3.5-flash-lite").strip(),
        prefijo=validate_prefix(os.getenv("PREFIJO", "etmunoz")),
        chunk_size=int(os.getenv("CHUNK_SIZE", "800")),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "120")),
        top_k=int(os.getenv("TOP_K", "4")),
        umbral=float(os.getenv("UMBRAL", "0.43")),
        model_provider=provider,
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").strip().rstrip("/"),
        ollama_timeout=float(os.getenv("OLLAMA_TIMEOUT", "300")),
        ollama_num_ctx=int(os.getenv("OLLAMA_NUM_CTX", "4096")),
        ollama_num_predict=int(os.getenv("OLLAMA_NUM_PREDICT", "512")),
    )
    if settings.vector_store not in {"faiss", "redis"}:
        raise ValueError("VECTOR_STORE debe ser faiss o redis.")
    if not 0 <= settings.chunk_overlap < settings.chunk_size:
        raise ValueError("Se requiere 0 <= CHUNK_OVERLAP < CHUNK_SIZE.")
    if settings.top_k < 1 or not 0 <= settings.umbral <= 1:
        raise ValueError("TOP_K debe ser positivo y UMBRAL debe estar entre 0 y 1.")
    if not settings.modelo:
        raise ValueError("MODELO no puede estar vacío.")
    endpoint = urlsplit(settings.ollama_base_url)
    if provider == "ollama" and (
        endpoint.scheme not in {"http", "https"} or not endpoint.netloc
        or settings.ollama_timeout <= 0 or settings.ollama_num_ctx < 1
        or settings.ollama_num_predict < 1
    ):
        raise ValueError("OLLAMA requiere una URL HTTP válida, timeout y límites de contexto/salida positivos.")
    return settings


def require_api_key() -> str:
    key = os.getenv("GOOGLE_API_KEY", "").strip()
    if not key:
        raise ValueError("Falta GOOGLE_API_KEY. Copia .env.example a .env y completa la clave.")
    return key
