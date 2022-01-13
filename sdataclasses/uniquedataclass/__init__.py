from dataclasses import FrozenInstanceError, dataclass

from sdataclasses import SerializableDataclass


class DuplicateError(Exception):
    pass


_ids = []


@dataclass(frozen=True)
class UniqueSerializableDataclass(SerializableDataclass):
    """
    This data class is a frozen version of the SerializableDataclass.
    It also only forbids duplicate instances by raising an error
    """

    id = None

    def __new__(cls, *args, input_dict: dict = None, **kwargs):
        return super().__new__(cls, *args, input_dict, **kwargs)

    def __post_init__(self) -> None:
        """
        The post init method is used to check the unicity of the dataclass.
        it raises an error if the user is a duplicate
        """
        if not self.id:
            object.__setattr__(self, "id", self.__hash__())
            if self.id not in _ids:
                _ids.append(self.id)
            else:
                raise DuplicateError(
                    "Duplication of UniqueSerializableDataclass instances is not allowed")
        else:
            pass

    def update(self, dict: dict = None, **kwargs) -> None:
        raise FrozenInstanceError(
            "UniqueSerializableDataclass attribute cannot be modified")
