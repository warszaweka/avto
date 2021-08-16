from sqlalchemy.orm import Session

from models import (ARS_ADDRESS_LENGTH, ARS_DESCRIPTION_LENGTH,
                    ARS_NAME_LENGTH, Ars)
from utils import process_address_input, process_phone_input

engine = None


def set_engine(new_engine):
    global engine
    engine = new_engine


main_id = 0


def main_show(id, state_args):
    return {
        "text": "Главное меню",
        "keyboard": [
            [{"text": "СТО", "callback": arses_id}],
            [{"text": "Аукцион заявок", "callback": requests_id}],
            [{"text": "Кабинет диллера", "callback": diller_id}],
            [{"text": "Кабинет клиента", "callback": client_id}],
        ],
    }


arses_id = 1


def arses_show(id, state_args):
    return {
        "text": "СТО",
        "keyboard": [[{"text": "Назад", "callback": main_id}]],
    }


requests_id = 2


def requests_show(id, state_args):
    return {
        "text": "Аукцион заявок",
        "keyboard": [[{"text": "Назад", "callback": main_id}]],
    }


diller_id = 3


def diller_show(id, state_args):
    return {
        "text": "Кабинет диллера",
        "keyboard": [
            [{"text": "Назад", "callback": main_id}],
            [{"text": "СТО", "callback": diller_arses_id}],
        ],
    }


diller_arses_id = 21


