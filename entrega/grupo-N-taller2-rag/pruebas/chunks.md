<!--
Integrantes: Fabio Durán; Gustavo Reyes; Ezequiel Muñoz
Objetivo: comparar configuraciones de fragmentación y sus resultados en la etapa 3.
fecha_hora_creacion: 20261027_1858
fecha_hora_modificacion: 20261028_1033
-->

# Configuraciones de chunks — etapa 3

Estado: **comparación ejecutada el 20261028_1014** con
`instrucciones/instruccion_10.txt`. Tres configuraciones medidas con la misma
pregunta, misma ingesta (`--reset`) y mismos `TOP_K=3` / `UMBRAL=0.43`.
Según `docs/reglas-taller.md` (etapa 3: 15 puntos), comparar al menos **dos
configuraciones** de chunk/solape, elegir una y justificarla; aquí se midieron
**tres**. Los valores de la configuración base son los predeterminados del
proyecto, ahora **sí** medidos sobre el corpus.

| Configuración | CHUNK_SIZE | CHUNK_OVERLAP | Corpus/versión | Nº de fragmentos | TOP_K / UMBRAL | Resultado de recuperación | Evidencia |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Base (elegida)** | 800 | 120 | PDF 57 páginas, `etmunoz_ollama` | **294** (promedio **627.6** car.; mín. 200, máx. 988) | 3 / 0.43 | **0.5054 y respuesta correcta** en las dos corridas | `capturas/20261028_1014_etapa3_ingesta_base_800_120.txt` |
| **A** | 400 | 50 | PDF 57 páginas, `etmunoz_ollama` | **573** (promedio **320.4** car.; mín. 101, máx. 490) | 3 / 0.43 | **0.6055 (el más alto) pero respuesta incorrecta** | `capturas/20261028_1014_etapa3_ingesta_A_400_50.txt` |
| **B** | 1200 | 200 | PDF 57 páginas, `etmunoz_ollama` | **193** (promedio **971.2** car.; mín. 322, máx. 1399) | 3 / 0.43 | **0.5118 y respuesta incorrecta** | `capturas/20261028_1014_etapa3_ingesta_B_1200_200.txt` |

Registrar backend, modelo de embeddings, fecha/hora y preguntas comparables.
Usar índices/prefijos separados al comparar configuraciones para no mezclar
fragmentos de ingestas anteriores.

> **Cómo se resolvió aquí**: en vez de tres prefijos se usó **`--reset` sobre el
> mismo prefijo `etmunoz_ollama`** en cada paso, que borra el índice antes de
> guardar: cada medición parte de cero y **no quedan fragmentos de la ingesta
> anterior**. Verificado en las tres corridas con `0 ya existían`. Las tres
> ingestas están documentadas en `docs/docker.md`.

### Tabla de la instrucción 10 (los tres datos pedidos)

| Configuración | CHUNK_SIZE | CHUNK_OVERLAP | Páginas | Fragmentos | Tamaño promedio | Fragmentos 1 y 2 muestran solape (sí/no) |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| A | 400 | 50 | 57 | 573 | 320.4 | **sí** — 45 caracteres reales de 50 configurados |
| B | 1200 | 200 | 57 | 193 | 971.2 | **no** — 0 caracteres reales de 200 configurados |
| Base (elegida) | 800 | 120 | 57 | 294 | 627.6 | **sí** — 83 caracteres reales de 120 configurados |

Pregunta única usada en las tres: **"¿Qué establece el principio de
proporcionalidad?"** (esperada en `Art. 3° lit. c), p. 5`).

| Configuración | Parecido | Fragmento TOP_1 | Respuesta |
| --- | ---: | --- | --- |
| A (400/50) | **0.6055** | p.5, **103 car.**, termina en `c) Principio de proporcionalidad` **sin contenido** | ❌ incorrecta: respondió el literal g) (transparencia/acceso) |
| B (1200/200) | 0.5118 | p.5, 816 car., **también** termina en `c)` **sin contenido** | ❌ incorrecta: respondió el literal b) (finalidad) |
| Base (800/120) | 0.5054 | p.5, fragmento que **sí contiene** el literal c) completo | ✅ **correcta** |

Con `temperature=0` del modelo (`src/rag/llm.py`), la base repitió **exactamente**
el mismo parecido y la misma respuesta en las dos corridas.

## Selección y justificación

**Elegimos: 800 / 120 (configuración base).**
**Porque:** es la **única de las tres que responde correctamente** la pregunta de
prueba. Las dos alternativas enseñan los dos modos de fallar que advertía la
instrucción, y con datos:

- **A (400/50) — fragmentos muy chicos, pierden contexto.** 573 fragmentos y el
  parecido **más alto de todas** (0.6055), pero el TOP_1 de **103 caracteres**
  contiene **solo el encabezado** `c) Principio de proporcionalidad` sin su
  texto: `merge_small_fragments` no lo fusiona porque el mínimo es
  `CHUNK_SIZE//4 = 100` y el fragmento mide 103. El modelo contesta con otro
  artículo y **la respuesta queda mal**. El parecido alto no sirve si el
  fragmento no trae el contenido.
- **B (1200/200) — fragmentos muy grandes, meten ruido y no garantizan el
  solape.** 193 fragmentos de 971 caracteres promedio: el TOP_3 (1314 car.)
  arrastra `g)`, `h)` y el arranque de un Título siguiente, y el literal c)
  sigue **fuera** de los tres recuperados → respuesta incorrecta. Además el
  solape **configurado no se materializa**: entre los fragmentos 1 y 2 midió
  **0 de 200** caracteres, porque el splitter solo arrastra colas cuando le
  sobran piezas al cerrar un chunk.
- **800/120 — el equilibrio de este PDF.** Con el umbral de fusión en 200 el
  encabezado de 125 caracteres de la p.5 **sí** se funde con su contenido (829
  car.), la respuesta sale completa y el solape real entre los fragmentos 1 y 2
  es **83 de 120** configurados (visible en la captura).

**Parecido más alto ≠ mejor respuesta**: la 400/50 gana en parecido y pierde en
contenido. Ese es el dato que justifica la elección.

Queda `CHUNK_SIZE=800` y `CHUNK_OVERLAP=120` en `.env` **para el resto del
taller**, y el índice Redis de 294 fragmentos fue **reingerido con esa
configuración** al cerrar la etapa.

### Validación del usuario (20261028_1033)

Tras revisar el commit `5dffe5f`, el usuario confirmó:

> Comentarios del Usuario: Quedan finalmente 800/120 como combinación final a
> dejar, junto con el umbral ya definido.

Confirma la elección de esta etapa **junto con el umbral ya definido**:
`UMBRAL=0.43` (barrido de 101 valores en `bateria.md`). La combinación vigente
para el resto del taller queda así:

| Parámetro | Valor | Origen |
| --- | ---: | --- |
| `CHUNK_SIZE` | **800** | Elegido en esta etapa y validado por el usuario |
| `CHUNK_OVERLAP` | **120** | Elegido en esta etapa y validado por el usuario |
| `UMBRAL` | **0.43** | Barrido exhaustivo de la etapa 4, ya definido |
| `TOP_K` | 3 | Sin cambios |

Registro completo del comentario en `docs/entrega.md`
(sección "Comentarios y validación del usuario"). No hubo cambios de código:
los tres valores ya estaban en `.env` y el índice ya estaba reingerido.
