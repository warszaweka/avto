from datetime import date
from decimal import Decimal, InvalidOperation

from fuzzywuzzy import process
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import (ARS_TITLE_LENGTH, DESCRIPTION_LENGTH, FUEL_TEXT_MAP, Ars,
                     Auto, Offer, Registration, Request, Spec, User, Vendor)

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
    has_auto = False
    with Session(engine["value"]) as session:
        if session.execute(select(Auto).where(
                Auto.user_id == user_id)).scalars().first() is not None:
            has_auto = True
    return {
        "text":
        "Главное меню навигации Автопилота."\
        "\nВвод новых заявок и контроль уже поданных происходит отсюда."\
        "\nЕсли нужна помощь, обратитесь в поддержку."\
        "\nХорошего вам дня!",
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
                    "text": "Новая заявка",
                    "callback": CREATE_REQUEST_SPEC_ID,
                },
            ],
            [
                {
                    "text": "Заявки в работе",
                    "callback": CLIENT_REQUESTS_ID,
                },
            ],
            [
                {
                    "text": "Победы",
                    "callback": CLIENT_WINS_ID,
                },
            ],
        ] if has_auto else []) + [
            [
                {
                    "text": "Поддержка",
                    "url": "tg://user?id=547862853",
                },
            ],
        ],
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
    if state_id == CLIENT_ID:
        del state_args["vendor_id"]
        return
    state_args["year"] = handler_arg


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
    if state_id == CLIENT_ID:
        del state_args["year"]
        del state_args["vendor_id"]
        return
    state_args["fuel"] = handler_arg


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
        "Укажите какие услуги СТО вам необходимы и двигаемся далее. Если есть сомнения, в следующе"\
        "м окне вы сможете описать техническую проблему.",
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
                    "state_id": CREATE_REQUEST_DESCRIPTION_ID,
                    "handler_arg": str(spec_dict["id"]),
                },
            },
        ] for spec_dict in specs_list],
    }


def create_request_spec_callback(user_id, state_args, state_id, handler_arg):
    if state_id == CREATE_REQUEST_DESCRIPTION_ID:
        state_args["spec_id"] = int(handler_arg)


CREATE_REQUEST_DESCRIPTION_ID = "create_request_description"


def create_request_description_show(user_id, state_args):
    return {
        "text": "Если вы хотите добавить описание или комментарий к ремонту, то это можно сделать"\
        " сейчас. Это необязательное для заполнения поле, но любая дополнительная информация помо"\
        "жет нашим специалистам в решении проблемы.",
        "keyboard": [
            [
                {
                    "text": "Отменить",
                    "callback": CLIENT_ID,
                },
            ],
        ],
    }


def create_request_description_callback(user_id, state_args, state_id,
                                        handler_arg):
    del state_args["spec_id"]


def create_request_description_text(user_id, state_args, handler_arg):
    if len(handler_arg) > DESCRIPTION_LENGTH:
        state_args["status"] = "Слишком длинный"
        return CREATE_REQUEST_DESCRIPTION_ID
    spec_id = state_args["spec_id"]
    del state_args["spec_id"]
    with Session(engine["value"]) as session:
        request = Request(
            spec_id=spec_id,
            description=handler_arg,
            auto_id=session.execute(
                select(Auto).where(
                    Auto.user_id == user_id)).scalars().first().id)
        session.add(request)
        session.commit()
        request_id = request.id
    state_args["id"] = request_id
    return CLIENT_REQUEST_ID


CLIENT_REQUESTS_ID = "client_requests"


