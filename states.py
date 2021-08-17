from sqlalchemy.orm import Session

from models import (Ars, ArsSpec, ArsVendor, Feedback, Offer, Request,
                    RequestSpec, Spec, Vendor)
from processors import (process_address_input, process_cost_input,
                        process_description_input, process_phone_input,
                        process_stars_input, process_title_input)

engine = None


def set_engine(new_engine):
    global engine
    engine = new_engine


main_id = "main"


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


diller_id = "diller"


def diller_show(id, state_args):
    with Session(engine) as session:
        arses_list = [
            {"id": ars.id, "title": ars.title}
            for ars in session.query(Ars).where(Ars.user_id == id)
        ]
    return {
        "text": "Кабинет диллера",
        "keyboard": [
            [
                {"text": "Назад", "callback": main_id},
                {"text": "Создать", "callback": ars_create_title_id},
            ]
        ]
        + [
            [
                {
                    "text": ars_dict["title"],
                    "callback": {
                        "state_id": ars_id,
                        "handler_arg": str(ars_dict["id"]),
                    },
                }
            ]
            for ars_dict in arses_list
        ],
    }


def diller_callback(id, state_args, state_id, handler_arg):
    if state_id == ars_id:
        state_args["ars_return"] = diller_id
        state_args["id"] = int(handler_arg)
    elif state_id == ars_create_title_id:
        state_args["ars_create_return"] = diller_id


client_id = "client"


def client_show(id, state_args):
    with Session(engine) as session:
        requests_list = [
            {"id": request.id, "title": request.title}
            for request in session.query(Request).where(Request.user_id == id)
        ]
    return {
        "text": "Кабинет клиента",
        "keyboard": [
            [
                {"text": "Назад", "callback": main_id},
                {"text": "Создать", "callback": request_create_title_id},
            ]
        ]
        + [
            [
                {
                    "text": request_dict["title"],
                    "callback": {
                        "state_id": request_id,
                        "handler_arg": str(request_dict["id"]),
                    },
                }
            ]
            for request_dict in requests_list
        ],
    }


def client_callback(id, state_args, state_id, handler_arg):
    if state_id == request_id:
        state_args["request_return"] = client_id
        state_args["id"] = int(handler_arg)
    elif state_id == request_create_title_id:
        state_args["request_create_return"] = client_id


arses_id = "arses"


def arses_show(id, state_args):
    with Session(engine) as session:
        arses_list = [
            {"id": ars.id, "title": ars.title}
            for ars in session.query(Ars).all()
        ]
    return {
        "text": "СТО",
        "keyboard": [
            [
                {"text": "Назад", "callback": main_id},
                {"text": "Создать", "callback": ars_create_title_id},
            ]
        ]
        + [
            [
                {
                    "text": ars_dict["title"],
                    "callback": {
                        "state_id": ars_id,
                        "handler_arg": str(ars_dict["id"]),
                    },
                }
            ]
            for ars_dict in arses_list
        ],
    }


def arses_callback(id, state_args, state_id, handler_arg):
    if state_id == ars_id:
        state_args["ars_return"] = arses_id
        state_args["id"] = int(handler_arg)
    elif state_id == ars_create_title_id:
        state_args["ars_create_return"] = arses_id


ars_create_title_id = "ars_create_title"


def ars_create_title_show(id, state_args):
    return {
        "text": "Введите название",
        "keyboard": [
            [{"text": "Отменить", "callback": state_args["ars_create_return"]}]
        ],
    }


def ars_create_title_callback(id, state_args, state_id, handler_arg):
    if state_id == state_args["ars_create_return"]:
        del state_args["ars_create_return"]


def ars_create_title_text(id, state_args, handler_arg):
    try:
        state_args["title"] = process_title_input(handler_arg)
        return ars_create_description_id
    except Exception as e:
        state_args["status"] = str(e)
        return ars_create_title_id


ars_create_description_id = "ars_create_description"


def ars_create_description_show(id, state_args):
    return {
        "text": "Введите описание",
        "keyboard": [
            [{"text": "Назад", "callback": ars_create_title_id}],
            [
                {
                    "text": "Отменить",
                    "callback": state_args["ars_create_return"],
                }
            ],
        ],
    }


def ars_create_description_callback(id, state_args, state_id, handler_arg):
    if state_id in [ars_create_title_id, state_args["ars_create_return"]]:
        del state_args["title"]
        if state_id == state_args["ars_create_return"]:
            del state_args["ars_create_return"]


def ars_create_description_text(id, state_args, handler_arg):
    try:
        state_args["description"] = process_description_input(handler_arg)
        return ars_create_address_id
    except Exception as e:
        state_args["status"] = str(e)
        return ars_create_description_id


ars_create_address_id = "ars_create_address"


def ars_create_address_show(id, state_args):
    return {
        "text": "Введите адрес",
        "keyboard": [
            [{"text": "Назад", "callback": ars_create_description_id}],
            [
                {
                    "text": "Отменить",
                    "callback": state_args["ars_create_return"],
                }
            ],
        ],
    }


def ars_create_address_callback(id, state_args, state_id, handler_arg):
    if state_id in [
        ars_create_description_id,
        state_args["ars_create_return"],
    ]:
        del state_args["description"]
        if state_id == state_args["ars_create_return"]:
            del state_args["title"]
            del state_args["ars_create_return"]


def ars_create_address_text(id, state_args, handler_arg):
    try:
        latitude, longitude = process_address_input(handler_arg)
        state_args["address"] = handler_arg
        state_args["latitude"] = latitude
        state_args["longitude"] = longitude
        return ars_create_phone_id
    except Exception as e:
        state_args["status"] = str(e)
        return ars_create_address_id


ars_create_phone_id = "ars_create_phone"


def ars_create_phone_show(id, state_args):
    return {
        "text": "Введите номер телефона",
        "keyboard": [
            [{"text": "Назад", "callback": ars_create_address_id}],
            [
                {
                    "text": "Отменить",
                    "callback": state_args["ars_create_return"],
                }
            ],
        ],
    }


def ars_create_phone_callback(id, state_args, state_id, handler_arg):
    if state_id in [ars_create_address_id, state_args["ars_create_return"]]:
        del state_args["address"]
        del state_args["latitude"]
        del state_args["longitude"]
        if state_id == state_args["ars_create_return"]:
            del state_args["description"]
            del state_args["title"]
            del state_args["ars_create_return"]


def ars_create_phone_text(id, state_args, handler_arg):
    try:
        state_args["phone"] = process_phone_input(handler_arg)
        return ars_create_picture_id
    except Exception as e:
        state_args["status"] = str(e)
        return ars_create_phone_id


ars_create_picture_id = "ars_create_picture"


def ars_create_picture_show(id, state_args):
    return {
        "text": "Отправьте фотографию",
        "keyboard": [
            [{"text": "Назад", "callback": ars_create_phone_id}],
            [{"text": "Пропустить", "callback": ars_confirm_id}],
            [
                {
                    "text": "Отменить",
                    "callback": state_args["ars_create_return"],
                }
            ],
        ],
    }


def ars_create_picture_callback(id, state_args, state_id, handler_arg):
    if state_id == ars_confirm_id:
        state_args["picture"] = None
    elif state_id in [ars_create_phone_id, state_args["ars_create_return"]]:
        del state_args["phone"]
        if state_id == state_args["ars_create_return"]:
            del state_args["address"]
            del state_args["latitude"]
            del state_args["longitude"]
            del state_args["description"]
            del state_args["title"]
            del state_args["ars_create_return"]


def ars_create_picture_photo(id, state_args, handler_arg):
    state_args["picture"] = handler_arg
    return ars_confirm_id


ars_confirm_id = "ars_confirm"


def ars_confirm_show(id, state_args):
    return {
        "text": "Подтвердите:\nНазвание: "
        + state_args["title"]
        + "\n"
        + "Описание: "
        + state_args["description"]
        + "\n"
        + "Адрес: "
        + state_args["address"]
        + "\n"
        + "Номер телефона: "
        + state_args["phone"],
        "photo": state_args["picture"],
        "keyboard": [
            [{"text": "Назад", "callback": ars_create_picture_id}],
            [
                {
                    "text": "Подтвердить",
                    "callback": {
                        "state_id": state_args["ars_create_return"],
                        "handler_arg": "confirm",
                    },
                }
            ],
            [
                {
                    "text": "Отменить",
                    "callback": state_args["ars_create_return"],
                }
            ],
        ],
    }


def ars_confirm_callback(id, state_args, state_id, handler_arg):
    if state_id in [ars_create_picture_id, state_args["ars_create_return"]]:
        if handler_arg == "confirm":
            with Session(engine) as session:
                session.add(
                    Ars(
                        title=state_args["title"],
                        description=state_args["description"],
                        address=state_args["address"],
                        latitude=state_args["latitude"],
                        longitude=state_args["longitude"],
                        phone=state_args["phone"],
                        picture=state_args["picture"],
                        user_id=id,
                    )
                )
                session.commit()
        del state_args["picture"]
        if state_id == state_args["ars_create_return"]:
            del state_args["phone"]
            del state_args["address"]
            del state_args["latitude"]
            del state_args["longitude"]
            del state_args["description"]
            del state_args["title"]
            del state_args["ars_create_return"]


ars_id = "ars"


