import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List
from sqlalchemy import create_engine, Engine, select
from sqlalchemy.orm import Session
from data.Models import Event
from enums.enums import UserEnum, EventTypeEnum

load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

if not DB_NAME or not DB_USER or not DB_PASSWORD:
    raise RuntimeError("Missing required DB env vars: DB_NAME, DB_USER, DB_PASSWORD")


def get_engine() -> Engine:
    """Return the SQLAlchemy engine instance."""
    return create_engine(f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@localhost/{DB_NAME}", echo=True)


def add_event(event_type: EventTypeEnum, user_type: UserEnum, ip_address) -> Optional[Dict[str, Any]]:
    """Insert an event into the `events` table using SQLAlchemy ORM and return the created row as a dict.

    Parameters
    - event_type: Event type (Enum value compatible with Event.event_type)
    - user_type: User type (Enum value compatible with Event.user_type)
    - ip_address: IP address string

    Returns the inserted row (including `id`) as a dict, or None on failure.
    """

    engine = get_engine()

    with Session(engine) as session:
        evt = Event(event_type=event_type, user_type=user_type, ip_address=ip_address)
        session.add(evt)
        session.commit()

        return {
            "id": evt.id,
            "event_type": evt.event_type,
            "user_type": evt.user_type,
            "ip_address": evt.ip_address,
        }


def get_event(event_id: int) -> Optional[Dict[str, Any]]:
    """Fetch a single event by id and return it as a dict. Returns None if not found or on error."""

    with Session(get_engine()) as session:
        evt = session.get(Event, event_id)
        if evt is None:
            return None
        return {
            "id": evt.id,
            "event_type": evt.event_type,
            "user_type": evt.user_type,
            "ip_address": evt.ip_address,
        }


def list_events(skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    """Return a list of events with offset/limit pagination as a list of dicts.

    If skip < 0 or limit <= 0, returns an empty list.
    """
    if skip < 0 or limit <= 0:
        return []

    with Session(get_engine()) as session:
        stmt = select(Event).order_by(Event.id).offset(skip).limit(limit)
        rows = session.execute(stmt).scalars().all()
        result: List[Dict[str, Any]] = []
        for evt in rows:
            result.append({
                "id": evt.id,
                "event_type": evt.event_type,
                "user_type": evt.user_type,
                "ip_address": evt.ip_address,
            })
        return result


# Expose public API
__all__ = ["add_event", "get_event", "list_events"]
