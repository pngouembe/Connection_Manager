import unittest
from dataclasses import FrozenInstanceError, asdict

from parameterized import parameterized
from mydataclasses.resources import Resource
from mydataclasses.sdataclasses import (MissingRequiredFields,
                                        SerializableDataclass,
                                        UnknownFieldError)
from mydataclasses.servers import Server
from mydataclasses.uniquedataclass import (DuplicateError,
                                           UniqueSerializableDataclass)
from users import UserInfo


class TestSDataclassMethods(unittest.TestCase):
    valid_dict = {
        # common required fields
        'name': 'test',
        # Resource required fields
        'user_list': [],
        'is_usable': True,
        'id': 0,
        # Server required fields
        'address': '127.0.0.1',
        'port': 65432,
        'resources': [Resource(name="R0", id=0)],
        # extra_info
        'extra_field': 'testing extra field support'
    }

    update_dict = {
        'name': 'updating required fields',
        'extra_field': 'and extra ones'
    }

    invalid_update_dict = {
        'name': 'updating required fields',
        'extra_field': 'and extra ones',
        'inexistent': 'trying with inexistent ones'
    }

    immutable_valid_dict = {
        # common required fields
        'name': 'test',
        # User required fields
        'address': '127.0.0.1',
        'port': 65432,
        'resource': 0,
        # extra_info
        'comment': 'test comment'
    }

    invalid_dict = {}

    # parameter lists
    sdc_list = [
        ("Resource", Resource, valid_dict, invalid_dict),
        ("Server", Server, valid_dict, invalid_dict)
    ]

    usdc_list = [
        ("UserInfo", UserInfo, immutable_valid_dict, invalid_dict)
    ]

    all_list = sdc_list + usdc_list

    @parameterized.expand(all_list)
    def test_dataclass_from_dict(self, name, cls, valid_dict, invalid_dict):
        t: SerializableDataclass = cls(**valid_dict)
        for k, v in valid_dict.items():
            self.assertEqual(v, getattr(t, k))
        with self.assertRaises(MissingRequiredFields):
            t = cls(**invalid_dict)
        del t

    @parameterized.expand(all_list)
    def test_dataclass_from_args(self, name, cls, valid_dict, invalid_dict):
        arg_list = []
        for k in cls.__dataclass_fields__.keys():
            if k in valid_dict.keys():
                arg_list.append(valid_dict[k])

        t: SerializableDataclass = cls(*arg_list)

        with self.assertRaises(MissingRequiredFields):
            cls(*invalid_dict.values())

        del t

    @parameterized.expand(all_list)
    def test_dataclass_update(self, name, cls: SerializableDataclass, valid_dict: dict, invalid_dict: dict):
        t: SerializableDataclass = cls(**valid_dict)
        valid_dict_copy = valid_dict.copy()
        valid_dict_copy.update(self.update_dict)
        t2: SerializableDataclass = cls(**valid_dict_copy)
        if isinstance(t, UniqueSerializableDataclass):
            with self.assertRaises(FrozenInstanceError):
                t.update(asdict(t2))
        else:
            t.update(asdict(t2))
            self.assertEqual(t, t2)
            with self.assertRaises(UnknownFieldError):
                t2.update(**self.invalid_update_dict)
        del t
        del t2

    @parameterized.expand(usdc_list)
    def test_dataclass_unique(self, name, cls: SerializableDataclass, valid_dict: dict, invalid_dict: dict):
        t: SerializableDataclass = cls(**valid_dict)
        with self.assertRaises(FrozenInstanceError):
            t.name = "Trying to set attribute"
        with self.assertRaises(DuplicateError):
            cls(**valid_dict)
        del t

    @parameterized.expand(all_list)
    def test_dataclass_serialize_deserialize(self, name, cls: SerializableDataclass, valid_dict: dict, invalid_dict: dict):
        t: SerializableDataclass = cls(**valid_dict)
        s = t.serialize()
        self.assertIsInstance(s, str)
        del t
        t2 = cls.deserialize(s)
        self.assertIsInstance(t2, cls)
        del t2


if __name__ == '__main__':
    unittest.main()
