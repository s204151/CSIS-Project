import os
from dotenv import load_dotenv
import psycopg
from typing import Optional, Dict, Any, List

load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

if not DB_NAME or not DB_USER or not DB_PASSWORD:
    raise RuntimeError("Missing required DB env vars: DB_NAME, DB_USER, DB_PASSWORD")


def get_conn():
    """Return a new psycopg connection using environment configuration."""
    return psycopg.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)


def _row_to_dict(cur, row) -> Dict[str, Any]:
    """Convert a cursor row (tuple) into a dict using cursor.description for column names."""
    cols = [c.name for c in cur.description]
    return dict(zip(cols, row))


def add_event(event) -> Optional[Dict[str, Any]]:
    """Insert an event into the `events` table using an EventCreate object and return the created row as a dict.

    Parameters
    - event: instance of EventCreate (has user, ip_address, success)

    Returns the inserted row (including `id`) or None on failure.
    """
    # Extract primitive values from the Pydantic model
    user_type = event.user_type.value if hasattr(event.user_type, 'value') else str(event.user_type)
    ip_address = str(event.ip_address)
    success = bool(event.success)

    sql = 'INSERT INTO events (user_type, ip_address, success) VALUES (%s, %s, %s) RETURNING *;'
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (user_type, ip_address, success))
            row = cur.fetchone()
            if row:
                return _row_to_dict(cur, row)
            return None


def get_event(event_id: int) -> Optional[Dict[str, Any]]:
    """Fetch a single event by id from the `events` table and return it as a dict.

    Returns None if not found.
    """
    sql = 'SELECT * FROM events WHERE id = %s;'
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (event_id,))
            row = cur.fetchone()
            if row:
                return _row_to_dict(cur, row)
            return None


def list_events(skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    """Return a list of events with offset/limit pagination as a list of dicts."""
    if skip < 0 or limit <= 0:
        return []

    sql = 'SELECT * FROM events ORDER BY id ASC OFFSET %s LIMIT %s;'
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (skip, limit))
            rows = cur.fetchall()
            return [_row_to_dict(cur, r) for r in rows]


# Expose public API
__all__ = ["get_conn", "add_event", "get_event", "list_events"]


print(get_event(1))
