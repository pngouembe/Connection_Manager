#!/usr/bin/env python3
from rich import inspect, print
from rich.pretty import pprint

from config.server import ServerConfig as config
from mydataclasses.servers import Server
from server import launch_server

from mylogger import log
from rich.logging import RichHandler

log.handlers = [RichHandler(show_path=False)]


def main():
    cfg_dict = config.as_dict()
    server = Server(**cfg_dict)
    inspect(server)
    launch_server(server_config=server)

if __name__ == "__main__":
    main()
