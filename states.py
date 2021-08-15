from decimal import Decimal

from sqlalchemy.orm import Session

from models import (ARS_ADDRESS_LENGTH, ARS_DESCRIPTION_LENGTH,
                    ARS_NAME_LENGTH, PHONE_LENGTH, Ars, ArsSpec, Spec, User)

engine = None


def set_engine(new_engine):
    global engine
    engine = new_engine


main_id = 0


def main_show(id, state_args):
    return {
        "text": "Главное меню",
        "keyboard": [
            [
                {
                    "text": "СТО",
                    "callback": {"state_id": ars_id, "handler_arg": ""},
                }
            ],
            [
                {
                    "text": "Аукцион заявок",
                    "callback": {"state_id": auction_id, "handler_arg": ""},
                }
            ],
            [
                {
                    "text": "Кабинет диллера",
                    "callback": {"state_id": diller_id, "handler_arg": ""},
                }
            ],
            [
                {
                    "text": "Кабинет клиента",
                    "callback": {"state_id": client_id, "handler_arg": ""},
                }
            ],
        ],
    }


ars_id = 1


def ars_show(id, state_args):
    return {
        "text": "СТО",
        "keyboard": [
            [
                {
                    "text": "Главное меню",
                    "callback": {"state_id": main_id, "handler_arg": ""},
                }
            ]
        ],
    }


auction_id = 2


def auction_show(id, state_args):
    return {
        "text": "Аукцион заявок",
        "keyboard": [
            [
                {
                    "text": "Главное меню",
                    "callback": {"state_id": main_id, "handler_arg": ""},
                }
            ]
        ],
    }


diller_id = 3


def diller_callback_handler(id, state_args, new_state_id, handler_arg):
    if new_state_id == diller_ars_id:
        state_args["id"] = int(handler_arg)


def diller_show(id, state_args):
    with Session(engine) as session:
        arses_list = []
        for ars in session.get(User, id).arses:
            arses_list.append({"id": ars.id, "name": ars.name})
    return {
        "text": "Кабинет диллера",
        "keyboard": [
            [
                {
                    "text": "Создать СТО",
                    "callback": {
                        "state_id": diller_create_ars_input_name_id,
                        "handler_arg": "",
                    },
                },
                {
                    "text": "Главное меню",
                    "callback": {"state_id": main_id, "handler_arg": ""},
                },
            ],
        ]
        + [
            [
                {
                    "text": ars_dict["name"],
                    "callback": {
                        "state_id": diller_ars_id,
                        "handler_arg": ars_dict["id"],
                    },
                }
            ]
            for ars_dict in arses_list
        ],
    }


diller_ars_id = 4


def diller_ars_callback_handler(id, state_args, new_state_id, handler_arg):
    if new_state_id == diller_id:
        del state_args["id"]


def diller_ars_show(id, state_args):
    with Session(engine) as session:
        ars = session.get(Ars, state_args["id"])
        ars_dict = {
            "name": ars.name,
            "description": ars.description,
            "photo": ars.photo,
            "phone": ars.phone,
            "address": ars.address,
            "ars_specs": [
                {
                    "spec_name": ars_spec.spec.name,
                    "cost_floor": ars_spec.cost_floor,
                    "cost_ceil": ars_spec.cost_ceil,
                }
                for ars_spec in ars.ars_specs
            ],
        }
    return {
        "text": f"Название: {ars_dict['name']}\nОписание: {ars_dict['description']}\nНомер телефона: {ars_dict['phone']}\nАдрес: {ars_dict['address']}",
        "photo": ars.photo if ars.photo else None,
        "keyboard": [
            [
                {
                    "text": "Кабинет диллера",
                    "callback": {"state_id": diller_id, "handler_arg": ""},
                }
            ],
        ]
        + [
            [
                {
                    "text": f"{ars_spec_dict['spec_name']} {ars_spec_dict['cost_florr']} {ars_spec_dict['cost_ceil']}",
                    "callback": {
                        "state_id": diller_ars_id,
                        "handler_arg": "",
                    },
                }
            ]
            for ars_spec_dict in ars_dict["ars_specs"]
        ],
    }


