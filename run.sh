#!/bin/bash

# --- Arduino Gas Controller Runner (Linux/macOS) ---

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    echo "Please install it from https://www.python.org/ or your package manager (e.g., brew install python on macOS, sudo apt install python3 on Linux)."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip and install requirements
echo "Checking dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Linux-specific check: group membership for serial access
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if ! groups $USER | grep &>/dev/null '\(dialout\|uucp\)'; then
        echo "WARNING: You might not have permission to access serial ports (USB/Arduino)."
        echo "Please run: sudo usermod -a -G dialout $USER (and then log out and back in)."
    fi
fi

# Run the app
echo "Starting Gas Controller on http://localhost:1080..."
python app.py
