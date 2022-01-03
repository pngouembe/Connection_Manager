#!/usr/bin/env python3
from config.client import ClientConfig as config
from rich import print, inspect
from rich.pretty import pprint


def main():
    cfg_dict = config.as_dict()
    pprint(cfg_dict, expand_all=True)


if __name__ == "__main__":
    main()
