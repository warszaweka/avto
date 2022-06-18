from datetime import date, datetime, time, timedelta
from decimal import Decimal, InvalidOperation
from math import ceil

from fuzzywuzzy import process
from geopy.distance import distance
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import (ARS_TITLE_LENGTH, DESCRIPTION_LENGTH, FUEL_TEXT_MAP, Auto,
                     Occupation, Offer, Registration, Request, Spec, User,
                     Vendor)

engine = {
    "value": None,
}

START_ID = "start"


def start_show(user_id, state_args):
    return {
        "text": "Старт",
        "contact": {
            "text": "Номер",
            "button": "📱 Номер",
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
    return DILLER_ID if is_diller else CHANGE_GEO_ID


CLIENT_ID = "client"


def client_show(user_id, state_args):
    vendor_title = None
    with Session(engine["value"]) as session:
        auto = session.get(User, user_id).auto
        if auto is not None:
            vendor_title = auto.vendor.title
            year = auto.year
            fuel = auto.fuel
            volume = auto.volume
    render_button_change_geo = {
        "text": "📍 Оновити геолокацію",
        "callback": CHANGE_GEO_ID,
    }
    render_button_change_auto_vendor = {
        "text": "🚗 Змінити авто",
        "callback": CHANGE_AUTO_VENDOR_ID,
    }
    render_button_support = {
        "text": "📞 Підтримка",
        "url": "tg://user?id=547862853",
    }
    return {
        "text":
        "Головне меню навігації Автопілота.\nВведення нових заявок та контро" +
        "ль вже поданих відбувається звідси." +
        (f"\nВаше авто:\n{vendor_title}, {str(volume)} л., {str(year)} г., " +
         FUEL_TEXT_MAP[fuel] if vendor_title is not None else ""),
        "keyboard": [
            [
                render_button_change_geo,
                render_button_change_auto_vendor,
            ],
            [
                {
                    "text": "📝 Нова заявка",
                    "callback": CREATE_REQUEST_SPEC_ID,
                },
                {
                    "text": "📄 Заявки у роботі",
                    "callback": CLIENT_REQUESTS_ID,
                },
            ],
            [
                {
                    "text": "📒 Акцепти",
                    "callback": CLIENT_WINS_ID,
                },
                render_button_support,
            ],
        ] if vendor_title is not None else [
            [
                render_button_change_geo,
                render_button_change_auto_vendor,
            ],
            [
                render_button_support,
            ],
        ],
    }


CHANGE_GEO_ID = "change_geo"


def change_geo_show(user_id, state_args):
    return {
        "text":
        "Геопозиція",
        "keyboard": [
            [
                {
                    "text": "❌ Відмінити",
                    "callback": CLIENT_ID,
                },
            ],
        ],
        "geo": {
            "text": "Геопозиція",
            "button": "📍 Геопозиція",
        },
    }


def change_geo_geo(user_id, state_args, handler_arg):
    with Session(engine["value"]) as session:
        auto = session.get(User, user_id).auto
        auto.latitude = handler_arg["latitude"]
        auto.longitude = handler_arg["longitude"]
        session.commit()
    return CLIENT_ID


CHANGE_AUTO_VENDOR_ID = "change_auto_vendor"


def change_auto_vendor_show(user_id, state_args):
    search = None
    if "search" in state_args:
        search = state_args["search"]
    with Session(engine["value"]) as session:
        if search is not None:
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
            } for title in [
                "Volkswagen",
                "Renault",
                "Skoda",
                "Toyota",
                "Ford",
                "Opel",
                "Hyundai",
                "Mersedes-Benz",
                "Daewoo",
            ]]
    if search is not None:
        vendors_list = [{
            "id": search_result[2],
            "title": search_result[0],
        } for search_result in process.extract(search, vendors_dict, limit=9)]
    return {
        "text":
        "Введення нових заявок та контроль вже поданих відбувається звідси.",
        "photo":
        "AgACAgIAAxkBAAMDYhD08GYEgB-QOQABOg0i_4jZHdh2AAI7uzEbppeJSBpyNfdzkIR" +
        "jAQADAgADbQADIwQ",
        "keyboard": [
            [
                {
                    "text": "❌ Відмінити",
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
    for i in range(6):
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
        "Виберіть рік випуску Вашого авто або введіть вручну",
        "photo":
        "AgACAgIAAxkBAAMEYhD1RR5D2zDHR3xjrWAguMcr1AcAAjy7MRuml4lI7rxRFjBqx10" +
        "BAAMCAANzAAMjBA",
        "keyboard": [
            [
                {
                    "text": "❌ Відмінити",
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
        state_args["_status"] = "Не число"
        return CHANGE_AUTO_YEAR_ID
    today_year = date.today().year
    if handler_arg < 1900 or handler_arg > today_year:
        state_args["_status"] = "Виходить за діапазон [1900, " +\
            f"{str(today_year)}]"
        return CHANGE_AUTO_YEAR_ID
    state_args["year"] = str(handler_arg)
    return CHANGE_AUTO_FUEL_ID


CHANGE_AUTO_FUEL_ID = "change_auto_fuel"


def change_auto_fuel_show(user_id, state_args):
    return {
        "text":
        "Виберіть вид палива авто",
        "photo":
        "AgACAgIAAxkBAAMFYhD1p7zzfwlP9qg2jtpAJv5ppzoAAj27MRuml4lIfyniNP4sfnM" +
        "BAAMCAANtAAMjBA",
        "keyboard": [
            [
                {
                    "text": "❌ Відмінити",
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
        "Введіть обсяг двигуна Вашого авто у літрах через точку. Приклад:" +
        " 1.2",
        "photo":
        "AgACAgIAAxkBAAMGYhD16IV61M6ZYIXzexMhDGFOeCAAAj67MRuml4lIA9oJSWsxvSk" +
        "BAAMCAANzAAMjBA",
        "keyboard": [
            [
                {
                    "text": "❌ Відмінити",
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
        state_args["_status"] = "Не число"
        return CHANGE_AUTO_VOLUME_ID
    if handler_arg < 0 or handler_arg > 10:
        state_args["_status"] = "Виходить за діапазон [0, 10]"
        return CHANGE_AUTO_VOLUME_ID
    fuel = state_args["fuel"]
    del state_args["fuel"]
    year = state_args["year"]
    del state_args["year"]
    vendor_id = state_args["vendor_id"]
    del state_args["vendor_id"]
    with Session(engine["value"]) as session:
        auto = session.get(User, user_id).auto
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
        "Вкажіть, які послуги СТО вам необхідні та рухаємося далі. Якщо є су" +
        "мніви, у наступному вікні ви зможете описати технічну проблему.",
        "keyboard": [
            [
                {
                    "text": "❌ Відмінити",
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
        "text":
        "Якщо ви хочете додати опис або коментар до ремонту, це можна зробит" +
        "и зараз. Це необов'язкове для заповнення поле, але будь-яка додатко" +
        "ва інформація допоможе нашим фахівцям у вирішенні проблеми.",
        "keyboard": [
            [
                {
                    "text": "❌ Відмінити",
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
        state_args["_status"] = "Занадто довгий"
        return CREATE_REQUEST_DESCRIPTION_ID
    spec_id = state_args["spec_id"]
    del state_args["spec_id"]
    with Session(engine["value"]) as session:
        request = Request(spec_id=spec_id,
                          description=handler_arg,
                          auto_id=session.get(User, user_id).auto.id)
        session.add(request)
        session.commit()
        request_id = request.id
    state_args["id"] = request_id
    return CLIENT_REQUEST_ID


CLIENT_REQUESTS_ID = "client_requests"


def client_requests_show(user_id, state_args):
    with Session(engine["value"]) as session:
        requests_list = [{
            "id": request.id,
            "spec_title": request.spec.title,
        } for request in session.get(User, user_id).auto.requests
            if request.active]
    return {
        "text":
        "Заявки на розгляд. Все просто.\nПо кожній заявці Ви отримаєте кільк" +
        "а пропозицій від СТО. Всі пропозиції дійсні 15 хвилин, тому бажано " +
        "вкластися з вибором у цей проміжок часу.\nНайкраща з пропозицій Ви " +
        "акцептуєте та у запропонований час прямуєте на СТО для ремонту.\nДе" +
        "тально ви можете бачити статус та перейти до конкретної заявки для " +
        "її підтвердження.",
        "keyboard": [
            [
                {
                    "text": "🔙 Назад",
                    "callback": CLIENT_ID,
                },
            ],
        ] + [[
            {
                "text": f"{i + 1}. " + request_dict["spec_title"],
                "callback": {
                    "state_id": CLIENT_REQUEST_ID,
                    "handler_arg": str(request_dict["id"]),
                },
            },
        ] for i, request_dict in enumerate(requests_list)],
    }


def client_requests_callback(user_id, state_args, state_id, handler_arg):
    if state_id == CLIENT_REQUEST_ID:
        state_args["id"] = int(handler_arg)


CLIENT_REQUEST_ID = "client_request"


def client_request_show(user_id, state_args):
    request_id = state_args["id"]
    offers_list = []
    with Session(engine["value"]) as session:
        request = session.get(Request, request_id)
        description = request.description
        spec_title = request.spec.title
        for offer in request.offers:
            ars = offer.ars
            ars_id = ars.id
            offers_list.append(
                {
                    "ars_id": ars_id,
                    "cost_floor": offer.cost_floor,
                    "cost_ceil": offer.cost_ceil,
                    "latitude": ars.latitude,
                    "longitude": ars.longitude,
                    "time": session.execute(
                        select(Occupation)
                        .where(Occupation.ars_id == ars_id)
                        .where(Occupation.request_id == request_id)
                    ).scalars().first().time,
                }
            )
        auto = request.auto
        vendor_title = auto.vendor.title
        year = auto.year
        fuel = auto.fuel
        volume = auto.volume
        latitude = auto.latitude
        longitude = auto.longitude
    render_offers = []
    for index, offer_dict in enumerate(offers_list):
        cost_ceil = offer_dict["cost_ceil"]
        render_offers.append([
            {
                "text":
                f"{index + 1}. " +
                str(offer_dict["cost_floor"]) +
                (f"-{str(cost_ceil)}" if cost_ceil is not None else "") +
                f" грн. {offer_dict['time'].strftime('%d-%m %H:00')}." +
                (" " + str(
                    ceil(
                        distance((latitude, longitude),
                                 (float(offer_dict["latitude"]),
                                  float(offer_dict["longitude"]))).km)) +
                 " км" if latitude is not None else ""),
                "callback": {
                    "state_id": CLIENT_OFFER_ID,
                    "handler_arg": str(offer_dict["ars_id"]),
                },
            },
        ])
    return {
        "text":
        f"Ваше авто: {vendor_title}, {str(year)}, {str(volume)}, " +
        f"{FUEL_TEXT_MAP[fuel]}.\nНадіслано заявку на наступні послуги ремон" +
        f"ту: {spec_title}.\nКоментар: {description}.",
        "keyboard": [
            [
                {
                    "text": "🔙 Назад",
                    "callback": CLIENT_REQUESTS_ID,
                },
                {
                    "text": "🗑 Видалити заявку",
                    "callback": {
                        "state_id": CLIENT_REQUESTS_ID,
                        "handler_arg": "delete",
                    },
                },
            ],
        ] + render_offers,
    }


def client_request_callback(user_id, state_args, state_id, handler_arg):
    request_id = state_args["id"]
    del state_args["id"]
    if state_id == CLIENT_OFFER_ID:
        state_args["request_id"] = request_id
        state_args["ars_id"] = int(handler_arg)
    elif handler_arg == "delete":
        with Session(engine["value"]) as session:
            session.get(Request, request_id).active = False
            session.commit()


CLIENT_OFFER_ID = "client_offer"


def client_offer_show(user_id, state_args):
    request_id = state_args["request_id"]
    offer_id = {
        "request_id": request_id,
        "ars_id": state_args["ars_id"],
    }
    with Session(engine["value"]) as session:
        offer = session.get(Offer, offer_id)
        cost_floor = offer.cost_floor
        cost_ceil = offer.cost_ceil
        description = offer.description
        occupation_time = session.execute(
            select(Occupation)
            .where(Occupation.ars_id == offer.ars_id)
            .where(Occupation.request_id == request_id)
        ).scalars().first().time
    return {
        "text":
        f"Пропозиція від СТО:\nПриблизна вартість робіт {str(cost_floor)}" +
        (f"-{str(cost_ceil)}" if cost_ceil is not None else "") +
        f" грн.\nЗапланований час візиту - " +
        occupation_time.strftime("%d-%m %H:00") +
        f"\nКоментар: {description}",
        "keyboard": [
            [
                {
                    "text": "🔙 Назад",
                    "callback": CLIENT_REQUEST_ID,
                },
                {
                    "text": "✓ Обрати",
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
            offer = session.get(Offer, offer_id)
            offer.request.active = False
            offer.winner = True
            session.commit()
    del state_args["ars_id"]
    state_args["id"] = request_id


CLIENT_WINS_ID = "client_wins"


def client_wins_show(user_id, state_args):
    requests_list = []
    with Session(engine["value"]) as session:
        for request in session.get(User, user_id).auto.requests:
            if request.active:
                continue
            for offer in request.offers:
                if offer.winner:
                    break
            else:
                continue
            requests_list.append({
                "id": request.id,
                "spec_title": request.spec.title,
            })
    return {
        "text":
        "Акцепти",
        "keyboard": [
            [
                {
                    "text": "🔙 Назад",
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
                phone = ars.user.phone
                title = ars.title
                latitude = ars.latitude
                longitude = ars.longitude
                ars_description = ars.description
                address = ars.address
                picture = ars.picture
                occupation_time = session.execute(
                    select(Occupation)
                    .where(Occupation.ars_id == ars.id)
                    .where(Occupation.request_id == request_id)
                ).scalars().first().time
                break
    render_message = {
        "text":
        f"Ви прийняли пропозицію від {title}.\n{ars_description}" +
        f"\nМи чекаємо вас {occupation_time.strftime('%d-%m о %H:00')}" +
        f" за адресою:\n{address}\nТел. {phone}" +
        f"\nПриблизна вартість робіт складе {str(cost_floor)}" +
        (f"-{str(cost_ceil)}" if cost_ceil is not None else "") +
        f"\nКоментар: {description}",
        "keyboard": [
            [
                {
                    "text": "🔙 Назад",
                    "callback": CLIENT_WINS_ID,
                },
            ],
            [
                {
                    "text": "📍 Місцезнаходження",
                    "url": "https://www.google.com/maps/place/" +
                    f"{latitude},{longitude}",
                },
            ],
        ],
    }
    if picture is not None:
        render_message["photo"] = picture
    return render_message


def client_win_callback(user_id, state_args, state_id, handler_arg):
    del state_args["id"]


DILLER_ID = "diller"


def diller_show(user_id, state_args):
    with Session(engine["value"]) as session:
        ars = session.get(User, user_id).ars
        title = ars.title
        description = ars.description
        picture = ars.picture
        spec_titles_list = [spec.title for spec in ars.specs]
    render_message = {
        "text":
        f"Дилер\n\n{title}\n{description}\n" + " ".join(spec_titles_list),
        "keyboard": [
            [
                {
                    "text": "✍ Змінити назву",
                    "callback": CHANGE_ARS_TITLE_ID,
                },
                {
                    "text": "✍ Змінити опис",
                    "callback": CHANGE_ARS_DESCRIPTION_ID,
                },
            ],
            [
                {
                    "text": "✍ Змінити зображення",
                    "callback": CHANGE_ARS_PICTURE_ID,
                },
                {
                    "text": "✍ Змінити спеціалізацію",
                    "callback": CHANGE_ARS_SPECS_ID,
                },
            ],
            [
                {
                    "text": "📄 Заявки",
                    "callback": DILLER_REQUESTS_ID,
                },
                {
                    "text": "📒 Акцепти",
                    "callback": DILLER_WINNERS_ID,
                },
            ],
            [
                {
                    "text": "📅 Планувальник",
                    "callback": OCCUPATIONS_DATE_ID,
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
                spec.id for spec in session.get(User, user_id).ars.specs
            ]
        state_args["spec_ids"] = spec_ids_list


CHANGE_ARS_TITLE_ID = "change_ars_title"


def change_ars_title_show(user_id, state_args):
    return {
        "text": "Введіть назву",
        "keyboard": [
            [
                {
                    "text": "❌ Відмінити",
                    "callback": DILLER_ID,
                },
            ],
        ],
    }


def change_ars_title_text(user_id, state_args, handler_arg):
    if len(handler_arg) > ARS_TITLE_LENGTH:
        state_args["_status"] = "Занадто довгий"
        return CHANGE_ARS_TITLE_ID
    with Session(engine["value"]) as session:
        session.get(User, user_id).ars.title = handler_arg
        session.commit()
    return DILLER_ID


CHANGE_ARS_DESCRIPTION_ID = "change_ars_description"


def change_ars_description_show(user_id, state_args):
    return {
        "text": "Введіть опис",
        "keyboard": [
            [
                {
                    "text": "❌ Відмінити",
                    "callback": DILLER_ID,
                },
            ],
        ],
    }


def change_ars_description_text(user_id, state_args, handler_arg):
    if len(handler_arg) > DESCRIPTION_LENGTH:
        state_args["_status"] = "Занадто довгий"
        return CHANGE_ARS_DESCRIPTION_ID
    with Session(engine["value"]) as session:
        session.get(User, user_id).ars.description = handler_arg
        session.commit()
    return DILLER_ID


CHANGE_ARS_PICTURE_ID = "change_ars_picture"


def change_ars_picture_show(user_id, state_args):
    return {
        "text": "Надішліть фотографію",
        "keyboard": [
            [
                {
                    "text": "❌ Відмінити",
                    "callback": DILLER_ID,
                },
            ],
        ],
    }


def change_ars_picture_photo(user_id, state_args, handler_arg):
    with Session(engine["value"]) as session:
        session.get(User, user_id).ars.picture = handler_arg
        session.commit()
    return DILLER_ID


CHANGE_ARS_SPECS_ID = "change_ars_specs"


def change_ars_specs_show(user_id, state_args):
    spec_ids_list = state_args["spec_ids"]
    specs_list = []
    spec_titles_list = []
    with Session(engine["value"]) as session:
        for spec in session.query(Spec).all():
            spec_id = spec.id
            spec_title = spec.title
            specs_list.append({
                "id": spec_id,
                "title": spec_title,
            })
            if spec_id in spec_ids_list:
                spec_titles_list.append(spec_title)
    return {
        "text":
        "Виберіть спеціалізацію\n\n" + " ".join(spec_titles_list),
        "keyboard": [
            [
                {
                    "text": "🔙 Назад",
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
            ars = session.get(User, user_id).ars
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
        ars = session.get(User, user_id).ars
        ars_id = ars.id
        spec_ids_list = [spec.id for spec in ars.specs]
        for request in session.query(Request).all():
            if not request.active:
                continue
            if request.spec_id not in spec_ids_list:
                continue
            for offer in request.offers:
                if offer.ars_id == ars_id:
                    break
            else:
                requests_list.append({
                    "id": request.id,
                    "spec_title": request.spec.title,
                })
    return {
        "text":
        "Заявки",
        "keyboard": [
            [
                {
                    "text": "🔙 Назад",
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
        auto = request.auto
        vendor_title = auto.vendor.title
        year = auto.year
        fuel = auto.fuel
        volume = auto.volume
    return {
        "text":
        f"Заявка\n\n{spec_title}\n{description}" +
        f"\n{vendor_title}, {str(volume)} л., {str(year)} г., " +
        FUEL_TEXT_MAP[fuel],
        "keyboard": [
            [
                {
                    "text": "🔙 Назад",
                    "callback": DILLER_REQUESTS_ID,
                },
                {
                    "text": "📝 Створити оффер",
                    "callback": CREATE_OFFER_OCCUPATION_DATE_ID,
                },
            ],
        ],
    }


def diller_request_callback(user_id, state_args, state_id, handler_arg):
    if state_id == CREATE_OFFER_OCCUPATION_DATE_ID:
        state_args["request_id"] = state_args["id"]
    del state_args["id"]


CREATE_OFFER_OCCUPATION_DATE_ID = "create_offer_occupation_date"


def create_offer_occupation_date_show(user_id, state_args):
    request_id = state_args["request_id"]
    with Session(engine["value"]) as session:
        request = session.get(Request, request_id)
        auto = request.auto
        vendor_title = auto.vendor.title
        year = auto.year
        fuel = auto.fuel
        volume = auto.volume
    today_date = date.today()
    render_dates = []
    for i in range(7):
        str_date = (today_date + timedelta(days=i)).isoformat()
        render_dates.append([
            {
                "text": str_date,
                "callback": {
                    "state_id": CREATE_OFFER_OCCUPATION_TIME_ID,
                    "handler_arg": str_date,
                },
            },
        ])
    return {
        "text":
        "Запропонувати дату та час ремонтних робіт" +
        f"\n{vendor_title}, {str(volume)} л., {str(year)} г., " +
        FUEL_TEXT_MAP[fuel],
        "keyboard": [
            [
                {
                    "text": "❌ Відмінити",
                    "callback": DILLER_REQUEST_ID,
                },
            ],
        ] + render_dates,
    }


def create_offer_occupation_date_callback(
    user_id,
    state_args,
    state_id,
    handler_arg,
):
    if state_id == DILLER_REQUEST_ID:
        state_args["id"] = state_args["request_id"]
        del state_args["request_id"]
        return
    state_args["date"] = handler_arg


CREATE_OFFER_OCCUPATION_TIME_ID = "create_offer_occupation_time"


def create_offer_occupation_time_show(user_id, state_args):
    request_id = state_args["request_id"]
    current_date = date.fromisoformat(state_args["date"])
    occupation_time_times_list_wo_request = []
    occupation_time_times_list_wo_winner = []
    occupation_time_times_list_winner = []
    with Session(engine["value"]) as session:
        request = session.get(Request, request_id)
        auto = request.auto
        vendor_title = auto.vendor.title
        year = auto.year
        fuel = auto.fuel
        volume = auto.volume
        ars = session.get(User, user_id).ars
        ars_id = ars.id
        for occupation in ars.occupations:
            occupation_time = occupation.time
            if occupation_time.date() == current_date:
                occupation_time_time = occupation_time.time()
                request = occupation.request
                if request is not None:
                    for offer in request.offers:
                        if offer.winner:
                            if offer.ars_id == ars_id:
                                occupation_time_times_list_winner.append(
                                    occupation_time_time
                                )
                            break
                    else:
                        occupation_time_times_list_wo_winner.append(
                            occupation_time_time
                        )
                else:
                    occupation_time_times_list_wo_request.append(
                        occupation_time_time
                    )

    render_times = []
    for i in range(4):
        render_times_row = []
        for j in range(3):
            current_time = time(9 + i + j * 4)
            str_time = current_time.isoformat()
            vacant = False
            if current_time in occupation_time_times_list_wo_request:
                mark = "⭕ "
            elif current_time in occupation_time_times_list_wo_winner:
                mark = "⏳ "
            elif current_time in occupation_time_times_list_winner:
                mark = "✅ "
            else:
                mark = ""
                vacant = True
            render_times_row.append({
                "text": f"{mark}{str_time}",
                "callback": {
                    "state_id": (
                        CREATE_OFFER_COST_ID
                        if vacant
                        else CREATE_OFFER_OCCUPATION_TIME_ID
                    ),
                    "handler_arg": str_time,
                },
            })
        render_times.append(render_times_row)
    return {
        "text":
        "Запропонувати дату та час ремонтних робіт" +
        f"\n{vendor_title}, {str(volume)} л., {str(year)} г., " +
        FUEL_TEXT_MAP[fuel],
        "keyboard": [
            [
                {
                    "text": "❌ Відмінити",
                    "callback": DILLER_REQUEST_ID,
                },
            ],
        ] + render_times,
    }


def create_offer_occupation_time_callback(
    user_id,
    state_args,
    state_id,
    handler_arg,
):
    if state_id == DILLER_REQUEST_ID:
        state_args["id"] = state_args["request_id"]
        del state_args["request_id"]
        del state_args["date"]
    elif state_id == CREATE_OFFER_COST_ID:
        state_args["time"] = handler_arg


CREATE_OFFER_COST_ID = "create_offer_cost"


def create_offer_cost_show(user_id, state_args):
    request_id = state_args["request_id"]
    with Session(engine["value"]) as session:
        request = session.get(Request, request_id)
        auto = request.auto
        vendor_title = auto.vendor.title
        year = auto.year
        fuel = auto.fuel
        volume = auto.volume
    return {
        "text":
        "Введіть ціну або ціновий діапазон" +
        f"\n{vendor_title}, {str(volume)} л., {str(year)} г., " +
        FUEL_TEXT_MAP[fuel],
        "keyboard": [
            [
                {
                    "text": "❌ Відмінити",
                    "callback": DILLER_REQUEST_ID,
                },
            ],
        ],
    }


def create_offer_cost_callback(user_id, state_args, state_id, handler_arg):
    state_args["id"] = state_args["request_id"]
    del state_args["request_id"]
    del state_args["date"]
    del state_args["time"]


def create_offer_cost_text(user_id, state_args, handler_arg):
    splitted = handler_arg.split("-")
    len_splitted = len(splitted)
    if len_splitted > 2:
        state_args["_status"] = "Невірний формат"
        return CREATE_OFFER_COST_ID
    try:
        cost_floor = int(splitted[0])
    except ValueError:
        state_args["_status"] = "cost_floor не число"
        return CREATE_OFFER_COST_ID
    if not 0 < cost_floor < 1000000:
        state_args["_status"] = "cost_floor виходить за діапазон [1, 999999]"
        return CREATE_OFFER_COST_ID
    cost_ceil = None
    if len_splitted == 2:
        try:
            cost_ceil = int(splitted[1])
        except ValueError:
            state_args["_status"] = "cost_ceil не число"
            return CREATE_OFFER_COST_ID
        if not cost_floor < cost_ceil < 1000000:
            state_args["_status"] = "cost_ceil виходить за діапазон [cost_f" +\
                "loor + 1, 999999]"
            return CREATE_OFFER_COST_ID
    state_args["cost_floor"] = cost_floor
    if cost_ceil is not None:
        state_args["cost_ceil"] = cost_ceil
    return CREATE_OFFER_DESCRIPTION_ID


CREATE_OFFER_DESCRIPTION_ID = "create_offer_description"


def create_offer_description_show(user_id, state_args):
    request_id = state_args["request_id"]
    with Session(engine["value"]) as session:
        request = session.get(Request, request_id)
        auto = request.auto
        vendor_title = auto.vendor.title
        year = auto.year
        fuel = auto.fuel
        volume = auto.volume
    return {
        "text":
        "Введіть опис" +
        f"\n{vendor_title}, {str(volume)} л., {str(year)} г., " +
        FUEL_TEXT_MAP[fuel],
        "keyboard": [
            [
                {
                    "text": "❌ Відмінити",
                    "callback": DILLER_REQUEST_ID,
                },
            ],
        ],
    }


def create_offer_description_callback(user_id, state_args, state_id,
                                      handler_arg):
    del state_args["date"]
    del state_args["time"]
    del state_args["cost_floor"]
    if "cost_ceil" in state_args:
        del state_args["cost_ceil"]
    state_args["id"] = state_args["request_id"]
    del state_args["request_id"]


def create_offer_description_text(user_id, state_args, handler_arg):
    if len(handler_arg) > DESCRIPTION_LENGTH:
        state_args["_status"] = "Занадто довгий"
        return CREATE_OFFER_DESCRIPTION_ID
    cost_floor = state_args["cost_floor"]
    del state_args["cost_floor"]
    cost_ceil = None
    if "cost_ceil" in state_args:
        cost_ceil = state_args["cost_ceil"]
        del state_args["cost_ceil"]
    request_id = state_args["request_id"]
    del state_args["request_id"]
    current_datetime = datetime.combine(date.fromisoformat(state_args["date"]),
                                        time.fromisoformat(state_args["time"]))
    del state_args["date"]
    del state_args["time"]
    with Session(engine["value"]) as session:
        ars_id = session.get(User, user_id).ars.id
        session.add(Occupation(
            time=current_datetime,
            ars_id=ars_id,
            request_id=request_id,
        ))
        session.add(
            Offer(request_id=request_id,
                  ars_id=ars_id,
                  cost_floor=cost_floor,
                  cost_ceil=cost_ceil,
                  description=handler_arg))
        session.commit()
    state_args["_status"] = "Ваша пропозиція відправлена клієнту. Очікуйте " +\
        "на підтвердження"
    return DILLER_REQUESTS_ID


DILLER_WINNERS_ID = "diller_winners"


def diller_winners_show(user_id, state_args):
    with Session(engine["value"]) as session:
        offers_list = [{
            "request_id": offer.request_id,
            "spec_title": offer.request.spec.title,
        } for offer in session.get(User, user_id).ars.offers if offer.winner]
    return {
        "text":
        "Акцепти",
        "keyboard": [
            [
                {
                    "text": "🔙 Назад",
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
                "request_id": request_id,
                "ars_id": session.get(User, user_id).ars.id,
            })
        cost_floor = offer.cost_floor
        cost_ceil = offer.cost_ceil
        description = offer.description
        request = offer.request
        spec_title = request.spec.title
        auto = request.auto
        year = auto.year
        fuel = auto.fuel
    return {
        "text":
        f"Акцепт\n\n{str(cost_floor)}" +
        (f"-{str(cost_ceil)}" if cost_ceil is not None else "") +
        f"\n{description}\n{spec_title}\n{year}\n{FUEL_TEXT_MAP[fuel]}",
        "keyboard": [
            [
                {
                    "text": "🔙 Назад",
                    "callback": DILLER_WINNERS_ID,
                },
            ],
        ],
    }


def diller_winner_callback(user_id, state_args, state_id, handler_arg):
    del state_args["request_id"]


OCCUPATIONS_DATE_ID = "occupations_date"


def occupations_date_show(user_id, state_args):
    today_date = date.today()
    render_dates = []
    for i in range(7):
        str_date = (today_date + timedelta(days=i)).isoformat()
        render_dates.append([
            {
                "text": str_date,
                "callback": {
                    "state_id": OCCUPATIONS_TIME_ID,
                    "handler_arg": str_date,
                },
            },
        ])
    return {
        "text":
        "Запланувати дату та час ремонтних робіт",
        "keyboard": [
            [
                {
                    "text": "🔙 Назад",
                    "callback": DILLER_ID,
                },
            ],
        ] + render_dates,
    }


def occupations_date_callback(user_id, state_args, state_id, handler_arg):
    if state_id == OCCUPATIONS_TIME_ID:
        state_args["date"] = handler_arg


OCCUPATIONS_TIME_ID = "occupations_time"


def occupations_time_show(user_id, state_args):
    current_date = date.fromisoformat(state_args["date"])
    occupation_time_times_list_wo_request = []
    occupation_time_times_list_wo_winner = []
    occupation_time_times_list_winner = []
    with Session(engine["value"]) as session:
        ars = session.get(User, user_id).ars
        ars_id = ars.id
        for occupation in ars.occupations:
            occupation_time = occupation.time
            if occupation_time.date() == current_date:
                occupation_time_time = occupation_time.time()
                request = occupation.request
                if request is not None:
                    for offer in request.offers:
                        if offer.winner:
                            if offer.ars_id == ars_id:
                                occupation_time_times_list_winner.append(
                                    occupation_time_time
                                )
                            break
                    else:
                        occupation_time_times_list_wo_winner.append(
                            occupation_time_time
                        )
                else:
                    occupation_time_times_list_wo_request.append(
                        occupation_time_time
                    )

    render_times = []
    for i in range(4):
        render_times_row = []
        for j in range(3):
            current_time = time(9 + i + j * 4)
            str_time = current_time.isoformat()
            if current_time in occupation_time_times_list_wo_request:
                mark = "⭕ "
            elif current_time in occupation_time_times_list_wo_winner:
                mark = "⏳ "
            elif current_time in occupation_time_times_list_winner:
                mark = "✅ "
            else:
                mark = ""
            render_times_row.append({
                "text": f"{mark}{str_time}",
                "callback": {
                    "state_id": OCCUPATIONS_TIME_ID,
                    "handler_arg": str_time,
                },
            })
        render_times.append(render_times_row)
    return {
        "text":
        "Запланувати дату та час ремонтних робіт",
        "keyboard": [
            [
                {
                    "text": "🔙 Назад",
                    "callback": OCCUPATIONS_DATE_ID,
                },
            ],
        ] + render_times,
    }


def occupations_time_callback(user_id, state_args, state_id, handler_arg):
    if state_id == OCCUPATIONS_DATE_ID:
        del state_args["date"]
        return
    current_datetime = datetime.combine(date.fromisoformat(state_args["date"]),
                                        time.fromisoformat(handler_arg))
    with Session(engine["value"]) as session:
        ars = session.get(User, user_id).ars
        for occupation in ars.occupations:
            if occupation.time == current_datetime:
                if occupation.request is None:
                    session.delete(occupation)
                break
        else:
            session.add(Occupation(time=current_datetime, ars_id=ars.id))
        session.commit()
