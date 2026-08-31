#!/bin/bash

set -Eeuo pipefail

APP_DIR="/opt/bookify"
COMPOSE_FILE="${APP_DIR}/docker-compose.production.yml"

ECR_REPOSITORY="${ECR_REPOSITORY:?ECR_REPOSITORY is required}"
IMAGE_TAG="${IMAGE_TAG:?IMAGE_TAG is required}"
AWS_REGION="${AWS_REGION:?AWS_REGION is required}"

cd "$APP_DIR"

echo "Deploying ${ECR_REPOSITORY}:${IMAGE_TAG}"

echo "Logging into ECR..."
aws ecr get-login-password --region "$AWS_REGION" \
  | docker login \
      --username AWS \
      --password-stdin \
      "$(echo "$ECR_REPOSITORY" | cut -d/ -f1)"

echo "Pulling application image..."
IMAGE_TAG="$IMAGE_TAG" \
ECR_REPOSITORY="$ECR_REPOSITORY" \
docker compose -f "$COMPOSE_FILE" pull api celery_worker

echo "Starting infrastructure..."
docker compose -f "$COMPOSE_FILE" up -d postgres redis

echo "Waiting for PostgreSQL and Redis..."
sleep 10

echo "Running database migrations..."
IMAGE_TAG="$IMAGE_TAG" \
ECR_REPOSITORY="$ECR_REPOSITORY" \
docker compose -f "$COMPOSE_FILE" run --rm api alembic upgrade head

echo "Starting application..."
IMAGE_TAG="$IMAGE_TAG" \
ECR_REPOSITORY="$ECR_REPOSITORY" \
docker compose -f "$COMPOSE_FILE" up -d api celery_worker

echo "Waiting for API health check..."

for attempt in {1..30}; do
  if curl --fail --silent http://127.0.0.1:8000/health >/dev/null; then
    echo "Deployment successful."
    docker compose -f "$COMPOSE_FILE" ps
    exit 0
  fi

  echo "Health check attempt ${attempt}/30 failed."
  sleep 5
done

echo "Deployment failed health verification."

docker compose -f "$COMPOSE_FILE" logs --tail=100 api

exit 1
