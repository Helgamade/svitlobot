# -*- coding: utf-8 -*-
"""
Minimal web app at https://svitlobot.helgamade.com/
Form: type message + secret, submit → send to Telegram channel.
"""
from __future__ import absolute_import
import os
from flask import Flask, request, Response, redirect, url_for, session

import config
from telegram_sender import send_to_channel

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024  # 8 KB max body
_app_secret = os.environ.get("FLASK_SECRET_KEY") or config.web_send_secret()
app.secret_key = _app_secret if _app_secret else "svitlobot-web-send-fallback"

HTML_FORM = """<!DOCTYPE html>
<html lang="uk">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="theme-color" content="#1a1a1a">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <title>Світлобот — надіслати в канал</title>
  <style>
    :root {
      --bg: #0f0f0f;
      --surface: #1a1a1a;
      --border: #2d2d2d;
      --text: #e8e8e8;
      --text-muted: #9a9a9a;
      --accent: #4a9eff;
      --accent-hover: #6bb1ff;
      --ok-bg: rgba(52, 168, 83, 0.2);
      --ok-border: #34a853;
      --err-bg: rgba(234, 67, 53, 0.2);
      --err-border: #ea4335;
      --radius: 12px;
      --radius-sm: 8px;
      --tap: 48px;
    }
    * { box-sizing: border-box; }
    html { -webkit-text-size-adjust: 100%; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: var(--bg);
      color: var(--text);
      margin: 0;
      min-height: 100vh;
      min-height: 100dvh;
      padding: max(0.75rem, env(safe-area-inset-top)) max(1rem, env(safe-area-inset-right)) max(1rem, env(safe-area-inset-bottom)) max(1rem, env(safe-area-inset-left));
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: flex-start;
    }
    .wrap {
      width: 100%;
      max-width: 420px;
    }
    .card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 1.5rem;
      margin-bottom: 1rem;
    }
    h1 {
      font-size: 1.35rem;
      font-weight: 600;
      margin: 0 0 1.25rem 0;
      letter-spacing: -0.02em;
    }
    label {
      display: block;
      font-size: 0.875rem;
      color: var(--text-muted);
      margin-bottom: 0.35rem;
      margin-top: 1rem;
    }
    label:first-of-type { margin-top: 0; }
    input[type="text"],
    textarea {
      width: 100%;
      padding: 0.85rem 1rem;
      font-size: 1rem;
      line-height: 1.45;
      color: var(--text);
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      -webkit-appearance: none;
      appearance: none;
      min-height: var(--tap);
      transition: border-color 0.15s;
    }
    textarea {
      min-height: 120px;
      resize: vertical;
    }
    input:focus, textarea:focus {
      outline: none;
      border-color: var(--accent);
    }
    ::placeholder { color: var(--text-muted); opacity: 0.8; }
    button {
      width: 100%;
      margin-top: 1.25rem;
      padding: 0.9rem 1rem;
      font-size: 1rem;
      font-weight: 600;
      color: #fff;
      background: var(--accent);
      border: none;
      border-radius: var(--radius-sm);
      min-height: var(--tap);
      cursor: pointer;
      transition: background 0.15s;
      -webkit-tap-highlight-color: transparent;
    }
    button:hover { background: var(--accent-hover); }
    button:active { opacity: 0.95; }
    .msg {
      margin-top: 1rem;
      padding: 0.85rem 1rem;
      border-radius: var(--radius-sm);
      font-size: 0.9rem;
      line-height: 1.4;
      border: 1px solid;
    }
    .msg.ok { background: var(--ok-bg); border-color: var(--ok-border); color: #81c995; }
    .msg.err { background: var(--err-bg); border-color: var(--err-border); color: #f28b82; }
    .sent-preview {
      margin-top: 0.75rem;
      padding: 0.85rem 1rem;
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      font-size: 0.9rem;
      line-height: 1.5;
      white-space: pre-wrap;
      word-break: break-word;
      color: var(--text-muted);
    }
    .sent-preview strong { color: var(--text); font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.03em; margin-bottom: 0.35rem; display: block; }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <h1>Надіслати в канал</h1>
      <form method="post" action="/">
        <label for="text">Повідомлення</label>
        <textarea id="text" name="text" required placeholder="Введіть текст..." autocomplete="off"></textarea>
        <label for="secret">Секрет</label>
        <input type="text" id="secret" name="secret" required placeholder="Пароль для відправки" autocomplete="off">
        <button type="submit">Надіслати в Telegram</button>
      </form>
      <!--EXTRA-->
    </div>
  </div>
</body>
</html>
"""


def _html_with_extra(extra):
    return HTML_FORM.replace("<!--EXTRA-->", extra)


def _escape_html(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _get_secret():
    s = config.web_send_secret()
    if not s:
        return None
    return s


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        extra = ""
        if request.args.get("sent") == "1":
            extra = '<p class="msg ok">Надіслано в канал.</p>'
            last = session.pop("last_sent", None)
            if last:
                extra += '<div class="sent-preview"><strong>Надіслано:</strong>' + _escape_html(last) + '</div>'
            extra += '<script>history.replaceState(null, "", "/");</script>'
        elif not _get_secret():
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
        session["last_sent"] = text
        return redirect(url_for("index", sent=1), code=302)
    except Exception as e:
        err_escaped = str(e).replace("<", "&lt;")
        return Response(_html_with_extra('<p class="msg err">Помилка: {}</p>'.format(err_escaped)), 502, mimetype="text/html; charset=utf-8")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
