from sqlalchemy import ForeignKey, Table
from sqlalchemy.dialects.postgresql import (BIGINT, INTEGER, JSONB, NUMERIC,
                                            SMALLINT, VARCHAR)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.schema import Column

DeclarativeBase = declarative_base()

SPEC_TITLE_LENGTH = 32
VENDOR_TITLE_LENGTH = 32
STATE_ID_LENGTH = 48
PHONE_LENGTH = 13
CALLBACK_DATA_LENGTH = 64
YEAR_LENGTH = 4
ARS_TITLE_LENGTH = 128
PICTURE_LENGTH = 128

DESCRIPTION_LENGTH = 2048
ADDRESS_LENGTH = 64

ars_spec = Table(
    "ars_spec", DeclarativeBase.metadata,
    Column("ars_id", BIGINT, ForeignKey("Ars.id"), primary_key=True),
    Column("spec_id", BIGINT, ForeignKey("Spec.id"), primary_key=True))


class Spec(DeclarativeBase):
    __tablename__ = "spec"

    id = Column(BIGINT, autoincrement=True, primary_key=True)
    title = Column(VARCHAR(SPEC_TITLE_LENGTH), nullable=False)

    requests = relationship("Request", back_populates="spec")
    arses = relationship("Ars", secondary=ars_spec, back_populates="specs")


class Vendor(DeclarativeBase):
    __tablename__ = "vendor"

    id = Column(BIGINT, autoincrement=True, primary_key=True)
    title = Column(VARCHAR(VENDOR_TITLE_LENGTH), nullable=False)

    autos = relationship("Auto", back_populates="vendor")


class User(DeclarativeBase):
    __tablename__ = "user"

    id = Column(BIGINT, autoincrement=True, primary_key=True)
    tg_id = Column(BIGINT, index=True, nullable=False, unique=True)
    tg_message_id = Column(BIGINT, nullable=False)
    state_id = Column(VARCHAR(STATE_ID_LENGTH), nullable=False)
    state_args = Column(JSONB, nullable=False)
    phone = Column(VARCHAR(PHONE_LENGTH), unique=True)

    callbacks = relationship("Callback", back_populates="user")
    auto = relationship("Auto", back_populates="user", uselist=False)
    ars = relationship("Ars", back_populates="user", uselist=False)


class Callback(DeclarativeBase):
    __tablename__ = "callback"

    id = Column(BIGINT, autoincrement=True, primary_key=True)
    data = Column(VARCHAR(CALLBACK_DATA_LENGTH), nullable=False)
    user_id = Column(BIGINT, ForeignKey(User.id), nullable=False)

    user = relationship(User, back_populates="callbacks")


class Auto(DeclarativeBase):
    __tablename__ = "auto"

    id = Column(BIGINT, autoincrement=True, primary_key=True)
    vendor_id = Column(BIGINT, ForeignKey(Vendor.id), nullable=False)
    year = Column(VARCHAR(YEAR_LENGTH), nullable=False)
    volume = Column(NUMERIC, nullable=False)
    user_id = Column(BIGINT, ForeignKey(User.id), nullable=False, unique=True)

    vendor = relationship(Vendor, back_populates="autos")
    user = relationship(User, back_populates="auto")
    requests = relationship("Request", back_populates="auto")
    feedbacks = relationship("Feedback", back_populates="auto")


class Ars(DeclarativeBase):
    __tablename__ = "ars"

    id = Column(BIGINT, autoincrement=True, primary_key=True)
    title = Column(VARCHAR(ARS_TITLE_LENGTH))
    description = Column(VARCHAR(DESCRIPTION_LENGTH))
    address = Column(VARCHAR(ADDRESS_LENGTH), nullable=False)
    latitude = Column(NUMERIC, nullable=False)
    longitude = Column(NUMERIC, nullable=False)
    picture = Column(VARCHAR(PICTURE_LENGTH))
    user_id = Column(BIGINT, ForeignKey(User.id), unique=True)

    user = relationship(User, back_populates="ars")
    specs = relationship(Spec, secondary=ars_spec, back_populates="arses")
    offers = relationship("Offer", back_populates="ars")
    feedbacks = relationship("Feedback", back_populates="ars")


class Registration(DeclarativeBase):
    __tablename__ = "registration"

    ars_id = Column(BIGINT, ForeignKey(Ars.id), primary_key=True)
    phone = Column(VARCHAR(PHONE_LENGTH), nullable=False, unique=True)


class Request(DeclarativeBase):
    __tablename__ = "request"

    id = Column(BIGINT, autoincrement=True, primary_key=True)
    spec_id = Column(BIGINT, ForeignKey(Spec.id), nullable=False)
    auto_id = Column(BIGINT, ForeignKey(Auto.id), nullable=False)

    spec = relationship(Spec, back_populates="requests")
    auto = relationship(Auto, back_populates="requests")
    offers = relationship("Offer", back_populates="request")


class Offer(DeclarativeBase):
    __tablename__ = "offer"

    request_id = Column(BIGINT, ForeignKey(Request.id), primary_key=True)
    ars_id = Column(BIGINT, ForeignKey(Ars.id), primary_key=True)
    cost_floor = Column(INTEGER, nullable=False)
    cost_ceil = Column(INTEGER)
    description = Column(VARCHAR(DESCRIPTION_LENGTH))

    request = relationship(Request, back_populates="offers")
    ars = relationship(Ars, back_populates="offers")


class Feedback(DeclarativeBase):
    __tablename__ = "feedback"

    auto_id = Column(BIGINT, ForeignKey(Auto.id), primary_key=True)
    ars_id = Column(BIGINT, ForeignKey(Ars.id), primary_key=True)
    stars = Column(SMALLINT, nullable=False)

    auto = relationship(Auto, back_populates="feedbacks")
    ars = relationship(Ars, back_populates="feedbacks")
