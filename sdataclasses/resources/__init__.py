from dataclasses import dataclass, field

from sdataclasses import SerializableDataclass


@dataclass(eq=False)
class Resource(SerializableDataclass):
    """
    resource dataclass allowing the storage of resource information
    and the exchange of it between users
    """

    # list of the required fields
    name: str = field()
    id: int = field()
    user_list: list = field(default_factory=list, compare=False)
    is_usable: bool = field(default=True)

    def __post_init__(self) -> None:
        self.is_free = True

    def add_user(self, user) -> None:
        """
        Add user given in argument to the resource user waiting list
        """
        self.user_list.append(user)
        self.is_free = False

    def remove_user(self, user) -> None:
        """
        Remove the user given in argument from the resource user waiting list
        """
        self.user_list.remove(user)
        if not self.user_list:
            self.is_free = True
