#!/bin/sh
set -e

python -m app.migrations.run_migrations

if [ "$SEED_ON_START" = "true" ]; then
    python -m app.seed
fi

exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
