from datetime import date
from decimal import Decimal, InvalidOperation

from fuzzywuzzy import process
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import (ARS_TITLE_LENGTH, DESCRIPTION_LENGTH, FUEL_TEXT_MAP, Ars,
                     Auto, Registration, Request, Spec, User, Vendor)

engine = {
    "value": None,
}

DEFAULT_VENDOR_TITLES_LIST = [
    "Volkswagen",
    "Renault",
    "Skoda",
    "Toyota",
    "Ford",
    "Opel",
    "Hyundai",
    "Mersedes-Benz",
    "Daewoo",
]

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
            fuel = auto.fuel
            volume = auto.volume
    return {
        "text":
        "Клиент\n" +
        ("\n" + vendor_title + "\n" + year + "\n" + FUEL_TEXT_MAP[fuel] +
         "\n" + str(volume) if auto is not None else ""),
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
                    "callback": CLIENT_REQUESTS_ID,
                },
            ],
        ] if auto is not None else []),
    }


CHANGE_AUTO_VENDOR_ID = "change_auto_vendor"


def change_auto_vendor_show(user_id, state_args):
    is_search = False
    if "search" in state_args:
        search = state_args["search"]
        is_search = True
    with Session(engine["value"]) as session:
        if is_search:
            vendors_dict = {
                vendor.id: vendor.title
                for vendor in session.query(Vendor).all()
            }
        else:
            vendors_list = [{
                "id":
                session.execute(select(Vendor).where(
                    Vendor.title == title)).scalars().first().id,
                "title":
                title,
            } for title in DEFAULT_VENDOR_TITLES_LIST]
    if is_search:
        vendors_list = [{
            "id": search_result[2],
            "title": search_result[0],
        } for search_result in process.extract(search, vendors_dict, limit=9)]
    return {
        "text":
        "Выберите марку авто или введите вручную",
        "photo":
        "AgACAgIAAxkBAAIDXGHxSaL6ORLMthA-QvusMDhD0A8OAALbuDEbZMaIS_H7E-LwbqZGAQADAgADcwADIwQ",
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
    if "search" in state_args:
        del state_args["search"]
    if state_id == CHANGE_AUTO_YEAR_ID:
        state_args["vendor_id"] = int(handler_arg)


def change_auto_vendor_text(user_id, state_args, handler_arg):
    if len(handler_arg) != 0:
        state_args["search"] = handler_arg
    elif "search" in state_args:
        del state_args["search"]
    return CHANGE_AUTO_VENDOR_ID


CHANGE_AUTO_YEAR_ID = "change_auto_year"


def change_auto_year_show(user_id, state_args):
    today_year = date.today().year
    render_years = []
    for i in range(3):
        render_years_row = []
        for j in range(3):
            str_year = str(today_year - 2 - i * 3 - j)
            render_years_row.append({
                "text": str_year,
                "callback": {
                    "state_id": CHANGE_AUTO_FUEL_ID,
                    "handler_arg": str_year,
                },
            })
        render_years.append(render_years_row)
    return {
        "text":
        "Выберите год выпуска Вашего авто или введите вручную",
        "photo":
        "AgACAgIAAxkBAAIDVWHxQV_vOdKeipTI5FNStBBJRbGMAAKyuDEbZMaIS3fMyQzlmN9BAQADAgADcwADIwQ",
        "keyboard": [
            [
                {
                    "text": "Отменить",
                    "callback": CLIENT_ID,
                },
            ],
        ] + render_years,
    }


def change_auto_year_callback(user_id, state_args, state_id, handler_arg):
    if state_id == CHANGE_AUTO_FUEL_ID:
        state_args["year"] = handler_arg
        return
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
    return CHANGE_AUTO_FUEL_ID


CHANGE_AUTO_FUEL_ID = "change_auto_fuel"


def change_auto_fuel_show(user_id, state_args):
    return {
        "text":
        "Выберите вид топлива авто",
        "photo":
        "AgACAgIAAxkBAAIDVGHxPdZzlJPa7wITyeubx5_F-_OcAAKouDEbZMaISxJEH1CrzvwLAQADAgADcwADIwQ",
        "keyboard": [
            [
                {
                    "text": "Отменить",
                    "callback": CLIENT_ID,
                },
            ],
        ] + [[
            {
                "text": fuel_text_item[1],
                "callback": {
                    "state_id": CHANGE_AUTO_VOLUME_ID,
                    "handler_arg": fuel_text_item[0],
                },
            },
        ] for fuel_text_item in FUEL_TEXT_MAP.items()],
    }


def change_auto_fuel_callback(user_id, state_args, state_id, handler_arg):
    if state_id == CHANGE_AUTO_VOLUME_ID:
        state_args["fuel"] = handler_arg
        return
    del state_args["year"]
    del state_args["vendor_id"]


CHANGE_AUTO_VOLUME_ID = "change_auto_volume"


def change_auto_volume_show(user_id, state_args):
    return {
        "text":
        "Введите объем двигателя Вашего авто в литрах, через точку. Пример:  1.2",
        "photo":
        "AgACAgIAAxkBAAIDVmHxQZoAAb8BlKhqC-GWxFt-h1ZrpwACtbgxG2TGiEtDJrZQZfnmNQEAAwIAA3MAAyME",
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
    del state_args["fuel"]
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
    fuel = state_args["fuel"]
    del state_args["fuel"]
    year = state_args["year"]
    del state_args["year"]
    vendor_id = state_args["vendor_id"]
    del state_args["vendor_id"]
    with Session(engine["value"]) as session:
        auto = session.execute(
            select(Auto).where(Auto.user_id == user_id)).scalars().first()
        if auto is None:
            session.add(
                Auto(vendor_id=vendor_id,
                     year=year,
                     fuel=fuel,
                     volume=handler_arg,
                     user_id=user_id))
        else:
            auto.vendor_id = vendor_id
            auto.year = year
            auto.fuel = fuel
            auto.volume = handler_arg
        session.commit()
    return CLIENT_ID


CREATE_REQUEST_SPEC_ID = "create_request_spec"


def create_request_spec_show(user_id, state_args):
    with Session(engine["value"]) as session:
        specs_list = [{
            "id": spec.id,
            "title": spec.title,
        } for spec in session.query(Spec).all()]
    return {
        "text":
        "Выберите специализацию",
        "keyboard": [
            [
                {
                    "text": "Отменить",
                    "callback": CLIENT_ID,
                },
            ],
        ] + [[
            {
                "text": spec_dict["title"],
                "callback": {
                    "state_id": CLIENT_REQUEST_ID,
                    "handler_arg": str(spec_dict["id"]),
                },
            },
        ] for spec_dict in specs_list],
    }


def create_request_spec_callback(user_id, state_args, state_id, handler_arg):
    if state_id == CLIENT_REQUEST_ID:
        with Session(engine["value"]) as session:
            request = Request(
                spec_id=int(handler_arg),
                auto_id=session.execute(
                    select(Auto).where(
                        Auto.user_id == user_id)).scalars().first().id)
            session.add(request)
            session.commit()
            request_id = request.id
        state_args["id"] = request_id


CLIENT_REQUESTS_ID = "client_requests"


def client_requests_show(user_id, state_args):
    with Session(engine["value"]) as session:
        requests_list = [{
            "id": request.id,
            "spec_title": request.spec.title,
        } for request in session.execute(
            select(Request).where(Request.auto_id == session.execute(
                select(Auto).where(Auto.user_id == user_id)).scalars().first().
                                  id)).scalars().all()]
    return {
        "text":
        "Заявки",
        "keyboard": [
            [
                {
                    "text": "Кабинет",
                    "callback": CLIENT_ID,
                },
            ],
        ] + [[
            {
                "text": request_dict["spec_title"],
                "callback": {
                    "state_id": CLIENT_REQUEST_ID,
                    "handler_arg": str(request_dict["id"]),
                },
            },
        ] for request_dict in requests_list],
    }


def client_requests_callback(user_id, state_args, state_id, handler_arg):
    if state_id == CLIENT_REQUEST_ID:
        state_args["id"] = int(handler_arg)


CLIENT_REQUEST_ID = "client_request"


def client_request_show(user_id, state_args):
    request_id = state_args["id"]
    with Session(engine["value"]) as session:
        spec_title = session.execute(
            select(Request).where(
                Request.id == request_id)).scalars().first().spec.title
    return {
        "text": "Заявка\n\n" + spec_title,
        "keyboard": [
            [
                {
                    "text": "Заявки",
                    "callback": CLIENT_REQUESTS_ID,
                },
            ],
        ],
    }


def client_request_callback(user_id, state_args, state_id, handler_arg):
    del state_args["id"]


DILLER_ID = "diller"


def diller_show(user_id, state_args):
    with Session(engine["value"]) as session:
        ars = session.execute(
            select(Ars).where(Ars.user_id == user_id)).scalars().first()
        title = ars.title
        description = ars.description
        picture = ars.picture
        spec_titles_list = [spec.title for spec in ars.specs]
    render_message = {
        "text":
        "Диллер\n" + ("\n" + title if title is not None else "") +
        ("\n" + description if description is not None else "") +
        ("\n" +
         " ".join(spec_titles_list) if len(spec_titles_list) != 0 else ""),
        "keyboard": [
            [
                {
                    "text": "Изменить название",
                    "callback": CHANGE_ARS_TITLE_ID,
                },
            ],
            [
                {
                    "text": "Изменить описание",
                    "callback": CHANGE_ARS_DESCRIPTION_ID,
                },
            ],
            [
                {
                    "text": "Изменить изображение",
                    "callback": CHANGE_ARS_PICTURE_ID,
                },
            ],
            [
                {
                    "text": "Изменить специализации",
                    "callback": CHANGE_ARS_SPECS_ID,
                },
            ],
            [
                {
                    "text": "Заявки",
                    "callback": DILLER_REQUESTS_ID,
                },
            ],
        ],
    }
    if picture is not None:
        render_message["photo"] = picture
    return render_message


def diller_callback(user_id, state_args, state_id, handler_arg):
    if state_id == CHANGE_ARS_SPECS_ID:
        with Session(engine["value"]) as session:
            spec_ids_list = [
                spec.id for spec in session.execute(
                    select(Ars).where(
                        Ars.user_id == user_id)).scalars().first().specs
            ]
        state_args["spec_ids"] = spec_ids_list


CHANGE_ARS_TITLE_ID = "change_ars_title"


def change_ars_title_show(user_id, state_args):
    return {
        "text": "Введите название",
        "keyboard": [
            [
                {
                    "text": "Отменить",
                    "callback": DILLER_ID,
                },
            ],
        ],
    }


def change_ars_title_text(user_id, state_args, handler_arg):
    if len(handler_arg) <= ARS_TITLE_LENGTH:
        with Session(engine["value"]) as session:
            session.execute(select(Ars).where(
                Ars.user_id == user_id)).scalars().first().title = handler_arg
            session.commit()
        return DILLER_ID
    state_args["status"] = "Слишком длинный"
    return CHANGE_ARS_TITLE_ID


CHANGE_ARS_DESCRIPTION_ID = "change_ars_description"


def change_ars_description_show(user_id, state_args):
    return {
        "text": "Введите описание",
        "keyboard": [
            [
                {
                    "text": "Отменить",
                    "callback": DILLER_ID,
                },
            ],
        ],
    }


def change_ars_description_text(user_id, state_args, handler_arg):
    if len(handler_arg) <= DESCRIPTION_LENGTH:
        with Session(engine["value"]) as session:
            session.execute(select(Ars).where(Ars.user_id == user_id)).scalars(
            ).first().description = handler_arg
            session.commit()
        return DILLER_ID
    state_args["status"] = "Слишком длинный"
    return CHANGE_ARS_DESCRIPTION_ID


CHANGE_ARS_PICTURE_ID = "change_ars_picture"


def change_ars_picture_show(user_id, state_args):
    return {
        "text": "Отправьте фотографию",
        "keyboard": [
            [
                {
                    "text": "Отменить",
                    "callback": DILLER_ID,
                },
            ],
        ],
    }


def change_ars_picture_photo(user_id, state_args, handler_arg):
    with Session(engine["value"]) as session:
        session.execute(select(Ars).where(
            Ars.user_id == user_id)).scalars().first().picture = handler_arg
        session.commit()
    return DILLER_ID


CHANGE_ARS_SPECS_ID = "change_ars_specs"


def change_ars_specs_show(user_id, state_args):
    spec_ids_list = state_args["spec_ids"]
    with Session(engine["value"]) as session:
        specs_list = [{
            "id": spec.id,
            "title": spec.title,
        } for spec in session.query(Spec).all()]
        spec_titles_list = [
            session.get(Spec, spec_id).title for spec_id in spec_ids_list
        ]
    return {
        "text":
        "Выберите специализацию\n" +
        ("\n" +
         " ".join(spec_titles_list) if len(spec_titles_list) != 0 else ""),
        "keyboard": [
            [
                {
                    "text": "Кабинет",
                    "callback": DILLER_ID,
                },
            ],
        ] + [[
            {
                "text": spec_dict["title"],
                "callback": {
                    "state_id": CHANGE_ARS_SPECS_ID,
                    "handler_arg": str(spec_dict["id"]),
                },
            },
        ] for spec_dict in specs_list],
    }


def change_ars_specs_callback(user_id, state_args, state_id, handler_arg):
    spec_ids_list = state_args["spec_ids"]
    if state_id == CHANGE_ARS_SPECS_ID:
        spec_id = int(handler_arg)
        if spec_id in spec_ids_list:
            spec_ids_list.remove(spec_id)
        else:
            spec_ids_list.append(spec_id)
    else:
        del state_args["spec_ids"]
        with Session(engine["value"]) as session:
            ars = session.execute(
                select(Ars).where(Ars.user_id == user_id)).scalars().first()
            specs = ars.specs
            specs.clear()
            for spec_id in spec_ids_list:
                specs.append(session.get(Spec, spec_id))
            session.commit()


DILLER_REQUESTS_ID = "diller_requests"


def diller_requests_show(user_id, state_args):
    with Session(engine["value"]) as session:
        spec_ids_list = [
            spec.id for spec in session.execute(
                select(Ars).where(
                    Ars.user_id == user_id)).scalars().first().specs
        ]
        requests_list = [{
            "id": request.id,
            "spec_title": request.spec.title,
        } for request in session.query(Request).all()
                         if request.spec.id in spec_ids_list]
    return {
        "text":
        "Заявки",
        "keyboard": [
            [
                {
                    "text": "Кабинет",
                    "callback": DILLER_ID,
                },
            ],
        ] + [[
            {
                "text": request_dict["spec_title"],
                "callback": {
                    "state_id": DILLER_ID,
                    "handler_arg": str(request_dict["id"]),
                },
            },
        ] for request_dict in requests_list],
    }
