from re import compile, sub

from requests import get

from models import ADDRESS_LENGTH, DESCRIPTION_LENGTH, TITLE_LENGTH

nv_key = None
phone_sub_pattern = compile(r"^\+?38")


def set_nv_key(new_nv_key):
    global nv_key
    nv_key = new_nv_key


def process_title_input(input):
    if len(input) > TITLE_LENGTH:
        raise Exception("Количество символов превышает " + str(TITLE_LENGTH))
    return input


def process_description_input(input):
    if len(input) > DESCRIPTION_LENGTH:
        raise Exception(
            "Количество символов превышает " + str(DESCRIPTION_LENGTH)
        )
    return input


def process_stars_input(input):
    try:
        input = int(input)
    except Exception:
        raise Exception("Не число")
    if input < 0 or input > 5:
        raise Exception("Число выходит за диапазон [0, 5]")
    return input


def process_cost_input(input, cost_floor=None, cost_ceil=None):
    try:
        input = int(input)
    except Exception:
        raise Exception("Не число")
    if input < 1 or input > 999999:
        raise Exception("Число выходит за диапазон [1, 999999]")
    if cost_floor and input <= cost_floor:
        raise Exception("Верхняя граница диапазона не выше нижней границы")
    elif cost_ceil and input >= cost_ceil:
        raise Exception("Нижняя граница диапазона не ниже верхней границы")
    return input


def process_phone_input(input):
    response = get(
        url="http://apilayer.net/api/validate",
        params={
            "access_key": nv_key,
            "number": sub(phone_sub_pattern, "", input),
            "country_code": "UA",
        },
    ).json()
    if not response["valid"]:
        raise Exception("Недействительный номер")
    return response["local_format"]


def process_address_input(input):
    if len(input) > ADDRESS_LENGTH:
        raise Exception("Количество символов превышает " + str(ADDRESS_LENGTH))
    response = get(
        url="https://nominatim.openstreetmap.org/search",
        params={
            "q": input,
            "format": "json",
            "countrycodes": "UA",
            "limit": "1",
        },
    ).json()
    if not response:
        raise Exception("Несуществующий адрес")
    return (response[0]["lat"], response[0]["lon"])
