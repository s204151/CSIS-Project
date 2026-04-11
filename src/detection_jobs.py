import dramatiq
from data.db_connector import get_recent_events, get_event, create_alert
from enums.enums import EventTypeEnum, AlertTypeEnum, SeverityEnum


def brute_force_detected(recent_events: list, threshold) -> bool:
    # This is just an example. In a real implementation, it would probably be more complex
    failed_attempts = sum(1 for evt in recent_events if evt["event_type"] == EventTypeEnum.login_failed)
    if failed_attempts >= threshold:
        return True
    return False


def suspicious_login_detected(recent_events: list, failed_threshold: int = 5) -> bool:
    """
        Detect suspicious behavior: a successful login that follows many consecutive failed logins.
        This is just an example. In a real implementation, it would probably be more complex
    """
    if not recent_events:
        return False

    for i, evt in enumerate(recent_events):
        if evt["event_type"] == EventTypeEnum.login_success:
            # count consecutive failed events before this one
            count = 0
            j = i + 1
            while j < len(recent_events) and recent_events[j]["event_type"] == EventTypeEnum.login_failed:
                count += 1
                j += 1
            if count >= failed_threshold:
                return True
    return False


@dramatiq.actor
def process_event(event_id: int):
    print(f"Processing event {event_id}")

    event = get_event(event_id)
    if not event:
        print(f"Event {event_id} not found")
        return

    recent_events = get_recent_events(last_minutes=1000, limit=10, ip_address=event["ip_address"])

    if brute_force_detected(recent_events, 5):
        print(f"Brute force detected for IP {event['ip_address']}")
        create_alert(alert_type=AlertTypeEnum.brute_force_detected,
                     severity=SeverityEnum.high,
                     ip_address=event["ip_address"],
                     event_id=event_id)

    if suspicious_login_detected(recent_events):
        print(f"Suspicious login pattern detected for IP {event['ip_address']}")
        create_alert(alert_type=AlertTypeEnum.suspicious,
                     severity=SeverityEnum.mid,
                     ip_address=event["ip_address"],
                     event_id=event_id)


def enqueue(event_id: int):
    """Enqueue a detection job for the given event id."""
    process_event.send(event_id)
