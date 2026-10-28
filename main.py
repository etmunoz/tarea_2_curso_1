# Integrantes: Fabio Durán; Gustavo Reyes; Ezequiel Muñoz
# Objetivo: ejecutar el agente RAG y sus opciones de trazado y diagrama desde la raíz.
# fecha_hora_creacion: 20261027_1815
# fecha_hora_modificacion: 20261027_2130

"""Ejecutar desde la raíz: python main.py rag 'pregunta'."""

import argparse
import sys

from src.rag.graph import build_graph


def _indentar(texto: str, prefijo: str = "      ") -> str:
    """Sangría uniforme para que el texto del fragmento no se pierda en la salida."""
    return "\n".join(prefijo + linea for linea in texto.splitlines())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Agentes RAG con LangGraph")
    parser.add_argument("agente", choices=["rag"])
    parser.add_argument("pregunta", nargs="?")
    parser.add_argument("--saltos", action="store_true", help="Imprime nodos recorridos y fragmentos")
    parser.add_argument(
        "--texto", action="store_true",
        help="Imprime el texto completo de cada fragmento del TOP_K (para revisar umbral)",
    )
    parser.add_argument("--diagrama", action="store_true", help="Imprime Mermaid sin ejecutar")
    parser.add_argument("--thread", default="default", help="thread_id de la memoria conversacional")
    args = parser.parse_args(argv)
    if not args.diagrama and not (args.pregunta and args.pregunta.strip()):
        parser.error("Se requiere una pregunta salvo con --diagrama.")
    graph = build_graph()
    if args.diagrama:
        print(graph.get_graph().draw_mermaid())
        return 0
    # thread_id separa las conversaciones dentro de MemorySaver.
    configuration = {"configurable": {"thread_id": args.thread}}
    try:
        for event in graph.stream(
            {"pregunta": args.pregunta}, configuration, stream_mode="updates"
        ):
            for node, update in event.items():
                if args.saltos:
                    print(f"[salto] {node}")
                if "mejor_parecido" in update and args.saltos:
                    print(f"  mejor_parecido: {update['mejor_parecido']:.4f}")
                if "fragmentos" in update and (args.saltos or args.texto):
                    for position, item in enumerate(update["fragmentos"], start=1):
                        print(
                            f"  fragmento {position}: {item['fuente']} p.{item['pagina']} "
                            f"parecido={item['parecido']:.4f}"
                        )
                        if args.texto:
                            # Texto íntegro del fragmento, para juzgar el umbral a ojo.
                            cuerpo = item["texto"].strip()
                            print(f"    inicio: {cuerpo[:80]!r}")
                            print(f"    largo: {len(cuerpo)} caracteres")
                            print("    texto:")
                            print(_indentar(cuerpo))
                if "respuesta" in update:
                    print(update["respuesta"])
    except Exception as exc:
        # No imprimir excepciones de proveedores: podrían contener URLs o credenciales.
        if isinstance(exc, ValueError) and str(exc).startswith((
            "Falta GOOGLE_API_KEY", "VECTOR_STORE", "PREFIJO", "Se requiere", "TOP_K",
            "EMBEDDING_MODEL", "Índice FAISS", "El índice usa otro", "MODEL_PROVIDER", "MODELO", "OLLAMA",
        )):
            print(f"Error: {exc}", file=sys.stderr)
        else:
            print(
                "Error al consultar el RAG. Revisa la ingesta, la configuración, "
                "el acceso a los modelos y la conexión al proveedor.", file=sys.stderr,
            )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
