from pydantic import BaseModel
from ipaddress import IPv4Address
from enums.enums import UserEnum, EventTypeEnum

class EventSchema(BaseModel):
    event_type: EventTypeEnum
    user_type: UserEnum
    ip_address: IPv4Address

class EventIdSchema(EventSchema):
    id: int