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
from ujson import dumps, loads

from models import DeclarativeBase, User
from states import handlers, shows, start_id

engine: Engine = create_engine(
    sub(r"^[^:]*", "postgresql+psycopg2", getenv("DB_URL"), 1)
)
DeclarativeBase.metadata.create_all(engine)

tg_token: str = getenv("TG_TOKEN")

admins: list = list(map(int, getenv("ADMINS").split(";")))


def tg_handler(data: dict):
    update: dict = {}

    type: str
    user_id: int
    chat_id: int
    if "message" in data:
        message: dict = data["message"]
        if "text" in message:
            type = "message"
            user_id = message["from"]["id"]
            chat_id = message["chat"]["id"]
            handler_args = message["text"]
        else:
            return
    elif "callback_query" in data:
        type = "callback"
        callback: dict = data["callback_query"]
        user_id = callback["from"]["id"]
        chat_id = callback["message"]["chat"]["id"]
        handler_args = loads(callback["data"])
    else:
        return
    update["type"] = type
    update["user_id"] = user_id
    update["chat_id"] = chat_id
    update["handler_args"] = handler_args

    update["admin"] = user_id in admins

    session: Session
    with Session(engine) as session:
        user: Optional[User] = session.get(User, user_id)
        if user is None:
            user = User(id=user_id, state_id=start_id)
            session.add(user)
        current_state_id: str = user.state_id
        current_state_args: Optional[dict] = user.state_args
        session.commit()
    update["current_state_id"] = current_state_id
    update["current_state_args"] = current_state_args

    new_state_id: str
    new_state_args: Optional[dict]
    new_state_id, new_state_args = handlers[current_state_id](update)
    if new_state_id is None:
        return
    update["new_state_id"] = new_state_id
    update["new_state_args"] = new_state_args

    render_message: dict
    render_row: list
    render_button: dict
    for render_message in shows[new_state_id](update):
        rendered_message = {"chat_id": chat_id, "text": render_message["text"]}
        if "keyboard" in render_message:
            rendered_message["reply_markup"] = {
                "inline_keyboard": [
                    [
                        {
                            "text": render_button["text"],
                            "callback_data": dumps(render_button["callback"]),
                        }
                        for render_button in render_row
                    ]
                    for render_row in render_message["keyboard"]
                ]
            }
        post(
            url=f"https://api.telegram.org/bot{tg_token}/sendMessage",
            json=rendered_message,
        ).raise_for_status()

    with Session(engine) as session:
        user = session.get(User, user_id)
        user.state_id = new_state_id
        if new_state_args is not None:
            user.state_args = new_state_args
        session.commit()


flask: Flask = Flask(__name__)


@flask.post(f"/{getenv('WH_TOKEN')}")
def flask_handler() -> tuple:
    spawn(tg_handler, request.json)
    return ("", 204)
