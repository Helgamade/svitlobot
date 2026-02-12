# Displayboard по HTTP (для Arduino без SSL)

**Китайські аналоги Arduino UNO R4 WiFi** часто не мають вбудованих CA-сертифікатів і не підтримують SSL/TLS як оригінал. З оригіналом працює HTTPS (kasa.helgamade.com), з клоном — тільки **HTTP на порту 8080**.

Якщо Arduino не може встановити HTTPS (`client.connect(server, 443)` → FAILED), використовуй **HTTP** на порту 8080.

## 1. Запуск HTTP-сервера

При деплої (`git push production master`) хук автоматично перезапускає **displayboard_http** (скрипт `deploy/start-displayboard-http-if-needed.sh`). Ручний запуск, якщо потрібно:

```bash
cd /home/idesig02/helgamade.com/svitlobot
./deploy/start-displayboard-http-if-needed.sh
# або напряму:
./venv/bin/python displayboard_http.py
```

Порт за замовчуванням: **8080**. Змінна середовища `DISPLAYBOARD_HTTP_PORT` — якщо потрібен інший порт. Відкрий порт 8080 на фаєрволі/панелі, якщо Arduino з іншої мережі звертається до сервера по IP.

У `.env` мають бути `TUYA_DEVICE_ID` та MySQL (MYSQL_*), щоб поверталось актуальне значення; інакше завжди `{"value":0}`.

Якщо сервер за фаєрволом, відкрий порт 8080 для локальної мережі або запускай displayboard_http на Raspberry Pi / ПК у тій же мережі, що й Arduino.

## 2. Arduino: HTTP замість HTTPS

- Використовуй **WiFiClient** (не WiFiSSLClient).
- Порт **80** для звичайного сайту не підійде (редирект на HTTPS). Порт **8080** — для displayboard_http.

Приклад змін:

```cpp
#include <WiFiS3.h>
#include <WiFiClient.h>   // звичайний клієнт, без SSL

const char* server = "192.168.0.XXX";  // IP машини, де запущено displayboard_http
const int   port   = 8080;
const char* path   = "/api/displayboard/current";

WiFiClient client;  // не WiFiSSLClient

// Далі той самий GET: client.connect(server, port), client.print("GET " path " HTTP/1.1\r\nHost: " server "\r\nConnection: close\r\n\r\n"); ...
```

Якщо displayboard_http крутиться на тому ж хості, що й svitlobot.helgamade.com, а порт 8080 відкритий — можна вказати IP хоста та port 8080.

## 3. Перевірка нульового IP (компіляція)

Щоб уникнути помилки порівняння `WiFi.localIP() == (uint32_t)0`, перевіряй нульовий IP по байтах:

```cpp
bool isZeroIP(IPAddress ip) {
  return (ip[0] == 0 && ip[1] == 0 && ip[2] == 0 && ip[3] == 0);
}

// У setup після WiFi.status() == WL_CONNECTED:
while (isZeroIP(WiFi.localIP()) && (attempts < 30)) {
  delay(500);
  Serial.print("_");
  attempts++;
}

// У loop перед запитом:
if (isZeroIP(WiFi.localIP())) { delay(500); return; }
```
