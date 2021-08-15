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

from models import Callback, DeclarativeBase, User
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

    start = False
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

            if content == "/start":
                start = True
        elif "photo" in data["message"]:
            subtype = "photo"
            content = data["message"]["photo"][0]["file_id"]
        else:
            return
    elif "callback_query" in data:
        type = "callback"
        tg_id = data["callback_query"]["from"]["id"]

        callback_data = data["callback_query"]["data"]
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
            callbacks_list = []
            for callback in user.callbacks:
                callbacks_list.append(callback.data)

    if start:
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
            callbacks_list = []
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
        handled = False
        if (
            type == "message"
            and state_id in message_handlers
            and subtype in message_handlers[state_id]
        ):
            handler_return = message_handlers[state_id][subtype](
                id, state_args, content
            )
            if handler_return is not None:
                handled = True
                state_id = handler_return
        elif type == "callback" and callback_data in callbacks_list:
            handled = True
            new_state_id, handler_arg = callback_data.split(":")
            new_state_id = int(new_state_id)
            if state_id in callback_handlers:
                handler_return = callback_handlers[state_id](
                    id, state_args, new_state_id, handler_arg
                )
                if handler_return is not None:
                    new_state_id = handler_return
            state_id = new_state_id
        if not handled and not start:
            return
        if handled:
            with Session(engine) as session:
                user = session.get(User, id)
                user.state_id = state_id
                user.state_args = state_args
                session.commit()

    callbacks_list = []
    status = ""
    if "status" in state_args:
        status = f"{state_args['status']}\n\n"
        del state_args["status"]
        with Session(engine) as session:
            user = session.get(User, id)
            del user.state_args["status"]
            session.commit()
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
                        rendered_callback_data = f"{render_button['callback']['state_id']}:{render_button['callback']['handler_arg']}"
                        rendered_button[
                            "callback_data"
                        ] = rendered_callback_data
                        callbacks_list.append(rendered_callback_data)
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
    with Session(engine) as session:
        user = session.get(User, id)
        for callback in user.callbacks:
            session.delete(callback)
        for callback_str in callbacks_list:
            session.add(Callback(data=callback_str, user_id=id))
        session.commit()


flask = Flask(__name__)


@flask.post(f"/{getenv('WH_TOKEN')}")
def flask_handler():
    spawn(tg_handler, request.json)
    return ("", 204)
