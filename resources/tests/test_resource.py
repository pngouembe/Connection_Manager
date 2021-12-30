import unittest
from resources import resource, create_resource
from users import user
from dataclasses import asdict, field


class TestResourceMethods(unittest.TestCase):

    def setUp(self):
        self.resource = resource(
            name="test_resource",
            id=0)

    def test_update(self):
        self.resource2 = resource(name="resource2", id=1)
        self.resource2.update(self.resource.serialize())
        self.assertEqual(self.resource, self.resource2)

    def test_create_resource(self):
        self.resource_dict = {
            "name": "test_resource3",
            "foo": "bar",
            "id": 0,
            "a": 10,
            "user_list": []}
        self.resource3 = create_resource(self.resource_dict)
        self.assertEqual(asdict(self.resource3), self.resource_dict)

        # testing required fields
        self.resource_dict = {
            "foo": "bar",
            "id": 0,
            "a": 10}
        with self.assertRaises(TypeError):
            self.resource3 = create_resource(self.resource_dict)

        with self.assertRaises(TypeError):
            self.resource3 = create_resource({})


if __name__ == '__main__':
    unittest.main()
