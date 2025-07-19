#!/usr/bin/env bash

# Stop existing containers if any
docker stop accounts_container social_service_container 2>/dev/null
docker rm accounts_container social_service_container 2>/dev/null

echo "🔧 Building accounts service..."
docker build -t accounts_service ./accounts

echo "🔧 Building social_service..."
docker build -t social_service ./social_service

echo "🚀 Running accounts service on port 8000..."
docker run -d \
  --name accounts_container \
  -p 8000:8000 \
  --env-file ./accounts/.env \
  accounts_service

echo "🚀 Running social_service on port 8001..."
docker run -d \
  --name social_service_container \
  -p 8001:8000 \
  --env-file ./social_service/.env \
  social_service

echo "✅ All services are up and running!"