def ars_show(id, state_args):
    with Session(engine) as session:
        ars = session.get(Ars, state_args["id"])
        ars_dict = {
            "title": ars.title,
            "description": ars.description,
            "address": ars.address,
            "phone": ars.phone,
            "picture": ars.picture,
        }
        admin = id == ars.user_id
    return {
        "text": "Название: "
        + ars_dict["title"]
        + "\n"
        + "Описание: "
        + ars_dict["description"]
        + "\n"
        + "Адрес: "
        + ars_dict["address"]
        + "\n"
        + "Номер телефона: "
        + ars_dict["phone"],
        "photo": ars_dict["picture"],
        "keyboard": [
            [
                {
                    "text": "Назад",
                    "callback": state_args["ars_return"],
                },
            ],
            [{"text": "Специализации СТО", "callback": ars_specs_id}],
            [{"text": "Вендоры СТО", "callback": ars_vendors_id}],
            [{"text": "Отзывы", "callback": feedbacks_id}],
        ]
        + (
            [
                [
                    {
                        "text": "Изменить название",
                        "callback": ars_edit_title_id,
                    }
                ],
                [
                    {
                        "text": "Изменить описание",
                        "callback": ars_edit_description_id,
                    }
                ],
                [
                    {
                        "text": "Изменить адрес",
                        "callback": ars_edit_address_id,
                    }
                ],
                [
                    {
                        "text": "Изменить номер телефона",
                        "callback": ars_edit_phone_id,
                    }
                ],
                [
                    {
                        "text": "Изменить фотографию",
                        "callback": ars_edit_picture_id,
                    }
                ],
                [
                    {
                        "text": "Удалить",
                        "callback": ars_delete_id,
                    }
                ],
            ]
            if admin
            else []
        ),
    }


def ars_callback(id, state_args, state_id, handler_arg):
    if state_id == state_args["ars_return"]:
        del state_args["id"]
        del state_args["ars_return"]
    elif state_id in [ars_specs_id, ars_vendors_id, feedbacks_id]:
        state_args["ars_id"] = state_args["id"]
        del state_args["id"]


ars_edit_title_id = "ars_edit_title"


def ars_edit_title_show(id, state_args):
    return {
        "text": "Введите новое название",
        "keyboard": [[{"text": "Отменить", "callback": ars_id}]],
    }


def ars_edit_title_text(id, state_args, handler_arg):
    try:
        state_args["title"] = process_title_input(handler_arg)
        return ars_confirm_title_id
    except Exception as e:
        state_args["status"] = str(e)
        return ars_edit_title_id


ars_confirm_title_id = "ars_confirm_title"


def ars_confirm_title_show(id, state_args):
    return {
        "text": "Подтвердите: " + state_args["title"],
        "keyboard": [
            [{"text": "Назад", "callback": ars_edit_title_id}],
            [
                {
                    "text": "Подтвердить",
                    "callback": {"state_id": ars_id, "handler_arg": "confirm"},
                }
            ],
            [{"text": "Отменить", "callback": ars_id}],
        ],
    }


def ars_confirm_title_callback(id, state_args, state_id, handler_arg):
    if state_id in [ars_edit_title_id, ars_id]:
        if handler_arg == "confirm":
            with Session(engine) as session:
                session.get(Ars, state_args["id"]).title = state_args["title"]
                session.commit()
        del state_args["title"]


ars_edit_description_id = "ars_edit_description"


def ars_edit_description_show(id, state_args):
    return {
        "text": "Введите новое описание",
        "keyboard": [[{"text": "Отменить", "callback": ars_id}]],
    }


def ars_edit_description_text(id, state_args, handler_arg):
    try:
        state_args["description"] = process_description_input(handler_arg)
        return ars_confirm_description_id
    except Exception as e:
        state_args["status"] = str(e)
        return ars_edit_description_id


ars_confirm_description_id = "ars_confirm_description"


def ars_confirm_description_show(id, state_args):
    return {
        "text": "Подтвердите: " + state_args["description"],
        "keyboard": [
            [{"text": "Назад", "callback": ars_edit_description_id}],
            [
                {
                    "text": "Подтвердить",
                    "callback": {"state_id": ars_id, "handler_arg": "confirm"},
                }
            ],
            [{"text": "Отменить", "callback": ars_id}],
        ],
    }


def ars_confirm_description_callback(id, state_args, state_id, handler_arg):
    if state_id in [ars_edit_description_id, ars_id]:
        if handler_arg == "confirm":
            with Session(engine) as session:
                session.get(Ars, state_args["id"]).description = state_args[
                    "description"
                ]
                session.commit()
        del state_args["description"]


ars_edit_address_id = "ars_edit_address"


def ars_edit_address_show(id, state_args):
    return {
        "text": "Введите новый адрес",
        "keyboard": [[{"text": "Отменить", "callback": ars_id}]],
    }


def ars_edit_address_text(id, state_args, handler_arg):
    try:
        latitude, longitude = process_address_input(handler_arg)
        state_args["address"] = handler_arg
        state_args["latitude"] = latitude
        state_args["longitude"] = longitude
        return ars_confirm_address_id
    except Exception as e:
        state_args["status"] = str(e)
        return ars_edit_address_id


ars_confirm_address_id = "ars_confirm_address"


def ars_confirm_address_show(id, state_args):
    return {
        "text": "Подтвердите: " + state_args["address"],
        "keyboard": [
            [{"text": "Назад", "callback": ars_edit_address_id}],
            [
                {
                    "text": "Подтвердить",
                    "callback": {"state_id": ars_id, "handler_arg": "confirm"},
                }
            ],
            [{"text": "Отменить", "callback": ars_id}],
        ],
    }


def ars_confirm_address_callback(id, state_args, state_id, handler_arg):
    if state_id in [ars_edit_address_id, ars_id]:
        if handler_arg == "confirm":
            with Session(engine) as session:
                ars = session.get(Ars, state_args["id"])
                ars.address = state_args["address"]
                ars.latitude = state_args["latitude"]
                ars.longitude = state_args["longitude"]
                session.commit()
        del state_args["address"]
        del state_args["latitude"]
        del state_args["longitude"]


ars_edit_phone_id = "ars_edit_phone"


def ars_edit_phone_show(id, state_args):
    return {
        "text": "Введите новый номер телефона",
        "keyboard": [[{"text": "Отменить", "callback": ars_id}]],
    }


def ars_edit_phone_text(id, state_args, handler_arg):
    try:
        state_args["phone"] = process_phone_input(handler_arg)
        return ars_confirm_phone_id
    except Exception as e:
        state_args["status"] = str(e)
        return ars_edit_phone_id


ars_confirm_phone_id = "ars_confirm_phone"


def ars_confirm_phone_show(id, state_args):
    return {
        "text": "Подтвердите: " + state_args["phone"],
        "keyboard": [
            [{"text": "Назад", "callback": ars_edit_phone_id}],
            [
                {
                    "text": "Подтвердить",
                    "callback": {"state_id": ars_id, "handler_arg": "confirm"},
                }
            ],
            [{"text": "Отменить", "callback": ars_id}],
        ],
    }


def ars_confirm_phone_callback(id, state_args, state_id, handler_arg):
    if state_id in [ars_edit_phone_id, ars_id]:
        if handler_arg == "confirm":
            with Session(engine) as session:
                session.get(Ars, state_args["id"]).phone = state_args["phone"]
                session.commit()
        del state_args["phone"]


ars_edit_picture_id = "ars_edit_picture"


def ars_edit_picture_show(id, state_args):
    return {
        "text": "Отправьте новую фотографию",
        "keyboard": [
            [{"text": "Пропустить", "callback": ars_confirm_picture_id}],
            [{"text": "Отменить", "callback": ars_id}],
        ],
    }


def ars_edit_picture_callback(id, state_args, state_id, handler_arg):
    if state_id == ars_confirm_picture_id:
        state_args["picture"] = None


def ars_edit_picture_photo(id, state_args, handler_arg):
    state_args["picture"] = handler_arg
    return ars_confirm_picture_id


ars_confirm_picture_id = "ars_confirm_picture"


def ars_confirm_picture_show(id, state_args):
    return {
        "text": "Подтвердите",
        "photo": state_args["picture"],
        "keyboard": [
            [{"text": "Назад", "callback": ars_edit_picture_id}],
            [
                {
                    "text": "Подтвердить",
                    "callback": {"state_id": ars_id, "handler_arg": "confirm"},
                }
            ],
            [{"text": "Отменить", "callback": ars_id}],
        ],
    }


def ars_confirm_picture_callback(id, state_args, state_id, handler_arg):
    if state_id in [ars_edit_picture_id, ars_id]:
        if handler_arg == "confirm":
            with Session(engine) as session:
                session.get(Ars, state_args["id"]).picture = state_args[
                    "picture"
                ]
                session.commit()
        del state_args["picture"]


ars_delete_id = "ars_delete"


def ars_delete_show(id, state_args):
    return {
        "text": "Подтвердите",
        "keyboard": [
            [{"text": "Подтвердить", "callback": state_args["ars_return"]}],
            [{"text": "Отменить", "callback": ars_id}],
        ],
    }


def ars_delete_callback(id, state_args, state_id, handler_arg):
    if state_id == state_args["ars_return"]:
        with Session(engine) as session:
            session.delete(session.get(Ars, state_args["id"]))
            session.commit()
        del state_args["id"]
        del state_args["ars_return"]


ars_specs_id = "ars_specs"


def ars_specs_show(id, state_args):
    with Session(engine) as session:
        ars_specs_list = [
            {
                "spec_id": ars_spec.spec_id,
                "spec_title": ars_spec.spec.title,
                "cost_floor": ars_spec.cost_floor,
                "cost_ceil": ars_spec.cost_ceil,
            }
            for ars_spec in session.query(ArsSpec).where(
                ArsSpec.ars_id == state_args["ars_id"]
            )
        ]
        admin = id == session.get(Ars, state_args["ars_id"]).user_id
    return {
        "text": "Специализации СТО",
        "keyboard": [
            [
                {"text": "Назад", "callback": ars_id},
            ]
            + (
                [{"text": "Создать", "callback": ars_spec_create_spec_id}]
                if admin
                else []
            )
        ]
        + [
            [
                {
                    "text": ars_spec_dict["spec_title"]
                    + " "
                    + str(ars_spec_dict["cost_floor"])
                    + (
                        (" " + str(ars_spec_dict["cost_ceil"]))
                        if ars_spec_dict["cost_ceil"]
                        else ""
                    ),
                    "callback": {
                        "state_id": ars_spec_id,
                        "handler_arg": str(ars_spec_dict["spec_id"]),
                    },
                }
            ]
            for ars_spec_dict in ars_specs_list
        ],
    }


