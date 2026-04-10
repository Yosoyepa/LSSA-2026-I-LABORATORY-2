#!/bin/bash
set -e

echo "=========================================="
echo "  ERTMS Cluster Orchestrator (LSSA Lab 2) "
echo "=========================================="

# Validar si el motor generó los archivos
if [ ! -d "skeleton" ] || [ ! -f "skeleton/docker-compose.yml" ]; then
    echo "❌ Error: La matriz 'skeleton/' no existe o no tiene Docker Compose."
    echo "Asegúrate de ejecutar el motor MDE primero:"
    echo "docker run --rm -v \"\$(pwd):/app\" lssa-lab2"
    exit 1
fi

COMMAND=${1:-start}

cd skeleton

case "$COMMAND" in
    start)
        echo "🚀 Levantando los 5 Tiers del clúster ERTMS (Presentation, Communication, Logic, Data, Physical)..."
        # Utilizamos docker compose (v2) como lo pide el entorno
        docker compose up --build -d
        echo ""
        echo "✅ Clúster iniciado correctamente."
        echo "> Tip: Ejecuta './run_cluster.sh status' para ver la salud de los contenedores."
        ;;
        
    stop)
        echo "🛑 Deteniendo y destruyendo el clúster completamente..."
        docker compose down -v
        echo "✅ Clúster apagado con éxito."
        ;;
        
    status)
        echo "📊 Estado de los Tiers:"
        docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep skeleton
        ;;
        
    logs)
        shift
        if [ -z "$1" ]; then
            echo "📝 Mostrando logs multicanal de todo el clúster... (Ctrl+C para salir)"
            docker compose logs -f --tail=20
        else
            echo "📝 Mostrando logs del servicio: $1 (Ctrl+C para salir)"
            docker compose logs -f --tail=50 "$1"
        fi
        ;;
        
    *)
        echo "Comando no reconocido: $COMMAND"
        echo "Uso: ./run_cluster.sh [start | stop | status | logs <servicio>]"
        echo "Por defecto, al no pasar parámetros, se ejecuta 'start'."
        exit 1
        ;;
esac

cd ..
