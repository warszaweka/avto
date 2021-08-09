from gevent.monkey import patch_all

patch_all()

from psycogreen.gevent import patch_psycopg

patch_psycopg()

from os import getenv
from re import sub
from typing import Optional

from flask import Flask, request
from gevent import spawn
from requests import Response, post
from sqlalchemy.future import Engine, create_engine
from sqlalchemy.orm import Session
from ujson import loads

from models import DeclarativeBase, User
from states import handlers, shows, start_state_id

engine: Engine = create_engine(
    sub(r"^[^:]*", "postgresql+psycopg2", getenv("DB_URL"), 1)
)
DeclarativeBase.metadata.create_all(engine)

tg_token: str = getenv("TG_TOKEN")

admins: list = list(map(int, getenv("ADMINS").split(";")))


def tg_request(method: str, data: dict) -> dict:
    response: Response = post(
        url=f"https://api.telegram.org/bot{tg_token}/{method}", json=data
    )
    response.raise_for_status()
    return response.json


def tg_handler(data: dict):
    print(data)
    update: dict = {}
    type: str
    if "message" in data:
        type = "message"
        message: dict = data["message"]
        user_id: int = message["from"]["id"]
        handler_args = message
    elif "callback_query" in data:
        type = "callback"
        callback: dict = data["callback_query"]
        user_id = callback["from"]["id"]
        handler_args = loads(callback["data"])
    else:
        return
    update["type"] = type
    update["user_id"] = user_id
    update["handler_args"] = handler_args

    update["admin"] = user_id in admins

    session: Session
    with Session(engine) as session:
        user: Optional[User] = session.get(User, user_id)
        if user is None:
            user = User(id=user_id, state_id=start_state_id, state_args={})
            session.add(user)
        current_state_id: str = user.state_id
        current_state_args: dict = user.state_args
        session.commit()
    update["current_state_id"] = current_state_id
    update["current_state_args"] = current_state_args


flask: Flask = Flask(__name__)


@flask.post(f"/{getenv('WH_TOKEN')}")
def flask_handler() -> tuple:
    spawn(tg_handler, request.json)
    return ("", 204)