def ars_specs_callback(id, state_args, state_id, handler_arg):
    if state_id == ars_id:
        state_args["id"] = state_args["ars_id"]
        del state_args["ars_id"]
    if state_id == ars_spec_id:
        state_args["spec_id"] = int(handler_arg)


ars_spec_create_spec_id = "ars_spec_create_spec"


def ars_spec_create_spec_show(id, state_args):
    with Session(engine) as session:
        specs_list = [
            {"id": spec.id, "title": spec.title}
            for spec in session.query(Spec).where(
                Spec.id.not_in(
                    session.query(ArsSpec.spec_id).where(
                        ArsSpec.ars_id == state_args["ars_id"]
                    )
                )
            )
        ]
    return {
        "text": "Выберите специализацию",
        "keyboard": [[{"text": "Отменить", "callback": ars_specs_id}]]
        + [
            [
                {
                    "text": spec_dict["title"],
                    "callback": {
                        "state_id": ars_spec_create_cost_floor_id,
                        "handler_arg": str(spec_dict["id"]),
                    },
                }
            ]
            for spec_dict in specs_list
        ],
    }


def ars_spec_create_spec_callback(id, state_args, state_id, handler_arg):
    if state_id == ars_spec_create_cost_floor_id:
        state_args["spec_id"] = int(handler_arg)


ars_spec_create_cost_floor_id = "ars_spec_create_cost_floor"


def ars_spec_create_cost_floor_show(id, state_args):
    return {
        "text": "Введите нижнюю цену",
        "keyboard": [
            [{"text": "Назад", "callback": ars_spec_create_spec_id}],
            [{"text": "Отменить", "callback": ars_specs_id}],
        ],
    }


def ars_spec_create_cost_floor_callback(id, state_args, state_id, handler_arg):
    if state_id in [ars_spec_create_spec_id, ars_specs_id]:
        del state_args["spec_id"]


def ars_spec_create_cost_floor_text(id, state_args, handler_arg):
    try:
        state_args["cost_floor"] = process_cost_input(handler_arg)
        return ars_spec_create_cost_ceil_id
    except Exception as e:
        state_args["status"] = str(e)
        return ars_spec_create_cost_floor_id


ars_spec_create_cost_ceil_id = "ars_spec_create_cost_ceil"


def ars_spec_create_cost_ceil_show(id, state_args):
    return {
        "text": "Введите верхнюю цену",
        "keyboard": [
            [{"text": "Назад", "callback": ars_spec_create_cost_floor_id}],
            [{"text": "Пропустить", "callback": ars_spec_confirm_id}],
            [{"text": "Отменить", "callback": ars_specs_id}],
        ],
    }


def ars_spec_create_cost_ceil_callback(id, state_args, state_id, handler_arg):
    if state_id == ars_spec_confirm_id:
        state_args["cost_ceil"] = None
    elif state_id in [ars_spec_create_cost_floor_id, ars_specs_id]:
        del state_args["cost_floor"]
        if state_id == ars_specs_id:
            del state_args["spec_id"]


def ars_spec_create_cost_ceil_text(id, state_args, handler_arg):
    try:
        state_args["cost_ceil"] = process_cost_input(
            handler_arg, cost_floor=state_args["cost_floor"]
        )
        return ars_spec_confirm_id
    except Exception as e:
        state_args["status"] = str(e)
        return ars_spec_create_cost_ceil_id


ars_spec_confirm_id = "ars_spec_confirm"


def ars_spec_confirm_show(id, state_args):
    with Session(engine) as session:
        spec_title = session.get(Spec, state_args["spec_id"]).title
    return {
        "text": "Подтвердите:\nСпециализация: "
        + spec_title
        + "\n"
        + "Нижняя цена: "
        + str(state_args["cost_floor"])
        + "\n"
        + "Верхняя цена: "
        + str(state_args["cost_ceil"]),
        "keyboard": [
            [{"text": "Назад", "callback": ars_spec_create_cost_ceil_id}],
            [
                {
                    "text": "Подтвердить",
                    "callback": {
                        "state_id": ars_specs_id,
                        "handler_arg": "confirm",
                    },
                }
            ],
            [{"text": "Отменить", "callback": ars_specs_id}],
        ],
    }


def ars_spec_confirm_callback(id, state_args, state_id, handler_arg):
    if state_id in [ars_spec_create_cost_ceil_id, ars_specs_id]:
        if handler_arg == "confirm":
            with Session(engine) as session:
                session.add(
                    ArsSpec(
                        ars_id=state_args["ars_id"],
                        spec_id=state_args["spec_id"],
                        cost_floor=state_args["cost_floor"],
                        cost_ceil=state_args["cost_ceil"],
                    )
                )
                session.commit()
        del state_args["cost_ceil"]
        if state_id == ars_specs_id:
            del state_args["cost_floor"]
            del state_args["spec_id"]


ars_spec_id = "ars_spec"


def ars_spec_show(id, state_args):
    with Session(engine) as session:
        ars_spec = session.get(
            ArsSpec,
            {"ars_id": state_args["ars_id"], "spec_id": state_args["spec_id"]},
        )
        ars_spec_dict = {
            "spec_title": ars_spec.spec.title,
            "cost_floor": ars_spec.cost_floor,
            "cost_ceil": ars_spec.cost_ceil,
        }
        admin = id == ars_spec.ars.user_id
    return {
        "text": "Специализация: "
        + ars_spec_dict["spec_title"]
        + "\n"
        + "Нижняя цена: "
        + str(ars_spec_dict["cost_floor"])
        + "\n"
        + "Верхняя цена: "
        + str(ars_spec_dict["cost_ceil"]),
        "keyboard": [[{"text": "Назад", "callback": ars_specs_id}]]
        + (
            [
                [
                    {
                        "text": "Изменить нижнюю цену",
                        "callback": ars_spec_edit_cost_floor_id,
                    }
                ],
                [
                    {
                        "text": "Изменить верхнюю цену",
                        "callback": ars_spec_edit_cost_ceil_id,
                    }
                ],
                [
                    {
                        "text": "Удалить",
                        "callback": ars_spec_delete_id,
                    }
                ],
            ]
            if admin
            else []
        ),
    }


def ars_spec_callback(id, state_args, state_id, handler_arg):
    if state_id == ars_specs_id:
        del state_args["spec_id"]


ars_spec_edit_cost_floor_id = "ars_spec_edit_cost_floor"


def ars_spec_edit_cost_floor_show(id, state_args):
    return {
        "text": "Введите новую нижнюю цену",
        "keyboard": [[{"text": "Отменить", "callback": ars_spec_id}]],
    }


def ars_spec_edit_cost_floor_text(id, state_args, handler_arg):
    try:
        with Session(engine) as session:
            cost_ceil = session.get(
                ArsSpec,
                {
                    "ars_id": state_args["ars_id"],
                    "spec_id": state_args["spec_id"],
                },
            ).cost_ceil
        state_args["cost_floor"] = process_cost_input(
            handler_arg, cost_ceil=cost_ceil
        )
        return ars_spec_confirm_cost_floor_id
    except Exception as e:
        state_args["status"] = str(e)
        return ars_spec_edit_cost_floor_id


ars_spec_confirm_cost_floor_id = "ars_spec_confirm_cost_floor"


def ars_spec_confirm_cost_floor_show(id, state_args):
    return {
        "text": "Подтвердите: " + str(state_args["cost_floor"]),
        "keyboard": [
            [{"text": "Назад", "callback": ars_spec_edit_cost_floor_id}],
            [
                {
                    "text": "Подтвердить",
                    "callback": {
                        "state_id": ars_spec_id,
                        "handler_arg": "confirm",
                    },
                }
            ],
            [{"text": "Отменить", "callback": ars_spec_id}],
        ],
    }


def ars_spec_confirm_cost_floor_id(id, state_args, state_id, handler_arg):
    if state_id in [ars_spec_edit_cost_floor_id, ars_spec_id]:
        if handler_arg == "confirm":
            with Session(engine) as session:
                session.get(
                    ArsSpec,
                    {
                        "ars_id": state_args["ars_id"],
                        "spec_id": state_args["spec_id"],
                    },
                ).cost_floor = state_args["cost_floor"]
                session.commit()
        del state_args["cost_floor"]


ars_spec_edit_cost_ceil_id = "ars_spec_edit_cost_ceil"


def ars_spec_edit_cost_ceil_show(id, state_args):
    return {
        "text": "Введите новую верхнюю цену",
        "keyboard": [
            [
                {
                    "text": "Пропустить",
                    "calblack": ars_spec_confirm_cost_ceil_id,
                }
            ],
            [{"text": "Отменить", "callback": ars_spec_id}],
        ],
    }


def ars_spec_edit_cost_ceil_callback(id, state_args, state_id, handler_arg):
    if state_id == ars_spec_confirm_cost_ceil_id:
        state_args["cost_ceil"] = None


def ars_spec_edit_cost_ceil_text(id, state_args, handler_arg):
    try:
        with Session(engine) as session:
            cost_floor = session.get(
                ArsSpec,
                {
                    "ars_id": state_args["ars_id"],
                    "spec_id": state_args["spec_id"],
                },
            ).cost_floor
        state_args["cost_ceil"] = process_cost_input(
            handler_arg, cost_floor=cost_floor
        )
        return ars_spec_confirm_cost_ceil_id
    except Exception as e:
        state_args["status"] = str(e)
        return ars_spec_edit_cost_ceil_id


ars_spec_confirm_cost_ceil_id = "ars_spec_confirm_cost_ceil"


def ars_spec_confirm_cost_ceil_show(id, state_args):
    return {
        "text": "Подтвердите: " + str(state_args["cost_ceil"]),
        "keyboard": [
            [{"text": "Назад", "callback": ars_spec_edit_cost_ceil_id}],
            [
                {
                    "text": "Подтвердить",
                    "callback": {
                        "state_id": ars_spec_id,
                        "handler_arg": "confirm",
                    },
                }
            ],
            [{"text": "Отменить", "callback": ars_spec_id}],
        ],
    }


