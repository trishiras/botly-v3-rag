#!/usr/bin/env bash

# Wait for Ollama to be ready
HOST="localhost"
PORT=11434
TIMEOUT=60

wait_for_it() {
    echo "Waiting up to $TIMEOUT seconds for Ollama at $HOST:$PORT..."
    START_TIME=$(date +%s)
    while :; do
        (echo > /dev/tcp/$HOST/$PORT) >/dev/null 2>&1 && break
        CURRENT_TIME=$(date +%s)
        ELAPSED_TIME=$((CURRENT_TIME - START_TIME))
        if [[ $ELAPSED_TIME -ge $TIMEOUT ]]; then
            echo "Timeout reached: Ollama did not start in $TIMEOUT seconds."
            exit 1
        fi
        sleep 1
    done
    echo "Ollama is up!"
}

wait_for_it