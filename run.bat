@echo off
TITLE Arduino Gas Controller - Windows Runner

REM --- Arduino Gas Controller Runner (Windows) ---

REM Check for Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. 
    echo Please install it from https://www.python.org/ or via Microsoft Store.
    echo Ensure "Add Python to PATH" is checked during installation.
    pause
    exit /b
)

REM Check if venv exists
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
)

REM Activate venv
echo [INFO] Activating virtual environment...
call venv\Scripts\activate

REM Update pip and install requirements
echo [INFO] Checking dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Run the application
echo ------------------------------------------------------------------
echo [INFO] Gas Controller starting on http://localhost:1080
echo [INFO] Close this window to stop the application.
echo ------------------------------------------------------------------
python app.py

pause
