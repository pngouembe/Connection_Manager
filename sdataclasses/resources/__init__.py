from dataclasses import dataclass, field
from typing import List

from sdataclasses import SerializableDataclass
from users import User


@dataclass(unsafe_hash=True, eq=False)
class Resource(SerializableDataclass):
    """
    resource dataclass allowing the storage of resource information
    and the exchange of it between users
    """

    # list of the required fields
    name: str = field()
    id: int = field()

    # TODO: Refactor dataclasses like done with user
    user_list: List[User] = field(default_factory=list, hash=False)
    is_usable: bool = field(default=True, hash=False)

    def __post_init__(self) -> None:
        self.is_free = True

    def add_user(self, user: User) -> None:
        """
        Add user given in argument to the resource user waiting list
        """
        user_info_list = [u.info for u in self.user_list]
        if user.info not in user_info_list:
            self.user_list.append(user)
            self.is_free = False

    def remove_user(self, user: User) -> None:
        """
        Remove the user given in argument from the resource user waiting list
        """
        try:
            self.user_list.remove(user)
        except ValueError:
            pass
        if not self.user_list:
            self.is_free = True
