import sys

from rich.console import Console
from rich.markup import escape
from rich.text import Text

console_stdout = Console()
console_stderr = Console(file=sys.stderr)


def err(message: str) -> None:
    """
    Prints an error message to stderr with a red prefix.

    :param message: The message to print.
    """
    err_prefix = Text('err:', style='bold red')
    console_stderr.print(err_prefix, message)


def suc(message: str) -> None:
    """
    Prints a success message to stdout with a green prefix.

    :param message: The message to print.
    """
    suc_prefix = Text('suc:', style='bold green')
    console_stdout.print(suc_prefix, message, highlight=False)


def war(message: str) -> None:
    """
    Prints a warning message to stdout with a yellow prefix.

    :param message: The message to print.
    """
    war_prefix = Text('war:', style='bold yellow')
    console_stdout.print(war_prefix, message, highlight=False)


def inf(message: str) -> None:
    """
    Prints an info message to stdout with a blue prefix.

    :param message: The message to print.
    """
    inf_prefix = Text('inf:', style='bold blue')
    console_stdout.print(inf_prefix, message, highlight=False)


def sanitize(message: str) -> str:
    """
    Sanitizes a message to escape any markup that might be interpreted by Rich.

    :param message: The message to sanitize.
    :return: The sanitized message string.
    """
    return escape(message)
