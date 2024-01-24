from langclient.models import Role, Message


def message_from_dict(dictionary: dict) -> "Message":
    return Message(
        role=Role(dictionary["role"]),
        content=dictionary["content"],
    )






def message_to_dict(message: Message) -> dict:
    return {"role": message.role.value, "content": message.content}
