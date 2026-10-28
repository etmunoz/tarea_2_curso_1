# Integrantes: Fabio Durán; Gustavo Reyes; Ezequiel Muñoz
# Objetivo: abrir una página del PDF y comprobar si una cita apunta al lugar correcto.
# fecha_hora_creacion: 20261028_1105
# fecha_hora_modificacion: 20261028_1120

"""Verifica citas contra el PDF, sin red y sin claves.

Uso desde la raíz:

    # ¿En qué páginas está esta frase? (búsqueda en todo el documento)
    uv run python scripts/cita.py --buscar "treinta días corridos"

    # ¿Está esta frase en la página que citó el agente?
    uv run python scripts/cita.py --pagina 10 --buscar "treinta días corridos"

    # ¿Aparece la palabra en el documento entero? (jurisdicciones inexistentes)
    uv run python scripts/cita.py --buscar "Argentina"

La numeración de --pagina es la impresa en el PDF (1-based), igual que
`metadata['page']` del fragmento: así la cita del agente se comprueba contra
lo que ve el lector, no contra un índice interno.

La comparación ignora mayúsculas, acentos y saltos de línea, porque el PDF
está justificado y parte las frases por la mitad.
"""

import argparse
import sys
import unicodedata
from pathlib import Path

from pypdf import PdfReader

DEFAULT_PDF = Path("docs/LEY-19628_28-AGO-1999_refundida_20261201.pdf")


def _base(caracter: str) -> str:
    """Letra sin acento; devuelve vacío para lo que no sea letra."""
    descompuesto = unicodedata.normalize("NFD", caracter)
    return "".join(
        pieza for pieza in descompuesto if unicodedata.category(pieza) != "Mn"
    )


def normalizar(texto: str) -> str:
    """Minúsculas, sin acentos y con un solo espacio: el patrón a buscar."""
    salida: list[str] = []
    espacio = False
    for caracter in texto:
        if caracter.isspace():
            espacio = True
            continue
        if espacio and salida:
            salida.append(" ")
        espacio = False
        salida.append(_base(caracter).lower())
    return "".join(salida)


def mapa_normalizado(original: str) -> tuple[str, list[int]]:
    """Como `normalizar`, pero conservando la posición de cada carácter original."""
    salida: list[str] = []
    indices: list[int] = []
    espacio = True
    for posicion, caracter in enumerate(original):
        if caracter.isspace():
            espacio = True
            continue
        if espacio and salida:
            salida.append(" ")
            indices.append(posicion)
        espacio = False
        salida.append(_base(caracter).lower())
        indices.append(posicion)
    return "".join(salida), indices


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verifica una cita contra el PDF")
    parser.add_argument("--buscar", required=True, help="Texto que se espera encontrar")
    parser.add_argument("--pagina", type=int, default=None,
                        help="Página citada (1-based, la impresa en el PDF)")
    parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF,
                        help=f"PDF del corpus (por defecto: {DEFAULT_PDF})")
    parser.add_argument("--contexto", type=int, default=160,
                        help="Caracteres de contexto a cada lado")
    args = parser.parse_args(argv)

    if not args.pdf.exists():
        print(f"No existe el PDF: {args.pdf}", file=sys.stderr)
        return 2

    lector = PdfReader(str(args.pdf))
    hojas = [hoja.extract_text() or "" for hoja in lector.pages]
    objetivo = normalizar(args.buscar)
    if not objetivo:
        print("El texto --buscar no tiene contenido.", file=sys.stderr)
        return 2

    coincidencias = [
        i + 1 for i, texto in enumerate(hojas) if objetivo in normalizar(texto)
    ]
    print(f"PDF: {args.pdf.name} ({len(hojas)} páginas)")
    print(f"Buscado: {args.buscar!r}  → {len(coincidencias)} página(s): "
          f"{', '.join(str(p) for p in coincidencias) or 'NINGUNA'}")

    if args.pagina is None:
        if len(coincidencias) == 1:
            print("Sin --pagina: esa frase solo está en una página, así que la "
                  "cita puede verificarse ahí.")
        return 0

    if not 1 <= args.pagina <= len(hojas):
        print(f"Página fuera de rango: {args.pagina}", file=sys.stderr)
        return 2

    original = hojas[args.pagina - 1]
    texto, indices = mapa_normalizado(original)
    inicio = texto.find(objetivo)
    if inicio < 0:
        print(f"VEREDICTO: la página citada ({args.pagina}) NO contiene el texto.")
        return 1

    print(f"VEREDICTO: la página citada ({args.pagina}) SÍ contiene el texto.")
    desde = indices[inicio]
    hasta = indices[inicio + len(objetivo) - 1] + 1
    izquierda = max(0, desde - args.contexto)
    derecha = min(len(original), hasta + args.contexto)
    print(f"--- contexto en p.{args.pagina} ---")
    print("…" + " ".join(original[izquierda:derecha].split()) + "…")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