def ars_spec_confirm_cost_ceil_id(id, state_args, state_id, handler_arg):
    if state_id in [ars_spec_edit_cost_ceil_id, ars_spec_id]:
        if handler_arg == "confirm":
            with Session(engine) as session:
                session.get(
                    ArsSpec,
                    {
                        "ars_id": state_args["ars_id"],
                        "spec_id": state_args["spec_id"],
                    },
                ).cost_ceil = state_args["cost_ceil"]
                session.commit()
        del state_args["cost_ceil"]


ars_spec_delete_id = "ars_spec_delete"


def ars_spec_delete_show(id, state_args):
    return {
        "text": "Подтвердите",
        "keyboard": [
            [{"text": "Подтвердить", "callback": ars_specs_id}],
            [{"text": "Отменить", "callback": ars_spec_id}],
        ],
    }


def ars_spec_delete_callback(id, state_args, state_id, handler_arg):
    if state_id == ars_specs_id:
        with Session(engine) as session:
            session.delete(
                session.get(
                    ArsSpec,
                    {
                        "ars_id": state_args["ars_id"],
                        "spec_id": state_args["spec_id"],
                    },
                )
            )
            session.commit()
        del state_args["spec_id"]


ars_vendors_id = "ars_vendors"


def ars_vendors_show(id, state_args):
    with Session(engine) as session:
        ars_vendors_list = [
            {
                "vendor_id": ars_vendor.vendor_id,
                "vendor_title": ars_vendor.vendor.title,
            }
            for ars_vendor in session.query(ArsVendor).where(
                ArsVendor.ars_id == state_args["ars_id"]
            )
        ]
        admin = id == session.get(Ars, state_args["ars_id"]).user_id
    return {
        "text": "Вендоры СТО",
        "keyboard": [
            [
                {"text": "Назад", "callback": ars_id},
            ]
            + (
                [{"text": "Создать", "callback": ars_vendor_create_vendor_id}]
                if admin
                else []
            )
        ]
        + [
            [
                {
                    "text": ars_vendor_dict["vendor_title"],
                    "callback": {
                        "state_id": ars_vendor_id,
                        "handler_arg": str(ars_vendor_dict["vendor_id"]),
                    },
                }
            ]
            for ars_vendor_dict in ars_vendors_list
        ],
    }


def ars_vendors_callback(id, state_args, state_id, handler_arg):
    if state_id == ars_id:
        state_args["id"] = state_args["ars_id"]
        del state_args["ars_id"]
    if state_id == ars_vendor_id:
        state_args["vendor_id"] = int(handler_arg)


ars_vendor_create_vendor_id = "ars_vendor_create_vendor"


def ars_vendor_create_vendor_show(id, state_args):
    with Session(engine) as session:
        vendors_list = [
            {"id": vendor.id, "title": vendor.title}
            for vendor in session.query(Vendor).where(
                Vendor.id.not_in(
                    session.query(ArsVendor.vendor_id).where(
                        ArsVendor.ars_id == state_args["ars_id"]
                    )
                )
            )
        ]
    return {
        "text": "Выберите вендор",
        "keyboard": [[{"text": "Отменить", "callback": ars_vendors_id}]]
        + [
            [
                {
                    "text": vendor_dict["title"],
                    "callback": {
                        "state_id": ars_vendor_confirm_id,
                        "handler_arg": str(vendor_dict["id"]),
                    },
                }
            ]
            for vendor_dict in vendors_list
        ],
    }


def ars_vendor_create_vendor_callback(id, state_args, state_id, handler_arg):
    if state_id == ars_vendor_confirm_id:
        state_args["vendor_id"] = int(handler_arg)


ars_vendor_confirm_id = "ars_vendor_confirm"


def ars_vendor_confirm_show(id, state_args):
    with Session(engine) as session:
        vendor_title = session.get(Vendor, state_args["vendor_id"]).title
    return {
        "text": "Подтвердите:\nВендор: " + vendor_title,
        "keyboard": [
            [{"text": "Назад", "callback": ars_vendor_create_vendor_id}],
            [
                {
                    "text": "Подтвердить",
                    "callback": {
                        "state_id": ars_vendors_id,
                        "handler_arg": "confirm",
                    },
                }
            ],
            [{"text": "Отменить", "callback": ars_vendors_id}],
        ],
    }


def ars_vendor_confirm_callback(id, state_args, state_id, handler_arg):
    if state_id in [ars_vendor_create_vendor_id, ars_vendors_id]:
        if handler_arg == "confirm":
            with Session(engine) as session:
                session.add(
                    ArsVendor(
                        ars_id=state_args["ars_id"],
                        vendor_id=state_args["vendor_id"],
                    )
                )
                session.commit()
        del state_args["vendor_id"]


ars_vendor_id = "ars_vendor"


def ars_vendor_show(id, state_args):
    with Session(engine) as session:
        ars_vendor = session.get(
            ArsVendor,
            {
                "ars_id": state_args["ars_id"],
                "vendor_id": state_args["vendor_id"],
            },
        )
        vendor_title = ars_vendor.vendor.title
        admin = id == ars_vendor.ars.user_id
    return {
        "text": "Вендор: " + vendor_title,
        "keyboard": [[{"text": "Назад", "callback": ars_vendors_id}]]
        + (
            [
                [{"text": "Удалить", "callback": ars_vendor_delete_id}],
            ]
            if admin
            else []
        ),
    }


def ars_vendor_callback(id, state_args, state_id, handler_arg):
    if state_id == ars_vendors_id:
        del state_args["vendor_id"]


ars_vendor_delete_id = "ars_vendor_delete"


def ars_vendor_delete_show(id, state_args):
    return {
        "text": "Подтвердите",
        "keyboard": [
            [{"text": "Подтвердить", "callback": ars_vendors_id}],
            [{"text": "Отменить", "callback": ars_vendor_id}],
        ],
    }


def ars_vendor_delete_callback(id, state_args, state_id, handler_arg):
    if state_id == ars_vendors_id:
        with Session(engine) as session:
            session.delete(
                session.get(
                    ArsVendor,
                    {
                        "ars_id": state_args["ars_id"],
                        "vendor_id": state_args["vendor_id"],
                    },
                )
            )
            session.commit()
        del state_args["vendor_id"]


feedbacks_id = "feedbacks"


def feedbacks_show(id, state_args):
    with Session(engine) as session:
        feedbacks_list = [
            {
                "user_id": feedback.user_id,
                "stars": feedback.stars,
                "title": feedback.title,
            }
            for feedback in session.query(Feedback).where(
                Feedback.ars_id == state_args["ars_id"]
            )
        ]
        admin = (
            session.get(
                Feedback, {"ars_id": state_args["ars_id"], "user_id": id}
            )
            is not None
        )
    return {
        "text": "Отзывы",
        "keyboard": [
            [
                {"text": "Назад", "callback": ars_id},
            ]
            + (
                []
                if admin
                else [
                    {"text": "Создать", "callback": feedback_create_stars_id}
                ]
            )
        ]
        + [
            [
                {
                    "text": str(feedback_dict["stars"])
                    + " "
                    + feedback_dict["title"],
                    "callback": {
                        "state_id": feedback_id,
                        "handler_arg": str(feedback_dict["user_id"]),
                    },
                }
            ]
            for feedback_dict in feedbacks_list
        ],
    }


def feedbacks_callback(id, state_args, state_id, handler_arg):
    if state_id == ars_id:
        state_args["id"] = state_args["ars_id"]
        del state_args["ars_id"]
    if state_id == feedback_id:
        state_args["user_id"] = int(handler_arg)


feedback_create_stars_id = "feedback_create_stars"


def feedback_create_stars_show(id, state_args):
    return {
        "text": "Введите количество звезд",
        "keyboard": [[{"text": "Отменить", "callback": feedbacks_id}]],
    }


def feedback_create_stars_text(id, state_args, handler_arg):
    try:
        state_args["stars"] = process_stars_input(handler_arg)
        return feedback_create_title_id
    except Exception as e:
        state_args["status"] = str(e)
        return feedback_create_stars_id


feedback_create_title_id = "feedback_create_title"


def feedback_create_title_show(id, state_args):
    return {
        "text": "Введите заголовок",
        "keyboard": [
            [{"text": "Назад", "callback": feedback_create_stars_id}],
            [{"text": "Отменить", "callback": feedbacks_id}],
        ],
    }


def feedback_create_title_callback(id, state_args, state_id, handler_arg):
    if state_id in [feedback_create_stars_id, feedbacks_id]:
        del state_args["stars"]


def feedback_create_title_text(id, state_args, handler_arg):
    try:
        state_args["title"] = process_title_input(handler_arg)
        return feedback_create_description_id
    except Exception as e:
        state_args["status"] = str(e)
        return feedback_create_title_id


feedback_create_description_id = "feedback_create_description"


def feedback_create_description_show(id, state_args):
    return {
        "text": "Введите описание",
        "keyboard": [
            [{"text": "Назад", "callback": feedback_create_title_id}],
            [{"text": "Отменить", "callback": feedbacks_id}],
        ],
    }


def feedback_create_description_callback(
    id, state_args, state_id, handler_arg
):
    if state_id in [feedback_create_title_id, feedbacks_id]:
        del state_args["title"]
        if state_id == feedbacks_id:
            del state_args["stars"]


def feedback_create_description_text(id, state_args, handler_arg):
    try:
        state_args["description"] = process_description_input(handler_arg)
        return feedback_confirm_id
    except Exception as e:
        state_args["status"] = str(e)
        return feedback_create_description_id


feedback_confirm_id = "feedback_confirm"


