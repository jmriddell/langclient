from typing import Iterable, Callable
from re import findall
from colorama import Fore

from openai import OpenAI
from openai.types.chat import ChatCompletionChunk

from langclient.models import Message, Role
from langclient.data_transformations import message_to_dict


def stream_chat(
    messages: list[Message],
    *,
    api_key: str,
    model="gpt-3.5-turbo-16k",
    temperature=1,
    max_tokens=14505,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
) -> Iterable[str]:
    client = OpenAI(api_key=api_key)
    generator: Iterable[ChatCompletionChunk] = client.chat.completions.create(
        model=model,
        messages=list(map(message_to_dict, messages)),
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        stream=True,
    )

    deltas_content = map(lambda chunk: chunk.choices[0].delta.content, generator)
    not_none_content = filter(lambda content: content is not None, deltas_content)

    return not_none_content


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
        with open(filename) as data:
            return data.read()
    except FileNotFoundError:
        return None


def _parse_file_content(message: str) -> str:
    "Match file mentions in <angle brackets> on message and parse them as content"
    files = _get_files_from_message(message)

    contents = [_file_content_section(file, _get_file_content(file)) for file in files]

    return "  ".join(contents)


def chat_input() -> Iterable[Message]:
    """Chat input stream."""

    while True:
        input_message = input(Fore.CYAN + "You:\n" + Fore.RESET)
        input_message += _parse_file_content(input_message)
        yield Message(role=Role.USER, content=input_message)


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


def step_process(
    previous_messages: list[Message], user_message: Message, chat_function: Callable
) -> list[Message]:
    """Get the next step in the conversation."""
    print(Fore.CYAN + "\nAssistant:" + Fore.RESET)
    assistant_response_chunks = chat_function([*previous_messages, user_message])

    assistant_response = Message(
        role=Role.ASSISTANT,
        content="".join(_print_intercept(assistant_response_chunks)),
    )
    print()
    print()
    return [*previous_messages, user_message, assistant_response]
