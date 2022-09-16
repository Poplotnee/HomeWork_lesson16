import json
from datetime import date


def get_json(path) -> list:
    """ Open json file and get list with Data"""
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)


def convert_to_date(item):
    """ transformation str-object to date format"""
    key = item.split('/')
    result = date(int(key[2]), int(key[0]), int(key[1]))
    return result



