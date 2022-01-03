import unittest
from users import User, user_from_dict, UserDuplicateError, MissingRequiredFields
from dataclasses import asdict, FrozenInstanceError


class TestUserMethods(unittest.TestCase):

    def setUp(self):
        self.user = User(name="test_user", address="127.0.0.1", resource=0)

    def tearDown(self):
        User.users_ids = []

    def test_update(self):
        self.user2 = User(name="test_user2", address="127.0.0.1", resource=0)
        self.user2.update(self.user.serialize())
        self.assertEqual(self.user, self.user2)

    def test_user_from_dict(self):
        self.user_dict = {
            "name": "test_user3",
            "address": "127.0.0.1",
            "resource": 0,
            "foo": "bar",
            "id": 0,
            "a": 10}
        self.user3 = user_from_dict(self.user_dict)
        self.assertEqual(asdict(self.user3), self.user_dict)

        # checking that the class is read-only
        with self.assertRaises(FrozenInstanceError):
            self.user3.resource = 1

        # testing required fields
        self.user_dict = {
            "address": "127.0.0.1",
            "foo": "bar",
            "id": 0,
            "a": 10}
        with self.assertRaises(MissingRequiredFields):
            self.user3 = user_from_dict(self.user_dict)

        with self.assertRaises(MissingRequiredFields):
            self.user3 = user_from_dict({})

    def test_userDuplicateError(self):
        with self.assertRaises(UserDuplicateError):
            self.user2 = User(name="test_user",
                              address="127.0.0.1", resource=0)


if __name__ == '__main__':
    unittest.main()
