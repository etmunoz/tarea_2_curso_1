<!--
Integrantes: Fabio Durán; Gustavo Reyes; Ezequiel Muñoz
Objetivo: registrar frases, predicción previa, cosenos y conclusión de la etapa de embeddings.
fecha_hora_creacion: 20261027_1907
fecha_hora_modificacion: 20261028_0737
-->

# Embeddings — etapa 2 (10 puntos)

Estado: **ejecutada el 20261028_0737** con `instrucciones/instrucción_07.txt`
("Embeddings: predice antes de medir"). Grupo: **N (confirmado)**.
Integrantes: Fabio Durán, Gustavo Reyes, Ezequiel Muñoz.

Meta declarada en la instrucción: comprobar con frases propias que
"parecido" significa parecido en **significado**, no en palabras.

Evidencia cruda (salidas literales, sin editar):

- `capturas/20261028_0737_etapa2_demo_embeddings.txt` — paso 3, tabla de cosenos.
- `capturas/20261028_0737_etapa2_indice_vs_coseno.txt` — paso 4, tabla de tiempos.

## 1. Las tres frases (paso 1)

Todas del dominio del taller; las dos primeras dicen lo mismo con palabras
distintas, la tercera es de otro tema.

| Nº | Frase exacta | Rol |
| --- | --- | --- |
| 1 | Qué nos dice la ley respecto de los tratamientos de los datos personales | mismo significado que la 2 |
| 2 | Para los datos personales la ley nos indica respecto del tratamiento de ellos | mismo significado que la 1 |
| 3 | Qué hay de los viajes que se tienen que realizar para ir a Colombia | tema distinto |

## 2. Predicción previa (paso 2) — escrita antes de medir

> "Pienso que las primeras dos frases debiesen estar su scoring dentro del
> 0,5 a 0,7 y que la tercera frase bajo 0,5."

| Campo | Registro |
| --- | --- |
| Fecha/hora de la predicción | 20261028_0728 (última modificación de `instrucciones/instrucción_07.txt`) |
| Par que creemos más parecido | **1 – 2**, por compartir "ley", "datos personales" y "tratamiento" con sintaxis distinta |
| Puntuación esperada para 1–2 | **entre 0,5 y 0,7** |
| Puntuación esperada para 1–3 y 2–3 | **por debajo de 0,5** |
| Fecha/hora de ejecución posterior | 20261028_0737 |
| Orden verificable | El archivo de la predicción (07:28) **precede** a la ejecución (07:37): la predicción no se reconstruyó después de ver el resultado |

## 3. Condiciones de ejecución (reproducibles) — paso 3

| Elemento | Valor |
| --- | --- |
| Comando | `uv run python scripts/demo_embeddings.py --frases "Qué nos dice la ley…" "Para los datos personales…" "Qué hay de los viajes…"` |
| Observación sobre el comando | La instrucción lo escribe con argumentos posicionales; `scripts/demo_common.py` los recibe con la bandera `--frases` (nargs=3). Se pasó el mismo texto exacto |
| Modelo de embeddings | `bge-m3` (`EMBEDDING_MODEL`), **1024 dimensiones** |
| Proveedor | Ollama local (`MODEL_PROVIDER=ollama`) |
| Backend / corpus | No interviene: el script solo embebe las tres frases y una pregunta |

## 4. Tabla de cosenos (paso 3) — salida literal

```
Modelo: bge-m3
Frase 1: Qué nos dice la ley respecto de los tratamientos de los datos personales
  Dimensión: 1024 números; primeros 5: [-0.05172588, -0.005091143, -0.07146919, 0.01187918, -0.017032528]
Frase 2: Para los datos personales la ley nos indica respecto del tratamiento de ellos
  Dimensión: 1024 números; primeros 5: [-0.046140056, -0.0016124435, -0.0688577, -0.002652848, -0.034254696]
Frase 3: Qué hay de los viajes que se tienen que realizar para ir a Colombia
  Dimensión: 1024 números; primeros 5: [-0.0251457, -0.015750146, -0.036578428, -0.031398874, -0.0057004923]

Par de frases | Coseno   | Observación
-------------|----------|-----------------
1 - 2        |  0.888802 | MÁS PARECIDO
1 - 3        |  0.379792 |
2 - 3        |  0.343577 |

Pregunta: no tengo internet
  Dimensión: 1024 números; primeros 5: [-0.023461686, 0.022647312, -0.03644255, -0.02742464, -0.029260112]
Frase más cercana: 2 (coseno=0.386233): Para los datos personales la ley nos indica respecto del tratamiento de ellos
OK: demo de embeddings completada.
```

