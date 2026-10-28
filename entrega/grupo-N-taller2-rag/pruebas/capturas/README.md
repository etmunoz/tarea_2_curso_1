<!--
Integrantes: Fabio Durán; Gustavo Reyes; Ezequiel Muñoz
Objetivo: indicar cómo reunir capturas y salidas verificables para la entrega.
fecha_hora_creacion: 20261027_1858
fecha_hora_modificacion: 20261028_1853
-->

# Capturas y salidas

Guardamos evidencias reales, legibles y sin claves ni URLs privadas.

## Instrucción 11 — nuevas evidencias (20261028)

| Archivo | Contenido |
| --- | --- |
| `bateria_topk1_dentro_20261028.json` | Cinco dentro con K=1 |
| `bateria_topk5_dentro_20261028.json` | Cinco dentro con K=5 |
| `bateria_topk5_completa_20261028.json` | Diez preguntas; regresión de jurisdicción en Q8 |
| `bateria_topk4_completa_20261028.json` | Diez preguntas con K=4 |
| `bateria_20261028_1558_umbra043.json` | Configuración elegida, K=4 y umbral 0.43 |
| `20261028_instruccion11_dentro.png` | Q3, seis causales y ruta responder |
| `20261028_instruccion11_fuera.png` | Q7, ruta no_se |
| `20261028_instruccion11_ambigua.png` | Q9, corridos y cita p.10 |
| `20261028_instruccion11_sinonimos.txt` | Primera redacción: falla recuperación |
| `20261028_instruccion11_sinonimos_sin_tokens.txt` | Segunda redacción: acierto, p.6 cuarta, 0.4988 |
| `20261028_instruccion11_lexico_fuera.txt` | Criptomonedas: 0.6259, declina |

Los PNG son capturas de HTML que presenta stdout real guardado por
`scripts/evidencia_etapa4.py`. Cada uno incluye su TXT y HTML de origen.
No se presentan como capturas de una ventana de terminal. Las capturas de
otras etapas listadas abajo continúan pendientes. Interpretación y
verificación textual del PDF en `../bateria.md`.

## Etapa 5 — instrucción 12 (20261028)

| Archivo | Contenido |
| --- | --- |
| `bateria_etapa5_antes_20261028.json` | Preguntas 1–3 con SYSTEM_PROMPT antes de las reglas 6–9 |
| `bateria_etapa5_despues_20261028.json` | Las mismas preguntas con reglas 6–9 |
| `etapa5_trampa_120_dias_20261028.txt` | Trampa inicial de los 120 días |
| `etapa5_trampa_120_dias_regla10_20261028.txt` | Repetición tras agregar regla 10; sigue sin corregir los 120 días |
| `etapa5_prompt_backup_pre_regla1_20261028.txt` | Copia exacta del prompt antes de quitar temporalmente la regla 1 |
| `etapa5_sin_regla1_umbral0_20261028.txt` | Pregunta de temperatura con regla 1 retirada y UMBRAL=0; no alucina |
| `etapa5_regla1_restaurada_umbral043_20261028.txt` | Misma consulta tras restaurar prompt y UMBRAL=0.43; ruta no_se |

## Contenido actual (inventario inicial 20261028_0809, actualizado 20261028_1016)

