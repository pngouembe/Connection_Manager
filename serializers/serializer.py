from enum import Enum
from serializers.yaml import YamlSerializer
from serializers.template import Serializer


class SerializerType(Enum):
    YAML = 0


def SerializerFactory(type: SerializerType) -> Serializer:
    if type == SerializerType.YAML:
        return YamlSerializer()
