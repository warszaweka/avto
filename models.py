from sqlalchemy.orm import declarative_base
from sqlalchemy.schema import Column
from sqlalchemy.types import JSON, Integer, String

Base = declarative_base()


class User(Base):
    __tablename__ = "state"

    id = Column(type=Integer, primary_key=True)
    state_id = Column(type=String(64), nullable=False)
    state_args = Column(type=JSON)
