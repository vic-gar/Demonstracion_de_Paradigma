# Demostración de Paradigma - Motor de búsqueda para archivos de logs

# Descripción

## Contexto del problema

Hoy en día, las aplicaciones, servidores y servicios de red generan grandes cantidades de archivos de logs que registran información relevante sobre su comportamiento: errores del sistema, conexiones de red, advertencias, fallos de autenticación, monitoreo de servicios y posibles incidentes de seguridad.

El problema surge cuando hay que analizar manualmente todos esos archivos. Cuando existen cientos o miles de logs, la búsqueda se vuelve lenta, tediosa y poco práctica, siendo una situación bastante común en áreas como la administración de servidores, el monitoreo de infraestructura, la ciberseguridad y el análisis forense digital.

A partir de esta necesidad, decidí desarrollar una herramienta capaz de procesar múltiples archivos de forma eficiente, aprovechando la concurrencia y las expresiones regulares.


# Objetivo del proyecto

El objetivo principal de este proyecto fue desarrollar un motor concurrente de búsqueda basado en expresiones regulares (Regex), inspirado en herramientas como `grep`. El sistema debe ser capaz de recorrer múltiples archivos, procesarlos de manera concurrente, detectar patrones dinámicamente y reducir el tiempo de búsqueda en comparación con una implementación secuencial tradicional.

Con esto se busca demostrar cómo la programación concurrente puede aplicarse para optimizar tareas de procesamiento masivo de texto, distribuyendo la carga de trabajo entre varios workers que operan en paralelo.


# Inspiración del proyecto

Este proyecto tomó como referencia la herramienta clásica de Unix/Linux llamada `grep`, ampliamente utilizada para buscar patrones dentro de archivos de texto mediante expresiones regulares.

La documentación oficial de GNU Grep la describe así:

> "`grep` searches the named input files for lines containing a match to the given patterns."

La idea fue tomar ese concepto base y extenderlo con soporte de concurrencia, permitiendo procesar múltiples archivos de forma simultánea. A diferencia del `grep` tradicional, que generalmente opera de forma secuencial, esta propuesta incorpora una arquitectura basada en el patrón Producer–Consumer, además de métricas y benchmarking para evaluar el desempeño del sistema.


# Paradigmas utilizados

El paradigma principal de este proyecto es la programación concurrente. La solución utiliza múltiples threads que trabajan al mismo tiempo para procesar diferentes archivos de logs. Para coordinar el acceso a los recursos compartidos se emplean colas de tareas y mecanismos de sincronización mediante locks, lo que evita condiciones de carrera y posibles corrupción de datos, gracias a esto, el sistema puede aprovechar mejor los recursos del equipo y reducir el tiempo total de procesamiento cuando se trabaja con muchos archivos.

Como paradigma secundario se utilizaron expresiones regulares y scripting para realizar búsquedas dinámicas de patrones textuales, con Regex, el sistema puede detectar coincidencias complejas dentro de los logs, permitiendo al usuario ingresar tanto texto simple como expresiones regulares avanzadas, y también cuenta con patrones predefinidos para los casos de búsqueda más comunes.


# Modelos

## Arquitectura general

La arquitectura implementada sigue el patrón Producer–Consumer. En este modelo, un componente productor recorre los directorios y agrega los archivos encontrados a una cola compartida de tareas, luego, múltiples workers actúan como consumidores: toman archivos de esa cola y los procesan de forma concurrente.

En esta arquitectura, el escáner de archivos es el productor, y los workers son los consumidores, cada worker obtiene un archivo de la cola, aplica la expresión regular y almacena los resultados encontrados.

Para evitar conflictos cuando varios threads modifican al mismo tiempo las estadísticas o la lista de resultados, el sistema utiliza `threading.Lock()` como mecanismo de sincronización.


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

# Pruebas de concurrencia

Para medir el impacto real de la concurrencia, se comparó el tiempo de ejecución entre una versión secuencial y la implementación concurrente usando cientos de archivos de logs duplicados.

Los resultados fueron los siguientes al buscar los errores en los logs:

Concurrente: 

<img width="446" height="121" alt="image" src="https://github.com/user-attachments/assets/63dc36d0-cba6-4719-82f9-8cbc5fb602d4" />


Secuencial:

<img width="443" height="129" alt="image" src="https://github.com/user-attachments/assets/53aee789-b7e8-4315-9dd0-1f0f8fd5ee9d" />


La diferencia no es muy notable, debido a que el volumen de archivos y datos no es tanta, pero aún así se puede observar que la versión concurrente (con 4 threads) fue más rápida que la secuencial (1 thread), lo que confirma que distribuir la carga entre múltiples workers tiene un impacto significativo en el rendimiento.


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


# Comparación con otro paradigma

Una alternativa al enfoque concurrente sería una solución imperativa y secuencial, donde el sistema procesaría un archivo a la vez, línea por línea.

La ventaja de esa aproximación es que es más sencilla de entender e implementar, sin embargo, no escala bien cuando el volumen de datos crece, ya que el tiempo de procesamiento aumenta de forma directamente proporcional.

La solución concurrente, en cambio, aprovecha mejor los recursos del sistema y reduce el tiempo de ejecución de manera considerable, el costo es una mayor complejidad en la implementación, ya que hay que manejar la sincronización entre threads y evitar condiciones de carrera.


# Conclusiones

Este proyecto permitió demostrar de forma práctica cómo la programación concurrente puede mejorar el rendimiento de una herramienta de procesamiento masivo de texto.

La combinación de workers concurrentes, colas compartidas y expresiones regulares dinámicas resultó en una herramienta funcional, eficiente y flexible para el análisis de logs, además, la arquitectura implementada refleja conceptos reales utilizados en herramientas de monitoreo, observabilidad y seguridad, lo que acerca el proyecto a aplicaciones de uso profesional.


# Referencias

GNU Grep Manual
https://www.gnu.org/software/grep/manual/grep.html

GNU Grep Programs
https://www.gnu.org/software/grep/doc/html_node/grep-Programs.html

GNU Grep Regular Expressions
https://www.gnu.org/software/grep/manual/html_node/Regular-Expressions.html

Python Threading Documentation
https://docs.python.org/3/library/threading.html
