"""
MySQL storage for device online/offline events. Used for duration and analytics.
Table: status_events (device_id, changed_at, is_online). Only state changes are stored.
Times are stored in Europe/Kyiv (local time Ukraine).
"""
from __future__ import absolute_import
from datetime import datetime
from typing import Optional, Tuple

try:
    import pymysql
except ImportError:
    pymysql = None  # type: ignore

try:
    import pytz
    _UTC = pytz.UTC
    try:
        _TZ_KYIV = pytz.timezone("Europe/Kyiv")
    except pytz.UnknownTimeZoneError:
        _TZ_KYIV = pytz.timezone("Europe/Kiev")
except Exception:
    _TZ_KYIV = None  # type: ignore

_TABLE = "status_events"
_TABLE_REVIEWS = "displayboard_reviews"


def _utc_to_kyiv(dt):
    """Convert naive UTC datetime to naive local datetime Europe/Kyiv for DB storage."""
    if _TZ_KYIV is None or dt is None:
        return dt
    if dt.tzinfo is None:
        dt = _UTC.localize(dt)
    return dt.astimezone(_TZ_KYIV).replace(tzinfo=None)


def _kyiv_to_utc(dt):
    """Interpret naive datetime as Europe/Kyiv and return naive UTC (for get_last)."""
    if _TZ_KYIV is None or dt is None:
        return dt
    return _TZ_KYIV.localize(dt).astimezone(_UTC).replace(tzinfo=None)


def _conn():
    import config
    kwargs = {
        "user": config.mysql_user(),
        "password": config.mysql_password(),
        "database": config.mysql_database(),
        "charset": "utf8mb4",
        "cursorclass": pymysql.cursors.DictCursor,
    }
    sock = config.mysql_unix_socket()
    if sock:
        kwargs["unix_socket"] = sock
    else:
        kwargs["host"] = config.mysql_host()
        kwargs["port"] = config.mysql_port()
    return pymysql.connect(**kwargs)


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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS displayboard_reviews (
            id TINYINT PRIMARY KEY DEFAULT 1,
            reviews_count INT NOT NULL DEFAULT 0,
            updated_at DATETIME NOT NULL
        )
    """)
    cursor.execute(
        "INSERT IGNORE INTO displayboard_reviews (id, reviews_count, updated_at) VALUES (1, 0, NOW())"
    )


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
                changed_at = row["changed_at"]
                if _TZ_KYIV and changed_at:
                    changed_at = _kyiv_to_utc(changed_at)
                return (changed_at, bool(row["is_online"]))
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
    now_local = _utc_to_kyiv(now)  # store and compare in Kyiv time
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
                    duration_sec = (now_local - last).total_seconds()
                cur.execute(
                    "INSERT INTO status_events (device_id, changed_at, is_online) VALUES (%s, %s, %s)",
                    (device_id, now_local, 1 if is_online else 0),
                )
                conn.commit()
                return (True, duration_sec, prev_online)
        finally:
            conn.close()
    except Exception:
        return (False, None, None)


def get_reviews_count() -> int:
    """Last saved reviews count for displayboard (helgamade.com.ua). 0 if no DB or no row."""
    if not pymysql or not mysql_available():
        return 0
    try:
        conn = _conn()
        try:
            with conn.cursor() as cur:
                ensure_table(cur)
                cur.execute(
                    "SELECT reviews_count FROM displayboard_reviews WHERE id = 1"
                )
                row = cur.fetchone()
                return int(row["reviews_count"]) if row else 0
        finally:
            conn.close()
    except Exception:
        return 0


def set_reviews_count(count: int) -> None:
    """Save reviews count for displayboard. Uses Europe/Kyiv for updated_at."""
    if not pymysql or not mysql_available():
        return
    now_local = _utc_to_kyiv(datetime.utcnow())
    try:
        conn = _conn()
        try:
            with conn.cursor() as cur:
                ensure_table(cur)
                cur.execute(
                    "UPDATE displayboard_reviews SET reviews_count = %s, updated_at = %s WHERE id = 1",
                    (max(0, count), now_local),
                )
                if cur.rowcount == 0:
                    cur.execute(
                        "INSERT INTO displayboard_reviews (id, reviews_count, updated_at) VALUES (1, %s, %s)",
                        (max(0, count), now_local),
                    )
                conn.commit()
        finally:
            conn.close()
    except Exception:
        pass


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
