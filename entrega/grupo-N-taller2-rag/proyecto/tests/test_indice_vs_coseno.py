# Integrantes: Fabio Durán; Gustavo Reyes; Ezequiel Muñoz
# Objetivo: verificar caché, igualdad de datos, rankings y conclusiones del benchmark sin red.
# fecha_hora_creacion: 20261027_1920
# fecha_hora_modificacion: 20261027_1946

import hashlib
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import numpy as np
from langchain_core.embeddings import Embeddings

from scripts import indice_vs_coseno as demo


class LocalEmbeddings(Embeddings):
    model = "test-local"
    output_dimensionality = None

    def __init__(self):
        self.documents = []
        self.queries = []

    @staticmethod
    def vector(text):
        return (np.frombuffer(hashlib.sha256(text.encode()).digest()[:8], dtype=np.uint8).astype(float) + 1).tolist()

    def embed_documents(self, texts):
        self.documents.extend(texts)
        return [self.vector(text) for text in texts]

    def embed_query(self, text):
        self.queries.append(text)
        return self.vector(text)


class IndexCosineTests(unittest.TestCase):
    def test_sizes_and_deterministic_corpus(self):
        self.assertEqual(demo.sample_sizes(2000), [200, 2000])
        self.assertEqual(demo.sample_sizes(20000), [200, 2000, 20000])
        self.assertEqual(demo.sample_sizes(500), [200, 500])
        self.assertEqual(demo.sample_sizes(10), [10])
        texts = demo.generate_fragments(2000)
        self.assertEqual(len(set(texts)), 2000)
        self.assertEqual(texts[:200], demo.generate_fragments(200))
        self.assertTrue(all(topic[0] in texts[i] for i, topic in enumerate(demo.TOPICS)))

    def test_document_cache_reuse_and_extension(self):
        embeddings = LocalEmbeddings()
        with tempfile.TemporaryDirectory() as directory, redirect_stdout(io.StringIO()):
            path = Path(directory)
            first = demo.cached_vectors(embeddings, demo.generate_fragments(105), directory=path)
            second = demo.cached_vectors(embeddings, demo.generate_fragments(50), directory=path)
            extended = demo.cached_vectors(embeddings, demo.generate_fragments(205), directory=path)
            self.assertEqual(len(embeddings.documents), 205)
            np.testing.assert_array_equal(first[:50], second)
            np.testing.assert_array_equal(first, extended[:105])
            np.testing.assert_array_equal(np.load(path / "vectores_demo.npy", allow_pickle=False), extended)

    def test_query_cache_reuses_all_questions(self):
        embeddings = LocalEmbeddings()
        with tempfile.TemporaryDirectory() as directory, redirect_stdout(io.StringIO()):
            path = Path(directory)
            demo.cached_vectors(embeddings, list(demo.QUESTIONS), query=True, directory=path)
            demo.cached_vectors(embeddings, list(demo.QUESTIONS), query=True, directory=path)
            self.assertEqual(embeddings.queries, list(demo.QUESTIONS))
            self.assertEqual(embeddings.documents, [])

    def test_cache_rejects_model_and_text_changes(self):
        embeddings = LocalEmbeddings()
        with tempfile.TemporaryDirectory() as directory, redirect_stdout(io.StringIO()):
            path = Path(directory)
            texts = demo.generate_fragments(3)
            demo.cached_vectors(embeddings, texts, directory=path)
            with self.assertRaisesRegex(ValueError, "textos"):
                demo.cached_vectors(embeddings, ["otro texto", *texts[1:]], directory=path)
            embeddings.model = "otro-modelo"
            with self.assertRaisesRegex(ValueError, "incompatible"):
                demo.cached_vectors(embeddings, texts, directory=path)
            self.assertEqual(len(embeddings.documents), 3)

    def test_cache_resumes_after_failed_batch(self):
        embeddings = LocalEmbeddings()
        original = embeddings.embed_documents
        calls = 0

        def fail_second(texts):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise RuntimeError("fallo simulado")
            return original(texts)

        with tempfile.TemporaryDirectory() as directory, redirect_stdout(io.StringIO()):
            path = Path(directory)
            with patch.object(embeddings, "embed_documents", side_effect=fail_second):
                with self.assertRaises(RuntimeError):
                    demo.cached_vectors(embeddings, demo.generate_fragments(150), directory=path)
            result = demo.cached_vectors(embeddings, demo.generate_fragments(150), directory=path)
            self.assertEqual(len(result), 150)
            self.assertEqual(len(embeddings.documents), 150)

    def test_zero_and_nonfinite_vectors_are_rejected(self):
        for vectors in (np.zeros((2, 3)), np.array([[float("nan"), 1]])):
            with self.assertRaises(ValueError):
                demo.normalize(vectors)

    def test_temporary_quota_retries_but_daily_quota_does_not(self):
        class QuotaError(Exception):
            code = 429

        embeddings = LocalEmbeddings()
        temporary = QuotaError()
        temporary.response_json = {"error": {"details": [{"retryDelay": "1s"}]}}
        with patch.object(embeddings, "embed_documents", side_effect=[temporary, [[1, 2]]]) as embed, patch.object(
            demo, "sleep"
        ) as wait, redirect_stdout(io.StringIO()):
            self.assertEqual(demo.embed_with_retry(embeddings, ["texto"], False), [[1, 2]])
        self.assertEqual(embed.call_count, 2)
        wait.assert_called_once_with(3.0)
        daily = QuotaError()
        daily.response_json = {"error": {"details": [{"violations": [{"quotaId": "EmbeddingsPerDay"}]}]}}
        with patch.object(embeddings, "embed_documents", side_effect=daily) as embed, patch.object(
            demo, "sleep"
        ) as wait, redirect_stdout(io.StringIO()):
            with self.assertRaises(QuotaError):
                demo.embed_with_retry(embeddings, ["texto"], False)
        self.assertEqual(embed.call_count, 1)
        wait.assert_not_called()

    def test_faiss_and_manual_use_same_vectors_without_embedding_again(self):
        embeddings = LocalEmbeddings()
        vectors = np.array([[1, 0], [0.8, 0.6], [0, 1], [-1, 0]], dtype=np.float32)
        query = np.array([1, 0], dtype=np.float32)
        backend = demo.FaissComparison(["uno", "dos", "tres", "cuatro"], vectors, embeddings)
        a, b = backend.manual(query, 3), backend.indexed(query, 3)
        self.assertEqual([i for i, _ in a], [0, 1, 2])
        self.assertEqual([i for i, _ in b], [0, 1, 2])
        np.testing.assert_allclose([score for _, score in a], [score for _, score in b], atol=1e-6)
        self.assertEqual(embeddings.documents, [])
        self.assertEqual(embeddings.queries, [])

    def test_redis_manual_loads_all_vectors_and_knn_returns_no_vectors(self):
        backend = demo.RedisComparison.__new__(demo.RedisComparison)
        backend.client = MagicMock()
        backend.keys = ["key-0", "key-1", "key-2"]
        backend.index = "test-index"
        vectors = np.array([[1, 0], [0.8, 0.6], [0, 1]], dtype=np.float32)
        pipeline = backend.client.pipeline.return_value.__enter__.return_value
        pipeline.execute.return_value = [vector.tobytes() for vector in vectors]
        query = np.array([1, 0], dtype=np.float32)
        self.assertEqual([i for i, _ in backend.manual(query, 3)], [0, 1, 2])
        self.assertEqual(pipeline.hget.call_count, 3)
        backend.client.execute_command.return_value = [
            3, b"key-0", [b"id", b"0", b"distance", b"0"],
            b"key-1", [b"id", b"1", b"distance", b"0.2"],
            b"key-2", [b"id", b"2", b"distance", b"1"],
        ]
        indexed = backend.indexed(query, 3)
        self.assertEqual(indexed, [(0, 1), (1, 0.8), (2, 0)])
        command = backend.client.execute_command.call_args.args
        self.assertEqual(command[0], "FT.SEARCH")
        self.assertIn("*=>[KNN 3 @vector $query AS distance]", command)
        position = command.index("RETURN")
        self.assertEqual(command[position:position + 4], ("RETURN", 2, "id", "distance"))

    def test_parse_search_response_accepts_resp2_and_resp3(self):
        resp2 = [
            3, b"idx:doc:0", [b"id", b"0", b"distance", b"0"],
            b"idx:doc:1", [b"id", b"1", b"distance", b"0.2"],
            b"idx:doc:2", [b"id", b"2", b"distance", b"1"],
        ]
        resp3 = {
            b"total_results": 3, b"format": b"STRING", b"attributes": [], b"warning": [],
            b"results": [
                {b"id": b"idx:doc:0", b"extra_attributes": {b"distance": b"0", b"id": b"0"}, b"values": []},
                {b"id": b"idx:doc:1", b"extra_attributes": {b"distance": b"0.2", b"id": b"1"}, b"values": []},
                {b"id": b"idx:doc:2", b"extra_attributes": {b"distance": b"1", b"id": b"2"}, b"values": []},
            ],
        }
        expected = [(0, 1), (1, 0.8), (2, 0)]
        self.assertEqual(demo.parse_search_response(resp2), expected)
        self.assertEqual(demo.parse_search_response(resp3), expected)

    def test_parse_search_response_uses_key_when_resp3_omits_id(self):
        resp3 = {
            b"results": [
                {b"id": b"idx:doc:7", b"extra_attributes": {b"distance": b"0.5"}, b"values": []},
            ],
        }
        self.assertEqual(demo.parse_search_response(resp3), [(7, 0.5)])

    def test_redis_indexed_parses_resp3_dict(self):
        backend = demo.RedisComparison.__new__(demo.RedisComparison)
        backend.client = MagicMock()
        backend.index = "test-index"
        backend.client.execute_command.return_value = {
            b"total_results": 2,
            b"results": [
                {b"id": b"test-index:doc:4", b"extra_attributes": {b"distance": b"0.25", b"id": b"4"}, b"values": []},
                {b"id": b"test-index:doc:9", b"extra_attributes": {b"distance": b"0.75", b"id": b"9"}, b"values": []},
            ],
        }
        indexed = backend.indexed(np.array([1, 0], dtype=np.float32), 2)
        self.assertEqual(indexed, [(4, 0.75), (9, 0.25)])

    def test_redis_indexed_rejects_short_response(self):
        backend = demo.RedisComparison.__new__(demo.RedisComparison)
        backend.client = MagicMock()
        backend.index = "test-index"
        backend.client.execute_command.return_value = {b"total_results": 1, b"results": []}
        with self.assertRaisesRegex(ValueError, "número solicitado"):
            backend.indexed(np.array([1, 0], dtype=np.float32), 3)

    def test_conclusions_reflect_data_not_assumed_index_win(self):
        rows = [demo.Measurement(200, "q", [(1, 1)], [(1, 1)], 1, 2),
                demo.Measurement(2000, "q", [(1, 1)], [(2, 1)], 3, 8)]
        lines = demo.conclusions(rows)
        self.assertEqual(len(lines), 2)
        self.assertIn("1/2", lines[0])
        self.assertIn("0/2", lines[0])
        self.assertIn("3.00x", lines[1])
        self.assertIn("4.00x", lines[1])

    def test_main_faiss_and_repeat_do_not_reembed(self):
        embeddings = LocalEmbeddings()
        settings = SimpleNamespace(vector_store="faiss", redis_url="", prefijo="prueba")
        with tempfile.TemporaryDirectory() as directory, patch.object(demo, "ROOT", Path(directory)), patch.object(
            demo, "get_embeddings", return_value=embeddings
        ), patch.object(demo, "get_settings", return_value=settings), redirect_stdout(io.StringIO()) as output:
            self.assertEqual(demo.main(["--n", "5", "--repeticiones", "1"]), 0)
            self.assertEqual(demo.main(["--n", "5", "--repeticiones", "1"]), 0)
        self.assertEqual(len(embeddings.documents), 5)
        self.assertEqual(len(embeddings.queries), 5)
        self.assertIn("5/5 reutilizados; 0 embeddings nuevos", output.getvalue())
        self.assertIn("OK: comparación terminada", output.getvalue())


if __name__ == "__main__":
    unittest.main()
