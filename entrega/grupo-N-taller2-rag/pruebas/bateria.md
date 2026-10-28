<!--
Integrantes: Fabio Durán; Gustavo Reyes; Ezequiel Muñoz
Objetivo: registrar la batería de diez preguntas y los resultados reales de la etapa 4.
fecha_hora_creacion: 20261027_1858
fecha_hora_modificacion: 20261028_1602
-->

# Batería de diez preguntas — etapa 4

**Estado vigente — instrucción 11 (20261028): UMBRAL=0.43, TOP_K=4,
chunks 800/120.** Consolidación al final; las tablas anteriores son históricas.

Estado: **ejecutada dos veces (20261027_2059 con `UMBRAL=0.65` y 20261027_2158 con `UMBRAL=0.58`)**.

Estado actualizado **20261028_0807**: el set se ejecutó **seis veces**. El
`UMBRAL` quedó **confirmado en 0.58 por decisión del usuario** y se recalculó la
batería completa sobre el corpus vigente (corrida 6, 20261028_0804). Las tablas
de las ejecuciones 1 y 2 se conservan **íntegras y sin modificar** como registro
de lo medido el 20261027; lo nuevo se añade en la sección
[**Actualización 20261028**](#actualización-20261028--decisión-de-umbral-058-y-recálculo)
al final del documento.

Estado final **20261028_0849**: el set se ejecutó **nueve veces**. Tras un
**barrido exhaustivo de `UMBRAL`** y la activación de la **regla 5 (sujeto/país)**
del `SYSTEM_PROMPT`, la configuración vigente pasó a **`UMBRAL = 0.43`**:
8/10 rutas, **0 falsos negativos** y **0 alucinaciones**. Todo el desarrollo de
ese cambio está en la sección final
[**Barrido exhaustivo y configuración final**](#barrido-exhaustivo-de-umbral-y-configuración-final-20261028);
las nueve corridas se conservan sin borrar ninguna.

Grupo: **N (confirmado)**. Integrantes: Fabio Durán, Gustavo Reyes, Ezequiel Muñoz.

Las preguntas y las respuestas esperadas fueron aprobadas antes de ejecutar.
Evidencia cruda:
- `capturas/bateria_20261027_2059.json` — ejecución 1 (`UMBRAL=0.65`).
- `capturas/bateria_20261027_2158_umbra058.json` — ejecución 2 (`UMBRAL=0.58`).
- `capturas/bateria_20261027_2357_umbra058.json` — ejecución 3 (`UMBRAL=0.58`, troceado corregido).
- `capturas/bateria_20261028_0008_umbra05.json` — ejecución 4 (`UMBRAL=0.50`, troceado corregido).
- `capturas/bateria_20261028_0012_umbra063.json` — ejecución 5 (`UMBRAL=0.63`, troceado corregido).
- `capturas/bateria_20261028_0804_umbra058.json` — ejecución 6 (`UMBRAL=0.58` con la regla 5 aún no aplicada).
- `capturas/bateria_20261028_0836_umbra05.json` — ejecución 7 (`UMBRAL=0.50`, regla 5 activa).
- `capturas/bateria_20261028_0841_umbra064.json` — ejecución 8 (`UMBRAL=0.64`, regla 5 activa).
- `capturas/bateria_20261028_0848_umbra043.json` — ejecución 9 (**`UMBRAL=0.43` configuración final**, regla 5 activa).

Ambos ficheros contienen la salida completa de los 10 grafos: nodos,
`mejor_parecido`, fragmentos y respuesta íntegra.

> **Las dos tablas siguientes corresponden a la ejecución 1 (`UMBRAL=0.65`).**
> La ejecución 2 con `UMBRAL=0.58` está en su propia sección más abajo, con la
> comparación de qué cambió en cada pregunta. Las tablas de la ejecución 1 se
> conservan **sin modificar** como registro de lo medido ese día.

## Condiciones de ejecución (reproducibles)

### Ejecución 1 — `UMBRAL=0.65` (20261027_2059)

| Elemento | Valor |
| --- | --- |
| Fecha/hora | 20261027_2059 |
| Comando | `uv run python data/_ejecutar_bateria.py` (invoca `graph.stream` con `thread_id` distinto por pregunta) |
| Corpus | `docs/LEY-19628_28-AGO-1999_refundida_20261201.pdf`, 57 páginas, 318 fragmentos |
| Backend / índice | Redis (`VECTOR_STORE=redis`, `PREFIJO=etmunoz_ollama`) |
| Embeddings / LLM | `bge-m3` (1024 dim) / `qwen3:8b` con `MODEL_PROVIDER=ollama` |
| Chunks | `CHUNK_SIZE=800`, `CHUNK_OVERLAP=120` |
| `TOP_K` / `UMBRAL` | 3 / 0.65 |
| Métrica | Similitud coseno (`1 - distancia`), 4 decimales |
| Páginas | Numeración impresa 1–57 = `metadata['page']` (1-based) |
| Prompt | `SYSTEM_PROMPT`/`USER_PROMPT` de `src/rag/prompts.py`, modificado 20261027_2015 |

### Ejecución 2 — `UMBRAL=0.58` (20261027_2158)

Idéntica a la anterior salvo dos campos:

| Elemento | Valor |
| --- | --- |
| Fecha/hora | 20261027_2158 |
| `UMBRAL` | **0.58** (cambiado en `.env`, `.env.example` y el default de `src/rag/config.py`) |
| Comando | `uv run python data/_bateria_058.py` (mismas 10 preguntas, mismo `thread_id`-prefijo por pregunta) |
| Corpus, backend, modelos, chunks, `TOP_K` | Sin cambios |

## Resultado general

### Ejecución 1 (`UMBRAL=0.65`)

| Ruta esperada | Ruta obtenida | Preguntas |
| --- | --- | --- |
| `responder` (1–5, 9–10) | `responder` | 1, 3, 4, 9, 10 |
| `responder` (1–5) | `no_se` ← **falso negativo** | **2, 5** |
| `no_se` (6–8) | `no_se` | 6, 7, 8 |

**8 de 10 rutas correctas.** Las dos fallas son falsos negativos por `UMBRAL`.

### Ejecución 2 (`UMBRAL=0.58`)

| Ruta esperada | Ruta obtenida | Preguntas |
| --- | --- | --- |
| `responder` (1–5, 9–10) | `responder` | 1, 2, 3, 4, 9, 10 |
| `responder` (1–5) | `no_se` ← **falso negativo** | **5** |
| `no_se` (6–8) | `responder` ← **cambio de ruta** | **6, 8** |
| `no_se` (6–8) | `no_se` | 7 |

**7 de 10 rutas correctas.** Detalle y balance en la sección de reejecución.

## Tabla completa

### Preguntas 1–5 · dentro del contexto

| Nº | Pregunta | Respuesta esperada y fuente/página | Respuesta obtenida | Fragmentos/citas recuperados | Parecido (métrica/valor) | Nodos (--saltos) | Evaluación | Evidencia |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | ¿Cuáles son los derechos que tiene el titular de los datos personales? | Acceso, rectificación, supresión, oposición, portabilidad y **bloqueo**; personales, intransferibles e irrenunciables. **Art. 4°, p. 6** | "…derecho de acceso [1 p.4], de rectificación [1 p.4], de supresión [1 p.4], de oposición [1 p.4], a la portabilidad [1 p.4], a la confirmación [2 p.6], y a la información sobre el tratamiento [2 p.6]" | p.4 (0.7285), p.6 (0.7203), p.5 (0.7166); citó los fragmentos 1 y 2 | **0.7285** | `buscar → responder` | **Parcial**: 5 de 6 derechos; **omite "bloqueo"** (estaba en p.6, el fragmento 2) y añade confirmación/información (Art. 5°, no Art. 4°). **Citas malformadas** `[1 p.4]` en vez de `[LEY-19628 p.4]` | `capturas/bateria_20261027_2059.json` |
| 2 | ¿Qué establece el principio de proporcionalidad? | Datos limitados a los necesarios, adecuados y pertinentes para los fines; conservarse solo el tiempo necesario. **Art. 3° lit. c), p. 5** | "No encontré evidencia en los documentos para responder eso." | **p.5 (0.5850)** ← contiene literalmente la respuesta; p.50 (0.4232), p.4 (0.4125) | **0.5849** | `buscar → no_se` | **FALLO por UMBRAL**: el fragmento correcto fue el **primer** resultado, pero 0.5850 < 0.65 y se descartó. La evidencia existía | `capturas/bateria_20261027_2059.json` |
| 3 | ¿En qué casos procede la supresión de los datos personales? | Seis causales: innecesarios, consentimiento revocado, ilícita, caducos, sentencia/resolución/obligación, oposición sin otro fundamento. **Art. 7°, p. 7** | Cuatro causales citadas: revocado [LEY-19628 p.7], ilícita [p.7], sentencia/resolución/obligación [p.7], oposición [p.7] | p.7 (0.6848), p.19 (0.6836), p.5 (0.6546) | **0.6848** | `buscar → responder` | **Parcial**: 4 de 6 causales; **faltan "innecesarios" (a) y "caducos" (d)**. Página correcta y **citas bien formadas** `[LEY-19628 p.7]` | `capturas/bateria_20261027_2059.json` |
| 4 | ¿Qué se entiende por anonimización? | Procedimiento irreversible por el que un dato no puede vincularse a una persona determinada ni permitir su identificación. **Art. 2° lit. k), p. 3** | "Anonimización es un procedimiento irreversible mediante el cual un dato personal no puede vincularse o asociarse a una persona determinada, ni permitir su identificación, por haberse destruido o eliminado el nexo con la información… **[LEY-19628 p.3]**" | p.3 (0.6533), p.29 (0.5581), p.20 (0.5183) | **0.6533** | `buscar → responder` | **CORRECTA**: coincide con el texto legal, página exacta y **cita bien formada**. Margen al umbral: +0.0033 | `capturas/bateria_20261027_2059.json` |
| 5 | ¿Qué es el derecho de acceso? | Confirmación de tratamiento, acceso a los datos y a la información prevista en la ley. **Art. 2° lit. q), p. 4** y **Art. 5°, p. 6** | "No encontré evidencia en los documentos para responder eso." | **p.4 (0.5361)** ← contiene literalmente la definición; p.6 (0.5213), p.6 (0.5040) | **0.5361** | `buscar → no_se` | **FALLO por UMBRAL**: el mejor fragmento es exactamente la fuente esperada, pero 0.5361 < 0.65. Peor falso negativo de la batería | `capturas/bateria_20261027_2059.json` |

