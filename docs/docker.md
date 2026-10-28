<!--
Integrantes: Fabio Durán; Gustavo Reyes; Ezequiel Muñoz
Objetivo: documentar configuración, operación y pruebas del Redis persistente en Docker.
fecha_hora_creacion: 20261027_1842
fecha_hora_modificacion: 20261028_1602
-->

# Docker y Redis del proyecto

Ejecutar todos los comandos desde `C:\Users\etmun\proyecto\tarea_2_curso_1`.
Este es el Redis persistente que se utilizará durante el resto de la tarea;
reemplaza el servidor temporal de las demos y el servidor externo sin memoria.

## Configuración

- Docker Desktop con motor Linux y Docker Compose.
- Servicio `redis` definido en `compose.yaml`, proyecto Compose `tarea_2_curso_1`.
- Imagen Redis 8.2 con Search, fijada por digest para reproducibilidad.
- Puerto del equipo: **127.0.0.1:16379**, dirigido al 6379 del contenedor.
- URL de desarrollo: `redis://localhost:16379`.
- Volumen persistente: **tarea_2_curso_1_redis_data**, montado en `/data`.
- AOF habilitado, sincronización cada segundo. Un fallo abrupto puede perder
  aproximadamente el último segundo de escrituras. El volumen no es un backup.
- Límite de memoria del contenedor: 512 MiB; Redis `maxmemory=256mb` y
  `noeviction`: si se llena, rechaza escrituras en vez de expulsar documentos.
- Política `unless-stopped`: vuelve a arrancar al reiniciar Docker salvo que
  se haya detenido explícitamente. Healthcheck mediante PING.
- Solo desarrollo local: sin contraseña ni TLS, no publicado en la red local.
  No cambiar el enlace a `0.0.0.0` ni usar esta configuración en producción.

El `.env` local queda configurado con estas dos variables, conservando la clave
Google y las demás opciones existentes:

```dotenv
VECTOR_STORE=redis
REDIS_URL=redis://localhost:16379
```

No copiar `.env.example` encima de un `.env` existente: se perderían sus valores.
Las variables del entorno de PowerShell tienen prioridad sobre `.env`.
Si quedaron overrides de pruebas, retirarlos de la sesión:

```powershell
Remove-Item Env:VECTOR_STORE, Env:REDIS_URL -ErrorAction SilentlyContinue
```

## Levantar

Abrir Docker Desktop y esperar a que el motor esté listo, o usar:

```powershell
docker desktop start
docker compose up -d --wait
docker compose ps
docker compose exec -T redis redis-cli ping
```

El último comando debe imprimir `PONG`. `up` crea contenedor, red y volumen
cuando no existen; si ya existen, los reutiliza. El Redis permanece ejecutándose
en segundo plano; no depende de mantener la consola abierta.

## Detener y volver a arrancar

Para apagar **solo el Redis de esta tarea**, conservando contenedor y datos:

```powershell
docker compose stop
```

Para volver a levantarlo:

```powershell
docker compose up -d --wait
```

Para retirar el contenedor y la red, conservando el volumen y sus datos:

```powershell
docker compose down
```

Después, `docker compose up -d --wait` crea un nuevo contenedor y carga los
datos del mismo volumen. **No añadir `--volumes`/`-v` a `down`: borraría los datos.**
No usar `docker volume prune` ni otras limpiezas globales para esta tarea.

Para cerrar Docker Desktop completo, primero guardar el trabajo de los demás
proyectos y detener sus servicios de forma apropiada; después salir desde su
menú. Cerrar Docker Desktop afecta también a los otros contenedores del equipo.
No se ha cerrado Docker Desktop ni detenido servicios ajenos durante esta instalación.

## Estado y diagnóstico

```powershell
docker compose ps
docker compose logs --tail 50 redis
docker compose exec -T redis redis-cli INFO persistence
docker compose exec -T redis redis-cli INFO memory
docker compose exec -T redis redis-cli FT._LIST
docker volume inspect tarea_2_curso_1_redis_data
```

