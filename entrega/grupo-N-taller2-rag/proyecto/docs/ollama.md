<!--
Integrantes: Fabio Durán; Gustavo Reyes; Ezequiel Muñoz
Objetivo: documentar la preparación de modelos locales Ollama y su aplicación al RAG.
fecha_hora_creacion: 20261027_1930
fecha_hora_modificacion: 20261027_1945
-->

# Preparación de Ollama — instrucciones 03a y 03b

## Alcance

Se prepara y aplica una alternativa local para el LLM y los embeddings, evitando
cuotas de una API externa. La preparación de dependencias y modelos se hizo en
las instrucciones 03a y 03b; la **migración del programa y de `.env`** en 03c.

Las cachés Gemini se conservan intactas y con su propio subdirectorio; no se
mezclan vectores entre proveedores. No se ingiere el PDF ni se generan aún el
documento final o el ZIP.

## Revisión previa y elección para 32 GB de RAM

`ollama list` confirmó que Ollama ya estaba instalado y atendiendo solicitudes.
Modelos presentes antes de esta preparación:

- `nomic-embed-text:latest` (274 MB).
- `phi3.5:latest` (2.2 GB).
- `llama3.2:3b` (2.0 GB).
- `qwen2.5-coder:7b` (4.7 GB).
- `mistral:latest` (4.4 GB).
- `gpt-oss:20b` (13 GB).

No estaban los dos modelos elegidos:

| Función | Modelo seleccionado | Motivo |
| --- | --- | --- |
| LLM | `qwen3:8b` | Modelo general multilingüe; elección razonable para pruebas con 32 GB de RAM, sin usar el modelo de 20B más pesado |
| Embeddings | `bge-m3` | Recuperación multilingüe, incluido español, con vectores de 1024 componentes |

Los modelos ya presentes no se borran ni se vuelven a descargar. Qwen Coder
está orientado a código; para este corpus legal se eligió un modelo general.
La RAM disponible no garantiza una velocidad determinada: también influyen
GPU, CPU, contexto y otros programas. Se probará con un contexto acotado.

## Dependencias Python

Ejecutado en el proyecto:

```powershell
uv add langchain-ollama
uv export --locked --no-dev --no-emit-project --output-file requirements.txt --quiet
```

Instalados en `.venv`: `langchain-ollama==1.1.0` y `ollama==0.6.3`.
Las clases `ChatOllama` y `OllamaEmbeddings` importan correctamente.
`uv pip check`: paquetes compatibles. Se mantienen las dependencias Google
para no romper la implementación actual ni el benchmark en curso.

## Descargas

Se iniciaron, tras comprobar la lista previa:

```powershell
ollama pull qwen3:8b
ollama pull bge-m3
```

Estado: **ambos modelos descargados y probados localmente**.
`ollama list` confirmó `qwen3:8b` (ID `500a1f067a9f`,
5.2 GB) y `bge-m3:latest` (ID `790764642607`, 1.2 GB).
Los modelos quedan en el almacenamiento de Ollama, fuera del repositorio,
de `.venv` y de Docker. No se incluyen sus pesos en la entrega.

Para consultar los modelos instalados y en ejecución posteriormente:

```powershell
ollama list
ollama ps
```

Para descargar de RAM un modelo cuando no se esté utilizando, sin borrar
sus archivos: `ollama stop qwen3:8b` o `ollama stop bge-m3`.
No se detienen otros modelos o servicios del usuario durante la preparación.

## Pruebas y estado

- Importación de las dos clases de LangChain: **OK**.
- `uv pip check`: **OK**.
- `uv run python -m unittest discover -s tests -v`: **30 pruebas aprobadas**
  tras instalar las nuevas dependencias. No prueban por sí solas la inferencia local.
  Tras la migración de 03c la suite alcanzó **41 pruebas**, más abajo.
- `ollama pull bge-m3`: **success**, descarga de aproximadamente 1.2 GB completada
  y verificada por Ollama.
- Prueba real local con `OllamaEmbeddings`: **OK**, tres documentos con vectores
  de **1024** componentes y una pregunta. Coseno contra `no tengo internet`:
  **0.793323**, **0.765289**, **0.416665**; vecino más cercano: frase 1 sobre internet.
  No se llamó a Google ni se escribieron estos vectores en la caché Gemini.
- `ollama pull qwen3:8b`: **success**, descarga de aproximadamente 5.2 GB
  completada y verificada por Ollama. Los demás modelos siguen presentes.
