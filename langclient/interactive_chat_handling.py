from re import findall
from typing import Iterable, Callable
from colorama import Fore
from itertools import accumulate
from functools import partial

from langclient.models import Message, Role, LanguageModel
from langclient.chat_functions import token_usage_stats


def _get_files_from_message(message: str) -> list[str]:
    "Match file mentions in <angle brackets> on message and return their names"
    pattern = r"<(.*?)>"
    return findall(pattern, message)


def _file_content_section(filename: str, file_content: str | None) -> str:
    "Return a file content section in a format friendly to the language model"
    if file_content is None:
        return f"FILE {filename} NOT ACCESSIBLE"
    return f"START {filename} CONTENT:  {file_content}  END {filename} CONTENT"


def _get_file_content(filename: str) -> str | None:
    "Get the content of the file with the given name"
    try:
        with open(filename, encoding="utf-8") as data:
            return data.read()
    except FileNotFoundError:
        return None


def _make_files_content_section(filenames: Iterable[str]) -> str:
    "Make a file content section for each file in filenames"
    file_contents = map(_get_file_content, filenames)
    file_sections = map(_file_content_section, filenames, file_contents)
    return "  ".join(file_sections)


def _parse_file_content(message: str) -> str:
    "Find file mentions in <angle brackets> and make a section for the contents"
    files = _get_files_from_message(message)

    return _make_files_content_section(files)


def _enhance_user_input(user_input: str) -> Message:
    """Enhance the user input with file content."""
    message_content = user_input + _parse_file_content(user_input)
    return Message(role=Role.USER, content=message_content)


def chat_input(user_name: str) -> Iterable[Message]:
    """Chat input stream."""

    while True:
        input_message = input()
        yield _enhance_user_input(input_message)


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


def _step_process(
    previous_messages: list[Message],
    user_message: Message,
    chat_function: Callable,
    model: LanguageModel,
    user_name: str,
) -> list[Message]:
    """Get the next step in the conversation."""
    assistant_response_chunks = chat_function([*previous_messages, user_message])

    assistant_response = Message(
        role=Role.ASSISTANT,
        content="".join(_print_intercept(assistant_response_chunks)),
    )

    chat_updated = [*previous_messages, user_message, assistant_response]

    user_head = Fore.CYAN + f"{user_name}:" + Fore.RESET
    user_head += token_usage_stats(chat_updated, model)

    print()
    print()
    print(user_head)

    return chat_updated


def chat_sequence_process(
    user_input: Iterable[Message],
    chat_function: Callable,
    model: LanguageModel,
    user_name: str,
) -> Iterable[Message]:
    accumulate_function = partial(
        _step_process, chat_function=chat_function, user_name=user_name, model=model
    )

    first_user_head = Fore.CYAN + f"{user_name}:" + Fore.RESET
    print(first_user_head)

    return accumulate(user_input, accumulate_function, initial=[])