Si el puerto 16379 está ocupado, no detener el proceso ajeno: elegir otro puerto
en `compose.yaml`, actualizar `REDIS_URL` en `.env` y documentar el cambio aquí.
Si se agota la memoria, revisar el uso y ajustar límites o corpus con autorización;
no borrar datos automáticamente.

## Pruebas con los scripts del proyecto

Requieren `GOOGLE_API_KEY` válida en `.env`; envían únicamente las frases de
demostración a Google y pueden generar consumo de API.

```powershell
uv run python scripts/demo_embeddings.py
uv run python scripts/test_storage.py
```

La primera muestra vectores de 3072 números con el modelo configurado,
similitudes coseno y el vecino de la pregunta. La segunda hace PING, crea el
índice `{PREFIJO}_demo_rag` si no existe, guarda tres frases con metadata
`{"fuente": "demo"}` y recupera los dos vecinos de `no tengo internet`.
Repetir la prueba no duplica documentos: sobrescribe las mismas tres claves.
El índice del corpus real `{PREFIJO}_rag` permanece separado.

Para comprobar que sobreviven a un reinicio:

```powershell
docker compose stop
docker compose up -d --wait
docker compose exec -T redis redis-cli FT.INFO etmunoz_demo_rag
uv run python scripts/test_storage.py
```

`FT.INFO` debe mostrar `num_docs` igual a 3 antes de repetir la inserción.
Si se cambia `PREFIJO`, adaptar el nombre del índice del comando anterior.

Pruebas automáticas sin red ni credenciales:

```powershell
uv run python -m unittest discover -s tests -v
```

## Bitácora

### Instalación persistente (instrucción 02b)

- Se comprobó Docker Desktop/Compose y que el puerto 16379 estuviera libre.
- Se añadió `compose.yaml` con volumen persistente, AOF, límites de memoria,
  healthcheck, puerto local y digest fijado de la imagen ya probada.
- Se actualizó únicamente `VECTOR_STORE` y `REDIS_URL` en `.env`, sin mostrar
  secretos ni cambiar `GOOGLE_API_KEY`. Se creó `.env.example` sin credenciales.
- No se migran datos del Redis externo; las demos generan sus propios datos.
  Para documentos del corpus, volver a ejecutar `scripts/ingest.py` contra este Redis.
- Se ejecutó `docker compose config --quiet`: configuración válida.
- Se ejecutó `docker compose up -d --wait`: creó la red del proyecto, el
  volumen `tarea_2_curso_1_redis_data` y el contenedor
  `tarea_2_curso_1-redis-1`; resultado `healthy`.
- `docker compose ps` confirmó la publicación exclusiva en `127.0.0.1:16379`.
  `docker compose exec -T redis redis-cli INFO persistence` confirmó AOF activo.
- `uv run python scripts/demo_embeddings.py`: **OK**, embeddings reales de
  `models/gemini-embedding-001`, 3072 números por vector. El par 1–2 fue el más
  parecido (coseno 0.927308); la pregunta quedó más cerca de la frase 1.
- `uv run python scripts/test_storage.py`: **OK**, PING, creación del índice
  `etmunoz_demo_rag`, tres documentos y recuperación de dos vecinos con
  `fuente=demo`. Distancias coseno: 0.188980 y 0.214275.
- Se ejecutó `docker compose down` **sin borrar volúmenes**, seguido de
  `docker compose up -d --wait`. Antes de reinsertar documentos se comprobó
  mediante el cliente Python Redis que `FT.INFO etmunoz_demo_rag` conservaba
  `num_docs=3` y `INFO persistence` mostraba `aof_enabled=1`: **persistencia OK**.
- Se repitió `uv run python scripts/test_storage.py` tras recrear el contenedor:
  **OK**, recuperó los mismos vecinos y reutilizó las claves de demostración.
