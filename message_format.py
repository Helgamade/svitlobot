# -*- coding: utf-8 -*-
"""Short Ukrainian status messages for Telegram."""
from __future__ import absolute_import
from datetime import datetime
from typing import Optional


def format_duration_ua(seconds: Optional[float]) -> Optional[str]:
    """Format seconds as 'Xгод Yхв' or 'Xхв' if < 60 min. None -> None."""
    if seconds is None or seconds < 0:
        return None
    m = int(seconds // 60)
    h = m // 60
    m = m % 60
    if h > 0:
        return "%dгод %dхв" % (h, m)
    return "%dхв" % m


def format_short_status(
    is_online: bool,
    now: Optional[datetime] = None,
    duration_sec: Optional[float] = None,
    prev_was_online: Optional[bool] = None,
) -> str:
    """
    Short message:
    - Online: "🟢 13:05 Світло є" + "🕓 Його не було 2год 50хв"
    - Offline: "🔴 10:13 Світло нема" + "🕓 Воно було 9год 39хв"
    If duration_sec is None, second line is omitted.
    """
    now = now or datetime.utcnow()
    t_str = now.strftime("%H:%M")
    if is_online:
        line1 = "🟢 %s Світло є" % t_str
        if duration_sec is not None and prev_was_online is False:
            d = format_duration_ua(duration_sec)
            if d:
                line1 += "\n🕓 Його не було %s" % d
    else:
        line1 = "🔴 %s Світло нема" % t_str
        if duration_sec is not None and prev_was_online is True:
            d = format_duration_ua(duration_sec)
            if d:
                line1 += "\n🕓 Воно було %s" % d
    return line1
