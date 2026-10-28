<!--
Integrantes: Fabio Durán; Gustavo Reyes; Ezequiel Muñoz
Objetivo: documentar el set de diez preguntas del agente: cinco con contexto, tres fuera de contexto y dos ambiguas.
fecha_hora_creacion: 20261027_2040
fecha_hora_modificacion: 20261028_0853
-->

# Set de diez preguntas del agente — instrucción 05

Grupo: **N (confirmado)**. Integrantes: Fabio Durán, Gustavo Reyes, Ezequiel Muñoz.

## Corpus y configuración de referencia

| Elemento | Valor |
| --- | --- |
| Corpus | `docs/LEY-19628_28-AGO-1999_refundida_20261201.pdf` (57 páginas con texto) |
| Backend | Redis (`VECTOR_STORE=redis`, índice `etmunoz_ollama_rag`) |
| Embeddings | `EMBEDDING_MODEL=bge-m3` (1024 dimensiones) |
| LLM | `MODELO=qwen3:8b` con `MODEL_PROVIDER=ollama` |
| Chunks | `CHUNK_SIZE=800`, `CHUNK_OVERLAP=120`, 318 fragmentos |
| `TOP_K` / `UMBRAL` | 3 / 0.65 |

Las páginas citadas corresponden a la numeración impresa del propio PDF
(página 1 a 57), que es la que el agente expone en `fragmento['pagina']`.

## 1. Cinco preguntas dentro del contexto del documento

Todas tienen respuestas explícitas en el texto ingerido.

| Nº | Pregunta | Fuente y página en el documento |
| --- | --- | --- |
| 1 | ¿Cuáles son los derechos que tiene el titular de los datos personales? | Art. 4°, p. 6: acceso, rectificación, supresión, oposición, portabilidad y bloqueo |
| 2 | ¿Qué establece el principio de proporcionalidad? | Art. 3° literal c), p. 5: limitar los datos a los necesarios, adecuados y pertinentes |
| 3 | ¿En qué casos procede la supresión de los datos personales? | Art. 7°, p. 7: datos innecesarios, consentimiento revocado, obtención ilícita, caducos, sentencia o resolución, oposición sin otro fundamento |
| 4 | ¿Qué se entiende por anonimización? | Art. 2° literal k), p. 3: procedimiento irreversible por el que un dato personal no puede vincularse con un titular |
| 5 | ¿Qué es el derecho de acceso? | Art. 2° literal q), p. 4 y Art. 5°, p. 6: confirmación de tratamiento y acceso a los datos e información prevista en la ley |

## 2. Tres preguntas fuera del contexto del documento

No tienen respuesta en la ley ingerida; el agente debe negarse a responder
invocando `no_se` o indicando que el contexto no alcanza.

| Nº | Pregunta | Por qué está fuera del corpus |
| --- | --- | --- |
| 6 | ¿Qué establece el GDPR de la Unión Europea sobre los encargados de tratamiento? | Norma europea distinta; el corpus es la ley chilena 19628 |
| 7 | ¿Cómo se configura la replicación en Redis Cluster? | Tema técnico ajeno al corpus legal |
| 8 | ¿Cuál es la multa máxima que aplica la autoridad de protección de datos de Argentina? | Otra jurisdicción y otra ley |

## 3. Dos preguntas ambiguas

Admiten más de una lectura razonable dentro del propio documento; sirven para
ver si el agente aclara la ambigüedad en vez de inventar una sola respuesta.

| Nº | Pregunta | Ambigüedad |
| --- | --- | --- |
| 9 | ¿Qué plazo tiene el responsable para responder al titular? | No hay un plazo único: varía según el derecho ejercido y el artículo aplicable |
| 10 | ¿Qué información debe entregar el responsable? | Depende de si se ejerce acceso, portabilidad u otro derecho; cada uno define su alcance |

## Uso previsto

Este set es la **entrada** de la etapa 4 de la rúbrica. La ejecución de las diez
preguntas con ruta, parecido, respuesta, cita y la justificación de `TOP_K` y
`UMBRAL` se registra en `entrega/grupo-N-taller2-rag/pruebas/bateria.md`.
Todavía **no se han ejecutado** las diez: solo están definidas aquí.

## Observación de ejecución real — 20261027_2045

Pregunta ejecutada fuera de la batería, sobre el mismo corpus y configuración
de la tabla superior:

```text
uv run python main.py rag "Objeto y ámbito de aplicación" --saltos
```

Salida literal:

