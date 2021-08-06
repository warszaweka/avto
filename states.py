from sqlalchemy.orm import Session
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from ujson import dumps, loads

from models import Article, User


def change_state(engine, user_id, state_id, state_args):
    with Session(engine) as session:
        user = session.get(User, user_id)
        user.state_id = state_id
        user.state_args = state_args
        session.commit()


def route_callback(engine, bot, admin, state_args, update, handler):
    if update.callback_query.data is None:
        return
    new_state_id, new_state_args = handler(
        engine,
        bot,
        admin,
        state_args,
        update,
        loads(update.callback_query.data),
    )
    if new_state_id is None:
        return
    user_id = update.callback_query.from_user.id
    get_state_shows()[new_state_id](
        engine,
        bot,
        update.callback_query.message.chat.id,
        user_id,
        admin,
        new_state_args,
    )
    change_state(engine, user_id, new_state_id, new_state_args)


def start_handler(engine, bot, admin, update):
    if update.message.text != "/start":
        return
    user_id = update.message.from_user.id
    main_show(engine, bot, update.message.chat.id, user_id, admin, None)
    with Session(engine) as session:
        session.add(
            User(
                id=user_id,
                state_id=main_id,
                state_args=None,
            )
        )
        session.commit()


def get_state_handlers_message():
    return {create_article_id: create_article_handler_message}


def get_state_handlers_callback():
    return {
        main_id: main_handler_callback,
        news_id: news_handler_callback,
        create_article_id: create_article_handler_callback,
        create_article_confirm_id: create_article_confirm_handler_callback,
        delete_article_id: delete_article_handler_callback,
        ars_id: ars_handler_callback,
        auction_id: auction_handler_callback,
        diller_id: diller_handler_callback,
        client_id: client_handler_callback,
    }


def get_state_shows():
    return {
        main_id: main_show,
        news_id: news_show,
        create_article_id: create_article_show,
        create_article_confirm_id: create_article_confirm_show,
        delete_article_id: delete_article_show,
        ars_id: ars_show,
        auction_id: auction_show,
        diller_id: diller_show,
        client_id: client_show,
    }


main_id = "main"


def main_handler_callback(engine, bot, admin, state_args, update):
    def handler(engine, bot, admin, state_args, update, data):
        if "state_id" in data:
            new_state_id = data["state_id"]
            if new_state_id in {
                news_id,
                ars_id,
                auction_id,
                diller_id,
                client_id,
            }:
                return (new_state_id, None)
        return (None, None)

    route_callback(engine, bot, admin, state_args, update, handler)


def main_show(engine, bot, chat_id, user_id, admin, new_state_args):
    bot.send_message(
        chat_id,
        "Главное меню",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Новости", callback_data=dumps({"state_id": news_id})
                    )
                ],
                [
                    InlineKeyboardButton(
                        "СТО", callback_data=dumps({"state_id": ars_id})
                    )
                ],
                [
                    InlineKeyboardButton(
                        "Аукцион заявок",
                        callback_data=dumps({"state_id": auction_id}),
                    )
                ],
                [
                    InlineKeyboardButton(
                        "Кабинет диллера",
                        callback_data=dumps({"state_id": diller_id}),
                    )
                ],
                [
                    InlineKeyboardButton(
                        "Кабинет клиента",
                        callback_data=dumps({"state_id": client_id}),
                    )
                ],
            ]
        ),
    )


news_id = "news"


def news_handler_callback(engine, bot, admin, state_args, update):
    def handler(engine, bot, admin, state_args, update, data):
        if "state_id" in data:
            new_state_id = data["state_id"]
            if (
                new_state_id == main_id
                or new_state_id == create_article_id
                and admin
            ):
                return (new_state_id, None)
            elif new_state_id == delete_article_id and admin:
                return (new_state_id, {"article_id": data["article_id"]})
        return (None, None)

    route_callback(engine, bot, admin, state_args, update, handler)


def news_show(engine, bot, chat_id, user_id, admin, new_state_args):
    bot.send_message(
        chat_id,
        "Новости",
        reply_markup=(
            InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Создать",
                            callback_data=dumps(
                                {"state_id": create_article_id}
                            ),
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Главное меню",
                            callback_data=dumps({"state_id": main_id}),
                        )
                    ],
                ]
            )
            if admin
            else InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Главное меню",
                            callback_data=dumps({"state_id": main_id}),
                        )
                    ]
                ]
            )
        ),
    )
    news = []
    with Session(engine) as session:
        for article in session.query(Article).all():
            news.append({"text": article.text, "id": article.id})
        session.commit()
    for article in news:
        bot.send_message(
            chat_id,
            article["text"],
            reply_markup=(
                InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Удалить",
                                callback_data=dumps(
                                    {
                                        "state_id": "delete_article",
                                        "article_id": article["id"],
                                    }
                                ),
                            )
                        ]
                    ]
                )
                if admin
                else None
            ),
        )


create_article_id = "create_article"


def create_article_handler_callback(engine, bot, admin, state_args, update):
    def handler(engine, bot, admin, state_args, update, data):
        return (data["state_id"], None)

    route_callback(engine, bot, admin, state_args, update, handler)


