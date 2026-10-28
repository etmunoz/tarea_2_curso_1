<!--
Integrantes: Fabio Durán; Gustavo Reyes; Ezequiel Muñoz
Objetivo: organizar la entrega, sus pendientes y la consolidación final de código y evidencias.
fecha_hora_creacion: 20261027_1858
fecha_hora_modificacion: 20261028_1949
-->

# Plan de entrega del taller 2 RAG

## Consolidación de la instrucción 11 (20261028)

Etapa 4 revisada con el set original. Comparación ejecutada de las cinco
dentro con TOP_K=1 y 5, y baterías completas con K=4 y 5. **Elegido TOP_K=4**;
se conservan UMBRAL=0.43 y chunks 800/120. Tabla completa, falsos positivos
(Q6/Q8), verificación textual del PDF y conclusiones en
`entrega/grupo-N-taller2-rag/pruebas/bateria.md`, sección «Consolidación de la
instrucción 11». Allí se conservan los antecedentes y resultados anteriores.

Cinco JSON nuevos conservan las respuestas; las tres imágenes
`20261028_instruccion11_{dentro,fuera,ambigua}.png` muestran stdout real
capturado y presentado en HTML (incluido), no una ventana de terminal.
Dos redacciones de sinónimos muestran un fallo y un acierto; la pregunta
de criptomonedas muestra parecido alto y rechazo correcto. La instrucción 12
(etapa 5) ya tiene ejecuciones antes/después para las preguntas 1–3, prueba de
premisa falsa y prueba temporal retirando/restaurando la regla 1. Resultados y
limitaciones en `pruebas/antes-despues.md`. La regla 10 no consiguió que el
agente corrigiera explícitamente «120 días»; con regla 1 retirada y UMBRAL=0
tampoco alucinó, pues la regla 3 siguió activa. Se conserva el resultado aunque
no sea el efecto esperado. El usuario pidió reglas 6–9 y luego la regla 10,
aunque la instrucción base pedía dos cambios; esta diferencia se documenta sin
ocultarla. La evidencia de etapa 5 está completa. La etapa 6 ya se ejecutó con
`reformular`; las mediciones muestran menos ruido en Q3, aunque sigue incompleta,
y una respuesta sin cambios en Q5. El usuario evalúa ambos casos como mejora;
las dos lecturas se distinguen en `pruebas/nodo-extra.md`.

La instrucción exacta está en `instrucciones/instruccion_11.txt`; conservar
también la transcripción de `salidas_opencode/salida_11.txt` para el documento
final. Esta actualización sustituye las menciones históricas a TOP_K=3 como
valor vigente; no cambia la validación del usuario de chunks y umbral.

Rúbrica y criterios obligatorios: [reglas del taller](reglas-taller.md),
reforzados en `AGENTS.md`. El foco son las pruebas y el pulido de prompts;
el código y las pruebas unitarias por sí solos no completan la entrega.

## Equipo

- Fabio Durán
- Gustavo Reyes
- Ezequiel Muñoz
- Nombre del grupo: **N**, confirmado como nombre literal, no como marcador.

Los nombres anteriores incluyen todos los nombres y apellidos, según la
confirmación del usuario en `instrucciones/instruccion_02f.txt`.
**No se utilizó material de compañeros**, según la misma confirmación.

### Identificación de la primera página (obligatoria)

Al generar el documento final, su **primera página** debe incluir:

- Título del taller y nombre o número de grupo confirmado.
- Nombres y apellidos completos y confirmados de los tres integrantes.
- Atribución del material de compañeros, si se utilizó: autor, material y uso.

Mantener los mismos datos visibles en `README.md` y en la copia final
`proyecto/README.md`. No basta con dejarlos en comentarios HTML ni en una
sección interior del documento. No generar aún el documento final.

| Material de compañero (si corresponde) | Nombre y apellidos del autor | Dónde se utilizó / referencia |
| --- | --- | --- |
| No se utilizó material de compañeros | No aplica | No aplica |

Confirmación registrada en `instrucciones/instruccion_02f.txt`. Si posteriormente
se incorpora material de compañeros, añadir la atribución y actualizar la declaración.

