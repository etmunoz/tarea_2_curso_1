<!--
Integrantes: Fabio Durán; Gustavo Reyes; Ezequiel Muñoz
Objetivo: definir y evaluar el nodo extra con rutas antes/después y dos casos de mejora.
fecha_hora_creacion: 20261027_1907
fecha_hora_modificacion: 20261028_1936
-->

# Nodo extra — etapa 6 (15 puntos)

**Estado: implementado y probado.** Se eligió `reformular`, porque en la etapa 4
una consulta con sinónimos no recuperó el fragmento de acceso esperado. Las
mediciones muestran que Q3 quedó menos ruidosa pero incompleta y que Q5 mantuvo
la misma respuesta; también se conserva la evaluación favorable del usuario.

## Prompt de implementación dado a OpenCode

> Agrega al agente `rag` un nodo nuevo llamado `reformular`.
> - **Por qué existe:** en la etapa 4 una pregunta dentro del corpus redactada con sinónimos no recuperó el fragmento esperado.
> - **Para qué sirve:** mejorar la consulta que llega a la búsqueda semántica sin responder al usuario ni cambiar su intención.
> - **Qué hace exactamente:** recibe la pregunta original y genera una sola consulta breve en español; conserva sujeto, jurisdicción, negaciones, cifras y plazos; no responde, no añade hechos o detalles no presentes en la pregunta; si ya es clara puede devolverla sin cambios. La búsqueda usa la reescritura, pero la respuesta final recibe la pregunta original.
> - **Dónde va en el grafo:** `START → reformular → buscar → (responder | no_se) → END`.
> - **Prompt propio en `src/rag/prompts.py`:** `PROMPT_REFORMULAR`.
> - `--saltos` debe mostrar el nodo, pregunta original y reformulada.
> - No alteres la lógica de los nodos existentes ni el criterio de UMBRAL.

La plantilla exacta de `instrucciones/instruccion_13.txt` y esta especificación
del nodo se conservan también en `prompts.md`, sección E, y en
`salidas_opencode/salida_13.txt`.

## Implementación y configuración de comparación

| Elemento | Valor |
| --- | --- |
| Nodo | `reformular`, antes de `buscar` |
| Código | `src/rag/graph.py`; delega a `tools.reformular()` |
| Prompt efectivo | `PROMPT_REFORMULAR` en `src/rag/prompts.py` |
| Búsqueda | Consulta reformulada; el estado conserva la pregunta original |
| Respuesta | Sigue recibiendo la pregunta original y los fragmentos recuperados |
| Configuración | Redis, qwen3:8b, bge-m3, UMBRAL=0.43, TOP_K=4, chunks 800/120 |
| Salida de trazado | `--saltos` imprime `[salto] reformular`, original y reescrita |

El sistema de respuestas, las reglas de `SYSTEM_PROMPT`, la arista por umbral,
el almacenamiento y el nodo `no_se` no se alteraron. `buscar` solo toma la
consulta reescrita si el estado la contiene; `responder` conserva la pregunta
original.

## Diagramas Mermaid

- Antes: `capturas/etapa6_diagrama_antes_20261028.mmd` — `START → buscar → (responder | no_se) → END`.
- Después: `capturas/etapa6_diagrama_despues_20261028.mmd` — `START → reformular → buscar → (responder | no_se) → END`.

## Dos preguntas de la batería: rutas y respuestas

Ambas se ejecutaron con la misma configuración antes/después. El parecido y la
ruta se comparan en los TXT crudos; las respuestas del LLM pueden variar entre
corridas incluso con `temperature=0`.

Mejora que se esperaba medir: para Q3, que la consulta legal más precisa reduzca
la competencia de p.19 y recupere mejor las seis causales de p.7; para Q5, que
la formulación más explícita mejore la cobertura del derecho de acceso más allá
de la confirmación inicial.

### Pregunta 3

**Pregunta:** ¿En qué casos procede la supresión de los datos personales?

