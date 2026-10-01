import re
import logging

from httpx import URL
from pathlib import Path
from rich.console import Console
from rich.logging import RichHandler
from typing import Union, Optional

from bnet.theme import THEME
from bnet.shared import APP_NAME

_console = Console(theme=THEME)
_console.set_window_title(APP_NAME.title())


def get_console() -> Console:
    return _console


def format_file_path(path: Union[Path, str]) -> str:
    if isinstance(path, Path):
        path = path.as_posix()

    return f"[file][link=file://{path}]{path}[/link][/]"


def format_url(url: Union[str, URL], display_text: Optional[str] = None) -> str:
    return f"[url][link={url}]{display_text or url}[/link][/]"


def format_duration(seconds: int) -> str:
    return f"[green]{seconds // 60}[/]m"


QUIET_LOGGERS = ("httpx", "httpcore", "websockets", "asyncio")

_REDACTIONS = [
    (
        re.compile(
            r"(?i)(authorization\W{1,6})(?:(?:bearer|basic)\s+)?[A-Za-z0-9._~+/=-]+"
        ),
        r"\1[REDACTED]",
    ),
    (
        re.compile(
            r"(?i)((?:access_token|refresh_token|client_secret|id_token)\W{1,4})[A-Za-z0-9._~+/=-]+"
        ),
        r"\1[REDACTED]",
    ),
]


class RedactingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        for pattern, repl in _REDACTIONS:
            msg = pattern.sub(repl, msg)
        record.msg, record.args = msg, ()
        return True


def setup_logging(
    level: int = logging.INFO, console: Optional[Console] = None
) -> None:
    handler = RichHandler(
        console=console or get_console(),
        markup=True,
        rich_tracebacks=True,
        show_path=False,
        log_time_format="[%X]",
    )
    handler.addFilter(RedactingFilter())
    logging.basicConfig(
        level=level, format="%(message)s", handlers=[handler], force=True
    )

    for name in QUIET_LOGGERS:
        logging.getLogger(name).setLevel(logging.WARNING)