diller_create_ars_input_name_id = 5


def diller_create_ars_input_name_text_handler(id, state_args, content):
    if len(content) <= ARS_NAME_LENGTH:
        state_args["name"] = content
        return diller_create_ars_input_description_id
    state_args[
        "status"
    ] = f"Название должно быть короче или равно {ARS_NAME_LENGTH}"
    return diller_create_ars_input_name_id


def diller_create_ars_input_name_show(id, state_args):
    return {
        "text": "Введите название",
        "keyboard": [
            [
                {
                    "text": "Отменить",
                    "callback": {"state_id": diller_id, "handler_arg": ""},
                }
            ]
        ],
    }


diller_create_ars_input_description_id = 6


def diller_create_ars_input_description_text_handler(id, state_args, content):
    if len(content) <= ARS_DESCRIPTION_LENGTH:
        state_args["description"] = content
        return diller_create_ars_input_photo_id
    state_args[
        "status"
    ] = f"Описание должно быть короче или равно {ARS_DESCRIPTION_LENGTH}"
    return diller_create_ars_input_description_id


def diller_create_ars_input_description_callback_handler(
    id, state_args, new_state_id, handler_arg
):
    del state_args["name"]


def diller_create_ars_input_description_show(id, state_args):
    return {
        "text": "Введите описание",
        "keyboard": [
            [
                {
                    "text": "Назад",
                    "callback": {
                        "state_id": diller_create_ars_input_name_id,
                        "handler_arg": "",
                    },
                },
                {
                    "text": "Отменить",
                    "callback": {"state_id": diller_id, "handler_arg": ""},
                },
            ]
        ],
    }


diller_create_ars_input_photo_id = 7


def diller_create_ars_input_photo_photo_handler(id, state_args, content):
    state_args["photo"] = content
    return diller_create_ars_input_phone_id


def diller_create_ars_input_photo_callback_handler(
    id, state_args, new_state_id, handler_arg
):
    if new_state_id != diller_create_ars_input_phone_id:
        del state_args["description"]
        if new_state_id == diller_id:
            del state_args["description"]


def diller_create_ars_input_photo_show(id, state_args):
    return {
        "text": "Отправьте фотографию",
        "keyboard": [
            [
                {
                    "text": "Пропустить",
                    "callback": {
                        "state_id": diller_create_ars_input_phone_id,
                        "handler_arg": "",
                    },
                },
                {
                    "text": "Назад",
                    "callback": {
                        "state_id": diller_create_ars_input_description_id,
                        "handler_arg": "",
                    },
                },
                {
                    "text": "Отменить",
                    "callback": {"state_id": diller_id, "handler_arg": ""},
                },
            ]
        ],
    }


diller_create_ars_input_phone_id = 8


def diller_create_ars_input_phone_text_handler(id, state_args, content):
    if len(content) <= PHONE_LENGTH:
        state_args["phone"] = content
        return diller_create_ars_input_address_id
    state_args[
        "status"
    ] = f"Номер телефона должен быть короче или равно {PHONE_LENGTH}"
    return diller_create_ars_input_phone_id


def diller_create_ars_input_phone_callback_handler(
    id, state_args, new_state_id, handler_arg
):
    if "photo" in state_args:
        del state_args["photo"]
    if new_state_id == diller_id:
        del state_args["name"]
        del state_args["description"]


def diller_create_ars_input_phone_show(id, state_args):
    return {
        "text": "Введите номер телефона",
        "keyboard": [
            [
                {
                    "text": "Назад",
                    "callback": {
                        "state_id": diller_create_ars_input_photo_id,
                        "handler_arg": "",
                    },
                },
                {
                    "text": "Отменить",
                    "callback": {"state_id": diller_id, "handler_arg": ""},
                },
            ]
        ],
    }


diller_create_ars_input_address_id = 9


