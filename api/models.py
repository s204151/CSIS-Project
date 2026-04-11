from pydantic import BaseModel
from ipaddress import IPv4Address

from sqlalchemy import create_engine

from enums.enums import UserEnum, EventTypeEnum, SeverityEnum
from datetime import datetime


class EventSchema(BaseModel):
    event_type: EventTypeEnum
    user_type: UserEnum
    ip_address: IPv4Address


class EventIdSchema(EventSchema):
    id: int


class AlertSchema(BaseModel):
    id: int
    created_at: datetime
    alert_type: EventTypeEnum
    severity: SeverityEnum
    ip_address: IPv4Address
