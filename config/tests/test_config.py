import unittest
import config
import config.client
import config.server
import config.tests
import os


class TestConfigFileMethods(unittest.TestCase):

    unsupported_file = "test.md"

    server_test_file = os.path.join(config.__path__[0], "server_config_template.yml")
    client_test_file = os.path.join(
        config.__path__[0], "client_config_template.yml")
    test_file = os.path.join(config.tests.__path__[0], "test.yml")
    handle_class = config.YamlConfigFile
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
        with self.assertRaises(config.UnsupportedFileError):
            config.ConfigFile.get_handler(self.unsupported_file)

        # Check that the correct handler instance is generated
        handler = config.ConfigFile.get_handler(self.test_file)
        self.assertIsInstance(handler, self.handle_class)

        # Check that the correct dict is generated
        dict = handler.as_dict_from_file(self.test_file)
        self.assertEqual(dict, self.exp_dict)

    def test_server_cfg_check(self):
        handler = config.ConfigFile.get_handler(self.test_file)
        dict = handler.as_dict_from_file(self.server_test_file)
        server_cfg = config.server.ServerConfig()

        server_cfg.check_for_required(dict)

        # Check that incomplete server config file loaded raises an error
        with self.assertRaises(config.MissingRequiredInfo):
            server_cfg.check_for_required(self.exp_dict)

    def test_client_cfg_check(self):
        handler = config.ConfigFile.get_handler(self.test_file)
        dict = handler.as_dict_from_file(self.client_test_file)
        client_cfg = config.client.ClientConfig()

        client_cfg.check_for_required(dict)

        # Check that incomplete client config file loaded raises an error
        with self.assertRaises(config.MissingRequiredInfo):
            client_cfg.check_for_required(self.exp_dict)


if __name__ == '__main__':
    unittest.main()
