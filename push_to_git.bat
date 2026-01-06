@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo [GIT] Polymarket Bot - Pushing to Repository
echo.

REM Configure git if needed
git config user.name "Polymarket Bot Developer" 2>nul
git config user.email "bot@polymarket.local" 2>nul

REM Add all changes
echo [GIT] Adding files...
git add -A

REM Check if there are changes to commit
git diff-index --quiet --cached HEAD
if %errorlevel% neq 0 (
    REM Commit changes
    echo [GIT] Committing changes...
    git commit -m "Polymarket Arbitrage Bot - Complete implementation with all features"
    
    REM Push to remote
    echo [GIT] Pushing to remote...
    git push origin main 2>nul
    
    if %errorlevel% eq 0 (
        echo.
        echo [OK] Successfully pushed to Git!
        echo.
    ) else (
        echo.
        echo [WARNING] Could not push - might need authentication
        echo Check: git push origin main
        echo.
    )
) else (
    echo [INFO] No changes to commit - repository is up to date
)

echo [GIT] Done!
pause
