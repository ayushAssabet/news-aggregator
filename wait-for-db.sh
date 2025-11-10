#!/bin/bash
set -e
host="$1"
shift
cmd="$@"

until pg_isready -h "$host" -p 5432 -U app > /dev/null 2> /dev/null; do
  >&2 echo "⏳ Waiting for Postgres ($host)..."
  sleep 2
done

>&2 echo "✅ Postgres is up — running command"
exec $cmd
