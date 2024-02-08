import inquirer


def select_language_model() -> str:
    """Select between the most relevant models"""
    select_model = [
        inquirer.List(
            "model",
            message="Select a model:",
            choices=[
                "gpt-3.5-turbo-0125",
                "gpt-4-0125-preview",
                "gpt-4-1106-preview",
                "gpt-4",
                "gpt-4-32k",
            ],
        ),
    ]

    answer = inquirer.prompt(select_model)

    return answer["model"]
