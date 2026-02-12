# -*- coding: utf-8 -*-
"""
Minimal HTTP-only server for Arduino displayboard (no SSL).
Serves GET /api/displayboard/current -> {"value": 0|1}.
Use when Arduino WiFiSSLClient fails (e.g. Renesas UNO R4 WiFi).
Run on the same machine as svitlobot or on a device in LAN; Arduino uses WiFiClient (port 8080).
"""
from __future__ import absolute_import
import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

# Load .env
_env = Path(__file__).resolve().parent / ".env"
if _env.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_env)
    except ImportError:
        pass

# Only need TUYA_DEVICE_ID + MySQL; don't import config (it requires TELEGRAM_* etc.)
import db


class DisplayboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.rstrip("/") != "/api/displayboard/current":
            self.send_response(404)
            self.end_headers()
            return
        value = 0
        reviews = 0
        device_id = os.environ.get("TUYA_DEVICE_ID", "").strip()
        if device_id and db.mysql_available():
            try:
                last = db.get_last(device_id)
                if last is not None:
                    _, is_online = last
                    value = 1 if is_online else 0
                reviews = db.get_reviews_count()
            except Exception:
                pass
        body = json.dumps({"value": value, "reviews": reviews}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        # Quiet log
        pass


def main():
    port = int(os.environ.get("DISPLAYBOARD_HTTP_PORT", "8080"))
    server = HTTPServer(("0.0.0.0", port), DisplayboardHandler)
    print("Displayboard HTTP on port %d (no SSL). Arduino: server=%s port=%d WiFiClient" % (port, "this_host_ip", port))
    server.serve_forever()


if __name__ == "__main__":
    main()
