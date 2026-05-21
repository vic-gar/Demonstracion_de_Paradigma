# Demonstración de Paradigma — Grep Concurrente con Regex

# Descripción

## Contexto del problema

Actualmente se generan enormes cantidades de archivos de logs que almacenan información relevante sobre el comportamiento de aplicaciones, servidores y servicios de red, lo cuales contienen eventos importantes como errores del sistema, conexiones de red, advertencias, fallos de autenticación, monitoreo de servicios y posibles incidentes de seguridad.

El análisis manual de estos archivos representa un problema importante debido al volumen de información que se produce constantemente. Cuando existen cientos o incluso miles de archivos de logs, el proceso de búsqueda se vuelve lento, ineficiente y poco escalable, siendo una problemática bastante común en áreas como la administración de servidores, la observabilidad de sistemas, el monitoreo de infraestructura, la ciberseguridad y el análisis forense digital.

Con base en esta necesidad, se propone el desarrollo de una herramienta capaz de procesar múltiples archivos de manera eficiente utilizando concurrencia y expresiones regulares.


# Objetivo del proyecto

El objetivo principal de este proyecto consiste en desarrollar un motor concurrente de búsqueda basado en expresiones regulares (Regex), inspirado en herramientas de análisis textual como `grep`. El sistema debe ser capaz de recorrer múltiples archivos, procesarlos concurrentemente, detectar patrones dinámicamente y reducir significativamente el tiempo de búsqueda en comparación con una implementación secuencial tradicional.

La solución busca demostrar cómo la programación concurrente puede aplicarse para optimizar tareas de procesamiento masivo de texto, aprovechando múltiples workers para distribuir la carga de trabajo entre varios hilos de ejecución.


# Inspiración del proyecto

El proyecto está inspirado en la herramienta clásica de Unix/Linux llamada `grep`, que es utilizada para buscar patrones dentro de archivos de texto utilizando expresiones regulares.

La documentación oficial de GNU Grep define esta herramienta de la siguiente manera:

> "`grep` searches the named input files for lines containing a match to the given patterns."

La idea principal del proyecto consiste en extender el concepto tradicional de `grep` agregando soporte para concurrencia mediante múltiples workers, permitiendo así procesar múltiples archivos simultáneamente y mejorar el rendimiento general del sistema.

A diferencia de `grep`, cuya implementación clásica suele ejecutarse de forma secuencial, esta propuesta incorpora una arquitectura concurrente basada en el patrón Producer–Consumer, así como métricas y benchmarking para evaluar el desempeño del sistema.


# Paradigmas utilizados

El paradigma principal utilizado en este proyecto es la programación concurrente. La solución emplea múltiples threads que trabajan simultáneamente para procesar diferentes archivos de logs, para coordinar el acceso a los recursos compartidos se utilizan colas de tareas y mecanismos de sincronización mediante locks, evitando condiciones de carrera y corrupción de datos. La concurrencia permite aprovechar mejor los recursos del sistema y reducir considerablemente el tiempo total de procesamiento cuando se trabaja con grandes volúmenes de archivos.

Como paradigma secundario se utilizan expresiones regulares y scripting para realizar búsquedas dinámicas de patrones textuales. Gracias a Regex, el sistema puede detectar automáticamente coincidencias complejas dentro de los logs, permitiendo al usuario ingresar tanto patrones simples como expresiones regulares avanzadas, soporta patrones predefinidos para búsquedas comunes, además de permitir que el usuario ingrese expresiones regulares personalizadas desde la línea de comandos.


# Modelos

## Arquitectura general

La arquitectura implementada sigue el patrón Producer–Consumer. En este modelo, un componente productor se encarga de recorrer directorios y agregar archivos a una cola compartida de tareas. Posteriormente, múltiples workers consumidores toman archivos desde dicha cola y los procesan concurrentemente.

El flujo general del sistema puede representarse de la siguiente manera:

```txt
Usuario ingresa patrón
           |
           v
+----------------------+
| Pattern Resolver     |
+----------------------+
           |
           v
+----------------------+
| File Scanner         |
+----------------------+
           |
           v
+----------------------+
| Shared Queue         |
+----------------------+
      /     |     \
     /      |      \
    v       v       v
Worker1  Worker2  Worker3
    \       |       /
     \      |      /
           v
+----------------------+
| Result Manager       |
+----------------------+
           |
           v
     Resultados Finales
```

En esta arquitectura, el escáner de archivos actúa como productor, mientras que los workers funcionan como consumidores concurrentes, cada worker obtiene archivos desde la cola, aplica la expresión regular correspondiente y almacena los resultados encontrados.

