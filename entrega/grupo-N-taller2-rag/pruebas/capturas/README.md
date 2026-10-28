<!--
Integrantes: Fabio Durán; Gustavo Reyes; Ezequiel Muñoz
Objetivo: indicar cómo reunir capturas y salidas verificables para la entrega.
fecha_hora_creacion: 20261027_1858
fecha_hora_modificacion: 20261028_1016
-->

# Capturas y salidas

Guardamos evidencias reales, legibles y sin claves ni URLs privadas.

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
