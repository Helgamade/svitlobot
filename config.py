"""Read config from environment. No defaults for secrets."""
import os
from pathlib import Path

# Load .env if present (optional; skip if dotenv not installed)
_env = Path(__file__).resolve().parent / ".env"
if _env.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_env)
    except ImportError:
        pass


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


def mysql_host() -> str:
    return os.environ.get("MYSQL_HOST", "localhost").strip()


def mysql_port() -> int:
    return int(os.environ.get("MYSQL_PORT", "3306"))


def mysql_user() -> str:
    return os.environ.get("MYSQL_USER", "").strip()


def mysql_password() -> str:
    return os.environ.get("MYSQL_PASSWORD", "").strip()


def mysql_database() -> str:
    return os.environ.get("MYSQL_DATABASE", "").strip()


def mysql_unix_socket() -> str:
    """Optional: path to MySQL socket (if set, host/port are ignored)."""
    return os.environ.get("MYSQL_UNIX_SOCKET", "").strip()


def mq_env() -> str:
    """Tuya MQ topic suffix: 'event' (prod) or 'event-test' (test)."""
    v = os.environ.get("MQ_MODE", "prod").strip().lower()
    return "event-test" if v == "test" else "event"
