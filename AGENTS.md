<!--
Integrantes: Fabio Durán; Gustavo Reyes; Ezequiel Muñoz
Objetivo: definir las reglas de desarrollo, documentación y entrega del proyecto.
fecha_hora_creacion: 20261027_1814
fecha_hora_modificacion: 20261027_1913
-->

# Reglas del proyecto

- Usar Python 3.12, `uv` y el entorno virtual `.venv`.
- Los agentes van en `src/{nombre_agente}/`, con `graph.py`, `prompts.py` y `tools.py`.
- `src/rag/storage.py` expone `get_vector_store(prefijo)`, que devuelve Redis o FAISS según `VECTOR_STORE`. FAISS es el valor predeterminado.
- Ejecutar desde la raíz: `python main.py {nombre_agente} "pregunta"` (o `uv run python ...`).
- `--saltos` imprime los nodos recorridos por el grafo.
- `--diagrama` imprime el Mermaid del grafo sin ejecutarlo ni requerir credenciales.
- Los scripts sueltos (demos, ingesta) van en `scripts/`; los índices FAISS, en `data/`.
- El modelo de embeddings se lee SIEMPRE de `EMBEDDING_MODEL`, únicamente en `src/rag/embeddings.py`.
- No incluir secretos en código ni versionar `.env`, documentos privados no autorizados o índices locales. El PDF autorizado del corpus debe incluirse en `docs/` y en la entrega, según la rúbrica.
- Mantener pruebas sin red ni credenciales; ejecutar `uv run python -m unittest discover -s tests -v`.
- Para esta tarea, trabajar con el Redis persistente de `compose.yaml`, configurado en `.env` y `.env.example`; FAISS sigue disponible como alternativa.
- Documentar de aquí en adelante cada cambio u operación Docker del proyecto en `docs/docker.md`, incluidos propósito, comandos, resultados y efecto sobre los datos.
- No detener contenedores de otros proyectos ni borrar el volumen `tarea_2_curso_1_redis_data` sin autorización explícita.
- Todos los archivos `.md` y `.py` propios del proyecto deben incluir integrantes (Fabio Durán, Gustavo Reyes y Ezequiel Muñoz), objetivo, `fecha_hora_creacion` y `fecha_hora_modificacion` en formato de 24 horas `YYYYMMDD_hhmm`. Conservar la creación y actualizar la modificación al editar. No modificar dependencias ni `.venv` para aplicar esta regla.
- Preparar las evidencias en `entrega/grupo-N-taller2-rag/`; **N es el nombre confirmado del grupo**, no un marcador a reemplazar. Mantener el código fuente canónico en la raíz y copiarlo a `proyecto/` solo al cerrar la entrega, evitando duplicados desactualizados.
- No generar el ZIP ni `documento-entrega.docx` hasta el final. El documento debe detallar cada instrucción `instruccion_NN.txt`/`instruccion_NNx.txt` (también con tilde), con pruebas, prompts y conclusiones, sin inventar resultados de etapas pendientes.
- Identificación obligatoria (`instruccion_02e.txt`): poner nombres y apellidos completos de todos los integrantes y nombre o número de grupo en la **primera página del documento final** y, de forma visible, en `README.md`. Según `instruccion_02f.txt`, los nombres completos confirmados son Fabio Durán, Gustavo Reyes y Ezequiel Muñoz; el nombre confirmado del grupo es **N**. No añadir apellidos ni sustituir el nombre del grupo sin una nueva indicación del usuario.
- Si se utilizó material de un compañero, atribuirlo por nombre y apellidos, identificar el material y dónde se usó, tanto en el README como en el documento final. Si aún no se ha confirmado, registrar la declaración como pendiente; solo declarar que no se usó material de compañeros cuando esté confirmado.
- Declaración confirmada en `instruccion_02f.txt`: **no se utilizó material de compañeros**. Mantener esta declaración en README y documento final; actualizarla con atribuciones si posteriormente se incorpora ese material.

## Reglas de evaluación y evidencias obligatorias

- Seguir la rúbrica completa de `docs/reglas-taller.md` (fuente: `instrucciones/instruccion_02d.txt`). Se evalúan sobre todo las pruebas del agente y el pulido de prompts; entregar código sin evidencias no cumple la entrega.
- Entregar las tres partes completas: todo el código final, todos los prompts y todas las pruebas. Las pruebas unitarias no reemplazan las pruebas de las etapas ni sus capturas.
- Conservar los dos tipos de prompts: instrucciones exactas dadas a OpenCode, correcciones e iteraciones; y prompts efectivos del agente (`SYSTEM_PROMPT`, `USER_PROMPT` y el del nodo extra al implementarse). Registrar versiones antes/después, motivos y evidencias; no confundir un requisito pendiente con una implementación existente.
- Cada etapa debe tener una conclusión corta basada en resultados reales, comandos/configuración reproducibles y referencias a tablas y capturas. Sin resultados, marcar explícitamente pendiente/no ejecutado.
- Etapa 1 (10 puntos): captura del agente respondiendo, prompts de OpenCode y qué se corrigió.
- Etapa 2 (10 puntos): tres frases, predicción previa, tabla de cosenos y conclusión.
- Etapa 3 (15 puntos): comparar al menos dos configuraciones de chunk/solape y justificar la elegida con pruebas.
- Etapa 4 (20 puntos): diez preguntas con ruta, parecido, respuesta y cita; justificar UMBRAL y TOP_K con datos.
- Etapa 5 (25 puntos): cambiar dos reglas de prompts; comparar antes/después en las mismas tres preguntas; ejecutar la prueba de la trampa y conservar `prompts.py` final.
- Etapa 6 (15 puntos): explicar por qué/para qué/qué hace el nodo extra, mostrar rutas con `--saltos` antes/después y dos preguntas donde mejora. No considerar automáticamente el nodo `no_context` existente como cumplimiento de esta etapa.
- Documento (5 puntos): identificación del grupo, orden, pruebas, ambos tipos de prompts y conclusión por etapa. Bonus opcional (+10): repetir la misma batería con FAISS y compararla con Redis bajo condiciones comparables.
- No realizar etapas futuras solo por reforzar estas reglas. Completar sus implementaciones y pruebas cuando se soliciten; mantener las plantillas de entrega alineadas con la rúbrica.
