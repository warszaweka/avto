import os

from flask import Flask, request
from redis import from_url
from rq import Queue
from sqlalchemy import create_engine, text
from telegram import Bot, Update

database_url = os.getenv("DATABASE_URL")
if database_url.startswith("postgres://"):
    database_url = database_url.replace(
        "postgres://", "postgresql+psycopg2://", 1
    )
engine = create_engine(database_url, future=True)

bot = Bot(os.getenv("API_TOKEN"))

webhook_token = os.getenv("WEBHOOK_TOKEN")

redis_url = os.getenv("REDIS_URL")

flask = Flask(__name__)
print("MAIN")  # debug


@flask.route(f"/{webhook_token}")
def flask_handler():
    print("FLASK")  # debug
    update = Update.de_json(request.get_json(), bot)
    Queue("default", connection=from_url(redis_url)).enqueue(
        redis_handler, update
    )


def redis_handler(update: Update):
    print("REDIS")  # debug
    if hasattr(update, "message") and hasattr(update.message, "text"):
        reply_text = update.message.text
        bot.send_message(update.message.chat.id, f"TEST: {reply_text}")
    with engine.connect() as connection:
        connection.execute(text("select 'worker test'")).all()
