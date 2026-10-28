<!--
Integrantes: Fabio Durán; Gustavo Reyes; Ezequiel Muñoz
Objetivo: explicar instalación, configuración, uso, pruebas y preparación de la entrega.
fecha_hora_creacion: 20261027_1806
fecha_hora_modificacion: 20261028_0905
-->

# tarea_2_curso_1

## Identificación del grupo

Integrantes (nombres y apellidos completos confirmados):

- **Fabio Durán**.
- **Gustavo Reyes**.
- **Ezequiel Muñoz**.

Nombre del grupo: **N** (confirmado; no es un marcador pendiente).

**Material de compañeros:** no se utilizó material de compañeros.
Identificación y declaración confirmadas en `instrucciones/instruccion_02f.txt`.

Esta identificación y la atribución deben figurar también en la **primera página**
del documento final.

## Entrega del taller

La estructura de trabajo está en `entrega/grupo-N-taller2-rag/`.
Consultar [el plan de entrega](docs/entrega.md): allí se indica qué completar
y cómo consolidar instrucciones, evidencias y código al terminar.
El documento final y el ZIP se generarán **al final**, no en esta etapa.

La [rúbrica del taller](docs/reglas-taller.md) y `AGENTS.md` guardan las reglas
obligatorias: entregar **todo el código, ambos tipos de prompts y todas las
pruebas**, con conclusiones por etapa. Puntaje base: 100; bonus FAISS/Redis: +10.
Las plantillas de `pruebas/` distinguen los requisitos pendientes de las evidencias reales.

