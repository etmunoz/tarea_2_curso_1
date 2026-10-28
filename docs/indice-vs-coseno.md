<!--
Integrantes: Fabio Durán; Gustavo Reyes; Ezequiel Muñoz
Objetivo: documentar el benchmark de coseno e índice, su caché, metodología y ejecución reproducible.
fecha_hora_creacion: 20261027_1923
fecha_hora_modificacion: 20261027_1951
-->

# Índice vectorial frente a coseno a mano — instrucción 03

## Ejecutar desde la raíz

```powershell
uv run python scripts/indice_vs_coseno.py --n 2000
```

Equivalente con `.venv` activado: `python scripts/indice_vs_coseno.py --n 2000`.
El backend es `VECTOR_STORE` de la configuración existente; Redis usa el
servidor persistente del proyecto. No se modifica `.env` ni se ingiere el PDF.

- `--n 2000` mide 200 y 2000 documentos.
- `--n 20000` mide 200, 2000 y 20000, con costes y memoria superiores.
- Si se indica otro máximo, también se incluye ese tamaño; por ejemplo,
  `--n 500` mide 200 y 500. Mínimo admitido: 3.
- `--repeticiones 3` es el valor predeterminado: tres mediciones de cada método
  por pregunta, además de un calentamiento excluido de los tiempos.

La primera ejecución llama a Google para generar embeddings reales y puede
generar consumo. La caché ahorra llamadas posteriores; no se prometen costes
nulos si aún faltan vectores o si hay que recuperar una caché perdida.

## Datos idénticos, sin reembeddings en la comparación

El generador determinista produce frases cortas sobre internet, cocina, salud,
viajes y programación; cada una tiene un identificador de caso único.
Los conjuntos menores son prefijos del mayor. Se calculan los embeddings
documentales una vez y cinco embeddings de preguntas, separadamente.
Cada método recibe el mismo vector de pregunta y los mismos vectores documentales.

Las tablas identifican los fragmentos como `F00001`, `F00002`, etc. El texto
exacto está en la lista `texts` de `data/vectores_demo.json`, en ese mismo orden,
y en los HASH de Redis. Se muestran tres IDs y sus similitudes por método.

### Caché

| Archivo local (no versionado) | Contenido |
| --- | --- |
| `data/vectores_demo.npy` | Matriz FLOAT32 de embeddings documentales |
| `data/vectores_demo.json` | Modelo, configuración, textos y número de filas completadas |
| `data/preguntas_demo.npy` | Matriz FLOAT32 de las cinco preguntas |
| `data/preguntas_demo.json` | Identidad y progreso de las preguntas |

Se valida modelo, dimensionalidad solicitada y textos antes de reutilizarla.
Se amplía para un `n` mayor sin reembebir su prefijo completo. Tras cada lote
de hasta 100 textos se guarda el progreso; las preguntas se guardan una a una.
En una ejecución interrumpida pueden existir filas reservadas aún no calculadas:
solo las primeras `completed` filas del JSON son válidas. No utilizar `.npy`
sin su JSON ni editar uno de los archivos por separado.

No hay garantía de recuperar una respuesta de API que haya tenido éxito remoto
pero no haya podido guardarse localmente por un fallo abrupto. En el caso normal,
las filas marcadas completas no vuelven a enviarse. No ejecutar procesos
concurrentes sobre esta misma caché. Para otro modelo, conservar una copia
separada y coherente de los archivos en vez de mezclar embeddings.

Google puede devolver 429. Se respetan esperas temporales indicadas por el
proveedor, con hasta tres reintentos por lote, sin repetir lotes guardados.
Una cuota diaria identificada no se reintenta automáticamente. Si sigue
fallando, el script termina con error y conserva el progreso para una ejecución
posterior. No imprime las claves ni el texto íntegro de errores de proveedores.

## Forma A: barrido exhaustivo en Python

- Redis: un HASH por fragmento con `id`, `text` y `vector` binario. Cada búsqueda
  trae **todos** los vectores a Python mediante pipelines y calcula cosenos
  con NumPy. El cronómetro incluye transferencia, conversión, cálculo y ordenación.
- FAISS: la forma A guarda los mismos vectores en una lista Python. Ya están
  en RAM: incluye conversión, cálculo y ordenación, pero **no hay transferencia
  por red**. La tabla indica `n` vectores usados en Python, no `n` viajes de red.

## Forma B: índice vectorial exacto

- Redis: el índice FLAT usa COSINE sobre el campo de los **mismos HASH**, sin
  duplicar embeddings mediante llamadas a Google. Consulta `FT.SEARCH KNN`
  devolviendo solo ID y distancia; convierte `1 - distancia` a similitud coseno.
- FAISS: `IndexFlatIP` sobre los mismos vectores normalizados; consulta mediante
  `similarity_search_with_score_by_vector`, sin volver a embeber la pregunta.
- A Python vuelven **cero vectores documentales** en B: solo vecinos/IDs y puntajes.
  El vector de consulta enviado no se cuenta como vector documental recibido.
- La coincidencia compara los tres IDs en orden. Empates o redondeo de FLOAT32
  pueden cambiar el orden: se informa la diferencia, no se fuerza una coincidencia.

## Metodología y límites de la conclusión

