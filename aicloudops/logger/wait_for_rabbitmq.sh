#!/bin/sh

RABBITMQ_HOST="rabbitmq"
RABBITMQ_PORT=5672

echo "Waiting for RabbitMQ to become available..."
echo "${@}"

# Loop until rabbitmq is ready
until nc -z "$RABBITMQ_HOST" "$RABBITMQ_PORT"; do
  echo "RabbitMQ is unavailable - sleeping"
  sleep 5
done

echo "RabbitMQ is up - starting logger servce..."

# Execute the CMD statement in the Dockerfile
exec "${@}"
