#!/bin/bash

# Start Ollama server in the background
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to be ready
/usr/src/app/scripts/wait-for-it.sh

# Pull the model
ollama pull qwen2.5:3b

# Wait for Ollama server to complete (if needed)
wait $OLLAMA_PID &

# Start Botly
streamlit run  /usr/src/app/botly_ui.py