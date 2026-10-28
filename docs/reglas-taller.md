<!--
Integrantes: Fabio Durán; Gustavo Reyes; Ezequiel Muñoz
Objetivo: conservar la rúbrica del taller y definir qué código, prompts y pruebas deben entregarse.
fecha_hora_creacion: 20261027_1907
fecha_hora_modificacion: 20261027_1913
-->

# Reglas del taller y rúbrica de evaluación

Fuente: `instrucciones/instruccion_02d.txt`. Este documento consolida sus reglas;
el archivo de instrucciones se conserva sin modificar. No certifica que las
etapas ya estén terminadas. Las obligaciones para futuras ediciones también
están registradas en `AGENTS.md`.

Complemento obligatorio: `instrucciones/instruccion_02e.txt` exige **nombres y
apellidos completos** y **nombre o número del grupo** en la **primera página**
del documento y en el `README.md` del proyecto. En `instruccion_02f.txt` se
confirmaron como completos los nombres Fabio Durán, Gustavo Reyes y Ezequiel
Muñoz, el nombre de grupo **N** y que **no se utilizó material de compañeros**.
Si posteriormente se utiliza material
de un compañero, indicar de quién es y qué se utilizó; no asumir una declaración
negativa cuando aún no se ha consultado. El registro de identificación y
declaraciones confirmadas está en `docs/entrega.md`.

## Principio de evaluación

El taller se califica por **cómo se probó el agente y cómo se pulieron sus
prompts**, no por la cantidad de código escrito con OpenCode. Deben verse las
tres partes completas: **código, prompts y pruebas**. Sin pruebas no hay nota.
Las pruebas unitarias son apoyo técnico, no sustituyen las evidencias de las etapas.

## Qué debe entregarse

1. **Todo el código final**: `src/`, `scripts/`, `main.py`, `AGENTS.md`,
   `requirements.txt`, `tests/`, `.env.example`, `README.md` y el PDF autorizado
   del corpus en `docs/`. Incluir la configuración Docker y los archivos uv
   necesarios para reproducir el proyecto. Nunca incluir `.env`, claves,
   `.venv`, `.git`, cachés ni `data/` pesado.
2. **Todos los prompts, de los dos tipos**:
   - Los textos exactos dados a OpenCode, con correcciones e iteraciones y
     explicación de qué cambió y por qué. No conservar solo el último prompt.
   - Los prompts efectivos del agente: `SYSTEM_PROMPT`, `USER_PROMPT` y el del
     nodo extra, cuando se implementen. Copiarlos completos al documento final,
     identificando archivo, versión y uso real. No basta con definir constantes
     que el agente no utilice.
3. **Todas las pruebas**: tablas, salidas y capturas de cada etapa; embeddings,
   chunks, diez preguntas, antes/después, trampa y ruta del nodo extra.
4. **Documento de entrega**: identificación del equipo y número de grupo,
   evidencias, ambos tipos de prompts y conclusión corta por etapa. La rúbrica
   admite Word, notebook o PDF; en este proyecto se acordó producir
   `documento-entrega.docx` al final, junto con el ZIP.

El nombre confirmado del grupo es **N**; conservarlo en la carpeta, el documento
y el ZIP final. No inventar el PDF, resultados, capturas,
predicciones previas ni mejoras. Si no hay evidencia, registrar **pendiente**.

## Rúbrica

| Etapa | Evidencia exigida | Ubicación de trabajo / destino final | Puntos |
| --- | --- | --- | ---: |
| 1 · Construir | Captura del agente respondiendo; prompts usados con OpenCode y qué se corrigió | `pruebas/construccion.md`, `pruebas/prompts.md`; documento y `proyecto/` | 10 |
| 2 · Embeddings | Tres frases, predicción previa, tabla de cosenos y conclusión | `pruebas/embeddings.md`; documento y `scripts/demo_embeddings.py` | 10 |
| 3 · Ingesta | Dos configuraciones de chunk/solape, elección y justificación | `pruebas/chunks.md`; documento y `scripts/ingest.py` | 15 |
| 4 · Batería | Diez preguntas con ruta, parecido, respuesta y cita; UMBRAL y TOP_K elegidos con datos | `pruebas/bateria.md`; documento | 20 |
| 5 · Pulir prompts | Dos reglas cambiadas; antes/después en tres preguntas; trampa; prompts finales | `pruebas/antes-despues.md`, `pruebas/prompts.md`; documento y `src/rag/prompts.py` | 25 |
| 6 · Nodo extra | Por qué, para qué y qué hace; rutas antes/después con `--saltos`; dos preguntas donde mejora | `pruebas/nodo-extra.md`; documento y `src/rag/graph.py` | 15 |
| Documento | Orden, identificación y conclusión por etapa | `documento-entrega.docx` (al final) | 5 |
| Bonus opcional | Misma batería con FAISS y comparación con Redis | Sección comparativa en `pruebas/bateria.md` y documento | +10 |

Puntaje base: **100 puntos**. Bonus: **hasta +10**.
Las rutas `pruebas/` se refieren a `entrega/grupo-N-taller2-rag/pruebas/`.
Las rutas de código son las de la raíz de trabajo; se copiarán a `proyecto/`
al cerrar la entrega, según `docs/entrega.md`.

## Trazabilidad mínima de cada prueba

- Fecha/hora, pregunta o entrada exacta, corpus y fuente/página.
- Backend, índice/prefijo, modelos, chunk/solape, TOP_K y UMBRAL.
- Versión del prompt y cambios respecto de la prueba anterior.
- Comando, salida real, nodos recorridos y ruta de la captura o transcripción.
- Puntaje recuperado con su significado (coseno/similitud o distancia; indicar
  si mayor o menor es mejor). No comparar distancias de backends distintos
  como si fueran la misma escala.
- Resultado esperado frente a observado y conclusión corta con limitaciones.

Para comparar Redis/FAISS o prompts antes/después, conservar el mismo corpus,
preguntas y demás parámetros salvo la variable estudiada. No mezclar índices
de ingestas distintas. El nodo extra debe tener pruebas propias: la presencia
de `no_context` no acredita por sí sola la etapa 6.

## Plantilla de registro de prompts

La instrucción menciona una plantilla, pero no incluye sus campos completos.
Se prepara esta plantilla de trabajo en `pruebas/prompts.md`, adaptable si se
facilita una plantilla oficial posterior:

1. Identificador, etapa, fecha/hora y tipo (OpenCode o agente).
2. Texto exacto completo y archivo/versión de origen.
3. Objetivo y comportamiento esperado.
4. Corrección/iteración anterior, motivo y texto nuevo completo.
5. Pruebas que demuestran el efecto, resultado y conclusión.

No presentar instrucciones futuras como prompts ya aplicados ni inferir un
`USER_PROMPT` o un prompt del nodo extra que aún no existe en el código.
