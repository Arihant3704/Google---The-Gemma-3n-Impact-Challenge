#!/bin/bash

echo "--- Installing Offboard (Local Machine) Dependencies ---"

# Install Ollama
echo "Checking for Ollama installation..."
if ! command -v ollama &> /dev/null
then
    echo "Ollama not found. Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "Ollama is already installed."
fi

# Pull the llava:7b model
echo "Pulling llava:7b model..."
ollama pull llava:7b

# Navigate to the offboard directory
cd offboard

# Install Python dependencies
echo "Installing Python packages from requirements.txt..."
pip3 install -r requirements.txt

echo "Offboard installation complete. You can now run the web server:"
echo "python3 main.py"
