from fastapi import FastAPI, HTTPException
from typing import List
from http import HTTPStatus
from data.db_connector import add_event as db_create_event, get_event as db_get_event, list_events as db_list_events, get_alert as db_get_alert, list_alerts as db_list_alerts
from api.models import EventSchema, EventIdSchema, AlertSchema
from src.detection_jobs import enqueue


app = FastAPI()


@app.get("/")
def root():
    """ Health check."""
    response = {
        "message": HTTPStatus.OK.phrase,
        "status-code": HTTPStatus.OK,
    }
    return response


@app.post("/events", response_model=EventIdSchema, status_code=201)
def create_event(event_in: EventSchema):
    """Create a new event and persist to Postgres."""
    try:
        created = db_create_event(event_type=event_in.event_type,
                                  user_type=event_in.user_type,
                                  ip_address=str(event_in.ip_address),
                                  datetime=event_in.datetime)
    except Exception as e:
        # hide raw DB details but return a helpful error
        raise HTTPException(status_code=500, detail=f"DB error: {e}")

    if not created:
        raise HTTPException(status_code=500, detail="Failed to create event")

    try:
        result = EventIdSchema(**created)
        # enqueue detection job but don't let worker failures break the API response
        try:
            enqueue(result.id)
        except Exception:
            # log could be added here; swallow to keep API stable
            pass
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Response mapping error: {e}")


@app.get("/events/{event_id}", response_model=EventIdSchema)
def get_event(event_id: int):
    """Get event by id from Postgres."""
    try:
        row = db_get_event(event_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")

    if not row:
        raise HTTPException(status_code=404, detail="Event not found")

    try:
        return EventIdSchema(**row)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Response mapping error: {e}")


@app.get("/events", response_model=List[EventIdSchema])
def list_events(skip: int = 0, limit: int = 100):
    """List events with optional pagination via skip & limit."""
    if skip < 0 or limit <= 0:
        raise HTTPException(status_code=400, detail="skip must be >= 0 and limit must be > 0")

    try:
        rows = db_list_events(skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")

    try:
        return [EventIdSchema(**r) for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Response mapping error: {e}")


# New: Alerts endpoints
@app.get("/alerts/{alert_id}", response_model=AlertSchema)
def get_alert(alert_id: int):
    """Get alert by id from Postgres."""
    try:
        row = db_get_alert(alert_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")

    if not row:
        raise HTTPException(status_code=404, detail="Alert not found")

    try:
        return AlertSchema(**row)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Response mapping error: {e}")


@app.get("/alerts", response_model=List[AlertSchema])
def list_alerts(skip: int = 0, limit: int = 100):
    """List alerts with optional pagination via skip & limit."""
    if skip < 0 or limit <= 0:
        raise HTTPException(status_code=400, detail="skip must be >= 0 and limit must be > 0")

    try:
        rows = db_list_alerts(skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")

    try:
        return [AlertSchema(**r) for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Response mapping error: {e}")
