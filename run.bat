@echo off
:: ══════════════════════════════════════════════════════════════════════════════
:: NutriAI — IBM Granite Nutrition Agent
:: Launcher + Installer Script
:: ══════════════════════════════════════════════════════════════════════════════
:: Double-click this file OR run from Command Prompt / PowerShell.
:: It will:
::   1. Check & install Python (via winget if missing)
::   2. Check & install Git (via winget if missing)
::   3. Create a Python virtual environment
::   4. Install all dependencies from requirements.txt
::   5. Set up .env configuration file
::   6. Launch the Flask application
:: ══════════════════════════════════════════════════════════════════════════════

title NutriAI — IBM Granite Nutrition Agent

echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║   🥗  NutriAI — IBM Granite Nutrition Agent             ║
echo  ║   Powered by IBM Granite LLM  ^|  Flask  ^|  Python      ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.

:: ── Step 1: Check Python ──────────────────────────────────────────────────────
echo [1/6] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  Python not found. Attempting to install via winget...
    winget install --id Python.Python.3.11 --source winget --silent --accept-package-agreements --accept-source-agreements
    if %errorlevel% neq 0 (
        echo.
        echo  ┌──────────────────────────────────────────────────────────┐
        echo  │  Python could not be installed automatically.            │
        echo  │  Please install manually:                                │
        echo  │    https://www.python.org/downloads/                     │
        echo  │  Check "Add Python to PATH" during setup, then re-run   │
        echo  │  this script.                                            │
        echo  └──────────────────────────────────────────────────────────┘
        pause
        exit /b 1
    )
    :: Refresh PATH
    call RefreshEnv.cmd >nul 2>&1
    set "PATH=%PATH%;%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts"
)
python --version
echo.

:: ── Step 2: Check Git ─────────────────────────────────────────────────────────
echo [2/6] Checking Git...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  Git not found. Attempting to install via winget...
    winget install --id Git.Git --source winget --silent --accept-package-agreements --accept-source-agreements
    if %errorlevel% neq 0 (
        echo  WARNING: Git could not be installed automatically.
        echo  To deploy to GitHub later, install from: https://git-scm.com
        echo  Continuing with app launch...
    ) else (
        set "PATH=%PATH%;C:\Program Files\Git\cmd"
        echo  Git installed successfully.
    )
) else (
    git --version
)
echo.

:: ── Step 3: Create virtual environment ───────────────────────────────────────
echo [3/6] Setting up virtual environment...
if not exist "venv" (
    python -m venv venv
    echo  Virtual environment created.
) else (
    echo  Virtual environment already exists.
)
echo.

:: ── Step 4: Install dependencies ─────────────────────────────────────────────
echo [4/6] Installing Python dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo  Retrying with --no-cache-dir...
    pip install -r requirements.txt --no-cache-dir
)
echo  All dependencies installed.
echo.

:: ── Step 5: Configure .env ───────────────────────────────────────────────────
echo [5/6] Configuring environment...
if not exist ".env" (
    copy .env.example .env >nul
    echo  Created .env from template.
    echo.
    echo  ┌──────────────────────────────────────────────────────────┐
    echo  │  OPTIONAL: Add IBM watsonx.ai credentials to .env        │
    echo  │                                                          │
    echo  │  Without credentials the app runs in DEMO MODE           │
    echo  │  (all features work using the built-in knowledge base).  │
    echo  │                                                          │
    echo  │  For LIVE IBM Granite mode:                              │
    echo  │    Edit .env and set IBM_API_KEY + IBM_PROJECT_ID        │
    echo  │    Get credentials: https://cloud.ibm.com                │
    echo  └──────────────────────────────────────────────────────────┘
    echo.
) else (
    echo  .env already configured.
)

:: Create plans directory
if not exist "plans" mkdir plans
echo.

:: ── Step 6: Launch app ────────────────────────────────────────────────────────
echo [6/6] Launching NutriAI...
echo.
echo  ══════════════════════════════════════════════════════════════
echo   🚀 App running at: http://localhost:5000
echo   Press Ctrl+C to stop the server
echo  ══════════════════════════════════════════════════════════════
echo.

:: Open browser after 3 seconds
start /b cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:5000"

python app.py

:: ── On exit ───────────────────────────────────────────────────────────────────
echo.
echo  Server stopped. Thank you for using NutriAI!
echo.
pause
