from sqlalchemy.orm import Session
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update

from models import User

main_id = "main"


def main_handle(bot, engine, update: Update):
    if hasattr(update, "callback_query") and hasattr(
        update.callback_query, "data"
    ):
        data = update.callback_query.data
        if data == news_id:
            if hasattr(update.callback_query, "message"):
                chat_id = update.callback_query.message.chat.id
            news_show(bot, chat_id)

            with Session(engine) as session:
                user = session.get(User, update.callback_query.from_user.id)
                user.state_id = news_id
                user.state_args = None
                session.commit()
        elif data == ars_id:
            if hasattr(update.callback_query, "message"):
                chat_id = update.callback_query.message.chat.id
            ars_show(bot, chat_id)

            with Session(engine) as session:
                user = session.get(User, update.callback_query.from_user.id)
                user.state_id = ars_id
                user.state_args = None
                session.commit()
        elif data == auction_id:
            if hasattr(update.callback_query, "message"):
                chat_id = update.callback_query.message.chat.id
            auction_show(bot, chat_id)

            with Session(engine) as session:
                user = session.get(User, update.callback_query.from_user.id)
                user.state_id = auction_id
                user.state_args = None
                session.commit()
        elif data == diller_id:
            if hasattr(update.callback_query, "message"):
                chat_id = update.callback_query.message.chat.id
            diller_show(bot, chat_id)

            with Session(engine) as session:
                user = session.get(User, update.callback_query.from_user.id)
                user.state_id = diller_id
                user.state_args = None
                session.commit()
        elif data == client_id:
            if hasattr(update.callback_query, "message"):
                chat_id = update.callback_query.message.chat.id
            client_show(bot, chat_id)

            with Session(engine) as session:
                user = session.get(User, update.callback_query.from_user.id)
                user.state_id = client_id
                user.state_args = None
                session.commit()


def main_show(bot: Bot, chat_id):
    bot.send_message(
        chat_id,
        "Главное меню",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Новости", callback_data=news_id)],
                [InlineKeyboardButton("СТО", callback_data=ars_id)],
                [
                    InlineKeyboardButton(
                        "Аукцион заявок", callback_data=auction_id
                    )
                ],
                [
                    InlineKeyboardButton(
                        "Кабинет диллера", callback_data=diller_id
                    )
                ],
                [
                    InlineKeyboardButton(
                        "Кабинет клиента", callback_data=client_id
                    )
                ],
            ]
        ),
    )


news_id = "news"


def news_handle(bot: Bot, engine, update: Update):
    if hasattr(update, "callback_query") and hasattr(
        update.callback_query, "data"
    ):
        data = update.callback_query.data
        if data == main_id:
            if hasattr(update.callback_query, "message"):
                chat_id = update.callback_query.message.chat.id
            main_show(bot, chat_id)

            with Session(engine) as session:
                user = session.get(User, update.callback_query.from_user.id)
                user.state_id = main_id
                user.state_args = None
                session.commit()


def news_show(bot: Bot, chat_id: int):
    bot.send_message(
        chat_id,
        "Новости",
        InlineKeyboardMarkup(
            [[InlineKeyboardButton("Главное меню", callback_data=main_id)]]
        ),
    )


ars_id = "ars"


def ars_handle(bot: Bot, engine, update: Update):
    if hasattr(update, "callback_query") and hasattr(
        update.callback_query, "data"
    ):
        data = update.callback_query.data
        if data == main_id:
            if hasattr(update.callback_query, "message"):
                chat_id = update.callback_query.message.chat.id
            main_show(bot, chat_id)

            with Session(engine) as session:
                user = session.get(User, update.callback_query.from_user.id)
                user.state_id = main_id
                user.state_args = None
                session.commit()


def ars_show(bot: Bot, chat_id: int):
    bot.send_message(
        chat_id,
        "СТО",
        InlineKeyboardMarkup(
            [[InlineKeyboardButton("Главное меню", callback_data=main_id)]]
        ),
    )


auction_id = "auction"


def auction_handle(bot: Bot, engine, update: Update):
    if hasattr(update, "callback_query") and hasattr(
        update.callback_query, "data"
    ):
        data = update.callback_query.data
        if data == main_id:
            if hasattr(update.callback_query, "message"):
                chat_id = update.callback_query.message.chat.id
            main_show(bot, chat_id)

            with Session(engine) as session:
                user = session.get(User, update.callback_query.from_user.id)
                user.state_id = main_id
                user.state_args = None
                session.commit()


def auction_show(bot: Bot, chat_id: int):
    bot.send_message(
        chat_id,
        "Аукцион заявок",
        InlineKeyboardMarkup(
            [[InlineKeyboardButton("Главное меню", callback_data=main_id)]]
        ),
    )


diller_id = "diller"


def diller_handle(bot: Bot, engine, update: Update):
    if hasattr(update, "callback_query") and hasattr(
        update.callback_query, "data"
    ):
        data = update.callback_query.data
        if data == main_id:
            if hasattr(update.callback_query, "message"):
                chat_id = update.callback_query.message.chat.id
            main_show(bot, chat_id)

            with Session(engine) as session:
                user = session.get(User, update.callback_query.from_user.id)
                user.state_id = main_id
                user.state_args = None
                session.commit()


def diller_show(bot: Bot, chat_id: int):
    bot.send_message(
        chat_id,
        "Кабинет диллера",
        InlineKeyboardMarkup(
            [[InlineKeyboardButton("Главное меню", callback_data=main_id)]]
        ),
    )


client_id = "client"


def client_handle(bot: Bot, engine, update: Update):
    if hasattr(update, "callback_query") and hasattr(
        update.callback_query, "data"
    ):
        data = update.callback_query.data
        if data == main_id:
            if hasattr(update.callback_query, "message"):
                chat_id = update.callback_query.message.chat.id
            main_show(bot, chat_id)

            with Session(engine) as session:
                user = session.get(User, update.callback_query.from_user.id)
                user.state_id = main_id
                user.state_args = None
                session.commit()


def client_show(bot: Bot, chat_id: int):
    bot.send_message(
        chat_id,
        "Кабинет клиента",
        InlineKeyboardMarkup(
            [[InlineKeyboardButton("Главное меню", callback_data=main_id)]]
        ),
    )


state_handlers = {
    main_id: main_handle,
    news_id: news_handle,
    ars_id: ars_handle,
    auction_id: auction_handle,
    diller_id: diller_handle,
    client_id: client_handle,
}
