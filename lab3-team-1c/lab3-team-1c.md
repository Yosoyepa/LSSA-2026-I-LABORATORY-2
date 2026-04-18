# LSSA 2026-I: Laboratory 3 - Quality Attributes Modeling
**Team:** 1c
**System:** ERTMS System of Systems (SoS) architecture

## 1. Grammatical Constraints vs. Free-form Strings

En el Model-Driven Engineering (MDE), la validación temprana de la arquitectura es crítica para garantizar que los modelos de diseño representen un sistema estable antes de que se invierta tiempo de cómputo en la generación de código. 

Al haber extendido la gramática `arch.tx` del laboratorio utilizando vocabularios cerrados (enumeraciones estrictas como `AvailabilityLevel: 'critical' | 'high' | 'standard';`) en lugar de variables primitivas (`STRING`), obligamos a que el *parser* funcione como un primer nivel de análisis estático y un linter arquitectónico. 

Si definiéramos la propiedad de *Performance* como texto libre y un arquitecto ingresara accidentalmente `performance: interative` en lugar de `interactive`, o algo ambiguo como `performance: fast`, el generador (`transformations.py`) no lo reportaría nativamente. El mapeo incorrecto se propagaría en silencio hasta el entorno de ejecución, resultando en un Docker Compose sin los límites correctos (`cpu_limit`), lo que comprometería todo el clúster bajo carga. Con las uniones transitivas forzadas en `textX`, la mera instanciación del AST abortará la ejecución en caso de divergencia tipográfica o semántica.

## 2. Mapping Documentation: Tactics in ERTMS

Las decisiones arquitectónicas (SLA limits y tácticas del T3/T5) definidas en `model.arch` están respaldadas por mitigaciones de escenarios de calidad:

- **Restricción de Seguridad en driver_interface -> api_gateway (`encrypted: true, rate_limit: 50`)**: 
  - *Táctica (Security - Prevent/Detect):* Authentication/Authorization.
  - *Justificación:* La interfaz del tren expone control físico (ej. frenos). Se forza `encrypted` a nivel de componente para evitar interceptación en texto plano (MITM spoofing) y un `rate_limit` estricto para mitigar ataques DDoS desde la cabina (flood attempts).
  
- **Disponibilidad y Límite de Memoria en api_gateway (`critical`, `replicas: 2`, `mem_limit: "256m"`)**: 
  - *Táctica (Availability - Fault Tolerance):* Active Redundancy.
  - *Justificación:* Al ser el único Reverse Proxy expuesto hacia la capa T1, su caída inhabilitaría la comunicación de toda la infraestructura. Se mapea a redundancia activa (dos réplicas) y límite de memoria para evitar que un OOM de este contendor colapse el Host Docker.
  
- **Tiempos de Ejecución Acotados mas -> onboard_unit (`timeout_ms: 200`)**: 
  - *Táctica (Performance - Resource Management):* Bound Execution Times.
  - *Justificación:* Las señales de "Movement Authority" que envía el *mas* para actualizar al tren rigen el freno de emergencia. Un retraso superior a 200 milisegundos podría provocar una colisión física entre convoyes.

---
**Evidencia de Verificación MDE:**
El comando `docker run --rm -v "$(pwd):/app" lssa-lab3` procesó el modelo exitosamente, imprimiendo el **Quality Annotation Summary** con cero errores de instanciación del DSL para las 31 topologías y 30 conectores modelados.
