from enum import Enum, auto


class Header(Enum):
    INVALID = 0
    END_CONNECTION = auto()
    INTRODUCE = auto()
    CONNECTION_READY = auto()
    WAIT = auto()
    FREE_RESOURCE = auto()
    TIMEOUT = auto()
    STATUS = auto()
    PING = auto()
    REQUEST_RESOURCE = auto()
    RELEASE_RESOURCE = auto()
