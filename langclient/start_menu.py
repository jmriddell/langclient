import inquirer
import json
from os.path import exists, expanduser
from pkgutil import get_data

from langclient.models import LanguageModel
from typing import List

default_user_config_file = expanduser("~/.langclient/user_config.json")
default_models_data_file = ("langclient.data", "models.json")


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


def _language_models() -> List[LanguageModel]:
    model_list_json_string = get_data(*default_models_data_file)
    assert model_list_json_string is not None, "No models data found"
    model_list_data = json.loads(model_list_json_string.decode("utf-8"))

    _unpack_model = lambda model_data: LanguageModel(**model_data)
    models = list(map(_unpack_model, model_list_data))

    return models


def select_language_model() -> LanguageModel:
    """Select between the most relevant models"""

    models = _language_models()
    model_names = list(map(lambda model: model.name, models))

    select_model = [
        inquirer.List(
            "model_name",
            message="Select a model:",
            choices=model_names,
        ),
    ]

    answer = inquirer.prompt(select_model)["model_name"]
    model_selected = list(filter(lambda model: model.name == answer, models))

    return model_selected[0]
