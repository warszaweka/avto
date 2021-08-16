from re import compile, sub

from requests import get


def process_cost_input(input):
    try:
        input = int(input)
    except Exception:
        return
    if input > 0:
        return input


nv_key = None


def set_nv_key(new_nv_key):
    global nv_key
    nv_key = new_nv_key


phone_sub_pattern = compile(r"^\+?38")


def process_phone_input(input):
    response = get(
        url="http://apilayer.net/api/validate",
        params={
            "access_key": nv_key,
            "number": sub(phone_sub_pattern, "", input),
            "country_code": "UA",
        },
    ).json()
    if response["valid"]:
        return response["local_format"]


def process_address_input(input):
    response = get(
        url="https://nominatim.openstreetmap.org/search",
        params={
            "q": input,
            "format": "json",
            "countrycodes": "UA",
            "limit": "1"
        },
    ).json()
    if response:
        return (response[0]["lat"], response[0]["lon"])