### Preguntas 6–8 · fuera del contexto (esperado: `no_se`, sin inventar)

| Nº | Pregunta | Respuesta esperada y fuente/página | Respuesta obtenida | Fragmentos/citas recuperados | Parecido (métrica/valor) | Nodos (--saltos) | Evaluación | Evidencia |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 6 | ¿Qué establece el GDPR de la Unión Europea sobre los encargados de tratamiento? | Sin respuesta en el corpus. Esperado `no_se` o contexto insuficiente, **sin inventar** el texto del GDPR | "No encontré evidencia en los documentos para responder eso." | p.52 (0.6286), p.3 (0.6121), p.11 (0.6033) | **0.6286** | `buscar → no_se` | **CORRECTA**: rechazó sin alucinar. **Atención**: 0.6286 está a solo 0.0214 del umbral | `capturas/bateria_20261027_2059.json` |
| 7 | ¿Cómo se configura la replicación en Redis Cluster? | Sin respuesta en el corpus. Esperado `no_se` o contexto insuficiente | "No encontré evidencia en los documentos para responder eso." | p.10 (0.3636), p.10 (0.3480), p.43 (0.3479) | **0.3636** | `buscar → no_se` | **CORRECTA**: rechazo cómodo, muy alejado del umbral | `capturas/bateria_20261027_2059.json` |
| 8 | ¿Cuál es la multa máxima que aplica la autoridad de protección de datos de Argentina? | Sin respuesta en el corpus (otra jurisdicción). Esperado `no_se` | "No encontré evidencia en los documentos para responder eso." | p.49 (0.6104), p.43 (0.5922), p.44 (0.5855) | **0.6104** | `buscar → no_se` | **CORRECTA**: rechazó sin alucinar. **Atención**: 0.6104 está a 0.0396 del umbral | `capturas/bateria_20261027_2059.json` |

### Preguntas 9–10 · ambiguas (esperado: `responder` + aclarar la ambigüedad)

| Nº | Pregunta | Respuesta esperada y fuente/página | Respuesta obtenida | Fragmentos/citas recuperados | Parecido (métrica/valor) | Nodos (--saltos) | Evaluación | Evidencia |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 9 | ¿Qué plazo tiene el responsable para responder al titular? | No hay un plazo único. Esperado: decir que varía según el derecho y el artículo, citando **Art. 5°/7°, pp. 6–7**; **no** fijar un número de días no escrito | "El responsable tiene un plazo de **treinta días hábiles** para responder al titular [LEY-19628 p.10]." | p.10 (0.7411), p.47 (0.7169), p.10 (0.6909) | **0.7411** | `buscar → responder` | **FALLO de contenido**: p.10 dice **"treinta días *corridos*"** para que el responsable se pronuncie, y **"treinta días *hábiles*"** es el plazo del **titular para reclamar** ante la Agencia (Art. 41). **Mezcló los dos plazos** y no aclaró la ambigüedad. Verificado con `pypdf` contra p.10 | `capturas/bateria_20261027_2059.json` |
| 10 | ¿Qué información debe entregar el responsable? | Distinguir acceso (**Art. 2° q, p. 4**; **Art. 5°, p. 6**) de portabilidad (**Art. 2° u, p. 4**) y decirlo explícitamente | "…toda la información que sea necesaria para el ejercicio de los derechos… y las políticas y prácticas sobre el tratamiento **[LEY-19628 p.5]**. Además, facilitar y mantener la política de tratamiento, su fecha y versión **[LEY-19628 p.13]**" | p.13 (0.7041), p.13 (0.6906), p.5 (0.6894) | **0.7041** | `buscar → responder` | **Parcial**: contenido verificado y citas bien formadas, pero **no distinguió acceso de portabilidad** como se esperaba; respondió en términos de políticas de información (p.13) en vez de los arts. 2° q) y u) | `capturas/bateria_20261027_2059.json` |

## Balance de calidad de respuestas (ejecución 1, con `UMBRAL=0.65`)

| Evaluación | Cantidad | Preguntas |
| --- | --- | --- |
| Correcta | 4 | 4 (en contexto), 6, 7, 8 (fuera de contexto) |
| Parcial | 3 | 1, 3, 10 |
| Fallo por `UMBRAL` (falso negativo) | 2 | 2, 5 |
| Fallo de contenido | 1 | 9 |
| Alucinación sobre dato ausente del corpus | **0** | — |

Dos defectos de formato observados en el prompt (candidatos a la etapa 5):
citas malformadas `[1 p.4]` (pregunta 1) e incompletas en la pregunta 2.

## Reejecución con `UMBRAL=0.58` — 20261027_2158

Se cambió `UMBRAL` de 0.65 a 0.58 en `.env` (y en `.env.example` y en el valor
por defecto de `src/rag/config.py`) y se volvieron a ejecutar las **mismas diez
preguntas**, con idéntico corpus, backend, modelos, `TOP_K=3` y `CHUNK_SIZE=800`.
Evidencia: `capturas/bateria_20261027_2158_umbra058.json`.

### Qué cambió realmente

Al subir el umbral a 0.6286 y bajarlo a 0.58, **seis de las diez rutas se
modifican o se mantienen por razones distintas**. Conviene verlo pregunta a
pregunta, porque el efecto neto **no** es el esperado:

| Nº | Parecido | Ruta con 0.65 | Ruta con 0.58 | Qué pasó |
| --- | --- | --- | --- | --- |
| 1 | 0.7285 | `responder` (parcial) | `responder` (parcial) | Sin cambio: sigue omitiendo "bloqueo" y citando `[1 p.4]` |
| 2 | 0.5850 | `no_se` | **`responder`** | **Empeoró**: ya no dice "no sé", ahora contesta **mal** (da el literal b) en vez del c) |
| 3 | 0.6848 | `responder` (parcial) | `responder` (parcial) | Sin cambio: 4 de 6 causales |
| 4 | 0.6533 | `responder` (correcta) | `responder` (correcta) | Sin cambio |
| 5 | 0.5361 | `no_se` | `no_se` | **No mejoró**: 0.5361 sigue bajo 0.58. Falsa negativa persistente |
| 6 | 0.6286 | `no_se` (correcta) | **`responder`** | **Riesgo asumido**, pero el modelo **declinó bien**: *"El contexto no incluye información sobre el GDPR"* |
| 7 | 0.3636 | `no_se` (correcta) | `no_se` | Sin cambio |
| 8 | 0.6104 | `no_se` (correcta) | **`responder`** | **Empeoró**: contesta atribuyendo a Argentina una cifra **chilena** (Art. 44, p.49) |
| 9 | 0.7411 | `responder` (incorrecta) | `responder` (incorrecta) | Sin cambio: sigue mezclando "corridos" y "hábiles" |
| 10 | 0.7041 | `responder` (parcial) | `responder` (parcial) | Sin cambio |

### Tabla de resultados con `UMBRAL=0.58`

Mismas columnas que la tabla superior; solo cambia lo que el umbral altera.

