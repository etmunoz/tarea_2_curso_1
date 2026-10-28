# Integrantes: Fabio Durán; Gustavo Reyes; Ezequiel Muñoz
# Objetivo: verificar las demos, sus cálculos y errores sin red ni credenciales reales.
# fecha_hora_creacion: 20261027_1832
# fecha_hora_modificacion: 20261027_1858

import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import Mock, patch

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from scripts import demo_embeddings, test_storage
from scripts.demo_common import DEFAULT_PHRASES, report_failure
from src.rag import storage


class DemoEmbeddings(Embeddings):
    model = "local-demo-test"

    def embed_query(self, text):
        return [1.0, 0.1, 0.0, 0.0, 0.0] if "internet" in text else [0.0, 0.0, 1.0, 0.0, 0.0]

    def embed_documents(self, texts):
        return [self.embed_query(text) for text in texts]


class DemoTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch.dict(os.environ, {}, clear=True))
        self.enterContext(patch("src.rag.config.load_dotenv"))

    def test_cosine_similarity(self):
        self.assertAlmostEqual(demo_embeddings.cosine_similarity([1, 0], [1, 0]), 1)
        self.assertAlmostEqual(demo_embeddings.cosine_similarity([1, 0], [0, 1]), 0)
        self.assertAlmostEqual(demo_embeddings.cosine_similarity([1, 0], [-1, 0]), -1)
        for left, right in [([0, 0], [1, 0]), ([1], [1, 2]), ([float("nan")], [1])]:
            with self.assertRaises(ValueError):
                demo_embeddings.cosine_similarity(left, right)

    def test_embeddings_output_and_ranking(self):
        with patch.object(demo_embeddings, "get_embeddings", return_value=DemoEmbeddings()), redirect_stdout(
            io.StringIO()
        ) as output:
            self.assertEqual(demo_embeddings.main([]), 0)
        text = output.getvalue()
        self.assertEqual(text.count("Dimensión: 5 números; primeros 5:"), 4)
        self.assertIn("1 - 2        |  1.000000 | MÁS PARECIDO", text)
        self.assertIn("Frase más cercana: 1", text)
        self.assertIn("OK:", text)

    def test_custom_arguments(self):
        embeddings = Mock(wraps=DemoEmbeddings())
        with patch.object(demo_embeddings, "get_embeddings", return_value=embeddings), redirect_stdout(io.StringIO()):
            self.assertEqual(demo_embeddings.main([
                "--frases", "internet uno", "internet dos", "cocina", "--pregunta", "internet",
            ]), 0)
        embeddings.embed_documents.assert_called_once_with(["internet uno", "internet dos", "cocina"])
        embeddings.embed_query.assert_called_once_with("internet")

    def test_faiss_demo_is_in_memory(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(
            storage, "ROOT", Path(directory)
        ), patch.object(storage, "get_embeddings", return_value=DemoEmbeddings()), redirect_stdout(
            io.StringIO()
        ) as output:
            # Un índice incompleto persistido no debe afectar a la demo en memoria.
            index = Path(directory) / "data" / "etmunoz_demo"
            index.mkdir(parents=True)
            (index / "index.faiss").write_bytes(b"no cargar")
            self.assertEqual(test_storage.main([]), 0)
            self.assertEqual((index / "index.faiss").read_bytes(), b"no cargar")
            self.assertFalse((index / "documents.json").exists())
        self.assertIn("OK: inserción y búsqueda en faiss", output.getvalue())
        self.assertEqual(output.getvalue().count("Metadata: {'fuente': 'demo'}"), 2)

    def test_redis_missing_url_is_actionable(self):
        with patch.dict(os.environ, {"VECTOR_STORE": "redis"}), patch.object(
            test_storage, "get_vector_store"
        ) as factory, redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()) as errors:
            self.assertEqual(test_storage.main([]), 1)
        factory.assert_not_called()
        self.assertIn("REDIS_URL=redis://localhost:6379", errors.getvalue())
        self.assertIn("FALLO", errors.getvalue())

    def test_redis_ping_documents_search_and_cleanup(self):
        store = Mock()
        store.similarity_search_with_score.return_value = [
            (Document(page_content=phrase, metadata={"fuente": "demo"}), score)
            for phrase, score in zip(DEFAULT_PHRASES[:2], [0.1, 0.2])
        ]
        with patch.dict(os.environ, {"VECTOR_STORE": "redis", "REDIS_URL": "redis://localhost:6379"}), patch.object(
            test_storage.Redis, "from_url"
        ) as connect, patch.object(test_storage, "get_vector_store", return_value=store) as factory, redirect_stdout(
            io.StringIO()
        ) as output:
            self.assertEqual(test_storage.main([]), 0)
        connect.return_value.ping.assert_called_once()
        connect.return_value.close.assert_called_once()
        factory.assert_called_once_with("etmunoz_demo", in_memory=True)
        documents = store.add_documents.call_args.args[0]
        self.assertEqual([doc.page_content for doc in documents], list(DEFAULT_PHRASES))
        self.assertTrue(all(doc.metadata == {"fuente": "demo"} for doc in documents))
        store.similarity_search_with_score.assert_called_once_with("no tengo internet", k=2)
        self.assertIn("OK: inserción y búsqueda en redis", output.getvalue())

    def test_errors_do_not_expose_secrets(self):
        with patch.object(demo_embeddings, "get_embeddings", side_effect=RuntimeError("secret-api-key")), redirect_stdout(
            io.StringIO()
        ), redirect_stderr(io.StringIO()) as errors:
            self.assertEqual(demo_embeddings.main([]), 1)
        self.assertNotIn("secret-api-key", errors.getvalue())
        self.assertIn("FALLO", errors.getvalue())

    def test_redis_memory_quota_message(self):
        with redirect_stderr(io.StringIO()) as errors:
            self.assertEqual(report_failure("creación del índice Redis", RuntimeError("used memory > maxmemory")), 1)
        self.assertIn("límite de memoria", errors.getvalue())
        self.assertIn("No se borraron datos", errors.getvalue())


if __name__ == "__main__":
    unittest.main()