## Comentarios y validación del usuario

Cada revisión del usuario se registra aquí con su fecha, el texto tal como se
recibió y el efecto en el proyecto. Los comentarios no reemplazan la evidencia:
solo la confirman o la corrigen.

### 20261028_1033 — Validación de la etapa 3

Texto recibido del usuario, tras revisar el commit `5dffe5f`:

> Comentarios del Usuario: Quedan finalmente 800/120 como combinación final a
> dejar, junto con el umbral ya definido.

- **Alcance**: confirma la elección de la etapa 3 (`instrucciones/instruccion_10.txt`).
- **Efecto**: **ninguno sobre el código**. Valida lo que ya estaba aplicado:
  `CHUNK_SIZE=800`, `CHUNK_OVERLAP=120` y `UMBRAL=0.43` en `.env` y
  `.env.example`, con el índice Redis de 294 fragmentos reingerido con esa
  configuración.
- **Evidencia**: `entrega/grupo-N-taller2-rag/pruebas/chunks.md` y las tres
  capturas `20261028_1014_etapa3_ingesta_*.txt`.
- Se deja escrito por si una revisión posterior contradice esta combinación:
  habría que reingerir con los valores nuevos y documentarlo en `docs/docker.md`.

### 20261028_1849 — Comentario del usuario sobre etapa 5

Texto recibido, conservado literalmente:

> La regla 10 cambió la redacción de la respuesta a la trampa, pero el modelo aún no señaló que 120 días carecía de respaldo. Ahora resguardo el prompt actual (incluida la regla 10) y confirmo UMBRAL=0.43, TOP_K=4 antes de la prueba temporal. Luego restauraré el archivo exacto y repetiré la misma pregunta.
>
> En el caso de la frase fuera, cambia la forma de la respuesta, más coherente en el caso de la situación normal. Si bien cambia la respuesta, no hay cambios significativos en la misma.

- **Efecto:** comentario incorporado a `pruebas/antes-despues.md`; no se cambió el prompt ni se repitieron las pruebas.

### 20261028_1936 — Evaluación del usuario sobre etapa 6

Texto recibido:

> Comentarios del Usuario: Claramente mejora la respuesta al ser reformulada, al menos para los dos casos probados se evidencia una mejora.

- **Efecto:** incorporado literalmente a `pruebas/nodo-extra.md` como evaluación
  del usuario, separado de los parecidos, rutas y respuestas medidos.

### 20261028_1949 — Contexto de credenciales, cuotas y proveedores

Comentario literal del usuario:

> Comentar de los problemas de acabado de keys, que nos llevaron a instalar en docker el redis y a trabajar con Ollama lo de los embeddings. Además de no tener los tokens para que OpenCode funcionara y que acabaron los modelos gratuitos para la cuenta.

- **Efecto:** se incorporará como contexto de las iteraciones de prompts y
  proveedores en `pruebas/prompts.md`. Las salidas anteriores documentan la
  limitación de memoria del Redis compartido y la cuota Gemini 429; la falta de
  tokens de OpenCode y el fin de los modelos gratuitos se conservan como
  declaración del usuario, sin datos de cuenta ni credenciales.

## Estructura preparada

### Corpus proporcionado (instrucción 02g)

- Origen: PDF indicado por el usuario en `instrucciones/instruccion_02g.txt`.
- Copia del proyecto: `docs/LEY-19628_28-AGO-1999_refundida_20261201.pdf`.
- Tamaño: **212210 bytes**; **57 páginas**, todas con texto extraíble;
  **175378 caracteres** extraídos en la verificación con `pypdf`.
- SHA256 idéntico en origen y copia:
  `4e469d6d0f9a3d4adef986e55b9add2e7b47bb97c6ceadb98e8bbc9c4eea2cad`.
- Se conservó el original en Downloads y no se alteró el contenido del PDF.
- Estado: archivo incorporado y validado localmente; **ingesta pendiente**.
  No se enviaron textos a Google ni se modificaron índices Redis/FAISS.
