from typing import Optional

from sqlalchemy.orm import Session

import main
from models import Article

create_article_input_id = "create_article_input"


def create_article_input_handler(update: dict) -> tuple:
    if update["type"] == "message":
        return (create_article_confirm_id, update["handler_args"])
    return (news_id, None)


def create_article_input_show(update: dict) -> list:
    return [
        {
            "text": "Введите статью",
            "keyboard": [[{"text": "Отмена", "callback": True}]],
        }
    ]


create_article_confirm_id = "create_article_confirm"


def create_article_confirm_handler(update: dict) -> tuple:
    if update["handler_args"]:
        session: Session
        with Session(main.engine) as session:
            session.add(Article(text=update["state_args"]))
            session.commit()
        return (news_id, None)
    return (create_article_input_id, None)


def create_article_confirm_show(update: dict) -> list:
    return [
        {"text": "Создать"},
        {"text": update["new_state_args"]},
        {
            "text": "Подтвердить",
            "keyboard": [
                [
                    {"text": "Да", "callback": True},
                    {"text": "Нет", "callback": False},
                ]
            ],
        },
    ]


delete_article_confirm_id = "delete_article_confirm"


def delete_article_confirm_handler(update: dict) -> tuple:
    if update["handler_args"]:
        session: Session
        with Session(main.engine) as session:
            session.delete(session.get(Article, update["state_args"]))
            session.commit()
    return (news_id, None)


def delete_article_confirm_show(update: dict) -> list:
    session: Session
    with Session(main.engine) as session:
        article: str = session.get(Article, update["new_state_args"]).text
    return [
        {"text": "Создать"},
        {"text": article},
        {
            "text": "Подтвердить",
            "keyboard": [
                [
                    {"text": "Да", "callback": True},
                    {"text": "Нет", "callback": False},
                ]
            ],
        },
    ]


start_id = "start"


def start_handler(update: dict) -> tuple:
    if update["type"] == "message" and update["handler_args"] == "/start":
        return (main_id, None)
    return (None, None)


main_id = "main"


def main_handler(update: dict) -> tuple:
    if update["type"] == "callback":
        handler_args = update["handler_args"]
        if isinstance(handler_args, str) and handler_args in [
            news_id,
            ars_id,
            auction_id,
            diller_id,
            client_id,
        ]:
            return (handler_args, None)
    return (None, None)


def main_show(update: dict) -> list:
    return {
        "text": "Главное меню",
        "keyboard": [
            [{"text": "Новости", "callback": news_id}],
            [{"text": "СТО", "callback": ars_id}],
            [{"text": "Аукцион заявок", "callback": auction_id}],
            [{"text": "Кабинет диллера", "callback": diller_id}],
            [{"text": "Кабинет клиента", "callback": client_id}],
        ],
    }


news_id = "news"


def news_handler(update: dict) -> tuple:
    if update["type"] == "callback":
        admin = update["admin"]
        handler_args = update["handler_args"]
        if isinstance(handler_args, str):
            if handler_args == main_id:
                return (main_id, None)
            elif handler_args == create_article_input_id and admin:
                return (create_article_input_id, None)
        elif isinstance(handler_args, int) and admin:
            return (delete_article_confirm_id, handler_args)
    return (None, None)


def news_show(update: dict) -> list:
    admin: bool = update["admin"]
    render_list: list = []
    keyboard: Optional[list] = [
        [{"text": "Главное меню", "callback": main_id}]
    ]
    if admin:
        keyboard.append(
            [{"text": "Создать", "callback": create_article_input_id}]
        )
    render_list.append({"text": "Новости", "keyboard": keyboard})

    news_dict: list = []
    session: Session
    with Session(main.engine) as session:
        article: Article
        for article in session.query(Article).all():
            news_dict.append({"id": article.id, "text": article.text})
        session.commit()
    article_dict: dict
    for article_dict in news_dict:
        render_message = {"text": article_dict["text"]}
        if admin:
            render_message["keyboard"] = [
                [{"text": "Удалить", "callback": article_dict["id"]}]
            ]
        render_list.append(render_message)

    return render_list


ars_id = "ars"


def ars_handler(update: dict) -> tuple:
    if update["type"] == "callback":
        handler_args = update["handler_args"]
        if isinstance(handler_args, str) and handler_args == main_id:
            return (handler_args, None)
    return (None, None)


def ars_show(update: dict) -> list:
    return [
        {
            "text": "СТО",
            "keyboard": [[{"text": "Главное меню", "callback": main_id}]],
        }
    ]


auction_id = "auction"


def auction_handler(update: dict) -> tuple:
    if update["type"] == "callback":
        handler_args = update["handler_args"]
        if isinstance(handler_args, str) and handler_args == main_id:
            return (handler_args, None)
    return (None, None)


def auction_show(update: dict) -> list:
    return [
        {
            "text": "Аукцион заявок",
            "keyboard": [[{"text": "Главное меню", "callback": main_id}]],
        }
    ]


diller_id = "diller"


def diller_handler(update: dict) -> tuple:
    if update["type"] == "callback":
        handler_args = update["handler_args"]
        if isinstance(handler_args, str) and handler_args == main_id:
            return (handler_args, None)
    return (None, None)


def diller_show(update: dict) -> list:
    return [
        {
            "text": "Кабинет диллера",
            "keyboard": [[{"text": "Главное меню", "callback": main_id}]],
        }
    ]


client_id = "client"


def client_handler(update: dict) -> tuple:
    if update["type"] == "callback":
        handler_args = update["handler_args"]
        if isinstance(handler_args, str) and handler_args == main_id:
            return (handler_args, None)
    return (None, None)


def client_show(update: dict) -> list:
    return [
        {
            "text": "Кабинет клиента",
            "keyboard": [[{"text": "Главное меню", "callback": main_id}]],
        }
    ]


shows = {
    main_id: main_show,
    news_id: news_show,
    create_article_input_id: create_article_input_show,
    create_article_confirm_id: create_article_confirm_show,
    delete_article_confirm_id: delete_article_confirm_show,
    ars_id: ars_show,
    auction_id: auction_show,
    diller_id: diller_show,
    client_id: client_show,
}
handlers = {
    start_id: start_handler,
    main_id: main_handler,
    news_id: news_handler,
    create_article_input_id: create_article_input_handler,
    create_article_confirm_id: create_article_confirm_handler,
    delete_article_confirm_id: delete_article_confirm_handler,
    ars_id: ars_handler,
    auction_id: auction_handler,
    diller_id: diller_handler,
    client_id: client_handler,
}