- `uv run python -m unittest discover -s tests -v`: **19 pruebas aprobadas**.
- Estado de entrega: Redis persistente **encendido y saludable**. No se
  detuvieron contenedores ajenos, no se eliminó el volumen y no se modificaron
  datos del Redis externo. La imagen descargada previamente se reutilizó.

### Reejecución con salidas en pantalla (instrucción 02b actualizada)

- `docker compose exec -T redis redis-cli ping`: `PONG`.
- `uv run python scripts/demo_embeddings.py`: **OK**; par más parecido 1–2
  (0.927308) y frase 1 más cercana a la pregunta (0.811020).
- `uv run python scripts/test_storage.py`: **OK** sobre el Redis persistente;
  distancias de los dos vecinos 0.188980 y 0.214275, metadata `fuente=demo`.
- `uv run python -m unittest discover -s tests -v`: **19 pruebas aprobadas**
  en 0.124 s.
- Se mostraron las salidas completas en la conversación para copiar y pegar.
  No se reinició ni recreó el contenedor; la demo reutilizó sus tres claves.
  No se borraron índices, volúmenes ni datos ajenos a la demostración.

### Comparación coseno e índice (instrucción 03)

- `docker compose ps` confirmó el Redis persistente `healthy` en
  `127.0.0.1:16379`; no se recreó ni se detuvo el contenedor.
- Se añadió `scripts/indice_vs_coseno.py`, que utilizará índices independientes
  `{PREFIJO}_coseno_{n}_{huella}` con HASH propios para cada conjunto sintético.
  A y B comparten esos mismos HASH; no toca el índice RAG ni las demos anteriores.
- Se ejecutó `uv run python scripts/indice_vs_coseno.py --n 2000`. El primer
  intento se detuvo por cuota Google 429, conservando 100 vectores en caché local.
- Se inició la reanudación con reintentos acotados. No se modificaron límites de memoria ni `.env`,
  ni se borraron índices, contenedores o volúmenes para completar la prueba.
- Esa reanudación se interrumpió por el límite de 120 s del ejecutor tras guardar
  200 vectores. Se inició otra sin límite temporal, conservando la caché y sin
  reiniciar Docker. La última ejecución terminó con código 1 por cuota Google
  429, tras guardar **900 de 2000 vectores** y agotar los reintentos del siguiente lote.
- No se alcanzó la fase de creación de índices Redis del benchmark; no hay
  mediciones de búsqueda de esta ejecución. Los índices de las demos anteriores
  y del proyecto no se borraron ni se modificaron como parte de esta preparación.
- No se inició otro reintento. La caché parcial queda disponible sin cambiar
  límites de Docker ni realizar limpiezas de memoria o volúmenes.

### Migración a Ollama y comparación real (instrucción 03c)

- No se reinició, recreó ni reconfiguró Docker durante la migración a Ollama.
  Redis sigue en `127.0.0.1:16379` con el volumen `tarea_2_curso_1_redis_data`
  y su estado `healthy`; el cliente Python corre en Windows y usa Ollama local.
- Se añadió `MODEL_PROVIDER=ollama` a `.env`; la clave Google se conservó sin
  mostrarse para poder volver a `MODEL_PROVIDER=google`.
- Se crearon índices independientes `etmunoz_ollama_coseno_200_de3bbaaa2e8821c0`
  y `etmunoz_ollama_coseno_2000_c5828ea4b9e088bd`, con HASH propios ligados al
  contenido y al modelo BGE-M3. No se borraron ni modificaron los índices de
  las demos anteriores ni los del proyecto.
- La primera ejecución del benchmark falló en la búsqueda con `KeyError: 2`
  por usar el parser RESP2 con la respuesta RESP3 del servidor; los índices se
  conservaron para reproducir y corregir el defecto sin reembeber.
- Tras corregir el parser, la comparación terminó con código 0 reutilizando la
  caché local (2000 vectores y 5 preguntas, 0 embeddings nuevos), sin llamadas
  a Google y sin superar el `maxmemory` de 256 MiB.
- No se realizó `docker compose down`, no se borraron volúmenes y no se
  reinició el contenedor en ninguna de estas operaciones.