**Antes:** `buscar → responder`; mejor parecido **0.6848**. Fragmentos: p.7
(0.6848), p.19 (0.6836), p.7 (0.6485), p.5 (0.6410). La respuesta enumera
cuatro causales de p.7 y agrega una condición de p.19 sobre salvaguardar vida,
salud o integridad; omite datos innecesarios y caducos.

**Después:** `reformular → buscar → responder`; reformulación: «¿En qué casos
legalmente se permite la supresión de datos personales?»; mejor parecido
**0.6831**. Fragmentos: p.7 (0.6831), p.19 (0.6655), p.7 (0.6648), p.20
(0.6428). La respuesta enumera cuatro causales de p.7, ya no agrega la de
p.19, pero todavía omite las causales de datos innecesarios y caducos.

**Evaluación:** mejora la precisión de la respuesta al no incluir el punto de
p.19 en esta corrida, pero **no mejora la exhaustividad**: sigue dando 4/6
causales. El parecido top-1 fue ligeramente menor; la ruta final siguió siendo
responder. P.19 bajó de 0.6836 a 0.6655 y ya no aparece en la respuesta, pero
dos fragmentos de p.7 siguieron recuperados y el modelo omitió dos causales.
Eso apunta a que la reescritura mitigó ruido, pero no resolvió la selección o
enumeración completa al generar. Es una explicación compatible con los datos,
no una causalidad demostrada. No se afirma una mejora global.

Salidas literales: `capturas/etapa6_antes_pregunta3_20261028.txt` y
`capturas/etapa6_despues_pregunta3_20261028.txt`.

### Pregunta 5

**Pregunta:** ¿Qué es el derecho de acceso?

**Antes:** `buscar → responder`; mejor parecido **0.5361**. Fragmentos p.4,
p.6, p.6 y p.4. Responde que el derecho permite solicitar confirmación de si
los datos personales están siendo tratados; cita `[LEY-19628 p.4]`, pero omite
el acceso a los datos y a la información prevista en la ley.

**Después:** `reformular → buscar → responder`; reformulación: «¿Cuál es el
alcance del derecho de acceso en el ámbito jurídico?»; mejor parecido
**0.5253**. Fragmentos p.4, p.6, p.7 y p.6. La respuesta vuelve a ser la
misma definición breve de confirmación y conserva la cita p.4; no añade el
acceso a los datos ni la información.

**Evaluación:** **sin mejora observable en la respuesta**; el parecido top-1
bajó ligeramente y la ruta final siguió siendo responder. El top-1 continuó
siendo p.4 (0.5253 frente a 0.5361) y el agente repitió la definición breve de
confirmación, aunque p.6 estaba entre los resultados. La reformulación no hizo
que la respuesta aprovechara ese fragmento adicional.

Salidas literales: `capturas/etapa6_antes_pregunta5_20261028.txt` y
`capturas/etapa6_despues_pregunta5_20261028.txt`.

## Pruebas automatizadas y conclusión

`uv run python -m unittest discover -s tests -v`: **60 pruebas OK**. Se añadieron
pruebas sin red para asegurar que la reformulación se use solo para buscar, que
la respuesta reciba la pregunta original, que `--saltos` muestre ambas y que
`--diagrama` no invoque modelos.

**Conclusión:** el grafo sí recorre el nuevo nodo y `--saltos` muestra la
reformulación. En las salidas medidas, Q3 evitó el punto extra de p.19 pero no
recuperó todas las causales; Q5 conservó la misma respuesta. El usuario
considera que ambos casos evidencian mejora; esa valoración queda registrada
sin sustituir las salidas observadas. No se ajustó `UMBRAL` ni se cambió de nodo.

**Comentario del usuario:** «Claramente mejora la respuesta al ser reformulada,
al menos para los dos casos probados se evidencia una mejora.»

Se conserva esta evaluación del usuario junto a las mediciones anteriores; no
se sustituyen las respuestas, rutas ni parecidos crudos.
