#!/bin/bash

# 1. Levantar el clúster en segundo plano
echo "🚀 Levantando el clúster..."
docker compose up -d --build

# 2. Esperar a que los servicios estén listos (simple sleep o un loop de healthcheck)
echo "⏳ Esperando a que los servicios inicien..."
sleep 15 

# 3. Lanzar una petición de prueba al Frontend
echo "🧪 Probando endpoint principal..."
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8888/)

if [ "$response" == "200" ]; then
    echo "✅ Test Frontend: OK (200)"
else
    echo "❌ Test Frontend: FALLÓ (Status: $response)"
    docker compose logs
    docker compose down
    exit 1
fi

# 4. Lanzar una petición al endpoint de health de la API (ejemplo)
echo "🧪 Probando API Health..."
api_response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5001/api/v1/health)

if [ "$api_response" == "200" ]; then
    echo "✅ Test BMC Service: OK (200)"
else
    echo "❌ Test BMC Service: FALLÓ (Status: $api_response)"
    docker compose down
    exit 1
fi

# 5. Apagar el clúster
echo "🛑 Apagando el clúster..."
docker compose down

echo "🎉 Todos los tests del clúster pasaron correctamente."
exit 0