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
from src.states import START_ID
from src.states import engine as states_engine

engine = create_engine(
    sub(r"^[^:]*", "postgresql+psycopg2", getenv("DATABASE_URL"), 1))
DeclarativeBase.metadata.create_all(engine)
states_engine["value"] = engine

tg_token = getenv("TG_TOKEN")

wp_id = getenv("WP_ID")


def tg_request(method, data):
    response = post(
        url="https://api.telegram.org/bot" + tg_token + "/" + method,
        json=data,
    ).json()
    print("REQUEST: " + method + " " + str(data) + "\nRESPONSE: " +
          str(response),
          file=stderr)
    if response["ok"]:
        return response["result"]
    return response["description"]


def tg_handler(data):
    print("UPDATE: " + str(data), file=stderr)

    is_message = False
    update_type = None
    if "message" in data:
        is_message = True
        data_message = data["message"]
        tg_id = data_message["from"]["id"]
        if "text" in data_message:
            data_message_text = data_message["text"]
            if data_message_text == "/start":
                update_type = "start"
            else:
                update_type = "text"
                handler_arg = data_message_text
        elif "photo" in data_message:
            update_type = "photo"
            handler_arg = data_message["photo"][0]["file_id"]
        elif "contact" in data_message:
            data_message_contact = data_message["contact"]
            if data_message_contact["user_id"] == tg_id:
                update_type = "contact"
                handler_arg = data_message_contact["phone_number"]
    elif "callback_query" in data:
        data_callback_query = data["callback_query"]
        tg_id = data_callback_query["from"]["id"]
        update_type = "callback"
        handler_arg = data_callback_query["data"]

    if update_type is not None:
        user_id = None
        with Session(engine) as session:
            user = session.execute(
                select(User).where(User.tg_id == tg_id)).scalars().first()
            if user is not None:
                user_id = user.id
                tg_message_id = user.tg_message_id
                state_id = user.state_id
                state_args = user.state_args
                callbacks_list = [callback.data for callback in user.callbacks]

        if update_type == "start" or user_id is not None:
            status = None

            if update_type == "start":
                if user_id is not None:
                    tg_request(
                        "deleteMessage",
                        {
                            "chat_id": tg_id,
                            "message_id": tg_message_id,
                        },
                    )

                tg_message_id = tg_request("sendPhoto", {
                    "chat_id": tg_id,
                    "photo": wp_id,
                })["message_id"]

                if user_id is not None:
                    with Session(engine) as session:
                        session.get(User,
                                    user_id).tg_message_id = tg_message_id
                        session.commit()
                else:
                    state_id = START_ID
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
            else:
                automaton = False
                automaton_handler = getattr(states,
                                            state_id + "_" + update_type, None)
                if update_type in ["text", "photo", "contact"]:
                    if automaton_handler is not None:
                        automaton_return = automaton_handler(
                            user_id, state_args, handler_arg)
                        if automaton_return is not None:
                            state_id = automaton_return
                            automaton = True
                elif handler_arg in callbacks_list:
                    if ":" in handler_arg:
                        state_id, handler_arg = handler_arg.split(":")
                    else:
                        state_id = handler_arg
                        handler_arg = None
                    if automaton_handler is not None:
                        automaton_return = automaton_handler(
                            user_id, state_args, state_id, handler_arg)
                        if automaton_return is not None:
                            state_id = automaton_return
                    automaton = True

                if automaton:
                    if "_status" in state_args:
                        status = state_args["_status"]
                        del state_args["_status"]
                    with Session(engine) as session:
                        user = session.get(User, user_id)
                        user.state_id = state_id
                        user.state_args = state_args
                        session.commit()

            if update_type == "start" or automaton:
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
                        render_message["photo"]
                        if "photo" in render_message else wp_id,
                        "caption":
                        (status + "\n\n" if status is not None else "") +
                        (render_message["text"]
                         if "text" in render_message else ""),
                    },
                }
                if "keyboard" in render_message:
                    rendered_inline_keyboard = []
                    for render_row in render_message["keyboard"]:
                        rendered_row = []
                        for render_button in render_row:
                            render_callback = render_button["callback"]
                            callback_data = (render_callback if isinstance(
                                render_callback,
                                str) else render_callback["state_id"] + ":" +
                                             render_callback["handler_arg"])
                            callbacks_list.append(callback_data)
                            rendered_row.append({
                                "text": render_button["text"],
                                "callback_data": callback_data,
                            })
                        rendered_inline_keyboard.append(rendered_row)
                    rendered_message["reply_markup"] = {
                        "inline_keyboard": rendered_inline_keyboard,
                    }

                with Session(engine) as session:
                    user = session.get(User, user_id)
                    for callback in user.callbacks:
                        session.delete(callback)
                    for callback_data in callbacks_list:
                        session.add(
                            Callback(data=callback_data, user_id=user_id))
                    session.commit()

                tg_request("editMessageMedia", rendered_message)

                if "_contact" in state_args:
                    tg_request(
                        "deleteMessage",
                        {
                            "chat_id": tg_id,
                            "message_id": state_args["_contact"],
                        },
                    )
                    del state_args["_contact"]
                    with Session(engine) as session:
                        session.get(User, user_id).state_args = state_args
                        session.commit()
                if "contact" in render_message:
                    render_contact = render_message["contact"]
                    state_args["_contact"] = tg_request(
                        "sendMessage", {
                            "chat_id": tg_id,
                            "text": render_contact["text"],
                            "reply_markup": {
                                "keyboard": [
                                    [
                                        {
                                            "text": render_contact["button"],
                                            "request_contact": True,
                                        },
                                    ],
                                ],
                            },
                        })["message_id"]
                    with Session(engine) as session:
                        session.get(User, user_id).state_args = state_args
                        session.commit()

    if is_message:
        tg_request(
            "deleteMessage",
            {
                "chat_id": tg_id,
                "message_id": data_message["message_id"],
            },
        )


flask = Flask(__name__)


@flask.post("/" + getenv("WH_TOKEN"))
def flask_handler():
    spawn(tg_handler, request.json)
    return ("", 204)
