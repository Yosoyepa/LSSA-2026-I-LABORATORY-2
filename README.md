# European Rail Traffic Management System (ERTMS) - (Grupo 1C)

## Instrucciones de Uso

### 1. Autogeneración de la Arquitectura
Primero, debemos compilar y ejecutar el Motor MDE para que procese nuestro modelo y genere el directorio `skeleton/`:

```bash
docker build -t lssa-lab2 .

docker run --rm -v "$(pwd):/app" lssa-lab2
```

### 2. Despliegue del Clúster ERTMS
Una vez generada la carpeta `skeleton/`, procedemos a desplegar el Sistema:

```bash
cd skeleton
docker-compose up --build -d
docker ps -a
```

### 3. Uso de Scripts de Orquestación (.sh)

```bash
# Otorgar permisos de ejecución al script
chmod +x nombre_del_script.sh

./nombre_del_script.sh
```

Ejecutar estos scripts en orden en la raíz del proyecto:

```
./run_cluster.sh
```

```
./test_cluster.sh
```

---

## Detener el Sistema

```bash
# Ejecutar en skeleton/
docker-compose down -v
```
