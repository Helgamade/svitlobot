@echo off
chcp 65001 >nul
REM Deploy Setup для svitlobot.helgamade.com
REM Устанавливает post-receive hook на production сервер

echo ===============================================================
echo DEPLOY SETUP для svitlobot.helgamade.com
echo ===============================================================
echo.

echo [1/2] Uploading post-receive hook to production...
scp .git-hooks\post-receive idesig02@idesig02.ftp.tools:~/deploy-svitlobot.git/hooks/post-receive
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to upload hook. Create bare repo on server first:
    echo   ssh idesig02@idesig02.ftp.tools "mkdir -p ~/deploy-svitlobot.git && cd ~/deploy-svitlobot.git && git init --bare"
    pause
    exit /b 1
)
echo OK: Hook uploaded

echo.
echo [2/2] Setting execute permissions and fixing line endings...
ssh idesig02@idesig02.ftp.tools "sed -i 's/\r$//' ~/deploy-svitlobot.git/hooks/post-receive && chmod +x ~/deploy-svitlobot.git/hooks/post-receive"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to set permissions
    pause
    exit /b 1
)
echo OK: Done

echo.
echo SETUP COMPLETE. Deploy: git push production master
pause
