from dataclasses import dataclass, field

from sdataclasses.uniquedataclass import UniqueSerializableDataclass


@dataclass(frozen=True)
class User(UniqueSerializableDataclass):
    """
    User dataclass allowing the storage of user information
    and the exchange of it between users
    """

    # list of the required fields
    name: str = field(hash=True)
    address: str = field(hash=True)
    resource: int = field(default=0, hash=True)
