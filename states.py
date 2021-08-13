from sqlalchemy.orm import Session

from models import (ARS_ADDRESS_LENGTH, ARS_DESCRIPTION_LENGTH,
                    ARS_NAME_LENGTH, PHONE_LENGTH, Ars, ArsSpec)

engine = None


def set_engine(new_engine):
    global engine
    engine = new_engine


main_id = "main"


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


ars_id = "ars"


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


auction_id = "auction"


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


diller_id = "diller"


def diller_show(id, state_args):
    return {
        "text": "Кабинет диллера",
        "keyboard": [
            [
                {
                    "text": "Создать СТО",
                    "callback": {
                        "state_id": create_ars_input_name_id,
                        "handler_arg": "",
                    },
                },
                {
                    "text": "Главное меню",
                    "callback": {"state_id": main_id, "handler_arg": ""},
                },
            ]
        ],
    }


create_ars_input_name_id = "create_ars_input_name"


def create_ars_input_name_text_handler(id, state_args, content):
    if len(content) <= ARS_NAME_LENGTH:
        state_args["name"] = content
        return create_ars_input_description_id
    state_args[
        "status"
    ] = f"Название должно быть короче или равно {ARS_NAME_LENGTH}"
    return create_ars_input_name_id


def create_ars_input_name_show(id, state_args):
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


create_ars_input_description_id = "create_ars_input_description"


def create_ars_input_description_text_handler(id, state_args, content):
    if len(content) <= ARS_DESCRIPTION_LENGTH:
        state_args["description"] = content
        return create_ars_input_photo_id
    state_args[
        "status"
    ] = f"Описание должно быть короче или равно {ARS_DESCRIPTION_LENGTH}"
    return create_ars_input_description_id


def create_ars_input_description_callback_handler(
    id, state_args, new_state_id, handler_arg
):
    del state_args["name"]


def create_ars_input_description_show(id, state_args):
    return {
        "text": "Введите описание",
        "keyboard": [
            [
                {
                    "text": "Назад",
                    "callback": {
                        "state_id": create_ars_input_name_id,
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


create_ars_input_photo_id = "create_ars_input_photo"


def create_ars_input_photo_photo_handler(id, state_args, content):
    state_args["photo"] = content
    return create_ars_input_phone_id


def create_ars_input_photo_callback_handler(
    id, state_args, new_state_id, handler_arg
):
    if new_state_id != create_ars_input_phone_id:
        del state_args["description"]
        if new_state_id == diller_id:
            del state_args["description"]


def create_ars_input_photo_show(id, state_args):
    return {
        "text": "Отправьте фотографию",
        "keyboard": [
            [
                {
                    "text": "Пропустить",
                    "callback": {
                        "state_id": create_ars_input_phone_id,
                        "handler_arg": "",
                    },
                },
                {
                    "text": "Назад",
                    "callback": {
                        "state_id": create_ars_input_description_id,
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


create_ars_input_phone_id = "create_ars_input_phone"


def create_ars_input_phone_text_handler(id, state_args, content):
    if len(content) <= PHONE_LENGTH:
        state_args["phone"] = content
        return create_ars_input_address_id
    state_args[
        "status"
    ] = f"Номер телефона должен быть короче или равно {PHONE_LENGTH}"
    return create_ars_input_phone_id


def create_ars_input_phone_callback_handler(
    id, state_args, new_state_id, handler_arg
):
    if "photo" in state_args:
        del state_args["photo"]
    if new_state_id == diller_id:
        del state_args["name"]
        del state_args["description"]


def create_ars_input_phone_show(id, state_args):
    return {
        "text": "Введите номер телефона",
        "keyboard": [
            [
                {
                    "text": "Назад",
                    "callback": {
                        "state_id": create_ars_input_photo_id,
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


create_ars_input_address_id = "create_ars_input_address"


def create_ars_input_address_text_handler(id, state_args, content):
    if len(content) <= ARS_ADDRESS_LENGTH:
        state_args["address"] = content
        state_args["ars_specs"] = []
        return create_ars_input_ars_specs_id
    state_args["status"] = f"Адрес должен быть короче или равно {PHONE_LENGTH}"
    return create_ars_input_address_id


def create_ars_input_address_callback_handler(
    id, state_args, new_state_id, handler_arg
):
    del state_args["phone"]
    if new_state_id == diller_id:
        del state_args["name"]
        del state_args["description"]
        if "photo" in state_args:
            del state_args["photo"]


def create_ars_input_address_show(id, state_args):
    return {
        "text": "Введите адрес",
        "keyboard": [
            [
                {
                    "text": "Назад",
                    "callback": {
                        "state_id": create_ars_input_phone_id,
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


create_ars_input_ars_specs_id = "create_ars_input_ars_specs"


def create_ars_input_ars_specs_callback_handler(
    id, state_args, new_state_id, handler_arg
):
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
    else:
        del state_args["address"]
        del state_args["ars_specs"]
        if new_state_id == diller_id:
            del state_args["name"]
            del state_args["description"]
            if "photo" in state_args:
                del state_args["photo"]
            del state_args["phone"]


def create_ars_input_ars_specs_show(id, state_args):
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
                        "state_id": create_ars_input_address_id,
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
            ]
        ],
    }


client_id = "client"


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
    create_ars_input_name_id: {"text": create_ars_input_name_text_handler},
    create_ars_input_description_id: {
        "text": create_ars_input_description_text_handler
    },
    create_ars_input_photo_id: {"photo": create_ars_input_photo_photo_handler},
    create_ars_input_phone_id: {"text": create_ars_input_phone_text_handler},
    create_ars_input_address_id: {
        "text": create_ars_input_address_text_handler
    },
}
callback_handlers = {
    create_ars_input_description_id: create_ars_input_description_callback_handler,
    create_ars_input_photo_id: create_ars_input_photo_callback_handler,
    create_ars_input_phone_id: create_ars_input_phone_callback_handler,
    create_ars_input_address_id: create_ars_input_address_callback_handler,
    create_ars_input_ars_specs_id: create_ars_input_ars_specs_callback_handler,
}
shows = {
    main_id: main_show,
    ars_id: ars_show,
    auction_id: auction_show,
    diller_id: diller_show,
    create_ars_input_name_id: create_ars_input_name_show,
    create_ars_input_description_id: create_ars_input_description_show,
    create_ars_input_photo_id: create_ars_input_photo_show,
    create_ars_input_phone_id: create_ars_input_phone_show,
    create_ars_input_address_id: create_ars_input_address_show,
    create_ars_input_ars_specs_id: create_ars_input_ars_specs_show,
    client_id: client_show,
}
