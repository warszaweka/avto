"""
from .models import ADDRESS_LENGTH, DESCRIPTION_LENGTH, TITLE_LENGTH


class ProcessException(Exception):
    pass


def process_title_input(process_input):
    if len(process_input) > TITLE_LENGTH:
        raise ProcessException("Количество символов превышает " +
                               str(TITLE_LENGTH))
    return process_input


def process_description_input(process_input):
    if len(process_input) > DESCRIPTION_LENGTH:
        raise ProcessException("Количество символов превышает " +
                               str(DESCRIPTION_LENGTH))
    return process_input


def process_stars_input(process_input):
    try:
        process_input = int(process_input)
    except ValueError as error:
        raise ProcessException("Не число") from error
    if process_input < 0 or process_input > 5:
        raise ProcessException("Число выходит за диапазон [0, 5]")
    return process_input


def process_cost_input(process_input, cost_floor=None, cost_ceil=None):
    try:
        process_input = int(process_input)
    except ValueError as error:
        raise ProcessException("Не число") from error
    if process_input < 1 or process_input > 999999:
        raise ProcessException("Число выходит за диапазон [1, 999999]")
    if cost_floor and process_input <= cost_floor:
        raise ProcessException(
            "Верхняя граница диапазона не выше нижней границы")
    if cost_ceil and process_input >= cost_ceil:
        raise ProcessException(
            "Нижняя граница диапазона не ниже верхней границы")
    return process_input
"""
