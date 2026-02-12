"""
Poll Tuya device status, send to Telegram channel. Placeholder for Arduino later.
"""
import logging
import time

import config
from tuya_client import get_token, get_device_status
from telegram_sender import send_to_channel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


def format_status(device_id: str, status_list: list[dict]) -> str:
    """Build human-readable status message."""
    lines = [f"Device: {device_id}", "Status:"]
    for s in status_list:
        code = s.get("code", "")
        value = s.get("value")
        lines.append(f"  {code}: {value}")
    return "\n".join(lines)


def send_to_arduino(status_text: str, status_list: list[dict]) -> None:
    """Placeholder: send status to Arduino UNO WiFi (HTTP or Serial)."""
    # TODO: implement when Arduino is ready
    # e.g. requests.post(f"http://{ARDUINO_IP}/status", json=status_list)
    pass


def run_once() -> bool:
    """Fetch status from Tuya, send to Telegram. Returns True on success."""
    base = config.tuya_base_url()
    aid = config.tuya_access_id()
    secret = config.tuya_access_secret()
    device_id = config.tuya_device_id()

    token = get_token(base, aid, secret)
    status_list = get_device_status(base, aid, secret, token, device_id)

    text = format_status(device_id, status_list)
    send_to_channel(config.telegram_bot_token(), config.telegram_channel_id(), text)
    send_to_arduino(text, status_list)
    return True


def main() -> None:
    interval = config.poll_interval()
    log.info("Starting Tuya status -> Telegram (interval=%ds)", interval)
    while True:
        try:
            run_once()
            log.info("Status sent to Telegram")
        except Exception as e:
            log.exception("Poll/send failed: %s", e)
        time.sleep(interval)


if __name__ == "__main__":
    main()
