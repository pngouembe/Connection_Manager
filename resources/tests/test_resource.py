import unittest
from resources import resource, resource_from_dict, missingRequiredFields
from users import user
from dataclasses import asdict, field


class TestResourceMethods(unittest.TestCase):

    def setUp(self):
        self.resource = resource(
            name="test_resource",
            id=0)
        self.resource_user = user(name="test user", ip_addr="127.0.0.1")

    def tearDown(self):
        user.users_ids = []

    def test_update(self):
        self.resource2 = resource(name="resource2", id=1)
        self.resource2.update(self.resource.serialize())
        self.assertEqual(self.resource, self.resource2)

    def test_resource_from_dict(self):
        self.resource_dict = {
            "foo": "bar",
            "a": 10,
            "name": "test_resource3",
            "id": 0,
            "user_list": [],
            "is_usable": True
            }
        self.resource3 = resource_from_dict(self.resource_dict)
        self.assertEqual(asdict(self.resource3), self.resource_dict)

        # testing required fields
        self.resource_dict = {
            "foo": "bar",
            "id": 0,
            "a": 10}
        with self.assertRaises(missingRequiredFields):
            self.resource3 = resource_from_dict(self.resource_dict)

        with self.assertRaises(missingRequiredFields):
            self.resource3 = resource_from_dict({})

    def test_str_representation(self):
        self.assertEqual(str(
            self.resource),
            "resource(name='test_resource', id=0, user_list=[], is_usable=True)")

    def test_add_user(self):
        self.resource.add_user(self.resource_user)
        self.assertEqual(str(
            self.resource),
            "resource(name='test_resource', id=0, user_list=[user(name='test user', ip_addr='127.0.0.1', resource=0)], is_usable=True)")

    def test_remove_user(self):
        self.resource.add_user(self.resource_user)
        self.resource.remove_user(self.resource_user)
        self.assertEqual(str(
            self.resource),
            "resource(name='test_resource', id=0, user_list=[], is_usable=True)")

if __name__ == '__main__':
    unittest.main()
