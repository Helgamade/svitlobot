@echo off
chcp 65001 >nul
REM Git Deploy для svitlobot.helgamade.com (как в kasa)

where git >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git not found!
    pause
    exit /b 1
)

echo GIT DEPLOY - svitlobot.helgamade.com
echo.

git status
echo.
set /p COMMIT_MESSAGE="Commit message (Enter = default): "
if "%COMMIT_MESSAGE%"=="" set COMMIT_MESSAGE="Deploy: %date% %time%"

git add .
git commit -m "%COMMIT_MESSAGE%"
if %ERRORLEVEL% NEQ 0 (
    echo Nothing to commit or commit failed.
    set /p PUSH_ONLY="Push anyway? (y/n): "
    if /i not "%PUSH_ONLY%"=="y" exit /b 1
)

echo.
echo Pushing to GitHub (origin)...
git push origin master
if %ERRORLEVEL% NEQ 0 git push origin main

echo.
echo Pushing to production server...
git push production master
if %ERRORLEVEL% NEQ 0 git push production main

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Push failed. Check remotes: git remote -v
    pause
    exit /b 1
)

echo.
echo DEPLOYMENT COMPLETE.
pause
