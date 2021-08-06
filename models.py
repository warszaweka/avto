from sqlalchemy.orm import declarative_base
from sqlalchemy.schema import Column
from sqlalchemy.types import JSON, Integer, String, UnicodeText

Base = declarative_base()


class User(Base):
    __tablename__ = "state"
    id = Column(Integer, primary_key=True)
    state_id = Column(String(64), nullable=False)
    state_args = Column(JSON)


class Article(Base):
    __tablename__ = "article"
    id = Column(Integer, primary_key=True)
    text = Column(UnicodeText)