| Nº | Pregunta | Respuesta esperada y fuente/página | Respuesta obtenida | Fragmentos/citas recuperados | Parecido (métrica/valor) | Nodos (--saltos) | Evaluación | Evidencia |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | ¿Cuáles son los derechos que tiene el titular de los datos personales? | Acceso, rectificación, supresión, oposición, portabilidad y **bloqueo**. **Art. 4°, p. 6** | Mismos derechos que en la ejecución 1, con `[1 p.4]` y `[2 p.6]` | p.4 (0.7285), p.6 (0.7203), p.5 (0.7166) | **0.7285** | `buscar → responder` | **Parcial, sin cambio**: omite "bloqueo"; **citas malformadas** | `capturas/bateria_20261027_2158_umbra058.json` |
| 2 | ¿Qué establece el principio de proporcionalidad? | Datos limitados a los necesarios, adecuados y pertinentes. **Art. 3° lit. c), p. 5** | "El principio de proporcionalidad establece que el titular otorgue nuevamente su consentimiento, y cuando lo disponga la ley **[1]**" | p.5 (0.5850) — **mide 125 car. y se corta justo en el encabezado `c) Principio de proporcionalidad`**; p.50 (0.4232), p.4 (0.4125) | **0.5850** | `buscar → no_se` → **`buscar → responder`** | **EMPEORÓ**: pasa el umbral pero **contesta con el literal b)**, no el c). El contenido del literal c) **no está en el fragmento** (medido con `--texto`); la cita `[1]` es aún más incompleta que antes | `capturas/bateria_20261027_2158_umbra058.json` |
| 3 | ¿En qué casos procede la supresión de los datos personales? | Seis causales. **Art. 7°, p. 7** | Cuatro causales con `[LEY-19628 p.7]` | p.7 (0.6848), p.19 (0.6836), p.5 (0.6546) | **0.6848** | `buscar → responder` | **Parcial, sin cambio**: faltan "innecesarios" y "caducos"; citas bien formadas | `capturas/bateria_20261027_2158_umbra058.json` |
| 4 | ¿Qué se entiende por anonimización? | Procedimiento irreversible. **Art. 2° lit. k), p. 3** | Texto legal completo con `[LEY-19628 p.3]` | p.3 (0.6533), p.29 (0.5581), p.20 (0.5183) | **0.6533** | `buscar → responder` | **CORRECTA, sin cambio** | `capturas/bateria_20261027_2158_umbra058.json` |
| 5 | ¿Qué es el derecho de acceso? | Confirmación, acceso e información. **Art. 2° lit. q), p. 4** y **Art. 5°, p. 6** | "No encontré evidencia en los documentos para responder eso." | **p.4 (0.5361)** ← contiene la definición; p.6 (0.5213), p.6 (0.5040) | **0.5361** | `buscar → no_se` | **SIN MEJORA**: falsa negativa **persiste**. 0.5361 < 0.58 | `capturas/bateria_20261027_2158_umbra058.json` |
| 6 | ¿Qué establece el GDPR de la Unión Europea sobre los encargados de tratamiento? | Sin respuesta en el corpus. Esperado `no_se` sin inventar | *"El contexto proporcionado no incluye información sobre el GDPR de la Unión Europea ni sobre los encargados de tratamiento. Por lo tanto, no es posible responder…"* | p.52 (0.6286), p.3 (0.6121), p.11 (0.6033) | **0.6286** | `buscar → no_se` → **`buscar → responder`** | **Ruta cambió, contenido correcto**: la regla 3 del prompt cubrió el caso. **Sin alucinación** | `capturas/bateria_20261027_2158_umbra058.json` |
| 7 | ¿Cómo se configura la replicación en Redis Cluster? | Sin respuesta en el corpus. Esperado `no_se` | "No encontré evidencia en los documentos para responder eso." | p.10 (0.3636), p.10 (0.3480), p.43 (0.3479) | **0.3636** | `buscar → no_se` | **CORRECTA, sin cambio** | `capturas/bateria_20261027_2158_umbra058.json` |
| 8 | ¿Cuál es la multa máxima que aplica la autoridad de protección de datos de Argentina? | Sin respuesta en el corpus. Esperado `no_se` | *"La multa máxima que aplica la autoridad de protección de datos de Argentina es el cincuenta por ciento de la remuneración mensual del jefe superior del órgano público… **[LEY-19628 p.49]**"* | p.49 (0.6104), p.43 (0.5922), p.44 (0.5855) | **0.6104** | `buscar → no_se` → **`buscar → responder`** | **EMPEORÓ — alucinación de jurisdicción**: la cifra **es real pero es chilena** (Art. 44, órganos públicos); *"Argentina"* **no aparece en las 57 páginas** (verificado con `pypdf`). La cita parece válida, lo que lo hace más peligroso | `capturas/bateria_20261027_2158_umbra058.json` |
| 9 | ¿Qué plazo tiene el responsable para responder al titular? | No hay plazo único; no fijar un número no escrito. **Art. 5°/7°, pp. 6–7** | "El responsable tiene un plazo de **treinta días hábiles** para responder al titular [LEY-19628 p.10]." | p.10 (0.7411), p.47 (0.7169), p.10 (0.6909) | **0.7411** | `buscar → responder` | **FALLO de contenido, sin cambio**: p.10 dice **corridos** para el responsable; **hábiles** es el plazo del titular para reclamar | `capturas/bateria_20261027_2158_umbra058.json` |
| 10 | ¿Qué información debe entregar el responsable? | Distinguir acceso (**Art. 2° q, p. 4**; **Art. 5°, p. 6**) de portabilidad (**Art. 2° u, p. 4**) | Políticas de tratamiento con `[LEY-19628 p.5]` y `[LEY-19628 p.13]` | p.13 (0.7041), p.13 (0.6906), p.5 (0.6894) | **0.7041** | `buscar → responder` | **Parcial, sin cambio**: no distingue acceso de portabilidad | `capturas/bateria_20261027_2158_umbra058.json` |

### Comparación de los dos balances

| Evaluación | Con 0.65 (ejecución 1) | Con 0.58 (ejecución 2) |
| --- | --- | --- |
| Correcta | 4 (4, 6, 7, 8) | **3** (4, 7 y la 6 por declinación) |
| Parcial | 3 (1, 3, 10) | 3 (1, 3, 10) |
| Fallo por `UMBRAL` (falso negativo) | 2 (2, 5) | **1** (5) |
| Fallo de contenido | 1 (9) | **3 (2, 8, 9)** |
| Alucinación sobre dato ausente | 0 | **1 (8)** |
| Rutas correctas esperadas | 8/10 | **7/10** |

### Lectura de la reejecución

1. **El resultado neto empeoró.** Las rutas correctas bajaron de 8/10 a 7/10 y
   las respuestas con contenido incorrecto subieron de 1 a 3.
2. **Dos regresiones concretas.** La pregunta 8 pasó de rechazo correcto a
   alucinación de jurisdicción; la 2 pasó de "no sé" a respuesta errónea. En los
   dos casos, **bajar el umbral convirtió un acierto en un error**.
3. **Una falsa negativa no se arregló.** La 5 (0.5361) sigue bloqueada: el rango
   de mejora real estaba más abajo de lo propuesto.
4. **La regla 3 del prompt sí protege parcialmente.** La 6 entró a `responder` y
   el modelo declinó correctamente. Pero **no protege** cuando el contexto es
   temáticamente parecido y de sujeto equivocado (la 8), que es justo el caso
   que la regla actual no menciona.
5. **Corrección de una recomendación previa.** Se había anticipado que 0.58
   "mantendría fuera a la 6 y la 8" y que "ganaría las 11, 12 y 13". Los datos
   lo desmienten: 6 (0.6286) y 8 (0.6104) están **por encima** de 0.58, y 12
   (0.5523) y 13 (0.5649) quedan **por debajo**. La predicción falló en cuatro
   de cinco casos.
6. **Diagnóstico de la causa 2 (no es un problema de umbral).** El TOP_1 de esa
   pregunta mide 125 caracteres y termina justo en el encabezado del literal c);
   el contenido real está en el siguiente fragmento, que no entró en el `TOP_K`.
   Ningún valor de `UMBRAL` lo arregla: hace falta corregir el troceado.

## Elección de TOP_K y UMBRAL con datos

| TOP_K probado | UMBRAL probado | Preguntas/resultados que lo sustentan | Elección y justificación | Evidencia |
| --- | --- | --- | --- | --- |
| 1 | 0.65 | — | **Descartado sin ejecutar**: en la pregunta 1 la fuente esperada (p.6) fue el **fragmento 2** (0.7203) y en la 10 se citó el **fragmento 3** (p.5, 0.6894). Con `TOP_K=1` ambos se pierden | Tabla de preguntas 1 y 10 |
| 3 | 0.65 | 1, 3, 4, 6, 7, 8, 9, 10 → ruta correcta | **Ejecutado**: 8/10 rutas correctas; las 2 fallas (2 y 5) dependen de `UMBRAL`, no de `TOP_K` | `capturas/bateria_20261027_2059.json` |
| 3 | 0.53 (calculado, **no ejecutado**) | Capturaría 2 (0.5850) y 5 (0.5361), pero dejaría pasar 6 (0.6286) y 8 (0.6104) a `responder` | **También 8/10**, con el mismo puntaje pero fallo más riesgoso. Queda **propuesto, no probado** | Cálculo sobre los 10 parecidos de la tabla |
| 3 | **0.58 (ejecutado 20261027_2158)** | 1, 2, 3, 4, 6, 8, 9, 10 → `responder`; 5 y 7 → `no_se` | **Empeora**: 7/10 rutas correctas, sube de 1 a 3 las respuestas con contenido incorrecto (2 y 8 pasan de acierto a error) y aparece **1 alucinación de jurisdicción** (8). Único avance: se reduce de 2 a 1 los falsos negativos (mejora solo la 2 en ruta, pero su respuesta es errónea) | `capturas/bateria_20261027_2158_umbra058.json` |

**Separación entre clases:** con `bge-m3`, los parecidos **no son separables**.
Las en-contexto 2 (0.5850) y 5 (0.5361) quedan **por debajo** de las
fuera-de-contexto 6 (0.6286) y 8 (0.6104). Ningún umbral distingue ambas clases
con estos datos.

**Configuración vigente en ese momento:** `UMBRAL=0.58` (elegido y aplicado el
20261027_2158). *Hoy es `0.43`: ver la sección final "Barrido exhaustivo de
`UMBRAL` y configuración final".*

**Comparación de las dos ejecuciones con datos:**

| Umbral | Rutas correctas | Respuestas incorrectas | Alucinaciones | Falsos negativos |
| --- | --- | --- | --- | --- |
| 0.65 (ejecución 1) | **8/10** | 1 (9) | **0** | 2 (2, 5) |
| 0.58 (ejecución 2) | 7/10 | **3 (2, 8, 9)** | **1 (8)** | 1 (5) |
| 0.53 (solo cálculo) | — | no ejecutado | se prevee riesgo en 6 y 8 | — |

**Lectura honesta:** con las diez preguntas, **0.65 obtuvo el mejor balance** y
0.58 lo empeora. Bajarlo redujo los falsos negativos de 2 a 1, pero convirtió dos
aciertos en errores (la 2 y la 8) y produjo la primera alucinación de la batería.
La mejora de la 2 en ruta es engañosa: su TOP_1 mide 125 caracteres y se corta en
el encabezado del literal c), así que **contesta mal en vez de no contestar**.

**Vigente = 0.58 por decisión del usuario**, pese a que los datos favorecen a
0.65. Se deja constancia para que la decisión final de la etapa 4 se tome con
esta comparación a la vista. La vía prometedora **no** es el umbral, sino
corregir el troceado (pregunta 2) y añadir una regla de sujeto al prompt
(pregunta 8).

