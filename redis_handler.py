from sqlalchemy import create_engine, text
from telegram import Bot, Update


def redis_handler(json, db, token):
    engine = create_engine(db, future=True)

    bot = Bot(token)

    update = Update.de_json(json, bot)

    if hasattr(update, "message") and hasattr(update.message, "text"):
        bot.send_message(
            update.message.chat.id, f"TEST: {update.message.text}"
        )

    with engine.connect() as conn:
        conn.execute(text("select 'worker test'")).all()
