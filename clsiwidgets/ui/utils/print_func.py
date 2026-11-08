from enum import Enum

import ipywidgets


class Color(Enum):
    RED = "\033[91m"
    GREEN = "\033[92m"
    RESET = "\033[0m"


def _print(output: ipywidgets.Output, msg: str, color: Color | None = None, append: bool = False) -> None:
    if not append:
        output.clear_output()

    with output:
        if color:
            print(f'{color.value}{msg}{Color.RESET.value}')
        else:
            print(msg)


def print_error(output: ipywidgets.Output, msg: str, append: bool = False) -> None:
    _print(output, msg=msg, color=Color.RED, append=append)


def print_msg(output: ipywidgets.Output, msg: str, append: bool = False) -> None:
    _print(output, msg=msg, append=append)


def print_success(output: ipywidgets.Output, msg: str, append: bool = False) -> None:
    _print(output, msg=msg, color=Color.GREEN, append=append)
