"""Interactive demo for langclient."""

from itertools import accumulate
from functools import partial
import argparse
from typing import Iterable, Callable
import readline  # noqa: F401

from langclient.chat_functions import stream_chat, user_input
from langclient.openai_auth import use_key, read_key_from_file
from langclient.models import Message, Role
from langclient.start_manu import select_language_model
from os.path import isfile, expanduser


def _graceful_exit(function: Callable) -> Callable:
    """Call the given function and exit gracefully on KeyboardInterrupt."""

    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except KeyboardInterrupt:
            print()
            print("Exiting...")
            exit(0)

    return wrapper


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


def _step_process(
    previous_messages: list[Message], user_message: Message, chat_function: Callable
) -> list[Message]:
    """Get the next step in the conversation."""
    print("\nAssistant:")
    assistant_response_chunks = chat_function([*previous_messages, user_message])

    assistant_response = Message(
        role=Role.ASSISTANT,
        content="".join(_print_intercept(assistant_response_chunks)),
    )
    print()
    print()
    return [*previous_messages, user_message, assistant_response]


def _chat_sequence_process(
    user_input: Iterable[Message], chat_function: Callable
) -> Iterable[Message]:
    accumulate_function = partial(_step_process, chat_function=chat_function)
    return accumulate(user_input, accumulate_function, initial=[])


def _get_arguments() -> dict:
    """Get the arguments for the main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--api-key",
        "-k",
        type=str,
        help="The api key to use.",
        dest="pre_provided_api_key",
    )
    parser.add_argument(
        "--api-key-file",
        "-f",
        type=str,
        help="The file to read the api key from.",
        dest="api_key_file_path",
    )
    return vars(parser.parse_args())


def _prompt_for_api_key():
    api_key = input("Please enter your API key: ")
    print()
    return api_key


def _get_key_from_config(filepath=expanduser("~/.langclient/openai-key")):
    if not isfile(filepath):
        return None
    return _read_key_from_file_if_path(filepath)


@_graceful_exit
def interactve_chat(
    pre_provided_api_key: str | None = None, api_key_file_path: str | None = None
):
    # Prompt the user for their API key
    api_key = (
        pre_provided_api_key
        or _read_key_from_file_if_path(api_key_file_path)
        or _get_key_from_config()
        or _prompt_for_api_key()
    )

    model_selected = select_language_model()

    stream_chat_ = use_key(api_key)(
        partial(stream_chat, model=model_selected, max_tokens=3500)
    )

    for _ in _chat_sequence_process(user_input(), stream_chat_):
        pass


def entrypoint():
    interactve_chat(**_get_arguments())


if __name__ == "__main__":
    entrypoint()
