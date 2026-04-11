import os
import sys
# ensure project root is on sys.path for imports like `api.api`
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient
from api.api import app

client = TestClient(app)

VALID_PAYLOAD = {
    "event_type": "login_success",
    "user_type": "member",
    "ip_address": "127.0.0.1",
    "datetime": "2026-04-11T00:00:00"
}


def test_root_health_check():
    r = client.get("/")
    assert r.status_code == 200
    assert "message" in r.json() and "status-code" in r.json()


def test_create_event_success(monkeypatch):
    def fake_db_create_event(event_type, user_type, ip_address):
        return {"id": 1, "event_type": event_type, "user_type": user_type, "ip_address": ip_address, "datetime": "2026-04-11T00:00:00"}

    monkeypatch.setattr("api.api.db_create_event", fake_db_create_event)

    r = client.post("/events", json=VALID_PAYLOAD)
    assert r.status_code == 201
    body = r.json()
    assert body["id"] == 1
    assert body["event_type"] == VALID_PAYLOAD["event_type"]
    assert body["user_type"] == VALID_PAYLOAD["user_type"]
    assert body["ip_address"] == VALID_PAYLOAD["ip_address"]


def test_create_event_db_exception(monkeypatch):
    def raising(event_type, user_type, ip_address):
        raise Exception("boom")

    monkeypatch.setattr("api.api.db_create_event", raising)

    r = client.post("/events", json=VALID_PAYLOAD)
    assert r.status_code == 500
    assert "DB error" in r.json().get("detail", "")


def test_create_event_failed_create(monkeypatch):
    def returns_false(event_type, user_type, ip_address):
        return None

    monkeypatch.setattr("api.api.db_create_event", returns_false)

    r = client.post("/events", json=VALID_PAYLOAD)
    assert r.status_code == 500
    assert r.json().get("detail") == "Failed to create event"


def test_create_event_validation_error():
    bad = VALID_PAYLOAD.copy()
    bad["ip_address"] = "not-an-ip"
    r = client.post("/events", json=bad)
    assert r.status_code == 422


def test_get_event_success(monkeypatch):
    def fake_get(event_id):
        return {"id": event_id, "event_type": "login_success", "user_type": "member", "ip_address": "127.0.0.1", "datetime": "2026-04-11T00:00:00"}

    monkeypatch.setattr("api.api.db_get_event", fake_get)

    r = client.get("/events/5")
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == 5


def test_get_event_not_found(monkeypatch):
    def fake_get(event_id):
        return None

    monkeypatch.setattr("api.api.db_get_event", fake_get)

    r = client.get("/events/9999")
    assert r.status_code == 404


def test_get_event_db_exception(monkeypatch):
    def raising(event_id):
        raise Exception("ohno")

    monkeypatch.setattr("api.api.db_get_event", raising)

    r = client.get("/events/2")
    assert r.status_code == 500
    assert "DB error" in r.json().get("detail", "")


def test_list_events_success(monkeypatch):
    def fake_list(skip, limit):
        return [
            {"id": 1, "event_type": "login_success", "user_type": "member", "ip_address": "127.0.0.1", "datetime": "2026-04-11T00:00:00"},
            {"id": 2, "event_type": "login_failed", "user_type": "admin", "ip_address": "10.0.0.2", "datetime": "2026-04-11T00:00:00"},
        ]

    monkeypatch.setattr("api.api.db_list_events", fake_list)

    r = client.get("/events")
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, list)
    assert len(body) == 2


def test_list_events_bad_params():
    r = client.get("/events?skip=-1&limit=0")
    assert r.status_code == 400


def test_list_events_db_exception(monkeypatch):
    def raising(skip, limit):
        raise Exception("err")

    monkeypatch.setattr("api.api.db_list_events", raising)

    r = client.get("/events")
    assert r.status_code == 500
    assert "DB error" in r.json().get("detail", "")


def test_get_alert_success(monkeypatch):
    def fake_get(alert_id):
        return {"id": alert_id, "alert_type": "brute_force_detected", "severity": "high", "ip_address": "10.0.0.5", "created_at": "2026-04-11T00:00:00", "event_id": 1}

    monkeypatch.setattr("api.api.db_get_alert", fake_get)

    r = client.get("/alerts/7")
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == 7


def test_get_alert_not_found(monkeypatch):
    def fake_get(alert_id):
        return None

    monkeypatch.setattr("api.api.db_get_alert", fake_get)

    r = client.get("/alerts/9999")
    assert r.status_code == 404


def test_get_alert_db_exception(monkeypatch):
    def raising(alert_id):
        raise Exception("boom")

    monkeypatch.setattr("api.api.db_get_alert", raising)

    r = client.get("/alerts/3")
    assert r.status_code == 500
    assert "DB error" in r.json().get("detail", "")


def test_list_alerts_success(monkeypatch):
    def fake_list(skip, limit):
        return [
            {"id": 1, "alert_type": "brute_force_detected", "severity": "mid", "ip_address": "127.0.0.1", "created_at": "2026-04-11T00:00:00", "event_id": 1},
            {"id": 2, "alert_type": "suspicious", "severity": "low", "ip_address": "10.0.0.2", "created_at": "2026-04-11T01:00:00", "event_id": 1},
        ]

    monkeypatch.setattr("api.api.db_list_alerts", fake_list)

    r = client.get("/alerts")
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, list)
    assert len(body) == 2


def test_list_alerts_bad_params():
    r = client.get("/alerts?skip=-1&limit=0")
    assert r.status_code == 400


def test_list_alerts_db_exception(monkeypatch):
    def raising(skip, limit):
        raise Exception("err")

    monkeypatch.setattr("api.api.db_list_alerts", raising)

    r = client.get("/alerts")
    assert r.status_code == 500
    assert "DB error" in r.json().get("detail", "")
