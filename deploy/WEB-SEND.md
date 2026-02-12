# Веб-форма отправки в канал (svitlobot.helgamade.com)

Сервис `web_send.py` — одна страница с полем ввода и кнопкой «Надіслати в Telegram». Для отправки нужно ввести текст и секрет (значение `WEB_SEND_SECRET` из `.env`).

## На сервере

1. В `.env` задать:
   ```
   WEB_SEND_SECRET=твій_секретний_пароль
   ```

2. Установить зависимости (если ещё не стоят Flask):
   ```bash
   cd /home/idesig02/helgamade.com/svitlobot
   ./venv/bin/pip install -r requirements.txt
   ```

3. Запустить приложение (один из вариантов).

   **Вариант A: gunicorn за локальным портом, веб-сервер проксирует на него**
   ```bash
   ./venv/bin/pip install gunicorn
   ./venv/bin/gunicorn -w 1 -b 127.0.0.1:5000 web_send:app
   ```
   В настройках виртуального хоста `svitlobot.helgamade.com` настроить проксирование `/` на `http://127.0.0.1:5000` (nginx: `proxy_pass`; Apache: `ProxyPass`).

   **Вариант B: встроенный сервер Flask (только для проверки)**
   ```bash
   ./venv/bin/python web_send.py
   ```
   По умолчанию слушает порт 5000. Для продакшена лучше gunicorn + прокси.

4. Чтобы процесс не падал после выхода из SSH: запускать через nohup, systemd или скрипт в cron (аналогично боту). Пример nohup:
   ```bash
   nohup ./venv/bin/gunicorn -w 1 -b 127.0.0.1:5000 web_send:app >> web_send.log 2>&1 &
   ```

## Доступ

Открыть в браузере: **https://svitlobot.helgamade.com/**  
Ввести текст, в поле «Секрет» — значение `WEB_SEND_SECRET`, нажать «Надіслати в Telegram». Сообщение уйдёт в тот же канал, что и бот.

Если `WEB_SEND_SECRET` не задан в `.env`, форма отображается, но отправка отключена (сообщение на странице).
