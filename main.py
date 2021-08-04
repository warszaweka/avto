import os

from flask import Flask
from redis import from_url
from rq import Queue
from sqlalchemy import create_engine, text

database_url = os.getenv("DATABASE_URL")
if database_url.startswith("postgres://"):
    database_url = database_url.replace(
        "postgres://", "postgresql+psycopg2://", 1
    )
engine = create_engine(database_url, future=True)

webhook_token = os.getenv("WEBHOOK_TOKEN")

redis_url = os.getenv("REDIS_URL")

flask = Flask(__name__)


@flask.route(f"/{webhook_token}")
def flask_handler():
    Queue('default', connection=from_url(redis_url)).enqueue(redis_handler)
    return "<p>main test</p>"


def redis_handler():
    with engine.connect() as connection:
        connection.execute(text("select 'worker test'")).all()
