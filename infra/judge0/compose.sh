#!/bin/sh
# Use only on an isolated test VM. Never print the resolved compose config:
# it contains secrets. This wrapper cannot make privileged containers safe.
set -eu
cd "$(dirname "$0")"
python3 manage_config.py check
# Compose environment takes precedence over --env-file. Avoid accidentally
# connecting the DB/Redis to credentials different from the service config.
unset POSTGRES_DB POSTGRES_USER POSTGRES_PASSWORD REDIS_PASSWORD
exec docker compose --env-file judge0.conf -f docker-compose.yml "$@"
