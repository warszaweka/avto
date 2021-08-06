from sqlalchemy.orm import Session

from models import User
from states import main_id, main_show


def start_handler(bot, engine, update):
    if (
        hasattr(update, "message")
        and hasattr(update.message, "text")
        and update.message.text == "/start"
    ):
        main_show(bot, update.message.chat.id)

        if hasattr(update.message, "from_user"):
            user_id = update.message.from_user.id
        with Session(engine) as session:
            session.add(
                User(user_id=user_id, state_id=main_id, state_args=None)
            )
            session.commit()