def feedback_confirm_show(id, state_args):
    return {
        "text": "Подтвердите:\nКоличество звезд: "
        + str(state_args["stars"])
        + "\n"
        + "Заголовок: "
        + state_args["title"]
        + "\n"
        + "Описание: "
        + state_args["description"],
        "keyboard": [
            [{"text": "Назад", "callback": feedback_create_description_id}],
            [
                {
                    "text": "Подтвердить",
                    "callback": {
                        "state_id": feedbacks_id,
                        "handler_arg": "confirm",
                    },
                }
            ],
            [{"text": "Отменить", "callback": feedbacks_id}],
        ],
    }


def feedback_confirm_callback(id, state_args, state_id, handler_arg):
    if state_id in [feedback_create_description_id, feedbacks_id]:
        if handler_arg == "confirm":
            with Session(engine) as session:
                session.add(
                    Feedback(
                        ars_id=state_args["ars_id"],
                        user_id=id,
                        stars=state_args["stars"],
                        title=state_args["title"],
                        description=state_args["description"],
                    )
                )
                session.commit()
        del state_args["description"]
        if state_id == feedbacks_id:
            del state_args["title"]
            del state_args["stars"]


feedback_id = "feedback"


def feedback_show(id, state_args):
    with Session(engine) as session:
        feedback = session.get(
            Feedback,
            {"ars_id": state_args["ars_id"], "user_id": state_args["user_id"]},
        )
        feedback_dict = {
            "stars": feedback.stars,
            "title": feedback.title,
            "description": feedback.description,
        }
    admin = id == state_args["user_id"]
    return {
        "text": "Количество звезд: "
        + str(feedback_dict["stars"])
        + "\n"
        + "Заголовок: "
        + feedback_dict["title"]
        + "\n"
        + "Описание: "
        + feedback_dict["description"],
        "keyboard": [[{"text": "Назад", "callback": feedbacks_id}]]
        + (
            [
                [
                    {
                        "text": "Изменить количество звезд",
                        "callback": feedback_edit_stars_id,
                    }
                ],
                [
                    {
                        "text": "Изменить заголовок",
                        "callback": feedback_edit_title_id,
                    }
                ],
                [
                    {
                        "text": "Изменить описание",
                        "callback": feedback_edit_description_id,
                    }
                ],
                [
                    {
                        "text": "Удалить",
                        "callback": feedback_delete_id,
                    }
                ],
            ]
            if admin
            else []
        ),
    }


def feedback_callback(id, state_args, state_id, handler_arg):
    if state_id == feedbacks_id:
        del state_args["user_id"]


feedback_edit_stars_id = "feedback_edit_stars"


def feedback_edit_stars_show(id, state_args):
    return {
        "text": "Введите новое количество звезд",
        "keyboard": [[{"text": "Отменить", "callback": feedback_id}]],
    }


def feedback_edit_stars_text(id, state_args, handler_arg):
    try:
        state_args["stars"] = process_stars_input(handler_arg)
        return feedback_confirm_stars_id
    except Exception as e:
        state_args["status"] = str(e)
        return feedback_edit_stars_id


feedback_confirm_stars_id = "feedback_confirm_stars"


def feedback_confirm_stars_show(id, state_args):
    return {
        "text": "Подтвердите: " + str(state_args["stars"]),
        "keyboard": [
            [{"text": "Назад", "callback": feedback_edit_stars_id}],
            [
                {
                    "text": "Подтвердить",
                    "callback": {
                        "state_id": feedback_id,
                        "handler_arg": "confirm",
                    },
                }
            ],
            [{"text": "Отменить", "callback": feedback_id}],
        ],
    }


def feedback_confirm_stars_callback(id, state_args, state_id, handler_arg):
    if state_id in [feedback_edit_stars_id, feedback_id]:
        if handler_arg == "confirm":
            with Session(engine) as session:
                session.get(
                    Feedback,
                    {
                        "ars_id": state_args["ars_id"],
                        "user_id": state_args["user_id"],
                    },
                ).stars = state_args["stars"]
                session.commit()
        del state_args["stars"]


feedback_edit_title_id = "feedback_edit_title"


def feedback_edit_title_show(id, state_args):
    return {
        "text": "Введите новый заголовок",
        "keyboard": [[{"text": "Отменить", "callback": feedback_id}]],
    }


def feedback_edit_title_text(id, state_args, handler_arg):
    try:
        state_args["title"] = process_title_input(handler_arg)
        return feedback_confirm_title_id
    except Exception as e:
        state_args["status"] = str(e)
        return feedback_edit_title_id


feedback_confirm_title_id = "feedback_confirm_title"


def feedback_confirm_title_show(id, state_args):
    return {
        "text": "Подтвердите: " + state_args["title"],
        "keyboard": [
            [{"text": "Назад", "callback": feedback_edit_title_id}],
            [
                {
                    "text": "Подтвердить",
                    "callback": {
                        "state_id": feedback_id,
                        "handler_arg": "confirm",
                    },
                }
            ],
            [{"text": "Отменить", "callback": feedback_id}],
        ],
    }


def feedback_confirm_title_callback(id, state_args, state_id, handler_arg):
    if state_id in [feedback_edit_title_id, feedback_id]:
        if handler_arg == "confirm":
            with Session(engine) as session:
                session.get(
                    Feedback,
                    {
                        "ars_id": state_args["ars_id"],
                        "user_id": state_args["user_id"],
                    },
                ).title = state_args["title"]
                session.commit()
        del state_args["title"]


feedback_edit_description_id = "feedback_edit_description"


def feedback_edit_description_show(id, state_args):
    return {
        "text": "Введите новое описание",
        "keyboard": [[{"text": "Отменить", "callback": feedback_id}]],
    }


def feedback_edit_description_text(id, state_args, handler_arg):
    try:
        state_args["description"] = process_description_input(handler_arg)
        return feedback_confirm_description_id
    except Exception as e:
        state_args["status"] = str(e)
        return feedback_edit_description_id


feedback_confirm_description_id = "feedback_confirm_description"


def feedback_confirm_description_show(id, state_args):
    return {
        "text": "Подтвердите: " + state_args["description"],
        "keyboard": [
            [{"text": "Назад", "callback": feedback_edit_description_id}],
            [
                {
                    "text": "Подтвердить",
                    "callback": {
                        "state_id": feedback_id,
                        "handler_arg": "confirm",
                    },
                }
            ],
            [{"text": "Отменить", "callback": feedback_id}],
        ],
    }


def feedback_confirm_description_callback(
    id, state_args, state_id, handler_arg
):
    if state_id in [feedback_edit_description_id, feedback_id]:
        if handler_arg == "confirm":
            with Session(engine) as session:
                session.get(
                    Feedback,
                    {
                        "ars_id": state_args["ars_id"],
                        "user_id": state_args["user_id"],
                    },
                ).description = state_args["description"]
                session.commit()
        del state_args["description"]


feedback_delete_id = "feedback_delete"


def feedback_delete_show(id, state_args):
    return {
        "text": "Подтвердите",
        "keyboard": [
            [{"text": "Подтвердить", "callback": feedbacks_id}],
            [{"text": "Отменить", "callback": feedback_id}],
        ],
    }


def feedback_delete_callback(id, state_args, state_id, handler_arg):
    if state_id == feedbacks_id:
        with Session(engine) as session:
            session.delete(
                session.get(
                    Feedback,
                    {
                        "ars_id": state_args["ars_id"],
                        "user_id": state_args["user_id"],
                    },
                )
            )
            session.commit()
        del state_args["user_id"]


requests_id = "requests"


def requests_show(id, state_args):
    with Session(engine) as session:
        requests_list = [
            {"id": request.id, "title": request.title}
            for request in session.query(Request).all()
        ]
    return {
        "text": "Аукцион заявок",
        "keyboard": [
            [
                {"text": "Назад", "callback": main_id},
                {"text": "Создать", "callback": request_create_title_id},
            ]
        ]
        + [
            [
                {
                    "text": request_dict["title"],
                    "callback": {
                        "state_id": request_id,
                        "handler_arg": str(request_dict["id"]),
                    },
                }
            ]
            for request_dict in requests_list
        ],
    }


def requests_callback(id, state_args, state_id, handler_arg):
    if state_id == request_id:
        state_args["request_return"] = requests_id
        state_args["id"] = int(handler_arg)
    elif state_id == request_create_title_id:
        state_args["request_create_return"] = requests_id


request_create_title_id = "request_create_title"


def request_create_title_show(id, state_args):
    return {
        "text": "Введите заголовок",
        "keyboard": [
            [
                {
                    "text": "Отменить",
                    "callback": state_args["request_create_return"],
                }
            ]
        ],
    }


def request_create_title_callback(id, state_args, state_id, handler_arg):
    if state_id == state_args["request_create_return"]:
        del state_args["request_create_return"]


def request_create_title_text(id, state_args, handler_arg):
    try:
        state_args["title"] = process_title_input(handler_arg)
        return request_create_description_id
    except Exception as e:
        state_args["status"] = str(e)
        return request_create_title_id


request_create_description_id = "request_create_description"


def request_create_description_show(id, state_args):
    return {
        "text": "Введите описание",
        "keyboard": [
            [{"text": "Назад", "callback": request_create_title_id}],
            [
                {
                    "text": "Отменить",
                    "callback": state_args["request_create_return"],
                }
            ],
        ],
    }


def request_create_description_callback(id, state_args, state_id, handler_arg):
    if state_id in [
        request_create_title_id,
        state_args["request_create_return"],
    ]:
        del state_args["title"]
        if state_id == state_args["request_create_return"]:
            del state_args["request_create_return"]


def request_create_description_text(id, state_args, handler_arg):
    try:
        state_args["description"] = process_description_input(handler_arg)
        return request_create_phone_id
    except Exception as e:
        state_args["status"] = str(e)
        return request_create_description_id


request_create_phone_id = "request_create_phone"


def request_create_phone_show(id, state_args):
    return {
        "text": "Введите номер телефона",
        "keyboard": [
            [{"text": "Назад", "callback": request_create_description_id}],
            [
                {
                    "text": "Отменить",
                    "callback": state_args["request_create_return"],
                }
            ],
        ],
    }


