# Integrantes: Fabio Durán; Gustavo Reyes; Ezequiel Muñoz
# Objetivo: conservar salidas reales de tres rutas y dos pruebas adicionales.
# fecha_hora_creacion: 20261028_1602
# fecha_hora_modificacion: 20261028_1602

"""El HTML muestra salida real capturada; no simula una terminal."""

import html
import os
from pathlib import Path
import subprocess
import sys

from bateria import PREGUNTAS


def main():
    destino = Path("entrega/grupo-N-taller2-rag/pruebas/capturas")
    casos = [("dentro", PREGUNTAS[2][2]), ("fuera", PREGUNTAS[6][2]),
             ("ambigua", PREGUNTAS[8][2]),
             ("sinonimos", "Si una persona quiere descubrir qué guardaron sobre ella, ¿qué puede pedir?"),
             ("lexico_fuera", "¿Qué establece esta ley sobre el tratamiento de datos personales en las criptomonedas?")]
    for nombre, pregunta in casos:
        comando = [sys.executable, "main.py", "rag", pregunta, "--saltos"]
        proceso = subprocess.run(comando, capture_output=True, text=True, encoding="utf-8",
                                 env={**os.environ, "PYTHONIOENCODING": "utf-8"}, timeout=600)
        if proceso.returncode:
            raise RuntimeError(f"Falló la consulta {nombre}")
        texto = f'uv run python main.py rag "{pregunta}" --saltos\n\n{proceso.stdout}'
        base = destino / f"20261028_instruccion11_{nombre}"
        base.with_suffix(".txt").write_text(texto, encoding="utf-8")
        base.with_suffix(".html").write_text(
            '<!doctype html><meta charset="utf-8"><title>Evidencia etapa 4</title>'
            '<style>body{font:19px monospace;padding:28px;background:#111827;color:#f3f4f6}'
            'pre{white-space:pre-wrap;line-height:1.5}</style>'
            '<h2>Etapa 4 — salida real capturada</h2>'
            '<p>Grupo N · 800/120 · UMBRAL=0.43 · TOP_K=4</p>'
            f'<pre>{html.escape(texto)}</pre>', encoding="utf-8")
        print(texto, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