def client_requests_show(user_id, state_args):
    requests_list = []
    with Session(engine["value"]) as session:
        for request in session.execute(
                select(Auto).where(
                    Auto.user_id == user_id)).scalars().first().requests:
            is_win = False
            for offer in request.offers:
                if offer.winner:
                    is_win = True
                    break
            if not is_win:
                requests_list.append({
                    "id": request.id,
                    "spec_title": request.spec.title,
                })
    return {
        "text":
        "Список поданных вами заявок. Здесь вы можете видеть их статус и перейти к конкретной зая"\
        "вке для ее подтверждения или отмены",
        "keyboard": [
            [
                {
                    "text": "Главное меню",
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
        request = session.get(Request, request_id)
        spec_title = request.spec.title
        offers_list = [{
            "ars_id": offer.ars_id,
            "cost_floor": offer.cost_floor,
            "cost_ceil": offer.cost_ceil,
        } for offer in request.offers]
    render_offers = []
    for offer_dict in offers_list:
        cost_ceil = offer_dict["cost_ceil"]
        render_offers.append([
            {
                "text":
                str(offer_dict["cost_floor"]) +
                ("-" + str(cost_ceil) if cost_ceil is not None else ""),
                "callback": {
                    "state_id": CLIENT_OFFER_ID,
                    "handler_arg": str(offer_dict["ars_id"]),
                },
            },
        ])
    return {
        "text":
        "Заявка\n\n" + spec_title,
        "keyboard": [
            [
                {
                    "text": "Заявки",
                    "callback": CLIENT_REQUESTS_ID,
                },
            ],
        ] + render_offers,
    }


def client_request_callback(user_id, state_args, state_id, handler_arg):
    if state_id == CLIENT_OFFER_ID:
        state_args["request_id"] = state_args["id"]
        state_args["ars_id"] = int(handler_arg)
    del state_args["id"]


CLIENT_OFFER_ID = "client_offer"


def client_offer_show(user_id, state_args):
    offer_id = {
        "request_id": state_args["request_id"],
        "ars_id": state_args["ars_id"],
    }
    with Session(engine["value"]) as session:
        offer = session.get(Offer, offer_id)
        cost_floor = offer.cost_floor
        cost_ceil = offer.cost_ceil
        description = offer.description
    return {
        "text":
        "Оффер\n\n" + str(cost_floor) +
        ("-" + str(cost_ceil) if cost_ceil is not None else "") + "\n" +
        description,
        "keyboard": [
            [
                {
                    "text": "Заявка",
                    "callback": CLIENT_REQUEST_ID,
                },
            ],
            [
                {
                    "text": "Выбрать",
                    "callback": CLIENT_WIN_ID,
                },
            ],
        ],
    }


def client_offer_callback(user_id, state_args, state_id, handler_arg):
    request_id = state_args["request_id"]
    del state_args["request_id"]
    if state_id == CLIENT_WIN_ID:
        offer_id = {
            "request_id": request_id,
            "ars_id": state_args["ars_id"],
        }
        with Session(engine["value"]) as session:
            session.get(Offer, offer_id).winner = True
            session.commit()
    del state_args["ars_id"]
    state_args["id"] = request_id


CLIENT_WINS_ID = "client_wins"


def client_wins_show(user_id, state_args):
    requests_list = []
    with Session(engine["value"]) as session:
        for request in session.execute(
                select(Auto).where(
                    Auto.user_id == user_id)).scalars().first().requests:
            is_win = False
            for offer in request.offers:
                if offer.winner:
                    is_win = True
                    break
            if is_win:
                requests_list.append({
                    "id": request.id,
                    "spec_title": request.spec.title,
                })
    return {
        "text":
        "Победы",
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
                    "state_id": CLIENT_WIN_ID,
                    "handler_arg": str(request_dict["id"]),
                },
            },
        ] for request_dict in requests_list],
    }


def client_wins_callback(user_id, state_args, state_id, handler_arg):
    if state_id == CLIENT_WIN_ID:
        state_args["id"] = int(handler_arg)


CLIENT_WIN_ID = "client_win"


def client_win_show(user_id, state_args):
    request_id = state_args["id"]
    with Session(engine["value"]) as session:
        request = session.get(Request, request_id)
        spec_title = request.spec.title
        for offer in request.offers:
            if offer.winner:
                cost_floor = offer.cost_floor
                cost_ceil = offer.cost_ceil
                description = offer.description
                ars = offer.ars
                ars_title = ars.title
                ars_description = ars.description
                ars_address = ars.address
                ars_picture = ars.picture
                break
    render_message = {
        "text":
        "Победа\n\n" + spec_title + "\n" + str(cost_floor) +
        ("-" + str(cost_ceil) if cost_ceil is not None else "") + "\n" +
        description + "\n" + ars_title + "\n" + ars_description + "\n" +
        ars_address,
        "keyboard": [
            [
                {
                    "text": "Победы",
                    "callback": CLIENT_WINS_ID,
                },
            ],
        ],
    }
    if ars_picture is not None:
        render_message["photo"] = ars_picture
    return render_message