def request_create_phone_callback(id, state_args, state_id, handler_arg):
    if state_id in [
        request_create_description_id,
        state_args["request_create_return"],
    ]:
        del state_args["description"]
        if state_id == state_args["request_create_return"]:
            del state_args["title"]
            del state_args["request_create_return"]


def request_create_phone_text(id, state_args, handler_arg):
    try:
        state_args["phone"] = process_phone_input(handler_arg)
        return request_create_picture_id
    except Exception as e:
        state_args["status"] = str(e)
        return request_create_phone_id


request_create_picture_id = "request_create_picture"


def request_create_picture_show(id, state_args):
    return {
        "text": "Отправьте фотографию",
        "keyboard": [
            [{"text": "Назад", "callback": request_create_phone_id}],
            [{"text": "Пропустить", "callback": request_confirm_id}],
            [
                {
                    "text": "Отменить",
                    "callback": state_args["request_create_return"],
                }
            ],
        ],
    }


def request_create_picture_callback(id, state_args, state_id, handler_arg):
    if state_id == request_confirm_id:
        state_args["picture"] = None
    elif state_id in [
        request_create_phone_id,
        state_args["request_create_return"],
    ]:
        del state_args["phone"]
        if state_id == state_args["request_create_return"]:
            del state_args["description"]
            del state_args["title"]
            del state_args["request_create_return"]


def request_create_picture_photo(id, state_args, handler_arg):
    state_args["picture"] = handler_arg
    return request_confirm_id


request_confirm_id = "request_confirm"


def request_confirm_show(id, state_args):
    return {
        "text": "Подтвердите:\nЗаголовок: "
        + state_args["title"]
        + "\n"
        + "Описание: "
        + state_args["description"]
        + "\n"
        + "Номер телефона: "
        + state_args["phone"],
        "photo": state_args["picture"],
        "keyboard": [
            [{"text": "Назад", "callback": request_create_picture_id}],
            [
                {
                    "text": "Подтвердить",
                    "callback": {
                        "state_id": state_args["request_create_return"],
                        "handler_arg": "confirm",
                    },
                }
            ],
            [
                {
                    "text": "Отменить",
                    "callback": state_args["request_create_return"],
                }
            ],
        ],
    }


def request_confirm_callback(id, state_args, state_id, handler_arg):
    if state_id in [
        request_create_picture_id,
        state_args["request_create_return"],
    ]:
        if handler_arg == "confirm":
            with Session(engine) as session:
                session.add(
                    Request(
                        title=state_args["title"],
                        description=state_args["description"],
                        phone=state_args["phone"],
                        picture=state_args["picture"],
                        user_id=id,
                    )
                )
                session.commit()
        del state_args["picture"]
        if state_id == state_args["request_create_return"]:
            del state_args["phone"]
            del state_args["description"]
            del state_args["title"]
            del state_args["request_create_return"]


request_id = "request"


def request_show(id, state_args):
    with Session(engine) as session:
        request = session.get(Request, state_args["id"])
        request_dict = {
            "title": request.title,
            "description": request.description,
            "phone": request.phone,
            "picture": request.picture,
        }
        admin = id == request.user_id
    return {
        "text": "Заголовок: "
        + request_dict["title"]
        + "\n"
        + "Описание: "
        + request_dict["description"]
        + "\n"
        + "Номер телефона: "
        + request_dict["phone"],
        "photo": request_dict["picture"],
        "keyboard": [
            [
                {
                    "text": "Назад",
                    "callback": state_args["request_return"],
                },
            ],
            [{"text": "Специализации Заявки", "callback": request_specs_id}],
            [{"text": "Офферы", "callback": offers_id}],
        ]
        + (
            [
                [
                    {
                        "text": "Изменить заголовок",
                        "callback": request_edit_title_id,
                    }
                ],
                [
                    {
                        "text": "Изменить описание",
                        "callback": request_edit_description_id,
                    }
                ],
                [
                    {
                        "text": "Изменить номер телефона",
                        "callback": request_edit_phone_id,
                    }
                ],
                [
                    {
                        "text": "Изменить фотографию",
                        "callback": request_edit_picture_id,
                    }
                ],
                [
                    {
                        "text": "Удалить",
                        "callback": request_delete_id,
                    }
                ],
            ]
            if admin
            else []
        ),
    }


def request_callback(id, state_args, state_id, handler_arg):
    if state_id == state_args["request_return"]:
        del state_args["id"]
        del state_args["request_return"]
    elif state_id in [request_specs_id, offers_id]:
        state_args["request_id"] = state_args["id"]
        del state_args["id"]


request_edit_title_id = "request_edit_title"


def request_edit_title_show(id, state_args):
    return {
        "text": "Введите новый заголовок",
        "keyboard": [[{"text": "Отменить", "callback": request_id}]],
    }


def request_edit_title_text(id, state_args, handler_arg):
    try:
        state_args["title"] = process_title_input(handler_arg)
        return request_confirm_title_id
    except Exception as e:
        state_args["status"] = str(e)
        return request_edit_title_id


request_confirm_title_id = "request_confirm_title"


def request_confirm_title_show(id, state_args):
    return {
        "text": "Подтвердите: " + state_args["title"],
        "keyboard": [
            [{"text": "Назад", "callback": request_edit_title_id}],
            [
                {
                    "text": "Подтвердить",
                    "callback": {
                        "state_id": request_id,
                        "handler_arg": "confirm",
                    },
                }
            ],
            [{"text": "Отменить", "callback": request_id}],
        ],
    }


def request_confirm_title_callback(id, state_args, state_id, handler_arg):
    if state_id in [request_edit_title_id, request_id]:
        if handler_arg == "confirm":
            with Session(engine) as session:
                session.get(Request, state_args["id"]).title = state_args[
                    "title"
                ]
                session.commit()
        del state_args["title"]


request_edit_description_id = "request_edit_description"


def request_edit_description_show(id, state_args):
    return {
        "text": "Введите новое описание",
        "keyboard": [[{"text": "Отменить", "callback": request_id}]],
    }


def request_edit_description_text(id, state_args, handler_arg):
    try:
        state_args["description"] = process_description_input(handler_arg)
        return request_confirm_description_id
    except Exception as e:
        state_args["status"] = str(e)
        return request_edit_description_id


request_confirm_description_id = "request_confirm_description"


def request_confirm_description_show(id, state_args):
    return {
        "text": "Подтвердите: " + state_args["description"],
        "keyboard": [
            [{"text": "Назад", "callback": request_edit_description_id}],
            [
                {
                    "text": "Подтвердить",
                    "callback": {
                        "state_id": request_id,
                        "handler_arg": "confirm",
                    },
                }
            ],
            [{"text": "Отменить", "callback": request_id}],
        ],
    }


def request_confirm_description_callback(
    id, state_args, state_id, handler_arg
):
    if state_id in [request_edit_description_id, request_id]:
        if handler_arg == "confirm":
            with Session(engine) as session:
                session.get(
                    Request, state_args["id"]
                ).description = state_args["description"]
                session.commit()
        del state_args["description"]


request_edit_phone_id = "request_edit_phone"


def request_edit_phone_show(id, state_args):
    return {
        "text": "Введите новый номер телефона",
        "keyboard": [[{"text": "Отменить", "callback": request_id}]],
    }


def request_edit_phone_text(id, state_args, handler_arg):
    try:
        state_args["phone"] = process_phone_input(handler_arg)
        return request_confirm_phone_id
    except Exception as e:
        state_args["status"] = str(e)
        return request_edit_phone_id


request_confirm_phone_id = "request_confirm_phone"


def request_confirm_phone_show(id, state_args):
    return {
        "text": "Подтвердите: " + state_args["phone"],
        "keyboard": [
            [{"text": "Назад", "callback": request_edit_phone_id}],
            [
                {
                    "text": "Подтвердить",
                    "callback": {
                        "state_id": request_id,
                        "handler_arg": "confirm",
                    },
                }
            ],
            [{"text": "Отменить", "callback": request_id}],
        ],
    }


def request_confirm_phone_callback(id, state_args, state_id, handler_arg):
    if state_id in [request_edit_phone_id, request_id]:
        if handler_arg == "confirm":
            with Session(engine) as session:
                session.get(Request, state_args["id"]).phone = state_args[
                    "phone"
                ]
                session.commit()
        del state_args["phone"]


request_edit_picture_id = "request_edit_picture"


def request_edit_picture_show(id, state_args):
    return {
        "text": "Отправьте новую фотографию",
        "keyboard": [
            [{"text": "Пропустить", "callback": request_confirm_picture_id}],
            [{"text": "Отменить", "callback": request_id}],
        ],
    }


def request_edit_picture_callback(id, state_args, state_id, handler_arg):
    if state_id == request_confirm_picture_id:
        state_args["picture"] = None


def request_edit_picture_photo(id, state_args, handler_arg):
    state_args["picture"] = handler_arg
    return request_confirm_picture_id


request_confirm_picture_id = "request_confirm_picture"


def request_confirm_picture_show(id, state_args):
    return {
        "text": "Подтвердите",
        "photo": state_args["picture"],
        "keyboard": [
            [{"text": "Назад", "callback": request_edit_picture_id}],
            [
                {
                    "text": "Подтвердить",
                    "callback": {
                        "state_id": request_id,
                        "handler_arg": "confirm",
                    },
                }
            ],
            [{"text": "Отменить", "callback": request_id}],
        ],
    }


def request_confirm_picture_callback(id, state_args, state_id, handler_arg):
    if state_id in [request_edit_picture_id, request_id]:
        if handler_arg == "confirm":
            with Session(engine) as session:
                session.get(Request, state_args["id"]).picture = state_args[
                    "picture"
                ]
                session.commit()
        del state_args["picture"]


request_delete_id = "request_delete"


def request_delete_show(id, state_args):
    return {
        "text": "Подтвердите",
        "keyboard": [
            [
                {
                    "text": "Подтвердить",
                    "callback": state_args["request_return"],
                }
            ],
            [{"text": "Отменить", "callback": request_id}],
        ],
    }