def create_article_handler_message(engine, bot, admin, state_args, update):
    if update.message.text is None:
        return
    new_state_args = {"text": update.message.text}
    user_id = update.message.from_user.id
    create_article_confirm_show(
        engine,
        bot,
        update.message.chat.id,
        user_id,
        admin,
        new_state_args,
    )
    change_state(engine, user_id, create_article_confirm_id, new_state_args)


def create_article_show(engine, bot, chat_id, user_id, admin, new_state_args):
    bot.send_message(
        chat_id,
        "Введите статью",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Отмена", callback_data=dumps({"state_id": news_id})
                    )
                ]
            ]
        ),
    )


create_article_confirm_id = "create_article_confirm"


def create_article_confirm_handler_callback(
    engine, bot, admin, state_args, update
):
    def handler(engine, bot, admin, state_args, update, data):
        if data["answer"]:
            with Session(engine) as session:
                session.add(Article(text=state_args["text"]))
                session.commit()
        return (data["state_id"], None)

    route_callback(engine, bot, admin, state_args, update, handler)


def create_article_confirm_show(
    engine, bot, chat_id, user_id, admin, new_state_args
):
    bot.send_message(chat_id, "Создать")
    bot.send_message(chat_id, new_state_args["text"])
    bot.send_message(
        chat_id,
        "Подтвердить",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Да",
                        callback_data=dumps(
                            {"state_id": news_id, "answer": True}
                        ),
                    )
                ],
                [
                    InlineKeyboardButton(
                        "Нет",
                        callback_data=dumps(
                            {"state_id": create_article_id, "answer": False}
                        ),
                    )
                ],
            ]
        ),
    )


delete_article_id = "delete_article"


def delete_article_handler_callback(engine, bot, admin, state_args, update):
    def handler(engine, bot, admin, state_args, update, data):
        if data["answer"]:
            with Session(engine) as session:
                session.delete(session.get(Article, state_args["article_id"]))
                session.commit()
        return (data["state_id"], None)

    route_callback(engine, bot, admin, state_args, update, handler)


def delete_article_show(engine, bot, chat_id, user_id, admin, new_state_args):
    bot.send_message(chat_id, "Удалить")
    with Session(engine) as session:
        article = session.get(Article, new_state_args["article_id"]).text
    bot.send_message(chat_id, article)
    bot.send_message(
        chat_id,
        "Подтвердить",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Да",
                        callback_data=dumps(
                            {"state_id": news_id, "answer": True}
                        ),
                    )
                ],
                [
                    InlineKeyboardButton(
                        "Нет",
                        callback_data=dumps(
                            {"state_id": news_id, "answer": False}
                        ),
                    )
                ],
            ]
        ),
    )


ars_id = "ars"


def ars_handler_callback(engine, bot, admin, state_args, update):
    def handler(engine, bot, admin, state_args, update, data):
        if "state_id" in data:
            new_state_id = data["state_id"]
            if new_state_id == main_id:
                return (new_state_id, None)
        return (None, None)

    route_callback(engine, bot, admin, state_args, update, handler)


def ars_show(engine, bot, chat_id, user_id, admin, new_state_args):
    bot.send_message(
        chat_id,
        "СТО",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Главное меню",
                        callback_data=dumps({"state_id": main_id}),
                    )
                ]
            ]
        ),
    )


auction_id = "auction"


def auction_handler_callback(engine, bot, admin, state_args, update):
    def handler(engine, bot, admin, state_args, update, data):
        if "state_id" in data:
            new_state_id = data["state_id"]
            if new_state_id == main_id:
                return (new_state_id, None)
        return (None, None)

    route_callback(engine, bot, admin, state_args, update, handler)


def auction_show(engine, bot, chat_id, user_id, admin, new_state_args):
    bot.send_message(
        chat_id,
        "Аукцион заявок",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Главное меню",
                        callback_data=dumps({"state_id": main_id}),
                    )
                ]
            ]
        ),
    )


diller_id = "diller"


def diller_handler_callback(engine, bot, admin, state_args, update):
    def handler(engine, bot, admin, state_args, update, data):
        if "state_id" in data:
            new_state_id = data["state_id"]
            if new_state_id == main_id:
                return (new_state_id, None)
        return (None, None)

    route_callback(engine, bot, admin, state_args, update, handler)


def diller_show(engine, bot, chat_id, user_id, admin, new_state_args):
    bot.send_message(
        chat_id,
        "Кабинет диллера",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Главное меню",
                        callback_data=dumps({"state_id": main_id}),
                    )
                ]
            ]
        ),
    )


client_id = "client"


def client_handler_callback(engine, bot, admin, state_args, update):
    def handler(engine, bot, admin, state_args, update, data):
        if "state_id" in data:
            new_state_id = data["state_id"]
            if new_state_id == main_id:
                return (new_state_id, None)
        return (None, None)

    route_callback(engine, bot, admin, state_args, update, handler)


def client_show(engine, bot, chat_id, user_id, admin, new_state_args):
    bot.send_message(
        chat_id,
        "Кабинет клиента",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Главное меню",
                        callback_data=dumps({"state_id": main_id}),
                    )
                ]
            ]
        ),
    )
