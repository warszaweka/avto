from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from telegram import Bot, Update

from models import Base, User
from start_handler import start_handler
from states import state_handlers


def redis_handler(token, db, json):
    bot = Bot(token)
    update = Update.de_json(json, bot)
    if hasattr(update, "message") and hasattr(update.message, "from_user"):
        user_id = update.message.from_user.id
    elif hasattr(update, "callback_query"):
        user_id = update.callback_query.from_user.id

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

    if user_exists:
        state_handler = state_handlers[state_id]
        if state_args is not None:
            state_handler(bot, engine, update, state_args=state_args)
        else:
            state_handler(bot, engine, update)
    else:
        start_handler(bot, engine, update)
