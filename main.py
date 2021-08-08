from gevent.monkey import patch_all

patch_all()

from psycogreen.gevent import patch_psycopg

patch_psycopg()

from os import getenv
from re import sub

from flask import Flask, request
from gevent import spawn
from requests import Response, request as requests_request
from sqlalchemy.future import Engine, create_engine
from sqlalchemy.schema import MetaData
from ujson import dumps, loads

from models import DeclarativeBase

engine = create_engine(
    sub(r"^[^:]*", "postgresql+psycopg2", getenv("DB_URL"), 1)
)
DeclarativeBase.metadata.create_all(engine)

tg_token: str = getenv("TG_TOKEN")

admins: list = list(map(int, getenv("ADMINS").split(";")))

flask: Flask = Flask(__name__)


@flask.route(f"/{getenv('WH_TOKEN')}", methods=["POST"])
def flask_handler() -> tuple:
    spawn(tg_handler, request.data)
    return ("", 204)


def tg_handler(data: bytes) -> None:
    data: dict = loads(data)
    print(dumps(data, indent=2))
    # if update.callback_query is not None:
        # callback = True
        # user_id = update.callback_query.from_user.id
    # elif update.message is not None:
        # callback = False
        # user_id = update.message.from_user.id
    # else:
        # return
    # with Session(engine) as session:
        # user = session.get(User, user_id)
        # if user is None:
            # user_exists = False
        # else:
            # user_exists = True
            # state_id = user.state_id
            # state_args = user.state_args
    # admin = user_id in admins


def tg_request(method: str, data: dict) -> dict:
    result: Response = requests_request(
        headers={"Content-Type": "application/json"},
        method="POST",
        url=f"https://api.telegram.org/bot{tg_token}/{method}",
        data=dumps(data),
    )
    result.raise_for_status()
    return loads(result.content)