> La última línea usa la **pregunta por defecto** del script
> (`no tengo internet`, de `DEFAULT_QUESTION`), que no pertenece al dominio de
> estas tres frases. Es un artefacto de la demo, **no** un resultado del taller.

## 5. Predicción frente a medición

| Par | Predicho | Medido | ¿Acierto? |
| --- | --- | --- | --- |
| **1 – 2** (mismo significado) | 0,5 – 0,7 | **0.888802** | ✅ Sí es el par más parecido, pero **quedó por encima** de la banda estimada |
| 1 – 3 (otro tema) | < 0,5 | **0.379792** | ✅ |
| 2 – 3 (otro tema) | < 0,5 | **0.343577** | ✅ |

Margen observado: 1–2 supera en **0,509** al peor de los otros dos pares
(0.379792). Entre las dos frases de otro tema y las de mismo significado no hay
zonas de solapamiento.

## 6. Paso 4 — barrido coseno frente a índice (`--n 2000`)

| Campo | Valor |
| --- | --- |
| Comando | `$env:PYTHONIOENCODING='utf-8'; $env:PYTHONUTF8='1'; uv run python scripts/indice_vs_coseno.py --n 2000` |
| Backend | Redis (`VECTOR_STORE=redis`) |
| Tamaños medidos | 200 y 2000; `top-k=3`; 3 repeticiones (mediana) |
| Embeddings | `bge-m3`, reutilizados de caché: 2000/2000 y 5/5, **0 embeddings nuevos** |
| A = barrido coseno en Python · B = índice Redis | Ambos reciben el **mismo** vector de pregunta y los **mismos** vectores de documentos |

### Salida literal (abreviada solo en las filas repetidas de n=2000)

```
Backend: redis; tamaños: [200, 2000]; top-k: 3; repeticiones: 3
A y B reciben el MISMO vector de pregunta y los MISMOS vectores de documentos.
Modelo: bge-m3
Caché vectores_demo: 2000/2000 reutilizados; 0 embeddings nuevos.
Caché preguntas_demo: 5/5 reutilizados; 0 embeddings nuevos.
Dimensión: 1024; los tamaños menores reutilizan el prefijo de la misma matriz.
Índice Redis: etmunoz_ollama_coseno_200_de3bbaaa2e8821c0; HASH e índice comparten los mismos vectores.

n=200
Pregunta | Top-3 A (ID:coseno) | Top-3 B (ID:coseno) | ¿Coinciden? | A ms | B ms | Vectores A→Python | Vectores B→Python
--- | --- | --- | --- | ---: | ---: | ---: | ---:
¿Cómo recupero la conexión a internet si el router no funciona? | F00001:0.7537, F00081:0.7188, F00041:0.7184 | F00001:0.7537, F00081:0.7188, F00041:0.7184 | sí | 18.153 | 2.728 | 200 | 0
¿Cómo preparo una comida casera con verduras? | F00022:0.6725, F00102:0.6496, F00182:0.6483 | F00022:0.6725, F00102:0.6496, F00182:0.6483 | sí | 16.249 | 2.725 | 200 | 0
¿Qué hábitos ayudan a cuidar la salud y descansar? | F00048:0.6381, F00008:0.6256, F00168:0.6216 | F00048:0.6381, F00008:0.6256, F00168:0.6216 | sí | 18.498 | 2.478 | 200 | 0
¿Cómo organizo un viaje y reservo alojamiento? | F00064:0.6767, F00144:0.6556, F00004:0.6553 | F00064:0.6767, F00144:0.6556, F00004:0.6553 | sí | 19.205 | 2.487 | 200 | 0
¿Cómo pruebo y depuro un programa en Python? | F00035:0.6925, F00195:0.6698, F00115:0.6664 | F00035:0.6925, F00195:0.6698, F00115:0.6664 | sí | 17.994 | 2.588 | 200 | 0

Índice Redis: etmunoz_ollama_coseno_2000_c5828ea4b9e088bd; HASH e índice comparten los mismos vectores.

n=2000
¿Cómo recupero la conexión a internet si el router no funciona? | F00001:0.7537, F00801:0.7486, F00401:0.7482 | F00001:0.7537, F00801:0.7486, F00401:0.7482 | sí | 199.435 | 3.199 | 2000 | 0
¿Cómo preparo una comida casera con verduras? | F00742:0.6829, F00342:0.6809, F01542:0.6767 | F00742:0.6829, F00342:0.6809, F01542:0.6767 | sí | 182.918 | 3.244 | 2000 | 0
¿Qué hábitos ayudan a cuidar la salud y descansar? | F01248:0.6474, F01648:0.6449, F01888:0.6440 | F01248:0.6474, F01648:0.6449, F01888:0.6440 | sí | 186.191 | 3.235 | 2000 | 0
¿Cómo organizo un viaje y reservo alojamiento? | F01664:0.6800, F00784:0.6790, F00384:0.6790 | F01664:0.6800, F00784:0.6790, F00384:0.6790 | sí | 203.414 | 3.276 | 2000 | 0
¿Cómo pruebo y depuro un programa en Python? | F01155:0.7133, F01555:0.7089, F00755:0.7084 | F01155:0.7133, F01555:0.7089, F00755:0.7084 | sí | 184.362 | 3.882 | 2000 | 0

Crecimiento (mediana entre las cinco preguntas):
n | A ms | B ms | A/B
---: | ---: | ---: | ---:
200 | 18.153 | 2.588 | 7.01x
2000 | 186.191 | 3.244 | 57.39x

Conclusión calculada:
Coincidieron los top-3 ordenados en 10/10 consultas; B fue más rápido en 10/10. Con n=2000, A/B=57.39x (medianas).
Al pasar de n=200 a 2000, el tiempo mediano de A cambió 10.26x y el de B 1.25x; los tiempos excluyen embeddings e inserción y no demuestran por sí solos complejidad asintótica.
OK: comparación terminada; caché conservada para repetir sin nuevos embeddings.
```

