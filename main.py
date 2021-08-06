from os import getenv

from flask import Flask, request
from redis import from_url
from rq import Queue

from redis_handler import redis_handler

db = getenv("DATABASE_URL")
if db.startswith("postgres://"):
    db = db.replace("postgres://", "postgresql+psycopg2://", 1)
token = getenv("API_TOKEN")
admins = getenv("ADMINS").split(";")
redis = getenv("REDIS_URL")
flask = Flask(__name__)


@flask.route(f"/{getenv('WEBHOOK_TOKEN')}", methods=["POST"])
def flask_handler():
    Queue("queue", connection=from_url(redis)).enqueue(
        redis_handler, db, token, admins, request.get_json()
    )
    return ("", 204)
