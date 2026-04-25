import sqlite3
import os
from datetime import datetime

# Use /tmp for Render (writable directory)
DB_NAME = os.path.join("/tmp", "traffic.db")

# ── Create tables if they don't exist ────────────────────────
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS signal_logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            lane        TEXT    NOT NULL,
            signal      TEXT    NOT NULL,
            vehicles    INTEGER NOT NULL,
            duration    INTEGER NOT NULL,
            timestamp   TEXT    NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stats_logs (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            total_vehicles    INTEGER NOT NULL,
            peak_lane         TEXT    NOT NULL,
            avg_wait_time     INTEGER NOT NULL,
            timestamp         TEXT    NOT NULL
        )
    ''')

    conn.commit()
    conn.close()
    print("Database initialized.")

# ── Save signal states ────────────────────────────────────────
def log_signals(signal_data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for item in signal_data:
        cursor.execute('''
            INSERT INTO signal_logs (lane, signal, vehicles, duration, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (item['lane'], item['signal'], item['vehicles'], item['duration'], timestamp))

    conn.commit()
    conn.close()

# ── Save summary stats ────────────────────────────────────────
def log_stats(stats):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute('''
        INSERT INTO stats_logs (total_vehicles, peak_lane, avg_wait_time, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (stats['total_vehicles'], stats['peak_lane'], stats['avg_wait_time'], timestamp))

    conn.commit()
    conn.close()

# ── Fetch last N signal log entries ──────────────────────────
def get_recent_logs(limit=20):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT lane, signal, vehicles, duration, timestamp
        FROM signal_logs
        ORDER BY id DESC
        LIMIT ?
    ''', (limit,))

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "lane":      r[0],
            "signal":    r[1],
            "vehicles":  r[2],
            "duration":  r[3],
            "timestamp": r[4]
        }
        for r in rows
    ]

# ── Fetch stats history ───────────────────────────────────────
def get_stats_history(limit=10):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT total_vehicles, peak_lane, avg_wait_time, timestamp
        FROM stats_logs
        ORDER BY id DESC
        LIMIT ?
    ''', (limit,))

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "total_vehicles": r[0],
            "peak_lane":      r[1],
            "avg_wait_time":  r[2],
            "timestamp":      r[3]
        }
        for r in rows
    ]