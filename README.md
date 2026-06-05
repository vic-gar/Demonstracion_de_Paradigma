# Demostración de Paradigma - Motor de búsqueda para archivos de logs

# Descripción

## Contexto del problema

Hoy en día, las aplicaciones, servidores y servicios de red generan grandes cantidades de archivos de logs que registran información relevante sobre su comportamiento: errores del sistema, conexiones de red, advertencias, fallos de autenticación, monitoreo de servicios y posibles incidentes de seguridad.

El problema surge cuando hay que analizar manualmente todos esos archivos. Cuando existen cientos o miles de logs, la búsqueda se vuelve lenta, tediosa y poco práctica, siendo una situación bastante común en áreas como la administración de servidores, el monitoreo de infraestructura, la ciberseguridad y el análisis forense digital.

A partir de esta necesidad, decidí desarrollar una herramienta capaz de procesar múltiples archivos de forma eficiente, aprovechando la concurrencia y las expresiones regulares.


# Objetivo del proyecto

El objetivo principal de este proyecto fue desarrollar un motor concurrente de búsqueda basado en expresiones regulares (Regex), inspirado en herramientas como `grep`. El sistema debe ser capaz de recorrer múltiples archivos, procesarlos de manera concurrente, detectar patrones dinámicamente y reducir el tiempo de búsqueda en comparación con una implementación secuencial tradicional.

Con esto se busca demostrar cómo la programación concurrente puede aplicarse para optimizar tareas de procesamiento masivo de texto, distribuyendo la carga de trabajo entre varios workers.


# Inspiración del proyecto

Este proyecto tomó como referencia la herramienta clásica de Unix/Linux llamada `grep`, ampliamente utilizada para buscar patrones dentro de archivos de texto mediante expresiones regulares.

La documentación oficial de GNU Grep la describe así:

> "`grep` searches the named input files for lines containing a match to the given patterns."

La idea fue tomar ese concepto base y extenderlo con soporte de concurrencia, permitiendo procesar múltiples archivos de forma simultánea. A diferencia del `grep` tradicional, que generalmente opera de forma secuencial, esta propuesta incorpora una arquitectura basada en el patrón Productor–Consumidor, además de métricas y benchmarking para evaluar el desempeño del sistema.


# Paradigmas utilizados

El paradigma principal de este proyecto es la programación concurrente. La solución utiliza múltiples hilos que trabajan al mismo tiempo para procesar diferentes archivos de logs. Para coordinar el acceso a los recursos compartidos se emplea una cola de tareas y una clase ContextoBusqueda que encapsula los resultados y el mecanismo de sincronización mediante locks, lo que evita condiciones de carrera y posible corrupción de datos, haciendo que el sistema aproveche mejor los recursos del equipo y reduzca el tiempo total de procesamiento cuando se trabaja con muchos archivos.

Como paradigma secundario se utilizaron expresiones regulares y scripting para realizar búsquedas dinámicas de patrones textuales. Con Regex, el sistema puede detectar coincidencias complejas dentro de los logs, permitiendo al usuario ingresar tanto texto simple como expresiones regulares avanzadas, y también cuenta con patrones predefinidos para los casos de búsqueda más comunes.


# Modelos

## Arquitectura general

La arquitectura implementada sigue el patrón Productor–Consumidor. En este modelo, un componente productor recorre los directorios y agrega los archivos encontrados a una cola compartida de tareas, luego, múltiples workers actúan como consumidores: toman archivos de esa cola y los procesan de forma concurrente.

En esta arquitectura, el escáner de archivos es el productor, y los workers son los consumidores, cada worker obtiene un archivo de la cola, aplica la expresión regular y almacena los resultados encontrados.

### ¿Por qué Productor–Consumidor y no otro modelo?

Este patrón es el más adecuado para el problema porque la tarea es naturalmente asimétrica: escanear archivos es rápido, mientras que leer línea por línea y aplicar una expresión regular es la operación costosa. En el modelo Productor–Consumidor, la cola actúa como buffer entre ambos roles, desacoplando la velocidad de producción de la de consumo y permitiendo que los trabajadores operen a su propio ritmo sin bloquear el escaneo (Silberschatz et al., 2018, 7.1.1). Además, si un archivo tiene miles de líneas y otro tiene diez, el trabajador que termina primero toma el siguiente de la
cola de inmediato, distribuyendo la carga de forma natural sin necesidad de repartirla desde antes.

