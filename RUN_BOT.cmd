@echo off
REM ============================================================
REM POLYMARKET ARBITRAGE BOT - RUN COMMANDS FOR CMD
REM ============================================================

REM Navigate to project directory
cd /d c:\Users\shh92\OneDrive\Documenti\BotPolymarket

REM Option 1: Run bot directly (simple)
python run_bot.py

REM Option 2: Run bot with virtual environment activation
REM .venv\Scripts\activate.bat && python run_bot.py

REM Option 3: Run bot with error logging to file
REM python run_bot.py > bot_output.log 2>&1

REM Option 4: Run bot and keep window open on exit
REM python run_bot.py
REM pause

REM Option 5: Run test WebSocket only
REM python test_ws.py
