import json

file_name = r"data/users.json"


def load_file(file_name: str) -> list:
    with open(file_name, "r", encoding="utf-8") as file:
        data = json.load(file)
        return data


