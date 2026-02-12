# -*- coding: utf-8 -*-
"""
Minimal web app at https://svitlobot.helgamade.com/
Form: type message + secret, submit → send to Telegram channel.
"""
from __future__ import absolute_import
import os
from flask import Flask, request, Response

import config
from telegram_sender import send_to_channel

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024  # 8 KB max body

HTML_FORM = """<!DOCTYPE html>
<html lang="uk">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Світлобот — надіслати в канал</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 480px; margin: 2rem auto; padding: 0 1rem; }
    h1 { font-size: 1.25rem; }
    label { display: block; margin-top: 0.75rem; }
    input[type="password"], textarea { width: 100%; box-sizing: border-box; padding: 0.5rem; }
    textarea { min-height: 100px; resize: vertical; }
    button { margin-top: 1rem; padding: 0.5rem 1rem; }
    .msg { margin-top: 1rem; padding: 0.5rem; border-radius: 4px; }
    .ok { background: #d4edda; }
    .err { background: #f8d7da; }
  </style>
</head>
<body>
  <h1>Надіслати повідомлення в канал</h1>
  <form method="post" action="/">
    <label for="text">Текст:</label>
    <textarea id="text" name="text" required placeholder="Введіть повідомлення..."></textarea>
    <label for="secret">Секрет (пароль):</label>
    <input type="password" id="secret" name="secret" required placeholder="WEB_SEND_SECRET з .env">
    <button type="submit">Надіслати в Telegram</button>
  </form>
  <!--EXTRA-->
</body>
</html>
"""


def _html_with_extra(extra):
    return HTML_FORM.replace("<!--EXTRA-->", extra)


def _get_secret():
    s = config.web_send_secret()
    if not s:
        return None
    return s


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        extra = ""
        if not _get_secret():
            extra = '<p class="msg err">WEB_SEND_SECRET не задано в .env — відправка вимкнена.</p>'
        return Response(_html_with_extra(extra), mimetype="text/html; charset=utf-8")

    # POST
    secret = _get_secret()
    if not secret:
        return Response(_html_with_extra('<p class="msg err">Відправка вимкнена (немає WEB_SEND_SECRET).</p>'), 503, mimetype="text/html; charset=utf-8")

    form_secret = (request.form.get("secret") or "").strip()
    if form_secret != secret:
        return Response(_html_with_extra('<p class="msg err">Невірний секрет.</p>'), 403, mimetype="text/html; charset=utf-8")

    text = (request.form.get("text") or "").strip()
    if not text:
        return Response(_html_with_extra('<p class="msg err">Текст порожній.</p>'), 400, mimetype="text/html; charset=utf-8")

    try:
        send_to_channel(config.telegram_bot_token(), config.telegram_channel_id(), text)
        return Response(_html_with_extra('<p class="msg ok">Надіслано в канал.</p>'), mimetype="text/html; charset=utf-8")
    except Exception as e:
        err_escaped = str(e).replace("<", "&lt;")
        return Response(_html_with_extra('<p class="msg err">Помилка: {}</p>'.format(err_escaped)), 502, mimetype="text/html; charset=utf-8")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
