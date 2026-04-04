#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "Building frontend..."
cd frontend && NEXT_PUBLIC_API_URL="" bun run build && cd ..

echo "Copying frontend build to backend/app/static..."
rm -rf backend/app/static && cp -r frontend/out backend/app/static

echo "Deploying to FastAPI Cloud..."
cd backend && uv run fastapi deploy
