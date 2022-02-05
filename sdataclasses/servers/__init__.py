from typing import Dict, List
from dataclasses import dataclass, field

from sdataclasses import SerializableDataclass


@dataclass
class Server(SerializableDataclass):
    """
    Server dataclass allowing the storage of server information
    and the exchange of it between users
    """

    # list of the required fields
    address: str = field(hash=True)
    port: int = field(hash=True)
    resources: List[Dict] = field(hash=False, compare=False)
    resource_free_delay: float = field(default=0, hash=False, compare=False)