**`TOP_K=3` elegido:** en 2 de 10 respuestas el contenido citado vino del
fragmento 2 o 3, no del primero.

## Bonus opcional: misma batería con FAISS (+10)

Repetir las diez preguntas sin cambiarlas, con el mismo corpus, modelos,
chunks y parámetros. Registrar la configuración y versión de ambos índices.
No basta con la demo de tres frases para acreditar esta comparación.

| Nº de pregunta | Ruta / parecido / respuesta / cita en Redis | Ruta / parecido / respuesta / cita en FAISS | Diferencias y evidencia |
| --- | --- | --- | --- |
| 1–10 (una fila por pregunta al ejecutar) | **Ejecutadas** (arriba) | No ejecutada | Pendiente |

## Conclusiones

Resultado de la **ejecución 1 (20261027_2059, `UMBRAL=0.65`)**:

1. **El grafo cumple la ruta en 8 de 10 casos** y las 3 preguntas fuera de
   contexto se rechazaron sin alucinar (ninguna invención de GDPR, Redis o
   norma argentina).
2. **`UMBRAL=0.65` genera dos falsos negativos graves** (preguntas 2 y 5): el
   fragmento con la respuesta literal era el primer resultado y se descartó.
   Los parecidos de `bge-m3` no separan las dos clases de preguntas.
3. **`TOP_K=3` está justificado por datos**: 2 respuestas citaron el fragmento
   2 o 3.
4. **Defecto de contenido serio en la pregunta 9**: el modelo mezcló los
   plazos de "corridos" y "hábiles" de la misma página 10. Se verificó contra
   el PDF; el error es del modelo, no de la recuperación.
5. **Calidad de citas desigual**: `LEY-19628 p.N` bien formada en las preguntas
   3, 4, 9 y 10; malformada `[1 p.4]` en la 1. Prompt a pulir en la etapa 5.
6. **Etapa 5 queda motivada con evidencia concreta**: al menos dos cambios de
   regla posibles (formato de cita y manejo de plazos/ambigüedad) sobre las
   mismas preguntas 1, 2 y 9.

Resultado de la **ejecución 2 (20261027_2158, `UMBRAL=0.58`)**:

7. **El balance empeoró**: de 8/10 a 7/10 rutas correctas, y de 1 a 3 las
   respuestas con contenido incorrecto.
8. **Dos regresiones concretas**: la pregunta 8 pasó de rechazo correcto a
   **alucinación de jurisdicción** (cifra chilena del Art. 44 atribuida a
   Argentina; "Argentina" no aparece en el corpus), y la 2 pasó de "no sé" a
   **respuesta errónea**. Bajar el umbral convirtió aciertos en errores.
9. **Un solo avance neto**: la 2 mejoró su ruta, pero su respuesta quedó
   incorrecta; la 5 (0.5361) **sigue bloqueada**, de modo que la mejora esperada
   no se materializó en calidad.
10. **La regla 3 del prompt protege solo a medias**: la 6 entró a `responder` y
    el modelo declinó bien, pero no evitó el fallo de la 8, donde el contexto es
    temáticamente parecido y de sujeto equivocado. Ese caso exige una regla
    explícita de sujeto/país/norma.
11. **Corrección de una predicción previa**: se había anticipado que 0.58
    mantendría fuera a 6 y 8 y que ganaría 11, 12 y 13. Los datos lo desmienten
    en cuatro de cinco casos; queda registrado para no repetir el error.

Hallazgo transversal (no depende del umbral):

12. **El troceado parte contenido de sus encabezados.** El TOP_1 de la pregunta
    2 mide 125 caracteres y termina justo en `c) Principio de proporcionalidad`;
    el literal completo está en el siguiente fragmento, fuera del `TOP_K`. Es la
    causa de que bajar el umbral produzca respuestas erróneas. **Corregir el
    troceado (o filtrar fragmentos degenerados, como el de 83 caracteres de la
    pregunta 12) es previo a cualquier ajuste de umbral.**

Estado: `UMBRAL=0.58` era la configuración **vigente** (decisión del usuario).
Los datos de ambas ejecuciones quedan a la vista para la decisión final de la
etapa 4. *Actualizado el 20261028: la configuración vigente pasó a `0.43` tras
el barrido exhaustivo; ver la última sección de este documento.*

---

# Actualización 20261028 — decisión de `UMBRAL = 0.58` y recálculo

**Decisión del usuario (20261028): se mantiene `UMBRAL = 0.58`.**
No hubo que editar código: `.env` (línea 11), `.env.example` (línea 18) y el
default de `src/rag/config.py` (línea 55) ya tenían `0.58`, y `get_settings()`
lo devuelve tal cual. Se recalculó después la batería completa sobre el corpus
vigente.

Todo lo que sigue se **añade**; las tablas de las ejecuciones 1 y 2 de más
arriba no se modificaron.

## Las seis corridas

| # | Fecha/hora | `UMBRAL` | Troceado | Fragmentos | Rutas correctas | Falsos negativos | Alucinaciones | Evidencia |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| 1 | 20261027_2059 | 0.65 | original | 318 | **8/10** | 2 (2, 5) | 0 | `capturas/bateria_20261027_2059.json` |
| 2 | 20261027_2158 | 0.58 | original | 318 | 7/10 | 1 (5) | 1 (8) | `capturas/bateria_20261027_2158_umbra058.json` |
| 3 | 20261027_2357 | 0.58 | **corregido** | 294 | 6/10 | 2 (2, 5) | 1 (8) | `capturas/bateria_20261027_2357_umbra058.json` |
| 4 | 20261028_0008 | 0.50 | corregido | 294 | **8/10** | **0** | 1 (8) | `capturas/bateria_20261028_0008_umbra05.json` |
| 5 | 20261028_0012 | 0.63 | corregido | 294 | **8/10** | 2 (2, 5) | **0** | `capturas/bateria_20261028_0012_umbra063.json` |
| 6 | 20261028_0804 | **0.58 (decisión del usuario)** | corregido | 294 | 6/10 | 2 (2, 5) | 1 (8) | `capturas/bateria_20261028_0804_umbra058.json` |
| 7 | 20261028_0836 | 0.50 + **regla 5** | corregido | 294 | **8/10** | **0** | **0** | `capturas/bateria_20261028_0836_umbra05.json` |
| 8 | 20261028_0841 | 0.64 + **regla 5** | corregido | 294 | **8/10** | 2 (2, 5) | **0** | `capturas/bateria_20261028_0841_umbra064.json` |
| 9 | 20261028_0848 | **0.43 + regla 5 (vigente)** | corregido | 294 | **8/10** | **0** | **0** | `capturas/bateria_20261028_0848_umbra043.json` |

Las corridas 3 y 6 son la **misma configuración** ejecutada en días distintos y
repiten **las 10 rutas y los 10 parecidos exactos**: la recuperación es
determinista. Las respuestas **no** se compararon carácter a carácter, así que
no se afirma que sean idénticas; lo observado visualmente apunta a diferencias
de formato en las citas. Las corridas 7, 8 y 9 son las que decidieron la
configuración final y se detallan en la última sección de este documento.

## Qué cambió en la pregunta 2 al corregir el troceado

| Versión del fragmento TOP_1 de la p.5 | Largo | Parecido | ¿Contiene el literal c)? |
| --- | ---: | ---: | --- |
| Troceado original (corridas 1–2) | 125 car. | **0.5850** | **No**: se cortaba justo en el encabezado `c) Principio de proporcionalidad` |
| Troceado corregido (corridas 3–6) | **829 car.** | **0.5054** | **Sí**, completo y verificado con `--texto` |

El arreglo del troceado **bajó** el parecido (un fragmento más largo diluye la
semejanza) pero **puso la respuesta dentro**. Consecuencia honesta: en el mismo
umbral 0.58 la pregunta 2 pasó de *responder mal* (corrida 2) a *no responder*
(corridas 3 y 6); la mejora real solo se ve al bajar el umbral — en la corrida 4
(0.50) responde **bien**: *"…los datos personales que se traten deben limitarse…"*.

## Tabla de decisión con los parecidos vigentes (troceado corregido)

| Nº | Tipo | Parecido | ¿≥ 0.50? | ¿≥ **0.58**? | ¿≥ 0.63? | Ruta esperada |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | en contexto | 0.7285 | `responder` | `responder` | `responder` | `responder` |
| 2 | en contexto | **0.5054** | `responder` | **`no_se`** | `no_se` | `responder` |
| 3 | en contexto | 0.6848 | `responder` | `responder` | `responder` | `responder` |
| 4 | en contexto | 0.6533 | `responder` | `responder` | `responder` | `responder` |
| 5 | en contexto | **0.5361** | `responder` | **`no_se`** | `no_se` | `responder` |
| 6 | fuera | **0.6286** | `no_se` | **`responder`** | `no_se` | `no_se` |
| 7 | fuera | 0.3636 | `no_se` | `no_se` | `no_se` | `no_se` |
| 8 | fuera | **0.6104** | `no_se` | **`responder`** | `no_se` | `no_se` |
| 9 | ambigua | 0.7411 | `responder` | `responder` | `responder` | `responder` |
| 10 | ambigua | 0.6986 | `responder` | `responder` | `responder` | `responder` |
| | | **Rutas correctas** | **8/10** | **6/10** | **8/10** | |

**Las clases siguen sin separarse.** Las en-contexto 2 (0.5054) y 5 (0.5361)
quedan **por debajo** de las fuera-de-contexto 6 (0.6286) y 8 (0.6104); ningún
valor de `UMBRAL` las distingue con `bge-m3`.

## Ejecución 6 — configuración vigente (20261028_0804)