- La escala 20000 no se ejecutó; no se ampliaron límites de memoria para ella.

### Ingesta real del corpus (instrucción 04)

- Redis permaneció `healthy` en `127.0.0.1:16379` durante toda la operación;
  no se reinició, recreó ni detuvo el contenedor, y no se tocó el volumen.
- Se ejecutó `uv run python scripts/ingest.py docs/LEY-19628_28-AGO-1999_refundida_20261201.pdf --reset`.
  `--reset` informó que el índice `etmunoz_ollama` no existía, por lo que no hubo
  borrado previo; solo se creó el índice nuevo con claves `etmunoz_ollama:rag:*`.
- Resultado real: **57 páginas leídas, 318 fragmentos generados**, tamaño medio
  580.3 caracteres (mínimo 24, máximo 800) con `CHUNK_SIZE=800` y
  `CHUNK_OVERLAP=120`. El solape real entre los fragmentos 1 y 2 fue de 83 caracteres.
- Los índices de las demos (`etmunoz_ollama_demo`) y los del benchmark
  (`etmunoz_ollama_coseno_*`) no se borraron ni modificaron.
- Sin `--reset`, una segunda ejecución agrega sin duplicar: los IDs son
  estables por hash de contenido (fuente + página + texto).

### Reingesta tras corregir el troceado (20261027_2337) y verificación (20261028)

- **Propósito**: aplicar la corrección del troceado (`merge_small_fragments()`
  en `scripts/ingest.py`, que funde los fragmentos menores que
  `CHUNK_SIZE//4 = 200` caracteres con un vecino de la **misma página**, en dos
  pasadas y sin superar `1.5 · CHUNK_SIZE = 1200`) y regenerar el índice, porque
  ninguna de las 30 configuraciones de `CHUNK_SIZE`/`CHUNK_OVERLAP` probadas
  unía el encabezado `c) Principio de proporcionalidad` con su contenido.
- **Comando**: `uv run python scripts/ingest.py docs/LEY-19628_28-AGO-1999_refundida_20261201.pdf --reset`
- **Efecto sobre los datos**: `--reset` **borró y recreó** el índice
  `etmunoz_ollama` (claves `etmunoz_ollama:rag:*`). El índice pasó de **318 a
  294 fragmentos**: 24 fusionados, tamaño mínimo **24 → 200** caracteres,
  máximo 988, media **580.3 → 627.6**. Verificado después: 0 fragmentos con
  texto repetido y la única cabecera duplicada (p.1) ya venía del PDF.
- **Los separadores no se tocaron**: siguen fijos en
  `["\n\n", ". ", " ", ""]` por `instruccion_04.txt`; el cambio se hizo solo
  en la posprocesión de fragmentos.
- **Verificación (20261028_0747 y 0813)**: `FT.SEARCH` sobre
  `etmunoz_ollama_rag` devuelve **294 docs**; midiendo el campo `text` de las
  294 claves: media **627.6**, mínimo **200**, máximo **988** y **0 fragmentos
  por debajo de 200 caracteres**. `get_settings()` reporta `umbral 0.58`,
  `chunk_size 800`, `chunk_overlap 120`, `top_k 3`.
- **Estado del contenedor**: Redis permaneció `healthy` en `127.0.0.1:16379`;
  **no** se reinició, recreó ni detuvo, y **no** se borró el volumen
  `tarea_2_curso_1_redis_data`. No se ejecutó `docker compose down`.
- **Índices no afectados**: `etmunoz_ollama_demo` y `etmunoz_ollama_coseno_*`
  quedaron como estaban.
- **Pruebas**: `uv run python -m unittest discover -s tests` → **59 pruebas OK**
  (5 nuevas de `merge_small_fragments()`).
- **Efecto en la etapa 4**: la pregunta 2 pasó de un fragmento de 125
  caracteres sin contenido a uno de 829 con el literal completo; su parecido
  bajó de 0.5850 a 0.5054 (detalle y seis corridas de la batería en
  `entrega/grupo-N-taller2-rag/pruebas/bateria.md`).
