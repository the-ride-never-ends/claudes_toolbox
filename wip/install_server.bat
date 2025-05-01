@echo off
setlocal enabledelayedexpansion

echo Beginning installation...

:: Check if Python 3.12 is installed
python --version 2>nul | findstr "3.12" >nul
if %errorlevel% neq 0 (
    python3 --version 2>nul | findstr "3.12" >nul
    if %errorlevel% neq 0 (
        echo Python 3.12 is not installed. Please install Python 3.12 and add it to your PATH.
        exit /b 1
    )
)

:: Determine which Python command to use
set PYTHON_CMD=python
python --version 2>nul | findstr "3.12" >nul
if %errorlevel% neq 0 (
    set PYTHON_CMD=python3
)

:: Check if uv is installed
uv --version 2>nul
if %errorlevel% neq 0 (
    echo uv is not installed. Installing uv with pip...
    pip install uv
)

:: Check if the virtual environment already exists
echo Setting up the environment...
uv venv --python %PYTHON_CMD%

:: Activate the virtual environment
echo Activating the virtual environment...
call .venv\Scripts\activate.bat

if %errorlevel% neq 0 (
    echo Error: Failed to activate the virtual environment.
    exit /b 1
)

:: Install required packages from requirements.txt
uv add -r requirements.txt

echo Installation complete!

endlocal
