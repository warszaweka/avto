from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy.schema import Column
from sqlalchemy.types import JSON, Integer, String, UnicodeText

DeclarativeBase: DeclarativeMeta = declarative_base()


class User(DeclarativeBase):
    __tablename__: str = "user"

    id: Column = Column(Integer, primary_key=True)
    state_id: Column = Column(String(64), nullable=False)
    state_args: Column = Column(JSON)


class Article(DeclarativeBase):
    __tablename__: str = "article"

    id: Column = Column(Integer, primary_key=True)
    text: Column = Column(UnicodeText, nullable=False)