#!/bin/bash
# Start the app on a fresh SQLite file and seed the three items the e2e script expects.
# Usage: run_app.sh <path-to-getting-started-app>
set -euo pipefail
APP_DIR=${1:?path to getting-started-app}
DB_DIR=$(mktemp -d)
PID_FILE=${PID_FILE:-/tmp/getting-started-app.pid}
[ -f "$PID_FILE" ] && kill "$(cat "$PID_FILE")" 2>/dev/null && sleep 1 || true
if curl -s -o /dev/null localhost:3000; then
  echo "port 3000 is already in use; stop that server first" >&2
  exit 1
fi
cd "$APP_DIR"
SQLITE_DB_LOCATION="$DB_DIR/todo.db" nohup node src/index.js > "$DB_DIR/app.log" 2>&1 < /dev/null &
echo $! > "$PID_FILE"
for _ in $(seq 20); do curl -s localhost:3000/items > /dev/null && break; sleep 0.5; done
for n in "Buy milk" "Renew passport before March" "Call the landlord about the leaking tap"; do
  curl -s -XPOST localhost:3000/items -H 'Content-Type: application/json' -d "{\"name\":\"$n\"}" -o /dev/null
done
echo "app pid $(cat "$PID_FILE"), log $DB_DIR/app.log"
