import inquirer
import json
from os.path import exists, expanduser

default_user_config_file = expanduser("~/.langclient/user_config.json")


def save_user_name(user_name: str, file_path: str = default_user_config_file):
    """Save user name on user config json file"""
    with open(file_path, "w") as file:
        json.dump({"name": user_name}, file)


def ask_user_name() -> str:
    ask_name = [inquirer.Text("user_name", message="Your Name")]

    answer = inquirer.prompt(ask_name)

    return answer["user_name"]


def user_name(file_path: str = default_user_config_file) -> str:
    """Name user to display on dialog"""
    if not exists(file_path):
        user_name = ask_user_name()
        save_user_name(user_name)

    with open(default_user_config_file, "r") as file:
        user_config = json.load(file)
        user_name = user_config["name"]

    return user_name


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