def diller_create_ars_input_address_text_handler(id, state_args, content):
    if len(content) <= ARS_ADDRESS_LENGTH:
        state_args["address"] = content
        state_args["ars_specs"] = []
        return diller_create_ars_input_ars_specs_id
    state_args["status"] = f"Адрес должен быть короче или равно {PHONE_LENGTH}"
    return diller_create_ars_input_address_id


def diller_create_ars_input_address_callback_handler(
    id, state_args, new_state_id, handler_arg
):
    del state_args["phone"]
    if new_state_id == diller_id:
        del state_args["name"]
        del state_args["description"]
        if "photo" in state_args:
            del state_args["photo"]


def diller_create_ars_input_address_show(id, state_args):
    return {
        "text": "Введите адрес",
        "keyboard": [
            [
                {
                    "text": "Назад",
                    "callback": {
                        "state_id": diller_create_ars_input_phone_id,
                        "handler_arg": "",
                    },
                },
                {
                    "text": "Отменить",
                    "callback": {"state_id": diller_id, "handler_arg": ""},
                },
            ]
        ],
    }


diller_create_ars_input_ars_specs_id = 10


def diller_create_ars_input_ars_specs_callback_handler(
    id, state_args, new_state_id, handler_arg
):
    if (
        new_state_id
        == diller_create_ars_input_ars_specs_add_ars_spec_choose_spec_id
    ):
        state_args["ars_specs"].append({})
        return
    if handler_arg == "create":
        with Session(engine) as session:
            ars = Ars(
                name=state_args["name"],
                description=state_args["description"],
                phone=state_args["phone"],
                address=state_args["address"],
                active=True,
                user_id=id,
            )
            if "photo" in state_args:
                ars.photo = state_args["photo"]
            session.add(ars)
            session.commit()
            ars_id = ars.id
            for ars_spec_dict in state_args["ars_specs"]:
                ars_spec = ArsSpec(
                    ars_id=ars_id,
                    spec_id=ars_spec_dict["spec_id"],
                    cost_floor=ars_spec_dict["cost_floor"],
                )
                if "cost_ceil" in ars_spec_dict:
                    ars_spec.cost_ceil = ars_spec_dict["cost_ceil"]
                session.add(ars_spec)
            session.commit()
    del state_args["address"]
    del state_args["ars_specs"]
    if new_state_id == diller_id:
        del state_args["name"]
        del state_args["description"]
        if "photo" in state_args:
            del state_args["photo"]
        del state_args["phone"]


def diller_create_ars_input_ars_specs_show(id, state_args):
    return {
        "text": "Добавьте специализации",
        "keyboard": [
            [
                {
                    "text": "Продолжить",
                    "callback": {
                        "state_id": diller_id,
                        "handler_arg": "create",
                    },
                },
                {
                    "text": "Назад",
                    "callback": {
                        "state_id": diller_create_ars_input_address_id,
                        "handler_arg": "",
                    },
                },
                {
                    "text": "Отменить",
                    "callback": {
                        "state_id": diller_id,
                        "handler_arg": "",
                    },
                },
                {
                    "text": "Добавить",
                    "callback": {
                        "state_id": diller_create_ars_input_ars_specs_add_ars_spec_choose_spec_id,
                        "handler_arg": "",
                    },
                },
            ]
        ],
    }


diller_create_ars_input_ars_specs_add_ars_spec_choose_spec_id = (
    "diller_create_ars_input_ars_specs_add_ars_spec_choose_spec"
)


def diller_create_ars_input_ars_specs_add_ars_spec_choose_spec_callback_handler(
    id, state_args, new_state_id, handler_arg
):
    if (
        new_state_id
        == diller_create_ars_input_ars_specs_add_ars_spec_input_cost_floor_id
    ):
        state_args["ars_specs"][len(state_args["ars_specs"]) - 1][
            "spec_id"
        ] = int(handler_arg)
    else:
        del state_args["ars_specs"][len(state_args["ars_specs"]) - 1]


