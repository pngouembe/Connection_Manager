# -*- coding: utf-8 -*-
"""Configuration module
This module is made to allow program to load its configuration
from an external config file.
This version of the module is made to import yaml configuration
files.
"""
from abc import abstractmethod
import os
import yaml


class UnsupportedFileError(Exception):
    pass


class MissingRequiredInfo(Exception):
    pass


class ConfigFile:
    yaml = '.yml'

    @classmethod
    def get_handler(cls, file: str):
        file_ext = os.path.splitext(file)[1].lower()
        if file_ext not in vars(cls).values():
            raise UnsupportedFileError(
                "{} extention not supported yet".format(file_ext))
        elif file_ext == cls.yaml:
            return YamlConfigFile()

    @abstractmethod
    def as_dict_from_file(cfg_file_path: str) -> dict:
        """
        This method return a dictionnary representing the configuration
        file passed in argument
        """
        pass


class YamlConfigFile(ConfigFile):
    def as_dict_from_file(self, cfg_file_path: str) -> dict:
        """
        This method return a dictionnary representing the yaml configuration
        file passed in argument
        """
        with open(cfg_file_path) as f:
            dict = yaml.safe_load(f)
        return dict


class Config():

    required_info = []
    @abstractmethod
    def setup_argument_parser():
        pass

    def check_for_required(self, loaded_info: dict):
        """
        Checks if the required information are contained in a given dict
        """
        missing_info = set(self.required_info) - set(loaded_info.keys())
        if missing_info:
            raise MissingRequiredInfo(
                "The following infos are missing from your config file {}".format(missing_info))

    @classmethod
    def as_dict(cls) -> dict:
        parser = cls.setup_argument_parser()
        args = parser.parse_args()
        cfg_dict = dict()
        if args.cfg_file:
            file_handler = ConfigFile.get_handler(file=args.cfg_file)
            cfg_dict = file_handler.as_dict_from_file(args.cfg_file)
        cfg_dict.update(vars(args))
        cls.check_for_required(cls, cfg_dict)
        return cfg_dict
