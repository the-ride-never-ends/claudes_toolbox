#!/bin/bash

# Check if the program has been opened via WSL command
source ~/.bashrc 2>/dev/null || source ~/.bash_profile 2>/dev/null || source ~/.zshrc 2>/dev/null

# Change to the directory where the script is located.
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Check if the script --in
# If it doesn't, run the install script.
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    bash "install_claudes_toolbox_server.sh"
fi

# Import .env variables
set -a 
source .env 
set +a

# Activate the virtual environment, then rn the Python script
if [ -d "venv" ]; then
    source venv/bin/activate && python app.py
elif [ -d ".venv" ]; then
    source .venv/bin/activate && uv run app.py
else
    exit 1
fi

# Deactivate the virtual environment
deactivate

exit 0