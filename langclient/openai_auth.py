"""Functions to manage openai api authentication."""

from typing import Callable
from functools import wraps, partial
from io import TextIOWrapper


def use_key(api_key: str) -> Callable[[Callable], Callable]:
    """Use the given key to authenticate with openai.

    Args:
        openai_key (str): The api key to use.

    Returns:
        Callable[[Callable], Callable]: A decorator that will make the function use the
        given key to authenticate with openai.
    """

    def decorator(func: Callable):
        return wraps(func)(partial(func, api_key=api_key))

    return decorator


_OpenFunction = Callable[[str], TextIOWrapper]


def read_key_from_file(path: str = ".openai-key", open_: _OpenFunction = open) -> str:
    with open_(path) as file:
        return file.read().strip()


def use_key_from_file(path: str = ".openai-key") -> Callable[[Callable], Callable]:
    return use_key(read_key_from_file(path))
