from gevent.monkey import patch_all

patch_all()

from psycogreen.gevent import patch_psycopg

patch_psycopg()

from os import getenv
from re import sub
from typing import Any, Optional

from flask import Flask, request
from gevent import spawn
from requests import Response, post
from sqlalchemy import select
from sqlalchemy.future import Engine, create_engine
from sqlalchemy.orm import Session
from sqlalchemy.schema import Column
from ujson import dumps, loads

from models import DeclarativeBase, User
from states import (callback_handlers, message_handlers, set_engine, shows,
                    start_id)

engine = create_engine(
    sub(r"^[^:]*", "postgresql+psycopg2", getenv("DB_URL"), 1)
)
DeclarativeBase.metadata.create_all(engine)
set_engine(engine)

tg_url = f"https://api.telegram.org/bot{getenv('TG_TOKEN')}/"

wp_id = getenv("WP_ID")


def tg_request(method, data):
    response = post(url=f"{tg_url}{method}", json=data)
    response.raise_for_status()
    response_data = response.json()
    if not response_data["ok"]:
        raise Exception(response_data["description"])
    return response_data["result"]


def tg_handler(data):
    if "message" in data:
        if "text" in data["message"]:
            subtype = "text"
            content = data["message"]["text"]
        elif "photo" in data["message"]:
            subtype = "photo"
            content = data["message"]["photo"][0]["file_id"]
        else:
            return
        type = "message"
        user_tg_id = data["message"]["from"]["id"]
        try:
            tg_request(
                "deleteMessage",
                {
                    "chat_id": user_tg_id,
                    "message_id": data["message"]["message_id"],
                },
            )
        except Exception:
            pass
    elif "callback_query" in data:
        callback = data["callback_query"]
        callback_data = loads(callback["data"])
        if not (
            isinstance(callback_data, dict)
            and "state_id" in callback_data
            and isinstance(callback_data["state_id"], str)
            and "state_args" in callback_data
            and isinstance(callback_data["state_args"], dict)
        ):
            return
        new_state_id = callback_data["state_id"]
        new_state_args = callback_data["state_args"]
        type = "callback"
        user_tg_id = callback["from"]["id"]
    else:
        return

    user_exists = False
    with Session(engine) as session:
        user = (
            session.execute(select(User).where(User.tg_id == user_tg_id))
            .scalars()
            .first()
        )
        if user is not None:
            user_exists = True
            user_id = user.id
            current_state_id = user.state_id
            current_state_args = user.state_args
            tg_message_id = user.tg_message_id
    if not user_exists:
        tg_message_id = tg_request(
            "sendPhoto", {"chat_id": user_tg_id, "photo": wp_id}
        )["result"]["message_id"]
        current_state_id = start_id
        current_state_args = {}
        with Session(engine) as session:
            user = User(
                tg_id=user_tg_id,
                tg_message_id=tg_message_id,
                state_id=current_state_id,
                state_args=current_state_args,
            )
            session.add(user)
            session.commit()
            user_id = user.id

    if type == "message":
        if current_state_id not in message_handlers:
            return
        handler_return = message_handlers[subtype][current_state_id](
            user_id, current_state_args, content
        )
        if handler_return is None:
            return
        new_state_id = handler_return
        new_state_args = current_state_args
    elif current_state_id in callback_handlers:
        try:
            handler_return = callback_handlers[current_state_id](
                user_id, current_state_args, new_state_id, new_state_args
            )
        except Exception:
            return
        if handler_return is not None:
            new_state_id = handler_return
    else:
        return

    render_message = shows[new_state_id](user_id, new_state_args)
    rendered_message = {"chat_id": user_tg_id, "message_id": tg_message_id}
    if "photo" in render_message:
        rendered_message = {
            "media": {
                "type": "photo",
                "media": render_message["photo"],
            }
        }
        if "text" in render_message:
            rendered_message["media"]["caption"] = render_message["text"]
    else:
        rendered_message = {
            "media": {
                "type": "photo",
                "media": wp_id,
                "caption": render_message["text"],
            }
        }
    if "keyboard" in render_message:
        rendered_keyboard = []
        for render_row in render_message["keyboard"]:
            rendered_row = []
            for render_button in render_row:
                if "text" in render_button:
                    rendered_button = {"text": render_button["text"]}
                    if "callback" in render_button:
                        rendered_button["callback_data"] = dumps(
                            render_button["callback"]
                        )
                    else:
                        rendered_button["url"] = render_button["url"]
                    rendered_row.append(rendered_button)
            if rendered_row:
                rendered_keyboard.append(rendered_row)
        if rendered_keyboard:
            rendered_message["reply_markup"] = {
                "inline_keyboard": rendered_keyboard
            }
    try:
        try:
            tg_request("editMessageMedia", rendered_message)
        except Exception:
            tg_message_id = tg_request(
                "sendPhoto", {"chat_id": user_tg_id, "photo": wp_id}
            )["result"]["message_id"]
            rendered_message["message_id"] = tg_message_id
            tg_request("editMessageMedia", rendered_message)
            with Session(engine) as session:
                user = session.get(User, user_id)
                user.tg_message_id = tg_message_id
                session.commit()
    except Exception:
        return

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
