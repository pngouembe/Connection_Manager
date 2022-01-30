from typing import List
from dataclasses import dataclass, field

from sdataclasses import SerializableDataclass
from sdataclasses.uniquedataclass.users import User


@dataclass(unsafe_hash=True)
class Resource(SerializableDataclass):
    """
    resource dataclass allowing the storage of resource information
    and the exchange of it between users
    """

    # list of the required fields
    name: str = field()
    id: int = field()
    user_list: List[User] = field(
        default_factory=list, compare=False, hash=False)
    is_usable: bool = field(default=True, compare=False, hash=False)

    def __post_init__(self) -> None:
        self.is_free = True

    def add_user(self, user) -> None:
        """
        Add user given in argument to the resource user waiting list
        """
        if user not in self.user_list:
            self.user_list.append(user)
            self.is_free = False

    def remove_user(self, user) -> None:
        """
        Remove the user given in argument from the resource user waiting list
        """
        try:
            self.user_list.remove(user)
        except ValueError:
            pass
        if not self.user_list:
            self.is_free = True
