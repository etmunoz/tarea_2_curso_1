# Integrantes: Fabio Durán; Gustavo Reyes; Ezequiel Muñoz
# Objetivo: demostrar embeddings, similitud coseno y recuperación de una frase por pregunta.
# fecha_hora_creacion: 20261027_1829
# fecha_hora_modificacion: 20261027_1938

"""Demuestra vectores y similitud coseno con el proveedor de embeddings configurado."""

import sys
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np

from scripts.demo_common import demo_parser, report_failure, validate_texts
from src.rag.embeddings import get_embeddings


def cosine_similarity(left, right) -> float:
    a, b = np.asarray(left, dtype=float), np.asarray(right, dtype=float)
    if a.ndim != 1 or a.shape != b.shape or not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError("Los vectores deben tener igual dimensión y números finitos.")
    norm = float(np.linalg.norm(a) * np.linalg.norm(b))
    if norm == 0:
        raise ValueError("No se puede calcular el coseno de un vector nulo.")
    return float(np.clip(np.dot(a, b) / norm, -1, 1))


def main(argv: list[str] | None = None) -> int:
    parser = demo_parser("Demo de embeddings y parecido coseno (Ollama o Google)")
    args = parser.parse_args(argv)
    try:
        validate_texts(args.frases, args.pregunta)
    except ValueError as exc:
        parser.error(str(exc))
    stage = "embeddings de las frases"
    try:
        embeddings = get_embeddings()
        print(f"Modelo: {embeddings.model}")
        vectors = embeddings.embed_documents(list(args.frases))
        for i, (phrase, vector) in enumerate(zip(args.frases, vectors, strict=True), 1):
            print(f"Frase {i}: {phrase}")
            print(f"  Dimensión: {len(vector)} números; primeros 5: {vector[:5]}")

        pairs = sorted(
            ((cosine_similarity(vectors[i], vectors[j]), i, j)
             for i, j in combinations(range(3), 2)),
            key=lambda pair: pair[0], reverse=True,
        )
        print("\nPar de frases | Coseno   | Observación")
        print("-------------|----------|-----------------")
        for position, (score, i, j) in enumerate(pairs):
            marker = "MÁS PARECIDO" if position == 0 else ""
            print(f"{i + 1} - {j + 1}        | {score: .6f} | {marker}")

        stage = "embedding de la pregunta"
        query = embeddings.embed_query(args.pregunta)
        print(f"\nPregunta: {args.pregunta}")
        print(f"  Dimensión: {len(query)} números; primeros 5: {query[:5]}")
        nearest = max(
            ((cosine_similarity(query, vector), i) for i, vector in enumerate(vectors)),
            key=lambda item: item[0],
        )
        score, i = nearest
        print(f"Frase más cercana: {i + 1} (coseno={score:.6f}): {args.frases[i]}")
        print("OK: demo de embeddings completada.")
        return 0
    except Exception as exc:
        return report_failure(stage, exc)


if __name__ == "__main__":
    raise SystemExit(main())
