import argparse
from config.base import Config, __path__, MissingRequiredInfo
import os


class ClientConfig(Config):

    required_info = ["name", "address", "resource"]

    def setup_argument_parser():
        default_cfg = "client_config_template.yml"
        parser = argparse.ArgumentParser(prog='Client-side connection manager',
                                         usage='python3 Connection_manager_client.py -c <config file path>',
                                         description='Program designed to keep track of the availability of a remote machine')

        # metavar='' so that there is no all caps argument name in usage
        parser.add_argument('-c', '--cfg_file',
                            type=str,
                            default=os.path.join(__path__[0], default_cfg),
                            metavar='',
                            help='path to the config file',
                            required=False)

        return parser
