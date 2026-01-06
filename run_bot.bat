@echo off
REM Polymarket Arbitrage Bot - Windows Launcher
REM Professional entry point for the trading bot

setlocal enabledelayedexpansion
cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org
    pause
    exit /b 1
)

REM Run the bot
echo Starting Polymarket Arbitrage Bot...
echo.
python run_bot.py

pause
