from datetime import date
from decimal import Decimal, InvalidOperation

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Auto, Registration, User

engine = {
    "value": None,
}

START_ID = "start"


def start_show(user_id, state_args):
    return {
        "text": "Старт",
        "contact": {
            "text": "Номер",
            "button": "Номер",
        },
    }


def start_contact(user_id, state_args, handler_arg):
    is_diller = False
    with Session(engine["value"]) as session:
        old_user = session.execute(
            select(User).where(User.phone == handler_arg)).scalars().first()
        if old_user is not None:
            auto = old_user.auto
            if auto is not None:
                auto.user_id = user_id
            else:
                ars = old_user.ars
                if ars is not None:
                    ars.user_id = user_id
                    is_diller = True
            session.delete(old_user)
        else:
            registration = session.execute(
                select(Registration).where(
                    Registration.phone == handler_arg)).scalars().first()
            if registration is not None:
                registration.ars.user_id = user_id
                session.delete(registration)
                is_diller = True
        session.get(User, user_id).phone = handler_arg
        session.commit()
    return DILLER_ID if is_diller else CLIENT_ID


CLIENT_ID = "client"


def client_show(user_id, state_args):
    vendor_title = None
    with Session(engine["value"]) as session:
        auto = session.execute(
            select(Auto).where(Auto.user_id == user_id)).scalars().first()
        if auto is not None:
            vendor_title = auto.vendor.title
            year = auto.year
            volume = auto.volume
    return {
        "text":
        "Клиент" + ("\n\n" + vendor_title + "\n" + year + "\n" +
                    str(volume) if vendor_title is not None else ""),
        "keyboard": [
            [
                {
                    "text": "Автопарк",
                    "callback": CHANGE_AUTO_VENDOR_ID,
                },
            ],
        ] + ([
            [
                {
                    "text": "Создать заявку",
                    "callback": CREATE_REQUEST_SPEC_ID,
                },
            ],
            [
                {
                    "text": "Заявки",
                    "callback": REQUESTS_ID,
                },
            ],
        ] if vendor_title is not None else []),
    }


CHANGE_AUTO_VENDOR_ID = "change_auto_vendor"


def change_auto_vendor_show(user_id, state_args):
    with Session(engine["value"]) as session:
        vendors_list = [{
            "id": vendor.id,
            "title": vendor.title,
        } for vendor in session.query(Vendor).all()]
    return {
        "text":
        "Выберите производителя",
        "keyboard": [
            [
                {
                    "text": "Отменить",
                    "callback": CLIENT_ID,
                },
            ],
        ] + [[
            {
                "text": vendor_dict["title"],
                "callback": {
                    "state_id": CHANGE_AUTO_YEAR_ID,
                    "handler_arg": str(vendor_dict["id"]),
                },
            },
        ] for vendor_dict in vendors_list],
    }


def change_auto_vendor_callback(user_id, state_args, state_id, handler_arg):
    if state_id == CHANGE_AUTO_YEAR_ID:
        state_args["vendor_id"] = int(handler_arg)


CHANGE_AUTO_YEAR_ID = "change_auto_year"


def change_auto_year_show(user_id, state_args):
    return {
        "text": "Введите год",
        "keyboard": [
            [
                {
                    "text": "Отменить",
                    "callback": CLIENT_ID,
                },
            ],
        ],
    }


def change_auto_year_callback(user_id, state_args, state_id, handler_arg):
    del state_args["vendor_id"]


def change_auto_year_text(user_id, state_args, handler_arg):
    try:
        handler_arg = int(handler_arg)
    except ValueError:
        state_args["status"] = "Не число"
        return CHANGE_AUTO_YEAR_ID
    if handler_arg < 1900 or handler_arg > date.today().year:
        state_args["status"] = "Выходит за рамки [1900, this]"
        return CHANGE_AUTO_YEAR_ID
    state_args["year"] = str(handler_arg)
    return CHANGE_AUTO_VOLUME_ID


CHANGE_AUTO_VOLUME_ID = "change_auto_volume"


def change_auto_volume_show(user_id, state_args):
    return {
        "text": "Введите объем",
        "keyboard": [
            [
                {
                    "text": "Отменить",
                    "callback": CLIENT_ID,
                },
            ],
        ],
    }


def change_auto_volume_callback(user_id, state_args, state_id, handler_arg):
    del state_args["year"]
    del state_args["vendor_id"]


def change_auto_volume_text(user_id, state_args, handler_arg):
    try:
        handler_arg = Decimal(handler_arg)
    except InvalidOperation:
        state_args["status"] = "Не число"
        return CHANGE_AUTO_VOLUME_ID
    if handler_arg < 0 or handler_arg > 10:
        state_args["status"] = "Выходит за рамки [0, 10]"
        return CHANGE_AUTO_VOLUME_ID
    with Session(engine["value"]) as session:
        auto = session.execute(
            select(Auto).where(Auto.user_id == user_id)).scalars().first()
        if auto is None:
            session.add(
                Auto(vendor_id=state_args["vendor_id"],
                     year=state_args["year"],
                     volume=handler_arg))
        else:
            auto.vendor_id = state_args["vendor_id"]
            auto.year = state_args["year"]
            auto.volume = handler_arg
        session.commit()
    del state_args["year"]
    del state_args["vendor_id"]
    return CLIENT_ID


CREATE_REQUEST_SPEC_ID = "create_request_spec"


def create_request_spec_show(user_id, state_args):
    return {
        "text": "Создать заявку",
    }


REQUESTS_ID = "requests"


def requests_show(user_id, state_args):
    return {
        "text": "Заявки",
    }


DILLER_ID = "diller"


def diller_show(user_id, state_args):
    return {
        "text": "Диллер",
    }


