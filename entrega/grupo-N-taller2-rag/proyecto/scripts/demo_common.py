# Integrantes: Fabio Durán; Gustavo Reyes; Ezequiel Muñoz
# Objetivo: compartir frases, argumentos y mensajes de error seguros entre las demos.
# fecha_hora_creacion: 20261027_1829
# fecha_hora_modificacion: 20261027_1938

"""Frases y utilidades compartidas por las demostraciones."""

import argparse
import sys

DEFAULT_PHRASES = (
    "No tengo conexión a internet en mi casa.",
    "En mi hogar no puedo conectarme a la red de internet.",
    "Para preparar una tortilla hay que batir los huevos.",
)
DEFAULT_QUESTION = "no tengo internet"


def demo_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--frases", nargs=3, default=DEFAULT_PHRASES,
        metavar=("FRASE_1", "FRASE_2", "FRASE_3"),
        help="Tres frases: dos equivalentes y una de otro tema",
    )
    parser.add_argument("--pregunta", default=DEFAULT_QUESTION)
    return parser


def validate_texts(phrases: list[str] | tuple[str, ...], question: str) -> None:
    if any(not text.strip() for text in (*phrases, question)):
        raise ValueError("Las frases y la pregunta no pueden estar vacías.")


def report_failure(stage: str, exc: Exception) -> int:
    # Las excepciones de proveedores pueden incluir claves o URLs con contraseña.
    print(f"FALLO en {stage} ({type(exc).__name__}).", file=sys.stderr)
    if "maxmemory" in str(exc).lower():
        print(
            "Redis superó su límite de memoria. Libera espacio con autorización, "
            "amplía la cuota o configura REDIS_URL con otro servidor. No se borraron datos.",
            file=sys.stderr,
        )
    elif stage == "PING de Redis":
        print("Revisa REDIS_URL, las credenciales y que el servidor sea accesible.", file=sys.stderr)
    elif stage == "creación del índice Redis":
        print(
            "Se requiere Redis con Search vectorial, permisos para crear índices y "
            "un proveedor de embeddings accesible (Ollama o Google).", file=sys.stderr,
        )
    else:
        print(
            "Revisa MODEL_PROVIDER, EMBEDDING_MODEL y conectividad. Para Ollama, "
            "comprueba el servidor y los modelos; para Google, la clave y cuota. "
            "Para Redis, revisa también los permisos y el índice.", file=sys.stderr,
        )
    return 1
