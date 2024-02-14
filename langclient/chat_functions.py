from typing import Iterable, TypeGuard
from colorama import Fore

from openai import OpenAI
from openai.types.chat import ChatCompletionChunk

from tiktoken import encoding_for_model

from langclient.models import Message, LanguageModel
from langclient.data_transformations import message_to_dict


def _filter_content_by_role(messages: list[Message], role: str):
    role_messages = list(filter(lambda message: message.role == role, messages))
    role_content = map(lambda message: message.content, role_messages)

    return role_content


def _format_token_number(number: int | float) -> str:
    return f"{round(number / 1000)}k" if number > 1000 else f"{number}"


def _token_cost(chat_tokens: dict[str, list[int]], model: LanguageModel):
    def _sum_accumulated_tokens(tokens):
        """Calculates the accumulated sum of tokens usage in the entire chat"""
        return sum([sum(tokens[: i + 1]) for i in range(len(tokens))])

    tokens_accummulated_input = _sum_accumulated_tokens(chat_tokens["input"])
    tokens_accummulated_output = _sum_accumulated_tokens(chat_tokens["output"])

    input_cost = tokens_accummulated_input / 1000 * model.cost_per_1kT_input
    output_cost = tokens_accummulated_output / 1000 * model.cost_per_1kT_output

    return input_cost + output_cost


def _token_usage_stats(messages: list[Message], model: LanguageModel) -> str:
    input_content = _filter_content_by_role(messages, "user")
    output_content = _filter_content_by_role(messages, "assistant")

    encoder = encoding_for_model(model.name)
    content_tokens = lambda content: len(encoder.encode(content))

    chat_tokens = {
        "input": list(map(content_tokens, input_content)),
        "output": list(map(content_tokens, output_content)),
    }

    total_cost = _token_cost(chat_tokens, model)
    cost_stats = "%.2f" % (total_cost)

    tokens_messages = sum(chat_tokens["input"] + chat_tokens["output"])
    usage_stats = f"{_format_token_number(tokens_messages)}/"
    usage_stats += f"{_format_token_number(model.max_token)}"

    stats_string = f" {Fore.MAGENTA}({usage_stats}){Fore.RESET}"
    stats_string += f" {Fore.GREEN}${cost_stats}{Fore.RESET}"
    return stats_string


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

    assistant_head = f"\n{Fore.CYAN}Assistant:{Fore.RESET}"
    assistant_head += _token_usage_stats(messages, model)

    print(assistant_head)

    def _typeguard(content: str | None) -> TypeGuard[str]:
        return content is not None

    not_none_content = filter(_typeguard, deltas_content)
    return not_none_content
