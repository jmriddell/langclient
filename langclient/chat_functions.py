from typing import Iterable

from openai import OpenAI
from openai.types.chat import ChatCompletionChunk

from langclient.models import Message
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
