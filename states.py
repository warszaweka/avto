engine = None


def set_engine(new_engine):
    global engine
    engine = new_engine


main_id = "main"


def main_callback_handler(user_id, state_args, new_state_id, new_state_args):
    if (
        new_state_id not in [ars_id, auction_id, diller_id, client_id]
        or new_state_args
    ):
        raise Exception()


def main_show(user_id, new_state_args):
    return {
        "text": "Главное меню",
        "keyboard": [
            [
                {
                    "text": "СТО",
                    "callback": {"state_id": ars_id, "state_args": {}},
                }
            ],
            [
                {
                    "text": "Аукцион заявок",
                    "callback": {"state_id": auction_id, "state_args": {}},
                }
            ],
            [
                {
                    "text": "Кабинет диллера",
                    "callback": {"state_id": diller_id, "state_args": {}},
                }
            ],
            [
                {
                    "text": "Кабинет клиента",
                    "callback": {"state_id": client_id, "state_args": {}},
                }
            ],
        ],
    }


ars_id = "ars"


def ars_callback_handler(user_id, state_args, new_state_id, new_state_args):
    if new_state_id != main_id or new_state_args:
        raise Exception()


def ars_show(user_id, new_state_args):
    return {
        "text": "СТО",
        "keyboard": [
            [
                {
                    "text": "Главное меню",
                    "callback": {"state_id": main_id, "state_args": {}},
                }
            ]
        ],
    }


auction_id = "auction"


def auction_callback_handler(
    user_id, state_args, new_state_id, new_state_args
):
    if new_state_id != main_id or new_state_args:
        raise Exception()


def auction_show(user_id, new_state_args):
    return {
        "text": "Аукцион заявок",
        "keyboard": [
            [
                {
                    "text": "Главное меню",
                    "callback": {"state_id": main_id, "state_args": {}},
                }
            ]
        ],
    }


diller_id = "diller"


def diller_callback_handler(user_id, state_args, new_state_id, new_state_args):
    if new_state_id != main_id or new_state_args:
        raise Exception()


def diller_show(user_id, new_state_args):
    return {
        "text": "Кабинет диллера",
        "keyboard": [
            [
                {
                    "text": "Главное меню",
                    "callback": {"state_id": main_id, "state_args": {}},
                }
            ]
        ],
    }


client_id = "client"


def client_callback_handler(user_id, state_args, new_state_id, new_state_args):
    if new_state_id != main_id or new_state_args:
        raise Exception()


def client_show(user_id, new_state_args):
    return {
        "text": "Кабинет клиента",
        "keyboard": [
            [
                {
                    "text": "Главное меню",
                    "callback": {"state_id": main_id, "state_args": {}},
                }
            ]
        ],
    }


message_handlers = {}
callback_handlers = {
    main_id: main_callback_handler,
    ars_id: ars_callback_handler,
    auction_id: auction_callback_handler,
    diller_id: diller_callback_handler,
    client_id: client_callback_handler,
}
shows = {
    main_id: main_show,
    ars_id: ars_show,
    auction_id: auction_show,
    diller_id: diller_show,
    client_id: client_show,
}
