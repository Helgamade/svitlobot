"""Read config from environment. No defaults for secrets."""
import os
from pathlib import Path

# Load .env if present (optional)
_env = Path(__file__).resolve().parent / ".env"
if _env.exists():
    from dotenv import load_dotenv
    load_dotenv(_env)


def _get(key: str) -> str:
    v = os.environ.get(key)
    if not v or not v.strip():
        raise SystemExit(f"Missing or empty env: {key}")
    return v.strip()


def tuya_access_id() -> str:
    return _get("TUYA_ACCESS_ID")


def tuya_access_secret() -> str:
    return _get("TUYA_ACCESS_SECRET")


def tuya_device_id() -> str:
    return _get("TUYA_DEVICE_ID")


def tuya_base_url() -> str:
    return os.environ.get("TUYA_BASE_URL", "https://openapi.tuyaeu.com").rstrip("/")


def telegram_bot_token() -> str:
    return _get("TELEGRAM_BOT_TOKEN")


def telegram_channel_id() -> str:
    return _get("TELEGRAM_CHANNEL_ID")


def poll_interval() -> int:
    return int(os.environ.get("POLL_INTERVAL", "300"))
