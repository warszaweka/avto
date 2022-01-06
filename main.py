from gevent.monkey import patch_all

patch_all()

from psycogreen.gevent import patch_psycopg

patch_psycopg()

from os import getenv
from re import sub
from sys import stderr

from flask import Flask, request
from gevent import spawn
from requests import post
from sqlalchemy import select
from sqlalchemy.future import create_engine
from sqlalchemy.orm import Session

from src import states
from src.models import Callback, DeclarativeBase, User
from src.states import MAIN_ID
from src.states import engine as states_engine

engine = create_engine(
    sub(r"^[^:]*", "postgresql+psycopg2", getenv("DATABASE_URL"), 1))
DeclarativeBase.metadata.create_all(engine)
states_engine["value"] = engine

tg_token = getenv("TG_TOKEN")

wp_id = getenv("WP_ID")


class TgRequestException(Exception):
    pass


def tg_request(method, data):
    response = post(
        url="https://api.telegram.org/bot" + tg_token + "/" + method,
        json=data,
    ).json()
    print("REQUEST: " + method + " " + str(data) + " RESPONSE: " +
          str(response),
          file=stderr)
    if not response["ok"]:
        raise TgRequestException(response["description"])
    return response["result"]


def tg_handler(data):
    print("UPDATE: " + str(data), file=stderr)

    is_message = False
    update_type = None
    if "message" in data:
        is_message = True
        tg_id = data["message"]["from"]["id"]
        if "text" in data["message"]:
            update_type = "text"
            handler_arg = data["message"]["text"]
        elif "photo" in data["message"]:
            update_type = "photo"
            handler_arg = data["message"]["photo"][0]["file_id"]
    elif "callback_query" in data:
        tg_id = data["callback_query"]["from"]["id"]
        update_type = "callback"
        handler_arg = data["callback_query"]["data"]

    if update_type is not None:
        user_id = None
        with Session(engine) as session:
            user = (session.execute(
                select(User).where(User.tg_id == tg_id)).scalars().first())
            if user:
                user_id = user.id
                tg_message_id = user.tg_message_id
                state_id = user.state_id
                state_args = user.state_args
                callbacks_list = [callback.data for callback in user.callbacks]

        automaton = True
        start = False
        if update_type == "text" and handler_arg == "/start":
            start = True
            if user_id is not None:
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
                        session.get(User,
                                    user_id).tg_message_id = tg_message_id
                        session.commit()
                    automaton = False
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
                automaton = False

        if user_id is not None:
            automatoned = False
            if automaton:
                automaton_handler = getattr(states,
                                            state_id + "_" + update_type, None)
                if update_type in ["text", "photo"]:
                    if automaton_handler:
                        automaton_return = automaton_handler(
                            user_id, state_args, handler_arg)
                        if automaton_return:
                            state_id = automaton_return
                            automatoned = True
                elif handler_arg in callbacks_list:
                    if ":" in handler_arg:
                        state_id, handler_arg = handler_arg.split(":")
                    else:
                        state_id = handler_arg
                        handler_arg = None
                    if automaton_handler:
                        automaton_return = automaton_handler(
                            user_id, state_args, state_id, handler_arg)
                        if automaton_return:
                            state_id = automaton_return
                    automatoned = True
            if automatoned:
                with Session(engine) as session:
                    user = session.get(User, user_id)
                    user.state_id = state_id
                    user.state_args = state_args
                    session.commit()

            if start or automatoned:
                status = None
                if "status" in state_args:
                    status = state_args["status"]
                    del state_args["status"]
                    with Session(engine) as session:
                        user = session.get(User, user_id)
                        user.state_args = state_args
                        session.commit()

                callbacks_list = []
                render_message = getattr(states,
                                         state_id + "_show")(user_id,
                                                             state_args)
                rendered_message = {
                    "chat_id": tg_id,
                    "message_id": tg_message_id,
                    "media": {
                        "type":
                        "photo",
                        "media":
                        render_message["photo"] if
                        ("photo" in render_message
                         and render_message["photo"]) else wp_id,
                        "caption":
                        (status + "\n\n" if status is not None else "") +
                        render_message["text"],
                    },
                    "reply_markup": {
                        "inline_keyboard": [],
                    },
                }
                for render_row in render_message["keyboard"]:
                    rendered_row = []
                    for render_button in render_row:
                        callback_data = (
                            render_button["callback"] if isinstance(
                                render_button["callback"], str) else
                            render_button["callback"]["state_id"] + ":" +
                            render_button["callback"]["handler_arg"])
                        callbacks_list.append(callback_data)
                        rendered_row.append({
                            "text": render_button["text"],
                            "callback_data": callback_data
                        })
                    rendered_message["reply_markup"]["inline_keyboard"].append(
                        rendered_row)

                with Session(engine) as session:
                    user = session.get(User, user_id)
                    for callback in user.callbacks:
                        session.delete(callback)
                    for callback_data in callbacks_list:
                        session.add(
                            Callback(data=callback_data, user_id=user_id))
                    session.commit()

                tg_request("editMessageMedia", rendered_message)

    if is_message:
        tg_request(
            "deleteMessage",
            {
                "chat_id": tg_id,
                "message_id": data["message"]["message_id"],
            },
        )


flask = Flask(__name__)


@flask.post("/" + getenv("WH_TOKEN"))
def flask_handler():
    spawn(tg_handler, request.json)
    return ("", 204)
