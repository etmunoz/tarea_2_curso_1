# Integrantes: Fabio Durán; Gustavo Reyes; Ezequiel Muñoz
# Objetivo: verificar selección de proveedor, ausencia de claves para Ollama y separación de cachés.
# fecha_hora_creacion: 20261027_1938
# fecha_hora_modificacion: 20261027_2015

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import Mock, patch

import numpy as np
from langchain_core.documents import Document
from langchain_core.messages import AIMessage
from langchain_ollama import OllamaEmbeddings

from scripts import indice_vs_coseno as demo
from src.rag import config, embeddings, llm, storage, tools


class ModelTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch.dict(os.environ, {}, clear=True))
        self.enterContext(patch.object(config, "load_dotenv"))
        self.enterContext(patch.object(embeddings, "load_dotenv"))

    def test_default_provider_is_ollama(self):
        settings = config.get_settings()
        self.assertEqual(settings.model_provider, "ollama")
        self.assertEqual(settings.modelo, "qwen3:8b")
        self.assertEqual(settings.ollama_base_url, "http://localhost:11434")

    def test_provider_and_ollama_settings_validation(self):
        for variable, value in [("MODEL_PROVIDER", "otro"), ("OLLAMA_BASE_URL", "ftp://localhost"),
                                ("OLLAMA_TIMEOUT", "0"), ("OLLAMA_NUM_CTX", "0"),
                                ("OLLAMA_NUM_PREDICT", "0"), ("MODELO", "")]:
            with self.subTest(variable=variable), patch.dict(os.environ, {variable: value}):
                with self.assertRaises(ValueError):
                    config.get_settings()

    def test_ollama_embeddings_need_no_google_key(self):
        with patch.object(embeddings, "OllamaEmbeddings") as constructor, patch.object(
            embeddings, "GoogleGenerativeAIEmbeddings"
        ) as google, patch.object(embeddings, "require_api_key") as key:
            self.assertIs(embeddings.get_embeddings(), constructor.return_value)
        self.assertEqual(constructor.call_args.kwargs["model"], "bge-m3")
        self.assertEqual(constructor.call_args.kwargs["base_url"], "http://localhost:11434")
        google.assert_not_called()
        key.assert_not_called()

    def test_ollama_chat_need_no_google_key(self):
        with patch.object(llm, "ChatOllama") as constructor, patch.object(
            llm, "ChatGoogleGenerativeAI"
        ) as google, patch.object(llm, "require_api_key") as key:
            self.assertIs(llm.get_chat_model(), constructor.return_value)
        self.assertEqual(constructor.call_args.kwargs["model"], "qwen3:8b")
        self.assertFalse(constructor.call_args.kwargs["reasoning"])
        self.assertEqual(constructor.call_args.kwargs["num_ctx"], 4096)
        google.assert_not_called()
        key.assert_not_called()

    def test_embedding_and_chat_model_overrides(self):
        with patch.dict(os.environ, {"EMBEDDING_MODEL": "otro-embedding", "MODELO": "otro-chat"}), patch.object(
            embeddings, "OllamaEmbeddings"
        ) as embed, patch.object(llm, "ChatOllama") as chat:
            embeddings.get_embeddings()
            llm.get_chat_model()
        self.assertEqual(embed.call_args.kwargs["model"], "otro-embedding")
        self.assertEqual(chat.call_args.kwargs["model"], "otro-chat")

    def test_google_still_requires_key(self):
        with patch.dict(os.environ, {"MODEL_PROVIDER": "google"}):
            for factory in (embeddings.get_embeddings, llm.get_chat_model):
                with self.subTest(factory=factory.__name__), self.assertRaisesRegex(ValueError, "Falta GOOGLE_API_KEY"):
                    factory()

    def test_google_provider_uses_google_classes(self):
        with patch.dict(os.environ, {"MODEL_PROVIDER": "google", "GOOGLE_API_KEY": "test-placeholder"}), patch.object(
            embeddings, "GoogleGenerativeAIEmbeddings"
        ) as embed, patch.object(llm, "ChatGoogleGenerativeAI") as chat:
            embeddings.get_embeddings()
            llm.get_chat_model()
        self.assertEqual(embed.call_args.kwargs["model"], "models/gemini-embedding-001")
        self.assertEqual(chat.call_args.kwargs["model"], "gemini-3.5-flash-lite")

    def test_generation_uses_selected_factory_and_keeps_context(self):
        model = Mock()
        model.invoke.return_value = AIMessage(content="Respuesta [prueba.txt p.1].")
        fragmentos = [{"texto": "Contexto de prueba", "fuente": "prueba.txt", "pagina": 1, "parecido": 0.9}]
        with patch.object(tools, "get_chat_model", return_value=model) as factory:
            self.assertEqual(tools.responder("Pregunta", fragmentos), "Respuesta [prueba.txt p.1].")
        factory.assert_called_once()
        messages = model.invoke.call_args.args[0]
        self.assertIn("Contexto de prueba", messages[1].content)
        self.assertIn("prueba.txt", messages[1].content)
        # El USER_PROMPT lleva la pregunta entre las etiquetas pedidas.
        self.assertIn("<pregunta>\nPregunta\n</pregunta>", messages[1].content)
        self.assertIn("<contexto>", messages[1].content)

    def test_buscar_returns_fragments_with_similarity(self):
        document = Document(page_content="Contenido", metadata={"source": "docs/ley.pdf", "page": 7})
        with patch.object(tools, "search_with_similarity", return_value=[(document, 0.8123)]):
            fragmentos = tools.buscar("pregunta")
        self.assertEqual(len(fragmentos), 1)
        self.assertEqual(fragmentos[0]["texto"], "Contenido")
        self.assertEqual(fragmentos[0]["fuente"], "ley.pdf")
        self.assertEqual(fragmentos[0]["pagina"], 7)
        self.assertAlmostEqual(fragmentos[0]["parecido"], 0.8123)

    def test_model_and_endpoint_get_separate_fingerprints(self):
        one = OllamaEmbeddings(model="bge-m3", base_url="http://localhost:11434")
        two = OllamaEmbeddings(model="otro", base_url="http://localhost:11434")
        three = OllamaEmbeddings(model="bge-m3", base_url="http://localhost:11435")
        self.assertEqual(embeddings.embedding_identity(one)["provider"], "ollama")
        self.assertEqual(len({embeddings.embedding_fingerprint(item) for item in (one, two, three)}), 3)

    def test_new_cache_does_not_overwrite_legacy_gemini_cache(self):
        local = OllamaEmbeddings(model="bge-m3", base_url="http://localhost:11434")
        with tempfile.TemporaryDirectory() as directory, patch.object(demo, "ROOT", Path(directory)), patch.object(
            demo, "embed_with_retry", return_value=[[1.0, 0.0]]
        ), redirect_stdout(io.StringIO()):
            legacy = Path(directory) / "data" / "vectores_demo.npy"
            legacy.parent.mkdir()
            legacy.write_bytes(b"legacy-google-cache")
            result = demo.cached_vectors(local, ["texto"])
            self.assertEqual(legacy.read_bytes(), b"legacy-google-cache")
            new = legacy.parent / "embeddings" / embeddings.embedding_fingerprint(local) / "vectores_demo.npy"
            np.testing.assert_array_equal(np.load(new, allow_pickle=False), result)

    def test_faiss_rejects_endpoint_change(self):
        local = OllamaEmbeddings(model="bge-m3", base_url="http://localhost:11434")
        with tempfile.TemporaryDirectory() as directory, patch.object(storage, "ROOT", Path(directory)), patch.object(
            storage, "get_embeddings", return_value=local
        ), patch.object(OllamaEmbeddings, "embed_query", return_value=[1.0, 0.0]):
            store = storage.get_vector_store("equipo")
            storage.persist_vector_store(store, "equipo")
            payload = json.loads((Path(directory) / "data" / "equipo" / "documents.json").read_text())
            self.assertEqual(payload["embedding_identity"]["provider"], "ollama")
            other = OllamaEmbeddings(model="bge-m3", base_url="http://localhost:11435")
            with patch.object(storage, "get_embeddings", return_value=other):
                with self.assertRaisesRegex(ValueError, "otro modelo o proveedor"):
                    storage.get_vector_store("equipo")


if __name__ == "__main__":
    unittest.main()
