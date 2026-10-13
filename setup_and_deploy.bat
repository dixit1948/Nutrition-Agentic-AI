@echo off
:: ══════════════════════════════════════════════════════════════════════════════
:: setup_and_deploy.bat
:: Full setup + GitHub deployment script for NutriAI
:: ══════════════════════════════════════════════════════════════════════════════
:: This script:
::   1. Installs Python (if missing) via winget
::   2. Installs Git (if missing) via winget
::   3. Creates venv + installs pip dependencies
::   4. Sets up .env
::   5. Initializes git repo and pushes to GitHub
::   6. Launches the application
::
:: USAGE:
::   Double-click this file, or run:
::   setup_and_deploy.bat YOUR_GITHUB_TOKEN
::
::   Replace YOUR_GITHUB_TOKEN with a Personal Access Token from:
::   https://github.com/settings/tokens/new  (scope: repo)
:: ══════════════════════════════════════════════════════════════════════════════

setlocal EnableDelayedExpansion

title NutriAI — Full Setup & Deploy

set "GITHUB_REPO=https://github.com/dixit1948/Nutrition-Agentic-AI.git"
set "GITHUB_TOKEN=%~1"

echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║   🥗  NutriAI — Full Setup + GitHub Deploy              ║
echo  ║   IBM Granite Nutrition Agent                           ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.

:: ── Step 1: Python ────────────────────────────────────────────────────────────
echo [1/7] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  Installing Python 3.11 via winget...
    winget install -e --id Python.Python.3.11 --accept-package-agreements --accept-source-agreements
    set "PATH=%PATH%;%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts"
    python --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo  ERROR: Python install failed. Download from https://www.python.org/downloads/
        pause & exit /b 1
    )
)
python --version
echo.

:: ── Step 2: Git ───────────────────────────────────────────────────────────────
echo [2/7] Checking Git...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  Installing Git via winget...
    winget install -e --id Git.Git --accept-package-agreements --accept-source-agreements
    set "PATH=%PATH%;C:\Program Files\Git\cmd"
    git --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo  WARNING: Git not available. Skipping GitHub push.
        goto :SETUP_VENV
    )
)
git --version
echo.

:: ── Step 3: Virtual environment ───────────────────────────────────────────────
:SETUP_VENV
echo [3/7] Setting up virtual environment...
if not exist "venv" (
    python -m venv venv
    echo  venv created.
) else (
    echo  venv exists.
)
call venv\Scripts\activate.bat
echo.

:: ── Step 4: Install dependencies ─────────────────────────────────────────────
echo [4/7] Installing dependencies...
python -m pip install --upgrade pip -q
pip install -r requirements.txt -q
if %errorlevel% neq 0 (
    pip install -r requirements.txt --no-cache-dir
)
echo  Dependencies installed.
echo.

:: ── Step 5: Configure .env ───────────────────────────────────────────────────
echo [5/7] Configuring .env...
if not exist ".env" (
    copy .env.example .env >nul
    echo  .env created from template. Edit it to add IBM credentials (optional).
) else (
    echo  .env already exists.
)
if not exist "plans" mkdir plans
echo.

:: ── Step 6: GitHub Deployment ────────────────────────────────────────────────
echo [6/7] Deploying to GitHub...

:: Check if token was provided
if "%GITHUB_TOKEN%"=="" (
    echo  No GitHub token provided.
    echo  To deploy to GitHub, run:
    echo    setup_and_deploy.bat ghp_YOUR_TOKEN_HERE
    echo.
    echo  Or use the PowerShell script:
    echo    PowerShell -ExecutionPolicy Bypass -File deploy_to_github.ps1 -Token "ghp_YOUR_TOKEN"
    echo.
    echo  Get a token at: https://github.com/settings/tokens/new
    goto :LAUNCH
)

:: Try git deployment
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  Git not available. Using PowerShell API deploy...
    PowerShell -ExecutionPolicy Bypass -File deploy_to_github.ps1 -Token "%GITHUB_TOKEN%"
    goto :LAUNCH
)

:: Git-based push
if not exist ".git" (
    git init
    git remote add origin https://%GITHUB_TOKEN%@github.com/dixit1948/Nutrition-Agentic-AI.git
)

git config user.email "nutriai@deploy.local"
git config user.name "NutriAI Deploy"

:: Create .gitkeep for plans directory
if not exist "plans\.gitkeep" echo.> plans\.gitkeep

git add -A
git commit -m "Deploy NutriAI — IBM Granite Nutrition Agent"

:: Try push
git push -u origin main 2>nul
if %errorlevel% neq 0 (
    git branch -M main
    git push -u origin main
)

if %errorlevel% equ 0 (
    echo.
    echo  ✅ Successfully pushed to GitHub!
    echo  View at: https://github.com/dixit1948/Nutrition-Agentic-AI
) else (
    echo  Push failed. Try running deploy_to_github.ps1 manually.
)
echo.

:: ── Step 7: Launch ───────────────────────────────────────────────────────────
:LAUNCH
echo [7/7] Launching NutriAI...
echo.
echo  ══════════════════════════════════════════════════════════════
echo   🚀  http://localhost:5000
echo  ══════════════════════════════════════════════════════════════
echo.

start /b cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:5000"
python app.py

echo.
echo  NutriAI stopped. Thank you!
pause
