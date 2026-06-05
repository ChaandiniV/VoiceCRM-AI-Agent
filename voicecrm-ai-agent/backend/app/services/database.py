import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from backend.app.config import get_settings


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    settings = get_settings()
    Path(settings.database_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(settings.database_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                call_sid TEXT,
                caller_phone TEXT,
                customer_name TEXT,
                started_at TEXT NOT NULL,
                status TEXT NOT NULL,
                source TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS transcripts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                call_id INTEGER NOT NULL,
                speaker TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(call_id) REFERENCES calls(id)
            );

            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                call_id INTEGER NOT NULL,
                customer_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT,
                company TEXT,
                industry TEXT,
                requirement TEXT NOT NULL,
                budget TEXT,
                timeline TEXT,
                preferred_channel TEXT,
                lead_score INTEGER NOT NULL,
                priority TEXT NOT NULL,
                next_action TEXT NOT NULL,
                crm_status TEXT NOT NULL,
                crm_record_id TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(call_id) REFERENCES calls(id)
            );

            CREATE TABLE IF NOT EXISTS webhook_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider TEXT NOT NULL,
                event_type TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )


def create_call(call_sid: str | None, caller_phone: str, customer_name: str, source: str) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO calls(call_sid, caller_phone, customer_name, started_at, status, source)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (call_sid, caller_phone, customer_name, utc_now(), "started", source),
        )
        return int(cur.lastrowid)


def update_call_status(call_id: int, status: str) -> None:
    with get_connection() as conn:
        conn.execute("UPDATE calls SET status = ? WHERE id = ?", (status, call_id))


def add_transcript(call_id: int, speaker: str, message: str) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO transcripts(call_id, speaker, message, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (call_id, speaker, message, utc_now()),
        )
        return int(cur.lastrowid)


def create_lead(
    *,
    call_id: int,
    customer_name: str,
    phone: str,
    email: str | None,
    company: str | None,
    industry: str | None,
    requirement: str,
    budget: str | None,
    timeline: str | None,
    preferred_channel: str | None,
    lead_score: int,
    priority: str,
    next_action: str,
    crm_status: str,
    crm_record_id: str | None,
) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO leads(
                call_id, customer_name, phone, email, company, industry, requirement,
                budget, timeline, preferred_channel, lead_score, priority, next_action,
                crm_status, crm_record_id, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                call_id,
                customer_name,
                phone,
                email,
                company,
                industry,
                requirement,
                budget,
                timeline,
                preferred_channel,
                lead_score,
                priority,
                next_action,
                crm_status,
                crm_record_id,
                utc_now(),
            ),
        )
        return int(cur.lastrowid)


def store_webhook_event(provider: str, event_type: str, payload: dict[str, Any]) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO webhook_events(provider, event_type, payload_json, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (provider, event_type, json.dumps(payload, default=str), utc_now()),
        )
        return int(cur.lastrowid)


def fetch_all(table: str) -> list[dict[str, Any]]:
    allowed = {"calls", "leads", "transcripts", "webhook_events"}
    if table not in allowed:
        raise ValueError(f"Unsupported table: {table}")
    with get_connection() as conn:
        rows = conn.execute(f"SELECT * FROM {table} ORDER BY id DESC").fetchall()
        return [dict(row) for row in rows]


def fetch_lead(lead_id: int) -> dict[str, Any] | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM leads WHERE id = ?", (lead_id,)).fetchone()
        return dict(row) if row else None
