# Integrantes: Fabio Durán; Gustavo Reyes; Ezequiel Muñoz
# Objetivo: comprobar qué palabras de una pregunta aparecen en el corpus, para las pruebas de sinónimos y de trampa.
# fecha_hora_creacion: 20261028_1105
# fecha_hora_modificacion: 20261028_1602

"""Mide cuántas palabras de una pregunta están literalmente en el PDF.

Uso desde la raíz:
    uv run python scripts/palabras.py "¿Qué establece el principio de proporcionalidad?"
    uv run python scripts/palabras.py "pregunta" --pdf docs/otro.pdf

Sirve para dos pruebas de la etapa 4:

- **Sinónimos**: una pregunta "dentro" redactada SIN las palabras del PDF.
  Debería seguir recuperando el mismo fragmento, porque el parecido es de
  significado. Aquí se comprueba de forma verificable que las palabras no
  aparecen, y no solo se afirma.
- **Trampa**: una pregunta "fuera" que SÍ comparte palabras con el PDF.
  Aquí se mide el solape léxico que explica su parecido engañosamente alto.

Solo usa `pypdf` sobre el PDF local: sin red y sin claves.
"""

import argparse
import re
import sys
import unicodedata
from pathlib import Path

from pypdf import PdfReader

DEFAULT_PDF = Path("docs/LEY-19628_28-AGO-1999_refundida_20261201.pdf")

# Palabras vacías en español y marcas de la ley que no aportan significado.
VACIAS = {
    "que", "como", "cual", "cuales", "donde", "cuando", "quien", "quienes",
    "este", "esta", "estos", "estas", "ese", "esa", "eso", "aquel", "aquella",
    "pero", "porque", "pues", "para", "por", "con", "sin", "sobre", "desde",
    "hasta", "entre", "muy", "mas", "menos", "tambien", "solo", "cada", "todo",
    "toda", "todos", "todas", "otro", "otra", "otros", "otras", "mismo", "misma",
    "ley", "articulo", "art", "num", "n", "segun", "cual", "cualquier",
}


def normalizar(texto: str) -> str:
    """Minúsculas y sin acentos, para comparar el PDF en mayúsculas con la pregunta."""
    sin_tildes = "".join(
        letra for letra in unicodedata.normalize("NFD", texto.lower())
        if unicodedata.category(letra) != "Mn"
    )
    return sin_tildes


def palabras(texto: str) -> list[str]:
    """Tokens de 4+ caracteres que no son palabras vacías."""
    brutas = re.findall(r"[a-záéíóúñ]{4,}", normalizar(texto))
    return [palabra for palabra in brutas if palabra not in VACIAS]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Palabras de la pregunta presentes en el PDF")
    parser.add_argument("pregunta", help="Pregunta a analizar")
    parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF,
                        help=f"PDF del corpus (por defecto: {DEFAULT_PDF})")
    args = parser.parse_args(argv)

    if not args.pdf.exists():
        print(f"No existe el PDF: {args.pdf}", file=sys.stderr)
        return 2

    lector = PdfReader(str(args.pdf))
    cuerpo = normalizar(" ".join(hoja.extract_text() or "" for hoja in lector.pages))

    consulta = palabras(args.pregunta)
    if not consulta:
        print("La pregunta no tiene palabras significativas que comparar.")
        return 0

    presentes = [p for p in consulta if re.search(rf"\b{re.escape(p)}\b", cuerpo)]
    ausentes = [p for p in consulta if p not in presentes]
    cobertura = 100.0 * len(presentes) / len(consulta)

    print(f"Páginas del PDF: {len(lector.pages)}")
    print(f"Pregunta: {args.pregunta}")
    print(f"Palabras significativas analizadas: {len(consulta)}")
    print(f"  presentes en el corpus ({len(presentes)}): {', '.join(presentes) or '(ninguna)'}")
    print(f"  ausentes del corpus  ({len(ausentes)}): {', '.join(ausentes) or '(ninguna)'}")
    print(f"Solape léxico: {cobertura:.1f}%")
    print()
    if ausentes and not presentes:
        print("LECTURA: ninguno de los tokens analizados está en el documento.")
        print("  → Pregunta por sinónimos: si aun así recupera el mismo fragmento,")
        print("    el parecido está midiendo significado y no coincidencia literal.")
    elif presentes and cobertura >= 50.0:
        print("LECTURA: la pregunta comparte la mayoría de sus palabras con el PDF")
        print("  → Puede dar un parecido alto sin que el tema sea el mismo.")
        print("    El umbral por sí solo puede no separar estos casos.")
    else:
        print("LECTURA: solape léxico parcial; comparar con el parecido coseno.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
