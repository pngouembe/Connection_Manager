# -*- coding: utf-8 -*-
"""serializer module
This module allow an abstraction of the tool used to serialize the data.
It provide a serializer factory class and serialize and deserialize functions.
"""
from enum import Enum
from .serializer import Serializer
from .yaml import YamlSerializer


class SerializerType(Enum):
    YAML = 0


def SerializerFactory(type: SerializerType) -> Serializer:
    if type == SerializerType.YAML:
        return YamlSerializer()