| Elemento | Valor |
| --- | --- |
| Fecha/hora | 20261028_0804 |
| Comando | `uv run python scripts/bateria.py --umbral 0.58 --etiqueta "UMBRAL=0.58 confirmado por el usuario; troceado corregido (294 fragmentos)"` |
| Corpus | `docs/LEY-19628_28-AGO-1999_refundida_20261201.pdf`, 57 páginas, **294 fragmentos** |
| Backend / índice | Redis (`VECTOR_STORE=redis`, `PREFIJO=etmunoz_ollama`) |
| Embeddings / LLM | `bge-m3` (1024 dim) / `qwen3:8b` con `MODEL_PROVIDER=ollama` |
| Chunks | `CHUNK_SIZE=800`, `CHUNK_OVERLAP=120` |
| `TOP_K` / **`UMBRAL`** | 3 / **0.58** |
| Métrica | Similitud coseno (`1 - distancia`), 4 decimales |
| Salida | `Con respuesta: 10/10` — 7x `buscar → responder`, 3x `buscar → no_se` |

### Tabla completa de la ejecución 6

#### Preguntas 1–5 · dentro del contexto

| Nº | Pregunta | Respuesta esperada y fuente/página | Respuesta obtenida | Fragmentos/citas recuperados | Parecido | Nodos | Evaluación | Evidencia |
| --- | --- | --- | --- | --- | ---: | --- | --- | --- |
| 1 | ¿Cuáles son los derechos que tiene el titular de los datos personales? | Acceso, rectificación, supresión, oposición, portabilidad y **bloqueo**. **Art. 4°, p. 6** | "…derecho de acceso [1 p.4], de rectificación [1 p.4], de supresión [1 p.4], de oposición [1 p.4], a la portabilidad [1 p.4], a la confirmación [2 p.6], y a la información sobre el tratamiento [2 p.6]" | p.4 (0.7285), p.6 (0.7203), p.5 (0.7166) | **0.7285** | `buscar → responder` | **Parcial**: omite "bloqueo"; **citas malformadas** `[1 p.4]` en vez de `[LEY-19628 p.4]` | `capturas/bateria_20261028_0804_umbra058.json` |
| 2 | ¿Qué establece el principio de proporcionalidad? | Datos limitados a los necesarios, adecuados y pertinentes; conservarse solo el tiempo necesario. **Art. 3° lit. c), p. 5** | "No encontré evidencia en los documentos para responder eso." | p.5 (0.5054, **829 car. con el literal c completo**), p.4 (0.4125), p.5 (0.394) | **0.5054** | `buscar → no_se` | **FALLO por UMBRAL**: 0.5054 < 0.58. Contenido **presente** y verificado con `--texto`; es el mejor de los tres falsos negativos | `capturas/bateria_20261028_0804_umbra058.json` |
| 3 | ¿En qué casos procede la supresión de los datos personales? | Seis causales. **Art. 7°, p. 7** | Cuatro causales con `[LEY-19628 p.7]` | p.7 (0.6848), p.19 (0.6836), p.7 (0.6485) | **0.6848** | `buscar → responder` | **Parcial**: 4 de 6; faltan "innecesarios" y "caducos". **Citas bien formadas** | `capturas/bateria_20261028_0804_umbra058.json` |
| 4 | ¿Qué se entiende por anonimización? | Procedimiento irreversible. **Art. 2° lit. k), p. 3** | Texto legal completo con `[LEY-19628 p.3]` | p.3 (0.6533), p.29 (0.5581), p.20 (0.5183) | **0.6533** | `buscar → responder` | **CORRECTA**: coincide con el texto, página exacta, cita bien formada. Margen +0.0733 | `capturas/bateria_20261028_0804_umbra058.json` |
| 5 | ¿Qué es el derecho de acceso? | Confirmación de tratamiento, acceso a los datos y a la información. **Art. 2° lit. q), p. 4** y **Art. 5°, p. 6** | "No encontré evidencia en los documentos para responder eso." | p.4 (0.5361, **343 car. con el literal q**), p.6 (0.5040), p.6 (0.5037) | **0.5361** | `buscar → no_se` | **FALLO por UMBRAL**: 0.5361 < 0.58. Contenido **presente** y verificado con `--texto` | `capturas/bateria_20261028_0804_umbra058.json` |

#### Preguntas 6–8 · fuera del contexto (esperado: `no_se`, sin inventar)

| Nº | Pregunta | Respuesta esperada | Respuesta obtenida | Fragmentos/citas recuperados | Parecido | Nodos | Evaluación | Evidencia |
| --- | --- | --- | --- | --- | ---: | --- | --- | --- |
| 6 | ¿Qué establece el GDPR de la Unión Europea sobre los encargados de tratamiento? | `no_se` o contexto insuficiente, sin inventar el texto del GDPR | *"El contexto proporcionado no incluye información sobre el GDPR de la Unión Europea, por lo que no es posible responder a la pregunta basándose únicamente en los documentos mencionados."* | p.52 (0.6286), p.11 (0.6033), p.17 (0.5982) | **0.6286** | `buscar → responder` | **Ruta distinta, contenido correcto**: declinó sin alucinar (admitido en `docs/preguntas.md`) | `capturas/bateria_20261028_0804_umbra058.json` |
| 7 | ¿Cómo se configura la replicación en Redis Cluster? | `no_se` | "No encontré evidencia en los documentos para responder eso." | p.10 (0.3636), p.10 (0.3480), p.43 (0.3479) | **0.3636** | `buscar → no_se` | **CORRECTA**: rechazo cómodo, muy alejado del umbral | `capturas/bateria_20261028_0804_umbra058.json` |
| 8 | ¿Cuál es la multa máxima que aplica la autoridad de protección de datos de Argentina? | `no_se` (otra jurisdicción) | *"La multa máxima que aplica la autoridad de protección de datos de Argentina es el cincuenta por ciento de la remuneración mensual del jefe superior del órgano público, en el caso de tratarse de datos personales sensibles **[LEY-19628 p.49]**"* | p.49 (0.6104), p.43 (0.5922), p.44 (0.5855) | **0.6104** | `buscar → responder` | **ALUCINACIÓN de jurisdicción**: la cifra es real pero **chilena** (Art. 44); "Argentina" no aparece en las 57 páginas. La cita parece válida, lo que lo hace más peligroso | `capturas/bateria_20261028_0804_umbra058.json` |

#### Preguntas 9–10 · ambiguas (esperado: `responder` + aclarar la ambigüedad)

| Nº | Pregunta | Respuesta esperada | Respuesta obtenida | Fragmentos/citas recuperados | Parecido | Nodos | Evaluación | Evidencia |
| --- | --- | --- | --- | --- | ---: | --- | --- | --- |
| 9 | ¿Qué plazo tiene el responsable para responder al titular? | No hay plazo único; no fijar un número no escrito. **Art. 5°/7°, pp. 6–7** | "El responsable tiene un plazo de **treinta días hábiles** para responder al titular [LEY-19628 p.10]." | p.10 (0.7411), p.47 (0.7169), p.10 (0.6909) | **0.7411** | `buscar → responder` | **FALLO de contenido**: p.10 dice **corridos** para el responsable; **hábiles** es el plazo del titular para reclamar. Verificado contra el PDF | `capturas/bateria_20261028_0804_umbra058.json` |
| 10 | ¿Qué información debe entregar el responsable? | Distinguir acceso (**Art. 2° q, p. 4**) de portabilidad (**Art. 2° u, p. 4**) | "…toda la información necesaria para el ejercicio de los derechos… [1 p.13]. Además, debe facilitar y mantener… la política de tratamiento… [1 p.13]. También debe adoptar medidas adecuadas… [3 p.5]" | p.13 (0.6986), p.13 (0.6906), p.5 (0.6894) | **0.6986** | `buscar → responder` | **Parcial**: no distingue acceso de portabilidad y **citas malformadas** `[1 p.13]`, `[3 p.5]` (en la corrida 1 salían bien formadas: inestabilidad del formato) | `capturas/bateria_20261028_0804_umbra058.json` |

### Balance de la ejecución 6 (configuración vigente)

| Evaluación | Cantidad | Preguntas |
| --- | ---: | --- |
| Correcta | 3 | 4 (en contexto), 7 (rechazo), 6 (declinación correcta) |
| Parcial | 3 | 1, 3, 10 |
| Fallo por `UMBRAL` (falso negativo) | 2 | **2, 5** |
| Fallo de contenido | 1 | 9 |
| Alucinación sobre dato ausente del corpus | **1** | **8** |
| **Rutas correctas** | **6/10** | |

### Los dos falsos negativos son de umbral, no de troceado

Se abrieron los dos fragmentos con `--texto` para confirmarlo:

- **Pregunta 2**, p.5, 0.5054, 829 caracteres → contiene literalmente
  *"c) Principio de proporcionalidad. Los datos personales que se traten deben
  limitarse estrictamente a aquéllos que resulten necesarios, adecuados y
  pertinentes en relación con los fines del tratamiento. Los datos personales
  pueden ser conservados sólo por el período de tiempo que sea necesario…"*
- **Pregunta 5**, p.4, 0.5361, 343 caracteres → contiene literalmente
  *"q) Derecho de acceso: derecho del titular de datos a solicitar y obtener del
  responsable, confirmación acerca de si sus datos personales están siendo
  tratados por él…"*

En ambos casos la evidencia está en el `TOP_K` y **el LLM no llega a ejecutarse**
porque `mejor_parecido < 0.58`. Ningún cambio de prompt puede arreglarlos:
solo el umbral (o un reordenamiento de la recuperación).

## Decisión y su coste medido