Proyecto RAG con Python 3.12, LangGraph y Gemini, administrado con
[uv](https://docs.astral.sh/uv/). Esta tarea usa **Redis persistente en Docker**;
FAISS sigue disponible como alternativa (predeterminado del código sin configuración).

## Redis de esta tarea

Desde la raíz, con Docker Desktop iniciado:

```powershell
docker compose up -d --wait   # Levantar
docker compose stop          # Detener conservando los datos
```

Configuración, reinicios, diagnóstico y bitácora: [docs/docker.md](docs/docker.md).
El puerto local es `16379`; `.env` usa `VECTOR_STORE=redis` y
`REDIS_URL=redis://localhost:16379`. No usar `docker compose down -v`.

## Preparación

Instalar `uv` en Windows (PowerShell), si no está disponible:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Instalar Python y crear el entorno virtual con las dependencias fijadas:

```powershell
uv python install
uv sync --locked
```

El archivo `.python-version` fija la versión de Python. El entorno local
se encuentra en `.venv` y no se incluye en Git.

## Configuración

Preparación y aplicación de una alternativa local para LLM y embeddings:
[Ollama, modelos y migración](docs/ollama.md). `langchain-ollama`, `qwen3:8b`
y `bge-m3` están instalados, y el programa ya trabaja con Ollama según
`MODEL_PROVIDER` en `.env`. Para volver a Google basta con
`MODEL_PROVIDER=google`; los índices y cachés quedan separados por proveedor.

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Completar `GOOGLE_API_KEY` en `.env`. Nunca subir este archivo a Git.
Las variables de entorno del sistema tienen prioridad sobre `.env`.

| Variable | Valor predeterminado / propósito |
| --- | --- |
| `GOOGLE_API_KEY` | Sin valor; obligatoria para ingesta y consultas |
| `VECTOR_STORE` | `redis` en esta tarea; alternativa: `faiss` |
| `REDIS_URL` | `redis://localhost:16379` para Docker de esta tarea |
| `EMBEDDING_MODEL` | `models/gemini-embedding-001` |
| `MODELO` | `gemini-3.5-flash-lite` |
| `PREFIJO` | `etmunoz`; usar uno distinto por equipo |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | `800` / `120` caracteres |
| `TOP_K` | `3` fragmentos |
| `UMBRAL` | `0.43` de similitud coseno mínima (barrido exhaustivo 20261028; antes `0.65` y `0.58`) |

El nombre de modelo solicitado se conserva literalmente: su disponibilidad
depende de Google y de tu cuenta. Si la API no lo ofrece, configura `MODELO`
con un modelo al que tengas acceso. No se sustituye silenciosamente.

## Ingesta y consultas

### PDF del corpus incorporado

Documento proporcionado por el usuario:
[`docs/LEY-19628_28-AGO-1999_refundida_20261201.pdf`](docs/LEY-19628_28-AGO-1999_refundida_20261201.pdf).
Se conservó su nombre original y se verificó una copia idéntica mediante SHA256.
Tiene **57 páginas**, todas con texto extraíble; no necesita OCR para la ingesta.

Estado: **copiado y verificado; todavía no ingerido ni enviado a Google**.
Cuando se solicite la ingesta de este corpus, ejecutar:

```powershell
uv run python scripts/ingest.py docs/LEY-19628_28-AGO-1999_refundida_20261201.pdf
```

La ingesta requiere la configuración del proyecto, envía texto a Google para
calcular embeddings y escribe en el backend configurado. Esta incorporación
solo verifica el archivo; no certifica su vigencia jurídica.

### Otros documentos y uso general

Guardar documentos privados dentro de `data/documentos/` (ignorado por Git).
Se admiten PDF con texto y TXT UTF-8, también carpetas recursivas.
Los PDF escaneados necesitan OCR externo.

```powershell
New-Item -ItemType Directory -Force data/documentos
# Copiar tus PDF o TXT a data/documentos antes de ejecutar la ingesta.
uv run python scripts/ingest.py data/documentos
uv run python main.py rag "¿Qué dicen los documentos?"
uv run python main.py rag "Resume los puntos principales" --saltos
uv run python main.py rag --diagrama
```

`--diagrama` solo imprime Mermaid: no ejecuta el grafo ni usa claves o red.
`--saltos` imprime los nodos efectivamente recorridos: `buscar` y, según
el resultado, `responder` o `no_se`. Sin evidencia (`mejor_parecido < UMBRAL`)
no se llama al modelo de chat. Las respuestas piden citas `[archivo p.N]`.
`--texto` lista el cuerpo completo de cada fragmento del `TOP_K` con su fuente,
página, parecido y largo; sirve para revisar el umbral a mano.

También se puede activar `.venv` y usar los comandos requeridos sin `uv run`:

```powershell
.\.venv\Scripts\Activate.ps1
python main.py rag "pregunta" --saltos
```

No es necesario activar el entorno para ejecutar comandos con `uv run`.

### Persistencia y cambio de backend

- FAISS guarda `index.faiss` y `documents.json` en `data/{PREFIJO}/`.
  No utiliza pickle ni `allow_dangerous_deserialization`. Cargar solo índices
  locales de confianza y conservar ambos archivos juntos.
- Para Redis, configurar `VECTOR_STORE=redis` y `REDIS_URL`. Se requiere
  Redis con soporte de búsqueda vectorial (Redis Stack o Redis 8 con Search),
  no un servidor antiguo sin el módulo de búsqueda. El índice se llama
  `{PREFIJO}_rag` y las claves usan `{PREFIJO}:rag`.
- El Redis persistente de esta tarea se inicia con:

  ```powershell
  docker compose up -d --wait
  ```

  Ver [la guía Docker](docs/docker.md). En producción, usar autenticación,
  TLS y copias de seguridad; la configuración incluida es solo local.
- Los backends son independientes: ejecutar nuevamente la ingesta al cambiar
  de backend. Usar un nuevo `PREFIJO` y reingestar si cambia el modelo de embeddings.
- La ingesta es incremental; repetir los mismos fragmentos no los duplica.
  Cambiar o quitar archivos de origen **no elimina** fragmentos antiguos:
  para reconstruir el corpus, usar un nuevo `PREFIJO` y reingestar.
- `UMBRAL` compara similitud coseno en ambos backends; puede ajustarse si no
  se recuperan fragmentos relevantes. Las llamadas a Google envían los textos
  y pueden tener costes: usar documentos que tengas autorización de procesar.

## Demos de embeddings y almacenamiento

Las dos demos comparten las mismas tres frases de ejemplo: dos sobre pérdida
de conexión a internet y una sobre cocina. Usan el modelo de embeddings
configurado en `.env` a través de la única fábrica compartida del proyecto.

```powershell
uv run python scripts/demo_embeddings.py
uv run python scripts/demo_embeddings.py --frases "No tengo internet" "No puedo conectarme a internet" "Estoy preparando una tortilla" --pregunta "Mi conexión no funciona"
```

La primera imprime dimensión y primeros cinco números de cada vector,
tabla de similitudes coseno ordenada y frase más cercana a la pregunta.
No depende de `VECTOR_STORE`: puede ejecutarse con FAISS o Redis configurados.

Para probar inserción y búsqueda de los dos vecinos más cercanos:

```powershell
$env:VECTOR_STORE = "faiss"
uv run python scripts/test_storage.py
$env:VECTOR_STORE = "redis"
uv run python scripts/test_storage.py
Remove-Item Env:VECTOR_STORE
```

- FAISS se crea únicamente en memoria y no carga ni guarda índices de `data/`.
- Redis requiere `REDIS_URL` explícita en `.env` o en el entorno. Primero hace
  PING y después crea el índice si no existe. No imprime la URL ni credenciales.
- Para no contaminar el corpus, se usa el prefijo `{PREFIJO}_demo`; en Redis
  quedan el índice `{PREFIJO}_demo_rag` y tres documentos con
  `metadata={"fuente": "demo"}`. Los IDs fijos evitan duplicados al repetir.
- El puntaje mostrado es una distancia: menor es mejor. FAISS devuelve L2²
  sobre vectores normalizados y Redis distancia coseno.
- Ambas demos admiten `--frases` (exactamente tres textos) y `--pregunta`.
  Finalizan con `OK` (código 0) o `FALLO` (código 1); argumentos inválidos usan
  código 2. Si Redis agota su memoria, hay que ampliar cuota o cambiar de
  servidor; el script no borra datos para liberar espacio.

La primera prueba Redis utilizó un contenedor temporal porque el servidor
externo estaba sin memoria. Ese contenedor ya fue retirado. Ahora se trabaja
con el Redis persistente de `compose.yaml`; no iniciar otro Redis en el puerto
16379. La [bitácora Docker](docs/docker.md#bitácora) registra la instalación y pruebas.

## Índice vectorial frente a coseno a mano

```powershell
uv run python scripts/indice_vs_coseno.py --n 2000
```

Compara 200 y 2000 fragmentos sintéticos sobre cinco temas usando exactamente
los mismos embeddings. Guarda documentos en `data/vectores_demo.npy` y sus
metadatos en `data/vectores_demo.json`; las cinco preguntas también se cachean.
Repetir o cambiar de backend no vuelve a calcular los vectores ya guardados.
No ejecutar dos procesos del benchmark simultáneamente sobre la misma caché.

Imprime top-3, coincidencias, tiempos, vectores recibidos en Python, crecimiento
y dos líneas de conclusión calculadas a partir de las mediciones. Con Redis,
A descarga todos los vectores y B usa `FT.SEARCH KNN`; con FAISS, A trabaja
con una lista en RAM y B usa un índice FAISS exacto. No se ingiere el PDF.

Uso, costes, cuotas, caché parcial y límites de memoria:
[docs/indice-vs-coseno.md](docs/indice-vs-coseno.md).

## Estructura

```text
main.py                  CLI de agentes
src/rag/graph.py         Grafo retrieve → generate/no_context
src/rag/prompts.py       Instrucciones del asistente
src/rag/tools.py         Recuperación y generación
src/rag/storage.py       Selección Redis/FAISS y persistencia
src/rag/embeddings.py    Única lectura de EMBEDDING_MODEL
src/rag/config.py        Configuración y validación
scripts/ingest.py        Ingesta PDF/TXT
scripts/demo_embeddings.py  Demostración de vectores y coseno
scripts/test_storage.py     Prueba operativa FAISS/Redis
scripts/demo_common.py      Frases y argumentos compartidos
scripts/indice_vs_coseno.py Comparación con datos y vectores idénticos
data/                   Documentos e índices locales (no versionados)
tests/                  Pruebas sin red ni claves reales
```

## Verificación

```powershell
uv sync --locked
uv run python --version
uv run python -m unittest discover -s tests -v
```

## Sincronización con GitHub

Antes de trabajar:

```powershell
git pull --ff-only
```

Para guardar y subir los cambios, revisarlos primero con `git diff`:

```powershell
git status
git diff
git add .
git commit -m "Describe los cambios realizados"
git push
```
