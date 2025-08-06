#!/bin/bash

echo "--- Installing Onboard (QCar) Dependencies ---"

# Navigate to the onboard directory
cd onboard

# Install Python dependencies
echo "Installing Python packages from requirements.txt..."
pip3 install -r requirements.txt

echo "Onboard installation complete. You can now run the QCar agent:"
echo "python3 main.py"
echo "Or run the demonstration mode:"
echo "python3 main.py --demonstrate"
