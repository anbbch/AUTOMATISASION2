import json
import sqlite3

DB_PATH = "runs.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            api TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            passed INTEGER NOT NULL,
            failed INTEGER NOT NULL,
            error_rate REAL NOT NULL,
            latency_ms_avg REAL NOT NULL,
            latency_ms_p95 REAL NOT NULL,
            availability REAL NOT NULL,
            payload TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_run(run_data):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO runs (
            api, timestamp, passed, failed, error_rate,
            latency_ms_avg, latency_ms_p95, availability, payload
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        run_data["api"],
        run_data["timestamp"],
        run_data["summary"]["passed"],
        run_data["summary"]["failed"],
        run_data["summary"]["error_rate"],
        run_data["summary"]["latency_ms_avg"],
        run_data["summary"]["latency_ms_p95"],
        run_data["summary"]["availability"],
        json.dumps(run_data, ensure_ascii=False)
    ))
    conn.commit()
    conn.close()


def list_runs(limit=20):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT id, api, timestamp, passed, failed, error_rate,
               latency_ms_avg, latency_ms_p95, availability, payload
        FROM runs
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    conn.close()

    results = []
    for row in rows:
        results.append({
            "id": row[0],
            "api": row[1],
            "timestamp": row[2],
            "passed": row[3],
            "failed": row[4],
            "error_rate": row[5],
            "latency_ms_avg": row[6],
            "latency_ms_p95": row[7],
            "availability": row[8],
            "payload": json.loads(row[9])
        })
    return results


def get_last_run():
    runs = list_runs(limit=1)
    return runs[0] if runs else None
