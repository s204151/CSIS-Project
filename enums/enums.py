from enum import Enum

class UserEnum(str, Enum):
    admin = 'admin'
    member = 'member'

class EventTypeEnum(str, Enum):
    login_success = 'login_success'
    login_failed = 'login_failed'