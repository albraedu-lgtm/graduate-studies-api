@echo off
chcp 65001 >nul
echo.
echo ==========================================
echo   نشر منصة الدراسات العليا على Render
echo   Deploy Graduate Studies to Render
echo ==========================================
echo.

cd /d "b:\New folder (2)\openedx-platform-master\graduate_api"

echo [1/5] Adding all files...
git add -A

echo [2/5] Committing changes...
git commit -m "Production Fix: Move DB operations to startup, fix static storage" --allow-empty

echo [3/5] Setting remote...
git remote set-url origin https://github.com/albraedu-lgtm/graduate-studies-api.git 2>nul

echo [4/5] Setting branch...
git branch -M main

echo [5/5] Pushing to GitHub (triggers auto-deploy on Render)...
git push -u origin main --force

echo.
echo ==========================================
echo   Backend pushed! Render will auto-deploy.
echo   Wait 3-5 minutes, then check:
echo   https://graduate-api.onrender.com/health/
echo ==========================================
echo.
pause
