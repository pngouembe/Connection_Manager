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
