# Justificación de Modificaciones al Modelo y Evolución a Sistema de Sistemas (SoS)

Este documento detalla el razonamiento detrás de las modificaciones propuestas para el archivo `model.arch` y proporciona sugerencias arquitectónicas para consolidar el sistema ERTMS como un verdadero Sistema de Sistemas (SoS), basándose en el análisis del Grupo 1C y los principios arquitectónicos de la Unidad 2.

## 1. Metodología de Modificación del Modelo (`model.arch`)

Las modificaciones propuestas se derivan directamente de la sección "1.4. Componentes incompletos o faltantes" y las tablas de conectores del documento `lab1_team_1c.pdf`. Para garantizar que el modelo siga siendo compatible con el motor MDE provisto (y su gramática `arch.tx`), se han aplicado ciertas convenciones y mapeos de tipos.

### Adición de Componentes Faltantes

Se incorporaron los componentes identificados por el equipo, mapeándolos a los `ComponentType` permitidos en la gramática actual:

*   **T1 - Presentation:**
    *   `mobile_app` (Tipo: `web_interface`): Para acceso de pasajeros.
    *   `maintenance_console` (Tipo: `operator_ui`): Para equipos de mantenimiento.
*   **T2 - Communication:**
    *   *Nota sobre la gramática:* Actualmente, `arch.tx` solo permite el tipo `api_gateway` en el Tier 2. Para no romper el parser, los nuevos componentes se mapean a este tipo, aunque semánticamente cumplan roles distintos.
    *   `load_balancer` (Tipo: `api_gateway`): Distribuye tráfico.
    *   `message_broker` (Tipo: `api_gateway`): Para eventos asíncronos.
    *   `gsm_r_gateway` (Tipo: `api_gateway`): Puente hacia la red de radio ferroviaria.
*   **T3 - Logic:**
    *   Se respeta el **ADR-001** forzando el sufijo `_ms`.
    *   `alerts_ms` (Tipo: `microservice`): Gestión de alarmas.
    *   `scheduling_ms` (Tipo: `microservice`): Planificación de rutas y turnos.
*   **T4 - Data:**
    *   Se respeta el **ADR-001** forzando el sufijo `_db`.
    *   `tickets_db` (Tipo: `database`): Para persistencia del `tickets_ms`.
    *   `alerts_db` (Tipo: `database`): Para persistencia del `alerts_ms`.
    *   `event_store_db` (Tipo: `database`): Registro inmutable para el MAS.
*   **T5 - Physical:**
    *   `onboard_radio_unit` (Tipo: `onboard_unit`): Equipo GSM-R embarcado.

### Integración de Nuevos Conectores

Se añadieron los flujos de información documentados en el análisis estructural:
*   **Cross-tier:** Conexiones desde las nuevas UIs (T1) hacia el Load Balancer (T2), ruteo hacia los nuevos microservicios (T3), dependencias hacia sus respectivas bases de datos (T4) y la comunicación vía el Gateway GSM-R (T2 <-> T5).
*   **Intra-tier:** Coordinación entre microservicios (ej. `passengers_ms -> tickets_ms`, `trains_ms -> routes_ms`) y la ingesta masiva de todas las bases de datos (T4) hacia el Data Lake (`dl`).

---

## 2. Sugerencias para consolidar el ERTMS como Sistema de Sistemas (SoS)

Según el documento `[LSSA_2026i] - U2 - The ERTMS.pdf`, un SoS se caracteriza por la independencia operativa y de gestión de sus sistemas constituyentes, colaborando para un comportamiento emergente. Para que la arquitectura autogenerada por nuestro MDE refleje fielmente un SoS, se sugieren las siguientes evoluciones:

### A. Gobernanza Distribuida y Desacoplamiento (T2 y T3)
*   **Situación actual:** El sistema depende de un `api_gateway` altamente centralizado (con ruteo estático hardcodeado según ADR-001). Esto asemeja el sistema a un monolito distribuido más que a un SoS.
*   **Sugerencia (SoS):** Transicionar hacia una **coreografía basada en eventos** utilizando el `message_broker` recién añadido. Los microservicios nacionales o de dominio (rutas, trenes, autoridades) deben publicar eventos de estado en lugar de depender de un orquestador central o peticiones sincrónicas directas. Esto garantiza la *Independencia Evolutiva*.

### B. Interoperabilidad Semántica (T3 y T4)
*   **Situación actual:** Los conectores `dependency` acoplan fuertemente cada microservicio a su base de datos, y los conectores `data_flow` asumen que todos hablan el mismo "idioma".
*   **Sugerencia (SoS):** Implementar **Contratos de API Estandarizados (Shared Semantics)**. En un SoS real, el `trains_ms` de España debe poder operar con el `routes_ms` de Francia. Se debe diseñar un modelo de datos canónico para los mensajes que transitan por T2, abstraído de las implementaciones específicas de T4.

### C. Autonomía Operacional y Resiliencia (T3 y T5)
*   **Situación actual:** El documento 1C señala que el `api_gateway` y la conexión T3 <-> T5 son puntos críticos de falla (SPOF).
*   **Sugerencia (SoS):** Reforzar la **Autonomía de Supervivencia** del `onboard_unit` (T5). Si la red GSM-R (T2) o el MAS (T3) fallan, el tren debe seguir operando de forma segura (Fail-Safe) basándose en la información local de sensores y balizas, sin depender del control centralizado. El sistema autogenerado debe inyectar lógicas de "Fallback" en los scripts de Python del T5.

### D. Red y Despliegue Federado
*   **Situación actual:** El **ADR-003** fuerza a todos los contenedores a vivir en una red plana (flat bridge network) para que se descubran mediante DNS de Docker, sacrificando el aislamiento.
*   **Sugerencia (SoS):** Un verdadero SoS requiere fronteras de seguridad estrictas (Zero Trust). Se debe evolucionar el generador MDE (modificando `transformations.py`) para soportar múltiples redes Docker (ej. `presentation_net`, `logic_net`, `physical_net`) e inyectar configuraciones de proxy inverso o mTLS para que las comunicaciones inter-tier sean explícitamente autorizadas y cifradas.

---
**Conclusión:** La expansión del modelo `model.arch` con los componentes del Grupo 1C es el primer paso. El verdadero desafío MDE será modificar `transformations.py` para que el código generado para estos nuevos componentes asuma comportamientos asíncronos, autónomos y tolerantes a fallos, características definitorias de un System of Systems.