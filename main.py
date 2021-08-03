import os

from flask import Flask
from sqlalchemy import create_engine, text

database_url = os.getenv("DATABASE_URL")
if database_url.startswith("postgres://"):
    database_url = database_url.replace(
        "postgres://", "postgresql+psycopg2://", 1
    )

engine = create_engine(database_url, future=True)

flask = Flask(__name__)


@flask.route("/")
def hello_world():
    with engine.connect() as connection:
        result = connection.execute(text("select 'hello world'")).all()
        return f"<p>{result}</p>"