- Al consolidar la entrega, copiarlo a
  `proyecto/docs/LEY-19628_28-AGO-1999_refundida_20261201.pdf`, conservando
  el nombre real; no hace falta renombrarlo a `tu-documento.pdf`.

### Directorios

```text
entrega/
└── grupo-N-taller2-rag/
    ├── pruebas/
    │   ├── bateria.md
    │   ├── chunks.md
    │   ├── antes-despues.md
    │   ├── construccion.md
    │   ├── embeddings.md
    │   ├── prompts.md
    │   ├── nodo-extra.md
    │   └── capturas/
    └── proyecto/
        ├── src/rag/
        ├── scripts/
        ├── tests/
        └── docs/
```

Las carpetas vacías tienen `.gitkeep`. El código se sigue editando **en la raíz
del repositorio**, no en `entrega/.../proyecto/`. Esta última es el destino de
la copia final, todavía pendiente, para no mantener dos versiones divergentes.
Las plantillas no representan pruebas ya ejecutadas.

No se generan todavía `documento-entrega.docx` ni `grupo-N-taller2-rag.zip`.
Tampoco se crea un PDF de ejemplo ni un script vacío que parezca implementado.

## Documento final, al terminar

Construir `documento-entrega.docx` con integrantes, grupo, objetivos, desarrollo,
pruebas de cada etapa, prompts utilizados y conclusiones sustentadas en resultados.
Incluir el detalle de **cada** archivo de instrucciones: `instruccion_NN.txt` o
`instruccion_NNx.txt`, admitiendo también `instrucción` con tilde. Ordenar por
número y luego por sufijo: `00`, `01`, `02`, `02a`, `02b`, `02c`, `03`, etc.

Para cada instrucción conservar su texto original, describir cambios, comandos,
salidas, archivos afectados, decisiones y limitaciones. Las salidas guardadas en
`salidas_opencode/` y la bitácora `docs/docker.md` son material de apoyo: deben
revisarse contra las pruebas reales y eliminar secretos antes de incorporarlas.
Si una instrucción se reemplaza, conservar su versión anterior o registrar el cambio;
no atribuir retrospectivamente un contenido nuevo a una ejecución anterior.

### Instrucciones presentes al preparar esta estructura

