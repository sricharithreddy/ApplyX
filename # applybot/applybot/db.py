# applybot/db.py
import sqlite3
from typing import Optional
DB_PATH = "applied_jobs.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS applied_jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        platform TEXT,
        job_id TEXT,
        job_title TEXT,
        company TEXT,
        job_url TEXT,
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(platform, job_id)
    )
    """)
    conn.commit()
    conn.close()

def has_applied(platform: str, job_id: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT 1 FROM applied_jobs WHERE platform=? AND job_id=?", (platform, job_id))
    res = c.fetchone()
    conn.close()
    return bool(res)

def save_application(platform: str, job_id: str, job_title: str, company: str, job_url: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("""
        INSERT INTO applied_jobs (platform, job_id, job_title, company, job_url)
        VALUES (?, ?, ?, ?, ?)
        """, (platform, job_id, job_title, company, job_url))
        conn.commit()
    except Exception:
        pass
    finally:
        conn.close()
