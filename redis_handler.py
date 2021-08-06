from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from telegram import Bot, Update

from models import Base, User
from states import (get_state_handlers_callback, get_state_handlers_message,
                    start_handler)


def redis_handler(db, token, admins, json):
    bot = Bot(token)
    update = Update.de_json(json, bot)
    if update.callback_query is not None:
        callback = True
        user_id = update.callback_query.from_user.id
    elif update.message is not None:
        callback = False
        user_id = update.message.from_user.id
    else:
        return
    engine = create_engine(db, future=True)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        user = session.get(User, user_id)
        if user is None:
            user_exists = False
        else:
            user_exists = True
            state_id = user.state_id
            state_args = user.state_args
    admin = user_id in admins
    if user_exists:
        if callback:
            state_handlers = get_state_handlers_callback()
        else:
            state_handlers = get_state_handlers_message()
        if state_id not in state_handlers:
            return
        state_handlers[state_id](
            engine, bot, admin, state_args, update
        )
    elif not callback:
        start_handler(engine, bot, admin, update)
    else:
        return