| Instrucción | Contenido actual | Evidencia / pendiente |
| --- | --- | --- |
| `00` | uv, Python y repositorio | Historial de trabajo y configuración del proyecto |
| `01` | Proyecto RAG y configuración | Código, dependencias y pruebas automatizadas |
| `02` | Demos de embeddings y almacenamiento | Scripts y salidas reales de las demos |
| `02a` | Redis persistente en Docker | `compose.yaml` y `docs/docker.md` |
| `02b` | Repetir pruebas mostrando salidas | Salidas en conversación y registro Docker |
| `02c` | Preparar la estructura de entrega | Este plan y plantillas de `pruebas/` |
| `02d` | Reforzar reglas y rúbrica del taller | `AGENTS.md`, `docs/reglas-taller.md` y plantillas alineadas |
| `02e` | Identificación y atribución obligatorias | README visible y requisitos de primera página |
| `02f` | Confirmación de identificación y declaración | Nombres completos confirmados; grupo N; sin material de compañeros |
| `02g` | Incorporar el PDF proporcionado | Copia en `docs/`, SHA256 idéntico y texto extraíble verificado; ingesta pendiente |
| `03` | Índice frente a coseno con los mismos datos | Ejecutado con Redis y BGE-M3: 45 pruebas, tablas de n=200 y n=2000, 10/10 coincidencias, A/B=49.87x; bug RESP2/RESP3 corregido, ver `docs/indice-vs-coseno.md` |
| `03a` | Alternativas de LLM y embeddings ante cuotas Gemini | Recomendación local y consideraciones de migración en `docs/ollama.md` |
| `03b` | Preparar Ollama, dependencias y modelos para 32 GB RAM | Dependencias y ambos modelos instalados; BGE-M3 (1024 dimensiones) y Qwen3 (generación en 35.46 s) probados localmente, detalles en `docs/ollama.md` |
| `03c` | Adaptar programa y `.env` para trabajar con Ollama | `MODEL_PROVIDER=ollama`, fábricas de chat y embeddings, huella por proveedor y caché separada; 48 pruebas y grafo completo con `--saltos`, detalles en `docs/ollama.md` |
| `04` | Generar `scripts/ingest.py` con PyPDFLoader y `--reset` | 57 páginas, 318 fragmentos, tamaño medio 580.3 car., solape real 83 car.; Redis poblado con `etmunoz_ollama` |
| `05` | Nuevo agente `rag` en LangGraph con estado en español, `mejor_parecido`, memoria y prompts etiquetados | Nodos `buscar`/`responder`/`no_se`, arista por `UMBRAL`, `MemorySaver` por `thread_id`, `--saltos` con fragmentos; 52 pruebas; set de 10 preguntas en `docs/preguntas.md` |
| `05a` | Ejecutar `python main.py rag "Objeto y ámbito de aplicación" --saltos` | Ruta `buscar → responder`: mejor_parecido **0.6827** > `UMBRAL=0.65` vigente ese día; salida en `salidas_opencode/salida_05a.txt` |
| `05b` | Completar `pruebas/bateria.md` con las 10 preguntas ad-hoc y sus respuestas esperadas | Páginas localizadas contra el PDF con `pypdf` y numeración 1-based confirmada en `ingest.py`; preguntas y fuentes en `docs/preguntas.md`; salida en `salidas_opencode/salida_05b.txt` |
| `05c` | Ejecutar la batería aprobada y completar la tabla | Las 10 preguntas ejecutadas y verificadas una a una contra el PDF; crudo en `pruebas/capturas/bateria_20261027_2059.json`; salida en `salidas_opencode/salida_05c.txt` |
| `06` | Añadir un flag para listar el texto de cada fragmento del `TOP_K` | Flag **`--texto`** en `main.py` junto a `--saltos`, con la función `_indentar()`; permitió diagnosticar que el TOP_1 de la pregunta 2 mide 125 caracteres y se corta en el encabezado; salida en `salidas_opencode/salida_06.txt` |
| `instrucción_07` | Embeddings: predecir antes de medir y comparar índice contra coseno | Etapa 2 completada: 3 frases, predicción escrita 20261028_0728 antes de la ejecución 20261028_0737, tabla de cosenos (1–2 = 0.888802; 1–3 = 0.379792; 2–3 = 0.343577) y tabla de tiempos con `--n 2000` (10/10 coincidencias, A/B=57.39x); evidencia en `entrega/grupo-N-taller2-rag/pruebas/embeddings.md` y `pruebas/capturas/20261028_0737_etapa2_*.txt` |
| `Instruccion_08` | Dos frases con las mismas palabras y distinto sentido: ¿salen menos parecidas que dos de igual significado? | **Ejecutada 20261028_0921** con `scripts/sentido.py` (script nuevo): control A1–A2 (igual significado) = **0.876027**, objetivo B1–B2 (mismo léxico, distinto sentido) = **0.716434**, margen **+0.159592** → **se cumple el orden esperado**. Predicción escrita a las 0919 antes de medir; evidencia en `pruebas/embeddings.md` (secciones 8–12) y `pruebas/capturas/20261028_0921_etapa2_instruccion08_sentido.txt` |
| `instruccion_09` | Revisión de los entregables de la etapa 2: frases + predicción + tabla de cosenos + conclusión de 2 líneas; tabla de tiempos n=200/2000 + regla en 1 línea | **Ejecutada 20261028_0938**. Ambos entregables verificados contra los archivos. **2 huecos corregidos**: faltaba la conclusión de dos líneas y la regla en una sola línea (añadidas en `embeddings.md` §6/§7 y en las dos capturas). **Limitación declarada** en §15: el orden de la predicción no tiene prueba a nivel de archivo, porque el mismo `embeddings.md` se editó después; proceso corregido para las próximas predicciones |
| `instruccion_10` | Etapa 3: ingerir con 400/50 y con 1200/200, ver fragmentos 1 y 2, preguntar al agente y elegir configuración | **Ejecutada 20261028_1014**. Medido con `--reset` en cada paso: **A 400/50 → 573 frag., 320.4 car., solape 45/50, parecido 0.6055 pero respuesta incorrecta** (TOP_1 de 103 car. solo con el encabezado `c)`); **B 1200/200 → 193 frag., 971.2 car., solape 0/200, parecido 0.5118 respuesta incorrecta**; **base 800/120 → 294 frag., 627.6 car., solape 83/120, parecido 0.5054 respuesta correcta (2 corridas idénticas)**. **Elegida 800/120**, dejada en `.env` y reingerida. Tablas y justificación en `pruebas/chunks.md`; capturas `20261028_1014_etapa3_ingesta_*.txt` |

