from fastapi import FastAPI, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, field_validator
from ipaddress import IPv4Address
from http import HTTPStatus
from enum import Enum, IntEnum
app = FastAPI()

class UserEnum(str, Enum):
    admin = 'admin'
    member = 'member'

class LoginTypeEnum(str, Enum):
    failure = 'failure'
    success = 'success'

class EventCreate(BaseModel):
    login_type: LoginTypeEnum
    user: UserEnum
    ip_address: IPv4Address
    success: bool

class Event(EventCreate):
    id: int

# In-memory storage for events
_events: Dict[int, Event] = {}
_next_id = 1

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
    """Create a new event. Server assigns an integer id."""
    global _next_id
    event = Event(id=_next_id, **event_in.model_dump())
    _events[_next_id] = event
    _next_id += 1
    return event


@app.get("/events/{event_id}", response_model=Event)
def get_event(event_id: int):
    """Get event by id."""
    event = _events.get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@app.get("/events", response_model=List[Event])
def list_events(skip: int = 0, limit: int = 100):
    """List events with optional pagination via skip & limit."""
    events = list(_events.values())
    # simple slice-based pagination
    return events[skip: skip + limit]