#!/bin/bash
set -e


# Allow for Docker installation to complete
until pg_isready -h localhost -U $POSTGRES_USER; do
  echo "Waiting for database to be ready..."
  sleep 2
done

# Run initialization script
# Conditional logic to not overwrite table inside init.sql
psql -h localhost -U $POSTGRES_USER -d $POSTGRES_DB -f /usr/local/bin/init.sql

# Return to original entrypoint
exec "$@"