Para garantizar la integridad de los datos compartidos, el sistema utiliza mecanismos de sincronización mediante `threading.Lock()`, evitando conflictos cuando múltiples threads modifican simultáneamente las estadísticas o la lista de resultados.


# Implementación

El proyecto fue desarrollado utilizando Python debido a su facilidad para el manejo de concurrencia, su soporte nativo para expresiones regulares y la rapidez de desarrollo que ofrece para prototipado y procesamiento textual.

Las librerías principales utilizadas fueron:

```python
os
re
sys
time
queue
threading
```

La librería `threading` se utiliza para crear múltiples workers concurrentes, mientras que `queue` permite implementar una cola compartida segura entre threads. Por otro lado, la librería `re` proporciona soporte para expresiones regulares dinámicas.

El sistema permite realizar búsquedas utilizando:

* texto simple,
* patrones predefinidos,
* expresiones regulares avanzadas.

Algunos ejemplos de patrones predefinidos incluyen la detección de errores, warnings, direcciones IP y eventos de seguridad.


# Pruebas

Para validar el funcionamiento del sistema se realizaron diferentes pruebas funcionales y de rendimiento.

En las pruebas funcionales se verificó que las expresiones regulares fueran capaces de detectar correctamente patrones dentro de los logs. Por ejemplo, al utilizar la expresión `ERROR.*` sobre una línea como `ERROR Database timeout`, el sistema identificó correctamente la coincidencia esperada.

También se realizaron pruebas utilizando expresiones regulares para detectar direcciones IP mediante el patrón:

```regex
\d+\.\d+\.\d+\.\d+
```

obteniendo como resultado la detección correcta de direcciones dentro de los archivos procesados.

Adicionalmente, se probaron casos negativos para verificar que líneas que no cumplían con el patrón no generaran coincidencias incorrectas.


# Pruebas de concurrencia

Para evaluar el impacto de la concurrencia, se comparó el tiempo de ejecución entre una versión secuencial y la implementación concurrente utilizando cientos de archivos de logs duplicados.

Los resultados obtenidos mostraron una mejora considerable en el rendimiento:

| Modo        | Tiempo |
| ----------- | ------ |
| Secuencial  | 12.7 s |
| Concurrente | 3.1 s  |

Estos resultados demuestran cómo la distribución de carga entre múltiples workers reduce significativamente el tiempo total de procesamiento.


# Análisis

## Complejidad temporal

En una implementación secuencial tradicional, si:

* `n` representa la cantidad de archivos,
* `m` representa el tamaño promedio de cada archivo,

la complejidad temporal puede expresarse como:

O(n · m)

Esto se debe a que el sistema debe recorrer secuencialmente todos los archivos y todas las líneas contenidas en ellos.

En la implementación concurrente, utilizando `p` workers, la complejidad ideal se aproxima a:

O((n · m) / p)

ya que la carga de trabajo se distribuye entre múltiples threads que procesan archivos simultáneamente.


# Comparación con otro paradigma

Una alternativa al paradigma concurrente sería implementar una solución completamente imperativa y secuencial. En este enfoque, el sistema procesaría un archivo a la vez y recorrería cada línea de forma lineal.

La principal ventaja de esta aproximación es su simplicidad conceptual y de implementación. Sin embargo, presenta problemas importantes de escalabilidad y rendimiento cuando el volumen de datos aumenta considerablemente.

Por otro lado, la solución concurrente aprovecha mejor los recursos del sistema, distribuyendo la carga entre múltiples workers y reduciendo considerablemente el tiempo total de ejecución. No obstante, esto introduce desafíos adicionales relacionados con sincronización, coordinación de threads y posibles condiciones de carrera.


# Conclusiones

El proyecto demuestra cómo la programación concurrente puede utilizarse para mejorar significativamente el rendimiento de sistemas de procesamiento masivo de texto.

El uso combinado de workers concurrentes, colas compartidas y expresiones regulares dinámicas permitió desarrollar una herramienta eficiente, flexible y escalable para análisis de logs y búsqueda de patrones textuales.

Además, la arquitectura implementada refleja conceptos utilizados en herramientas reales de monitoreo, observabilidad y análisis de seguridad, acercando el proyecto a aplicaciones prácticas utilizadas en la industria.


# Referencias

GNU Grep Manual
https://www.gnu.org/software/grep/manual/grep.html

GNU Grep Programs
https://www.gnu.org/software/grep/doc/html_node/grep-Programs.html

GNU Grep Regular Expressions
https://www.gnu.org/software/grep/manual/html_node/Regular-Expressions.html

Python Threading Documentation
https://docs.python.org/3/library/threadi
