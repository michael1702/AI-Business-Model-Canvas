#!/bin/bash
export OPENAI_API_KEY="sk-dummy-key-for-testing"
export JWT_SECRET="test-secret"
set -e

echo "🚀 Start Container-Cluster..."
docker compose up -d --build

echo "⏳ Wait for initialization (15s)..."
sleep 15

echo "🧪 Test Frontend Availability..."
curl -f http://localhost:8888/ || exit 1

echo "🧪 Test API Health Check..."
curl -f http://localhost:5001/api/v1/health || exit 1

echo "✅ Cluster-Test successful!"
docker compose down