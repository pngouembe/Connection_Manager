from dataclasses import dataclass, field
from typing import List

from mydataclasses.resources import Resource
from mydataclasses.sdataclasses import SerializableDataclass


@dataclass
class Server(SerializableDataclass):
    """
    Server dataclass allowing the storage of server information
    and the exchange of it between users
    """

    # list of the required fields
    address: str = field(hash=True)
    port: int = field(hash=True)
    resources: List[Resource] = field(hash=False, compare=False)
    resource_free_delay: float = field(default=0, hash=False, compare=False)
    socket_timeout: float = field(default=1, hash=False, compare=False)
