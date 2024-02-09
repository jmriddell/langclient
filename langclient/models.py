"""Models for openai chat models"""

from enum import Enum
from pydantic import BaseModel


class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class Message(BaseModel):
    role: Role
    content: str


class Chat(BaseModel):
    messages: list[Message]


class LanguageModel(BaseModel):
    name: str
    max_token: int
    cost_per_1kT_input: float
    cost_per_1kT_output: float
