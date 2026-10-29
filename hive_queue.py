import sqlite3
import json
import time
import os
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB_PATH = BASE / "hive_queue.db"

def init_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_type TEXT NOT NULL,
            payload TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            attempts INTEGER DEFAULT 0,
            max_attempts INTEGER DEFAULT 5,
            created_at REAL NOT NULL,
            updated_at REAL NOT NULL,
            idempotency_key TEXT UNIQUE
        )
    """)
    conn.commit()
    conn.close()

def enqueue(task_type, payload, idempotency_key=None):
    conn = sqlite3.connect(str(DB_PATH))
    now = time.time()
    try:
        conn.execute(
            "INSERT INTO queue (task_type, payload, created_at, updated_at, idempotency_key) VALUES (?,?,?,?,?)",
            (task_type, json.dumps(payload), now, now, idempotency_key),
        )
        conn.commit()
        print(f"Enqueued: {task_type}")
    except sqlite3.IntegrityError:
        print(f"Duplicate (idempotency): {idempotency_key}")
    conn.close()

def recover():
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("UPDATE queue SET status='pending' WHERE status='in_progress'")
    conn.commit()
    conn.close()
    print("Recovered in-progress tasks to pending.")

def dequeue():
    conn = sqlite3.connect(str(DB_PATH))
    row = conn.execute(
        "SELECT id, task_type, payload, attempts, max_attempts FROM queue WHERE status='pending' ORDER BY created_at LIMIT 1"
    ).fetchone()
    if row is None:
        conn.close()
        return None
    qid, task_type, payload, attempts, max_attempts = row
    conn.execute("UPDATE queue SET status='in_progress', attempts=attempts+1, updated_at=? WHERE id=?", (time.time(), qid))
    conn.commit()
    conn.close()
    return {"id": qid, "task_type": task_type, "payload": json.loads(payload), "attempts": attempts + 1, "max_attempts": max_attempts}

def complete(qid):
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("UPDATE queue SET status='done', updated_at=? WHERE id=?", (time.time(), qid))
    conn.commit()
    conn.close()

def fail(qid, error):
    conn = sqlite3.connect(str(DB_PATH))
    row = conn.execute("SELECT attempts, max_attempts FROM queue WHERE id=?", (qid,)).fetchone()
    if row:
        attempts, max_attempts = row
        if attempts >= max_attempts:
            conn.execute("UPDATE queue SET status='failed', updated_at=? WHERE id=?", (time.time(), qid))
        else:
            delay = min(2 ** attempts, 60)
            conn.execute("UPDATE queue SET status='pending', updated_at=? WHERE id=?", (time.time() + delay, qid))
    conn.commit()
    conn.close()

def status():
    conn = sqlite3.connect(str(DB_PATH))
    rows = conn.execute("SELECT status, COUNT(*) FROM queue GROUP BY status").fetchall()
    conn.close()
    return dict(rows)

if __name__ == "__main__":
    import sys
    init_db()
    if len(sys.argv) < 2:
        print("Usage: hive_queue.py [init|status|enqueue <type> <payload>|dequeue|recover]")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "init":
        print("Database initialized.")
    elif cmd == "status":
        print(status())
    elif cmd == "enqueue" and len(sys.argv) >= 4:
        enqueue(sys.argv[2], json.loads(sys.argv[3]))
    elif cmd == "dequeue":
        item = dequeue()
        print(item if item else "No pending tasks.")
    elif cmd == "recover":
        recover()
    else:
        print("Unknown command")