def diller_create_ars_input_ars_specs_add_ars_spec_choose_spec_show(
    id, state_args
):
    with Session(engine) as session:
        specs_list = [
            {"id": spec.id, "name": spec.name}
            for spec in session.query(Spec).all()
        ]
    return {
        "text": "Выберите специализацию",
        "keyboard": [
            [
                {
                    "text": "Отменить",
                    "callback": {
                        "state_id": diller_create_ars_input_ars_specs_id,
                        "handler_arg": "",
                    },
                }
            ],
        ]
        + [
            [
                {
                    "text": spec_dict["name"],
                    "callback": {
                        "state_id": diller_create_ars_input_ars_specs_add_ars_spec_input_cost_floor_id,
                        "handler_arg": spec_dict["id"],
                    },
                }
            ]
            for spec_dict in specs_list
        ],
    }


diller_create_ars_input_ars_specs_add_ars_spec_input_cost_floor_id = (
    "diller_create_ars_input_ars_specs_add_ars_spec_input_cost_floor"
)


def diller_create_ars_input_ars_specs_add_ars_spec_input_cost_floor_text_handler(
    id, state_args, content
):
    try:
        state_args["ars_specs"][len(state_args["ars_specs"]) - 1][
            "cost_floor"
        ] = str(Decimal(content))
        return (
            diller_create_ars_input_ars_specs_add_ars_spec_input_cost_ceil_id
        )
    except Exception:
        state_args["status"] = "Ошибка"
        return (
            diller_create_ars_input_ars_specs_add_ars_spec_input_cost_floor_id
        )


def diller_create_ars_input_ars_specs_add_ars_spec_input_cost_floor_callback_handler(
    id, state_args, new_state_id, handler_arg
):
    if (
        new_state_id
        == diller_create_ars_input_ars_specs_add_ars_spec_choose_spec_id
    ):
        del state_args["ars_specs"][len(state_args["ars_specs"]) - 1][
            "spec_id"
        ]
    del state_args["ars_specs"][len(state_args["ars_specs"]) - 1]


def diller_create_ars_input_ars_specs_add_ars_spec_input_cost_floor_show(
    id, state_args
):
    return {
        "text": "Введите нижнюю цену",
        "keyboard": [
            [
                {
                    "text": "Назад",
                    "callback": {
                        "state_id": diller_create_ars_input_ars_specs_add_ars_spec_choose_spec_id,
                        "handler_arg": "",
                    },
                },
                {
                    "text": "Отменить",
                    "callback": {
                        "state_id": diller_create_ars_input_ars_specs_id,
                        "handler_arg": "",
                    },
                },
            ]
        ],
    }


diller_create_ars_input_ars_specs_add_ars_spec_input_cost_ceil_id = (
    "diller_create_ars_input_ars_specs_add_ars_spec_input_ceil_floor"
)


def diller_create_ars_input_ars_specs_add_ars_spec_input_cost_ceil_text_handler(
    id, state_args, content
):
    try:
        state_args["ars_specs"][len(state_args["ars_specs"]) - 1][
            "cost_ceil"
        ] = str(Decimal(content))
        return diller_create_ars_input_ars_specs_id
    except Exception:
        state_args["status"] = "Ошибка"
        return (
            diller_create_ars_input_ars_specs_add_ars_spec_input_cost_ceil_id
        )


def diller_create_ars_input_ars_specs_add_ars_spec_input_cost_ceil_callback_handler(
    id, state_args, new_state_id, handler_arg
):
    if handler_arg != "skip":
        if (
            new_state_id
            == diller_create_ars_input_ars_specs_add_ars_spec_input_cost_floor_id
        ):
            del state_args["ars_specs"][len(state_args["ars_specs"]) - 1][
                "cost_floor"
            ]
        else:
            del state_args["ars_specs"][len(state_args["ars_specs"]) - 1]


