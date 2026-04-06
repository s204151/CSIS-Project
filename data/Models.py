from sqlalchemy import Integer, String, Enum
from sqlalchemy.orm import mapped_column, DeclarativeBase
from enums.enums import UserEnum, EventTypeEnum


# declarative base class
class Base(DeclarativeBase):
    pass


class Event(Base):
    __tablename__ = 'events'

    id = mapped_column(Integer, primary_key=True)
    event_type = mapped_column(Enum(EventTypeEnum.login_success, EventTypeEnum.login_failed, name="event_type_enum"))
    user_type = mapped_column(Enum(UserEnum.admin, UserEnum.member, name="user_enum"))
    ip_address = mapped_column(String)
