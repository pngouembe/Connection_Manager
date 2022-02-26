from rich.text import Text
import re


class RichLogLine:
    log_pattern = r"(?P<time>\[\d{2}:\d{2}:\d{2}\])?(?P<space1>\s+)(?P<level>\w+)(?P<space2>\s+)(?P<msg>\S.*)"
    time_markup = "[bold blue]"
    # TODO: Add emojis :P
    level_markup = {
        "DEBUG": "[bold green]DEBUG[/]",
        "INFO": "[bold white]INFO[/]",
        "WARNING": "[bold yellow]WARNING[/]",
        "ERROR": "[bold red]ERROR[/]",
        "CRITICAL": "[bold red underline]CRITICAL[/]"
    }
    msg_markup = "[white]"
    end_markup = "[/]"

    def __init__(self, log_line: str) -> None:
        self.original_log = log_line
        match = re.search(self.log_pattern, log_line)
        if match:
            self.groups = match.groupdict()
            try:
                self.level = self.level_markup[self.groups["level"]]
            except KeyError:
                self.level = self.level_markup["CRITICAL"]
            self.log_line = re.sub(
                self.log_pattern,
                rf"{self.time_markup}\1{self.end_markup}\2{self.level}\4{self.msg_markup}\5",
                log_line
            )
        else:
            self.log_line = self.original_log
        #     self.time = self.time_markup + \
        #         self.groups["time"] + self.end_markup
        #     self.level = self.level_markup[self.groups["level"].strip()]
        #     self.msg = self.msg_markup + self.groups["msg"] + self.end_markup
        # self.log_line = self.time + \
        #     self.level.ljust(len(self.groups["level"])) + self.msg

    def __rich__(self):
        return self.log_line

    def __repr__(self) -> str:
        return self.original_log


class RichLogLines:
    def __init__(self, log_lines: list) -> None:
        self.log_lines = [RichLogLine(log_line) for log_line in log_lines]

    def __rich__(self):
        return "\n".join([log_line.__rich__() for log_line in self.log_lines])

    def __repr__(self) -> str:
        return "\n".join([log_line.__repr__() for log_line in self.log_lines])