def diller_create_ars_input_ars_specs_add_ars_spec_input_cost_ceil_show(
    id, state_args
):
    return {
        "text": "Введите верхнюю цену",
        "keyboard": [
            [
                {
                    "text": "Пропустить",
                    "callback": {
                        "state_id": diller_create_ars_input_ars_specs_id,
                        "handler_arg": "skip",
                    },
                },
                {
                    "text": "Назад",
                    "callback": {
                        "state_id": diller_create_ars_input_ars_specs_add_ars_spec_input_cost_floor_id,
                        "handler_arg": "",
                    },
                },
                {
                    "text": "Отменить",
                    "callback": {
                        "state_id": diller_create_ars_input_ars_specs_id,
                        "handler_arg": "",
                    },
                },
            ]
        ],
    }


client_id = 11


def client_show(id, state_args):
    return {
        "text": "Кабинет клиента",
        "keyboard": [
            [
                {
                    "text": "Главное меню",
                    "callback": {"state_id": main_id, "handler_arg": ""},
                }
            ]
        ],
    }


message_handlers = {
    diller_create_ars_input_name_id: {
        "text": diller_create_ars_input_name_text_handler
    },
    diller_create_ars_input_description_id: {
        "text": diller_create_ars_input_description_text_handler
    },
    diller_create_ars_input_photo_id: {
        "photo": diller_create_ars_input_photo_photo_handler
    },
    diller_create_ars_input_phone_id: {
        "text": diller_create_ars_input_phone_text_handler
    },
    diller_create_ars_input_address_id: {
        "text": diller_create_ars_input_address_text_handler
    },
    diller_create_ars_input_ars_specs_add_ars_spec_input_cost_floor_id: {
        "text": diller_create_ars_input_ars_specs_add_ars_spec_input_cost_floor_text_handler
    },
    diller_create_ars_input_ars_specs_add_ars_spec_input_cost_ceil_id: {
        "text": diller_create_ars_input_ars_specs_add_ars_spec_input_cost_ceil_text_handler
    },
}
callback_handlers = {
    diller_id: diller_callback_handler,
    diller_ars_id: diller_ars_callback_handler,
    diller_create_ars_input_description_id: diller_create_ars_input_description_callback_handler,
    diller_create_ars_input_photo_id: diller_create_ars_input_photo_callback_handler,
    diller_create_ars_input_phone_id: diller_create_ars_input_phone_callback_handler,
    diller_create_ars_input_address_id: diller_create_ars_input_address_callback_handler,
    diller_create_ars_input_ars_specs_id: diller_create_ars_input_ars_specs_callback_handler,
    diller_create_ars_input_ars_specs_add_ars_spec_choose_spec_id: diller_create_ars_input_ars_specs_add_ars_spec_choose_spec_callback_handler,
    diller_create_ars_input_ars_specs_add_ars_spec_input_cost_floor_id: diller_create_ars_input_ars_specs_add_ars_spec_input_cost_floor_callback_handler,
    diller_create_ars_input_ars_specs_add_ars_spec_input_cost_ceil_id: diller_create_ars_input_ars_specs_add_ars_spec_input_cost_ceil_callback_handler,
}
shows = {
    main_id: main_show,
    ars_id: ars_show,
    auction_id: auction_show,
    diller_id: diller_show,
    diller_ars_id: diller_ars_show,
    diller_create_ars_input_name_id: diller_create_ars_input_name_show,
    diller_create_ars_input_description_id: diller_create_ars_input_description_show,
    diller_create_ars_input_photo_id: diller_create_ars_input_photo_show,
    diller_create_ars_input_phone_id: diller_create_ars_input_phone_show,
    diller_create_ars_input_address_id: diller_create_ars_input_address_show,
    diller_create_ars_input_ars_specs_id: diller_create_ars_input_ars_specs_show,
    diller_create_ars_input_ars_specs_add_ars_spec_choose_spec_id: diller_create_ars_input_ars_specs_add_ars_spec_choose_spec_show,
    diller_create_ars_input_ars_specs_add_ars_spec_input_cost_floor_id: diller_create_ars_input_ars_specs_add_ars_spec_input_cost_floor_show,
    diller_create_ars_input_ars_specs_add_ars_spec_input_cost_ceil_id: diller_create_ars_input_ars_specs_add_ars_spec_input_cost_ceil_show,
    client_id: client_show,
}
