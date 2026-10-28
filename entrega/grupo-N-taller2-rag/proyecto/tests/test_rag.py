# Integrantes: Fabio Durán; Gustavo Reyes; Ezequiel Muñoz
# Objetivo: verificar configuración, grafo, ingesta y almacenamiento del RAG sin red.
# fecha_hora_creacion: 20261027_1816
# fecha_hora_modificacion: 20261028_1927

import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import Mock, patch

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

import main
from scripts.ingest import load_documents, main as ingest, merge_small_fragments
from src.rag import config, storage
from src.rag.graph import build_graph
from src.rag.prompts import NO_CONTEXT


class LocalEmbeddings(Embeddings):
    model = "test-local"

    def embed_documents(self, texts):
        return [self.embed_query(text) for text in texts]

    def embed_query(self, text):
        return [1.0, 0.0] if "gato" in text.lower() else [0.0, 1.0]


class RagTests(unittest.TestCase):
    def setUp(self):
        self.environment = patch.dict(os.environ, {}, clear=True)
        self.environment.start()
        self.addCleanup(self.environment.stop)
        for target in ("src.rag.config.load_dotenv", "src.rag.embeddings.load_dotenv"):
            mock = patch(target)
            mock.start()
            self.addCleanup(mock.stop)

    def test_defaults_and_validation(self):
        settings = config.get_settings()
        self.assertEqual(settings.vector_store, "faiss")
        self.assertEqual(settings.top_k, 4)
        for variable, value in [
            ("VECTOR_STORE", "invalid"), ("PREFIJO", "../otro"),
            ("CHUNK_SIZE", "100"), ("TOP_K", "0"), ("UMBRAL", "1.1"),
        ]:
            with self.subTest(variable=variable), patch.dict(os.environ, {variable: value}):
                with self.assertRaises(ValueError):
                    config.get_settings()

    def test_embeddings_require_key(self):
        from src.rag.embeddings import get_embeddings

        with patch.dict(os.environ, {"MODEL_PROVIDER": "google"}):
            with self.assertRaisesRegex(ValueError, "Falta GOOGLE_API_KEY"):
                get_embeddings()

    def test_diagram_does_not_use_providers(self):
        with patch("src.rag.tools.reformular") as reformular, patch(
            "src.rag.tools.buscar"
        ) as buscar, patch(
            "src.rag.tools.responder"
        ) as responder, redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main.main(["rag", "--diagrama"]), 0)
        self.assertIn("graph TD", output.getvalue())
        reformular.assert_not_called()
        buscar.assert_not_called()
        responder.assert_not_called()

    def test_graph_with_context(self):
        fragmentos = [{"texto": "El gato duerme.", "fuente": "demo.txt", "pagina": 1, "parecido": 0.9}]
        with patch("src.rag.tools.reformular", return_value="¿Qué hace el gato?"), patch(
            "src.rag.tools.buscar", return_value=fragmentos
        ) as buscar, patch(
            "src.rag.tools.responder", return_value="El gato duerme [demo.txt p.1]."
        ) as responder:
            result = build_graph().invoke(
                {"pregunta": "¿Qué hace ese felino?"},
                {"configurable": {"thread_id": "test-1"}},
            )
        self.assertEqual(result["respuesta"], "El gato duerme [demo.txt p.1].")
        self.assertEqual(result["mejor_parecido"], 0.9)
        buscar.assert_called_once_with("¿Qué hace el gato?")
        responder.assert_called_once_with("¿Qué hace ese felino?", fragmentos)

    def test_graph_without_context_and_trace(self):
        with patch("src.rag.tools.reformular", return_value="consulta reformulada"), patch(
            "src.rag.tools.buscar", return_value=[]
        ) as buscar, patch(
            "src.rag.tools.responder"
        ) as responder, redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main.main(["rag", "pregunta", "--saltos"]), 0)
        responder.assert_not_called()
        buscar.assert_called_once_with("consulta reformulada")
        self.assertIn("[salto] reformular", output.getvalue())
        self.assertIn("pregunta original: pregunta", output.getvalue())
        self.assertIn("pregunta reformulada: consulta reformulada", output.getvalue())
        self.assertIn("[salto] buscar", output.getvalue())
        self.assertIn("[salto] no_se", output.getvalue())
        self.assertIn(NO_CONTEXT, output.getvalue())

    def test_saltos_shows_fragments_similarity_and_best(self):
        fragmentos = [
            {"texto": "Texto.", "fuente": "ley.pdf", "pagina": 3, "parecido": 0.77},
            {"texto": "Otro.", "fuente": "ley.pdf", "pagina": 9, "parecido": 0.71},
        ]
        with patch("src.rag.tools.reformular", return_value="pregunta"), patch(
            "src.rag.tools.buscar", return_value=fragmentos
        ), patch(
            "src.rag.tools.responder", return_value="Respuesta citada [ley.pdf p.3]."
        ), redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main.main(["rag", "pregunta", "--saltos"]), 0)
        printed = output.getvalue()
        self.assertIn("ley.pdf p.3 parecido=0.7700", printed)
        self.assertIn("ley.pdf p.9 parecido=0.7100", printed)
        self.assertIn("mejor_parecido: 0.7700", printed)

    def test_graph_routes_to_responder_when_best_meets_threshold(self):
        fragmentos = [{"texto": "Texto.", "fuente": "ley.pdf", "pagina": 3, "parecido": 0.9}]
        with patch("src.rag.tools.reformular", return_value="pregunta"), patch(
            "src.rag.tools.buscar", return_value=fragmentos
        ), patch(
            "src.rag.tools.responder", return_value="Sí [ley.pdf p.3]."
        ) as responder, redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main.main(["rag", "pregunta", "--saltos"]), 0)
        responder.assert_called_once()
        self.assertIn("[salto] responder", output.getvalue())
        self.assertNotIn("[salto] no_se", output.getvalue())

    def test_texto_flag_shows_fragment_bodies(self):
        fragmentos = [
            {"texto": "Artículo 7°. Dato personal: cualquier información vinculada "
                      "a una persona identificable.", "fuente": "ley.pdf", "pagina": 2,
             "parecido": 0.6223},
            {"texto": "Artículo 30. Agencia de Protección de Datos.",
             "fuente": "ley.pdf", "pagina": 32, "parecido": 0.589},
        ]
        with patch("src.rag.tools.reformular", return_value="pregunta"), patch(
            "src.rag.tools.buscar", return_value=fragmentos
        ), patch(
            "src.rag.tools.responder", return_value="Respuesta."
        ), redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main.main(["rag", "pregunta", "--texto"]), 0)
        printed = output.getvalue()
        # Cada fragmento se numera y se muestra con su cuerpo completo.
        self.assertIn("fragmento 1: ley.pdf p.2 parecido=0.6223", printed)
        self.assertIn("fragmento 2: ley.pdf p.32 parecido=0.5890", printed)
        self.assertIn("Artículo 7°. Dato personal: cualquier información", printed)
        self.assertIn("Artículo 30. Agencia de Protección de Datos.", printed)
        self.assertIn("largo: ", printed)

    def test_texto_flag_is_not_implied_by_saltos(self):
        fragmentos = [
            {"texto": "Texto largo que no debe verse con --saltos.",
             "fuente": "ley.pdf", "pagina": 2, "parecido": 0.9},
        ]
        with patch("src.rag.tools.reformular", return_value="pregunta"), patch(
            "src.rag.tools.buscar", return_value=fragmentos
        ), patch(
            "src.rag.tools.responder", return_value="Respuesta."
        ), redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main.main(["rag", "pregunta", "--saltos"]), 0)
        printed = output.getvalue()
        self.assertIn("ley.pdf p.2 parecido=0.9000", printed)
        # --saltos conserva su salida corta: no imprime el cuerpo del fragmento.
        self.assertNotIn("Texto largo que no debe verse", printed)
        self.assertNotIn("texto:", printed)

    def test_memory_keeps_messages_by_thread_id(self):
        fragmentos = [{"texto": "Texto.", "fuente": "ley.pdf", "pagina": 3, "parecido": 0.9}]
        graph = build_graph()
        with patch("src.rag.tools.reformular", return_value="primera"), patch(
            "src.rag.tools.buscar", return_value=fragmentos
        ), patch(
            "src.rag.tools.responder", return_value="Primera respuesta."
        ):
            first = graph.invoke(
                {"pregunta": "Primera"}, {"configurable": {"thread_id": "hilo-A"}}
            )
        self.assertEqual(first["respuesta"], "Primera respuesta.")
        checkpoint = graph.get_state({"configurable": {"thread_id": "hilo-A"}})
        self.assertTrue(checkpoint.values.get("messages"))
        other = graph.get_state({"configurable": {"thread_id": "hilo-B"}})
        self.assertFalse(other.values.get("messages"))

    def test_faiss_ingestion_reload_threshold_and_idempotency(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(
            storage, "ROOT", Path(directory)
        ), patch.object(storage, "get_embeddings", return_value=LocalEmbeddings()):
            source = Path(directory) / "corpus.txt"
            source.write_text("El gato duerme en casa.", encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                self.assertEqual(ingest([str(source)]), 0)
                self.assertEqual(ingest([str(source)]), 0)
            store = storage.get_vector_store("etmunoz")
            self.assertEqual(store.index.ntotal, 1)
            self.assertEqual(len(storage.search_documents("gato")), 1)
            self.assertEqual(storage.search_documents("perro"), [])
            documents = storage.search_documents("gato")
            self.assertEqual(documents[0].metadata["page"], 1)
            self.assertEqual(documents[0].metadata["source"], str(source.resolve()))
            self.assertFalse(list(Path(directory).rglob("*.pkl")))

    def test_faiss_rejects_model_change_and_partial_index(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(
            storage, "ROOT", Path(directory)
        ), patch.object(storage, "get_embeddings", return_value=LocalEmbeddings()):
            store = storage.get_vector_store("equipo")
            store.add_documents([Document(page_content="gato")])
            storage.persist_vector_store(store, "equipo")
            changed = LocalEmbeddings()
            changed.model = "otro-modelo"
            with patch.object(storage, "get_embeddings", return_value=changed):
                with self.assertRaisesRegex(ValueError, "otro modelo"):
                    storage.get_vector_store("equipo")
            (Path(directory) / "data" / "equipo" / "documents.json").unlink()
            with self.assertRaisesRegex(ValueError, "incompleto"):
                storage.get_vector_store("equipo")

    def test_redis_configuration_without_server(self):
        with patch.dict(os.environ, {"VECTOR_STORE": "redis"}), patch.object(
            storage, "get_embeddings", return_value=LocalEmbeddings()
        ), patch.object(storage, "RedisVectorStore") as constructor:
            storage.get_vector_store("equipo")
        redis_config = constructor.call_args.kwargs["config"]
        self.assertEqual(redis_config.index_name, "equipo_rag")
        self.assertEqual(redis_config.key_prefix, "equipo:rag")
        self.assertEqual(redis_config.distance_metric, "COSINE")

    def test_redis_cosine_threshold(self):
        store = Mock()
        good, bad = Document(page_content="relevante"), Document(page_content="lejano")
        store.similarity_search_with_score.return_value = [(good, 0.2), (bad, 0.5)]
        # UMBRAL y TOP_K se fijan aquí a propósito: la prueba mide el FILTRO
        # (similitudes 0.8 y 0.5), no los valores por defecto de la configuración,
        # que cambian cuando la etapa 4 elige otra combinación.
        with patch.dict(os.environ, {"VECTOR_STORE": "redis", "UMBRAL": "0.58",
                                     "TOP_K": "3"}), patch.object(
            storage, "get_vector_store", return_value=store
        ):
            self.assertEqual(storage.search_documents("pregunta"), [good])
        store.similarity_search_with_score.assert_called_once_with("pregunta", k=3)

    def test_load_pdf_and_txt(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "ejemplo.txt").write_text("Texto local", encoding="utf-8")
            (root / "ejemplo.pdf").touch()
            page = Document(page_content="Texto PDF", metadata={"source": str(root / "ejemplo.pdf"), "page": 0})
            with patch("scripts.ingest.PyPDFLoader") as loader:
                loader.return_value.load.return_value = [page]
                documents = load_documents(root)
            self.assertEqual({doc.page_content for doc in documents}, {"Texto local", "Texto PDF"})
            # PyPDFLoader entrega la página 0-based; el script la expone 1-based.
            self.assertTrue(all(doc.metadata["page"] == 1 for doc in documents))
            self.assertTrue(all(doc.metadata["filename"] in {"ejemplo.txt", "ejemplo.pdf"} for doc in documents))
            self.assertEqual(loader.call_count, 1)

    def test_missing_route_and_scanned_pdf_fail_clearly(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "no_existe.pdf"
            self.assertEqual(ingest([str(missing)]), 1)
            scanned = Path(directory) / "escaneado.pdf"
            scanned.touch()
            with patch("scripts.ingest.PyPDFLoader") as loader:
                loader.return_value.load.return_value = [
                    Document(page_content="   ", metadata={"source": str(scanned), "page": 0})
                ]
                self.assertEqual(ingest([str(scanned)]), 1)

    def test_split_uses_env_separators_and_reports_overlap(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(
            storage, "ROOT", Path(directory)
        ), patch.object(storage, "get_embeddings", return_value=LocalEmbeddings()), patch.dict(
            os.environ, {"CHUNK_SIZE": "40", "CHUNK_OVERLAP": "10"}
        ):
            source = Path(directory) / "corpus.txt"
            source.write_text("Primera parte. Segunda parte. Tercera parte. Cuarta parte.", encoding="utf-8")
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(ingest([str(source)]), 0)
            printed = output.getvalue()
            self.assertIn("Páginas leídas: 1", printed)
            self.assertIn("Fragmentos generados:", printed)
            self.assertIn("Tamaño promedio de fragmento:", printed)
            self.assertIn("Solape real entre 1 y 2:", printed)
            store = storage.get_vector_store("etmunoz")
            for document in store.similarity_search("parte", k=store.index.ntotal):
                self.assertIn("fragment", document.metadata)

    def test_reset_removes_index_before_saving(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(
            storage, "ROOT", Path(directory)
        ), patch.object(storage, "get_embeddings", return_value=LocalEmbeddings()):
            source = Path(directory) / "corpus.txt"
            source.write_text("El gato duerme en casa.", encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                self.assertEqual(ingest([str(source)]), 0)
            self.assertEqual(storage.get_vector_store("etmunoz").index.ntotal, 1)
            (source).write_text("El perro corre en el parque.", encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                self.assertEqual(ingest([str(source), "--reset"]), 0)
            store = storage.get_vector_store("etmunoz")
            self.assertEqual(store.index.ntotal, 1)
            self.assertEqual(len(storage.search_documents("perro")), 1)
            self.assertEqual(storage.search_documents("gato"), [])

    def test_merge_short_fragments_keeps_heading_with_its_content(self):
        # El caso real de la página 5: el encabezado quedó solo (125 car.) y
        # su contenido en el fragmento vecino (704 car.).
        heading = Document(page_content="y cuando lo disponga la ley.\n    c) Principio de ",
                           metadata={"page": 5})
        body = Document(page_content=". Los datos personales deben limitarse a aquéllos "
                                     "que resulten necesarios, adecuados y pertinentes.",
                        metadata={"page": 5})
        merged = merge_small_fragments([heading, body], minimum=200, maximum=1200)
        self.assertEqual(len(merged), 1)
        self.assertIn("c) Principio de", merged[0].page_content)
        self.assertIn("adecuados y pertinentes", merged[0].page_content)
        self.assertEqual(merged[0].metadata["page"], 5)

    def test_merge_never_crosses_pages(self):
        short = Document(page_content="resto corto", metadata={"page": 4})
        next_page = Document(page_content="contenido de la página cinco", metadata={"page": 5})
        merged = merge_small_fragments([short, next_page], minimum=200, maximum=1200)
        self.assertEqual(len(merged), 2)

    def test_merge_respects_maximum_length(self):
        left = Document(page_content="corto", metadata={"page": 1})
        right = Document(page_content="x" * 100, metadata={"page": 1})
        merged = merge_small_fragments([left, right], minimum=200, maximum=50)
        self.assertEqual(len(merged), 2)

    def test_merge_never_drops_text(self):
        chunks = [
            Document(page_content="uno", metadata={"page": 1}),
            Document(page_content="dos", metadata={"page": 1}),
            Document(page_content="tres", metadata={"page": 2}),
        ]
        merged = merge_small_fragments(chunks, minimum=200, maximum=1000)
        texto = "".join(c.page_content for c in merged)
        for palabra in ("uno", "dos", "tres"):
            self.assertIn(palabra, texto)
        self.assertEqual(sum(len(c.page_content) for c in merged),
                         sum(len(c.page_content) for c in chunks))

    def test_merge_disabled_when_minimum_is_zero(self):
        chunks = [Document(page_content="a", metadata={"page": 1}),
                  Document(page_content="b", metadata={"page": 1})]
        self.assertEqual(merge_small_fragments(chunks, minimum=0, maximum=10), chunks)

    def test_empty_corpus_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "No se extrajo texto"):
                load_documents(Path(directory))


if __name__ == "__main__":
    unittest.main()
