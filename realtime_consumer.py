# -*- coding: utf-8 -*-
"""
Realtime status via Tuya Message Queue (Pulsar).
Requires Python 3.8+ and: pip install -r requirements.txt -r requirements-mq.txt
Run after enabling Message Service in Tuya IoT project (EU) and subscribing to event topic.
"""
from __future__ import absolute_import
import json
import logging
import sys
import time
from datetime import datetime

import pulsar

import config
from tuya_mq.mq_authentication import get_authentication
from tuya_mq.message_util import decrypt_message, message_id
from telegram_sender import send_to_channel
from message_format import format_short_status
import db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

PULSAR_EU = "pulsar+ssl://mqe.tuyaeu.com:7285/"
MQ_ENV_PROD = "event"
MQ_ENV_TEST = "event-test"
RECONNECT_DELAY_SEC = 30


def _now_from_ts(ts_ms):
    """Convert 13-digit ms timestamp to datetime (UTC)."""
    if ts_ms is None:
        return datetime.utcnow()
    try:
        return datetime.utcfromtimestamp(int(ts_ms) / 1000.0)
    except (TypeError, ValueError, OSError):
        return datetime.utcnow()


def _handle_status_change(device_id: str, is_online: bool, now_utc: datetime) -> None:
    changed, duration_sec, prev_online = db.record_if_changed(device_id, is_online, now_utc)
    if not changed:
        return
    now_local = datetime.now()
    text = format_short_status(
        is_online,
        now=now_local,
        duration_sec=duration_sec,
        prev_was_online=prev_online,
    )
    try:
        send_to_channel(config.telegram_bot_token(), config.telegram_channel_id(), text)
        log.info("MQ status -> Telegram: %s", "online" if is_online else "offline")
    except Exception as e:
        log.exception("Telegram send failed: %s", e)


def handle_decrypted(decrypted_json: str, our_device_id: str) -> None:
    try:
        data = json.loads(decrypted_json)
    except (json.JSONDecodeError, TypeError):
        log.warning("Invalid JSON in decrypted message")
        return
    biz_code = data.get("bizCode") or data.get("bizcode")
    biz_data = data.get("bizData") or data.get("bizdata") or {}
    dev_id = (biz_data.get("devId") or biz_data.get("devid") or "").strip()
    if dev_id != our_device_id:
        return
    ts_ms = biz_data.get("time") or data.get("ts")
    now_utc = _now_from_ts(ts_ms)
    if biz_code == "deviceOffline":
        _handle_status_change(our_device_id, False, now_utc)
    elif biz_code == "deviceOnline":
        _handle_status_change(our_device_id, True, now_utc)
    # devicePropertyMessage (protocol 1000) can be added later if needed for relay/switch reports


def run_consumer_loop(client, consumer, access_key: str, device_id: str) -> None:
    """Process messages until connection error or interrupt."""
    while True:
        msg = consumer.receive()
        msg_id_str = message_id(msg.message_id())
        try:
            decrypted = decrypt_message(msg, access_key)
            handle_decrypted(decrypted, device_id)
        except Exception as e:
            log.exception("Handle message %s: %s", msg_id_str, e)
        try:
            consumer.acknowledge_cumulative(msg)
        except Exception as e:
            log.exception("Ack failed: %s", e)


def main() -> None:
    access_id = config.tuya_access_id()
    access_key = config.tuya_access_secret()
    device_id = config.tuya_device_id()
    mq_env = config.mq_env()
    topic = access_id + "/out/" + mq_env
    subscription = access_id + "-sub"

    while True:
        client = None
        try:
            log.info("Connecting to Pulsar EU, topic=%s sub=%s device=%s", topic, subscription, device_id)
            client = pulsar.Client(
                PULSAR_EU,
                authentication=get_authentication(access_id, access_key),
                tls_allow_insecure_connection=True,
            )
            consumer = client.subscribe(
                topic,
                subscription,
                consumer_type=pulsar.ConsumerType.Failover,
            )
            run_consumer_loop(client, consumer, access_key, device_id)
        except pulsar.Interrupted:
            log.info("Interrupted")
            break
        except KeyboardInterrupt:
            log.info("Stopped by user")
            break
        except Exception as e:
            log.exception("Pulsar connection/loop failed, reconnecting in %ss: %s", RECONNECT_DELAY_SEC, e)
            if client:
                try:
                    client.close()
                except Exception:
                    pass
            time.sleep(RECONNECT_DELAY_SEC)
        else:
            break
    if client:
        try:
            client.close()
        except Exception:
            pass


if __name__ == "__main__":
    if sys.version_info < (3, 8):
        sys.exit("realtime_consumer requires Python 3.8+")
    main()
