from sqlalchemy.orm import declarative_base
from sqlalchemy.schema import Column
from sqlalchemy.types import JSON, Integer, String

Base = declarative_base()


class User(Base):
    __tablename__ = "state"

    id = Column(Integer, primary_key=True)
    state_id = Column(String(64), nullable=False)
    state_args = Column(JSON)
