#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test: write to status_events, read back. Run from project root with VENV python:
  ./venv/bin/python deploy/test_db_write_read.py
  or:  ./deploy/run_test_db.sh
(If you use plain 'python' and get ImportError, your shell may alias python to system one.)
"""
from __future__ import print_function
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    try:
        import config
        import db
    except Exception as e:
        print("Import error:", e)
        return 1

    if not db.pymysql:
        print("PyMySQL not installed")
        return 1

    print("MYSQL_HOST:", config.mysql_host())
    print("MYSQL_PORT:", config.mysql_port())
    print("MYSQL_DATABASE:", config.mysql_database())
    print("MYSQL_USER:", config.mysql_user())
    print("MYSQL_UNIX_SOCKET:", config.mysql_unix_socket() or "(not set)")
    print("db.mysql_available():", db.mysql_available())

    try:
        conn = db._conn()
        print("Connection: OK")
    except Exception as e:
        print("Connection FAIL:", e)
        print("(Main app would NOT use DB; fix .env and connection.)")
        return 1

    test_device = "_test_svitlobot"
    now = datetime.utcnow()

    try:
        with conn.cursor() as cur:
            db.ensure_table(cur)
            print("Table status_events: OK")

            cur.execute(
                "INSERT INTO status_events (device_id, changed_at, is_online) VALUES (%s, %s, %s)",
                (test_device, now, 1),
            )
            conn.commit()
            print("INSERT: OK (device_id=%s, is_online=1)" % test_device)

            cur.execute(
                "SELECT id, device_id, changed_at, is_online FROM status_events ORDER BY changed_at DESC LIMIT 10"
            )
            rows = cur.fetchall()
            print("SELECT: %d row(s)" % len(rows))
            for r in rows:
                print("  id=%s device_id=%s changed_at=%s is_online=%s" % (
                    r.get("id"), r.get("device_id"), r.get("changed_at"), r.get("is_online")
                ))

            cur.execute("DELETE FROM status_events WHERE device_id = %s", (test_device,))
            conn.commit()
            print("DELETE test row: OK")
    except Exception as e:
        print("Query FAIL:", e)
        return 1
    finally:
        conn.close()

    print("Done. DB write/read works.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
