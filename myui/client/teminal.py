import os
import threading
import time
from collections import deque
from queue import Empty, Queue

from com import message
from com.header import Header
from myconsole import console
from mylogger import log, log_stream
from myui.terminal import TerminalDashboard
from myui.utils import RichLogLines
from rich.console import Console, Group
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.pretty import Pretty
from rich.table import Table
from rich.text import Text
from users import User

import client.actions.handle as actions

# TODO: Terminal configuration
HEADER_SIZE = 2
TABS_SIZE = 3
FOOTER_SIZE = 7
QUEUE_TIMEOUT = 1
MAIN_SIZE = os.get_terminal_size().lines - HEADER_SIZE - FOOTER_SIZE - 2


class ClientTerminalDashboard(TerminalDashboard):
    def generate_layout(self) -> Layout:
        layout = Layout(name="root")
        layout.split(
            Layout(name="header", size=HEADER_SIZE),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=FOOTER_SIZE),
        )

        layout["main"].split_row(
            Layout(name="user"),
            Layout(name="messages", ratio=2)
        )

        self.header = layout["header"]
        self.user_panel = layout["user"]
        self.messages = layout["messages"]
        self.footer = layout["footer"]

        return layout

    def run(self) -> None:
        layout = self.generate_layout()

        title = Text(self.user.info.name,
                     style="bold yellow", justify="center")
        self.header.update(title)

        self.user_panel.update(Panel(Pretty(self.user)))
        # self.messages.update(Panel(msg_table, title="Recieved messages"))
        # update 4 times a second to feel fluid
        with Live(layout, auto_refresh=False, console=console) as live:
            row = 0
            rows = []
            log_lines = deque(maxlen=5)
            messages = deque(maxlen=MAIN_SIZE)
            while self.run_event.is_set():
                try:
                    msg: message.Message = self.queue.get(
                        timeout=QUEUE_TIMEOUT)
                except Empty:
                    pass
                else:
                    messages.append(msg)
                    self.messages.update(
                        Panel(Group(*messages), title="Recieved messages"))
                    # msg_table.add_row(msg)

                logs = log_stream.getvalue()
                for line in logs.splitlines():
                    if line not in log_lines:
                        log_lines.append(line)

                self.footer.update(
                    Panel(RichLogLines(log_lines), title="Logs"))

                live.refresh()