| Valor | Rutas | Falsos negativos | Alucinaciones | Limitación |
| --- | ---: | ---: | ---: | --- |
| 0.50 (corrida 4) | 8/10 | **0** | 1 (8) | Deja pasar 6 y 8 a `responder`; la 8 alucina |
| **0.58 (corrida 6, elegido)** | **6/10** | **2 (2, 5)** | **1 (8)** | No aprovecha que 2 y 5 ya contienen la respuesta |
| 0.63 (corrida 5) | 8/10 | 2 (2, 5) | **0** | Los falsos negativos no llegan al LLM: ningún prompt los arregla |

**Decisión registrada: el usuario eligió mantener `UMBRAL = 0.58` el 20261028.**
Con los datos disponibles, 0.58 es el **peor de los tres en rutas** (6/10 frente
a 8/10 de 0.50 y 0.63) y combina los dos problemas a la vez: dos falsos
negativos y una alucinación. Se deja escrito este coste para que la etapa 4 lo
afronte con evidencia y no con una justificación a posteriori.

Lo que **no** resuelve ningún umbral, con estos datos:

1. **La separación de clases**: 6 (0.6286) y 8 (0.6104) superan a 2 (0.5054) y
   5 (0.5361). Hace falta otra señal (filtro de sujeto/jurisdicción en el prompt,
   o reordenamiento) — es la etapa 5.
2. **La alucinación de la pregunta 8**, que aparece en 0.50 y 0.58 y solo se
   evita en 0.63, que a cambio castiga a 2 y 5.
3. **El fallo de contenido de la 9** y el **formato de citas** inestable
   (`[1 p.4]`, `[3 p.5]`): problemas de prompt, etapa 5.

## Conclusiones añadidas (corridas 3–6)

13. **La configuración vigente era `UMBRAL=0.58`, `TOP_K=3`, `CHUNK_SIZE=800`,
    `CHUNK_OVERLAP=120` y 294 fragmentos**, confirmada por el usuario y
    recalculada el 20261028_0804 con resultado **6/10 rutas correctas**.
    *Actualizado el 20261028: la vigente pasó a **`UMBRAL=0.43`** (8/10, 0 falsos
    negativos, 0 alucinaciones). `TOP_K`, los chunks y los 294 fragmentos siguen
    iguales.*
14. **La corrección del troceado funcionó**: el literal c) de la pregunta 2
    pasó de estar fuera del fragmento (125 car.) a estar dentro (829 car.),
    verificado con `--texto`. Pero **bajó el parecido de 0.5850 a 0.5054**, así
    que a 0.58 la pregunta sigue sin responder — ahora por umbral, no por
    contenido.
15. **Los dos falsos negativos (2 y 5) están diagnosticados como de umbral**:
    ambos fragmentos contienen la respuesta literal y el LLM no se ejecuta.
16. **0.58 es el peor de los tres umbrales probados en rutas (6/10)** y el único
    que junta falsos negativos y alucinación. Queda registrado con datos; la
    decisión es del usuario.
17. **La estabilidad es buena entre corridas idénticas**: 3 y 6 (mismo umbral,
    mismo troceado) repiten las 10 rutas y los 10 parecidos exactos.
18. **El formato de citas es inestable entre corridas**: la pregunta 10 citó
    `[LEY-19628 p.13]` en la corrida 1 y `[1 p.13]`/`[3 p.5]` en la corrida 6,
    con el mismo prompt. Argumento directo para la etapa 5.

---

# Barrido exhaustivo de `UMBRAL` y configuración final (20261028)

Solicitud del usuario: determinar con pruebas cuál es el mejor umbral y
considerar la regla de sujeto/país para la pregunta 8.

## 1. Por qué 0.58 no puede ser el mejor valor

La arista `evidencia()` de `src/rag/graph.py` decide con
`mejor_parecido >= UMBRAL`. Como la recuperación es **determinista**, con los
diez parecidos fijos la ruta solo puede cambiar en esos diez valores: hay
**11 regímenes posibles**, no infinitos. 0.58 cae en el régimen
`(0.5361, 0.6104]`, que da **6/10** — el peor de los cinco regímenes centrales.

## 2. Barrido exhaustivo — `scripts/umbral.py` (nuevo, permanente)

Comando: `uv run python scripts/umbral.py`. No usa el LLM: mide ruta, falsos
negativos y cuántas preguntas fuera de contexto llegarían al modelo.

```
UMBRAL configurado ahora en el proyecto (get_settings()): 0.43
Parecidos recuperados (TOP_K=3, Redis, bge-m3) — medidos ahora, sin LLM:
 Nº | Tipo         | Parecido | Ruta esperada
---:|--------------|---------:|--------------
  1 | en_contexto  | 0.7285 | responder
  2 | en_contexto  | 0.5054 | responder
  3 | en_contexto  | 0.6848 | responder
  4 | en_contexto  | 0.6533 | responder
  5 | en_contexto  | 0.5361 | responder
  6 | fuera        | 0.6286 | no_se
  7 | fuera        | 0.3636 | no_se
  8 | fuera        | 0.6104 | no_se
  9 | ambigua      | 0.7411 | responder
 10 | ambigua      | 0.6986 | responder

Barrido exhaustivo de UMBRAL (todos los intervalos con ruta distinta):
 Intervalo de UMBRAL        | Ejemplo | OK | Falsos negativos | Fuera que llega al LLM
----------------------------|---------|----|------------------|------------------------
 [0.0000, 0.3636]           |  0.1818 |  7 | -                 | 6,7,8
 (0.3636, 0.5054]           |  0.4345 |  8 | -                 | 6,8
 (0.5054, 0.5361]           |  0.5207 |  7 | 2                 | 6,8
 (0.5361, 0.6104]           |  0.5733 |  6 | 2,5               | 6,8
 (0.6104, 0.6286]           |  0.6195 |  7 | 2,5               | 6
 (0.6286, 0.6533]           |  0.6410 |  8 | 2,5               | -
 (0.6533, 0.6848]           |  0.6691 |  7 | 2,4,5             | -
 (0.6848, 0.6986]           |  0.6917 |  6 | 2,3,4,5           | -
 (0.6986, 0.7285]           |  0.7135 |  5 | 2,3,4,5,10        | -
 (0.7285, 0.7410]           |  0.7348 |  4 | 1,2,3,4,5,10      | -
 (0.7410, 1.0000]           |  0.8705 |  3 | 1,2,3,4,5,9,10    | -

Barrido fino 0.00..1.00 paso 0.01 (101 valores): 11 configuraciones de ruta.
Intervalos distintos por los 10 parecidos: 11.

Máximo de rutas correctas: 8/10, alcanzado en:
  (0.3636, 0.5054]  (p. ej. 0.43) -> falsos negativos -, fuera que pasa [6, 8]
  (0.6286, 0.6533]  (p. ej. 0.64) -> falsos negativos [2, 5], fuera que pasa -
```

**El barrido es exhaustivo**: los 101 valores de 0.00 a 1.00 con paso 0.01
producen **exactamente las mismas 11 configuraciones de ruta** que los
intervalos de la tabla, así que no se omite ningún régimen.

## 3. Los dos máximos, decididos con contenido (no solo con ruta)

Ambos intervalos dan 8/10; se desempatan ejecutando la batería en cada uno con
el prompt nuevo:

| Intervalo | Corrida | Umbral | Rutas | Falsos negativos | Alucinaciones | Contenido medido |
| --- | --- | ---: | ---: | --- | --- | --- |
| **A** `(0.3636, 0.5054]` | 7 (20261028_0836) | 0.50 | **8/10** | **0** | **0** — la 8 es rechazada por la regla 5, no por el umbral | 6 correctas, 4 parciales, **0 faltas de contenido** |
| **B** `(0.6286, 0.6533]` | 8 (20261028_0841) | 0.64 | **8/10** | **2 (2, 5)** | 0 — porque la 8 queda bloqueada | 4 correctas, 3 parciales, 2 FN, 1 falta (9) |

**Gana el intervalo A**: mismas rutas, **dos falsos negativos menos** y las
preguntas 2 y 5 (que contienen literalmente su respuesta) vuelven a responder.
El intervalo B solo logra 0 alucinaciones **bloqueando**; con la regla 5 activa
ya no hace falta bloquear a la 8.

## 4. Configuración final: `UMBRAL = 0.43` + regla 5

Dentro de A, 0.43 es el **punto de mayor margen**: `0.43 − 0.3636 = 0.0664`
por debajo (mantiene fuera a la 7) y `0.5054 − 0.43 = 0.0754` por arriba
(déjala entrar). Elegido el máximo del mínimo de los dos márgenes (centro
teórico 0.4345), no el borde.

Aplicado en `.env` (línea 11), `.env.example` (línea 18) y en el default de
`src/rag/config.py` (línea 55): **`0.43`**.
Verificación: `uv run python -m unittest discover -s tests` → **59 pruebas OK**
(`test_redis_cosine_threshold` pasó a fijar `UMBRAL` explícito en la prueba,
para que deje de depender del valor por defecto).

## 5. Corridas 7, 8 y 9

| # | Fecha/hora | Umbral | Prompt | Rutas | FN | Aluc. | Evidencia |
| --- | --- | ---: | --- | ---: | --- | ---: | --- |
| 7 | 20261028_0836 | 0.50 | con regla 5 | 8/10 | 0 | 0 | `capturas/bateria_20261028_0836_umbra05.json` |
| 8 | 20261028_0841 | 0.64 | con regla 5 | 8/10 | 2 (2, 5) | 0 | `capturas/bateria_20261028_0841_umbra064.json` |
| 9 | 20261028_0848 | **0.43 (final)** | con regla 5 | **8/10** | **0** | **0** | `capturas/bateria_20261028_0848_umbra043.json` |

## 6. Tabla completa de la corrida 9 (configuración vigente)

