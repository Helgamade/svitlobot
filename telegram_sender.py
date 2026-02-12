"""Send message to Telegram channel via Bot API."""
import requests

TELEGRAM_API = "https://api.telegram.org"


def send_to_channel(bot_token: str, channel_id: str, text: str) -> bool:
    """Post text to channel. Returns True on success."""
    url = f"{TELEGRAM_API}/bot{bot_token}/sendMessage"
    payload = {"chat_id": channel_id, "text": text, "disable_web_page_preview": True}
    r = requests.post(url, json=payload, timeout=10)
    if not r.ok:
        raise RuntimeError(f"Telegram API error: {r.status_code} {r.text}")
    data = r.json()
    if not data.get("ok"):
        raise RuntimeError(f"Telegram API: {data}")
    return True
