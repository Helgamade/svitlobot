# Деплой на сервер через Git

## Локально (один раз)

```bash
cd e:\svitlobot.helgamade.com
git init
git add .
git commit -m "Initial: Tuya status -> Telegram"
git remote add origin <URL_РЕПОЗИТОРИЯ>   # GitHub, GitLab или свой сервер
git push -u origin main
```

Если ветка по умолчанию у тебя `master`: `git push -u origin master`.

## На сервере (Linux)

### 1. Клонировать и настроить

```bash
git clone <URL_РЕПОЗИТОРИЯ> svitlobot
cd svitlobot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env   # вписать TUYA_*, TELEGRAM_*, TUYA_DEVICE_ID и т.д.
```

### 2. Запуск вручную (проверка)

```bash
source venv/bin/activate
python main.py
```

### 3. Постоянный запуск (systemd)

Создать юнит (подставь свой путь и пользователя):

```bash
sudo nano /etc/systemd/system/svitlobot.service
```

Содержимое:

```ini
[Unit]
Description=Tuya status -> Telegram
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/home/www-data/svitlobot
Environment=PATH=/home/www-data/svitlobot/venv/bin
ExecStart=/home/www-data/svitlobot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Включить и запустить:

```bash
sudo systemctl daemon-reload
sudo systemctl enable svitlobot
sudo systemctl start svitlobot
sudo systemctl status svitlobot
```

Логи: `journalctl -u svitlobot -f`

### Альтернатива: screen/tmux

```bash
screen -S svitlobot
source venv/bin/activate
python main.py
# Ctrl+A, D — отключиться; screen -r svitlobot — вернуться
```

## Обновление на сервере

```bash
cd svitlobot
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart svitlobot   # если используешь systemd
```
