import logging

from rich.logging import RichHandler
from myconsole import log_console, log_stream

FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET",
    format=FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler(console=log_console, show_path=False)]
)

clog = logging.getLogger()