def diller_arses_show(id, state_args):
    with Session(engine) as session:
        arses_list = [
            {"id": ars.id, "name": ars.name}
            for ars in session.query(Ars).where(Ars.user_id == id)
        ]
    return {
        "text": "Кабинет диллера : СТО",
        "keyboard": [
            [
                {"text": "Назад", "callback": diller_id},
                {"text": "Создать", "callback": create_ars_input_name_id},
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


def diller_arses_callback_handler(id, state_args, new_state_id, handler_arg):
    if new_state_id == diller_ars_id:
        state_args["id"] = int(handler_arg)


create_ars_input_name_id = 5


def create_ars_input_name_show(id, state_args):
    return {
        "text": "Введите название",
        "keyboard": [[{"text": "Отменить", "callback": diller_arses_id}]],
    }


def create_ars_input_name_text_handler(id, state_args, content):
    if len(content) <= ARS_NAME_LENGTH:
        state_args["name"] = content
        return create_ars_input_description_id
    state_args["status"] = f"Название должно быть не длиннее {ARS_NAME_LENGTH}"
    return create_ars_input_name_id


create_ars_input_description_id = 6


def create_ars_input_description_show(id, state_args):
    return {
        "text": "Введите описание",
        "keyboard": [
            [{"text": "Назад", "callback": create_ars_input_name_id}],
            [{"text": "Отменить", "callback": diller_arses_id}],
        ],
    }


def create_ars_input_description_callback_handler(
    id, state_args, new_state_id, handler_arg
):
    if new_state_id in [create_ars_input_name_id, diller_arses_id]:
        del state_args["name"]


def create_ars_input_description_text_handler(id, state_args, content):
    if len(content) <= ARS_DESCRIPTION_LENGTH:
        state_args["description"] = content
        return create_ars_input_photo_id
    state_args[
        "status"
    ] = f"Описание должно быть не длиннее {ARS_DESCRIPTION_LENGTH}"
    return create_ars_input_description_id


create_ars_input_photo_id = 7


def create_ars_input_photo_show(id, state_args):
    return {
        "text": "Отправьте фотографию",
        "keyboard": [
            [{"text": "Назад", "callback": create_ars_input_description_id}],
            [{"text": "Пропустить", "callback": create_ars_input_phone_id}],
            [{"text": "Отменить", "callback": diller_arses_id}],
        ],
    }


def create_ars_input_photo_callback_handler(
    id, state_args, new_state_id, handler_arg
):
    if new_state_id in [create_ars_input_description_id, diller_arses_id]:
        del state_args["description"]
        if new_state_id == diller_arses_id:
            del state_args["name"]


def create_ars_input_photo_photo_handler(id, state_args, content):
    state_args["photo"] = content
    return create_ars_input_phone_id


create_ars_input_phone_id = 8


def create_ars_input_phone_show(id, state_args):
    return {
        "text": "Введите номер телефона",
        "keyboard": [
            [{"text": "Назад", "callback": create_ars_input_photo_id}],
            [{"text": "Отменить", "callback": diller_arses_id}],
        ],
    }


def create_ars_input_phone_callback_handler(
    id, state_args, new_state_id, handler_arg
):
    if new_state_id in [create_ars_input_photo_id, diller_arses_id]:
        if "photo" in state_args:
            del state_args["photo"]
        if new_state_id == diller_arses_id:
            del state_args["description"]
            del state_args["name"]


def create_ars_input_phone_text_handler(id, state_args, content):
    content = process_phone_input(content)
    if content is not None:
        state_args["phone"] = content
        return create_ars_input_address_id
    state_args["status"] = "Неверный номер телефона"
    return create_ars_input_phone_id


create_ars_input_address_id = 9


def create_ars_input_address_show(id, state_args):
    return {
        "text": "Введите адрес",
        "keyboard": [
            [{"text": "Назад", "callback": create_ars_input_phone_id}],
            [{"text": "Отменить", "callback": diller_arses_id}],
        ],
    }


def create_ars_input_address_callback_handler(
    id, state_args, new_state_id, handler_arg
):
    if new_state_id in [create_ars_input_phone_id, diller_arses_id]:
        del state_args["phone"]
        if new_state_id == diller_arses_id:
            if "photo" in state_args:
                del state_args["photo"]
            del state_args["description"]
            del state_args["name"]


def create_ars_input_address_text_handler(id, state_args, content):
    if len(content) <= ARS_ADDRESS_LENGTH:
        geo = process_address_input(content)
        if geo is not None:
            with Session(engine) as session:
                ars = Ars(
                    name=state_args["name"],
                    description=state_args["description"],
                    phone=state_args["phone"],
                    address=content,
                    latitude=geo[0],
                    longitude=geo[1],
                    user_id=id,
                )
                if "photo" in state_args:
                    ars.photo = state_args["photo"]
                session.add(ars)
                session.commit()
            del state_args["phone"]
            if "photo" in state_args:
                del state_args["photo"]
            del state_args["description"]
            del state_args["name"]
            return diller_arses_id
        state_args["status"] = "Неверный адрес"
        return create_ars_input_address_id
    state_args["status"] = f"Адрес должен быть не длиннее {ARS_ADDRESS_LENGTH}"
    return create_ars_input_address_id


diller_ars_id = 4


def diller_ars_show(id, state_args):
    with Session(engine) as session:
        ars = session.get(Ars, state_args["id"])
        ars_dict = {
            "name": ars.name,
            "description": ars.description,
            "photo": ars.photo,
            "phone": ars.phone,
            "address": ars.address,
        }
    return {
        "text": f"Название: {ars_dict['name']}\n"
        + f"Описание: {ars_dict['description']}\n"
        + f"Номер телефона: {ars_dict['phone']}\n"
        + f"Адрес: {ars_dict['address']}",
        "photo": ars.photo if ars.photo else None,
        "keyboard": [
            [{"text": "Назад", "callback": diller_arses_id}],
            [
                {
                    "text": "Изменить название",
                    "callback": update_ars_input_name_id,
                }
            ],
            [
                {
                    "text": "Изменить описание",
                    "callback": update_ars_input_description_id,
                }
            ],
            [
                {
                    "text": "Изменить фотографию",
                    "callback": update_ars_input_photo_id,
                }
            ],
            [
                {
                    "text": "Изменить номер телефона",
                    "callback": update_ars_input_phone_id,
                }
            ],
            [
                {
                    "text": "Изменить адрес",
                    "callback": update_ars_input_address_id,
                }
            ],
            [
                {
                    "text": "Удалить",
                    "callback": {
                        "state_id": diller_arses_id,
                        "handler_arg": "delete",
                    },
                }
            ],
        ],
    }


def diller_ars_callback_handler(id, state_args, new_state_id, handler_arg):
    if new_state_id == diller_arses_id:
        if handler_arg == "delete":
            with Session(engine) as session:
                session.delete(session.get(Ars, state_args["id"]))
                session.commit()
        del state_args["id"]


update_ars_input_name_id = 31


def update_ars_input_name_show(id, state_args):
    return {
        "text": "Введите новое название",
        "keyboard": [[{"text": "Отменить", "callback": diller_ars_id}]],
    }


def update_ars_input_name_text_handler(id, state_args, content):
    if len(content) <= ARS_NAME_LENGTH:
        with Session(engine) as session:
            session.get(Ars, state_args["id"]).name = content
            session.commit()
        return diller_ars_id
    state_args["status"] = f"Название должно быть не длиннее {ARS_NAME_LENGTH}"
    return update_ars_input_name_id


update_ars_input_description_id = 32


def update_ars_input_description_show(id, state_args):
    return {
        "text": "Введите новое описание",
        "keyboard": [[{"text": "Отменить", "callback": diller_ars_id}]],
    }


def update_ars_input_description_text_handler(id, state_args, content):
    if len(content) <= ARS_DESCRIPTION_LENGTH:
        with Session(engine) as session:
            session.get(Ars, state_args["id"]).description = content
            session.commit()
        return diller_ars_id
    state_args[
        "status"
    ] = f"Описание должно быть не длиннее {ARS_DESCRIPTION_LENGTH}"
    return update_ars_input_description_id


update_ars_input_photo_id = 33


def update_ars_input_photo_show(id, state_args):
    return {
        "text": "Отпраьте новую фотографию",
        "keyboard": [[{"text": "Отменить", "callback": diller_ars_id}]],
    }


def update_ars_input_photo_photo_handler(id, state_args, content):
    with Session(engine) as session:
        session.get(Ars, state_args["id"]).photo = content
        session.commit()
    return diller_ars_id


update_ars_input_phone_id = 34


def update_ars_input_phone_show(id, state_args):
    return {
        "text": "Введите новый номер телефона",
        "keyboard": [[{"text": "Отменить", "callback": diller_ars_id}]],
    }


def update_ars_input_phone_text_handler(id, state_args, content):
    content = process_phone_input(content)
    if content is not None:
        with Session(engine) as session:
            session.get(Ars, state_args["id"]).phone = content
            session.commit()
        return diller_ars_id
    state_args["status"] = "Неверный номер телефона"
    return update_ars_input_phone_id


update_ars_input_address_id = 35


def update_ars_input_address_show(id, state_args):
    return {
        "text": "Введите новый адрес",
        "keyboard": [[{"text": "Отменить", "callback": diller_ars_id}]],
    }


def update_ars_input_address_text_handler(id, state_args, content):
    if len(content) <= ARS_ADDRESS_LENGTH:
        geo = process_address_input(content)
        if geo is not None:
            with Session(engine) as session:
                ars = session.get(Ars, state_args["id"])
                ars.address = content
                ars.latitude = geo[0]
                ars.longitude = geo[1]
                session.commit()
            return diller_ars_id
        state_args["status"] = "Неверный адрес"
        return update_ars_input_address_id
    state_args["status"] = f"Адрес должен быть не длиннее {ARS_ADDRESS_LENGTH}"
    return update_ars_input_address_id


client_id = 14


def client_show(id, state_args):
    return {
        "text": "Кабинет клиента",
        "keyboard": [[{"text": "Назад", "callback": main_id}]],
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
    update_ars_input_name_id: {"text": update_ars_input_name_text_handler},
    update_ars_input_description_id: {
        "text": update_ars_input_description_text_handler
    },
    update_ars_input_photo_id: {"photo": update_ars_input_photo_photo_handler},
    update_ars_input_phone_id: {"text": update_ars_input_phone_text_handler},
    update_ars_input_address_id: {
        "text": update_ars_input_address_text_handler
    },
}
callback_handlers = {
    diller_arses_id: diller_arses_callback_handler,
    create_ars_input_description_id: create_ars_input_description_callback_handler,
    create_ars_input_photo_id: create_ars_input_photo_callback_handler,
    create_ars_input_phone_id: create_ars_input_phone_callback_handler,
    create_ars_input_address_id: create_ars_input_address_callback_handler,
    diller_ars_id: diller_ars_callback_handler,
}
shows = {
    main_id: main_show,
    arses_id: arses_show,
    requests_id: requests_show,
    diller_id: diller_show,
    diller_arses_id: diller_arses_show,
    create_ars_input_name_id: create_ars_input_name_show,
    create_ars_input_description_id: create_ars_input_description_show,
    create_ars_input_photo_id: create_ars_input_photo_show,
    create_ars_input_phone_id: create_ars_input_phone_show,
    create_ars_input_address_id: create_ars_input_address_show,
    diller_ars_id: diller_ars_show,
    update_ars_input_name_id: update_ars_input_name_show,
    update_ars_input_description_id: update_ars_input_description_show,
    update_ars_input_photo_id: update_ars_input_photo_show,
    update_ars_input_phone_id: update_ars_input_phone_show,
    update_ars_input_address_id: update_ars_input_address_show,
    client_id: client_show,
}
