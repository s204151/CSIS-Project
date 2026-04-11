import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List
from sqlalchemy import create_engine, Engine, select, text
from sqlalchemy.orm import Session
from data.Models import Event, Alert
from enums.enums import UserEnum, EventTypeEnum, AlertTypeEnum, SeverityEnum
from datetime import datetime, timedelta

load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


def get_engine() -> Engine:
    """Return the SQLAlchemy engine instance.

    Raises RuntimeError if DB environment variables are not set.
    """
    if not DB_NAME or not DB_USER or not DB_PASSWORD:
        raise RuntimeError("Missing required DB env vars: DB_NAME, DB_USER, DB_PASSWORD")
    return create_engine(f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@localhost/{DB_NAME}", echo=True)


def add_event(event_type: EventTypeEnum, user_type: UserEnum, ip_address, datetime: datetime) -> Optional[Dict[str, Any]]:
    """Insert an event into the `events` table using SQLAlchemy ORM and return the created row as a dict.

    Parameters
    - event_type: Event type (Enum value compatible with Event.event_type)
    - user_type: User type (Enum value compatible with Event.user_type)
    - ip_address: IP address string

    Returns the inserted row (including `id`) as a dict, or None on failure.
    """

    engine = get_engine()

    with Session(engine) as session:
        evt = Event(event_type=event_type, user_type=user_type, ip_address=ip_address, datetime=datetime)
        session.add(evt)
        session.commit()

        return {
            "id": evt.id,
            "event_type": evt.event_type,
            "user_type": evt.user_type,
            "ip_address": evt.ip_address,
            "datetime": evt.datetime
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


def get_alert(alert_id: int) -> Optional[Dict[str, Any]]:
    """Fetch a single alert by id and return it as a dict. Returns None if not found."""

    with Session(get_engine()) as session:
        alt = session.get(Alert, alert_id)
        if alt is None:
            return None
        return {
            "id": alt.id,
            "alert_type": alt.alert_type,
            "severity": alt.severity,
            "ip_address": alt.ip_address,
            "created_at": alt.created_at,
            "event_id": alt.event_id,
        }


def list_alerts(skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    """Return a list of alerts with offset/limit pagination as a list of dicts.

    If skip < 0 or limit <= 0, returns an empty list.
    """
    if skip < 0 or limit <= 0:
        return []

    with Session(get_engine()) as session:
        stmt = select(Alert).order_by(Alert.id).offset(skip).limit(limit)
        rows = session.execute(stmt).scalars().all()
        result: List[Dict[str, Any]] = []
        for alt in rows:
            result.append({
                "id": alt.id,
                "alert_type": alt.alert_type,
                "severity": alt.severity,
                "ip_address": alt.ip_address,
                "created_at": alt.created_at,
                "event_id": alt.event_id,
            })
        return result


def get_recent_events(last_minutes: int, limit: int = 100, ip_address: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return up to `limit` events created within the last `last_minutes` minutes.

    - last_minutes must be > 0
    - limit must be > 0
    - ip_address: optional filter to only return events from this IP

    Uses SQLAlchemy to query the `events` table based on the Event.datetime column and
    returns a list of dicts in descending datetime order (newest first).
    """
    if last_minutes <= 0 or limit <= 0:
        return []

    # use current time (naive) to match how datetimes are stored by the models
    cutoff = datetime.now() - timedelta(minutes=last_minutes)

    with Session(get_engine()) as session:
        # base condition: recent events
        stmt = select(Event).where(Event.datetime >= cutoff)

        # optional IP filter (use text() with a bound parameter to keep the query simple and avoid
        # static-analysis type warnings)
        if ip_address:
            stmt = stmt.where(text("ip_address = :ip")).params(ip=ip_address)

        # newest first, limit
        stmt = stmt.order_by(Event.datetime.desc()).limit(limit)

        rows = session.execute(stmt).scalars().all()
        result: List[Dict[str, Any]] = []
        for evt in rows:
            result.append({
                "id": evt.id,
                "event_type": evt.event_type,
                "user_type": evt.user_type,
                "ip_address": evt.ip_address,
                "datetime": getattr(evt, "datetime", None),
            })
        return result


def create_alert(alert_type: AlertTypeEnum, severity: SeverityEnum, ip_address: str, event_id: int) -> Optional[Dict[str, Any]]:
    engine = get_engine()

    with Session(engine) as session:
        alt = Alert(alert_type=alert_type,
                    severity=severity,
                    ip_address=ip_address,
                    created_at=datetime.now(),
                    event_id=event_id)
        session.add(alt)
        session.commit()

        return {
            "id": alt.id,
            "alert_type": alt.alert_type,
            "severity": alt.severity,
            "ip_address": alt.ip_address,
            "created_at": alt.created_at,
            "event_id": alt.event_id,
        }


# Expose public API
__all__ = ["add_event", "get_event", "list_events", "get_alert", "list_alerts", "create_alert", "get_recent_events"]
