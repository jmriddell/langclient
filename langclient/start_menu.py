import inquirer


def select_language_model() -> str:
    """Select between the most relevant models"""
    select_model = [
        inquirer.List(
            'model',
            message="Select a model:",
            choices=["gpt-3.5-turbo-1106", "gpt-4-1106-preview", "gpt-4"],
        ),
    ]

    answer = inquirer.prompt(select_model)

    return answer["model"]
