# Integrantes: Fabio Durán; Gustavo Reyes; Ezequiel Muñoz
# Objetivo: ejecutar la batería de diez preguntas y guardar la salida cruda como evidencia.
# fecha_hora_creacion: 20261027_2345
# fecha_hora_modificacion: 20261028_1602

"""Batería de diez preguntas (5 en contexto, 3 fuera, 2 ambiguas); sin red propia.

Uso desde la raíz:
    uv run python scripts/bateria.py [--umbral 0.65] [--top-k 5] [--solo 1,2,3]
                                     [--salida ruta.json] [--etiqueta texto]

Corre las diez preguntas de docs/preguntas.md contra el índice vigente y
graba un JSON con la ruta de nodos, el mejor parecido, los TOP_K fragmentos
y la respuesta de cada una. El umbral y el TOP_K se pasan por variable de
entorno para no tocar .env: así se comparan configuraciones bajo la misma
ingesta. --solo admite una lista de números para repetir solo un subconjunto
(con --salida obligatorio, para no pisar la evidencia de la corrida completa).
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Permite `uv run python scripts/bateria.py ...` sin instalar el proyecto.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.rag.graph import build_graph

# Set aprobado en docs/preguntas.md: 5 en contexto, 3 fuera de contexto, 2 ambiguas.
PREGUNTAS = [
    (1, "en_contexto", "¿Cuáles son los derechos que tiene el titular de los datos personales?"),
    (2, "en_contexto", "¿Qué establece el principio de proporcionalidad?"),
    (3, "en_contexto", "¿En qué casos procede la supresión de los datos personales?"),
    (4, "en_contexto", "¿Qué se entiende por anonimización?"),
    (5, "en_contexto", "¿Qué es el derecho de acceso?"),
    (6, "fuera", "¿Qué establece el GDPR de la Unión Europea sobre los encargados de tratamiento?"),
    (7, "fuera", "¿Cómo se configura la replicación en Redis Cluster?"),
    (8, "fuera", "¿Cuál es la multa máxima que aplica la autoridad de protección de datos de Argentina?"),
    (9, "ambigua", "¿Qué plazo tiene el responsable para responder al titular?"),
    (10, "ambigua", "¿Qué información debe entregar el responsable?"),
]


def ejecutar(graph, pregunta: str, thread_id: str) -> dict:
    """Recorre el grafo una vez y devuelve nodos, fragmentos y respuesta."""
    configuration = {"configurable": {"thread_id": thread_id}}
    nodos: list[str] = []
    fragmentos: list[dict] = []
    mejor = None
    respuesta = None
    for event in graph.stream({"pregunta": pregunta}, configuration, stream_mode="updates"):
        for node, update in event.items():
            nodos.append(node)
            if "mejor_parecido" in update and update["mejor_parecido"] is not None:
                mejor = update["mejor_parecido"]
            if "fragmentos" in update and update["fragmentos"] is not None:
                fragmentos = [
                    {
                        "pagina": item["pagina"],
                        "parecido": round(item["parecido"], 4),
                        "fuente": item["fuente"],
                        "largo": len(item.get("texto", "")),
                    }
                    for item in update["fragmentos"]
                ]
            if "respuesta" in update and update["respuesta"]:
                respuesta = update["respuesta"]
    return {
        "nodos": nodos,
        "mejor_parecido": mejor,
        "fragmentos": fragmentos,
        "respuesta": respuesta,
        "error": None,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Batería de diez preguntas del RAG")
    parser.add_argument("--umbral", help="UMBRAL de esta corrida (solo informativo; "
                                         "se aplica vía variable de entorno)")
    parser.add_argument("--top-k", type=int, help="TOP_K de esta corrida (se aplica "
                                                  "vía variable de entorno)")
    parser.add_argument("--solo", default="",
                        help="Números de pregunta separados por coma, p. ej. 1,2,3,4,5")
    parser.add_argument("--salida", type=Path, default=None,
                        help="Ruta del JSON de evidencia")
    parser.add_argument("--etiqueta", default="",
                        help="Texto libre para nombrar la corrida")
    args = parser.parse_args(argv)

    # Se fija ANTES de importar config para que get_settings() lo lea.
    if args.umbral:
        os.environ["UMBRAL"] = args.umbral
    if args.top_k is not None:
        if args.top_k < 1:
            parser.error("--top-k debe ser positivo")
        os.environ["TOP_K"] = str(args.top_k)

    preguntas = PREGUNTAS
    if args.solo:
        try:
            seleccion = {int(item) for item in args.solo.split(",")}
        except ValueError:
            print("Error: --solo debe ser una lista de números, p. ej. 1,2,3", flush=True)
            return 2
        preguntas = [pregunta for pregunta in PREGUNTAS if pregunta[0] in seleccion]
        if not preguntas or seleccion - {p[0] for p in PREGUNTAS}:
            print("Error: --solo debe contener números de pregunta entre 1 y 10.", flush=True)
            return 2
        if args.salida is None:
            print("Error: --solo requiere --salida para no pisar la corrida completa.",
                  flush=True)
            return 2

    from src.rag.config import get_settings
    settings = get_settings()

    graph = build_graph()
    resultados = []
    for numero, tipo, pregunta in preguntas:
        # thread_id distinto por pregunta: MemorySaver no mezcle conversaciones.
        registro = {
            "numero": numero,
            "tipo": tipo,
            "pregunta": pregunta,
        }
        try:
            registro.update(ejecutar(graph, pregunta, f"bateria-{numero}"))
        except Exception as exc:  # sin volcar excepciones: podrían traer credenciales
            registro.update({
                "nodos": [], "mejor_parecido": None, "fragmentos": [],
                "respuesta": None, "error": f"{type(exc).__name__}",
            })
        resultados.append(registro)
        print(f"[{numero:>2}] {tipo:<12} mejor={registro['mejor_parecido']} "
              f"nodos={registro['nodos']}", flush=True)

    documento = {
        "fecha": datetime.now().strftime("%Y%m%d_%H%M"),
        "etiqueta": args.etiqueta,
        "umbral": settings.umbral,
        "top_k": settings.top_k,
        "chunk_size": settings.chunk_size,
        "chunk_overlap": settings.chunk_overlap,
        "prefijo": settings.prefijo,
        "vector_store": settings.vector_store,
        "modelo": settings.modelo,
        "embedding": os.getenv("EMBEDDING_MODEL", ""),
        "resultados": resultados,
    }

    salida = args.salida
    if salida is None:
        marca = f"umbra{str(settings.umbral).replace('.', '')}"
        if args.top_k:
            marca += f"_topk{args.top_k}"
        salida = Path("entrega/grupo-N-taller2-rag/pruebas/capturas") / (
            f"bateria_{documento['fecha']}_{marca}.json"
        )
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(
        json.dumps(documento, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nEvidencia guardada en {salida}", flush=True)

    total = len(resultados)
    respondidas = sum(1 for r in resultados if r["respuesta"])
    rutas: dict[str, int] = {}
    for r in resultados:
        clave = " -> ".join(r["nodos"]) or "(sin nodos)"
        rutas[clave] = rutas.get(clave, 0) + 1
    print(f"Con respuesta: {respondidas}/{total}", flush=True)
    for ruta, cantidad in sorted(rutas.items(), key=lambda par: -par[1]):
        print(f"  {cantidad}x {ruta}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
