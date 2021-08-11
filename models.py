from sqlalchemy import ForeignKey
from sqlalchemy.orm import RelationshipProperty, declarative_base, relationship
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy.schema import Column
from sqlalchemy.types import JSON, BigInteger, String, Unicode, UnicodeText

ars_name_length = 128

DeclarativeBase: DeclarativeMeta = declarative_base()


class User(DeclarativeBase):
    __tablename__: str = "user"

    id: Column = Column(BigInteger, primary_key=True)
    state_id: Column = Column(String(64), nullable=False)
    state_args: Column = Column(JSON, nullable=False)

    arses: RelationshipProperty = relationship("Ars", back_populates="user")


class Article(DeclarativeBase):
    __tablename__: str = "article"

    id: Column = Column(BigInteger, primary_key=True, autoincrement=True)
    text: Column = Column(UnicodeText, nullable=False)
    photo: Column = Column(UnicodeText)


class Ars(DeclarativeBase):
    __tablename__: str = "ars"

    id: Column = Column(BigInteger, primary_key=True, autoincrement=True)
    name: Column = Column(Unicode(ars_name_length), nullable=False)
    description: Column = Column(UnicodeText)
    photo: Column = Column(UnicodeText)
    phone_number: Column = Column(String(16))
    address: Column = Column(String(64))
    user_id: Column = Column(BigInteger, ForeignKey(User.id), nullable=False)

    user: RelationshipProperty = relationship(User, back_populates="arses")
