from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import (BIGINT, BOOLEAN, JSONB, MONEY,
                                            VARCHAR)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.schema import Column

DeclarativeBase = declarative_base()

PHOTO_LENGTH = 128
PHONE_LENGTH = 16

STATE_ID_LENGTH = 64


class User(DeclarativeBase):
    __tablename__ = "user"

    id = Column(BIGINT, autoincrement=True, primary_key=True)
    tg_id = Column(BIGINT, index=True, nullable=False, unique=True)
    tg_message_id = Column(BIGINT, nullable=False)
    state_id = Column(VARCHAR(STATE_ID_LENGTH), nullable=False)
    state_args = Column(JSONB, nullable=False)

    arses = relationship("Ars", back_populates="user")
    requests = relationship("Request", back_populates="user")


SPEC_NAME_LENGTH = 32


class Spec(DeclarativeBase):
    __tablename__ = "spec"

    id = Column(BIGINT, autoincrement=True, primary_key=True)
    name = Column(VARCHAR(SPEC_NAME_LENGTH), nullable=False)

    ars_specs = relationship("ArsSpec", back_populates="spec")
    request_specs = relationship("RequestSpec", back_populates="spec")


ARS_NAME_LENGTH = 128
ARS_DESCRIPTION_LENGTH = 2048
ARS_ADDRESS_LENGTH = 64


class Ars(DeclarativeBase):
    __tablename__ = "ars"

    id = Column(BIGINT, autoincrement=True, primary_key=True)
    name = Column(VARCHAR(ARS_NAME_LENGTH), nullable=False)
    description = Column(VARCHAR(ARS_DESCRIPTION_LENGTH), nullable=False)
    photo = Column(VARCHAR(PHOTO_LENGTH))
    phone = Column(VARCHAR(PHONE_LENGTH), nullable=False)
    address = Column(VARCHAR(ARS_ADDRESS_LENGTH), nullable=False)
    active = Column(BOOLEAN, nullable=False)
    user_id = Column(BIGINT, ForeignKey(User.id), nullable=False)

    user = relationship(User, back_populates="arses")
    ars_specs = relationship("ArsSpec", back_populates="ars")
    offers = relationship("Offer", back_populates="ars")


class ArsSpec(DeclarativeBase):
    __tablename__ = "ars_spec"

    ars_id = Column(BIGINT, ForeignKey(Ars.id), primary_key=True)
    spec_id = Column(BIGINT, ForeignKey(Spec.id), primary_key=True)
    cost_floor = Column(MONEY, nullable=False)
    cost_ceil = Column(MONEY)

    ars = relationship(Ars, back_populates="ars_specs")
    spec = relationship(Spec, back_populates="ars_specs")


REQEST_DESCRIPTION_LENGTH = 2048


class Request(DeclarativeBase):
    __tablename__ = "request"

    id = Column(BIGINT, autoincrement=True, primary_key=True)
    description = Column(VARCHAR(REQEST_DESCRIPTION_LENGTH), nullable=False)
    photo = Column(VARCHAR(PHOTO_LENGTH))
    phone = Column(VARCHAR(PHONE_LENGTH), nullable=False)
    active = Column(BOOLEAN, nullable=False)
    user_id = Column(BIGINT, ForeignKey(User.id), nullable=False)

    user = relationship(User, back_populates="requests")
    request_specs = relationship("RequestSpec", back_populates="request")
    offers = relationship("Offer", back_populates="request")


class RequestSpec(DeclarativeBase):
    __tablename__ = "request_spec"

    request_id = Column(BIGINT, ForeignKey(Request.id), primary_key=True)
    spec_id = Column(BIGINT, ForeignKey(Spec.id), primary_key=True)

    request = relationship(Request, back_populates="request_specs")
    spec = relationship(Spec, back_populates="request_specs")


class Offer(DeclarativeBase):
    __tablename__ = "offer"

    id = Column(BIGINT, autoincrement=True, primary_key=True)
    cost_floor = Column(MONEY, nullable=False)
    cost_ceil = Column(MONEY)
    active = Column(BOOLEAN, nullable=False)
    winner = Column(BOOLEAN, nullable=False)
    ars_id = Column(BIGINT, ForeignKey(Ars.id), nullable=False)
    request_id = Column(BIGINT, ForeignKey(Request.id), nullable=False)

    ars = relationship(Ars, back_populates="offers")
    request = relationship(Request, back_populates="offers")