"""
MAIN_ID = "main"


def main_show(user_id, state_args):
    return {
        "text":
        "Главное меню",
        "keyboard": [
            [{
                "text": "СТО",
                "callback": ARSES_ID
            }],
            [{
                "text": "Аукцион заявок",
                "callback": REQUESTS_ID
            }],
            [{
                "text": "Кабинет диллера",
                "callback": DILLER_ID
            }],
            [{
                "text": "Кабинет клиента",
                "callback": CLIENT_ID
            }],
        ],
    }


DILLER_ID = "diller"


def diller_show(user_id, state_args):
    with Session(engine["value"]) as session:
        arses_list = [{
            "id": ars.id,
            "title": ars.title
        } for ars in session.query(Ars).where(Ars.user_id == user_id)]
    return {
        "text":
        "Кабинет диллера",
        "keyboard": [[
            {
                "text": "Назад",
                "callback": MAIN_ID
            },
            {
                "text": "Создать",
                "callback": ARS_CREATE_TITLE_ID
            },
        ]] + [[{
            "text": ars_dict["title"],
            "callback": {
                "state_id": ARS_ID,
                "handler_arg": str(ars_dict["id"]),
            },
        }] for ars_dict in arses_list],
    }


def diller_callback(user_id, state_args, state_id, handler_arg):
    if state_id == ARS_ID:
        state_args["ars_return"] = DILLER_ID
        state_args["id"] = int(handler_arg)
    elif state_id == ARS_CREATE_TITLE_ID:
        state_args["ars_create_return"] = DILLER_ID


CLIENT_ID = "client"


def client_show(user_id, state_args):
    with Session(engine["value"]) as session:
        requests_list = [{
            "id": request.id,
            "title": request.title
        } for request in session.query(Request).where(
            Request.user_id == user_id)]
    return {
        "text":
        "Кабинет клиента",
        "keyboard": [[
            {
                "text": "Назад",
                "callback": MAIN_ID
            },
            {
                "text": "Создать",
                "callback": REQUEST_CREATE_TITLE_ID
            },
        ]] + [[{
            "text": request_dict["title"],
            "callback": {
                "state_id": REQUEST_ID,
                "handler_arg": str(request_dict["id"]),
            },
        }] for request_dict in requests_list],
    }


def client_callback(user_id, state_args, state_id, handler_arg):
    if state_id == REQUEST_ID:
        state_args["request_return"] = CLIENT_ID
        state_args["id"] = int(handler_arg)
    elif state_id == REQUEST_CREATE_TITLE_ID:
        state_args["request_create_return"] = CLIENT_ID


ARS_OFFERS_ID = "ars_offers"


def ars_offers_show(user_id, state_args):
    with Session(engine["value"]) as session:
        offers_list = [{
            "request_id": offer.request_id,
            "request_title": offer.request.title,
        } for offer in session.query(Offer).where(
            Offer.ars_id == state_args["ars_id"])]
    return {
        "text":
        "Офферы",
        "keyboard": [[
            {
                "text": "Назад",
                "callback": ARS_ID
            },
        ]] + [[{
            "text": offer_dict["request_title"],
            "callback": {
                "state_id": OFFER_ID,
                "handler_arg": str(offer_dict["request_id"]),
            },
        }] for offer_dict in offers_list],
    }


def ars_offers_callback(user_id, state_args, state_id, handler_arg):
    if state_id == ARS_ID:
        state_args["id"] = state_args["ars_id"]
        del state_args["ars_id"]
    elif state_id == OFFER_ID:
        state_args["offer_return"] = ARS_OFFERS_ID
        state_args["request_id"] = int(handler_arg)


ARSES_ID = "arses"


def arses_show(user_id, state_args):
    with Session(engine["value"]) as session:
        arses_list = [{
            "id": ars.id,
            "title": ars.title
        } for ars in session.query(Ars).all()]
    return {
        "text":
        "СТО",
        "keyboard": [[
            {
                "text": "Назад",
                "callback": MAIN_ID
            },
            {
                "text": "Создать",
                "callback": ARS_CREATE_TITLE_ID
            },
        ]] + [[{
            "text": ars_dict["title"],
            "callback": {
                "state_id": ARS_ID,
                "handler_arg": str(ars_dict["id"]),
            },
        }] for ars_dict in arses_list],
    }


def arses_callback(user_id, state_args, state_id, handler_arg):
    if state_id == ARS_ID:
        state_args["ars_return"] = ARSES_ID
        state_args["id"] = int(handler_arg)
    elif state_id == ARS_CREATE_TITLE_ID:
        state_args["ars_create_return"] = ARSES_ID


ARS_CREATE_TITLE_ID = "ars_create_title"


def ars_create_title_show(user_id, state_args):
    return {
        "text":
        "Введите название",
        "keyboard": [[{
            "text": "Отменить",
            "callback": state_args["ars_create_return"]
        }]],
    }


def ars_create_title_callback(user_id, state_args, state_id, handler_arg):
    if state_id == state_args["ars_create_return"]:
        del state_args["ars_create_return"]


def ars_create_title_text(user_id, state_args, handler_arg):
    try:
        state_args["title"] = process_title_input(handler_arg)
        return ARS_CREATE_DESCRIPTION_ID
    except ProcessException as exception:
        state_args["status"] = str(exception)
        return ARS_CREATE_TITLE_ID


ARS_CREATE_DESCRIPTION_ID = "ars_create_description"


def ars_create_description_show(user_id, state_args):
    return {
        "text":
        "Введите описание",
        "keyboard": [
            [{
                "text": "Назад",
                "callback": ARS_CREATE_TITLE_ID
            }],
            [{
                "text": "Отменить",
                "callback": state_args["ars_create_return"],
            }],
        ],
    }


def ars_create_description_callback(user_id, state_args, state_id,
                                    handler_arg):
    if state_id in [ARS_CREATE_TITLE_ID, state_args["ars_create_return"]]:
        del state_args["title"]
        if state_id == state_args["ars_create_return"]:
            del state_args["ars_create_return"]


def ars_create_description_text(user_id, state_args, handler_arg):
    try:
        state_args["description"] = process_description_input(handler_arg)
        return ARS_CREATE_ADDRESS_ID
    except ProcessException as exception:
        state_args["status"] = str(exception)
        return ARS_CREATE_DESCRIPTION_ID


ARS_CREATE_ADDRESS_ID = "ars_create_address"


def ars_create_address_show(user_id, state_args):
    return {
        "text":
        "Введите адрес",
        "keyboard": [
            [{
                "text": "Назад",
                "callback": ARS_CREATE_DESCRIPTION_ID
            }],
            [{
                "text": "Отменить",
                "callback": state_args["ars_create_return"],
            }],
        ],
    }


def ars_create_address_callback(user_id, state_args, state_id, handler_arg):
    if state_id in [
            ARS_CREATE_DESCRIPTION_ID,
            state_args["ars_create_return"],
    ]:
        del state_args["description"]
        if state_id == state_args["ars_create_return"]:
            del state_args["title"]
            del state_args["ars_create_return"]


def ars_create_address_text(user_id, state_args, handler_arg):
    try:
        latitude, longitude = process_address_input(handler_arg)
        state_args["address"] = handler_arg
        state_args["latitude"] = latitude
        state_args["longitude"] = longitude
        return ARS_CREATE_PHONE_ID
    except ProcessException as exception:
        state_args["status"] = str(exception)
        return ARS_CREATE_ADDRESS_ID


ARS_CREATE_PHONE_ID = "ars_create_phone"


def ars_create_phone_show(user_id, state_args):
    return {
        "text":
        "Введите номер телефона",
        "keyboard": [
            [{
                "text": "Назад",
                "callback": ARS_CREATE_ADDRESS_ID
            }],
            [{
                "text": "Отменить",
                "callback": state_args["ars_create_return"],
            }],
        ],
    }


def ars_create_phone_callback(user_id, state_args, state_id, handler_arg):
    if state_id in [ARS_CREATE_ADDRESS_ID, state_args["ars_create_return"]]:
        del state_args["address"]
        del state_args["latitude"]
        del state_args["longitude"]
        if state_id == state_args["ars_create_return"]:
            del state_args["description"]
            del state_args["title"]
            del state_args["ars_create_return"]


def ars_create_phone_text(user_id, state_args, handler_arg):
    try:
        state_args["phone"] = handler_arg[:10]
        return ARS_CREATE_PICTURE_ID
    except ProcessException as exception:
        state_args["status"] = str(exception)
        return ARS_CREATE_PHONE_ID


ARS_CREATE_PICTURE_ID = "ars_create_picture"


def ars_create_picture_show(user_id, state_args):
    return {
        "text":
        "Отправьте фотографию",
        "keyboard": [
            [{
                "text": "Назад",
                "callback": ARS_CREATE_PHONE_ID
            }],
            [{
                "text": "Пропустить",
                "callback": ARS_CONFIRM_ID
            }],
            [{
                "text": "Отменить",
                "callback": state_args["ars_create_return"],
            }],
        ],
    }


def ars_create_picture_callback(user_id, state_args, state_id, handler_arg):
    if state_id == ARS_CONFIRM_ID:
        state_args["picture"] = None
    elif state_id in [ARS_CREATE_PHONE_ID, state_args["ars_create_return"]]:
        del state_args["phone"]
        if state_id == state_args["ars_create_return"]:
            del state_args["address"]
            del state_args["latitude"]
            del state_args["longitude"]
            del state_args["description"]
            del state_args["title"]
            del state_args["ars_create_return"]


def ars_create_picture_photo(user_id, state_args, handler_arg):
    state_args["picture"] = handler_arg
    return ARS_CONFIRM_ID


ARS_CONFIRM_ID = "ars_confirm"


def ars_confirm_show(user_id, state_args):
    return {
        "text":
        "Подтвердите:\nНазвание: " + state_args["title"] + "\n" +
        "Описание: " + state_args["description"] + "\n" + "Адрес: " +
        state_args["address"] + "\n" + "Номер телефона: " +
        state_args["phone"],
        "photo":
        state_args["picture"],
        "keyboard": [
            [{
                "text": "Назад",
                "callback": ARS_CREATE_PICTURE_ID
            }],
            [{
                "text": "Подтвердить",
                "callback": {
                    "state_id": state_args["ars_create_return"],
                    "handler_arg": "confirm",
                },
            }],
            [{
                "text": "Отменить",
                "callback": state_args["ars_create_return"],
            }],
        ],
    }


def ars_confirm_callback(user_id, state_args, state_id, handler_arg):
    if state_id in [ARS_CREATE_PICTURE_ID, state_args["ars_create_return"]]:
        if handler_arg == "confirm":
            with Session(engine["value"]) as session:
                session.add(
                    Ars(
                        title=state_args["title"],
                        description=state_args["description"],
                        address=state_args["address"],
                        latitude=state_args["latitude"],
                        longitude=state_args["longitude"],
                        phone=state_args["phone"],
                        picture=state_args["picture"],
                        user_id=user_id,
                    ))
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


ARS_ID = "ars"


def ars_show(user_id, state_args):
    with Session(engine["value"]) as session:
        ars = session.get(Ars, state_args["id"])
        ars_dict = {
            "title": ars.title,
            "description": ars.description,
            "address": ars.address,
            "phone": ars.phone,
            "picture": ars.picture,
        }
        admin = user_id == ars.user_id
    return {
        "text":
        "Название: " + ars_dict["title"] + "\n" + "Описание: " +
        ars_dict["description"] + "\n" + "Адрес: " + ars_dict["address"] +
        "\n" + "Номер телефона: " + ars_dict["phone"],
        "photo":
        ars_dict["picture"],
        "keyboard": [
            [
                {
                    "text":
                    "Назад",
                    "callback": ((state_args["ars_return"] if isinstance(
                        state_args["ars_return"], str) else OFFER_ID) if
                                 ("ars_return" in state_args) else MAIN_ID),
                },
            ],
            [{
                "text": "Специализации СТО",
                "callback": ARS_SPECS_ID
            }],
            [{
                "text": "Вендоры СТО",
                "callback": ARS_VENDORS_ID
            }],
            [{
                "text": "Отзывы",
                "callback": FEEDBACKS_ID
            }],
            [{
                "text": "Офферы",
                "callback": ARS_OFFERS_ID
            }],
        ] + ([
            [{
                "text": "Изменить название",
                "callback": ARS_EDIT_TITLE_ID,
            }],
            [{
                "text": "Изменить описание",
                "callback": ARS_EDIT_DESCRIPTION_ID,
            }],
            [{
                "text": "Изменить адрес",
                "callback": ARS_EDIT_ADDRESS_ID,
            }],
            [{
                "text": "Изменить номер телефона",
                "callback": ARS_EDIT_PHONE_ID,
            }],
            [{
                "text": "Изменить фотографию",
                "callback": ARS_EDIT_PICTURE_ID,
            }],
            [{
                "text": "Удалить",
                "callback": ARS_DELETE_ID,
            }],
        ] if admin else []),
    }


def ars_callback(user_id, state_args, state_id, handler_arg):
    if (state_id == MAIN_ID or state_id == OFFER_ID
            or "ars_return" in state_args
            and state_id == state_args["ars_return"]):
        if state_id == OFFER_ID:
            state_args["ars_id"] = state_args["id"]
            state_args["request_id"] = state_args["ars_return"]
        del state_args["id"]
        if "ars_return" in state_args:
            del state_args["ars_return"]
        if state_id == MAIN_ID:
            if "request_return" in state_args:
                del state_args["request_return"]
            if "offer_return" in state_args:
                del state_args["offer_return"]
    elif state_id in [
            ARS_SPECS_ID,
            ARS_VENDORS_ID,
            FEEDBACKS_ID,
            ARS_OFFERS_ID,
    ]:
        state_args["ars_id"] = state_args["id"]
        del state_args["id"]


ARS_EDIT_TITLE_ID = "ars_edit_title"


def ars_edit_title_show(user_id, state_args):
    return {
        "text": "Введите новое название",
        "keyboard": [[{
            "text": "Отменить",
            "callback": ARS_ID
        }]],
    }


def ars_edit_title_text(user_id, state_args, handler_arg):
    try:
        state_args["title"] = process_title_input(handler_arg)
        return ARS_CONFIRM_TITLE_ID
    except ProcessException as exception:
        state_args["status"] = str(exception)
        return ARS_EDIT_TITLE_ID


ARS_CONFIRM_TITLE_ID = "ars_confirm_title"


def ars_confirm_title_show(user_id, state_args):
    return {
        "text":
        "Подтвердите: " + state_args["title"],
        "keyboard": [
            [{
                "text": "Назад",
                "callback": ARS_EDIT_TITLE_ID
            }],
            [{
                "text": "Подтвердить",
                "callback": {
                    "state_id": ARS_ID,
                    "handler_arg": "confirm"
                },
            }],
            [{
                "text": "Отменить",
                "callback": ARS_ID
            }],
        ],
    }


def ars_confirm_title_callback(user_id, state_args, state_id, handler_arg):
    if state_id in [ARS_EDIT_TITLE_ID, ARS_ID]:
        if handler_arg == "confirm":
            with Session(engine["value"]) as session:
                session.get(Ars, state_args["id"]).title = state_args["title"]
                session.commit()
        del state_args["title"]


ARS_EDIT_DESCRIPTION_ID = "ars_edit_description"


def ars_edit_description_show(user_id, state_args):
    return {
        "text": "Введите новое описание",
        "keyboard": [[{
            "text": "Отменить",
            "callback": ARS_ID
        }]],
    }


def ars_edit_description_text(user_id, state_args, handler_arg):
    try:
        state_args["description"] = process_description_input(handler_arg)
        return ARS_CONFIRM_DESCRIPTION_ID
    except ProcessException as exception:
        state_args["status"] = str(exception)
        return ARS_EDIT_DESCRIPTION_ID


ARS_CONFIRM_DESCRIPTION_ID = "ars_confirm_description"


def ars_confirm_description_show(user_id, state_args):
    return {
        "text":
        "Подтвердите: " + state_args["description"],
        "keyboard": [
            [{
                "text": "Назад",
                "callback": ARS_EDIT_DESCRIPTION_ID
            }],
            [{
                "text": "Подтвердить",
                "callback": {
                    "state_id": ARS_ID,
                    "handler_arg": "confirm"
                },
            }],
            [{
                "text": "Отменить",
                "callback": ARS_ID
            }],
        ],
    }


def ars_confirm_description_callback(user_id, state_args, state_id,
                                     handler_arg):
    if state_id in [ARS_EDIT_DESCRIPTION_ID, ARS_ID]:
        if handler_arg == "confirm":
            with Session(engine["value"]) as session:
                session.get(
                    Ars,
                    state_args["id"]).description = state_args["description"]
                session.commit()
        del state_args["description"]


ARS_EDIT_ADDRESS_ID = "ars_edit_address"


def ars_edit_address_show(user_id, state_args):
    return {
        "text": "Введите новый адрес",
        "keyboard": [[{
            "text": "Отменить",
            "callback": ARS_ID
        }]],
    }


def ars_edit_address_text(user_id, state_args, handler_arg):
    try:
        latitude, longitude = process_address_input(handler_arg)
        state_args["address"] = handler_arg
        state_args["latitude"] = latitude
        state_args["longitude"] = longitude
        return ARS_CONFIRM_ADDRESS_ID
    except ProcessException as exception:
        state_args["status"] = str(exception)
        return ARS_EDIT_ADDRESS_ID


ARS_CONFIRM_ADDRESS_ID = "ars_confirm_address"


def ars_confirm_address_show(user_id, state_args):
    return {
        "text":
        "Подтвердите: " + state_args["address"],
        "keyboard": [
            [{
                "text": "Назад",
                "callback": ARS_EDIT_ADDRESS_ID
            }],
            [{
                "text": "Подтвердить",
                "callback": {
                    "state_id": ARS_ID,
                    "handler_arg": "confirm"
                },
            }],
            [{
                "text": "Отменить",
                "callback": ARS_ID
            }],
        ],
    }


def ars_confirm_address_callback(user_id, state_args, state_id, handler_arg):
    if state_id in [ARS_EDIT_ADDRESS_ID, ARS_ID]:
        if handler_arg == "confirm":
            with Session(engine["value"]) as session:
                ars = session.get(Ars, state_args["id"])
                ars.address = state_args["address"]
                ars.latitude = state_args["latitude"]
                ars.longitude = state_args["longitude"]
                session.commit()
        del state_args["address"]
        del state_args["latitude"]
        del state_args["longitude"]


ARS_EDIT_PHONE_ID = "ars_edit_phone"


def ars_edit_phone_show(user_id, state_args):
    return {
        "text": "Введите новый номер телефона",
        "keyboard": [[{
            "text": "Отменить",
            "callback": ARS_ID
        }]],
    }


def ars_edit_phone_text(user_id, state_args, handler_arg):
    try:
        state_args["phone"] = handler_arg[:10]
        return ARS_CONFIRM_PHONE_ID
    except ProcessException as exception:
        state_args["status"] = str(exception)
        return ARS_EDIT_PHONE_ID


ARS_CONFIRM_PHONE_ID = "ars_confirm_phone"


def ars_confirm_phone_show(user_id, state_args):
    return {
        "text":
        "Подтвердите: " + state_args["phone"],
        "keyboard": [
            [{
                "text": "Назад",
                "callback": ARS_EDIT_PHONE_ID
            }],
            [{
                "text": "Подтвердить",
                "callback": {
                    "state_id": ARS_ID,
                    "handler_arg": "confirm"
                },
            }],
            [{
                "text": "Отменить",
                "callback": ARS_ID
            }],
        ],
    }


def ars_confirm_phone_callback(user_id, state_args, state_id, handler_arg):
    if state_id in [ARS_EDIT_PHONE_ID, ARS_ID]:
        if handler_arg == "confirm":
            with Session(engine["value"]) as session:
                session.get(Ars, state_args["id"]).phone = state_args["phone"]
                session.commit()
        del state_args["phone"]


ARS_EDIT_PICTURE_ID = "ars_edit_picture"


def ars_edit_picture_show(user_id, state_args):
    return {
        "text":
        "Отправьте новую фотографию",
        "keyboard": [
            [{
                "text": "Пропустить",
                "callback": ARS_CONFIRM_PICTURE_ID
            }],
            [{
                "text": "Отменить",
                "callback": ARS_ID
            }],
        ],
    }


def ars_edit_picture_callback(user_id, state_args, state_id, handler_arg):
    if state_id == ARS_CONFIRM_PICTURE_ID:
        state_args["picture"] = None


def ars_edit_picture_photo(user_id, state_args, handler_arg):
    state_args["picture"] = handler_arg
    return ARS_CONFIRM_PICTURE_ID


ARS_CONFIRM_PICTURE_ID = "ars_confirm_picture"


def ars_confirm_picture_show(user_id, state_args):
    return {
        "text":
        "Подтвердите",
        "photo":
        state_args["picture"],
        "keyboard": [
            [{
                "text": "Назад",
                "callback": ARS_EDIT_PICTURE_ID
            }],
            [{
                "text": "Подтвердить",
                "callback": {
                    "state_id": ARS_ID,
                    "handler_arg": "confirm"
                },
            }],
            [{
                "text": "Отменить",
                "callback": ARS_ID
            }],
        ],
    }


def ars_confirm_picture_callback(user_id, state_args, state_id, handler_arg):
    if state_id in [ARS_EDIT_PICTURE_ID, ARS_ID]:
        if handler_arg == "confirm":
            with Session(engine["value"]) as session:
                session.get(Ars,
                            state_args["id"]).picture = state_args["picture"]
                session.commit()
        del state_args["picture"]


ARS_DELETE_ID = "ars_delete"


def ars_delete_show(user_id, state_args):
    return {
        "text":
        "Подтвердите",
        "keyboard": [
            [{
                "text":
                "Подтвердить",
                "callback":
                (state_args["ars_return"] if
                 ("ars_return" in state_args
                  and isinstance(state_args["ars_return"], str)) else MAIN_ID),
            }],
            [{
                "text": "Отменить",
                "callback": ARS_ID
            }],
        ],
    }


def ars_delete_callback(user_id, state_args, state_id, handler_arg):
    if (state_id == MAIN_ID or "ars_return" in state_args
            and state_id == state_args["ars_return"]):
        with Session(engine["value"]) as session:
            session.delete(session.get(Ars, state_args["id"]))
            session.commit()
        del state_args["id"]
        if "ars_return" in state_args:
            del state_args["ars_return"]
        if state_id == MAIN_ID:
            if "request_return" in state_args:
                del state_args["request_return"]
            if "offer_return" in state_args:
                del state_args["offer_return"]


ARS_SPECS_ID = "ars_specs"


def ars_specs_show(user_id, state_args):
    with Session(engine["value"]) as session:
        ars_specs_list = [{
            "spec_id": ars_spec.spec_id,
            "spec_title": ars_spec.spec.title,
            "cost_floor": ars_spec.cost_floor,
            "cost_ceil": ars_spec.cost_ceil,
        } for ars_spec in session.query(ArsSpec).where(
            ArsSpec.ars_id == state_args["ars_id"])]
        admin = user_id == session.get(Ars, state_args["ars_id"]).user_id
    return {
        "text":
        "Специализации СТО",
        "keyboard": [[
            {
                "text": "Назад",
                "callback": ARS_ID
            },
        ] + ([{
            "text": "Создать",
            "callback": ARS_SPEC_CREATE_SPEC_ID
        }] if admin else [])] + [[{
            "text":
            ars_spec_dict["spec_title"] + " " +
            str(ars_spec_dict["cost_floor"]) +
            ((" " + str(ars_spec_dict["cost_ceil"]))
             if ars_spec_dict["cost_ceil"] else ""),
            "callback": {
                "state_id": ARS_SPEC_ID,
                "handler_arg": str(ars_spec_dict["spec_id"]),
            },
        }] for ars_spec_dict in ars_specs_list],
    }


def ars_specs_callback(user_id, state_args, state_id, handler_arg):
    if state_id == ARS_ID:
        state_args["id"] = state_args["ars_id"]
        del state_args["ars_id"]
    if state_id == ARS_SPEC_ID:
        state_args["spec_id"] = int(handler_arg)


ARS_SPEC_CREATE_SPEC_ID = "ars_spec_create_spec"


def ars_spec_create_spec_show(user_id, state_args):
    with Session(engine["value"]) as session:
        specs_list = [{
            "id": spec.id,
            "title": spec.title
        } for spec in session.query(Spec).where(
            Spec.id.not_in(
                session.query(ArsSpec.spec_id).where(
                    ArsSpec.ars_id == state_args["ars_id"])))]
    return {
        "text":
        "Выберите специализацию",
        "keyboard": [[{
            "text": "Отменить",
            "callback": ARS_SPECS_ID
        }]] + [[{
            "text": spec_dict["title"],
            "callback": {
                "state_id": ARS_SPEC_CREATE_COST_FLOOR_ID,
                "handler_arg": str(spec_dict["id"]),
            },
        }] for spec_dict in specs_list],
    }


def ars_spec_create_spec_callback(user_id, state_args, state_id, handler_arg):
    if state_id == ARS_SPEC_CREATE_COST_FLOOR_ID:
        state_args["spec_id"] = int(handler_arg)


ARS_SPEC_CREATE_COST_FLOOR_ID = "ars_spec_create_cost_floor"


def ars_spec_create_cost_floor_show(user_id, state_args):
    return {
        "text":
        "Введите нижнюю цену",
        "keyboard": [
            [{
                "text": "Назад",
                "callback": ARS_SPEC_CREATE_SPEC_ID
            }],
            [{
                "text": "Отменить",
                "callback": ARS_SPECS_ID
            }],
        ],
    }


def ars_spec_create_cost_floor_callback(user_id, state_args, state_id,
                                        handler_arg):
    if state_id in [ARS_SPEC_CREATE_SPEC_ID, ARS_SPECS_ID]:
        del state_args["spec_id"]


def ars_spec_create_cost_floor_text(user_id, state_args, handler_arg):
    try:
        state_args["cost_floor"] = process_cost_input(handler_arg)
        return ARS_SPEC_CREATE_COST_CEIL_ID
    except ProcessException as exception:
        state_args["status"] = str(exception)
        return ARS_SPEC_CREATE_COST_FLOOR_ID


ARS_SPEC_CREATE_COST_CEIL_ID = "ars_spec_create_cost_ceil"


def ars_spec_create_cost_ceil_show(user_id, state_args):
    return {
        "text":
        "Введите верхнюю цену",
        "keyboard": [
            [{
                "text": "Назад",
                "callback": ARS_SPEC_CREATE_COST_FLOOR_ID
            }],
            [{
                "text": "Пропустить",
                "callback": ARS_SPEC_CONFIRM_ID
            }],
            [{
                "text": "Отменить",
                "callback": ARS_SPECS_ID
            }],
        ],
    }


def ars_spec_create_cost_ceil_callback(user_id, state_args, state_id,
                                       handler_arg):
    if state_id == ARS_SPEC_CONFIRM_ID:
        state_args["cost_ceil"] = None
    elif state_id in [ARS_SPEC_CREATE_COST_FLOOR_ID, ARS_SPECS_ID]:
        del state_args["cost_floor"]
        if state_id == ARS_SPECS_ID:
            del state_args["spec_id"]


def ars_spec_create_cost_ceil_text(user_id, state_args, handler_arg):
    try:
        state_args["cost_ceil"] = process_cost_input(
            handler_arg, cost_floor=state_args["cost_floor"])
        return ARS_SPEC_CONFIRM_ID
    except ProcessException as exception:
        state_args["status"] = str(exception)
        return ARS_SPEC_CREATE_COST_CEIL_ID


ARS_SPEC_CONFIRM_ID = "ars_spec_confirm"


def ars_spec_confirm_show(user_id, state_args):
    with Session(engine["value"]) as session:
        spec_title = session.get(Spec, state_args["spec_id"]).title
    return {
        "text":
        "Подтвердите:\nСпециализация: " + spec_title + "\n" + "Нижняя цена: " +
        str(state_args["cost_floor"]) + "\n" + "Верхняя цена: " +
        str(state_args["cost_ceil"]),
        "keyboard": [
            [{
                "text": "Назад",
                "callback": ARS_SPEC_CREATE_COST_CEIL_ID
            }],
            [{
                "text": "Подтвердить",
                "callback": {
                    "state_id": ARS_SPECS_ID,
                    "handler_arg": "confirm",
                },
            }],
            [{
                "text": "Отменить",
                "callback": ARS_SPECS_ID
            }],
        ],
    }


def ars_spec_confirm_callback(user_id, state_args, state_id, handler_arg):
    if state_id in [ARS_SPEC_CREATE_COST_CEIL_ID, ARS_SPECS_ID]:
        if handler_arg == "confirm":
            with Session(engine["value"]) as session:
                session.add(
                    ArsSpec(
                        ars_id=state_args["ars_id"],
                        spec_id=state_args["spec_id"],
                        cost_floor=state_args["cost_floor"],
                        cost_ceil=state_args["cost_ceil"],
                    ))
                session.commit()
        del state_args["cost_ceil"]
        if state_id == ARS_SPECS_ID:
            del state_args["cost_floor"]
            del state_args["spec_id"]


ARS_SPEC_ID = "ars_spec"


def ars_spec_show(user_id, state_args):
    with Session(engine["value"]) as session:
        ars_spec = session.get(
            ArsSpec,
            {
                "ars_id": state_args["ars_id"],
                "spec_id": state_args["spec_id"]
            },
        )
        ars_spec_dict = {
            "spec_title": ars_spec.spec.title,
            "cost_floor": ars_spec.cost_floor,
            "cost_ceil": ars_spec.cost_ceil,
        }
        admin = user_id == ars_spec.ars.user_id
    return {
        "text":
        "Специализация: " + ars_spec_dict["spec_title"] + "\n" +
        "Нижняя цена: " + str(ars_spec_dict["cost_floor"]) + "\n" +
        "Верхняя цена: " + str(ars_spec_dict["cost_ceil"]),
        "keyboard": [[{
            "text": "Назад",
            "callback": ARS_SPECS_ID
        }]] + ([
            [{
                "text": "Изменить нижнюю цену",
                "callback": ARS_SPEC_EDIT_COST_FLOOR_ID,
            }],
            [{
                "text": "Изменить верхнюю цену",
                "callback": ARS_SPEC_EDIT_COST_CEIL_ID,
            }],
            [{
                "text": "Удалить",
                "callback": ARS_SPEC_DELETE_ID,
            }],
        ] if admin else []),
    }


def ars_spec_callback(user_id, state_args, state_id, handler_arg):
    if state_id == ARS_SPECS_ID:
        del state_args["spec_id"]


ARS_SPEC_EDIT_COST_FLOOR_ID = "ars_spec_edit_cost_floor"


def ars_spec_edit_cost_floor_show(user_id, state_args):
    return {
        "text": "Введите новую нижнюю цену",
        "keyboard": [[{
            "text": "Отменить",
            "callback": ARS_SPEC_ID
        }]],
    }


def ars_spec_edit_cost_floor_text(user_id, state_args, handler_arg):
    try:
        with Session(engine["value"]) as session:
            cost_ceil = session.get(
                ArsSpec,
                {
                    "ars_id": state_args["ars_id"],
                    "spec_id": state_args["spec_id"],
                },
            ).cost_ceil
        state_args["cost_floor"] = process_cost_input(handler_arg,
                                                      cost_ceil=cost_ceil)
        return ARS_SPEC_CONFIRM_COST_FLOOR_ID
    except ProcessException as exception:
        state_args["status"] = str(exception)
        return ARS_SPEC_EDIT_COST_FLOOR_ID


ARS_SPEC_CONFIRM_COST_FLOOR_ID = "ars_spec_confirm_cost_floor"


def ars_spec_confirm_cost_floor_show(user_id, state_args):
    return {
        "text":
        "Подтвердите: " + str(state_args["cost_floor"]),
        "keyboard": [
            [{
                "text": "Назад",
                "callback": ARS_SPEC_EDIT_COST_FLOOR_ID
            }],
            [{
                "text": "Подтвердить",
                "callback": {
                    "state_id": ARS_SPEC_ID,
                    "handler_arg": "confirm",
                },
            }],
            [{
                "text": "Отменить",
                "callback": ARS_SPEC_ID
            }],
        ],
    }


def ars_spec_confirm_cost_floor_callback(user_id, state_args, state_id,
                                         handler_arg):
    if state_id in [ARS_SPEC_EDIT_COST_FLOOR_ID, ARS_SPEC_ID]:
        if handler_arg == "confirm":
            with Session(engine["value"]) as session:
                session.get(
                    ArsSpec,
                    {
                        "ars_id": state_args["ars_id"],
                        "spec_id": state_args["spec_id"],
                    },
                ).cost_floor = state_args["cost_floor"]
                session.commit()
        del state_args["cost_floor"]


ARS_SPEC_EDIT_COST_CEIL_ID = "ars_spec_edit_cost_ceil"


def ars_spec_edit_cost_ceil_show(user_id, state_args):
    return {
        "text":
        "Введите новую верхнюю цену",
        "keyboard": [
            [{
                "text": "Пропустить",
                "calblack": ARS_SPEC_CONFIRM_COST_CEIL_ID,
            }],
            [{
                "text": "Отменить",
                "callback": ARS_SPEC_ID
            }],
        ],
    }


def ars_spec_edit_cost_ceil_callback(user_id, state_args, state_id,
                                     handler_arg):
    if state_id == ARS_SPEC_CONFIRM_COST_CEIL_ID:
        state_args["cost_ceil"] = None


def ars_spec_edit_cost_ceil_text(user_id, state_args, handler_arg):
    try:
        with Session(engine["value"]) as session:
            cost_floor = session.get(
                ArsSpec,
                {
                    "ars_id": state_args["ars_id"],
                    "spec_id": state_args["spec_id"],
                },
            ).cost_floor
        state_args["cost_ceil"] = process_cost_input(handler_arg,
                                                     cost_floor=cost_floor)
        return ARS_SPEC_CONFIRM_COST_CEIL_ID
    except ProcessException as exception:
        state_args["status"] = str(exception)
        return ARS_SPEC_EDIT_COST_CEIL_ID


ARS_SPEC_CONFIRM_COST_CEIL_ID = "ars_spec_confirm_cost_ceil"


def ars_spec_confirm_cost_ceil_show(user_id, state_args):
    return {
        "text":
        "Подтвердите: " + str(state_args["cost_ceil"]),
        "keyboard": [
            [{
                "text": "Назад",
                "callback": ARS_SPEC_EDIT_COST_CEIL_ID
            }],
            [{
                "text": "Подтвердить",
                "callback": {
                    "state_id": ARS_SPEC_ID,
                    "handler_arg": "confirm",
                },
            }],
            [{
                "text": "Отменить",
                "callback": ARS_SPEC_ID
            }],
        ],
    }


def ars_spec_confirm_cost_ceil_callback(user_id, state_args, state_id,
                                        handler_arg):
    if state_id in [ARS_SPEC_EDIT_COST_CEIL_ID, ARS_SPEC_ID]:
        if handler_arg == "confirm":
            with Session(engine["value"]) as session:
                session.get(
                    ArsSpec,
                    {
                        "ars_id": state_args["ars_id"],
                        "spec_id": state_args["spec_id"],
                    },
                ).cost_ceil = state_args["cost_ceil"]
                session.commit()
        del state_args["cost_ceil"]


ARS_SPEC_DELETE_ID = "ars_spec_delete"


def ars_spec_delete_show(user_id, state_args):
    return {
        "text":
        "Подтвердите",
        "keyboard": [
            [{
                "text": "Подтвердить",
                "callback": ARS_SPECS_ID
            }],
            [{
                "text": "Отменить",
                "callback": ARS_SPEC_ID
            }],
        ],
    }


def ars_spec_delete_callback(user_id, state_args, state_id, handler_arg):
    if state_id == ARS_SPECS_ID:
        with Session(engine["value"]) as session:
            session.delete(
                session.get(
                    ArsSpec,
                    {
                        "ars_id": state_args["ars_id"],
                        "spec_id": state_args["spec_id"],
                    },
                ))
            session.commit()
        del state_args["spec_id"]


ARS_VENDORS_ID = "ars_vendors"


def ars_vendors_show(user_id, state_args):
    with Session(engine["value"]) as session:
        ars_vendors_list = [{
            "vendor_id": ars_vendor.vendor_id,
            "vendor_title": ars_vendor.vendor.title,
        } for ars_vendor in session.query(ArsVendor).where(
            ArsVendor.ars_id == state_args["ars_id"])]
        admin = user_id == session.get(Ars, state_args["ars_id"]).user_id
    return {
        "text":
        "Вендоры СТО",
        "keyboard": [[
            {
                "text": "Назад",
                "callback": ARS_ID
            },
        ] + ([{
            "text": "Создать",
            "callback": ARS_VENDOR_CREATE_VENDOR_ID
        }] if admin else [])] + [[{
            "text": ars_vendor_dict["vendor_title"],
            "callback": {
                "state_id": ARS_VENDOR_ID,
                "handler_arg": str(ars_vendor_dict["vendor_id"]),
            },
        }] for ars_vendor_dict in ars_vendors_list],
    }


def ars_vendors_callback(user_id, state_args, state_id, handler_arg):
    if state_id == ARS_ID:
        state_args["id"] = state_args["ars_id"]
        del state_args["ars_id"]
    if state_id == ARS_VENDOR_ID:
        state_args["vendor_id"] = int(handler_arg)


ARS_VENDOR_CREATE_VENDOR_ID = "ars_vendor_create_vendor"


def ars_vendor_create_vendor_show(user_id, state_args):
    with Session(engine["value"]) as session:
        vendors_list = [{
            "id": vendor.id,
            "title": vendor.title
        } for vendor in session.query(Vendor).where(
            Vendor.id.not_in(
                session.query(ArsVendor.vendor_id).where(
                    ArsVendor.ars_id == state_args["ars_id"])))]
    return {
        "text":
        "Выберите вендор",
        "keyboard": [[{
            "text": "Отменить",
            "callback": ARS_VENDORS_ID
        }]] + [[{
            "text": vendor_dict["title"],
            "callback": {
                "state_id": ARS_VENDOR_CONFIRM_ID,
                "handler_arg": str(vendor_dict["id"]),
            },
        }] for vendor_dict in vendors_list],
    }


def ars_vendor_create_vendor_callback(user_id, state_args, state_id,
                                      handler_arg):
    if state_id == ARS_VENDOR_CONFIRM_ID:
        state_args["vendor_id"] = int(handler_arg)


ARS_VENDOR_CONFIRM_ID = "ars_vendor_confirm"


def ars_vendor_confirm_show(user_id, state_args):
    with Session(engine["value"]) as session:
        vendor_title = session.get(Vendor, state_args["vendor_id"]).title
    return {
        "text":
        "Подтвердите:\nВендор: " + vendor_title,
        "keyboard": [
            [{
                "text": "Назад",
                "callback": ARS_VENDOR_CREATE_VENDOR_ID
            }],
            [{
                "text": "Подтвердить",
                "callback": {
                    "state_id": ARS_VENDORS_ID,
                    "handler_arg": "confirm",
                },
            }],
            [{
                "text": "Отменить",
                "callback": ARS_VENDORS_ID
            }],
        ],
    }


def ars_vendor_confirm_callback(user_id, state_args, state_id, handler_arg):
    if state_id in [ARS_VENDOR_CREATE_VENDOR_ID, ARS_VENDORS_ID]:
        if handler_arg == "confirm":
            with Session(engine["value"]) as session:
                session.add(
                    ArsVendor(
                        ars_id=state_args["ars_id"],
                        vendor_id=state_args["vendor_id"],
                    ))
                session.commit()
        del state_args["vendor_id"]


ARS_VENDOR_ID = "ars_vendor"


def ars_vendor_show(user_id, state_args):
    with Session(engine["value"]) as session:
        ars_vendor = session.get(
            ArsVendor,
            {
                "ars_id": state_args["ars_id"],
                "vendor_id": state_args["vendor_id"],
            },
        )
        vendor_title = ars_vendor.vendor.title
        admin = user_id == ars_vendor.ars.user_id
    return {
        "text":
        "Вендор: " + vendor_title,
        "keyboard": [[{
            "text": "Назад",
            "callback": ARS_VENDORS_ID
        }]] + ([
            [{
                "text": "Удалить",
                "callback": ARS_VENDOR_DELETE_ID
            }],
        ] if admin else []),
    }


def ars_vendor_callback(user_id, state_args, state_id, handler_arg):
    if state_id == ARS_VENDORS_ID:
        del state_args["vendor_id"]


ARS_VENDOR_DELETE_ID = "ars_vendor_delete"


def ars_vendor_delete_show(user_id, state_args):
    return {
        "text":
        "Подтвердите",
        "keyboard": [
            [{
                "text": "Подтвердить",
                "callback": ARS_VENDORS_ID
            }],
            [{
                "text": "Отменить",
                "callback": ARS_VENDOR_ID
            }],
        ],
    }


def ars_vendor_delete_callback(user_id, state_args, state_id, handler_arg):
    if state_id == ARS_VENDORS_ID:
        with Session(engine["value"]) as session:
            session.delete(
                session.get(
                    ArsVendor,
                    {
                        "ars_id": state_args["ars_id"],
                        "vendor_id": state_args["vendor_id"],
                    },
                ))
            session.commit()
        del state_args["vendor_id"]


FEEDBACKS_ID = "feedbacks"


def feedbacks_show(user_id, state_args):
    with Session(engine["value"]) as session:
        feedbacks_list = [{
            "user_id": feedback.user_id,
            "stars": feedback.stars,
            "title": feedback.title,
        } for feedback in session.query(Feedback).where(
            Feedback.ars_id == state_args["ars_id"])]
        admin = (session.get(Feedback, {
            "ars_id": state_args["ars_id"],
            "user_id": user_id
        }) is not None)
    return {
        "text":
        "Отзывы",
        "keyboard": [[
            {
                "text": "Назад",
                "callback": ARS_ID
            },
        ] + ([] if admin else [{
            "text": "Создать",
            "callback": FEEDBACK_CREATE_STARS_ID
        }])] +
        [[{
            "text": str(feedback_dict["stars"]) + " " + feedback_dict["title"],
            "callback": {
                "state_id": FEEDBACK_ID,
                "handler_arg": str(feedback_dict["user_id"]),
            },
        }] for feedback_dict in feedbacks_list],
    }


def feedbacks_callback(user_id, state_args, state_id, handler_arg):
    if state_id == ARS_ID:
        state_args["id"] = state_args["ars_id"]
        del state_args["ars_id"]
    if state_id == FEEDBACK_ID:
        state_args["user_id"] = int(handler_arg)


FEEDBACK_CREATE_STARS_ID = "feedback_create_stars"


def feedback_create_stars_show(user_id, state_args):
    return {
        "text": "Введите количество звезд",
        "keyboard": [[{
            "text": "Отменить",
            "callback": FEEDBACKS_ID
        }]],
    }


def feedback_create_stars_text(user_id, state_args, handler_arg):
    try:
        state_args["stars"] = process_stars_input(handler_arg)
        return FEEDBACK_CREATE_TITLE_ID
    except ProcessException as exception:
        state_args["status"] = str(exception)
        return FEEDBACK_CREATE_STARS_ID


FEEDBACK_CREATE_TITLE_ID = "feedback_create_title"


def feedback_create_title_show(user_id, state_args):
    return {
        "text":
        "Введите заголовок",
        "keyboard": [
            [{
                "text": "Назад",
                "callback": FEEDBACK_CREATE_STARS_ID
            }],
            [{
                "text": "Отменить",
                "callback": FEEDBACKS_ID
            }],
        ],
    }


def feedback_create_title_callback(user_id, state_args, state_id, handler_arg):
    if state_id in [FEEDBACK_CREATE_STARS_ID, FEEDBACKS_ID]:
        del state_args["stars"]


def feedback_create_title_text(user_id, state_args, handler_arg):
    try:
        state_args["title"] = process_title_input(handler_arg)
        return FEEDBACK_CREATE_DESCRIPTION_ID
    except ProcessException as exception:
        state_args["status"] = str(exception)
        return FEEDBACK_CREATE_TITLE_ID


FEEDBACK_CREATE_DESCRIPTION_ID = "feedback_create_description"


def feedback_create_description_show(user_id, state_args):
    return {
        "text":
        "Введите описание",
        "keyboard": [
            [{
                "text": "Назад",
                "callback": FEEDBACK_CREATE_TITLE_ID
            }],
            [{
                "text": "Отменить",
                "callback": FEEDBACKS_ID
            }],
        ],
    }


def feedback_create_description_callback(user_id, state_args, state_id,
                                         handler_arg):
    if state_id in [FEEDBACK_CREATE_TITLE_ID, FEEDBACKS_ID]:
        del state_args["title"]
        if state_id == FEEDBACKS_ID:
            del state_args["stars"]


def feedback_create_description_text(user_id, state_args, handler_arg):
    try:
        state_args["description"] = process_description_input(handler_arg)
        return FEEDBACK_CONFIRM_ID
    except ProcessException as exception:
        state_args["status"] = str(exception)
        return FEEDBACK_CREATE_DESCRIPTION_ID


FEEDBACK_CONFIRM_ID = "feedback_confirm"


def feedback_confirm_show(user_id, state_args):
    return {
        "text":
        "Подтвердите:\nКоличество звезд: " + str(state_args["stars"]) + "\n" +
        "Заголовок: " + state_args["title"] + "\n" + "Описание: " +
        state_args["description"],
        "keyboard": [
            [{
                "text": "Назад",
                "callback": FEEDBACK_CREATE_DESCRIPTION_ID
            }],
            [{
                "text": "Подтвердить",
                "callback": {
                    "state_id": FEEDBACKS_ID,
                    "handler_arg": "confirm",
                },
            }],
            [{
                "text": "Отменить",
                "callback": FEEDBACKS_ID
            }],
        ],
    }


def feedback_confirm_callback(user_id, state_args, state_id, handler_arg):
    if state_id in [FEEDBACK_CREATE_DESCRIPTION_ID, FEEDBACKS_ID]:
        if handler_arg == "confirm":
            with Session(engine["value"]) as session:
                session.add(
                    Feedback(
                        ars_id=state_args["ars_id"],
                        user_id=user_id,
                        stars=state_args["stars"],
                        title=state_args["title"],
                        description=state_args["description"],
                    ))
                session.commit()
        del state_args["description"]
        if state_id == FEEDBACKS_ID:
            del state_args["title"]
            del state_args["stars"]


FEEDBACK_ID = "feedback"


def feedback_show(user_id, state_args):
    with Session(engine["value"]) as session:
        feedback = session.get(
            Feedback,
            {
                "ars_id": state_args["ars_id"],
                "user_id": state_args["user_id"]
            },
        )
        feedback_dict = {
            "stars": feedback.stars,
            "title": feedback.title,
            "description": feedback.description,
        }
    admin = user_id == state_args["user_id"]
    return {
        "text":
        "Количество звезд: " + str(feedback_dict["stars"]) + "\n" +
        "Заголовок: " + feedback_dict["title"] + "\n" + "Описание: " +
        feedback_dict["description"],
        "keyboard": [[{
            "text": "Назад",
            "callback": FEEDBACKS_ID
        }]] + ([
            [{
                "text": "Изменить количество звезд",
                "callback": FEEDBACK_EDIT_STARS_ID,
            }],
            [{
                "text": "Изменить заголовок",
                "callback": FEEDBACK_EDIT_TITLE_ID,
            }],
            [{
                "text": "Изменить описание",
                "callback": FEEDBACK_EDIT_DESCRIPTION_ID,
            }],
            [{
                "text": "Удалить",
                "callback": FEEDBACK_DELETE_ID,
            }],
        ] if admin else []),
    }


def feedback_callback(user_id, state_args, state_id, handler_arg):
    if state_id == FEEDBACKS_ID:
        del state_args["user_id"]


FEEDBACK_EDIT_STARS_ID = "feedback_edit_stars"


def feedback_edit_stars_show(user_id, state_args):
    return {
        "text": "Введите новое количество звезд",
        "keyboard": [[{
            "text": "Отменить",
            "callback": FEEDBACK_ID
        }]],
    }


def feedback_edit_stars_text(user_id, state_args, handler_arg):
    try:
        state_args["stars"] = process_stars_input(handler_arg)
        return FEEDBACK_CONFIRM_STARS_ID
    except ProcessException as exception:
        state_args["status"] = str(exception)
        return FEEDBACK_EDIT_STARS_ID


FEEDBACK_CONFIRM_STARS_ID = "feedback_confirm_stars"


def feedback_confirm_stars_show(user_id, state_args):
    return {
        "text":
        "Подтвердите: " + str(state_args["stars"]),
        "keyboard": [
            [{
                "text": "Назад",
                "callback": FEEDBACK_EDIT_STARS_ID
            }],
            [{
                "text": "Подтвердить",
                "callback": {
                    "state_id": FEEDBACK_ID,
                    "handler_arg": "confirm",
                },
            }],
            [{
                "text": "Отменить",
                "callback": FEEDBACK_ID
            }],
        ],
    }


def feedback_confirm_stars_callback(user_id, state_args, state_id,
                                    handler_arg):
    if state_id in [FEEDBACK_EDIT_STARS_ID, FEEDBACK_ID]:
        if handler_arg == "confirm":
            with Session(engine["value"]) as session:
                session.get(
                    Feedback,
                    {
                        "ars_id": state_args["ars_id"],
                        "user_id": state_args["user_id"],
                    },
                ).stars = state_args["stars"]
                session.commit()
        del state_args["stars"]


FEEDBACK_EDIT_TITLE_ID = "feedback_edit_title"


def feedback_edit_title_show(user_id, state_args):
    return {
        "text": "Введите новый заголовок",
        "keyboard": [[{
            "text": "Отменить",
            "callback": FEEDBACK_ID
        }]],
    }


def feedback_edit_title_text(user_id, state_args, handler_arg):
    try:
        state_args["title"] = process_title_input(handler_arg)
        return FEEDBACK_CONFIRM_TITLE_ID
    except ProcessException as exception:
        state_args["status"] = str(exception)
        return FEEDBACK_EDIT_TITLE_ID


FEEDBACK_CONFIRM_TITLE_ID = "feedback_confirm_title"


def feedback_confirm_title_show(user_id, state_args):
    return {
        "text":
        "Подтвердите: " + state_args["title"],
        "keyboard": [
            [{
                "text": "Назад",
                "callback": FEEDBACK_EDIT_TITLE_ID
            }],
            [{
                "text": "Подтвердить",
                "callback": {
                    "state_id": FEEDBACK_ID,
                    "handler_arg": "confirm",
                },
            }],
            [{
                "text": "Отменить",
                "callback": FEEDBACK_ID
            }],
        ],
    }


def feedback_confirm_title_callback(user_id, state_args, state_id,
                                    handler_arg):
    if state_id in [FEEDBACK_EDIT_TITLE_ID, FEEDBACK_ID]:
        if handler_arg == "confirm":
            with Session(engine["value"]) as session:
                session.get(
                    Feedback,
                    {
                        "ars_id": state_args["ars_id"],
                        "user_id": state_args["user_id"],
                    },
                ).title = state_args["title"]
                session.commit()
        del state_args["title"]


FEEDBACK_EDIT_DESCRIPTION_ID = "feedback_edit_description"


def feedback_edit_description_show(user_id, state_args):
    return {
        "text": "Введите новое описание",
        "keyboard": [[{
            "text": "Отменить",
            "callback": FEEDBACK_ID
        }]],
    }


def feedback_edit_description_text(user_id, state_args, handler_arg):
    try:
        state_args["description"] = process_description_input(handler_arg)
        return FEEDBACK_CONFIRM_DESCRIPTION_ID
    except ProcessException as exception:
        state_args["status"] = str(exception)
        return FEEDBACK_EDIT_DESCRIPTION_ID


FEEDBACK_CONFIRM_DESCRIPTION_ID = "feedback_confirm_description"


def feedback_confirm_description_show(user_id, state_args):
    return {
        "text":
        "Подтвердите: " + state_args["description"],
        "keyboard": [
            [{
                "text": "Назад",
                "callback": FEEDBACK_EDIT_DESCRIPTION_ID
            }],
            [{
                "text": "Подтвердить",
                "callback": {
                    "state_id": FEEDBACK_ID,
                    "handler_arg": "confirm",
                },
            }],
            [{
                "text": "Отменить",
                "callback": FEEDBACK_ID
            }],
        ],
    }


def feedback_confirm_description_callback(user_id, state_args, state_id,
                                          handler_arg):
    if state_id in [FEEDBACK_EDIT_DESCRIPTION_ID, FEEDBACK_ID]:
        if handler_arg == "confirm":
            with Session(engine["value"]) as session:
                session.get(
                    Feedback,
                    {
                        "ars_id": state_args["ars_id"],
                        "user_id": state_args["user_id"],
                    },
                ).description = state_args["description"]
                session.commit()
        del state_args["description"]


FEEDBACK_DELETE_ID = "feedback_delete"


def feedback_delete_show(user_id, state_args):
    return {
        "text":
        "Подтвердите",
        "keyboard": [
            [{
                "text": "Подтвердить",
                "callback": FEEDBACKS_ID
            }],
            [{
                "text": "Отменить",
                "callback": FEEDBACK_ID
            }],
        ],
    }


def feedback_delete_callback(user_id, state_args, state_id, handler_arg):
    if state_id == FEEDBACKS_ID:
        with Session(engine["value"]) as session:
            session.delete(
                session.get(
                    Feedback,
                    {
                        "ars_id": state_args["ars_id"],
                        "user_id": state_args["user_id"],
                    },
                ))
            session.commit()
        del state_args["user_id"]


REQUESTS_ID = "requests"


def requests_show(user_id, state_args):
    with Session(engine["value"]) as session:
        requests_list = [{
            "id": request.id,
            "title": request.title
        } for request in session.query(Request).all()]
    return {
        "text":
        "Аукцион заявок",
        "keyboard": [[
            {
                "text": "Назад",
                "callback": MAIN_ID
            },
            {
                "text": "Создать",
                "callback": REQUEST_CREATE_TITLE_ID
            },
        ]] + [[{
            "text": request_dict["title"],
            "callback": {
                "state_id": REQUEST_ID,
                "handler_arg": str(request_dict["id"]),
            },
        }] for request_dict in requests_list],
    }


def requests_callback(user_id, state_args, state_id, handler_arg):
    if state_id == REQUEST_ID:
        state_args["request_return"] = REQUESTS_ID
        state_args["id"] = int(handler_arg)
    elif state_id == REQUEST_CREATE_TITLE_ID:
        state_args["request_create_return"] = REQUESTS_ID


REQUEST_CREATE_TITLE_ID = "request_create_title"


def request_create_title_show(user_id, state_args):
    return {
        "text":
        "Введите заголовок",
        "keyboard": [[{
            "text": "Отменить",
            "callback": state_args["request_create_return"],
        }]],
    }


def request_create_title_callback(user_id, state_args, state_id, handler_arg):
    if state_id == state_args["request_create_return"]:
        del state_args["request_create_return"]


def request_create_title_text(user_id, state_args, handler_arg):
    try:
        state_args["title"] = process_title_input(handler_arg)
        return REQUEST_CREATE_DESCRIPTION_ID
    except ProcessException as exception:
        state_args["status"] = str(exception)
        return REQUEST_CREATE_TITLE_ID


REQUEST_CREATE_DESCRIPTION_ID = "request_create_description"


def request_create_description_show(user_id, state_args):
    return {
        "text":
        "Введите описание",
        "keyboard": [
            [{
                "text": "Назад",
                "callback": REQUEST_CREATE_TITLE_ID
            }],
            [{
                "text": "Отменить",
                "callback": state_args["request_create_return"],
            }],
        ],
    }


def request_create_description_callback(user_id, state_args, state_id,
                                        handler_arg):
    if state_id in [
            REQUEST_CREATE_TITLE_ID,
            state_args["request_create_return"],
    ]:
        del state_args["title"]
        if state_id == state_args["request_create_return"]:
            del state_args["request_create_return"]


def request_create_description_text(user_id, state_args, handler_arg):
    try:
        state_args["description"] = process_description_input(handler_arg)
        return REQUEST_CREATE_PHONE_ID
    except ProcessException as exception:
        state_args["status"] = str(exception)
        return REQUEST_CREATE_DESCRIPTION_ID


REQUEST_CREATE_PHONE_ID = "request_create_phone"


def request_create_phone_show(user_id, state_args):
    return {
        "text":
        "Введите номер телефона",
        "keyboard": [
            [{
                "text": "Назад",
                "callback": REQUEST_CREATE_DESCRIPTION_ID
            }],
            [{
                "text": "Отменить",
                "callback": state_args["request_create_return"],
            }],
        ],
    }


def request_create_phone_callback(user_id, state_args, state_id, handler_arg):
    if state_id in [
            REQUEST_CREATE_DESCRIPTION_ID,
            state_args["request_create_return"],
    ]:
        del state_args["description"]
        if state_id == state_args["request_create_return"]:
            del state_args["title"]
            del state_args["request_create_return"]


def request_create_phone_text(user_id, state_args, handler_arg):
    try:
        state_args["phone"] = handler_arg[:10]
        return REQUEST_CREATE_PICTURE_ID
    except ProcessException as exception:
        state_args["status"] = str(exception)
        return REQUEST_CREATE_PHONE_ID


REQUEST_CREATE_PICTURE_ID = "request_create_picture"


def request_create_picture_show(user_id, state_args):
    return {
        "text":
        "Отправьте фотографию",
        "keyboard": [
            [{
                "text": "Назад",
                "callback": REQUEST_CREATE_PHONE_ID
            }],
            [{
                "text": "Пропустить",
                "callback": REQUEST_CONFIRM_ID
            }],
            [{
                "text": "Отменить",
                "callback": state_args["request_create_return"],
            }],
        ],
    }


def request_create_picture_callback(user_id, state_args, state_id,
                                    handler_arg):
    if state_id == REQUEST_CONFIRM_ID:
        state_args["picture"] = None
    elif state_id in [
            REQUEST_CREATE_PHONE_ID,
            state_args["request_create_return"],
    ]:
        del state_args["phone"]
        if state_id == state_args["request_create_return"]:
            del state_args["description"]
            del state_args["title"]
            del state_args["request_create_return"]


def request_create_picture_photo(user_id, state_args, handler_arg):
    state_args["picture"] = handler_arg
    return REQUEST_CONFIRM_ID


REQUEST_CONFIRM_ID = "request_confirm"


def request_confirm_show(user_id, state_args):
    return {
        "text":
        "Подтвердите:\nЗаголовок: " + state_args["title"] + "\n" +
        "Описание: " + state_args["description"] + "\n" + "Номер телефона: " +
        state_args["phone"],
        "photo":
        state_args["picture"],
        "keyboard": [
            [{
                "text": "Назад",
                "callback": REQUEST_CREATE_PICTURE_ID
            }],
            [{
                "text": "Подтвердить",
                "callback": {
                    "state_id": state_args["request_create_return"],
                    "handler_arg": "confirm",
                },
            }],
            [{
                "text": "Отменить",
                "callback": state_args["request_create_return"],
            }],
        ],
    }


def request_confirm_callback(user_id, state_args, state_id, handler_arg):
    if state_id in [
            REQUEST_CREATE_PICTURE_ID,
            state_args["request_create_return"],
    ]:
        if handler_arg == "confirm":
            with Session(engine["value"]) as session:
                session.add(
                    Request(
                        title=state_args["title"],
                        description=state_args["description"],
                        phone=state_args["phone"],
                        picture=state_args["picture"],
                        user_id=user_id,
                    ))
                session.commit()
        del state_args["picture"]
        if state_id == state_args["request_create_return"]:
            del state_args["phone"]
            del state_args["description"]
            del state_args["title"]
            del state_args["request_create_return"]


REQUEST_ID = "request"


def request_show(user_id, state_args):
    with Session(engine["value"]) as session:
        request = session.get(Request, state_args["id"])
        request_dict = {
            "title": request.title,
            "description": request.description,
            "phone": request.phone,
            "picture": request.picture,
        }
        admin = user_id == request.user_id
    return {
        "text":
        "Заголовок: " + request_dict["title"] + "\n" + "Описание: " +
        request_dict["description"] + "\n" + "Ном��р телефона: " +
        request_dict["phone"],
        "photo":
        request_dict["picture"],
        "keyboard": [
            [
                {
                    "text":
                    "Назад",
                    "callback":
                    ((state_args["request_return"] if isinstance(
                        state_args["request_return"], str) else OFFER_ID) if
                     ("request_return" in state_args) else MAIN_ID),
                },
            ],
            [{
                "text": "Специализации Заявки",
                "callback": REQUEST_SPECS_ID
            }],
            [{
                "text": "Офферы",
                "callback": OFFERS_ID
            }],
        ] + ([
            [{
                "text": "Изменить заголовок",
                "callback": REQUEST_EDIT_TITLE_ID,
            }],
            [{
                "text": "Изменить описание",
                "callback": REQUEST_EDIT_DESCRIPTION_ID,
            }],
            [{
                "text": "Изменить номер телефона",
                "callback": REQUEST_EDIT_PHONE_ID,
            }],
            [{
                "text": "Изменить фотографию",
                "callback": REQUEST_EDIT_PICTURE_ID,
            }],
            [{
                "text": "Удалить",
                "callback": REQUEST_DELETE_ID,
            }],
        ] if admin else []),
    }


def request_callback(user_id, state_args, state_id, handler_arg):
    if (state_id == MAIN_ID or state_id == OFFER_ID
            or "request_return" in state_args
            and state_id == state_args["request_return"]):
        if state_id == OFFER_ID:
            state_args["request_id"] = state_args["id"]
            state_args["ars_id"] = state_args["request_return"]
        del state_args["id"]
        if "request_return" in state_args:
            del state_args["request_return"]
        if state_id == MAIN_ID:
            if "ars_return" in state_args:
                del state_args["ars_return"]
            if "offer_return" in state_args:
                del state_args["offer_return"]
    elif state_id in [REQUEST_SPECS_ID, OFFERS_ID]:
        state_args["request_id"] = state_args["id"]
        del state_args["id"]


REQUEST_EDIT_TITLE_ID = "request_edit_title"


def request_edit_title_show(user_id, state_args):
    return {
        "text": "Введите новый заголовок",
        "keyboard": [[{
            "text": "Отменить",
            "callback": REQUEST_ID
        }]],
    }


def request_edit_title_text(user_id, state_args, handler_arg):
    try:
        state_args["title"] = process_title_input(handler_arg)
        return REQUEST_CONFIRM_TITLE_ID
    except ProcessException as exception:
        state_args["status"] = str(exception)
        return REQUEST_EDIT_TITLE_ID


REQUEST_CONFIRM_TITLE_ID = "request_confirm_title"


def request_confirm_title_show(user_id, state_args):
    return {
        "text":
        "Подтвердите: " + state_args["title"],
        "keyboard": [
            [{
                "text": "Назад",
                "callback": REQUEST_EDIT_TITLE_ID
            }],
            [{
                "text": "Подтвердить",
                "callback": {
                    "state_id": REQUEST_ID,
                    "handler_arg": "confirm",
                },
            }],
            [{
                "text": "Отменить",
                "callback": REQUEST_ID
            }],
        ],
    }


def request_confirm_title_callback(user_id, state_args, state_id, handler_arg):
    if state_id in [REQUEST_EDIT_TITLE_ID, REQUEST_ID]:
        if handler_arg == "confirm":
            with Session(engine["value"]) as session:
                session.get(Request,
                            state_args["id"]).title = state_args["title"]
                session.commit()
        del state_args["title"]


REQUEST_EDIT_DESCRIPTION_ID = "request_edit_description"


def request_edit_description_show(user_id, state_args):
    return {
        "text": "Введите новое описание",
        "keyboard": [[{
            "text": "Отменить",
            "callback": REQUEST_ID
        }]],
    }


def request_edit_description_text(user_id, state_args, handler_arg):
    try:
        state_args["description"] = process_description_input(handler_arg)
        return REQUEST_CONFIRM_DESCRIPTION_ID
    except ProcessException as exception:
        state_args["status"] = str(exception)
        return REQUEST_EDIT_DESCRIPTION_ID


REQUEST_CONFIRM_DESCRIPTION_ID = "request_confirm_description"


def request_confirm_description_show(user_id, state_args):
    return {
        "text":
        "Подтвердите: " + state_args["description"],
        "keyboard": [
            [{
                "text": "Назад",
                "callback": REQUEST_EDIT_DESCRIPTION_ID
            }],
            [{
                "text": "Подтвердить",
                "callback": {
                    "state_id": REQUEST_ID,
                    "handler_arg": "confirm",
                },
            }],
            [{
                "text": "Отменить",
                "callback": REQUEST_ID
            }],
        ],
    }


def request_confirm_description_callback(user_id, state_args, state_id,
                                         handler_arg):
    if state_id in [REQUEST_EDIT_DESCRIPTION_ID, REQUEST_ID]:
        if handler_arg == "confirm":
            with Session(engine["value"]) as session:
                session.get(
                    Request,
                    state_args["id"]).description = state_args["description"]
                session.commit()
        del state_args["description"]


REQUEST_EDIT_PHONE_ID = "request_edit_phone"


def request_edit_phone_show(user_id, state_args):
    return {
        "text": "Введите новый номер телефона",
        "keyboard": [[{
            "text": "Отменить",
            "callback": REQUEST_ID
        }]],
    }


def request_edit_phone_text(user_id, state_args, handler_arg):
    try:
        state_args["phone"] = handler_arg[:10]
        return REQUEST_CONFIRM_PHONE_ID
    except ProcessException as exception:
        state_args["status"] = str(exception)
        return REQUEST_EDIT_PHONE_ID


REQUEST_CONFIRM_PHONE_ID = "request_confirm_phone"


def request_confirm_phone_show(user_id, state_args):
    return {
        "text":
        "Подтвердите: " + state_args["phone"],
        "keyboard": [
            [{
                "text": "Назад",
                "callback": REQUEST_EDIT_PHONE_ID
            }],
            [{
                "text": "Подтвердить",
                "callback": {
                    "state_id": REQUEST_ID,
                    "handler_arg": "confirm",
                },
            }],
            [{
                "text": "Отменить",
                "callback": REQUEST_ID
            }],
        ],
    }


def request_confirm_phone_callback(user_id, state_args, state_id, handler_arg):
    if state_id in [REQUEST_EDIT_PHONE_ID, REQUEST_ID]:
        if handler_arg == "confirm":
            with Session(engine["value"]) as session:
                session.get(Request,
                            state_args["id"]).phone = state_args["phone"]
                session.commit()
        del state_args["phone"]


REQUEST_EDIT_PICTURE_ID = "request_edit_picture"


def request_edit_picture_show(user_id, state_args):
    return {
        "text":
        "Отправьте новую фотографию",
        "keyboard": [
            [{
                "text": "Пропустить",
                "callback": REQUEST_CONFIRM_PICTURE_ID
            }],
            [{
                "text": "Отменить",
                "callback": REQUEST_ID
            }],
        ],
    }


def request_edit_picture_callback(user_id, state_args, state_id, handler_arg):
    if state_id == REQUEST_CONFIRM_PICTURE_ID:
        state_args["picture"] = None


def request_edit_picture_photo(user_id, state_args, handler_arg):
    state_args["picture"] = handler_arg
    return REQUEST_CONFIRM_PICTURE_ID


REQUEST_CONFIRM_PICTURE_ID = "request_confirm_picture"


def request_confirm_picture_show(user_id, state_args):
    return {
        "text":
        "Подтвердите",
        "photo":
        state_args["picture"],
        "keyboard": [
            [{
                "text": "Назад",
                "callback": REQUEST_EDIT_PICTURE_ID
            }],
            [{
                "text": "Подтвердить",
                "callback": {
                    "state_id": REQUEST_ID,
                    "handler_arg": "confirm",
                },
            }],
            [{
                "text": "Отменить",
                "callback": REQUEST_ID
            }],
        ],
    }


def request_confirm_picture_callback(user_id, state_args, state_id,
                                     handler_arg):
    if state_id in [REQUEST_EDIT_PICTURE_ID, REQUEST_ID]:
        if handler_arg == "confirm":
            with Session(engine["value"]) as session:
                session.get(Request,
                            state_args["id"]).picture = state_args["picture"]
                session.commit()
        del state_args["picture"]


REQUEST_DELETE_ID = "request_delete"


def request_delete_show(user_id, state_args):
    return {
        "text":
        "Подтвердите",
        "keyboard": [
            [{
                "text":
                "Подтвердить",
                "callback":
                (state_args["request_return"] if
                 ("request_return" in state_args and isinstance(
                     state_args["request_return"], str)) else MAIN_ID),
            }],
            [{
                "text": "Отменить",
                "callback": REQUEST_ID
            }],
        ],
    }


def request_delete_callback(user_id, state_args, state_id, handler_arg):
    if (state_id == MAIN_ID or "request_return" in state_args
            and state_id == state_args["request_return"]):
        with Session(engine["value"]) as session:
            session.delete(session.get(Request, state_args["id"]))
            session.commit()
        del state_args["id"]
        if "request_return" in state_args:
            del state_args["ars_return"]
        if state_id == MAIN_ID:
            if "ars_return" in state_args:
                del state_args["ars_return"]
            if "offer_return" in state_args:
                del state_args["offer_return"]


REQUEST_SPECS_ID = "request_specs"


def request_specs_show(user_id, state_args):
    with Session(engine["value"]) as session:
        request_specs_list = [{
            "spec_id": request_spec.spec_id,
            "spec_title": request_spec.spec.title,
        } for request_spec in session.query(RequestSpec).where(
            RequestSpec.request_id == state_args["request_id"])]
        admin = user_id == session.get(Request,
                                       state_args["request_id"]).user_id
    return {
        "text":
        "Специализации заявки",
        "keyboard": [[
            {
                "text": "Назад",
                "callback": REQUEST_ID
            },
        ] + ([{
            "text": "Создать",
            "callback": REQUEST_SPEC_CREATE_SPEC_ID
        }] if admin else [])] + [[{
            "text": request_spec_dict["spec_title"],
            "callback": {
                "state_id": REQUEST_SPEC_ID,
                "handler_arg": str(request_spec_dict["spec_id"]),
            },
        }] for request_spec_dict in request_specs_list],
    }


def request_specs_callback(user_id, state_args, state_id, handler_arg):
    if state_id == REQUEST_ID:
        state_args["id"] = state_args["request_id"]
        del state_args["request_id"]
    if state_id == REQUEST_SPEC_ID:
        state_args["spec_id"] = int(handler_arg)


REQUEST_SPEC_CREATE_SPEC_ID = "request_spec_create_spec"


def request_spec_create_spec_show(user_id, state_args):
    with Session(engine["value"]) as session:
        specs_list = [{
            "id": spec.id,
            "title": spec.title
        } for spec in session.query(Spec).where(
            Spec.id.not_in(
                session.query(RequestSpec.spec_id).where(
                    RequestSpec.request_id == state_args["request_id"])))]
    return {
        "text":
        "Выберите специализацию",
        "keyboard": [[{
            "text": "Отменить",
            "callback": REQUEST_SPECS_ID
        }]] + [[{
            "text": spec_dict["title"],
            "callback": {
                "state_id": REQUEST_SPEC_CONFIRM_ID,
                "handler_arg": str(spec_dict["id"]),
            },
        }] for spec_dict in specs_list],
    }


def request_spec_create_spec_callback(user_id, state_args, state_id,
                                      handler_arg):
    if state_id == REQUEST_SPEC_CONFIRM_ID:
        state_args["spec_id"] = int(handler_arg)


REQUEST_SPEC_CONFIRM_ID = "request_spec_confirm"


def request_spec_confirm_show(user_id, state_args):
    with Session(engine["value"]) as session:
        spec_title = session.get(Spec, state_args["spec_id"]).title
    return {
        "text":
        "Подтвердите:\nСпециализация: " + spec_title,
        "keyboard": [
            [{
                "text": "Назад",
                "callback": REQUEST_SPEC_CREATE_SPEC_ID
            }],
            [{
                "text": "Подтвердить",
                "callback": {
                    "state_id": REQUEST_SPECS_ID,
                    "handler_arg": "confirm",
                },
            }],
            [{
                "text": "Отменить",
                "callback": REQUEST_SPECS_ID
            }],
        ],
    }


def request_spec_confirm_callback(user_id, state_args, state_id, handler_arg):
    if state_id in [REQUEST_SPEC_CREATE_SPEC_ID, REQUEST_SPECS_ID]:
        if handler_arg == "confirm":
            with Session(engine["value"]) as session:
                session.add(
                    RequestSpec(
                        request_id=state_args["request_id"],
                        spec_id=state_args["spec_id"],
                    ))
                session.commit()
        del state_args["spec_id"]


REQUEST_SPEC_ID = "request_spec"


def request_spec_show(user_id, state_args):
    with Session(engine["value"]) as session:
        request_spec = session.get(
            RequestSpec,
            {
                "request_id": state_args["request_id"],
                "spec_id": state_args["spec_id"],
            },
        )
        spec_title = request_spec.spec.title
        admin = user_id == request_spec.request.user_id
    return {
        "text":
        "Специализация: " + spec_title,
        "keyboard": [[{
            "text": "Назад",
            "callback": REQUEST_SPECS_ID
        }]] + ([
            [{
                "text": "Удалить",
                "callback": REQUEST_SPEC_DELETE_ID
            }],
        ] if admin else []),
    }


def request_spec_callback(user_id, state_args, state_id, handler_arg):
    if state_id == REQUEST_SPECS_ID:
        del state_args["spec_id"]


REQUEST_SPEC_DELETE_ID = "request_spec_delete"


def request_spec_delete_show(user_id, state_args):
    return {
        "text":
        "Подтвердите",
        "keyboard": [
            [{
                "text": "Подтвердить",
                "callback": REQUEST_SPECS_ID
            }],
            [{
                "text": "Отменить",
                "callback": REQUEST_SPEC_ID
            }],
        ],
    }


def request_spec_delete_callback(user_id, state_args, state_id, handler_arg):
    if state_id == REQUEST_SPECS_ID:
        with Session(engine["value"]) as session:
            session.delete(
                session.get(
                    RequestSpec,
                    {
                        "request_id": state_args["request_id"],
                        "spec_id": state_args["spec_id"],
                    },
                ))
            session.commit()
        del state_args["spec_id"]


OFFERS_ID = "offers"


def offers_show(user_id, state_args):
    with Session(engine["value"]) as session:
        offers_list = [{
            "ars_id": offer.ars_id,
            "ars_title": offer.ars.title,
            "cost_floor": offer.cost_floor,
            "cost_ceil": offer.cost_ceil,
            "winner": offer.winner,
        } for offer in session.query(Offer).where(
            Offer.request_id == state_args["request_id"])]
    return {
        "text":
        "Офферы",
        "keyboard": [[
            {
                "text": "Назад",
                "callback": REQUEST_ID
            },
            {
                "text": "Создать",
                "callback": OFFER_CREATE_ARS_ID
            },
        ]] + [[{
            "text": ("W" if offer_dict["winner"] else " ") + " " +
            offer_dict["ars_title"] + " " + str(offer_dict["cost_floor"]) +
            ((" " + str(offer_dict["cost_ceil"]))
             if offer_dict["cost_ceil"] else ""),
            "callback": {
                "state_id": OFFER_ID,
                "handler_arg": str(offer_dict["ars_id"]),
            },
        }] for offer_dict in offers_list],
    }


def offers_callback(user_id, state_args, state_id, handler_arg):
    if state_id == REQUEST_ID:
        state_args["id"] = state_args["request_id"]
        del state_args["request_id"]
    elif state_id == OFFER_ID:
        state_args["offer_return"] = OFFERS_ID
        state_args["ars_id"] = int(handler_arg)


OFFER_CREATE_ARS_ID = "offer_create_ars"


def offer_create_ars_show(user_id, state_args):
    with Session(engine["value"]) as session:
        arses_list = [{
            "id": ars.id,
            "title": ars.title
        } for ars in session.query(Ars).where(
            Ars.user_id == user_id and Ars.id.not_in(
                session.query(Offer.ars_id).where(
                    Offer.request_id == state_args["request_id"])))]
    return {
        "text":
        "Выберите СТО",
        "keyboard": [[{
            "text": "Отменить",
            "callback": OFFERS_ID,
        }]] + [[{
            "text": ars_dict["title"],
            "callback": {
                "state_id": OFFER_CREATE_COST_FLOOR_ID,
                "handler_arg": str(ars_dict["id"]),
            },
        }] for ars_dict in arses_list],
    }


def offer_create_ars_callback(user_id, state_args, state_id, handler_arg):
    if state_id == OFFER_CREATE_COST_FLOOR_ID:
        state_args["ars_id"] = int(handler_arg)


OFFER_CREATE_COST_FLOOR_ID = "offer_create_cost_floor"


def offer_create_cost_floor_show(user_id, state_args):
    return {
        "text":
        "Введите нижнюю цену",
        "keyboard": [
            [{
                "text": "Назад",
                "callback": OFFER_CREATE_ARS_ID
            }],
            [{
                "text": "Отменить",
                "callback": OFFERS_ID,
            }],
        ],
    }


def offer_create_cost_floor_callback(user_id, state_args, state_id,
                                     handler_arg):
    if state_id in [OFFER_CREATE_ARS_ID, OFFERS_ID]:
        del state_args["ars_id"]


def offer_create_cost_floor_text(user_id, state_args, handler_arg):
    try:
        state_args["cost_floor"] = process_cost_input(handler_arg)
        return OFFER_CREATE_COST_CEIL_ID
    except ProcessException as exception:
        state_args["status"] = str(exception)
        return OFFER_CREATE_COST_FLOOR_ID


OFFER_CREATE_COST_CEIL_ID = "offer_create_cost_ceil"


def offer_create_cost_ceil_show(user_id, state_args):
    return {
        "text":
        "Введите верхнюю цену",
        "keyboard": [
            [{
                "text": "Назад",
                "callback": OFFER_CREATE_COST_FLOOR_ID
            }],
            [{
                "text": "Пропустить",
                "callback": OFFER_CREATE_DESCRIPTION_ID
            }],
            [{
                "text": "Отменить",
                "callback": OFFERS_ID,
            }],
        ],
    }


def offer_create_cost_ceil_callback(user_id, state_args, state_id,
                                    handler_arg):
    if state_id == OFFER_CREATE_DESCRIPTION_ID:
        state_args["cost_ceil"] = None
    elif state_id in [
            OFFER_CREATE_COST_FLOOR_ID,
            OFFERS_ID,
    ]:
        del state_args["cost_floor"]
        if state_id == OFFERS_ID:
            del state_args["ars_id"]


def offer_create_cost_ceil_text(user_id, state_args, handler_arg):
    try:
        state_args["cost_ceil"] = process_cost_input(
            handler_arg, cost_floor=state_args["cost_floor"])
        return OFFER_CREATE_DESCRIPTION_ID
    except ProcessException as exception:
        state_args["status"] = str(exception)
        return OFFER_CREATE_COST_CEIL_ID


OFFER_CREATE_DESCRIPTION_ID = "offer_create_description"


def offer_create_description_show(user_id, state_args):
    return {
        "text":
        "Введите описание",
        "keyboard": [
            [{
                "text": "Назад",
                "callback": OFFER_CREATE_COST_CEIL_ID
            }],
            [{
                "text": "Отменить",
                "callback": OFFERS_ID,
            }],
        ],
    }


def offer_create_description_callback(user_id, state_args, state_id,
                                      handler_arg):
    if state_id in [
            OFFER_CREATE_COST_CEIL_ID,
            OFFERS_ID,
    ]:
        del state_args["cost_ceil"]
        if state_id == OFFERS_ID:
            del state_args["cost_floor"]
            del state_args["ars_id"]


def offer_create_description_text(user_id, state_args, handler_arg):
    try:
        state_args["description"] = process_description_input(handler_arg)
        return OFFER_CONFIRM_ID
    except ProcessException as exception:
        state_args["status"] = str(exception)
        return OFFER_CREATE_DESCRIPTION_ID


OFFER_CONFIRM_ID = "offer_confirm"


def offer_confirm_show(user_id, state_args):
    with Session(engine["value"]) as session:
        ars_title = session.get(Ars, state_args["ars_id"]).title
    return {
        "text":
        "Подтвердите:\nСТО: " + ars_title + "\n" + "Нижняя цена: " +
        str(state_args["cost_floor"]) + "\n" + "Верхняя цена: " +
        str(state_args["cost_ceil"]) + "\n" + "Описание: " +
        state_args["description"],
        "keyboard": [
            [{
                "text": "Назад",
                "callback": OFFER_CREATE_DESCRIPTION_ID
            }],
            [{
                "text": "Подтвердить",
                "callback": {
                    "state_id": OFFERS_ID,
                    "handler_arg": "confirm",
                },
            }],
            [{
                "text": "Отменить",
                "callback": OFFERS_ID,
            }],
        ],
    }


def offer_confirm_callback(user_id, state_args, state_id, handler_arg):
    if state_id in [
            OFFER_CREATE_DESCRIPTION_ID,
            OFFERS_ID,
    ]:
        if handler_arg == "confirm":
            with Session(engine["value"]) as session:
                session.add(
                    Offer(
                        request_id=state_args["request_id"],
                        ars_id=state_args["ars_id"],
                        cost_floor=state_args["cost_floor"],
                        cost_ceil=state_args["cost_ceil"],
                        description=state_args["description"],
                        winner=False,
                    ))
                session.commit()
        del state_args["description"]
        if state_id == OFFERS_ID:
            del state_args["cost_ceil"]
            del state_args["cost_floor"]
            del state_args["ars_id"]


OFFER_ID = "offer"


def offer_show(user_id, state_args):
    with Session(engine["value"]) as session:
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
        admin_request = user_id == offer.request.user_id
        admin_ars = user_id == offer.ars.user_id
    return {
        "text":
        "Нижняя цена: " + str(offer_dict["cost_floor"]) + "\n" +
        "Верхняя цена: " + str(offer_dict["cost_ceil"]) + "\n" + "Описание: " +
        offer_dict["description"] + "\n" + "Победитель: " +
        ("W" if offer_dict["winner"] else " "),
        "keyboard": [
            [{
                "text":
                "Назад",
                "callback": (state_args["offer_return"]
                             if "offer_return" in state_args else MAIN_ID),
            }],
            [{
                "text": "Заявка",
                "callback": REQUEST_ID
            }],
            [{
                "text": "СТО",
                "callback": ARS_ID
            }],
        ] + ([
            [{
                "text": "Изменить нижнюю цену",
                "callback": OFFER_EDIT_COST_FLOOR_ID,
            }],
            [{
                "text": "Изменить верхнюю цену",
                "callback": OFFER_EDIT_COST_CEIL_ID,
            }],
            [{
                "text": "Изменить описание",
                "callback": OFFER_EDIT_DESCRIPTION_ID,
            }],
            [{
                "text": "Удалить",
                "callback": OFFER_DELETE_ID,
            }],
        ] if admin_ars else []) + ([[{
            "text": "Выбрать победителем",
            "callback": OFFER_CONFIRM_WINNER_ID,
        }]] if (admin_request and not offer_dict["winner"]) else []),
    }


def offer_callback(user_id, state_args, state_id, handler_arg):
    if (state_id == MAIN_ID or "offer_return" in state_args
            and state_id == state_args["offer_return"]):
        if "offer_return" in state_args:
            if state_args["offer_return"] == OFFERS_ID:
                del state_args["ars_id"]
            elif state_args["offer_return"] == ARS_OFFERS_ID:
                del state_args["request_id"]
            del state_args["offer_return"]
        else:
            if "ars_return" in state_args:
                del state_args["ars_return"]
            if "request_return" in state_args:
                del state_args["request_return"]
            del state_args["request_id"]
            del state_args["ars_id"]
    elif state_id == REQUEST_ID:
        state_args["id"] = state_args["request_id"]
        state_args["request_return"] = state_args["ars_id"]
        del state_args["request_id"]
        del state_args["ars_id"]
    elif state_id == ARS_ID:
        state_args["id"] = state_args["ars_id"]
        state_args["ars_return"] = state_args["request_id"]
        del state_args["request_id"]
        del state_args["ars_id"]


OFFER_EDIT_COST_FLOOR_ID = "offer_edit_cost_floor"


def offer_edit_cost_floor_show(user_id, state_args):
    return {
        "text": "Введите новую нижнюю цену",
        "keyboard": [[{
            "text": "Отменить",
            "callback": OFFER_ID
        }]],
    }


def offer_edit_cost_floor_text(user_id, state_args, handler_arg):
    try:
        with Session(engine["value"]) as session:
            cost_ceil = session.get(
                Offer,
                {
                    "request_id": state_args["request_id"],
                    "ars_id": state_args["ars_id"],
                },
            ).cost_ceil
        state_args["cost_floor"] = process_cost_input(handler_arg,
                                                      cost_ceil=cost_ceil)
        return OFFER_CONFIRM_COST_FLOOR_ID
    except ProcessException as exception:
        state_args["status"] = str(exception)
        return OFFER_EDIT_COST_FLOOR_ID


OFFER_CONFIRM_COST_FLOOR_ID = "offer_confirm_cost_floor"


def offer_confirm_cost_floor_show(user_id, state_args):
    return {
        "text":
        "Подтвердите: " + str(state_args["cost_floor"]),
        "keyboard": [
            [{
                "text": "Назад",
                "callback": OFFER_EDIT_COST_FLOOR_ID
            }],
            [{
                "text": "Подтвердить",
                "callback": {
                    "state_id": OFFER_ID,
                    "handler_arg": "confirm",
                },
            }],
            [{
                "text": "Отменить",
                "callback": OFFER_ID
            }],
        ],
    }


def offer_confirm_cost_floor_callback(user_id, state_args, state_id,
                                      handler_arg):
    if state_id in [OFFER_EDIT_COST_FLOOR_ID, OFFER_ID]:
        if handler_arg == "confirm":
            with Session(engine["value"]) as session:
                session.get(
                    Offer,
                    {
                        "request_id": state_args["request_id"],
                        "ars_id": state_args["ars_id"],
                    },
                ).cost_floor = state_args["cost_floor"]
                session.commit()
        del state_args["cost_floor"]


OFFER_EDIT_COST_CEIL_ID = "offer_edit_cost_ceil"


def offer_edit_cost_ceil_show(user_id, state_args):
    return {
        "text":
        "Введите новую верхнюю цену",
        "keyboard": [
            [{
                "text": "Пропустить",
                "calblack": OFFER_CONFIRM_COST_CEIL_ID,
            }],
            [{
                "text": "Отменить",
                "callback": OFFER_ID
            }],
        ],
    }


def offer_edit_cost_ceil_callback(user_id, state_args, state_id, handler_arg):
    if state_id == OFFER_CONFIRM_COST_CEIL_ID:
        state_args["cost_ceil"] = None


def offer_edit_cost_ceil_text(user_id, state_args, handler_arg):
    try:
        with Session(engine["value"]) as session:
            cost_floor = session.get(
                Offer,
                {
                    "request_id": state_args["request_id"],
                    "ars_id": state_args["ars_id"],
                },
            ).cost_floor
        state_args["cost_ceil"] = process_cost_input(handler_arg,
                                                     cost_floor=cost_floor)
        return OFFER_CONFIRM_COST_CEIL_ID
    except ProcessException as exception:
        state_args["status"] = str(exception)
        return OFFER_EDIT_COST_CEIL_ID


OFFER_CONFIRM_COST_CEIL_ID = "offer_confirm_cost_ceil"


def offer_confirm_cost_ceil_show(user_id, state_args):
    return {
        "text":
        "Подтвердите: " + str(state_args["cost_ceil"]),
        "keyboard": [
            [{
                "text": "Назад",
                "callback": OFFER_EDIT_COST_CEIL_ID
            }],
            [{
                "text": "Подтвердить",
                "callback": {
                    "state_id": OFFER_ID,
                    "handler_arg": "confirm",
                },
            }],
            [{
                "text": "Отменить",
                "callback": OFFER_ID
            }],
        ],
    }


def offer_confirm_cost_ceil_callback(user_id, state_args, state_id,
                                     handler_arg):
    if state_id in [OFFER_EDIT_COST_CEIL_ID, OFFER_ID]:
        if handler_arg == "confirm":
            with Session(engine["value"]) as session:
                session.get(
                    Offer,
                    {
                        "request_id": state_args["request_id"],
                        "ars_id": state_args["ars_id"],
                    },
                ).cost_ceil = state_args["cost_ceil"]
                session.commit()
        del state_args["cost_ceil"]


OFFER_EDIT_DESCRIPTION_ID = "offer_edit_description"


def offer_edit_description_show(user_id, state_args):
    return {
        "text": "Введите новое описание",
        "keyboard": [[{
            "text": "Отменить",
            "callback": OFFER_ID
        }]],
    }


def offer_edit_description_text(user_id, state_args, handler_arg):
    try:
        state_args["description"] = process_description_input(handler_arg)
        return OFFER_CONFIRM_DESCRIPTION_ID
    except ProcessException as exception:
        state_args["status"] = str(exception)
        return OFFER_EDIT_DESCRIPTION_ID


OFFER_CONFIRM_DESCRIPTION_ID = "offer_confirm_description"


def offer_confirm_description_show(user_id, state_args):
    return {
        "text":
        "Подтвердите: " + state_args["description"],
        "keyboard": [
            [{
                "text": "Назад",
                "callback": OFFER_EDIT_DESCRIPTION_ID
            }],
            [{
                "text": "Подтвердить",
                "callback": {
                    "state_id": OFFER_ID,
                    "handler_arg": "confirm",
                },
            }],
            [{
                "text": "Отменить",
                "callback": OFFER_ID
            }],
        ],
    }


def offer_confirm_description_callback(user_id, state_args, state_id,
                                       handler_arg):
    if state_id in [OFFER_EDIT_DESCRIPTION_ID, OFFER_ID]:
        if handler_arg == "confirm":
            with Session(engine["value"]) as session:
                session.get(
                    Offer,
                    {
                        "request_id": state_args["request_id"],
                        "ars_id": state_args["ars_id"],
                    },
                ).description = state_args["description"]
                session.commit()
        del state_args["description"]


OFFER_CONFIRM_WINNER_ID = "offer_confirm_winner"


def offer_confirm_winner_show(user_id, state_args):
    return {
        "text":
        "Подтвердите",
        "keyboard": [
            [{
                "text": "Подтвердить",
                "callback": {
                    "state_id": OFFER_ID,
                    "handler_arg": "confirm",
                },
            }],
            [{
                "text": "Отменить",
                "callback": OFFER_ID
            }],
        ],
    }


def offer_confirm_winner_callback(user_id, state_args, state_id, handler_arg):
    if state_id == OFFER_ID:
        if handler_arg == "confirm":
            with Session(engine["value"]) as session:
                session.get(
                    Offer,
                    {
                        "request_id": state_args["request_id"],
                        "ars_id": state_args["ars_id"],
                    },
                ).winner = True
                session.commit()


OFFER_DELETE_ID = "offer_delete"


def offer_delete_show(user_id, state_args):
    return {
        "text":
        "Подтвердите",
        "keyboard": [
            [{
                "text":
                "Подтвердить",
                "callback": (state_args["offer_return"]
                             if "offer_return" in state_args else MAIN_ID),
            }],
            [{
                "text": "Отменить",
                "callback": OFFER_ID
            }],
        ],
    }


def offer_delete_callback(user_id, state_args, state_id, handler_arg):
    if (state_id == MAIN_ID or "offer_return" in state_args
            and state_id == state_args["offer_return"]):
        with Session(engine["value"]) as session:
            session.delete(
                session.get(
                    Offer,
                    {
                        "request_id": state_args["request_id"],
                        "ars_id": state_args["ars_id"],
                    },
                ))
            session.commit()
        if "offer_return" in state_args:
            if state_args["offer_return"] == OFFERS_ID:
                del state_args["ars_id"]
            elif state_args["offer_return"] == ARS_OFFERS_ID:
                del state_args["request_id"]
            del state_args["offer_return"]
        else:
            if "ars_return" in state_args:
                del state_args["ars_return"]
            if "request_return" in state_args:
                del state_args["request_return"]
            del state_args["request_id"]
            del state_args["ars_id"]
"""
