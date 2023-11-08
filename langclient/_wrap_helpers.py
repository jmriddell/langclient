"""Helpers to wrap openai funcitons."""

from typing import Callable
from functools import wraps


def make_api_key_argument_mandatory(func: Callable):
    """Make the api key argument mandatory for the decorated function."""

    @wraps(func)
    def wrapper(*args, api_key, **kwargs):
        return func(*args, api_key=api_key, **kwargs)

    return wrapper
