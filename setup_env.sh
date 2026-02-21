#!/bin/bash

echo "--- Starting Environment Setup ---"

# Create Virtual Environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
echo "Installing Python dependencies... this may take a minute."
pip install -r requirements.txt

# Create necessary folders
mkdir -p debug_output models src

echo "--- Environment Setup Complete ---"
echo "To activate the environment, run: source venv/bin/activate"