### Cuándo usar cada forma (línea pedida en el paso 4)

> **Barrido coseno en Python (A)**: para verificar o depurar con pocos datos
> (cientos de fragmentos), cuando necesitas ver todos los vectores y auditar los
> puntajes. **Índice vectorial (B)**: para la búsqueda en producción sobre el
> corpus real, porque devuelve los mismos resultados a un costo casi constante
> (3 ms) en lugar de 186 ms.

### Incidencia reproducida y resuelta

La primera ejecución del paso 4 **falló** con `UnicodeEncodeError`: las líneas
387-388 de `scripts/indice_vs_coseno.py` imprimen `→` (U+2192), carácter que
**no existe en cp1252**, la codificación por defecto de la consola de Windows.
Se resolvió **sin modificar el código**, forzando UTF-8 en la salida:

```powershell
$env:PYTHONIOENCODING='utf-8'; $env:PYTHONUTF8='1'; uv run python scripts/indice_vs_coseno.py --n 2000
```

## 7. Conclusión de la etapa

1. **El orden de la predicción se acertó**: 1–2 es el par más parecido y las dos
   frases del tema distinto quedan por debajo de 0,5, como se esperaba.
2. **La magnitud se subestimó**: se predijo 0,5–0,7 y se midió **0.888802**.
   Aunque la frase 2 reordena casi todas las palabras de la frase 1 y comparte
   el mismo vocabulario ("ley", "datos personales", "tratamiento"), el coseno
   premia el **significado compartido**, no la coincidencia literal de la
   cadena. Esto es lo que la instrucción pedía comprobar.
3. **El margen confirma la separación**: hay **0,509** entre el par equivalente
   y el par más parecido de los de otro tema; ninguna pareja de otro tema se
   acerca siquiera a 0,4.
4. **Lo que esta prueba NO demuestra**: son solo 3 frases cortas de un mismo
   dominio, sin ruido ni sinonimia rara. **No** valida por sí sola el umbral de
   recuperación del agente: en `pruebas/bateria.md` se ve que con el mismo
   `bge-m3` los parecidos de preguntas **en contexto** (0.5054, 0.5361) quedan
   **por debajo** de preguntas **fuera de contexto** (0.6104, 0.6286). Que dos
   frases de ~10 palabras se parezcan no garantiza que una pregunta encuentre su
   fragmento correcto entre 294.
5. **El paso 4 refuerza la elección de backend**: con los mismos vectores, el
   índice devuelve los **mismos top-3 ordenados en 10/10 consultas** a 3 ms
   frente a 186 ms (57,39x con n=2000), de modo que no se sacrifica calidad de
   recuperación al usar Redis en lugar del barrido en Python.
