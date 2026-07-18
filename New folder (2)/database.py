import os
import sqlite3
from datetime import datetime

DB_NAME = os.getenv("AGENT_DB_NAME", "agent_workspace.db")


def init_db() -> None:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS trip_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            destination TEXT NOT NULL,
            duration_days INTEGER NOT NULL,
            itinerary TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS coding_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_type TEXT NOT NULL,
            code_input TEXT NOT NULL,
            ai_response TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    conn.commit()
    conn.close()


def save_trip(destination: str, duration: int, itinerary: str) -> None:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO trip_plans (destination, duration_days, itinerary, created_at) VALUES (?, ?, ?, ?)",
        (destination, duration, itinerary, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_all_trips():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT destination, duration_days, itinerary, created_at FROM trip_plans ORDER BY id DESC"
    )
    trips = cursor.fetchall()
    conn.close()
    return trips


def save_coding_task(task_type: str, code_input: str, ai_response: str) -> None:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO coding_history (task_type, code_input, ai_response, created_at) VALUES (?, ?, ?, ?)",
        (task_type, code_input, ai_response, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_coding_history():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT task_type, code_input, ai_response, created_at FROM coding_history ORDER BY id DESC"
    )
    history = cursor.fetchall()
    conn.close()
    return history
