# Деплой svitlobot (как kasa.helgamade.com — Git на сервер idesig02)

## Один источник правды (Git)

- **Локально** — ты коммитишь в одну ветку (master).
- **Один репозиторий** — тот же код в GitHub (origin) и на сервере (production = bare-репо).
- **Сервер** — после каждого `git push production master` hook делает: `git fetch` + `git reset --hard` + `git clean -fd` (кроме .env, venv, логов). Рабочая папка на сервере = **точная копия репо**, старых/лишних файлов не остаётся.

## Схема

- **origin** — GitHub (бэкап): `https://github.com/Helgamade/svitlobot.git`
- **production** — сервер: `idesig02@idesig02.ftp.tools:deploy-svitlobot.git`
- На сервере: bare-репо `~/deploy-svitlobot.git`, рабочая папка `/home/idesig02/helgamade.com/svitlobot`

## Локально (один раз)

```powershell
cd e:\svitlobot.helgamade.com

# Remotes (как в kasa)
git remote add origin https://github.com/Helgamade/svitlobot.git
git remote add production idesig02@idesig02.ftp.tools:deploy-svitlobot.git

# Репо на GitHub создай вручную: https://github.com/new → Helgamade/svitlobot
git push -u origin master
```

## Один раз на сервере

По SSH на `idesig02@idesig02.ftp.tools`:

```bash
# 1. Bare-репозиторий для деплоя
mkdir -p ~/deploy-svitlobot.git
cd ~/deploy-svitlobot.git
git init --bare

# 2. Рабочая директория (первый раз — пустая, заполнится при первом push)
mkdir -p /home/idesig02/helgamade.com/svitlobot
```

Локально загрузи hook и запушь код:

```powershell
.\deploy-setup.bat
git push production master
```

После первого push на сервере в `~/helgamade.com/svitlobot` появится код. Дальше:

```bash
cd /home/idesig02/helgamade.com/svitlobot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env   # TUYA_*, TELEGRAM_*, TELEGRAM_CHANNEL_ID
```

Создай systemd-юнит (путь и пользователь как в kasa):

```bash
sudo nano /etc/systemd/system/svitlobot.service
```

```ini
[Unit]
Description=Tuya status -> Telegram
After=network.target

[Service]
Type=simple
User=idesig02
WorkingDirectory=/home/idesig02/helgamade.com/svitlobot
Environment=PATH=/home/idesig02/helgamade.com/svitlobot/venv/bin
ExecStart=/home/idesig02/helgamade.com/svitlobot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable svitlobot
sudo systemctl start svitlobot
```

## Обычный деплой

Как в kasa: коммит → push в origin → push в production.

```powershell
.\deploy-git.bat
```

Или вручную:

```powershell
git add .
git commit -m "Описание"
git push origin master
git push production master
```

После `git push production master` hook на сервере обновит код в `/home/idesig02/helgamade.com/svitlobot` и перезапустит `systemctl restart svitlobot` (если юнит есть).

## Проверка remotes

```powershell
git remote -v
```

Ожидается:

```
origin      https://github.com/Helgamade/svitlobot.git (fetch)
origin      https://github.com/Helgamade/svitlobot.git (push)
production  idesig02@idesig02.ftp.tools:deploy-svitlobot.git (fetch)
production  idesig02@idesig02.ftp.tools:deploy-svitlobot.git (push)
```

## Если hook не срабатывает

Исправь перевод строк (LF) и права:

```bash
ssh idesig02@idesig02.ftp.tools "sed -i 's/\r$//' ~/deploy-svitlobot.git/hooks/post-receive && chmod +x ~/deploy-svitlobot.git/hooks/post-receive"
```

Или снова запусти `.\deploy-setup.bat`.