def request_delete_callback(id, state_args, state_id, handler_arg):
    if state_id == state_args["request_return"]:
        with Session(engine) as session:
            session.delete(session.get(Request, state_args["id"]))
            session.commit()
        del state_args["id"]
        del state_args["request_return"]


request_specs_id = "request_specs"


def request_specs_show(id, state_args):
    with Session(engine) as session:
        request_specs_list = [
            {
                "spec_id": request_spec.spec_id,
                "spec_title": request_spec.spec.title,
            }
            for request_spec in session.query(RequestSpec).where(
                RequestSpec.request_id == state_args["request_id"]
            )
        ]
        admin = id == session.get(Request, state_args["request_id"]).user_id
    return {
        "text": "Специализации заявки",
        "keyboard": [
            [
                {"text": "Назад", "callback": request_id},
            ]
            + (
                [{"text": "Создать", "callback": request_spec_create_spec_id}]
                if admin
                else []
            )
        ]
        + [
            [
                {
                    "text": request_spec_dict["spec_title"],
                    "callback": {
                        "state_id": request_spec_id,
                        "handler_arg": str(request_spec_dict["spec_id"]),
                    },
                }
            ]
            for request_spec_dict in request_specs_list
        ],
    }


def request_specs_callback(id, state_args, state_id, handler_arg):
    if state_id == request_id:
        state_args["id"] = state_args["request_id"]
        del state_args["request_id"]
    if state_id == request_spec_id:
        state_args["spec_id"] = int(handler_arg)


request_spec_create_spec_id = "request_spec_create_spec"


def request_spec_create_spec_show(id, state_args):
    with Session(engine) as session:
        specs_list = [
            {"id": spec.id, "title": spec.title}
            for spec in session.query(Spec).where(
                Spec.id.not_in(
                    session.query(RequestSpec.spec_id).where(
                        RequestSpec.request_id == state_args["request_id"]
                    )
                )
            )
        ]
    return {
        "text": "Выберите специализацию",
        "keyboard": [[{"text": "Отменить", "callback": request_specs_id}]]
        + [
            [
                {
                    "text": spec_dict["title"],
                    "callback": {
                        "state_id": request_spec_confirm_id,
                        "handler_arg": str(spec_dict["id"]),
                    },
                }
            ]
            for spec_dict in specs_list
        ],
    }


def request_spec_create_spec_callback(id, state_args, state_id, handler_arg):
    if state_id == request_spec_confirm_id:
        state_args["spec_id"] = int(handler_arg)


request_spec_confirm_id = "request_spec_confirm"


def request_spec_confirm_show(id, state_args):
    with Session(engine) as session:
        spec_title = session.get(Spec, state_args["spec_id"]).title
    return {
        "text": "Подтвердите:\nСпециализация: " + spec_title,
        "keyboard": [
            [{"text": "Назад", "callback": request_spec_create_spec_id}],
            [
                {
                    "text": "Подтвердить",
                    "callback": {
                        "state_id": request_specs_id,
                        "handler_arg": "confirm",
                    },
                }
            ],
            [{"text": "Отменить", "callback": request_specs_id}],
        ],
    }


def request_spec_confirm_callback(id, state_args, state_id, handler_arg):
    if state_id in [request_spec_create_spec_id, request_specs_id]:
        if handler_arg == "confirm":
            with Session(engine) as session:
                session.add(
                    RequestSpec(
                        request_id=state_args["request_id"],
                        spec_id=state_args["spec_id"],
                    )
                )
                session.commit()
        del state_args["spec_id"]


request_spec_id = "request_spec"


def request_spec_show(id, state_args):
    with Session(engine) as session:
        request_spec = session.get(
            RequestSpec,
            {
                "request_id": state_args["request_id"],
                "spec_id": state_args["spec_id"],
            },
        )
        spec_title = request_spec.spec.title
        admin = id == request_spec.request.user_id
    return {
        "text": "Специализация: " + spec_title,
        "keyboard": [[{"text": "Назад", "callback": request_specs_id}]]
        + (
            [
                [{"text": "Удалить", "callback": request_spec_delete_id}],
            ]
            if admin
            else []
        ),
    }


def request_spec_callback(id, state_args, state_id, handler_arg):
    if state_id == request_specs_id:
        del state_args["spec_id"]


request_spec_delete_id = "request_spec_delete"


def request_spec_delete_show(id, state_args):
    return {
        "text": "Подтвердите",
        "keyboard": [
            [{"text": "Подтвердить", "callback": request_specs_id}],
            [{"text": "Отменить", "callback": request_spec_id}],
        ],
    }


def request_spec_delete_callback(id, state_args, state_id, handler_arg):
    if state_id == request_specs_id:
        with Session(engine) as session:
            session.delete(
                session.get(
                    RequestSpec,
                    {
                        "request_id": state_args["request_id"],
                        "spec_id": state_args["spec_id"],
                    },
                )
            )
            session.commit()
        del state_args["spec_id"]


offers_id = "offers"


def offers_show(id, state_args):
    with Session(engine) as session:
        offers_list = [
            {
                "ars_id": offer.ars_id,
                "ars_title": offer.ars.title,
                "cost_floor": offer.cost_floor,
                "cost_ceil": offer.cost_ceil,
                "winner": offer.winner,
            }
            for offer in session.query(Offer).where(
                Offer.request_id == state_args["request_id"]
            )
        ]
    return {
        "text": "Офферы",
        "keyboard": [
            [
                {"text": "Назад", "callback": request_id},
                {"text": "Создать", "callback": offer_create_ars_id},
            ]
        ]
        + [
            [
                {
                    "text": ("W" if offer_dict["winner"] else " ")
                    + " "
                    + offer_dict["ars_title"]
                    + " "
                    + str(offer_dict["cost_floor"])
                    + (
                        (" " + str(offer_dict["cost_ceil"]))
                        if offer_dict["cost_ceil"]
                        else ""
                    ),
                    "callback": {
                        "state_id": offer_id,
                        "handler_arg": str(offer_dict["ars_id"]),
                    },
                }
            ]
            for offer_dict in offers_list
        ],
    }


def offers_callback(id, state_args, state_id, handler_arg):
    if state_id == request_id:
        state_args["id"] = state_args["request_id"]
        del state_args["request_id"]
    if state_id == offer_id:
        state_args["ars_id"] = int(handler_arg)


offer_create_ars_id = "offer_create_ars"


def offer_create_ars_show(id, state_args):
    with Session(engine) as session:
        arses_list = [
            {"id": ars.id, "title": ars.title}
            for ars in session.query(Ars).where(
                Ars.user_id == id
                and Ars.id.not_in(
                    session.query(Offer.ars_id).where(
                        Offer.request_id == state_args["request_id"]
                    )
                )
            )
        ]
    return {
        "text": "Выберите СТО",
        "keyboard": [[{"text": "Отменить", "callback": offers_id}]]
        + [
            [
                {
                    "text": ars_dict["title"],
                    "callback": {
                        "state_id": offer_create_cost_floor_id,
                        "handler_arg": str(ars_dict["id"]),
                    },
                }
            ]
            for ars_dict in arses_list
        ],
    }


def offer_create_ars_callback(id, state_args, state_id, handler_arg):
    if state_id == offer_create_cost_floor_id:
        state_args["ars_id"] = int(handler_arg)


offer_create_cost_floor_id = "offer_create_cost_floor"


def offer_create_cost_floor_show(id, state_args):
    return {
        "text": "Введите нижнюю цену",
        "keyboard": [
            [{"text": "Назад", "callback": offer_create_ars_id}],
            [{"text": "Отменить", "callback": offers_id}],
        ],
    }


def offer_create_cost_floor_callback(id, state_args, state_id, handler_arg):
    if state_id in [offer_create_ars_id, offers_id]:
        del state_args["ars_id"]


def offer_create_cost_floor_text(id, state_args, handler_arg):
    try:
        state_args["cost_floor"] = process_cost_input(handler_arg)
        return offer_create_cost_ceil_id
    except Exception as e:
        state_args["status"] = str(e)
        return offer_create_cost_floor_id


offer_create_cost_ceil_id = "offer_create_cost_ceil"


def offer_create_cost_ceil_show(id, state_args):
    return {
        "text": "Введите верхнюю цену",
        "keyboard": [
            [{"text": "Назад", "callback": offer_create_cost_floor_id}],
            [{"text": "Пропустить", "callback": offer_create_description_id}],
            [{"text": "Отменить", "callback": offers_id}],
        ],
    }


def offer_create_cost_ceil_callback(id, state_args, state_id, handler_arg):
    if state_id == offer_create_description_id:
        state_args["cost_ceil"] = None
    elif state_id in [offer_create_cost_floor_id, offers_id]:
        del state_args["cost_floor"]
        if state_id == offers_id:
            del state_args["ars_id"]


def offer_create_cost_ceil_text(id, state_args, handler_arg):
    try:
        state_args["cost_ceil"] = process_cost_input(
            handler_arg, cost_floor=state_args["cost_floor"]
        )
        return offer_create_description_id
    except Exception as e:
        state_args["status"] = str(e)
        return offer_create_cost_ceil_id


offer_create_description_id = "offer_create_description"


def offer_create_description_show(id, state_args):
    return {
        "text": "Введите описание",
        "keyboard": [
            [{"text": "Назад", "callback": offer_create_cost_ceil_id}],
            [{"text": "Отменить", "callback": offers_id}],
        ],
    }


def offer_create_description_callback(id, state_args, state_id, handler_arg):
    if state_id in [offer_create_cost_ceil_id, offers_id]:
        del state_args["cost_ceil"]
        if state_id == offers_id:
            del state_args["cost_floor"]
            del state_args["ars_id"]


def offer_create_description_text(id, state_args, handler_arg):
    try:
        state_args["description"] = process_description_input(handler_arg)
        return offer_confirm_id
    except Exception as e:
        state_args["status"] = str(e)
        return offer_create_description_id


offer_confirm_id = "offer_confirm"


