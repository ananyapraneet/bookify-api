#!/bin/bash

set -Eeuo pipefail

APP_DIR="/opt/bookify"
COMPOSE_FILE="${APP_DIR}/docker-compose.production.yml"
ENV_FILE="${APP_DIR}/.env.production"

ECR_REPOSITORY="${ECR_REPOSITORY:?ECR_REPOSITORY is required}"
IMAGE_TAG="${IMAGE_TAG:?IMAGE_TAG is required}"
AWS_REGION="${AWS_REGION:?AWS_REGION is required}"

cd "$APP_DIR"

echo "Deploying ${ECR_REPOSITORY}:${IMAGE_TAG}"

echo "Loading production configuration from SSM..."

SSM_PATH="/bookify/production"

get_ssm_parameter() {
    local parameter_name="$1"

    aws ssm get-parameter \
        --region "$AWS_REGION" \
        --name "${SSM_PATH}/${parameter_name}" \
        --with-decryption \
        --query "Parameter.Value" \
        --output text
}

umask 077

cat > "$ENV_FILE" <<EOF
POSTGRES_USER=$(get_ssm_parameter "POSTGRES_USER")
POSTGRES_PASSWORD=$(get_ssm_parameter "POSTGRES_PASSWORD")
POSTGRES_DB=$(get_ssm_parameter "POSTGRES_DB")
POSTGRES_HOST=$(get_ssm_parameter "POSTGRES_HOST")
POSTGRES_PORT=$(get_ssm_parameter "POSTGRES_PORT")
JWT_SECRET_KEY=$(get_ssm_parameter "JWT_SECRET_KEY")
JWT_ALGORITHM=$(get_ssm_parameter "JWT_ALGORITHM")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=$(get_ssm_parameter "JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
ECR_REPOSITORY=${ECR_REPOSITORY}
IMAGE_TAG=${IMAGE_TAG}
EOF

trap 'rm -f "$ENV_FILE"' EXIT

echo "Production configuration loaded."

echo "Logging into ECR..."

aws ecr get-login-password --region "$AWS_REGION" \
    | docker login \
        --username AWS \
        --password-stdin \
        "$(echo "$ECR_REPOSITORY" | cut -d/ -f1)"

echo "Pulling application image..."

docker compose \
    --env-file "$ENV_FILE" \
    -f "$COMPOSE_FILE" \
    pull api celery_worker

echo "Starting infrastructure..."

docker compose \
    --env-file "$ENV_FILE" \
    -f "$COMPOSE_FILE" \
    up -d postgres redis

echo "Waiting for PostgreSQL and Redis..."

sleep 10

echo "Running database migrations..."

docker compose \
    --env-file "$ENV_FILE" \
    -f "$COMPOSE_FILE" \
    run --rm api alembic upgrade head

echo "Starting application..."

docker compose \
    --env-file "$ENV_FILE" \
    -f "$COMPOSE_FILE" \
    up -d api celery_worker nginx

echo "Waiting for API health check..."

for attempt in {1..30}; do
    if curl --fail --silent http://127.0.0.1/health >/dev/null; then
        echo "Deployment successful."

        docker compose \
            --env-file "$ENV_FILE" \
            -f "$COMPOSE_FILE" \
            ps

        exit 0
    fi

    echo "Health check attempt ${attempt}/30 failed."
    sleep 5
done

echo "Deployment failed health verification."

docker compose \
    --env-file "$ENV_FILE" \
    -f "$COMPOSE_FILE" \
    logs --tail=100 api

exit 1