def client_win_callback(user_id, state_args, state_id, handler_arg):
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
        "Диллер\n\n" + title + "\n" + description + "\n" +
        " ".join(spec_titles_list),
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
            [
                {
                    "text": "Победители",
                    "callback": DILLER_WINNERS_ID,
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
    if len(handler_arg) > ARS_TITLE_LENGTH:
        state_args["status"] = "Слишком длинный"
        return CHANGE_ARS_TITLE_ID
    with Session(engine["value"]) as session:
        session.execute(select(Ars).where(
            Ars.user_id == user_id)).scalars().first().title = handler_arg
        session.commit()
    return DILLER_ID


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
    if len(handler_arg) > DESCRIPTION_LENGTH:
        state_args["status"] = "Слишком длинный"
        return CHANGE_ARS_DESCRIPTION_ID
    with Session(engine["value"]) as session:
        session.execute(select(Ars).where(Ars.user_id == user_id)).scalars(
        ).first().description = handler_arg
        session.commit()
    return DILLER_ID


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
        "Выберите специализацию\n\n" + " ".join(spec_titles_list),
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
    if state_id == DILLER_ID:
        del state_args["spec_ids"]
        with Session(engine["value"]) as session:
            ars = session.execute(
                select(Ars).where(Ars.user_id == user_id)).scalars().first()
            specs = ars.specs
            specs.clear()
            for spec_id in spec_ids_list:
                specs.append(session.get(Spec, spec_id))
            session.commit()
        return
    spec_id = int(handler_arg)
    if spec_id in spec_ids_list:
        spec_ids_list.remove(spec_id)
        return
    spec_ids_list.append(spec_id)


DILLER_REQUESTS_ID = "diller_requests"


def diller_requests_show(user_id, state_args):
    requests_list = []
    with Session(engine["value"]) as session:
        ars = session.execute(
            select(Ars).where(Ars.user_id == user_id)).scalars().first()
        ars_id = ars.id
        spec_ids_list = [spec.id for spec in ars.specs]
        for request in session.query(Request).all():
            spec = request.spec
            if spec.id in spec_ids_list:
                skip = False
                for offer in request.offers:
                    if offer.winner or offer.ars_id == ars_id:
                        skip = True
                        break
                if not skip:
                    requests_list.append({
                        "id": request.id,
                        "spec_title": spec.title,
                    })
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
                    "state_id": DILLER_REQUEST_ID,
                    "handler_arg": str(request_dict["id"]),
                },
            },
        ] for request_dict in requests_list],
    }


def diller_requests_callback(user_id, state_args, state_id, handler_arg):
    if state_id == DILLER_REQUEST_ID:
        state_args["id"] = int(handler_arg)


DILLER_REQUEST_ID = "diller_request"


def diller_request_show(user_id, state_args):
    request_id = state_args["id"]
    with Session(engine["value"]) as session:
        request = session.get(Request, request_id)
        spec_title = request.spec.title
        description = request.description
    return {
        "text":
        "Заявка\n\n" + spec_title + "\n" + description,
        "keyboard": [
            [
                {
                    "text": "Заявки",
                    "callback": DILLER_REQUESTS_ID,
                },
            ],
            [
                {
                    "text": "Создать оффер",
                    "callback": CREATE_OFFER_COST_ID,
                },
            ],
        ],
    }


def diller_request_callback(user_id, state_args, state_id, handler_arg):
    if state_id == CREATE_OFFER_COST_ID:
        state_args["request_id"] = state_args["id"]
    del state_args["id"]


CREATE_OFFER_COST_ID = "create_offer_cost"


def create_offer_cost_show(user_id, state_args):
    return {
        "text": "Введите цену или ценовой диапазон",
        "keyboard": [
            [
                {
                    "text": "Отменить",
                    "callback": DILLER_REQUEST_ID,
                },
            ],
        ],
    }


def create_offer_cost_callback(user_id, state_args, state_id, handler_arg):
    state_args["id"] = state_args["request_id"]
    del state_args["request_id"]