### Instrucciones 11–14 — actualización

| Instrucción | Estado y resultados |
| --- | --- |
| `instruccion_11` | Etapa 4 ejecutada con comparaciones TOP_K=1/3/4/5; **TOP_K=4 elegido** con UMBRAL=0.43 y chunks 800/120. Tabla, falsos positivos, prueba léxica y citas en `pruebas/bateria.md`; JSON y capturas en `pruebas/capturas/`. |
| `instruccion_12` | Etapa 5: antes/después preguntas 1–3, trampa 120 días y prueba temporal quitando/restaurando regla 1 ejecutadas. La regla 10 no corrigió explícitamente la premisa; sin regla 1 y UMBRAL=0 tampoco hubo alucinación, pues regla 3 permaneció activa. Evidencia y prompt vigente en `pruebas/antes-despues.md` y `pruebas/prompts.md`. La diferencia entre las reglas pedidas por el usuario y el requisito original de dos cambios se declara explícitamente. |
| `instruccion_13` | Etapa 6: nodo `reformular` antes de `buscar`, prompt propio, diagramas Mermaid antes/después y preguntas 3 y 5 con `--saltos`. El nodo aparece en las rutas; Q3 deja de añadir el punto p.19 pero sigue incompleta, Q5 no cambia sustantivamente. No se afirma mejora donde no la hubo. Evidencia en `pruebas/nodo-extra.md`, `pruebas/prompts.md`, `pruebas/capturas/` y `salidas_opencode/salida_13.txt`. 60 pruebas unitarias OK. |
| `instruccion_14` | Barrido cruzado de las 28 fuentes de instrucción 00–14 (incluidos sufijos) y sus salidas: matriz fuente→registro, iteraciones y cautelas sobre salidas-resumen en `pruebas/prompts.md`. La sección de prompts de OpenCode y los prompts finales SYSTEM_PROMPT, USER_PROMPT y PROMPT_REFORMULAR están listos para copiar. DOCX/ZIP siguen pendientes: la evidencia de etapa 1 y otros ítems del checklist aún están abiertos, y el plan reserva los archivos finales para después de completarlo. |

### Estado actual frente a los valores históricos de la tabla

La tabla anterior registra lo que produjo **cada instrucción el día en que se
ejecutó**; no es el estado de hoy. Valores vigentes al **20261028_0849**
(`UMBRAL` se actualizó ese día tras el barrido exhaustivo pedido por el usuario;
los demás campos se verificaron el **20261028_0747**):