- Generación con Qwen3 mediante `ChatOllama`: **OK**, contexto 4096, temperatura 0,
  razonamiento desactivado y máximo de 96 tokens generados. Tiempo total observado:
  **35.46 s**, incluida la carga inicial; no es una medición de rendimiento estable.
  No se llamó a Google.

Pregunta exacta de la prueba de generación:

```text
Responde en español en una sola oración: ¿Para qué sirve un sistema RAG?
```

Salida real:

```text
Modelo: qwen3:8b
Respuesta: Un sistema RAG sirve para mejorar la capacidad de los modelos de lenguaje al integrar información externa y actualizada en sus respuestas.
Tiempo total: 35.46 s
OK: generación local con ChatOllama. Sin llamadas a Google.
```

Estas pruebas verifican la instalación e inferencia local, no la calidad del
agente con el PDF. La migración del RAG a Ollama se describirá a continuación.

## Migración aplicada al programa (instrucción 03c)

La migración mantuvo Gemini como opción válida mediante un selector explícito
`MODEL_PROVIDER`; el valor predeterminado pasó a ser `ollama`.

| Archivo | Cambio |
| --- | --- |
| `src/rag/config.py` | Nuevo `Settings` con `model_provider`, `ollama_base_url`, `ollama_timeout`, `ollama_num_ctx` y `ollama_num_predict`, con validación de URL y límites |
| `src/rag/llm.py` | Nuevo: `get_chat_model()` construye `ChatOllama` o `ChatGoogleGenerativeAI` |
| `src/rag/embeddings.py` | `get_embeddings()` devuelve `OllamaEmbeddings` con `EMBEDDING_MODEL`; añade `embedding_identity()` y `embedding_fingerprint()` |
| `src/rag/tools.py` | `generate()` usa la fábrica compartida `get_chat_model()` |
| `src/rag/storage.py` | El índice guarda `embedding_identity`; rechaza cambio de proveedor o endpoint |
| `scripts/indice_vs_coseno.py` | Caché por proveedor en `data/embeddings/<huella>/` |
| `main.py` | Añade mensajes de error accionables para `MODEL_PROVIDER`, `MODELO` y `OLLAMA` |
| `.env` | `MODEL_PROVIDER=ollama`, `MODELO=qwen3:8b`, `EMBEDDING_MODEL=bge-m3`, `PREFIJO=etmunoz_ollama` y parámetros Ollama |
| `.env.example` | Refleja la nueva configuración y marca `GOOGLE_API_KEY` como opcional |

La única lectura de `EMBEDDING_MODEL` sigue estando en `src/rag/embeddings.py`,
como exige `AGENTS.md`. La clave Google se conservó en `.env` sin mostrarse ni
copiarse, para poder volver a `MODEL_PROVIDER=google`.

### Verificación real

- **41 pruebas automatizadas aprobadas** (`uv run python -m unittest discover -s tests -v`),
  incluyendo las nuevas de selección de proveedor, ausencia de clave Google,
  huellas distintas por endpoint y separación de la caché Gemini.
- `uv run python scripts/demo_embeddings.py`: **OK**, vectores de 1024 componentes
  con `bge-m3`, coseno más alto 0.908784 entre las frases equivalentes y vecino
  más cercano correcto (coseno 0.793323).
- `uv run python scripts/test_storage.py`: **OK** en Redis con el prefijo
  `etmunoz_ollama_demo`.
- Recorrido completo del grafo con `--saltos` (fragmentos de demostración, sin PDF ingerido):

```text
[salto] retrieve
[salto] generate
Según el contexto proporcionado, no tienes conexión a internet en tu casa [1], y en tu hogar no puedes conectarte a la red de internet [2].
```

- `ollama ps` tras la ejecución mostró `bge-m3` en GPU (664 MB) y `qwen3:8b`
  en 59%/41% CPU/GPU (6.0 GB), contexto 4096.

### Límites de esta migración

- **No se ingerió todavía el PDF** `docs/LEY-19628_28-AGO-1999_refundida_20261201.pdf`;
  la ejecución anterior usó los tres fragmentos de demostración de Redis.
- `UMBRAL=0.65` se heredó del ajuste con embeddings de Gemini. Con vectores de
  BGE-M3 debe reevaluarse con datos, no asumirse equivalente.
- No se reinició ni reconfiguró Docker. Redis sigue en `127.0.0.1:16379` con el
  mismo volumen; el cliente Python corre en Windows y usa Ollama local.
- La comparación con FAISS y el documento final siguen pendientes.

Fuentes: [ChatOllama](https://docs.langchain.com/oss/python/integrations/chat/ollama)
y [OllamaEmbeddings](https://docs.langchain.com/oss/python/integrations/text_embedding/ollama).