| Archivo | Etapa | Qué documenta |
| --- | --- | --- |
| `bateria_20261027_2059.json` | 4 | Batería de 10 preguntas, **`UMBRAL=0.65`**, troceado original (318 fragmentos) |
| `bateria_20261027_2158_umbra058.json` | 4 | Batería de 10 preguntas, **`UMBRAL=0.58`**, troceado original (318 fragmentos) |
| `bateria_20261027_2357_umbra058.json` | 4 | Batería con **`UMBRAL=0.58`** tras corregir el troceado (**294 fragmentos**) |
| `bateria_20261028_0008_umbra05.json` | 4 | Batería con **`UMBRAL=0.50`** y troceado corregido |
| `bateria_20261028_0012_umbra063.json` | 4 | Batería con **`UMBRAL=0.63`** y troceado corregido |
| `bateria_20261028_0804_umbra058.json` | 4 | **Configuración vigente ese día**: `UMBRAL=0.58` confirmado por el usuario, troceado corregido, 294 fragmentos (prompt aún sin la regla 5) |
| `bateria_20261028_0836_umbra05.json` | 4 / 5 | `UMBRAL=0.50` **con la regla 5 activa**: 8/10 rutas, 0 falsos negativos, la 8 se niega |
| `bateria_20261028_0841_umbra064.json` | 4 / 5 | `UMBRAL=0.64` con la regla 5: 8/10 rutas, 2 falsos negativos (2, 5) |
| `bateria_20261028_0848_umbra043.json` | 4 / 5 | **CONFIGURACIÓN VIGENTE**: `UMBRAL=0.43` + regla 5 → 8/10 rutas, 0 falsos negativos, 0 alucinaciones |
| `20261028_0737_etapa2_demo_embeddings.txt` | 2 | Tabla de cosenos de las tres frases y predicción previa (`instrucción_07`, paso 3) |
| `20261028_0737_etapa2_indice_vs_coseno.txt` | 2 / 3 | Barrido coseno frente a índice con `--n 2000`: 10/10 coincidencias, A/B=57.39x (`instrucción_07`, paso 4) |
| `20261028_0921_etapa2_instruccion08_sentido.txt` | 2 | **Instrucción 08**: mismo léxico con distinto sentido (0.716434) frente a igual significado (0.876027) — se cumple el orden esperado |
| `20261028_1014_etapa3_ingesta_A_400_50.txt` | 3 | **Instrucción 10, config A**: 400/50 → 573 fragmentos, promedio 320.4, solape real **45/50**. Parecido **0.6055 (el más alto)** pero respuesta **incorrecta**: el TOP_1 de 103 car. solo trae el encabezado `c)` |
| `20261028_1014_etapa3_ingesta_B_1200_200.txt` | 3 | **Instrucción 10, config B**: 1200/200 → 193 fragmentos, promedio 971.2, solape real **0/200**. Parecido 0.5118 y respuesta **incorrecta** (respondió el literal b) |
| `20261028_1014_etapa3_ingesta_base_800_120.txt` | 3 | **Instrucción 10, base elegida**: 800/120 → 294 fragmentos, promedio 627.6, solape real **83/120**. Parecido 0.5054 y respuesta **correcta** en dos corridas idénticas |

Los tres `.txt` de la etapa 3 (`20261028_1014_etapa3_ingesta_*`) guardan la salida
literal de cada `ingest.py --reset`: páginas, fragmentos, promedio, los
fragmentos 1 y 2 con el **solape medido**, y la consulta al agente con
`--saltos --texto`. Análisis y elección en [`../chunks.md`](../chunks.md).

Los **nueve** JSON contienen la salida completa de los 10 grafos: nodos, `mejor_parecido`,
fragmentos y respuesta íntegra. Las tablas resumidas y sus conclusiones están en
[`../bateria.md`](../bateria.md), [`../prompts.md`](../prompts.md) y
[`../embeddings.md`](../embeddings.md).

## Pendiente (falta)

- Capturas `.png` de terminal: la rúbrica pide capturas y los archivos anteriores
  son `.txt`/`.json` de apoyo, que **no las sustituyen**.
- Terminal de `uv run python scripts/test_storage.py` contra Redis persistente.
- Terminal de `uv run python main.py rag "pregunta" --saltos` (y con `--texto`).
- Comparación de prompts / prueba de la trampa (etapa 5). Las configuraciones de
  chunks de la etapa 3 **ya quedaron documentadas** en tres `.txt`.

## Convención

`YYYYMMDD_hhmm_etapa_descripcion.png` para capturas;
`YYYYMMDD_hhmm_etapa_descripcion.txt` para salidas de apoyo.
Anotar comando, configuración, fecha y referencia en la tabla correspondiente.
Revisar las salidas de `salidas_opencode/` antes de copiarlas.