Para cada tamaño y cada una de las cinco preguntas se hace un calentamiento y
se alterna el orden de A/B en las repeticiones. Cada celda de tiempo es la mediana
de sus repeticiones; el resumen por tamaño toma la mediana entre preguntas.
Los conteos de transferencia son **por búsqueda**, no el total de repeticiones.
Se excluyen embeddings, preparación, inserción e inicialización del índice.

La conclusión de dos líneas usa coincidencias, métodos más rápidos y cambios
de las medianas entre el menor y el mayor tamaño. No presupone que B gane.
Los índices FLAT siguen siendo búsquedas exactas con coste lineal en vectores:
la demostración muestra también el efecto de ejecutar cerca de los datos y
evitar transferencias. No demuestra una complejidad sublineal ni generaliza
unos pocos tiempos a cualquier hardware o corpus.

Los 20000 vectores de 3072 componentes ocupan aproximadamente 234 MiB solo
en la matriz FLOAT32. Redis necesita además los HASH, el índice y otras
estructuras; el límite actual de 256 MiB puede ser insuficiente. No se amplía
automáticamente ni se borran datos para liberar espacio. Si se quiere ejecutar
esa escala, revisar capacidad con autorización o probar FAISS con RAM suficiente.

## Estado de verificación

- **45 pruebas automatizadas aprobadas**, sin red, incluyendo FAISS real,
  consulta KNN simulada, reuso/extensión/reanudación de caché, cuotas temporales/diarias
  y el parser de `FT.SEARCH` en RESP2 y RESP3.
- Primer intento real con Redis y `--n 2000`: Google devolvió 429 tras guardar
  el primer lote de 100 vectores. No se considera una comparación completada.
- La primera reanudación alcanzó 200 vectores guardados, pero el ejecutor la
  interrumpió al superar 120 segundos mientras respetaba las cuotas temporales.
- Se volvió a iniciar en segundo plano sin límite temporal del ejecutor,
  reutilizando el progreso. La ejecución **terminó con código 1** por cuota
  Google 429 después de agotar los tres reintentos del lote siguiente.
- Progreso final verificado localmente: **900 de 2000 vectores documentales
  completos**, modelo `models/gemini-embedding-001`. La matriz reservada es
  `(2000, 3072)`; las 1100 filas restantes no son embeddings válidos. Los 900
  vectores completos se conservan y tienen valores finitos.
- No se llegó a calcular las cinco preguntas ni a construir los índices del
  benchmark, porque la carga completa de embeddings ocurre antes de esa fase.
  No hay tablas reales de comparación ni conclusiones de rendimiento todavía.
- No queda una ejecución Gemini de este benchmark en segundo plano. No se
  iniciaron más reintentos automáticamente ni se mezcló esta caché con BGE-M3.
- La escala 20000 no se ejecutó en esta preparación.

## Ejecución real con Ollama/BGE-M3 (instrucción 03c)

Tras migrar el programa a Ollama, el benchmark se ejecutó con `bge-m3`
(dimensión 1024) y Redis. Los 2000 vectores y las 5 preguntas se generaron sin
llamadas a Google y quedaron en `data/embeddings/fe5309331e3296e4/`, separados
de la caché Gemini de `data/vectores_demo.*`.

### Bug detectado y corregido durante la ejecución

La primera ejecución con BGE-M3 cargó los 2000 embeddings y creó el índice de
n=200, pero falló con `KeyError: 2` en la fase de búsqueda. La causa no era
Ollama: `redis-py` habló con el servidor mediante **RESP3**, que devuelve
`FT.SEARCH` como un **diccionario** con `results` y `extra_attributes`, mientras
que el parser esperaba la **lista plana** de RESP2. Con Gemini la ejecución nunca
había alcanzado esa fase por el 429, por lo que el defecto permanecía latente.
Se añadió `parse_search_response()`, que admite ambos protocolos y usa el id de
la clave cuando RESP3 omite el campo, más cuatro pruebas nuevas. Se verificó
que ambos formatos producen los mismos puntajes (`1 - distancia`).

### Resultados reales (Redis, `--n 2000`, 3 repeticiones)

| n | A (coseno a mano) ms | B (índice Redis KNN) ms | A/B |
| ---: | ---: | ---: | ---: |
| 200 | 17.261 | 2.535 | 6.81x |
| 2000 | 206.693 | 4.145 | 49.87x |

Transferencia por búsqueda: A movió 200 y 2000 vectores completos de Redis a
Python; B movió 0 vectores documentales. Los **top-3 coincidieron en orden en
10/10 consultas** y B fue más rápido en 10/10.

Conclusión calculada por el propio script:

```text
Coincidieron los top-3 ordenados en 10/10 consultas; B fue más rápido en 10/10. Con n=2000, A/B=49.87x (medianas).
Al pasar de n=200 a n=2000, el tiempo mediano de A cambió 11.97x y el de B 1.63x; los tiempos excluyen embeddings e inserción y no demuestran por sí solos complejidad asintótica.
```

Ambos métodos devuelven resultados **idénticos**: el índice no aproxima, solo
evita traer los vectores a Python. Redis no superó su `maxmemory` con BGE-M3.
La escala 20000 sigue sin ejecutarse y no se afirma nada sobre ella.
