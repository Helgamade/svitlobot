# Что нужно агенту, чтобы делать деплой на 100% сам

Тебе ничего делать не нужно для обычного деплоя — агент сам пушит в Git и на сервер. Ниже — что уже есть и что нужно один раз.

## Уже есть (ничего не настраивать)

- **SSH** с твоей машины на сервер `idesig02@idesig02.ftp.tools` — работает (иначе бы `git push production` не проходил).
- **Git remotes**: `origin` (GitHub), `production` (сервер).
- **Hook на сервере**: при `git push production master` код обновляется в `/home/idesig02/helgamade.com/svitlobot` и перезапускается сервис (если установлен).

Этого достаточно, чтобы агент делал деплой сам: говоришь «задеплой» / «выкати» — агент выполняет `deploy-setup.bat` (если менял хук), коммит, `git push origin master`, `git push production master`.

---

## Один раз на сервере (без этого бот не запустится)

Это не «каждый деплой», а разовая настройка окружения и сервиса. Агент не может подставить твои секреты в `.env` без доступа к ним.

**Вариант А — ты сам один раз по SSH:**

```bash
cd /home/idesig02/helgamade.com/svitlobot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env   # вписать TUYA_ACCESS_ID, TUYA_ACCESS_SECRET, TUYA_DEVICE_ID, TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID

sudo cp deploy/svitlobot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable svitlobot
sudo systemctl start svitlobot
```

**Вариант Б — чтобы агент создал .env на сервере:**  
Один раз дать агенту значения переменных (например, в чате: «подставь в .env на сервере: TUYA_ACCESS_ID=..., ...») — агент выполнит по SSH команды вида `echo "TUYA_ACCESS_ID=..." >> .env` и т.д. Секреты в чат писать не обязательно: можно сделать только venv + systemd, а `.env` заполнить самому.

---

## Итог

- **Деплой с гита (хуки, пуш на сервер)** — агент делает сам, тебе ничего делать не нужно.
- **Первый запуск бота на сервере** — один раз: venv, зависимости, `.env`, systemd (ты по SSH или один раз даёшь секреты агенту для создания `.env`).
