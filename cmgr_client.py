#!/usr/bin/env python3
from client import launch_client
from config.client import ClientConfig as config


def main():
    cfg_dict = config.as_dict()
    launch_client(client_dict=cfg_dict)


if __name__ == "__main__":
    main()
