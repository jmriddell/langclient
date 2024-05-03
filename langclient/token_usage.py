from colorama import Fore
from tiktoken import encoding_for_model

from langclient.models import Role, Message, LanguageModel


def _filter_content_by_role(messages: list[Message], role: Role):
    role_messages = list(filter(lambda message: message.role == role, messages))
    role_content = map(lambda message: message.content, role_messages)

    return role_content


def _format_token_number(number: int | float) -> str:
    return f"{round(number / 1000)}k" if number > 1000 else f"{number}"


def _token_cost(chat_tokens: dict[str, list[int]], model: LanguageModel):
    def _sum_accumulated_tokens(tokens):
        """Calculates the accumulated sum of tokens usage in the entire chat"""
        return sum([sum(tokens[: i + 1]) for i in range(len(tokens))])

    def _token_cost(tokens, cost_1kT_token):
        token_usage_accummulated = _sum_accumulated_tokens(tokens)
        return token_usage_accummulated * cost_1kT_token / 1000

    input_cost = _token_cost(chat_tokens["input"], model.cost_1kT_input)
    output_cost = _token_cost(chat_tokens["output"], model.cost_1kT_output)

    return input_cost + output_cost


def token_usage_stats(messages: list[Message], model: LanguageModel) -> str:
    input_content = _filter_content_by_role(messages, Role.USER)
    output_content = _filter_content_by_role(messages, Role.ASSISTANT)

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

    color_token = Fore.LIGHTMAGENTA_EX
    color_cost = Fore.LIGHTBLACK_EX

    stats_string = f" {color_token}({usage_stats}){Fore.RESET}"
    stats_string += f" {color_cost}${cost_stats}{Fore.RESET}"

    return stats_string
