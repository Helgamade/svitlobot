"""
Poll Tuya device status, send to Telegram channel. Placeholder for Arduino later.
Short UA messages; MySQL stores state changes for duration/analytics.
"""
from __future__ import absolute_import
import logging
import time
from datetime import datetime
from typing import List

import config
from tuya_client import get_token, get_device_info, get_device_status
from telegram_sender import send_to_channel
from message_format import format_short_status
import db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


def send_to_arduino(status_text: str, status_list: List[dict]) -> None:
    """Placeholder: send status to Arduino UNO WiFi (HTTP or Serial)."""
    # TODO: implement when Arduino is ready
    # e.g. requests.post(f"http://{ARDUINO_IP}/status", json=status_list)
    pass


def run_once() -> bool:
    """Fetch status from Tuya; on state change save to DB and send short UA message to Telegram."""
    base = config.tuya_base_url()
    aid = config.tuya_access_id()
    secret = config.tuya_access_secret()
    device_id = config.tuya_device_id()

    token = get_token(base, aid, secret)
    device_info = get_device_info(base, aid, secret, token, device_id)
    status_list = get_device_status(base, aid, secret, token, device_id)

    is_online = device_info.get("is_online", False) is True
    now_utc = datetime.utcnow()
    changed = False
    duration_sec = None
    prev_online = None

    if db.mysql_available():
        changed, duration_sec, prev_online = db.record_if_changed(device_id, is_online, now_utc)
    else:
        if not hasattr(run_once, "_last_online"):
            run_once._last_online = {}  # type: ignore
        last = run_once._last_online.get(device_id)  # type: ignore
        if last is None:
            changed = True
        elif last != is_online:
            changed = True
            prev_online = last
        run_once._last_online[device_id] = is_online  # type: ignore

    if changed:
        now_local = datetime.now()
        text = format_short_status(
            is_online,
            now=now_local,
            duration_sec=duration_sec,
            prev_was_online=prev_online,
        )
        send_to_channel(config.telegram_bot_token(), config.telegram_channel_id(), text)
        send_to_arduino(text, status_list)
        log.info("Status changed -> Telegram: %s", "online" if is_online else "offline")
    return True


def main() -> None:
    interval = config.poll_interval()
    log.info("Starting Tuya status -> Telegram (interval=%ds)", interval)
    while True:
        try:
            run_once()
        except Exception as e:
            log.exception("Poll/send failed: %s", e)
        time.sleep(interval)


if __name__ == "__main__":
    main()
