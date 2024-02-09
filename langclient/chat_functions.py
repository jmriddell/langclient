from typing import Iterable, TypeGuard

from openai import OpenAI
from openai.types.chat import ChatCompletionChunk

from tiktoken import encoding_for_model

from langclient.models import Message, LanguageModel
from langclient.data_transformations import message_to_dict


def _filter_content_by_role(messages: list[Message], role: str):
    role_messages = list(filter(lambda message: message.role == role, messages))
    role_content = map(lambda message: message.content, role_messages)

    return role_content


def count_tokens(messages: list[Message], model: LanguageModel):
    input_contents = _filter_content_by_role(messages, "user")
    outputs_contents = _filter_content_by_role(messages, "assistant")

    encoder = encoding_for_model(model.name)
    content_tokens = lambda content: len(encoder.encode(content))

    tokens = {
        "input": sum(map(content_tokens, input_contents)),
        "output": sum(map(content_tokens, outputs_contents)),
    }

    tokens_total = tokens["input"] + tokens["output"]

    input_cost = tokens["input"] / 1000 * model.cost_per_1kT_input
    output_cost = tokens["output"] / 1000 * model.cost_per_1kT_output
    cost_total = input_cost + output_cost

    print(f"Token usage: {tokens_total}/{model.max_token}")
    print(f"Accummulated cost: USD ${cost_total}")


def stream_chat(
    messages: list[Message],
    *,
    api_key: str,
    model: LanguageModel,
    temperature=1,
    max_tokens=14505,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
) -> Iterable[str]:
    client = OpenAI(api_key=api_key)
    list_of_dict_messages = list(map(message_to_dict, messages))
    generator: Iterable[ChatCompletionChunk] = client.chat.completions.create(
        model=model.name,
        messages=list_of_dict_messages,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        stream=True,
    )  # type: ignore[assignment] # TODO: Do it properly

    deltas_content = map(lambda chunk: chunk.choices[0].delta.content, generator)

    count_tokens(messages, model)

    def _typeguard(content: str | None) -> TypeGuard[str]:
        return content is not None

    not_none_content = filter(_typeguard, deltas_content)
    return not_none_content
