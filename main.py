from gevent.monkey import patch_all

patch_all()

from psycogreen.gevent import patch_psycopg

patch_psycopg()

from os import getenv
from re import sub
from sys import stderr # DEBUG

from flask import Flask, request
from gevent import spawn
from requests import post
from sqlalchemy import select
from sqlalchemy.future import create_engine
from sqlalchemy.orm import Session

from src import states
from src.models import Callback, DeclarativeBase, User
from src.processors import nv_key
from src.states import MAIN_ID
from src.states import engine as states_engine

engine = create_engine(
    sub(r"^[^:]*", "postgresql+psycopg2", getenv("DATABASE_URL"), 1))
DeclarativeBase.metadata.create_all(engine)
states_engine["value"] = engine

tg_token = getenv("TG_TOKEN")

wp_id = getenv("WP_ID")

nv_key["value"] = getenv("NV_KEY")


class TgRequestException(Exception):
    pass


def tg_request(method, data):
    response = post(
        url="https://api.telegram.org/bot" + tg_token + "/" + method,
        json=data,
    ).json()
    if not response["ok"]:
        raise TgRequestException(response["description"])
    return response["result"]


def add_callback_data(callbacks_list, callback_data):
    callbacks_list.append(callback_data)
    return callback_data


def tg_handler(data):
    print(data, file=stderr) # DEBUG
    # START DEBUG
    if data["message"]["text"] == "contact" or data["message"]["text"] == "contact1":
        tg_request(
            "sendMessage",
            {
                "chat_id": data["message"]["from"]["id"],
                "text": "contact_request",
                "reply_markup": {
                    "keyboard": [
                        [
                            {
                                "text": "button",
                                "request_contact": True,
                            },
                        ],
                    ],
                    "one_time_keyboard": True if data["message"]["text"] == "contact1" else False,
                },
            },
        )
    # END DEBUG
    handling = True

    start = False
    if "message" in data:
        tg_id = data["message"]["from"]["id"]

        tg_request(
            "deleteMessage",
            {
                "chat_id": tg_id,
                "message_id": data["message"]["message_id"],
            },
        )

        if "text" in data["message"]:
            update_type = "text"
            handler_arg = data["message"]["text"]

            if handler_arg == "/start":
                start = True
        elif "photo" in data["message"]:
            update_type = "photo"
            handler_arg = data["message"]["photo"][0]["file_id"]
        else:
            return
    elif "callback_query" in data:
        update_type = "callback"
        tg_id = data["callback_query"]["from"]["id"]
        handler_arg = data["callback_query"]["data"]
    else:
        return

    user_exists = False
    with Session(engine) as session:
        user = (session.execute(
            select(User).where(User.tg_id == tg_id)).scalars().first())
        if user:
            user_exists = True

            user_id = user.id
            tg_message_id = user.tg_message_id
            state_id = user.state_id
            state_args = user.state_args
            callbacks_list = [callback.data for callback in user.callbacks]

    if start:
        if user_exists:
            try:
                tg_request(
                    "editMessageMedia",
                    {
                        "chat_id": tg_id,
                        "message_id": tg_message_id,
                        "media": {
                            "type": "photo",
                            "media": wp_id
                        },
                    },
                )
            except TgRequestException:
                tg_message_id = tg_request("sendPhoto", {
                    "chat_id": tg_id,
                    "photo": wp_id
                })["message_id"]
                with Session(engine) as session:
                    session.get(User, user_id).tg_message_id = tg_message_id
                    session.commit()

                handling = False
        else:
            tg_message_id = tg_request("sendPhoto", {
                "chat_id": tg_id,
                "photo": wp_id
            })["message_id"]
            state_id = MAIN_ID
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
                user_id = user.id

            handling = False
    elif not user_exists:
        return

    if handling:
        handled = False
        handler = getattr(states, state_id + "_" + update_type, None)
        if update_type in ["text", "photo"]:
            if handler:
                handler_return = handler(user_id, state_args, handler_arg)
                if handler_return:
                    state_id = handler_return
                    handled = True
        elif handler_arg in callbacks_list:
            if ":" in handler_arg:
                state_id, handler_arg = handler_arg.split(":")
            else:
                state_id = handler_arg
                handler_arg = None
            if handler:
                handler_return = handler(user_id, state_args, state_id,
                                         handler_arg)
                if handler_return:
                    state_id = handler_return
            handled = True
        if not (handled or start):
            return
        if handled:
            with Session(engine) as session:
                user = session.get(User, user_id)
                user.state_id = state_id
                user.state_args = state_args
                session.commit()

    status = ""
    if "status" in state_args:
        status = state_args["status"] + "\n\n"
        del state_args["status"]
        with Session(engine) as session:
            user = session.get(User, user_id)
            user.state_args = state_args
            session.commit()
    render_message = getattr(states, state_id + "_show")(user_id, state_args)
    callbacks_list = []
    rendered_message = {
        "chat_id": tg_id,
        "message_id": tg_message_id,
        "media": {
            "type":
            "photo",
            "media":
            render_message["photo"] if
            ("photo" in render_message and render_message["photo"]) else wp_id,
            "caption":
            status + render_message["text"],
        },
        "reply_markup": {
            "inline_keyboard": [],
        },
    }
    for render_row in render_message["keyboard"]:
        rendered_row = []
        for render_button in render_row:
            callback_data = (render_button["callback"] if isinstance(
                render_button["callback"],
                str) else render_button["callback"]["state_id"] + ":" +
                             render_button["callback"]["handler_arg"])
            callbacks_list.append(callback_data)
            rendered_row.append({
                "text": render_button["text"],
                "callback_data": callback_data
            })
        rendered_message["reply_markup"]["inline_keyboard"].append(
            rendered_row)
    tg_request("editMessageMedia", rendered_message)
    with Session(engine) as session:
        user = session.get(User, user_id)
        for callback in user.callbacks:
            session.delete(callback)
        for callback_data in callbacks_list:
            session.add(Callback(data=callback_data, user_id=user_id))
        session.commit()


flask = Flask(__name__)


@flask.post("/" + getenv("WH_TOKEN"))
def flask_handler():
    spawn(tg_handler, request.json)
    return ("", 204)
