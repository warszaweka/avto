from gevent.monkey import patch_all

patch_all()

from psycogreen.gevent import patch_psycopg

patch_psycopg()

from os import getenv
from re import sub
from typing import Optional

from flask import Flask, request
from gevent import spawn
from requests import post
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
    print(data)  # debug
    return
    type: str
    chat_id: int
    user_id: int
    handler_args: dict
    if "message" in data:
        type = "message"
        message: dict = data["message"]
        chat_id = message["chat"]["id"]
        user_id = message["from"]["id"]
        handler_args = {}
        if "text" in message:
            handler_args["text"] = message["text"]
    elif "callback_query" in data:
        callback: dict = data["callback_query"]
        handler_args = loads(callback["data"])
        if not isinstance(handler_args, dict):
            return
        type = "callback"
        chat_id = callback["message"]["chat"]["id"]
        user_id = callback["from"]["id"]
    else:
        return

    admin: bool = user_id in admins

    session: Session
    with Session(engine) as session:
        user: Optional[User] = session.get(User, user_id)
        if user is None:
            user = User(id=user_id, state_id=start_id, state_args={})
            session.add(user)
        current_state_id: str = user.state_id
        current_state_args: dict = user.state_args
        session.commit()

    handler_return = handlers[current_state_id][type](
        user_id, admin, current_state_args, handler_args
    )
    if handler_return is None:
        return
    new_state_id: str
    new_state_args: dict = {}
    render_list: list = []
    if not isinstance(handler_return, tuple):
        new_state_id = handler_return
    else:
        new_state_id = handler_return[0]
        new_state_args = handler_return[1]
        if len(handler_return) == 3:
            render_list = handler_return[2]

    render_list.extend(shows[new_state_id](user_id, admin, new_state_args))

    render_message: dict
    for render_message in render_list:
        rendered_message = {"chat_id": chat_id}
        url: str
        if "keyboard" in render_message:
            rendered_keyboard: list = []
            render_row: list
            render_button: dict
            for render_row in render_message["keyboard"]:
                rendered_row = []
                for render_button in render_row:
                    if "text" in render_button:
                        rendered_button = {"text": render_button["text"]}
                        if "callback" in render_button:
                            rendered_button["callback_data"] = dumps(
                                render_button["callback"]
                            )
                        rendered_row.append(rendered_button)
                if rendered_row:
                    rendered_keyboard.append(rendered_row)
            if rendered_keyboard:
                rendered_message["reply_markup"] = {
                    "inline_keyboard": rendered_keyboard
                }
        if "text" in render_message:
            rendered_message["text"] = render_message["text"]
            url = f"https://api.telegram.org/bot{tg_token}/sendMessage"
        post(
            url=url,
            json=rendered_message,
        ).raise_for_status()

    with Session(engine) as session:
        user = session.get(User, user_id)
        user.state_id = new_state_id
        user.state_args = new_state_args
        session.commit()


flask: Flask = Flask(__name__)


@flask.post(f"/{getenv('WH_TOKEN')}")
def flask_handler() -> tuple:
    spawn(tg_handler, request.json)
    return ("", 204)
