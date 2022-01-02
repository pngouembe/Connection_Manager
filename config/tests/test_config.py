import unittest
import config
import config.tests
import os


class TestConfigFileMethods(unittest.TestCase):

    unsupported_file = "test.md"

    test_file = os.path.join(config.tests.__path__[0], "test.yml")
    handle_class = config.yamlConfigFile
    exp_dict = {
        "test": "test value",
        "test_list": ["test1", "test2"],
        "test_dict": [
            {"test1": 1},
            {"test2": 2}
        ]
    }

    def test_yml_file_as_dict(self):
        # test that an error is raised when file extention is not supported
        with self.assertRaises(config.unsupportedFileError):
            config.configFile.get_handler(self.unsupported_file)

        # Check that the correct handler instance is generated
        handler = config.configFile.get_handler(self.test_file)
        self.assertIsInstance(handler, self.handle_class)

        # Check that the correct dict is generated
        dict = handler.as_dict_from_file(self.test_file)
        self.assertEqual(dict, self.exp_dict)
