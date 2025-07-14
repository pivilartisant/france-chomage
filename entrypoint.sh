#!/bin/bash
set -e

echo "🚀 France Chômage Bot - Universal Entrypoint"

# Detect environment and delegate to appropriate script
if [ "$RAILWAY_ENVIRONMENT" ] || [ "$RAILWAY_PUBLIC_DOMAIN" ] || [ "$RAILWAY_PROJECT_ID" ] || [ "$FORCE_RAILWAY_ENTRYPOINT" ]; then
    echo "🚂 Railway environment detected - using Railway entrypoint"
    exec /railway-entrypoint.sh "$@"
elif [ "$DOCKER_ENV" ] || [ -f /.dockerenv ]; then
    echo "🐳 Docker environment detected - using Docker entrypoint"
    exec /docker-entrypoint.sh "$@"
else
    echo "🖥️ Local environment detected - starting directly"
    exec "$@"
fi
