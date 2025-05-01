#!/bin/bash

echo "Beginning installation..."

# Check if Python 3.12 is installed
if ! command -v python3.12 &> /dev/null; then
    echo "Python 3.12 is not installed. Please install Python 3.12 and add it to your PATH."
    exit 1
fi

# Check Python version if python3 exists
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version | awk '{print $2}')
    if [[ $(echo "$python_version" | cut -d. -f1,2) != "3.12" ]]; then
        echo "Python 3.12 is required but found $python_version. Please install Python 3.12."
        exit 1
    fi
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Source the shell configuration to update PATH
    source ~/.bashrc 2>/dev/null || source ~/.bash_profile 2>/dev/null || source ~/.zshrc 2>/dev/null

    # Check if the installation was successful
    if ! command -v uv &> /dev/null; then
        echo "Failed to install uv. Please install it manually."
        exit 1
    else
        echo "uv installed successfully."
    fi
fi

# Check if the virtual environment already exists
echo "Setting up the environment..."
if [ -d "venv" ] || [ -d ".venv" ]; then
    echo "Virtual environment already exists. Skipping creation."
    if [ -d "venv" ]; then
        venv_type="venv"
    else
        venv_type=".venv"
    fi
else
    # Create a virtual environment if it doesn't exist.
    echo "Creating a virtual environment..."
    read -p "Creating virtual environment. Choices 'uv' or 'pip': " venv_choice
    if [ "$venv_choice" == "pip" ]; then
        python3 -m venv venv
        venv_type="venv"
    else
        uv venv --python 3.12
        venv_type=".venv"
    fi
fi

# Install the virtual environment if requested.
if [ ! -d ".venv" ] && [ ! -d "venv" ]; then

    read -p "Virtual environment not found. Would you like to create one? (y/n) " create_venv

    if [ "$create_venv" == "y" ] || [ "$create_venv" == "Y" ]; then

        read -p "Creating virtual environment. Choices 'uv' or 'pip': " venv_choice

        if [[ $venv_choice == "uv" ]]; then
            echo "Creating virtual environment using uv..."
            uv venv --python 3.12
        else # default to pip
            echo "Creating virtual environment using pip..."
            python3 -m venv venv
        fi

        # Check if install.sh exists before executing it
        if [ -f "install.sh" ]; then
            bash "install.sh"
            echo "Virtual environment created successfully."
        else
            echo "Warning: install.sh not found. Please create the virtual environment manually."
        fi
    else
        echo "Skipping virtual environment creation..."
    fi
fi

# Activate the virtual environment
echo "Activating the virtual environment..."
if ! source "$venv_type/bin/activate"; then
    echo "Error: Failed to activate the virtual environment."
    exit 1
fi
echo "Virtual environment activated."

# Install required packages from requirements.txt
if [[ -f "requirements.txt" ]]; then
    echo "Installing required packages..."
    if [ "$venv_type" == "venv" ]; then
        pip install -r requirements.txt
    else
        uv add -r requirements.txt
    fi
else
    echo "requirements.txt not found. Skipping package installation."
fi

echo "Installation complete!"
