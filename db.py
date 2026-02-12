"""
MySQL storage for device online/offline events. Used for duration and analytics.
Table: status_events (device_id, changed_at, is_online). Only state changes are stored.
"""
from __future__ import absolute_import
from datetime import datetime
from typing import Optional, Tuple

try:
    import pymysql
except ImportError:
    pymysql = None  # type: ignore

_TABLE = "status_events"


def _conn():
    import config
    return pymysql.connect(
        host=config.mysql_host(),
        user=config.mysql_user(),
        password=config.mysql_password(),
        database=config.mysql_database(),
        port=config.mysql_port(),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )


def ensure_table(cursor) -> None:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS status_events (
            id INT AUTO_INCREMENT PRIMARY KEY,
            device_id VARCHAR(64) NOT NULL,
            changed_at DATETIME(3) NOT NULL,
            is_online TINYINT(1) NOT NULL,
            INDEX (device_id, changed_at)
        )
    """)


def get_last(device_id: str) -> Optional[Tuple[datetime, bool]]:
    """Returns (changed_at, is_online) of last event for device, or None."""
    if not pymysql or not mysql_available():
        return None
    try:
        conn = _conn()
        try:
            with conn.cursor() as cur:
                ensure_table(cur)
                cur.execute(
                    "SELECT changed_at, is_online FROM status_events WHERE device_id = %s ORDER BY changed_at DESC LIMIT 1",
                    (device_id,),
                )
                row = cur.fetchone()
                if not row:
                    return None
                return (row["changed_at"], bool(row["is_online"]))
        finally:
            conn.close()
    except Exception:
        return None


def record_if_changed(device_id: str, is_online: bool, now: Optional[datetime] = None) -> Tuple[bool, Optional[float], Optional[bool]]:
    """
    If state changed, insert row and return (True, duration_seconds, previous_online).
    Otherwise return (False, None, None).
    duration_seconds = how long the previous state lasted (now - last changed_at).
    """
    if not pymysql or not mysql_available():
        return (False, None, None)
    now = now or datetime.utcnow()
    try:
        conn = _conn()
        try:
            with conn.cursor() as cur:
                ensure_table(cur)
                cur.execute(
                    "SELECT changed_at, is_online FROM status_events WHERE device_id = %s ORDER BY changed_at DESC LIMIT 1",
                    (device_id,),
                )
                row = cur.fetchone()
                if row and bool(row["is_online"]) == is_online:
                    return (False, None, None)
                prev_online = bool(row["is_online"]) if row else None
                duration_sec = None
                if row and row["changed_at"]:
                    last = row["changed_at"]
                    duration_sec = (now - last).total_seconds()
                cur.execute(
                    "INSERT INTO status_events (device_id, changed_at, is_online) VALUES (%s, %s, %s)",
                    (device_id, now, 1 if is_online else 0),
                )
                conn.commit()
                return (True, duration_sec, prev_online)
        finally:
            conn.close()
    except Exception:
        return (False, None, None)


def mysql_available() -> bool:
    """True if MySQL config is set and connection works."""
    if not pymysql:
        return False
    try:
        import config
        if not config.mysql_user() or not config.mysql_database():
            return False
        conn = _conn()
        conn.close()
        return True
    except Exception:
        return False
