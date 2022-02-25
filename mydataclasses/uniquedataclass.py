from dataclasses import FrozenInstanceError, dataclass

from mydataclasses.sdataclasses import SerializableDataclass


class DuplicateError(Exception):
    pass


_ids = []


@dataclass(frozen=True)
class BaseFrozenDataclass:
    pass

@dataclass(frozen=True)
class UniqueSerializableDataclass(SerializableDataclass, BaseFrozenDataclass):
    """
    This data class is a frozen version of the SerializableDataclass.
    It also only forbids duplicate instances by raising an error
    """

    _id = None
    _is_duplicate = False

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, **kwargs)

    def __del__(self):
        if self._is_duplicate == False and self._id in _ids:
            _ids.remove(self._id)

    def __post_init__(self) -> None:
        """
        The post init method is used to check the unicity of the dataclass.
        it raises an error if the user is a duplicate
        """
        if not self._id:
            object.__setattr__(self, "_id", self.__hash__())

            if self._id not in _ids:
                _ids.append(self._id)
            else:
                object.__setattr__(self, "_is_duplicate", True)
                raise DuplicateError(
                    "Duplication of UniqueSerializableDataclass instances is not allowed")

    def update(self, dict: dict = None, **kwargs) -> None:
        raise FrozenInstanceError(
            "UniqueSerializableDataclass attribute cannot be modified")
