from abc import abstractmethod


class Serializer:
    @abstractmethod
    def serialize(self, dict: dict, **kwargs) -> str:
        """
        Function used to convert a dict into a str.
        additional elements can be added using the kwargs argument
        """
        pass

    @abstractmethod
    def deserialize(self, str: str, **kwargs) -> dict:
        """
        Function used to convert a str into a dict.
        additional elements can be added using the kwargs argument
        """
        pass