- **Cambio posterior de configuración (20261028_0849, sin operación Docker)**:
  `UMBRAL` pasó de `0.58` a `0.43` tras un barrido exhaustivo y la activación de
  la regla 5 del `SYSTEM_PROMPT`. **No hubo reingesta ni toque a contenedores**:
  el umbral se lee en cada consulta desde `get_settings()`, así que el índice
  de 294 fragmentos en `tarea_2_curso_1_redis_data` **no cambió**. Verificado
  con `FT.SEARCH` → 294 docs y con
  `uv run python main.py rag "…" --saltos`, que leyó `0.43` del `.env`.
  Detalle en `pruebas/bateria.md` (sección "Barrido exhaustivo de `UMBRAL` y
  configuración final").

---

## 20261028_1014 — tres reingestas para la etapa 3 (comparar chunk y solape)

- **Propósito**: medir con datos cómo cambia el documento al cortarlo distinto
  (`instrucciones/instruccion_10.txt`), no cambiar de servidor.
- **Comando, repetido tres veces** (solo cambiaba `CHUNK_SIZE`/`CHUNK_OVERLAP`
  en `.env`):

  ```powershell
  uv run python scripts/ingest.py "docs/LEY-19628_28-AGO-1999_refundida_20261201.pdf" --reset
  ```

- **Orden y resultados**:

  | Paso | `.env` | Páginas | Fragmentos nuevos | Promedio | Mín / máx | Fusionados |
  | --- | --- | ---: | ---: | ---: | ---: | ---: |
  | A | 400 / 50 | 57 | **573** | 320.4 | 101 / 490 | 54 (mín. 100) |
  | B | 1200 / 200 | 57 | **193** | 971.2 | 322 / 1399 | 17 (mín. 300) |
  | Final | **800 / 120** | 57 | **294** | 627.6 | 200 / 988 | 24 (mín. 200) |

- **Efecto sobre los datos**: cada paso ejecutó **`--reset` sobre el índice
  `etmunoz_ollama`**, es decir, **borró y repobló** ese índice dentro del volumen
  `tarea_2_curso_1_redis_data`. Las tres salidas confirman
  `0 ya existían`, es decir que **no se mezclaron** fragmentos de ingestas
  anteriores. **El volumen no se borró, el contenedor no se reinició ni se
  detuvo** y `docker compose down` **no** se ejecutó.
- **Estado final**: índice `etmunoz_ollama_rag` con **294 fragmentos**, la
  configuración **elegida (800/120)**, coherente con el `.env` que queda para el
  resto del taller.
- **Índices ajenos no afectados**: `etmunoz_ollama_demo` y
  `etmunoz_ollama_coseno_*` siguen como estaban.
- **Salidas guardadas**: `entrega/grupo-N-taller2-rag/pruebas/capturas/
  20261028_1014_etapa3_ingesta_{A_400_50,B_1200_200,base_800_120}.txt`.
  Análisis y elección en `pruebas/chunks.md`.

## 20261028 — instrucción 11: consultas y cambio de TOP_K

Propósito: comparar cobertura y rechazos con K=1, 3, 4 y 5. Comandos:
`uv run python scripts/bateria.py --top-k 1 --solo 1,2,3,4,5 --salida resultado.json`,
análogos con K=5 y baterías completas con K=4/5; consultas `main.py --saltos`.
Resultado: se elige TOP_K=4; permanecen UMBRAL=0.43 y chunks 800/120.
No se ejecutaron operaciones Docker ni ingestas. Estas consultas no cambian
los 294 fragmentos del índice; contenedor y volumen persistente se conservan.
Detalle y evidencias: `entrega/grupo-N-taller2-rag/pruebas/bateria.md`.

Registrar aquí cada operación o cambio Docker de esta tarea: propósito,
comandos, resultado y efecto sobre contenedores, volúmenes o datos. Nunca
incluir claves, contraseñas ni URLs privadas.
