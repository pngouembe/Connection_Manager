# -*- coding: utf-8 -*-
"""sdataclasses module
This is a modified version of the dataclass class adding the following
features:
- Creating dataclass from dict
- Serializing dataclass into a string using a serializer
- Deserializing a string into a dataclass object
- Updating dataclasses from a dict

"""
from dataclasses import _MISSING_TYPE, asdict, dataclass, field, make_dataclass

from serializers import SerializerFactory, SerializerType


class MissingRequiredFields(Exception):
    def __init__(self, *args) -> None:
        self.message = "Missing the following fields: {}".format(*args)
        super().__init__(self.message)


class UnknownFieldError(Exception):
    pass


_serializer = SerializerFactory(SerializerType.YAML)


@dataclass
class DictDataclass:
    """
    This dataclass can be built from a dict by unpacking it (DictDataclass(**dict)).
    If the dict contains keys that are not part of the existing fields of the class,
    a new dataclass with those new fields will be generated.
    This allows to have dataclasses with predefined required fields and any
    user defined fields
    """

    """
    Contains the class already generated as imbricated dict
    {
        input_fields : {
            cls.__name__: class
        }
    }
    """
    _classes = {}

    def __new__(cls, *args, **kwargs):
        cls.exp_fields = [k for k in cls.__dataclass_fields__.keys()]

        # get required fields among expected fields
        cls.req_fields = []
        for k in cls.exp_fields:
            f = cls.__dataclass_fields__[k]
            inst_check = (isinstance(f.default, _MISSING_TYPE),
                          isinstance(f.default_factory, _MISSING_TYPE))
            if inst_check == (True, True):
                cls.req_fields.append(k)

        if not kwargs and not args:
            raise MissingRequiredFields(cls.req_fields)

        input_keys = []
        if kwargs:
            input_keys = kwargs.keys()

        # Adding positional args in the dict
        if args:
            if len(args) > len(cls.exp_fields):
                msg = "Too many positional argument, expecting {} got {}"
                msg = msg.format(len(cls.exp_fields), len(args))
                raise ValueError(msg)
            for i, arg in enumerate(args):
                if cls.exp_fields[i] in input_keys:
                    msg = "Two arguments for the {} field (positional and named argument)"
                    msg = msg.format(
                        cls.exp_fields[i])
                    raise ValueError(msg)
                else:
                    kwargs[cls.exp_fields[i]] = arg
            input_keys = kwargs.keys()

        missing_fields = set(cls.req_fields) - set(input_keys)
        if missing_fields:
            raise MissingRequiredFields(missing_fields)

        # Check if the generation of a new class due to extra fields is needed
        extra_fields = set(input_keys) - set(cls.exp_fields)
        if not extra_fields:
            return super().__new__(cls)
        else:
            input_fields = frozenset([(k, type(v))
                                     for k, v in kwargs.items()])

            # checking if the class have already been generated
            if input_fields in cls._classes.keys():
                if cls.__name__ in cls._classes[input_fields].keys():
                    new_cls = cls._classes[input_fields][cls.__name__]
                    return new_cls(**kwargs)
            else:
                cls._classes[input_fields] = {}

            # Extract the field list from the args given to the constructor
            # if the fields already exists, keep their characteristics
            field_list = []
            for k, v in kwargs.items():
                t = type(v)
                if k in cls.exp_fields:
                    field_flags = {
                        'init': cls.__dataclass_fields__[k].init,
                        'repr': cls.__dataclass_fields__[k].repr,
                        'hash': cls.__dataclass_fields__[k].hash,
                        'compare': cls.__dataclass_fields__[k].compare
                    }
                else:
                    field_flags = {
                        'hash': False,
                        'compare': False
                    }
                # Check if field content is immutable
                if not isinstance(v, (list, dict, set)):
                    f = (k, t, field(default=v, **field_flags))
                else:
                    f = (k, t, field(default_factory=t, **field_flags))
                field_list.append(f)

            # Extract dataclass params from the class used as the base for generation
            class_flags = {k: getattr(cls.__dataclass_params__, k)
                           for k in cls.__dataclass_params__.__slots__}

            # create the new dataclass with the appropriate fields
            new_cls = make_dataclass(
                cls.__name__, field_list, bases=(cls, *cls.__bases__), **class_flags)
            # Saving generated class for future use
            cls._classes[input_fields].update({cls.__name__: new_cls})
            return new_cls(**kwargs)


@dataclass
class SerializableDataclass(DictDataclass):
    """
    This dataclass can be initialized using a dict by calling the constructor
    passing your dict as the kwargs named argument
    """

    def serialize(self, **kwargs) -> str:
        """
        This function allow to serialize the dataclass.
        Additional information can be passed using kwargs argument
        """
        return _serializer.serialize(dict=asdict(self), **kwargs)

    @classmethod
    def deserialize(cls, str: str, **kwargs):
        dict = _serializer.deserialize(str, **kwargs)
        return cls(**dict)

    def update(self, dict: dict = None, **kwargs) -> None:
        if not dict:
            dict = {}
        if kwargs:
            dict.update(kwargs)

        for k, v in dict.items():
            if k in self.__dataclass_fields__.keys():
                setattr(self, k, v)
            else:
                raise UnknownFieldError(
                    "Trying to update {} which is not a field of this dataclass".format(k))
