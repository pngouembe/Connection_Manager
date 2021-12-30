import unittest
from users import user, create_user, userDuplicateError
from dataclasses import asdict, FrozenInstanceError


class TestUserMethods(unittest.TestCase):

    def setUp(self):
        self.user = user(name="test_user", ip_addr="127.0.0.1", resource=0)

    def tearDown(self):
        user.users_ids = []

    def test_update(self):
        self.user2 = user(name="test_user2", ip_addr="127.0.0.1", resource=0)
        self.user2.update(self.user.serialize())
        self.assertEqual(self.user, self.user2)

    def test_create_user(self):
        self.user_dict = {
            "name": "test_user3",
            "ip_addr": "127.0.0.1",
            "resource": 0,
            "foo": "bar",
            "id": 0,
            "a": 10}
        self.user3 = create_user(self.user_dict)
        self.assertEqual(asdict(self.user3), self.user_dict)

        # checking that the class is read-only
        with self.assertRaises(FrozenInstanceError):
            self.user3.resource = 1

        # testing required fields
        self.user_dict = {
            "ip_addr": "127.0.0.1",
            "foo": "bar",
            "id": 0,
            "a": 10}
        with self.assertRaises(TypeError):
            self.user3 = create_user(self.user_dict)

        with self.assertRaises(TypeError):
            self.user3 = create_user({})

    def test_userDuplicateError(self):
        with self.assertRaises(userDuplicateError):
            self.user2 = user(name="test_user",
                              ip_addr="127.0.0.1", resource=0)


if __name__ == '__main__':
    unittest.main()
