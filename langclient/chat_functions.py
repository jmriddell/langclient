from typing import Iterable

import openai

from models import Message
from data_transformations import message_to_dict


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
    generator = openai.ChatCompletion.create(
        model=model,
        messages=list(map(message_to_dict, messages)),
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        stream=True,
        api_key=api_key,
    )

    deltas = map(lambda chunk: chunk["choices"][0]["delta"], generator)
    content_deltas = filter(lambda delta: "content" in delta, deltas)
    content = map(lambda delta: delta["content"], content_deltas)

    return content
