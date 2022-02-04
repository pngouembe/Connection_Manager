from dataclasses import dataclass, field
from socket import socket
from threading import Event
from typing import Set

from sdataclasses.uniquedataclass import UniqueSerializableDataclass


@dataclass(frozen=True)
class UserInfo(UniqueSerializableDataclass):
    """
    UserInfo dataclass allowing the storage of user information
    and the exchange of it between users
    """

    # list of the required fields
    name: str = field(hash=True)
    address: str = field(hash=True)
    resource: int = field(default=0, hash=True)


@dataclass(unsafe_hash=True)
class User:
    info: UserInfo
    socket: socket  # TODO: field(hash=False) not working, need to investigate
    wait_for_reconnection: Event = field(default_factory=Event, hash=False)
    requested_resources: Set = field(default_factory=set, hash=False)

    def __post_init__(self):
        self.wait_for_reconnection.clear()

    def __repr__(self) -> str:
        return self.info.__repr__()

    def __del__(self):
        self.socket.close()
        del self.info
        del self.wait_for_reconnection
        del self.requested_resources
