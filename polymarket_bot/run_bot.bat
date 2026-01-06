@echo off
REM Set UTF-8 encoding
chcp 65001 >nul

REM Change to the correct directory
cd /d "%~dp0"

REM Run the main bot
echo [BOT] Starting Polymarket Arbitrage Bot...
echo [BOT] Directory: %CD%
echo.

python main.py

REM Keep window open on error
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Bot crashed with code %errorlevel%
    pause
)
