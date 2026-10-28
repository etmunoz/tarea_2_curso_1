# Integrantes: Fabio Durán; Gustavo Reyes; Ezequiel Muñoz
# Objetivo: barrer exhaustivamente UMBRAL sobre los parecidos reales de las diez preguntas.
# fecha_hora_creacion: 20261028_0825
# fecha_hora_modificacion: 20261028_1135

"""Barrido exhaustivo de UMBRAL. Ejecutar desde la raíz:

    uv run python scripts/umbral.py

La arista `evidencia` de `src/rag/graph.py` envía a `responder` cuando
`mejor_parecido >= UMBRAL`. Como la recuperación es determinista, con los diez
parecidos fijos la ruta solo puede cambiar en esos diez valores: recorrer
0.00..1.00 con paso 0.01 no crea regímenes nuevos. Este script lista todos los
intervalos distintos (el barrido completo) y comprueba esa afirmación.

No llama al LLM: mide ruta, falsos negativos y cuántas preguntas fuera de
contexto llegarían al modelo. El contenido de esas respuestas se mide aparte,
con `scripts/bateria.py`.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.bateria import PREGUNTAS
from src.rag.config import get_settings
from src.rag.tools import buscar

# El mismo criterio que usa `evidencia()`: responder si mejor_parecido >= UMBRAL.
def ruta(mejor: float, umbral: float) -> str:
    return "responder" if mejor >= umbral else "no_se"


def main() -> int:
    parecidos = []
    ajustes = get_settings()
    configurado = ajustes.umbral
    print(f"UMBRAL configurado ahora en el proyecto (get_settings()): {configurado}")
    print(f"Parecidos recuperados (TOP_K={ajustes.top_k}, Redis, bge-m3) — medidos ahora, sin LLM:")
    print(" Nº | Tipo         | Parecido | Ruta esperada")
    print("---:|--------------|---------:|--------------")
    for numero, tipo, pregunta in PREGUNTAS:
        mejor = max((f["parecido"] for f in buscar(pregunta)), default=0.0)
        esperada = "no_se" if tipo == "fuera" else "responder"
        parecidos.append((numero, tipo, mejor, esperada))
        print(f"{numero:>3} | {tipo:<12} | {mejor:.4f} | {esperada}")

    cortes = sorted({round(p[2], 6) for p in parecidos})
    # Regímenes: [0, c1], (c1, c2], ..., (cN, 1]
    limites = [0.0] + cortes + [1.000001]
    print("\nBarrido exhaustivo de UMBRAL (todos los intervalos con ruta distinta):")
    print(" Intervalo de UMBRAL        | Ejemplo | OK | Falsos negativos | Fuera que llega al LLM")
    print("----------------------------|---------|----|------------------|------------------------")

    firmas = {}
    resumen = []
    for i in range(len(limites) - 1):
        bajo, alto = limites[i], limites[i + 1]
        # Un umbral representativo dentro del intervalo (abierto por la izquierda).
        ejemplo = round((bajo + alto) / 2, 4)
        if ejemplo > 1:
            ejemplo = 1.0
        if bajo >= 1:
            break
        correctas = 0
        falsos = []
        fuera_pasa = []
        for numero, tipo, mejor, esperada in parecidos:
            obtenida = ruta(mejor, ejemplo)
            if obtenida == esperada:
                correctas += 1
            elif esperada == "responder":
                falsos.append(numero)
            else:
                fuera_pasa.append(numero)
        etiqueta = f"[{bajo:>6.4f}, {min(alto, 1.0):>6.4f}]"
        if bajo == 0.0:
            etiqueta = f"[0.0000, {cortes[0]:.4f}]"
        elif alto > 1:
            etiqueta = f"({cortes[-1]:.4f}, 1.0000]"
        else:
            etiqueta = f"({bajo:.4f}, {min(alto, 1.0):.4f}]"
        firma = (tuple(falsos), tuple(fuera_pasa))
        firmas.setdefault(firma, etiqueta)
        resumen.append((etiqueta, ejemplo, correctas, falsos, fuera_pasa))
        print(
            f" {etiqueta:<26} | {ejemplo:>7.4f} | {correctas:>2} | "
            f"{','.join(str(n) for n in falsos) or '-':<17} | "
            f"{','.join(str(n) for n in fuera_pasa) or '-'}"
        )

    # Comprobación del barrido fino.
    vistos = set()
    for paso in range(0, 101):
        umbral = paso / 100
        vistos.add(tuple(
            (n, ruta(m, umbral)) for n, _, m, _ in parecidos
        ))
    print(f"\nBarrido fino 0.00..1.00 paso 0.01 (101 valores): {len(vistos)} configuraciones de ruta.")
    print(f"Intervalos distintos por los 10 parecidos: {len(resumen)}.")
    if len(vistos) != len(resumen):
        print("AVISO: el barrido fino encuentra más regímenes (hay cortes entre centésimas).")

    maximo = max(r[2] for r in resumen)
    print(f"\nMáximo de rutas correctas: {maximo}/10, alcanzado en:")
    for etiqueta, ejemplo, correctas, falsos, fuera_pasa in resumen:
        if correctas == maximo:
            print(f"  {etiqueta}  (p. ej. {ejemplo:.2f}) -> "
                  f"falsos negativos {falsos or '-'}, fuera que pasa {fuera_pasa or '-'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
