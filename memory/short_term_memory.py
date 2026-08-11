import sqlite3
import os
from datetime import datetime

class ShortTermMemory:
    def __init__(self, db_path="memory/short_term_memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt TEXT NOT NULL,
                    intent TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp
                ON interactions (timestamp)
            """)

    def store(self, prompt, intent):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO interactions (prompt, intent) VALUES (?, ?)",
                (prompt, intent)
            )

    def get_recent(self, limit=100):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT prompt, intent FROM interactions ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
            return cursor.fetchall()

    def get_all(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT prompt, intent FROM interactions")
            return cursor.fetchall()