from collections import deque
import threading
from queue import Empty, Queue
import time

import client.actions.handle as actions
from com import message
from com.header import Header
from mylogger import log, log_stream
from myconsole import console
from rich.live import Live
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel
from myui.utils import RichLogLines
from users import User


class UiThread(threading.Thread):

    def __init__(self, user: User, run_event: threading.Event, queue: Queue) -> None:
        self.user = user
        self.run_event = run_event
        self.queue = queue
        super().__init__(name=user.info.name)

    def run(self) -> None:
        msg_table = Table.grid(expand=True)

        layout = Layout(name="root")
        layout.split(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=7),
        )
        layout["main"].split_row(
            Layout(name="side"),
            Layout(name="body", ratio=2, minimum_size=60),
        )

        layout["body"].update(Panel(msg_table, title="Recieved messages"))
        # update 4 times a second to feel fluid
        with Live(layout, refresh_per_second=4):
            row = 0
            rows = []
            log_lines = deque(maxlen=5)
            while self.run_event.is_set():
                time.sleep(0.4)  # arbitrary delay
                # update the renderable internally
                rows.append((f"{row}", f"description {row}", "[red]ERROR"))
                if len(rows) > 10:
                    rows.pop(0)
                table = Table(expand=True)
                table.add_column("Row ID")
                table.add_column("Description")
                table.add_column("Level")

                for r in rows:
                    table.add_row(*r)

                layout["side"].update(Panel(table, title="Table"))
                row += 1
                try:
                    msg: message.Message = self.queue.get_nowait()
                    msg_table.add_row(msg)
                except Empty:
                    pass
                logs = log_stream.getvalue()
                for line in logs.splitlines():
                    if line not in log_lines:
                        log_lines.append(line)

                layout["footer"].update(
                    Panel(RichLogLines(log_lines), title="Logs"))
