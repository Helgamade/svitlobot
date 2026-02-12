# -*- coding: utf-8 -*-
"""
Parse reviews count from helgamade.com.ua and save to our MySQL (displayboard_reviews).
Run by cron every 10–30 min. Same logic as parser_otzyv_helgamade.php, our DB.
"""
from __future__ import absolute_import
import re
import os
from pathlib import Path

_env = Path(__file__).resolve().parent / ".env"
if _env.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_env)
    except ImportError:
        pass

import requests
import db

REVIEWS_URL = os.environ.get("REVIEWS_PARSER_URL", "https://helgamade.com.ua/ua/")
USER_AGENT = "SvitlobotReviews/1.0"
TIMEOUT = 15


def parse_reviews_count(html: str) -> int:
    """Find first number in text of element with class b-review-info__link. Returns 0 if not found."""
    # Same as PHP: //a[@class="b-review-info__link"] -> textContent -> first \d+
    m = re.search(r'class="b-review-info__link"[^>]*>([^<]+)<', html, re.DOTALL)
    if not m:
        return 0
    num_m = re.search(r"\d+", m.group(1))
    return int(num_m.group(0)) if num_m else 0


def run_once() -> bool:
    try:
        r = requests.get(REVIEWS_URL, timeout=TIMEOUT, headers={"User-Agent": USER_AGENT})
        r.raise_for_status()
        count = parse_reviews_count(r.text)
        db.set_reviews_count(count)
        return True
    except Exception:
        return False


def main():
    run_once()


if __name__ == "__main__":
    main()
