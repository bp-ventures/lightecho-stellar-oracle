#!/usr/bin/env bash
if [ -z "$1" ]; then
  echo "Error: at least one argument must be provided"
  exit 1
fi
cleanup() {
  echo "Received termination signal. Exiting..."
  exit 0
}
trap cleanup INT TERM
MYNAME=$(basename "$1")
echo "Starting $MYNAME. Press Ctrl+C or use 'kill' to exit."

while true; do
    "$@"
    #sleep_for=$((RANDOM % 30 + 1))
    sleep_for=30
    date
    echo "$MYNAME has exited, restarting it after $sleep_for seconds"
    sleep $sleep_for || break
done
