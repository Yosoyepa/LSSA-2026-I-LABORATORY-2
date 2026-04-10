# European Rail Traffic Management System (ERTMS) - SoS Architecture (Grupo 1C)

## 📖 Descripción del Proyecto
Este proyecto implementa la arquitectura del sistema ferroviario ERTMS utilizando un paradigma de **Ingeniería Dirigida por Modelos (MDE)**. En lugar de programar los microservicios uno a uno, hemos definido un Lenguaje Específico de Dominio (DSL) en `arch.tx`, modelado la topología de red y componentes en `model.arch`, y construido un motor de transformación en Python que **autogenera** la infraestructura completa del clúster.

---

## ⚙️ La Fábrica MDE y el Directorio `skeleton/`

**⚠️ CRÍTICO: Entendiendo el flujo de la arquitectura**

El directorio raíz de este proyecto contiene el **Motor Generador**, no el código fuente final de la aplicación. 

Al ejecutar el motor, este lee nuestro diseño en `model.arch` y **crea automáticamente el directorio `skeleton/`**. 
**De la carpeta `skeleton/` es de donde salen TODOS los servicios, APIs, bases de datos y scripts físicos.** Es el clúster ERTMS materializado y listo para ser orquestado por Docker.

*Nota de buenas prácticas:* No debes modificar los archivos dentro de `skeleton/` manualmente, ya que cualquier cambio se sobrescribirá si vuelves a correr el generador MDE. Los cambios estructurales deben hacerse en `model.arch` y las reglas lógicas en `transformations.py`.

---

## 🚀 Instrucciones de Uso

### 1. Autogeneración de la Arquitectura
Primero, debemos compilar y ejecutar el Motor MDE para que procese nuestro modelo y genere el directorio `skeleton/`:

```bash
# 1. Compilar la imagen Docker del Motor MDE
docker build -t lssa-lab2 .

# 2. Ejecutar el motor mapeando tu directorio actual
# Al finalizar este comando, aparecerá la carpeta 'skeleton/' mágicamente
docker run --rm -v "$(pwd):/app" lssa-lab2
```

### 2. Despliegue del Clúster ERTMS
Una vez generada la carpeta `skeleton/`, procedemos a desplegar el Sistema de Sistemas (SoS):

```bash
# 1. Entrar al directorio autogenerado
cd skeleton

# 2. Levantar la infraestructura (T1 a T5) en segundo plano
docker-compose up --build -d

# 3. Comprobar que todos los contenedores estén sanos (Up)
docker ps -a
```

### 3. Uso de Scripts de Orquestación (.sh)
Si has creado o se te han provisto scripts de Bash (`.sh`) para automatizar el despliegue, pruebas de estrés o poblado de bases de datos, es indispensable otorgarles **permisos de ejecución** antes de invocarlos en sistemas basados en Unix (Linux/macOS).

```bash
# Otorgar permisos de ejecución al script
chmod +x nombre_del_script.sh

# Ejecutar el script
./nombre_del_script.sh
```

---

## 📊 Auditorías y Trazabilidad

En un Sistema de Sistemas crítico (como el control de trenes), las auditorías son el pilar de la seguridad y la resiliencia. En este proyecto, la auditoría se aborda en dos frentes:

1. **Auditoría Técnica y Operacional (En Tiempo de Ejecución):**
   - Todos los flujos de auditoría del sistema en vivo operan dentro de los servicios desplegados en `skeleton/`.
   - **Event Store DB & Data Lake (`dl`):** Los microservicios de la capa lógica (T3) y las bases de datos (T4) están configurados para ingerir sus registros históricos hacia el Data Lake y el Event Store. Aquí es donde residen los registros inmutables de los movimientos de los trenes, los comandos del MAS (Movement Authority) y los logs del sistema, esenciales para la auditoría de seguridad post-incidente.

2. **Auditoría Arquitectónica y de Diseño (En Tiempo de Diseño):**
   - **`report.pdf`**: Documento exigido que actúa como auditoría analítica sobre las Decisiones de Arquitectura (ADRs) tomadas y los workarounds aplicados para superar las limitantes del generador MDE.
   - **`sos_evolution_rationale.md`**: Bitácora técnica del Grupo 1C que audita las modificaciones realizadas a la topología base, justificando la inclusión de balanceadores de carga, buses de eventos y pasarelas GSM-R para evolucionar el proyecto hacia un verdadero SoS descentralizado.

---

## 🛑 Detener el Sistema

Para apagar el clúster ERTMS, detener los simuladores de trenes y destruir los contenedores y redes virtuales, ejecuta el siguiente comando desde dentro de la carpeta `skeleton/`:

```bash
docker-compose down -v
```
*(El flag `-v` asegura que se limpien los volúmenes de las bases de datos).*