| Nº | Pregunta | Respuesta esperada y fuente/página | Respuesta obtenida | Fragmentos/citas | Parecido | Nodos | Evaluación | Evidencia |
| --- | --- | --- | --- | --- | ---: | --- | --- | --- |
| 1 | ¿Cuáles son los derechos que tiene el titular de los datos personales? | Acceso, rectificación, supresión, oposición, portabilidad y **bloqueo**. **Art. 4°, p. 6** | "...derecho de acceso, derecho de rectificación, derecho de supresión, derecho de oposición, derecho a la portabilidad... [1 p.4]. Además, tiene derecho a solicitar confirmación... [2 p.6]. El responsable debe proporcionar toda la información... [3 p.5]" | p.4 (0.7285), p.6 (0.7203), p.5 (0.7166) | **0.7285** | `buscar → responder` | **Parcial**: omite "bloqueo"; **citas malformadas** `[1 p.4]` | `capturas/bateria_20261028_0848_umbra043.json` |
| 2 | ¿Qué establece el principio de proporcionalidad? | Datos limitados a los necesarios, adecuados y pertinentes. **Art. 3° lit. c), p. 5** | "El principio de proporcionalidad establece que los datos personales que se traten deben limitarse estrictamente a aquéllos que resulten necesarios, adecuados y pertinentes en relación con los fines del tratamiento **[LEY-19628 p.5]**." | p.5 (0.5054, 829 car. con el literal c) | **0.5054** | `buscar → responder` | **CORRECTA** (antes era falso negativo y antes aún respondía mal) | `capturas/bateria_20261028_0848_umbra043.json` |
| 3 | ¿En qué casos procede la supresión de los datos personales? | Seis causales. **Art. 7°, p. 7** | Cuatro causales con `[LEY-19628 p.7]` | p.7 (0.6848), p.19 (0.6836), p.7 (0.6485) | **0.6848** | `buscar → responder` | **Parcial**: faltan "innecesarios" y "caducos"; citas bien formadas | `capturas/bateria_20261028_0848_umbra043.json` |
| 4 | ¿Qué se entiende por anonimización? | Procedimiento irreversible. **Art. 2° lit. k), p. 3** | Texto legal completo con `[LEY-19628 p.3]` | p.3 (0.6533), p.29 (0.5581), p.20 (0.5183) | **0.6533** | `buscar → responder` | **CORRECTA** | `capturas/bateria_20261028_0848_umbra043.json` |
| 5 | ¿Qué es el derecho de acceso? | Confirmación de tratamiento, acceso y información. **Art. 2° lit. q), p. 4** | "El derecho de acceso es el derecho del titular de datos a solicitar y obtener del responsable, confirmación acerca de si sus datos personales están siendo tratados por él **[LEY-19628 p.4]**." | p.4 (0.5361, 343 car. con el literal q) | **0.5361** | `buscar → responder` | **CORRECTA** (antes era falso negativo) | `capturas/bateria_20261028_0848_umbra043.json` |
| 6 | ¿Qué establece el GDPR de la Unión Europea sobre los encargados de tratamiento? | `no_se` sin inventar | "El contexto proporcionado no contiene información sobre el GDPR de la Unión Europea ni sobre los encargados de tratamiento según este. Por lo tanto, el documento no lo contiene [archivo no relacionado]." | p.52 (0.6286), p.11 (0.6033), p.17 (0.5982) | **0.6286** | `buscar → responder` | **Contenido correcto** (declina sin alucinar); ruta distinta a la esperada; **cita malformada** | `capturas/bateria_20261028_0848_umbra043.json` |
| 7 | ¿Cómo se configura la replicación en Redis Cluster? | `no_se` | "No encontré evidencia en los documentos para responder eso." | p.10 (0.3636), p.10 (0.3480), p.43 (0.3479) | **0.3636** | `buscar → no_se` | **CORRECTA** (única ruta `no_se` de esta corrida) | `capturas/bateria_20261028_0848_umbra043.json` |
| 8 | ¿Cuál es la multa máxima que aplica la autoridad de protección de datos de Argentina? | `no_se` (otra jurisdicción) | **"El documento mencionado no especifica la multa máxima que aplica la autoridad de protección de datos de Argentina [1]."** | p.49 (0.6104), p.43 (0.5922), p.44 (0.5855) | **0.6104** | `buscar → responder` | **CORREGIDA por la regla 5**: antes atribuía la cifra chilena del Art. 44 a Argentina; ahora **declina**. **Cita malformada** `[1]` | `capturas/bateria_20261028_0848_umbra043.json` |
| 9 | ¿Qué plazo tiene el responsable para responder al titular? | No hay plazo único; no fijar un número no escrito. **Art. 5°/7°, pp. 6–7** | "El responsable tiene un plazo de **treinta días hábiles** para responder al titular [LEY-19628 p.10]." | p.10 (0.7411), p.47 (0.7169), p.10 (0.6909) | **0.7411** | `buscar → responder` | **FALLO de contenido**: p.10 dice **corridos**. En la corrida 7 el mismo prompt dio "corridos": **inestable** | `capturas/bateria_20261028_0848_umbra043.json` |
| 10 | ¿Qué información debe entregar el responsable? | Distinguir acceso (**Art. 2° q, p. 4**) de portabilidad (**Art. 2° u, p. 4**) | "...[19628 p.5]. Además... la política de tratamiento... [19628 p.13]" | p.13 (0.6986), p.13 (0.6906), p.5 (0.6894) | **0.6986** | `buscar → responder` | **Parcial**: no distingue acceso de portabilidad; cita casi bien formada (`19628` sin `LEY-`) | `capturas/bateria_20261028_0848_umbra043.json` |

## 7. Balance de la corrida 9 (configuración vigente)

| Evaluación | Cantidad | Preguntas |
| --- | ---: | --- |
| Correcta | 6 | 2, 4, 5 (en contexto), 6 (declinación), 7 (rechazo), 8 (declinación) |
| Parcial | 3 | 1, 3, 10 |
| Falso negativo (`UMBRAL`) | **0** | — |
| Fallo de contenido | 1 | 9 |
| Alucinación | **0** | — |
| **Rutas correctas** | **8/10** | (las 2 distintas son 6 y 8, ambas con contenido correcto) |

## 8. Antes y después sobre las mismas diez preguntas

| Métrica | Antes — `0.58` + prompt original (corrida 6, 0804) | Después — `0.43` + regla 5 (corrida 9, 0848) |
| --- | --- | --- |
| Rutas correctas | **6/10** | **8/10** |
| Falsos negativos | **2** (2, 5) | **0** |
| Alucinaciones | **1** (8) | **0** |
| Fallos de contenido | 1 (9) | 1 (9) |
| Correctas (contenido) | 3 (4, 7 y 6) | **6** (2, 4, 5, 6, 7, 8) |
| Parciales | 3 (1, 3, 10) | 3 (1, 3, 10) |

La mejora de la pregunta 2 y la 5 es del **umbral** (contenían la respuesta y
no llegaban al LLM). La mejora de la pregunta 8 es de la **regla 5** (seguía
llegando al LLM, igual que en 0.50 y 0.58, y ahora se niega).

## 9. Reproducción

```powershell
uv run python scripts/umbral.py
uv run python scripts/bateria.py --umbral 0.43 --etiqueta "CONFIGURACION FINAL..."
uv run python main.py rag "¿Cuál es la multa máxima que aplica la autoridad de protección de datos de Argentina?" --saltos
uv run python -m unittest discover -s tests
```

Salida real de la última de ellas, con el `.env` vigente:

```text
[salto] buscar
  mejor_parecido: 0.6104
  fragmento 1: ... p.49 parecido=0.6104
  fragmento 2: ... p.43 parecido=0.5922
  fragmento 3: ... p.44 parecido=0.5855
[salto] responder
El documento mencionado no especifica la multa máxima que aplica la autoridad de protección de datos de Argentina [1].
```

## 10. Conclusiones añadidas (barrido y configuración final)

19. **El mejor umbral con estos datos es `0.43`**, punto de mayor margen del
    único régimen que maximiza rutas (8/10) **y** elimina los falsos negativos.
    Quedó aplicado en los tres archivos de configuración.
20. **0.58 era el peor umbral razonable**: 6/10, con 2 falsos negativos y
    1 alucinación. El barrido lo demuestra sin recurrir a opiniones.
21. **La regla 5 (sujeto/país) elimina la alucinación de la pregunta 8**,
    confirmado en dos corridas con umbral distinto (0.50 y 0.43), donde la 8
    **sí llega al LLM** y aun así se niega. Es la mejora que ningún umbral
    podía dar: entre 0.50 y 0.58 la 8 alucinaba siempre.
22. **Queda un fallo de contenido (la 9)**, de prompt y no de umbral, que
    alternó entre "corridos" (corrida 7) y "hábiles" (corrida 9) con el mismo
    texto: es material de la etapa 5.
23. **Las citas malformadas persisten** (`[1 p.4]`, `[1]`, `[archivo no
    relacionado]`, `[19628 p.5]`) pese a la regla 2 del `SYSTEM_PROMPT`.
    Sin reglas que el modelo cumpla de forma estable, tampoco la 5 debe darse
    por consolidada sin más corridas.
24. **Límite del barrido**: se hizo sobre las diez preguntas del set. Un umbral
    más bajo admite más consultas frontera; la contención de esos casos depende
    de las reglas 3 y 5 del prompt, no del umbral.

---

# Consolidación de la instrucción 11 — 20261028

Se conserva el set aprobado, incluidas las preguntas de GDPR y Argentina:
son fuera del corpus pero cercanas al tema, más difíciles que clima/bitcoin.
Redis, 294 fragmentos, bge-m3, qwen3:8b, chunks 800/120 y los cinco puntos
del SYSTEM_PROMPT se mantuvieron durante la comparación. No hubo reingesta.

## Tabla solicitada: diez preguntas con TOP_K=4

