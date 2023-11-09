"""Interactive demo for langclient."""

from itertools import accumulate
import argparse
from typing import Iterable, Callable
import readline  # noqa: F401

from chat_functions import stream_chat
from openai_auth import use_key, read_key_from_file
from models import Message, Role


def _messages_accumulate(messages: Iterable[Message]):
    """Accumulate the messages in a chat."""
    return accumulate(messages, lambda acc, message: [*acc, message], initial=[])


def _user_input() -> Iterable[Message]:
    """Get user input for a chat."""
    while True:
        yield Message(role=Role.USER, content=input("You:\n"))


def _side_effect(function: Callable, iter: Iterable):
    """Call the given function on each item in the given iterable."""

    def call_and_pass(item):
        function(item)
        return item

    yield from (call_and_pass(item) for item in iter)


def _print_inline(string: str):
    """Print the given string inline."""
    print(string, end="", flush=True)


def _print_intercept(iter: Iterable):
    """Print the given iterable inline."""
    return _side_effect(_print_inline, iter)


def _read_key_from_file_if_path(path: str | None) -> str | None:
    """Read the key from the given path if it exists.

    Args:
        path (str | None): The path to read from.
        open (type(open), optional): The open function to use. Defaults to open.

    Returns:
        str | None: The key if it exists, otherwise None.
    """
    if path is None:
        return None
    return read_key_from_file(path)


def main(pre_provided_api_key: str | None = None, api_key_file_path: str | None = None):
    # Prompt the user for their API key
    api_key = (
        pre_provided_api_key
        or _read_key_from_file_if_path(api_key_file_path)
        or input("Please enter your API key: ")
    )
    print()

    # Decorate the stream_chat function with the given key
    stream_chat_ = use_key(api_key)(stream_chat)

    messages = []

    for user_message in _user_input():
        messages.append(user_message)

        print("\nAssistant:")
        assistant_response_chunks = stream_chat_(messages)
        messages.append(
            Message(
                role=Role.ASSISTANT,
                content="".join(_print_intercept(assistant_response_chunks)),
            )
        )
        print()
        print()


if __name__ == "__main__":
    # read args
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--api-key",
        "-k",
        type=str,
        help="The api key to use.",
    )
    parser.add_argument(
        "--api-key-file",
        "-f",
        type=str,
        help="The file to read the api key from.",
    )
    args = parser.parse_args()

    # run main
    main(args.api_key, args.api_key_file)