Para evitar conflictos cuando varios threads modifican al mismo tiempo las estadísticas o la lista de resultados, el sistema utiliza `threading.Lock()` encapsulado dentro de ContextoBusqueda.  La arquitectura se representa gráficamente de la siguiente forma: 

<img width="603" height="680" alt="Usuario ingresa patrón" src="https://github.com/user-attachments/assets/5b5d8883-8bea-4db0-a479-8bd3bf2326de" />


# Implementación

El proyecto fue desarrollado en Python, ya que ofrece buen soporte nativo para concurrencia, manejo de expresiones regulares y permite prototipar de forma rápida.

Las librerías principales utilizadas fueron:

```python
os
re
sys
time
queue
threading
```

La librería `threading` permite crear los workers concurrentes, `queue` implementa la cola compartida de forma segura entre threads, y `re` proporciona el soporte para expresiones regulares dinámicas.

El sistema acepta búsquedas mediante:

* texto simple,
* patrones predefinidos,
* expresiones regulares avanzadas.

Algunos ejemplos de patrones predefinidos incluyen la detección de errores, warnings, direcciones IP y eventos de seguridad.


# Pruebas

Para verificar que el sistema funcionara correctamente se realizaron pruebas tanto funcionales como de rendimiento.

En las pruebas funcionales se comprobó que las expresiones regulares detectaran bien los patrones dentro de los logs. Por ejemplo, al buscar con `ERROR.*` sobre una línea como `ERROR Database timeout`, el sistema identificó la coincidencia correctamente.

<img width="449" height="228" alt="image" src="https://github.com/user-attachments/assets/60225eef-79cb-415a-a878-2554d2ab851d" />

<img width="460" height="127" alt="image" src="https://github.com/user-attachments/assets/45844de5-f5fa-44da-8a07-526fee655097" />

También se probó la detección de direcciones IP con el patrón:

```regex
\d+\.\d+\.\d+\.\d+
```

obteniendo resultados correctos en los archivos procesados.

<img width="435" height="198" alt="image" src="https://github.com/user-attachments/assets/8eb356e1-ccfa-4709-b442-428fded67e46" />

<img width="440" height="117" alt="image" src="https://github.com/user-attachments/assets/18fa8486-4058-448d-adda-8431d2eb1d28" />

Para ejecutar el sistema no se requieren librerías externas, ya que todas las que utiliza vienen incluidas en la instalación estándar de Python. Para correrlo, desde la terminal hay que ubicarse en la carpeta del proyecto y ejecutar el siguiente comando:

```
python grep.py <patrón> [directorio]
```

En donde el parámetro <patrón> es obligatorio e indica qué se quiere buscar, el parámetro [directorio] es opcional, si no se especifica, el sistema buscará por defecto en la carpeta ./logs.

Algunos ejemplos de uso con los patrones predefinidos:

```
python grep.py errores
python grep.py timeouts ./mis_logs
python grep.py ips
```

También se puede ingresar una expresión regular personalizada directamente:

```
python grep.py "ERROR.*timeout" ./logs
```

Los patrones predefinidos disponibles son: errores, advertencias, ips, timeouts, seguridad y correos.

Si se desea probar el sistema con el benchmark incluido, primero se deben generar los archivos de prueba ejecutando:

​```
python generar_logs.py
​```

Esto creará la carpeta `./logs_benchmark` con 800 archivos listos para usar.


# Pruebas de concurrencia

Para medir el impacto real de la concurrencia, se comparó el tiempo de ejecución entre una versión secuencial (1 trabajador) y la implementación concurrente usando 800 archivos de logs con 300 líneas cada uno (240,000 líneas en total), generados con el script `generar_logs.py`. Para cambiar entre ambas versiones basta con modificar el valor de `NUM_TRABAJADORES` entre `1` y `4` en el archivo `grep.py`.

Los resultados obtenidos al buscar errores fueron los siguientes:

Concurrente: 

<img width="446" height="121" alt="image" src="https://github.com/user-attachments/assets/63dc36d0-cba6-4719-82f9-8cbc5fb602d4" />


Secuencial:

