# Добавить origin и запушить. Запуск: .\push.ps1 "https://github.com/USER/svitlobot.git"
param([Parameter(Mandatory=$true)] [string] $RepoUrl)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (git remote get-url origin 2>$null) {
    git remote set-url origin $RepoUrl
} else {
    git remote add origin $RepoUrl
}
git push -u origin master

Write-Host "Done. On server: git clone $RepoUrl && cd svitlobot && ... (see DEPLOY.md)"
