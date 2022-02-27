from dataclasses import dataclass, field
from socket import socket
from threading import Event
from typing import List, Set

from mydataclasses.sdataclasses import SerializableDataclass
from mydataclasses.uniquedataclass import UniqueSerializableDataclass


@dataclass(frozen=True)
class UserInfo(UniqueSerializableDataclass):
    """
    UserInfo dataclass allowing the storage of user information
    and the exchange of it between users
    """

    # list of the required fields
    name: str = field(hash=True)
    address: str = field(hash=True)
    port: int = field(hash=True)


@dataclass(unsafe_hash=True)
class User:
    info: UserInfo
    socket: socket  # TODO: field(hash=False) not working, need to investigate
    # user_event used to:
    # - notify reconnection on server side
    user_event: Event = field(default_factory=Event, hash=False)
    waiting_for_reconnection: bool = field(default=False, hash=False)
    accessible_resources_list: List = field(default_factory=list, hash=False)
    requested_resources: Set = field(default_factory=set, hash=False)
    current_resource: int = field(default=None)
    recovery_time: float = field(default=0, hash=False)

    def __repr__(self) -> str:
        return self.info.__repr__()

    def __del__(self):
        del self.info
        self.socket.close()
        del self.user_event
        del self.requested_resources
