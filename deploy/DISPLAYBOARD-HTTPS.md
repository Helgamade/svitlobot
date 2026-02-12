# Displayboard по HTTPS — чому kasa працює, svitlobot ні

Один і той самий скетч Arduino (WiFiSSLClient) підключається до **kasa.helgamade.com:443** і не підключається до **svitlobot.helgamade.com:443**. Код однаковий, різниця тільки в тому, що віддає **сервер** по TLS: сертифікат, цепочка, версія TLS або шифри.

## Що порівняти на сервері

Обидва сайти на одному хості (idesig02). Потрібно зробити TLS для **svitlobot** таким же, як для **kasa**.

### 1. Порівняти сертифікати та цепочку (локально або по SSH)

```bash
# Kasa (працює з Arduino)
openssl s_client -connect kasa.helgamade.com:443 -servername kasa.helgamade.com </dev/null 2>/dev/null | openssl x509 -noout -issuer -subject -dates

# Svitlobot (не працює)
openssl s_client -connect svitlobot.helgamade.com:443 -servername svitlobot.helgamade.com </dev/null 2>/dev/null | openssl x509 -noout -issuer -subject -dates
```

Подивись: **issuer** (хто видав), **subject** (для кого). Якщо різні — у панелі хостингу для svitlobot треба виставити той самий сертифікат, що й для kasa (якщо є wildcard `*.helgamade.com` або multi-SAN з обома іменами).

### 2. Перевірити повну цепочку (скільки сертифікатів віддає сервер)

```bash
# Скільки сертифікатів у відповіді (має бути ≥ 2: сервер + проміжний)
echo | openssl s_client -connect kasa.helgamade.com:443 -servername kasa.helgamade.com -showcerts 2>/dev/null | grep -c "BEGIN CERTIFICATE"
echo | openssl s_client -connect svitlobot.helgamade.com:443 -servername svitlobot.helgamade.com -showcerts 2>/dev/null | grep -c "BEGIN CERTIFICATE"
```

Якщо для **kasa** виходить 2 (або більше), а для **svitlobot** — 1, то Arduino не може перевірити ланцюг (йому потрібен проміжний сертифікат). Рішення: у налаштуваннях SSL для **svitlobot.helgamade.com** вказати **повну цепочку** (certificate + intermediate), як для kasa.

### 3. Що змінити в панелі хостингу (idesig02)

- Відкрий налаштування SSL для **svitlobot.helgamade.com**.
- Якщо для kasa використовується один сертифікат на кілька доменів (наприклад kasa + svitlobot) — вистав для svitlobot **той самий** сертифікат, що й для kasa.
- Якщо сертифікат окремий (наприклад Let's Encrypt окремо для кожного домену) — переконайся, що в поле сертифіката вставлена **повна цепочка**: спочатку сертифікат сайту, потім проміжний(і) (наприклад R3 для Let's Encrypt). Без проміжного Arduino (Renesas WiFiS3) часто не приймає з’єднання.
- Збережи зміни і перезавантаж веб-сервер / перезапусти HTTPS (якщо панель це дозволяє).

### 4. Як взяти повну цепочку для Let's Encrypt

Якщо сертифікат Let's Encrypt:

- У панелі часто є опція типу «Install full chain» або окреме поле для «Chain» / «Intermediate».
- Або вручну: сертифікат домену + файл проміжного, наприклад `https://letsencrypt.org/certs/2024/r3.pem` (або актуальний з їхнього сайту), вставити під основний сертифікат в одне поле «Certificate».

Після того як svitlobot почав віддавати ту саму конфігурацію TLS, що й kasa (той самий сертифікат або повна цепочка), Arduino має підключатися без змін у скетчі (тільки `server = "svitlobot.helgamade.com"`).
