from dataclasses import dataclass, field
from typing import List, Union

from mydataclasses.sdataclasses import SerializableDataclass
from users import User, UserInfo


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
    user_list: List[UserInfo] = field(default_factory=list, hash=False, repr=False)
    is_usable: bool = field(default=True, hash=False)

    def __post_init__(self) -> None:
        self.is_free = True

    def add_user(self, user: Union[User, UserInfo]) -> None:
        """
        Add user given in argument to the resource user waiting list
        """
        if isinstance(user, User):
            user = user.info
        if user not in self.user_list:
            self.user_list.append(user)
            self.is_free = False

    def remove_user(self, user: Union[User, UserInfo]) -> None:
        """
        Remove the user given in argument from the resource user waiting list
        """
        if isinstance(user, User):
            user = user.info
        try:
            self.user_list.remove(user)
        except ValueError:
            pass
        if not self.user_list:
            self.is_free = True
