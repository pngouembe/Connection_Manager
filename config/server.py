import argparse
import os
from config import Config, __path__, MissingRequiredInfo, ConfigFile
from sdataclasses.resources import Resource


class ServerConfig(Config):

    required_info = ["address", "port", "resources"]

    def setup_argument_parser():
        default_cfg = "server_config_template.yml"
        default_resource = "resource_template.yml"

        parser = argparse.ArgumentParser(prog='Server-side connection manager',
                                         usage='python3 Connection_manager_server.py -c <config file path> -r <resource file path>',
                                         description='Program designed to keep track of the availability of a remote machine')

        # metavar='' so that there is no all caps argument name in usage
        parser.add_argument('-c', '--cfg_file',
                            type=str,
                            default=os.path.join(__path__[0], default_cfg),
                            metavar='',
                            help='path to the config file',
                            required=False)
        parser.add_argument('-r', '--rsrc_file',
                            type=str,
                            default=os.path.join(
                                __path__[0], default_resource),
                            metavar='',
                            help='path to the resource file',
                            required=False)

        return parser

    @classmethod
    def as_dict(cls) -> dict:
        if not cls.parser:
            cls.parser = cls.setup_argument_parser()
            cls.args = cls.parser.parse_args()
        if cls.args.rsrc_file:
            file_handler = ConfigFile.get_handler(file=cls.args.rsrc_file)
            dict = file_handler.as_dict_from_file(cls.args.rsrc_file)
            if "resources" in dict.keys():
                resource_list = []
                for i, r in enumerate(dict["resources"]):
                    resource_list.append(Resource(**r, id=i))
                dict["resources"] = resource_list
            cls.cfg_dict.update(dict)
        return super().as_dict()
