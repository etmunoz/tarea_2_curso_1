# Integrantes: Fabio Durán; Gustavo Reyes; Ezequiel Muñoz
# Objetivo: medir si dos frases con las mismas palabras pero distinto sentido salen menos parecidas que dos de igual significado.
# fecha_hora_creacion: 20261028_0919
# fecha_hora_modificacion: 20261028_0919

"""Prueba de `instrucciones/Instruccion_08.txt`. Ejecutar desde la raíz:

    uv run python scripts/sentido.py

Embebe las cuatro frases en UNA sola llamada (mismo modelo, mismo lote) y
compara dos pares:

  * control  — dos frases de IGUAL significado con palabras distintas;
  * objetivo — dos frases con las MISMAS palabras y sentidos distintos.

La instrucción pide que el coseno del par objetivo sea MENOR que el del
control. Si no ocurre, se anota igual: es un hallazgo válido.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.demo_embeddings import cosine_similarity
from src.rag.embeddings import get_embeddings

# Control: las dos dicen lo mismo (el banco dejó de operar) con palabras distintas.
DEFAULT_IGUALES = (
    "El banco cerró sus puertas al público.",
    "El banco dejó de operar.",
)
# Objetivo: misma palabra clave, dos sentidos distintos (institución / asiento).
DEFAULT_DISTINTOS = (
    "El banco cerró.",
    "Me senté en el banco.",
)


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Coseno entre pares de igual y distinto significado")
    ap.add_argument("--iguales", nargs=2, default=DEFAULT_IGUALES, metavar=("A1", "A2"),
                    help="Dos frases con el mismo significado")
    ap.add_argument("--distintos", nargs=2, default=DEFAULT_DISTINTOS, metavar=("B1", "B2"),
                    help="Dos frases con las mismas palabras y distinto sentido")
    return ap


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    etiquetas = ["A1", "A2", "B1", "B2"]
    textos = list(args.iguales) + list(args.distintos)
    if any(not t.strip() for t in textos):
        print("Las cuatro frases deben ser no vacías.", file=sys.stderr)
        return 1
    try:
        embeddings = get_embeddings()
        vectors = embeddings.embed_documents(textos)
        print(f"Modelo: {embeddings.model}  (dimensión {len(vectors[0])})")
        print("\nFrases de IGUAL significado (control):")
        print(f"  A1: {textos[0]}")
        print(f"  A2: {textos[1]}")
        print("\nFrases con las MISMAS palabras pero DISTINTO sentido (objetivo):")
        print(f"  B1: {textos[2]}")
        print(f"  B2: {textos[3]}")

        pares = [
            (0, 1, "igual significado (control)"),
            (2, 3, "mismo léxico, distinto sentido (objetivo)"),
            (0, 2, "cruce A1-B1"),
            (0, 3, "cruce A1-B2"),
            (1, 2, "cruce A2-B1"),
            (1, 3, "cruce A2-B2"),
        ]
        print("\nPar        | Coseno   | Tipo")
        print("-----------|----------|----------------------------------")
        resultados = {}
        for i, j, tipo in pares:
            score = cosine_similarity(vectors[i], vectors[j])
            resultados[(i, j)] = score
            print(f"{etiquetas[i]} - {etiquetas[j]}    | {score: .6f} | {tipo}")

        control = resultados[(0, 1)]
        objetivo = resultados[(2, 3)]
        delta = control - objetivo
        print("\nVeredicto:")
        print(f"  control  (A1-A2, igual significado)   = {control:.6f}")
        print(f"  objetivo (B1-B2, distinto sentido)    = {objetivo:.6f}")
        print(f"  control - objetivo                    = {delta:+.6f}")
        if objetivo < control:
            print("  ¿Objetivo MENOR que control? SÍ — se cumple lo esperado.")
        else:
            print("  ¿Objetivo MENOR que control? NO — hallazgo anotado: el par con")
            print("  las mismas palabras y distinto sentido no quedó por debajo.")
        print("OK: prueba de significado completada.")
        return 0
    except Exception as exc:
        # Las excepciones de proveedores pueden incluir claves o URLs con contraseña.
        print(f"FALLO en embeddings ({type(exc).__name__}). Revisa "
              f"MODEL_PROVIDER, EMBEDDING_MODEL y conectividad.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
