from typing import Iterable, TypeGuard
from colorama import Fore

from openai import OpenAI
from openai.types.chat import ChatCompletionChunk

from langclient.models import Message, LanguageModel
from langclient.data_transformations import message_to_dict
from langclient.token_usage import token_usage_stats


def stream_chat(
    messages: list[Message],
    *,
    api_key: str,
    model: LanguageModel,
    temperature=1,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
) -> Iterable[str]:
    client = OpenAI(api_key=api_key)
    list_of_dict_messages = list(map(message_to_dict, messages))
    generator: Iterable[ChatCompletionChunk] = client.chat.completions.create(
        model=model.name,
        messages=list_of_dict_messages,
        temperature=temperature,  # next parameters have no effect
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        stream=True,
    )  # type: ignore[assignment] # TODO: Do it properly

    deltas_content = map(lambda chunk: chunk.choices[0].delta.content, generator)

    color_assistant = Fore.BLUE
    assistant_name = "Assistant"

    assistant_head = f"{color_assistant}{assistant_name}:{Fore.RESET}"
    assistant_head += token_usage_stats(messages, model)

    print()
    print(assistant_head)

    def _typeguard(content: str | None) -> TypeGuard[str]:
        return content is not None

    not_none_content = filter(_typeguard, deltas_content)
    return not_none_content
