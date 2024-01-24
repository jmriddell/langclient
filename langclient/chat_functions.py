from typing import Iterable
from re import findall

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
    presence_penalty=0
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


def _parse_file_content(message: str) -> dict:
    "Match file mentions in <angle brackets> on message and parse them as content"
    pattern = r'<(.*?)>'
    files = findall(pattern, message)
    
    def _segment_file_content(file):
        content = f"START {file} CONTENT:  "

        try:
            with open(file) as data:
                content += data.read()
        except FileNotFoundError:
            return f"FILE {file} NOT ACCESSIBLE"

        content += f"  END {file} CONTENT"
        
        return content

    contents = [ _segment_file_content(file) for file in files ]

    return "  ".join(contents)


def user_input() -> Iterable[Message]:
    """Get user input for a chat."""

    while True:
        input_message = input("You:\n")
        input_message += _parse_file_content(input_message)
        yield Message(role=Role.USER, content=input_message)
