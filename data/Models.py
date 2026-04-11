from sqlalchemy import Integer, String, Enum, DateTime, ForeignKey
from sqlalchemy.orm import mapped_column, DeclarativeBase
from enums.enums import UserEnum, EventTypeEnum, SeverityEnum, AlertTypeEnum


# declarative base class
class Base(DeclarativeBase):
    pass


class Event(Base):
    __tablename__ = 'events'

    id = mapped_column(Integer, primary_key=True)
    event_type = mapped_column(Enum(EventTypeEnum, name="event_type_enum"))
    user_type = mapped_column(Enum(UserEnum, name="user_enum"))
    ip_address = mapped_column(String)
    datetime = mapped_column(DateTime)


class Alert(Base):
    __tablename__ = 'alerts'

    id = mapped_column(Integer, primary_key=True)
    alert_type = mapped_column(Enum(AlertTypeEnum, name="alert_type_enum"))
    severity = mapped_column(Enum(SeverityEnum, name="severity_type_enum"))
    ip_address = mapped_column(String)
    created_at = mapped_column(DateTime)
    event_id = mapped_column(Integer, ForeignKey("events.id"), nullable=False)