Fuente íntegra: `capturas/bateria_20261028_1558_umbra043.json`.
En las rutas siguientes, R = `buscar → responder`, N = `buscar → no_se`.
Declinar dentro de R no equivale a recorrer N.

| # | Pregunta | Tipo | Ruta (--saltos) | Mejor parecido | ¿Respondió o no_se? | ¿Cita correcta? | Comentario |
| --- | --- | --- | --- | ---: | --- | --- | --- |
| 1 | ¿Cuáles son los derechos que tiene el titular de los datos personales? | dentro | R | 0.7285 | Respondió | Parcial: `[1 p.4]` no sostiene bloqueo; p.6 sí, formato incorrecto | Enumera los seis derechos; persiste fallo de atribución |
| 2 | ¿Qué establece el principio de proporcionalidad? | dentro | R | 0.5054 | Respondió | Sí, p.5 | Núcleo correcto; no desarrolla conservación temporal |
| 3 | ¿En qué casos procede la supresión de los datos personales? | dentro | R | 0.6848 | Respondió | Sí, p.7 | Seis causales completas |
| 4 | ¿Qué se entiende por anonimización? | dentro | R | 0.6533 | Respondió | Sí, p.3 | Definición correcta |
| 5 | ¿Qué es el derecho de acceso? | dentro | R | 0.5361 | Respondió | Sí, p.4 | Definición breve; no desarrolla toda la información del art.5 |
| 6 | ¿Qué establece el GDPR de la Unión Europea sobre los encargados de tratamiento? | fuera | R | 0.6286 | Declina desde responder | No: `[archivo no relacionado]` no identifica fuente | Falso positivo del umbral; no inventa el GDPR |
| 7 | ¿Cómo se configura la replicación en Redis Cluster? | fuera | N | 0.3636 | no_se | No aplica | Rechazo por umbral |
| 8 | ¿Cuál es la multa máxima que aplica la autoridad de protección de datos de Argentina? | fuera | R | 0.6104 | Declina desde responder | No aplica, sin cita | Falso positivo del umbral, contenido rechazado correctamente |
| 9 | ¿Qué plazo tiene el responsable para responder al titular? | ambigua | R | 0.7411 | Respondió | Sí, p.10 | Treinta días corridos; omite prórroga y no pide aclaración |
| 10 | ¿Qué información debe entregar el responsable? | ambigua | R | 0.6986 | Respondió | Sí, pp.13 y 5 | Información pública/transparencia; no distingue todos los supuestos |

**Balance de rutas:** 8/10 según la expectativa histórica; 0 falsos negativos
en las cinco dentro y 2 falsos positivos (6, 8). Ambos se rechazan por contenido
en el nodo responder. Esto no significa 10/10 respuestas perfectas: hay
omisiones, ambigüedad sin aclarar y errores de cita.

## Comparación ejecutada de TOP_K

| TOP_K | Q1 derechos | Q3 causales | Q8 Argentina | Q9 plazo | Evidencia |
| ---: | --- | --- | --- | --- | --- |
| 1 | 5/6, falta bloqueo | 4/6 | No ejecutada con K=1 | No ejecutada con K=1 | `bateria_topk1_dentro_20261028.json` |
| 3 | 5/6, falta bloqueo | 4/6 | Declina | Hábiles, incorrecto en corrida 9 histórica | `bateria_20261028_0848_umbra043.json` |
| 5 | 6/6, cita p.4 insuficiente | 5/6, falta caducos | Atribuye cifra chilena a Argentina | Corridos, incluye prórroga | `bateria_topk5_dentro_20261028.json`, `bateria_topk5_completa_20261028.json` |
| **4** | **6/6**, cita aún defectuosa | **6/6** | **Declina** | **Corridos**, sin prórroga | `bateria_topk4_completa_20261028.json`, `bateria_20261028_1558_umbra043.json` |

Q2 y Q5 conservaron sus definiciones breves con K=1/3/4/5; Q4 mantuvo
la definición de anonimización (con variaciones de extensión). El mejor
parecido y la ruta no cambiaron al variar K: el TOP_1 fue el mismo.
K=5 produjo `[1 p.4]` en Q5; K=1 y K=4 usaron `[LEY-19628 p.4]`.

**Elección: TOP_K=4**, por cobertura de derechos y causales, sin la regresión
de jurisdicción observada con K=5. La comparación K=3 usa el histórico con
igual corpus/configuración salvo K; se contrastó también Q8 directamente.
No se atribuye toda variación exclusivamente a K: el modelo varía incluso
con temperature=0. Dos consultas consecutivas de Q1 produjeron respuestas
distintas, aunque ambas enumeraron seis derechos. La afirmación previa
«gana en todo» era excesiva: las citas y la ambigüedad siguen sin resolverse.

## Umbral y errores de separación

**UMBRAL elegido: 0.43**, confirmado por el usuario y conservado. Las dentro
abarcan 0.5054–0.7285; las fuera 0.3636–0.6286. No hay separación perfecta:
Q6 y Q8 superan a Q2 y Q5. El intervalo (0.3636, 0.5054] admite las cinco
dentro y bloquea Q7; elevarlo por encima de 0.6286 bloquearía Q2 y Q5.
0.43 es cercano al centro del intervalo, no exactamente el máximo margen
(centro aproximado 0.4345). La prueba adicional de criptomonedas confirma
que el umbral no basta para reconocer ausencia temática.

## Verificación de citas contra el PDF

Se abrieron las páginas mediante extracción con `pypdf` y `scripts/cita.py`.
Es verificación textual del PDF, no una inspección visual de su maquetación.

| Página | Texto comprobado | Resultado |
| ---: | --- | --- |
| 4 / 6 | Derechos y bloqueo | p.4 no contiene bloqueo; p.6 contiene el listado completo |
| 5 | Principio de proporcionalidad | Texto legal presente |
| 7 | Los datos no resulten necesarios / datos caducos | Causales presentes |
| 3 | Anonimización | Definición presente |
| 4 / 6 | Derecho de acceso / confirmación acerca de si | Definición y desarrollo presentes |
| 10 | Treinta días corridos | Plazo del responsable y prórroga; no confundir con reclamación |
| 13 / 5 | Política de tratamiento / toda la información que sea necesaria | Respaldo a Q10 |
| 1–57 | Argentina | Sin coincidencias; la cifra de p.49 no prueba una multa argentina |

Ejemplo reproducible: `uv run python scripts/cita.py --pagina 10 --buscar
"treinta días corridos"`. Una búsqueda literal negativa no demuestra ausencia:
las anotaciones marginales interrumpen frases (ocurrió al buscar la causal a).

## Pruebas adicionales: significado y parecido engañoso

1. **Sinónimos, primera redacción:** «Si una persona quiere descubrir qué
   guardaron sobre ella, ¿qué puede pedir?» → 0.5241; recuperó pp.2/53/28/26,
   no el derecho de acceso. Respondió imponiendo condiciones de cesión de
   datos: fallo de recuperación/contenido, candidato a reformulación en etapa 6.
   Con K=12 apareció p.6 en posición 9, pero ese ensayo no cambia K elegido.
2. **Sinónimos sin tokens analizados presentes:** «¿Puedo averiguar qué
   guardaron de mí?» → **0.4988**, ruta responder; p.6 aparece cuarta (0.4898).
   Responde correctamente sobre confirmación y acceso, citando p.6.
   `palabras.py` comprueba que `puedo`, `averiguar`, `guardaron` no aparecen
   como palabras completas. La medida excluye palabras vacías y tokens de
   menos de cuatro letras: no significa ausencia de absolutamente todas las
   palabras. Se conserva la primera redacción fallida, sin seleccionar solo éxitos.
3. **Fuera con léxico común:** «¿Qué establece esta ley sobre el tratamiento
   de datos personales en las criptomonedas?» → **0.6259**, ruta responder,
   declinación correcta. Cuatro de cinco tokens analizados coinciden (80%).
   Se trata de ausencia de contenido específico, no de una afirmación sobre
   la aplicabilidad jurídica general de la ley a las criptomonedas.

Salidas: `capturas/20261028_instruccion11_sinonimos.txt`,
`capturas/20261028_instruccion11_sinonimos_sin_tokens.txt` y
`capturas/20261028_instruccion11_lexico_fuera.txt`.
Esta prueba léxica no reemplaza la prueba de inyección/trampa de la etapa 5.

## Capturas, reproducción y conclusión

- Dentro: `capturas/20261028_instruccion11_dentro.png` (Q3).
- Fuera: `capturas/20261028_instruccion11_fuera.png` (Q7, nodo no_se).
- Ambigua: `capturas/20261028_instruccion11_ambigua.png` (Q9).

Son capturas de una vista HTML de **stdout real**, guardado directamente al
ejecutar `main.py --saltos`; se incluyen HTML y TXT para trazabilidad. No son
fotografías de una ventana de terminal. Se generaron con Edge headless.
`uv run python scripts/evidencia_etapa4.py` reproduce esas salidas.

```powershell
uv run python scripts/bateria.py --umbral 0.43 --top-k 1 --solo 1,2,3,4,5 --salida resultado_k1.json
uv run python scripts/bateria.py --umbral 0.43 --top-k 5 --solo 1,2,3,4,5 --salida resultado_k5.json
uv run python scripts/bateria.py --top-k 4 --salida resultado_k4.json
uv run python scripts/palabras.py "¿Puedo averiguar qué guardaron de mí?"
uv run python main.py rag "¿Puedo averiguar qué guardaron de mí?" --saltos --texto
```

**Conclusión:** se mantienen 800/120 y UMBRAL=0.43; TOP_K pasa de 3 a 4.
Mejora la cobertura de Q1/Q3 y el plazo de Q9 en las corridas observadas,
pero persisten citas defectuosas y sensibilidad a la redacción. Es una elección
basada en este set, no una garantía general ni una etapa 5/6 completada.
