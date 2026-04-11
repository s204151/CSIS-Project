from enum import Enum

class UserEnum(str, Enum):
    admin = 'admin'
    member = 'member'

class EventTypeEnum(str, Enum):
    login_success = 'login_success'
    login_failed = 'login_failed'

class SeverityEnum(str, Enum):
    low = 'low'
    mid = 'mid'
    high = 'high'

class AlertTypeEnum(str, Enum):
    brute_force_detected = 'brute_force_detected'
    suspicious = 'suspicious'