```text
[salto] buscar
  mejor_parecido: 0.6827
  fragmento: LEY-19628_28-AGO-1999_refundida_20261201.pdf p.15 parecido=0.6827
  fragmento: LEY-19628_28-AGO-1999_refundida_20261201.pdf p.37 parecido=0.5864
  fragmento: LEY-19628_28-AGO-1999_refundida_20261201.pdf p.2 parecido=0.5683
[salto] responder
El objeto de la presente ley es regular el tratamiento de datos personales, incluyendo
su análisis, rastreo, perfilamiento o predicción de comportamiento [1 p.2]. El ámbito
de aplicación comprende el tratamiento de datos personales realizado por un responsable
que, sin estar establecido en el territorio nacional, le resulta aplicable la legislación
nacional a causa de un contrato o del derecho internacional [1 p.2].
```

### Observación 1 — cita malformada (entrada para la etapa 5)

El `SYSTEM_PROMPT` exige `[archivo p.N]` (p. ej. `[LEY-19628 p.2]`), pero
`qwen3:8b` emitió `[1 p.2]`: usó el **índice del fragmento** en lugar del nombre
del archivo. El contenido y la página son correctos; falla solo el formato.

- Regla incumplida: regla 2 de `SYSTEM_PROMPT` (formato de cita).
- No se corrigió: el pulido de prompts es la etapa 5, todavía pendiente.
- Queda registrado aquí como defecto observado con evidencia real, no como
  resultado de etapa ejecutada.

### Observación 2 — el fragmento que motiva la respuesta no es el mejor (dato para la etapa 4)

El fragmento de mayor parecido está en p.15 (0.6827), pero la respuesta se apoya
en el texto de p.2 (0.5683, el más bajo del `TOP_K`).

Esto es el comportamiento esperado: `UMBRAL` decide **si** responde usando solo
`mejor_parecido`, mientras que `responder` recibe los 3 fragmentos y elige el
relevante. Señala que `TOP_K=3` aporta cobertura que el único mejor fragmento
no daría; es un argumento a sopesar al justificar `TOP_K` en la etapa 4.

## Actualización 20261028_0809 — estado vigente

La tabla "Corpus y configuración de referencia" y la frase *"Todavía **no se
han ejecutado** las diez"* describen el estado del **20261027_2040** y se
conservan arriba como antecedente. El estado actual es otro:

| Elemento | Valor en 20261027_2040 (arriba) | **Valor vigente (20261028)** |
| --- | --- | --- |
| Fragmentos | 318 | **294** (reingesta con `--reset` el 20261027_2337 tras corregir el troceado) |
| `UMBRAL` | 0.65 | **0.58**, confirmado por decisión del usuario el 20261028 |
| `TOP_K` / chunks | 3 · 800/120 | sin cambios: 3 · 800/120 |
| ¿Se ejecutaron las diez? | No, solo estaban definidas | **Sí, seis veces** |

Las diez preguntas **siguen idénticas**; lo que cambió es el estado de
ejecución y la configuración. Evidencia completa (rutas, parecidos, respuestas,
citas y justificación de `TOP_K`/`UMBRAL`):
`entrega/grupo-N-taller2-rag/pruebas/bateria.md`, última sección
"Actualización 20261028".

## Actualización 20261028_0853 — configuración final

La tabla anterior describe el estado de las **08:09** y se conserva como
antecedente. A partir de las 08:25 el usuario pidió determinar el mejor umbral
*probando exhaustivamente* y evaluar la regla de sujeto/país para la pregunta 8.
Resultado:

| Elemento | Valor a las 08:09 | **Valor vigente (08:53)** |
| --- | --- | --- |
| `UMBRAL` | 0.58 (decisión del usuario) | **0.43** — barrido 0.00–1.00 (11 regímenes) + batería en los dos intervalos óptimos |
| Prompt `SYSTEM_PROMPT` | 4 reglas | **5 reglas** (regla 5: sujeto/país) desde `20261028_0827` |
| Rutas correctas | 6/10 | **8/10** |
| Falsos negativos | 2 (2, 5) | **0** |
| Alucinaciones | 1 (8) | **0** |
| ¿Se ejecutaron las diez? | seis veces | **nueve veces** (corridas 7, 8 y 9) |

Las diez preguntas **siguen idénticas**; también lo son `TOP_K=3` y los chunks
800/120. El cambio de umbral **no** exigió reingesta: solo se relee
`get_settings().umbral`. Evidencia: `pruebas/bateria.md`, sección "Barrido
exhaustivo de `UMBRAL` y configuración final"; `pruebas/prompts.md`, sección C.