def create_offer_cost_text(user_id, state_args, handler_arg):
    splitted = handler_arg.split("-")
    len_splitted = len(splitted)
    if len_splitted > 2:
        state_args["status"] = "Неверный формат"
        return CREATE_OFFER_COST_ID
    try:
        cost_floor = int(splitted[0])
    except ValueError:
        state_args["status"] = "cost_floor не число"
        return CREATE_OFFER_COST_ID
    if not 0 < cost_floor < 1000000:
        state_args["status"] = "cost_floor выходит за диапазон [1, 999999]"
        return CREATE_OFFER_COST_ID
    cost_ceil = None
    if len_splitted == 2:
        try:
            cost_ceil = int(splitted[1])
        except ValueError:
            state_args["status"] = "cost_ceil не число"
            return CREATE_OFFER_COST_ID
        if not cost_floor < cost_ceil < 1000000:
            state_args[
                "status"] = "cost_ceil выходит за диапазон [cost_floor + 1, 999999]"
            return CREATE_OFFER_COST_ID
    state_args["cost_floor"] = cost_floor
    if cost_ceil is not None:
        state_args["cost_ceil"] = cost_ceil
    return CREATE_OFFER_DESCRIPTION_ID


CREATE_OFFER_DESCRIPTION_ID = "create_offer_description"


def create_offer_description_show(user_id, state_args):
    return {
        "text": "Введите описание",
        "keyboard": [
            [
                {
                    "text": "Отменить",
                    "callback": DILLER_REQUEST_ID,
                },
            ],
        ],
    }


def create_offer_description_callback(user_id, state_args, state_id,
                                      handler_arg):
    del state_args["cost_floor"]
    if "cost_ceil" in state_args:
        del state_args["cost_ceil"]
    state_args["id"] = state_args["request_id"]
    del state_args["request_id"]


def create_offer_description_text(user_id, state_args, handler_arg):
    if len(handler_arg) > DESCRIPTION_LENGTH:
        state_args["status"] = "Слишком длинный"
        return CREATE_OFFER_DESCRIPTION_ID
    cost_floor = state_args["cost_floor"]
    del state_args["cost_floor"]
    cost_ceil = None
    if "cost_ceil" in state_args:
        cost_ceil = state_args["cost_ceil"]
        del state_args["cost_ceil"]
    request_id = state_args["request_id"]
    del state_args["request_id"]
    with Session(engine["value"]) as session:
        session.add(
            Offer(request_id=request_id,
                  ars_id=session.execute(
                      select(Ars).where(
                          Ars.user_id == user_id)).scalars().first().id,
                  cost_floor=cost_floor,
                  cost_ceil=cost_ceil,
                  description=handler_arg))
        session.commit()
    return DILLER_REQUESTS_ID


DILLER_WINNERS_ID = "diller_winners"


def diller_winners_show(user_id, state_args):
    with Session(engine["value"]) as session:
        offers_list = [{
            "request_id": offer.request_id,
            "spec_title": offer.request.spec.title,
        } for offer in session.execute(
            select(Ars).where(Ars.user_id == user_id)).scalars().first().offers
                       if offer.winner]
    return {
        "text":
        "Победители",
        "keyboard": [
            [
                {
                    "text": "Кабинет",
                    "callback": DILLER_ID,
                },
            ],
        ] + [[
            {
                "text": offer_dict["spec_title"],
                "callback": {
                    "state_id": DILLER_WINNER_ID,
                    "handler_arg": str(offer_dict["request_id"]),
                },
            },
        ] for offer_dict in offers_list],
    }


def diller_winners_callback(user_id, state_args, state_id, handler_arg):
    if state_id == DILLER_WINNER_ID:
        state_args["request_id"] = int(handler_arg)


DILLER_WINNER_ID = "diller_winner"


def diller_winner_show(user_id, state_args):
    request_id = state_args["request_id"]
    with Session(engine["value"]) as session:
        offer = session.get(
            Offer, {
                "request_id":
                request_id,
                "ars_id":
                session.execute(select(Ars).where(
                    Ars.user_id == user_id)).scalars().first().id,
            })
        cost_floor = offer.cost_floor
        cost_ceil = offer.cost_ceil
        description = offer.description
        request = offer.request
        spec_title = request.spec.title
        auto = request.auto
        auto_year = auto.year
        auto_fuel = auto.fuel
    return {
        "text":
        "Победитель\n\n" + str(cost_floor) +
        ("-" + str(cost_ceil) if cost_ceil is not None else "") + "\n" +
        description + "\n" + spec_title + "\n" + auto_year + "\n" +
        FUEL_TEXT_MAP[auto_fuel],
        "keyboard": [
            [
                {
                    "text": "Победители",
                    "callback": DILLER_WINNERS_ID,
                },
            ],
        ],
    }


def diller_winner_callback(user_id, state_args, state_id, handler_arg):
    del state_args["request_id"]