| Campo | Valor en la fila de su instrucción | Valor vigente | Qué cambió y cómo se verificó |
| --- | --- | --- | --- |
| Fragmentos del corpus | `04`: **318** | **294** | Se corrigió el troceado añadiendo `merge_small_fragments()` a `scripts/ingest.py` (fundir fragmentos < 200 caracteres con un vecino de la misma página) y se reingestó con `--reset` el 20261027_2337. Mínimo 24 → 200 caracteres, 24 fragmentos fusionados. Verificado con `FT.SEARCH` sobre el índice `etmunoz_ollama_rag`: **294 docs** |
| Pruebas automatizadas | `05`: **52** | **59** | Las 5 nuevas son de `merge_small_fragments()`. Verificado con `uv run python -m unittest discover -s tests`: **Ran 59 tests … OK** |
| `UMBRAL` | `05a`: **0.65** | **0.43** | Valor en `.env` (línea 11), `.env.example` (línea 18) y en el default de `src/rag/config.py` (línea 55); `get_settings()` devuelve `umbral 0.43`. **Historial**: el 20261028 el usuario confirmó **0.58** (coste medido: 6/10 rutas); después pidió determinar el mejor umbral *probando exhaustivamente*, y un barrido de los 101 valores de 0.00 a 1.00 mostró que 0.58 cae en el régimen de **6/10**, el peor de los centrales, con 2 falsos negativos y 1 alucinación. Solo dos intervalos dan 8/10; se ejecutó la batería en ambos y ganó `(0.3636, 0.5054]`, eligiendo **0.43** por ser el punto de mayor margen. Resultado: **8/10 rutas, 0 falsos negativos, 0 alucinaciones**. Barrido y corridas 7–9 en `pruebas/bateria.md`; script `scripts/umbral.py` |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` / `TOP_K` | — | 800 / 120 / 4 | TOP_K=4 elegido en la instrucción 11 mediante comparación de batería; valor vigente en `.env`, `.env.example` y default |

Los separadores del splitter siguen **fijos** en `["\n\n", ". ", " ", ""]`
(`instruccion_04.txt`) y no se modificaron al corregir el troceado.

## Checklist final (no ejecutar aún)

- [x] Confirmar el nombre del grupo: **N**. Conservar `grupo-N-taller2-rag/`
      y el nombre final `grupo-N-taller2-rag.zip`.
- [x] Confirmar nombres y apellidos completos de los tres integrantes.
- [x] Confirmar la declaración: no se utilizó material de compañeros.
- [ ] Reproducir los nombres, grupo N y declaración confirmados en la primera
      página del documento final y en `proyecto/README.md` al cerrar la entrega.
- [ ] Completar las evidencias de las seis etapas, no solo las pruebas unitarias.
- [x] Registrar la predicción de embeddings antes de la ejecución correspondiente;
      no reconstruir retrospectivamente una predicción a partir de sus resultados.
      Hecho en `pruebas/embeddings.md`: predicción escrita en
      `instrucciones/instrucción_07.txt` a las 07:28 y ejecución a las 07:37.
      **Repetido con `Instruccion_08.txt`**: predicción escrita a las **09:19**
      y ejecución a las **09:21** del 20261028 (secciones 8–12 del mismo archivo).
- [x] Comparar dos configuraciones de chunks y justificar la elegida.
      Hecho el 20261028_1014 con **tres** configuraciones (400/50, 1200/200 y la
      base 800/120), misma pregunta, `--reset` en cada paso y `--texto` para ver
      los fragmentos. **Elegida 800/120** por ser la única cuya respuesta es
      correcta; justificación y tablas en `pruebas/chunks.md`, capturas en
      `pruebas/capturas/20261028_1014_etapa3_ingesta_*.txt`.
- [x] Ejecutar diez preguntas con ruta, parecido, respuesta y cita; justificar
      TOP_K y UMBRAL con datos. Ejecutado **nueve veces** (ver `pruebas/bateria.md`):
      tabla completa con ruta, parecido, respuesta y cita en las corridas 1, 2, 6 y 9;
      `TOP_K=3` justificado porque 2 respuestas citaron el fragmento 2 o 3;
      `UMBRAL` **barrido exhaustivamente** (0.00–1.00 paso 0.01, 11 regímenes,
      `scripts/umbral.py`) en 0.65, 0.58, 0.50, 0.63, 0.64 y **0.43**, comparados
      los dos intervalos que dan 8/10 y **configurado en 0.43** (corrida
      `20261028_0848`).
- [x] Documentar etapa 5: preguntas 1–3 antes/después, comentarios del usuario,
      trampa de 120 días con regla 10 y control de regla 1 retirada/restaurada.
      Resultados y limitaciones reales en `pruebas/antes-despues.md`; se declara
      que regla 10 no corrigió la premisa y que no hubo alucinación sin regla 1.
      La diferencia entre las reglas adicionales acordadas y el requisito base
      de dos reglas queda explícita, no se presenta como cumplimiento exacto.
- [x] Implementar y evaluar el nodo extra con rutas antes/después en dos preguntas;
      explicar por qué, para qué y qué hace. Se eligió `reformular`; no hubo mejora
      sustantiva global: resultado, diagramas, prompt y limitaciones en
      `pruebas/nodo-extra.md`. La rúbrica permite documentar honestamente si no mejora.
- [ ] Registrar todos los prompts exactos de OpenCode con sus correcciones y los
      efectivos del agente: SYSTEM_PROMPT, USER_PROMPT y prompt del nodo extra.
      **Sección de prompts compilada** en `pruebas/prompts.md` a partir de los
      textos fuente y las transcripciones disponibles; los prompts efectivos
      finales están listos para pegar en el DOCX. La incorporación al documento
      Word final sigue pendiente junto con el resto de la consolidación.
- [ ] Añadir una conclusión corta por etapa, incluida cualquier limitación observada.
- [ ] Si se opta al bonus, repetir la misma batería con FAISS y compararla con Redis.
- [ ] Guardar capturas legibles de las demos y de una ejecución con `--saltos`.
- [x] Incorporar el PDF proporcionado en `docs/` y verificar su integridad y texto.
- [ ] Copiar `docs/LEY-19628_28-AGO-1999_refundida_20261201.pdf` a `proyecto/docs/`
      al consolidar la entrega final, conservando su nombre real.
- [x] Implementar `scripts/indice_vs_coseno.py` y sus pruebas automatizadas.
- [ ] Incorporar las salidas reales completas de la comparación por tamaños
      cuando termine la ejecución; no confundir esta instrucción 03 con haber
      completado la etapa de comparación de chunks de la rúbrica.
- [ ] Actualizar `requirements.txt` desde `uv.lock` con
      `uv export --locked --no-dev --no-emit-project --output-file requirements.txt`.
- [ ] Copiar el código final a `proyecto/`: `AGENTS.md`, `main.py`,
      `requirements.txt`, `.env.example`, `README.md`, `src/`, `scripts/`,
      `tests/`, `docs/`, `compose.yaml`, `pyproject.toml`, `uv.lock`,
      `.python-version` y `.gitignore`; incluir las instrucciones sin secretos
      para poder reconstruir el desarrollo.
- [ ] No copiar recursivamente la raíz completa: excluir `entrega/`, `.git/`,
      `.venv/`, `.env`, cachés, secretos, logs sensibles e índices o `data/` pesado.
- [ ] Verificar los integrantes, objetivo y fechas en cada `.md` y `.py`
      propio, incluidos los archivos que se agreguen en etapas posteriores.
- [ ] Construir `documento-entrega.docx` a partir de todas las instrucciones y evidencias.
- [ ] Probar la copia de `proyecto/` con un entorno nuevo y sin claves incluidas.
- [ ] Crear el ZIP con `documento-entrega.docx`, `pruebas/` y `proyecto/`
      directamente en su raíz; revisar su contenido antes de entregar.

## Fechas de los archivos

Formato local de 24 horas: `YYYYMMDD_hhmm`. En los archivos existentes se tomó
la creación del sistema de archivos local; no es una fecha histórica de autoría
garantizada tras copias o clonaciones. Desde esta preparación, conservar el campo
`fecha_hora_creacion` y actualizar `fecha_hora_modificacion` al editar el contenido.
Los comentarios no cambian la lógica de los módulos Python.

## Verificación de esta preparación

- Directorios y tres tablas de evidencias creados, con etapas pendientes explícitas.
- `requirements.txt` exportado en la raíz desde `uv.lock` con el comando del checklist;
  regenerarlo al terminar si cambian las dependencias.
- Validados integrantes, objetivo y formato de ambas fechas en los **23 archivos
  `.md` y `.py`** propios presentes al preparar la entrega.
- `uv run python -m unittest discover -s tests -v`: **19 pruebas aprobadas**.
- No se generaron ZIP ni documento final; no se copiaron secretos, entornos ni índices.