def offer_confirm_show(id, state_args):
    with Session(engine) as session:
        ars_title = session.get(Ars, state_args["ars_id"]).title
    return {
        "text": "Подтвердите:\nСТО: "
        + ars_title
        + "\n"
        + "Нижняя цена: "
        + str(state_args["cost_floor"])
        + "\n"
        + "Верхняя цена: "
        + str(state_args["cost_ceil"])
        + "\n"
        + "Описание: "
        + state_args["description"],
        "keyboard": [
            [{"text": "Назад", "callback": offer_create_description_id}],
            [
                {
                    "text": "Подтвердить",
                    "callback": {
                        "state_id": offers_id,
                        "handler_arg": "confirm",
                    },
                }
            ],
            [{"text": "Отменить", "callback": offers_id}],
        ],
    }


def offer_confirm_callback(id, state_args, state_id, handler_arg):
    if state_id in [offer_create_description_id, offers_id]:
        if handler_arg == "confirm":
            with Session(engine) as session:
                session.add(
                    Offer(
                        request_id=state_args["request_id"],
                        ars_id=state_args["ars_id"],
                        cost_floor=state_args["cost_floor"],
                        cost_ceil=state_args["cost_ceil"],
                        description=state_args["description"],
                        winner=False,
                    )
                )
                session.commit()
        del state_args["description"]
        if state_id == offers_id:
            del state_args["cost_ceil"]
            del state_args["cost_floor"]
            del state_args["ars_id"]


offer_id = "offer"


def offer_show(id, state_args):
    with Session(engine) as session:
        offer = session.get(
            Offer,
            {
                "request_id": state_args["request_id"],
                "ars_id": state_args["ars_id"],
            },
        )
        offer_dict = {
            "cost_floor": offer.cost_floor,
            "cost_ceil": offer.cost_ceil,
            "description": offer.description,
            "winner": offer.winner,
        }
        admin_request = id == offer.request.user_id
        admin_ars = id == offer.ars.user_id
    return {
        "text": "Нижняя цена: "
        + str(offer_dict["cost_floor"])
        + "\n"
        + "Верхняя цена: "
        + str(offer_dict["cost_ceil"])
        + "\n"
        + "Описание: "
        + offer_dict["description"]
        + "\n"
        + "Победитель: "
        + ("W" if offer_dict["winner"] else " "),
        "keyboard": [[{"text": "Назад", "callback": offers_id}]]
        + (
            [
                [
                    {
                        "text": "Изменить нижнюю цену",
                        "callback": offer_edit_cost_floor_id,
                    }
                ],
                [
                    {
                        "text": "Изменить верхнюю цену",
                        "callback": offer_edit_cost_ceil_id,
                    }
                ],
                [
                    {
                        "text": "Изменить описание",
                        "callback": offer_edit_description_id,
                    }
                ],
                [
                    {
                        "text": "Удалить",
                        "callback": offer_delete_id,
                    }
                ],
            ]
            if admin_ars
            else []
        )
        + (
            [
                [
                    {
                        "text": "Выбрать победителем",
                        "callback": offer_confirm_winner_id,
                    }
                ]
            ]
            if (admin_request and not offer_dict["winner"])
            else []
        ),
    }


def offer_callback(id, state_args, state_id, handler_arg):
    if state_id == offers_id:
        del state_args["ars_id"]


offer_edit_cost_floor_id = "offer_edit_cost_floor"


def offer_edit_cost_floor_show(id, state_args):
    return {
        "text": "Введите новую нижнюю цену",
        "keyboard": [[{"text": "Отменить", "callback": offer_id}]],
    }


def offer_edit_cost_floor_text(id, state_args, handler_arg):
    try:
        with Session(engine) as session:
            cost_ceil = session.get(
                Offer,
                {
                    "request_id": state_args["request_id"],
                    "ars_id": state_args["ars_id"],
                },
            ).cost_ceil
        state_args["cost_floor"] = process_cost_input(
            handler_arg, cost_ceil=cost_ceil
        )
        return offer_confirm_cost_floor_id
    except Exception as e:
        state_args["status"] = str(e)
        return offer_edit_cost_floor_id


offer_confirm_cost_floor_id = "offer_confirm_cost_floor"


def offer_confirm_cost_floor_show(id, state_args):
    return {
        "text": "Подтвердите: " + str(state_args["cost_floor"]),
        "keyboard": [
            [{"text": "Назад", "callback": offer_edit_cost_floor_id}],
            [
                {
                    "text": "Подтвердить",
                    "callback": {
                        "state_id": offer_id,
                        "handler_arg": "confirm",
                    },
                }
            ],
            [{"text": "Отменить", "callback": offer_id}],
        ],
    }


def offer_confirm_cost_floor_callback(id, state_args, state_id, handler_arg):
    if state_id in [offer_edit_cost_floor_id, offer_id]:
        if handler_arg == "confirm":
            with Session(engine) as session:
                session.get(
                    Offer,
                    {
                        "request_id": state_args["request_id"],
                        "ars_id": state_args["ars_id"],
                    },
                ).cost_floor = state_args["cost_floor"]
                session.commit()
        del state_args["cost_floor"]


offer_edit_cost_ceil_id = "offer_edit_cost_ceil"


def offer_edit_cost_ceil_show(id, state_args):
    return {
        "text": "Введите новую верхнюю цену",
        "keyboard": [
            [
                {
                    "text": "Пропустить",
                    "calblack": offer_confirm_cost_ceil_id,
                }
            ],
            [{"text": "Отменить", "callback": offer_id}],
        ],
    }


def offer_edit_cost_ceil_callback(id, state_args, state_id, handler_arg):
    if state_id == offer_confirm_cost_ceil_id:
        state_args["cost_ceil"] = None


def offer_edit_cost_ceil_text(id, state_args, handler_arg):
    try:
        with Session(engine) as session:
            cost_floor = session.get(
                Offer,
                {
                    "request_id": state_args["request_id"],
                    "ars_id": state_args["ars_id"],
                },
            ).cost_floor
        state_args["cost_ceil"] = process_cost_input(
            handler_arg, cost_floor=cost_floor
        )
        return offer_confirm_cost_ceil_id
    except Exception as e:
        state_args["status"] = str(e)
        return offer_edit_cost_ceil_id


offer_confirm_cost_ceil_id = "offer_confirm_cost_ceil"


def offer_confirm_cost_ceil_show(id, state_args):
    return {
        "text": "Подтвердите: " + str(state_args["cost_ceil"]),
        "keyboard": [
            [{"text": "Назад", "callback": offer_edit_cost_ceil_id}],
            [
                {
                    "text": "Подтвердить",
                    "callback": {
                        "state_id": offer_id,
                        "handler_arg": "confirm",
                    },
                }
            ],
            [{"text": "Отменить", "callback": offer_id}],
        ],
    }


def offer_confirm_cost_ceil_callback(id, state_args, state_id, handler_arg):
    if state_id in [offer_edit_cost_ceil_id, offer_id]:
        if handler_arg == "confirm":
            with Session(engine) as session:
                session.get(
                    Offer,
                    {
                        "request_id": state_args["request_id"],
                        "ars_id": state_args["ars_id"],
                    },
                ).cost_ceil = state_args["cost_ceil"]
                session.commit()
        del state_args["cost_ceil"]


offer_edit_description_id = "offer_edit_description"


def offer_edit_description_show(id, state_args):
    return {
        "text": "Введите новое описание",
        "keyboard": [[{"text": "Отменить", "callback": offer_id}]],
    }


def offer_edit_description_text(id, state_args, handler_arg):
    try:
        state_args["description"] = process_description_input(handler_arg)
        return offer_confirm_description_id
    except Exception as e:
        state_args["status"] = str(e)
        return offer_edit_description_id


offer_confirm_description_id = "offer_confirm_description"


def offer_confirm_description_show(id, state_args):
    return {
        "text": "Подтвердите: " + state_args["description"],
        "keyboard": [
            [{"text": "Назад", "callback": offer_edit_description_id}],
            [
                {
                    "text": "Подтвердить",
                    "callback": {
                        "state_id": offer_id,
                        "handler_arg": "confirm",
                    },
                }
            ],
            [{"text": "Отменить", "callback": offer_id}],
        ],
    }


def offer_confirm_description_callback(id, state_args, state_id, handler_arg):
    if state_id in [offer_edit_description_id, offer_id]:
        if handler_arg == "confirm":
            with Session(engine) as session:
                session.get(
                    Offer,
                    {
                        "request_id": state_args["request_id"],
                        "ars_id": state_args["ars_id"],
                    },
                ).description = state_args["description"]
                session.commit()
        del state_args["description"]


offer_confirm_winner_id = "offer_confirm_winner"


def offer_confirm_winner_show(id, state_args):
    return {
        "text": "Подтвердите",
        "keyboard": [
            [
                {
                    "text": "Подтвердить",
                    "callback": {
                        "state_id": offer_id,
                        "handler_arg": "confirm",
                    },
                }
            ],
            [{"text": "Отменить", "callback": offer_id}],
        ],
    }


def offer_confirm_winner_callback(id, state_args, state_id, handler_arg):
    if state_id == offer_id:
        if handler_arg == "confirm":
            with Session(engine) as session:
                session.get(
                    Offer,
                    {
                        "request_id": state_args["request_id"],
                        "ars_id": state_args["ars_id"],
                    },
                ).winner = True
                session.commit()


offer_delete_id = "offer_delete"


def offer_delete_show(id, state_args):
    return {
        "text": "Подтвердите",
        "keyboard": [
            [{"text": "Подтвердить", "callback": offers_id}],
            [{"text": "Отменить", "callback": offer_id}],
        ],
    }


def offer_delete_callback(id, state_args, state_id, handler_arg):
    if state_id == offers_id:
        with Session(engine) as session:
            session.delete(
                session.get(
                    Offer,
                    {
                        "request_id": state_args["request_id"],
                        "ars_id": state_args["ars_id"],
                    },
                )
            )
            session.commit()
        del state_args["ars_id"]
