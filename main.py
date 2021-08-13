from gevent.monkey import patch_all

patch_all()

from psycogreen.gevent import patch_psycopg

patch_psycopg()

from os import getenv
from re import sub

from flask import Flask, request
from gevent import spawn
from requests import post
from sqlalchemy import select
from sqlalchemy.future import create_engine
from sqlalchemy.orm import Session
from ujson import dumps, loads

from models import DeclarativeBase, User
from states import (callback_handlers, main_id, message_handlers, set_engine,
                    shows)

engine = create_engine(
    sub(r"^[^:]*", "postgresql+psycopg2", getenv("DATABASE_URL"), 1)
)
DeclarativeBase.metadata.create_all(engine)
set_engine(engine)

tg_token = getenv("TG_TOKEN")

wp_id = getenv("WP_ID")


def tg_request(method, data):
    response = post(
        url=f"https://api.telegram.org/bot{tg_token}/{method}",
        json=data,
    )
    response_data = response.json()
    if not response_data["ok"]:
        raise Exception(response_data["description"])
    return response_data["result"]


def tg_handler(data):
    handling = True

    if "message" in data:
        type = "message"
        tg_id = data["message"]["from"]["id"]

        tg_request(
            "deleteMessage",
            {
                "chat_id": tg_id,
                "message_id": data["message"]["message_id"],
            },
        )

        if "text" in data["message"]:
            subtype = "text"
            content = data["message"]["text"]
        elif "photo" in data["message"]:
            subtype = "photo"
            content = data["message"]["photo"][0]["file_id"]
        else:
            return
    elif "callback_query" in data:
        type = "callback"
        tg_id = data["callback_query"]["from"]["id"]

        callback_data = loads(data["callback_query"]["data"])
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
    else:
        return

    user_exists = False

    with Session(engine) as session:
        user = (
            session.execute(select(User).where(User.tg_id == tg_id))
            .scalars()
            .first()
        )
        if user is not None:
            user_exists = True
            id = user.id
            tg_message_id = user.tg_message_id
            state_id = user.state_id
            state_args = user.state_args

    start = False
    if type == "message" and subtype == "text" and content == "/start":
        start = True
        if user_exists:
            try:
                tg_request(
                    "editMessageMedia",
                    {
                        "chat_id": tg_id,
                        "message_id": tg_message_id,
                        "media": {"type": "photo", "media": wp_id},
                    },
                )
            except Exception:
                tg_message_id = tg_request(
                    "sendPhoto", {"chat_id": tg_id, "photo": wp_id}
                )["message_id"]
                with Session(engine) as session:
                    user = session.get(User, id)
                    user.tg_message_id = tg_message_id
                    session.commit()
                handling = False
        else:
            tg_message_id = tg_request(
                "sendPhoto", {"chat_id": tg_id, "photo": wp_id}
            )["message_id"]
            state_id = main_id
            state_args = {}
            with Session(engine) as session:
                user = User(
                    tg_id=tg_id,
                    tg_message_id=tg_message_id,
                    state_id=state_id,
                    state_args=state_args,
                )
                session.add(user)
                session.commit()
                id = user.id
            handling = False
    elif not user_exists:
        return

    if handling:
        false_start = False
        if (
            type == "message"
            and state_id in message_handlers
            and subtype in message_handlers[state_id]
        ):
            handler_return = message_handlers[state_id][subtype](
                id, state_args, content
            )
            if handler_return is None:
                if start:
                    false_start = True
                else:
                    return
            else:
                state_id = handler_return
        elif type == "callback" and state_id in callback_handlers:
            print(new_state_id, new_state_args)  # debug
            try:
                handler_return = callback_handlers[state_id](
                    id, state_args, new_state_id, new_state_args
                )
            except Exception:
                return
            if handler_return is None:
                state_id = new_state_id
            else:
                state_id = handler_return
            if "action" in new_state_args:
                del new_state_args["action"]
            for new_state_arg_key, new_state_arg_val in new_state_args.items():
                if (
                    new_state_arg_val is None
                    and new_state_arg_key in state_args
                ):
                    del state_args[new_state_arg_key]
                else:
                    state_args[new_state_arg_key] = new_state_arg_val
        else:
            if start:
                false_start = True
            else:
                return
        if not false_start:
            with Session(engine) as session:
                user = session.get(User, id)
                user.state_id = state_id
                user.state_args = state_args
                session.commit()

    status = ""
    if "status" in state_args:
        status = f"{state_args['status']}\n\n"
        del state_args["status"]
    render_message = shows[state_id](id, state_args)
    rendered_message = {
        "chat_id": tg_id,
        "message_id": tg_message_id,
        "media": {
            "type": "photo",
            "media": wp_id,
            "caption": f"{status}{render_message['text']}",
        },
    }
    if "photo" in render_message and render_message["photo"]:
        rendered_message["media"]["media"] = render_message["photo"]
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
    tg_request("editMessageMedia", rendered_message)


flask: Flask = Flask(__name__)


@flask.post(f"/{getenv('WH_TOKEN')}")
def flask_handler() -> tuple:
    spawn(tg_handler, request.json)
    return ("", 204)
