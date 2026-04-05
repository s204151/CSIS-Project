from fastapi import FastAPI, HTTPException
from typing import List
from pydantic import BaseModel
from ipaddress import IPv4Address
from http import HTTPStatus
from enum import Enum
from data.CSIS_db_connector import add_event as db_create_event, get_event as db_get_event, list_events as db_list_events


app = FastAPI()

class UserEnum(str, Enum):
    admin = 'admin'
    member = 'member'

class EventCreate(BaseModel):
    user_type: UserEnum
    ip_address: IPv4Address
    success: bool

class Event(EventCreate):
    id: int

@app.get("/")
def root():
    """ Health check."""
    response = {
        "message": HTTPStatus.OK.phrase,
        "status-code": HTTPStatus.OK,
    }
    return response

@app.post("/events", response_model=Event, status_code=201)
def create_event(event_in: EventCreate):
    """Create a new event and persist to Postgres."""
    try:
        created = db_create_event(event_in)
    except Exception as e:
        # hide raw DB details but return a helpful error
        raise HTTPException(status_code=500, detail=f"DB error: {e}")

    if not created:
        raise HTTPException(status_code=500, detail="Failed to create event")

    try:
        return Event(**created)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Response mapping error: {e}")


@app.get("/events/{event_id}", response_model=Event)
def get_event(event_id: int):
    """Get event by id from Postgres."""
    try:
        row = db_get_event(event_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")
    if not row:
        raise HTTPException(status_code=404, detail="Event not found")
    try:
        return Event(**row)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Response mapping error: {e}")


@app.get("/events", response_model=List[Event])
def list_events(skip: int = 0, limit: int = 100):
    """List events with optional pagination via skip & limit."""
    if skip < 0 or limit <= 0:
        raise HTTPException(status_code=400, detail="skip must be >= 0 and limit must be > 0")
    try:
        rows = db_list_events(skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")
    try:
        return [Event(**r) for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Response mapping error: {e}")