<img width="443" height="129" alt="image" src="https://github.com/user-attachments/assets/53aee789-b7e8-4315-9dd0-1f0f8fd5ee9d" />


Con este volumen de datos la diferencia de tiempo es notoria.


# Análisis

## Complejidad temporal

En una implementación secuencial, si:

* `n` es la cantidad de archivos,
* `m` es el tamaño promedio de cada archivo,

la complejidad temporal es:

O(n · m)

ya que se recorre cada archivo y cada una de sus líneas de forma lineal.

En la implementación concurrente con `p` workers, la complejidad ideal se aproxima a:

O((n · m) / p)

porque la carga se divide entre los threads que trabajan en paralelo.

La fórmula O((n·m)/p) asume condiciones perfectas que en la práctica no se cumplen. En Python, el GIL (Global Interpreter Lock) hace que solo un hilo pueda ejecutarse a la vez en operaciones de CPU. Por esta razón, el beneficio real de usar threading proviene de las operaciones de lectura de archivos, momento en el que el GIL se libera (Python Software Foundation, 2024, sección GIL and performance considerations).

Por todo esto, el speedup real está limitado por la fracción secuencial del programa. Según la Ley de Amdahl, el speedup máximo alcanzable con `p` trabajadores es (GeeksForGeeks, 2026, párr. 5):

​```
S = 1 / ((1 - P ) + (P / N))
​```

Donde `P` es la fracción del programa que puede ejecutarse en paralelo y `N` el número de trabajadores. Esto significa que si una parte del programa es obligatoriamente secuencial, como el escaneo del directorio o la escritura de resultados, el speedup nunca alcanza exactamente `N`, y su incremento se vuelve marginal conforme se agregan más trabajadores (GeeksForGeeks, 2026, párr. 8).


# Comparación con otro paradigma

Una alternativa al enfoque concurrente sería una solución secuencial, donde el sistema procesaría un archivo a la vez, línea por línea.

La diferencia entre ambos enfoques no siempre es visible, ya que con pocos archivos pequeños el tiempo de administración de hilos puede ser mayor que el tiempo de procesamiento real. Para observar una diferencia significativa se recomienda trabajar con al menos 500 archivos de más de 100 líneas cada uno, ya que a partir de ese volumen el tiempo de lectura acumulado supera el costo de crear y sincronizar los hilos. En el benchmark incluido se utilizaron 800 archivos de 300 líneas cada uno, con lo que la diferencia de tiempos entre ambas versiones resultó claramente perceptible.

La solución concurrente aprovecha mejor los recursos del sistema y reduce el tiempo de ejecución de manera considerable, el costo es una mayor complejidad en la implementación, ya que hay que manejar la sincronización entre hilos y evitar condiciones de carrera.


# Conclusiones

Este proyecto permitió comprobar en la práctica cómo la programación concurrente puede reducir el tiempo de procesamiento en una herramienta de búsqueda masiva en archivos de texto. Como se analizó en la sección de complejidad, la mejora teórica O((n·m)/p) no siempre se alcanza en la realidad, debido a las limitaciones del GIL de Python, el costo de sincronización entre hilos y la distribución desigual de trabajo, factores que hacen que el speedup real sea menor al esperado según la Ley de Amdahl. Aun así, la combinación de trabajadores concurrentes, una cola compartida y expresiones regulares dinámicas produjo una herramienta funcional y flexible para el análisis de logs.


# Referencias

GeeksForGeeks. (2026, abril 8). Amdahl's law in Computer Organization. https://www.geeksforgeeks.org/computer-organization-architecture/computer-organization-amdahls-law-and-its-proof/

GNU Grep Manual. https://www.gnu.org/software/grep/manual/grep.html

GNU Grep Programs. https://www.gnu.org/software/grep/doc/html_node/grep-Programs.html

GNU Grep Regular Expressions. https://www.gnu.org/software/grep/manual/html_node/Regular-Expressions.html

Python Software Foundation. (2024). *threading — Thread-based parallelism*. https://docs.python.org/3/library/threading.html

Silberschatz, A., & Galvin, P., & Gagne, G. (2018). *Operating System Concepts* (10th ed.). Wiley. https://os.ecci.ucr.ac.cr/slides/Abraham-Silberschatz-Operating-System-Concepts-10th-2018.pdf
