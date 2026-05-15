@echo off
chcp 65001 >nul
echo ==========================================
echo   رفع الواجهة الخلفية إلى GitHub
echo   Push Backend to GitHub
echo ==========================================
echo.

cd /d "b:\New folder (2)\openedx-platform-master\graduate_api"

echo [1/5] Adding files...
git add .

echo [2/5] Committing...
git commit -m "Production Ready - Dual Approval System"

echo [3/5] Setting remote...
git remote set-url origin https://github.com/albraedu-lgtm/graduate_studies_api.git

echo [4/5] Setting branch...
git branch -M main

echo [5/5] Pushing to GitHub...
git push -u origin main

echo.
echo ==========================================
echo   Done! Check your GitHub repository.
echo ==========================================
pause
