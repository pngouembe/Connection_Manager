from io import StringIO

from rich.console import Console

console = Console()

log_stream = StringIO()
log_console = Console(file=log_stream)
