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
api_token = os.getenv("API_TOKEN")
webhook_token = os.getenv("WEBHOOK_TOKEN")
redis_url = os.getenv("REDIS_URL")


def get_bot():
    if not hasattr(get_bot, "bot"):
        get_bot.bot = Bot(api_token)
    return get_bot.bot


flask = Flask(__name__)


@flask.route(f"/{webhook_token}", methods=["POST"])
def flask_handler():
    update = Update.de_json(request.get_json(), get_bot())
    Queue("default", connection=from_url(redis_url)).enqueue(
        redis_handler, update
    )


def redis_handler(update: Update):
    def get_engine():
        if not hasattr(redis_handler, "engine"):
            redis_handler.engine = create_engine(database_url, future=True)
        return redis_handler.engine

    if hasattr(update, "message") and hasattr(update.message, "text"):
        reply_text = update.message.text
        get_bot().send_message(update.message.chat.id, f"TEST: {reply_text}")

    with get_engine.connect() as connection:
        connection.execute(text("select 'worker test'")).all()
