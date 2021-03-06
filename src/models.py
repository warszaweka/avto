from sqlalchemy import ForeignKey, Table
from sqlalchemy.dialects.postgresql import (BIGINT, BOOLEAN, ENUM, INTEGER,
                                            JSONB, NUMERIC, TIMESTAMP, VARCHAR)
from sqlalchemy.orm import declarative_base  # type: ignore[attr-defined]
from sqlalchemy.orm import relationship
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

FUEL_TEXT_MAP = {
    "gasoline": "Бензин",
    "diesel": "Дизель",
    "electric": "Електро",
}

ars_spec = Table(
    "ars_spec", DeclarativeBase.metadata,
    Column("ars_id", BIGINT, ForeignKey("ars.id"), primary_key=True),
    Column("spec_id", BIGINT, ForeignKey("spec.id"), primary_key=True))


class Spec(DeclarativeBase):  # type: ignore[valid-type, misc]
    __tablename__ = "spec"

    id = Column(BIGINT, autoincrement=True, primary_key=True)
    title = Column(VARCHAR(SPEC_TITLE_LENGTH), nullable=False, unique=True)

    requests = relationship("Request", back_populates="spec")
    arses = relationship("Ars", secondary=ars_spec, back_populates="specs")

    def __str__(self):
        return self.title


class Vendor(DeclarativeBase):  # type: ignore[valid-type, misc]
    __tablename__ = "vendor"

    id = Column(BIGINT, autoincrement=True, primary_key=True)
    title = Column(VARCHAR(VENDOR_TITLE_LENGTH), nullable=False, unique=True)

    autos = relationship("Auto", back_populates="vendor")

    def __str__(self):
        return self.title


class User(DeclarativeBase):  # type: ignore[valid-type, misc]
    __tablename__ = "user"

    id = Column(BIGINT, autoincrement=True, primary_key=True)
    tg_id = Column(BIGINT, index=True, nullable=False, unique=True)
    tg_message_id = Column(BIGINT, nullable=False)
    state_id = Column(VARCHAR(STATE_ID_LENGTH), nullable=False)
    state_args = Column(JSONB, nullable=False)
    phone = Column(VARCHAR(PHONE_LENGTH), unique=True)

    callbacks = relationship("Callback",
                             back_populates="user",
                             passive_deletes=True)
    auto = relationship("Auto", back_populates="user", uselist=False)
    ars = relationship("Ars", back_populates="user", uselist=False)

    def __str__(self):
        return self.phone


class Callback(DeclarativeBase):  # type: ignore[valid-type, misc]
    __tablename__ = "callback"

    id = Column(BIGINT, autoincrement=True, primary_key=True)
    data = Column(VARCHAR(CALLBACK_DATA_LENGTH), nullable=False)
    user_id = Column(BIGINT,
                     ForeignKey(User.id, ondelete="CASCADE"),
                     nullable=False)

    user = relationship(User, back_populates="callbacks")

    def __str__(self):
        return f"{self.user}/{self.data}"


class Auto(DeclarativeBase):  # type: ignore[valid-type, misc]
    __tablename__ = "auto"

    id = Column(BIGINT, autoincrement=True, primary_key=True)
    vendor_id = Column(BIGINT, ForeignKey(Vendor.id), nullable=False)
    year = Column(VARCHAR(YEAR_LENGTH), nullable=False)
    fuel = Column("fuel",
                  ENUM(*FUEL_TEXT_MAP.keys(), name="fuel"),
                  nullable=False)
    volume = Column(NUMERIC, nullable=False)
    latitude = Column(NUMERIC)
    longitude = Column(NUMERIC)
    user_id = Column(BIGINT, ForeignKey(User.id), nullable=False, unique=True)

    vendor = relationship(Vendor, back_populates="autos")
    user = relationship(User, back_populates="auto")
    requests = relationship("Request", back_populates="auto")

    def __str__(self):
        return str(self.user)


class Ars(DeclarativeBase):  # type: ignore[valid-type, misc]
    __tablename__ = "ars"

    id = Column(BIGINT, autoincrement=True, primary_key=True)
    title = Column(VARCHAR(ARS_TITLE_LENGTH), nullable=False, default="")
    description = Column(VARCHAR(DESCRIPTION_LENGTH),
                         nullable=False,
                         default="")
    address = Column(VARCHAR(ADDRESS_LENGTH), nullable=False)
    latitude = Column(NUMERIC, nullable=False)
    longitude = Column(NUMERIC, nullable=False)
    picture = Column(VARCHAR(PICTURE_LENGTH))
    user_id = Column(BIGINT, ForeignKey(User.id), unique=True)

    user = relationship(User, back_populates="ars")
    specs = relationship(Spec, secondary=ars_spec, back_populates="arses")
    offers = relationship("Offer", back_populates="ars")
    registration = relationship("Registration",
                                back_populates="ars",
                                uselist=False)
    occupations = relationship("Occupation", back_populates="ars")

    def __str__(self):
        return self.title


class Registration(DeclarativeBase):  # type: ignore[valid-type, misc]
    __tablename__ = "registration"

    ars_id = Column(BIGINT, ForeignKey(Ars.id), primary_key=True)
    phone = Column(VARCHAR(PHONE_LENGTH), nullable=False, unique=True)

    ars = relationship(Ars, back_populates="registration")

    def __str__(self):
        return self.phone


class Request(DeclarativeBase):  # type: ignore[valid-type, misc]
    __tablename__ = "request"

    id = Column(BIGINT, autoincrement=True, primary_key=True)
    spec_id = Column(BIGINT, ForeignKey(Spec.id), nullable=False)
    description = Column(VARCHAR(DESCRIPTION_LENGTH), nullable=False)
    active = Column(BOOLEAN, nullable=False, default=True)
    auto_id = Column(BIGINT, ForeignKey(Auto.id), nullable=False)

    spec = relationship(Spec, back_populates="requests")
    auto = relationship(Auto, back_populates="requests")
    offers = relationship("Offer", back_populates="request")
    occupations = relationship("Occupation", back_populates="request")

    def __str__(self):
        return f"{self.auto}/{self.spec}/{self.active}"


class Offer(DeclarativeBase):  # type: ignore[valid-type, misc]
    __tablename__ = "offer"

    request_id = Column(BIGINT, ForeignKey(Request.id), primary_key=True)
    ars_id = Column(BIGINT, ForeignKey(Ars.id), primary_key=True)
    cost_floor = Column(INTEGER, nullable=False)
    cost_ceil = Column(INTEGER)
    description = Column(VARCHAR(DESCRIPTION_LENGTH), nullable=False)
    winner = Column(BOOLEAN, nullable=False, default=False)

    request = relationship(Request, back_populates="offers")
    ars = relationship(Ars, back_populates="offers")

    def __str__(self):
        return f"{self.request}/{self.ars}"


class Occupation(DeclarativeBase):  # type: ignore[valid-type, misc]
    __tablename__ = "occupation"

    id = Column(BIGINT, autoincrement=True, primary_key=True)
    time = Column(TIMESTAMP, nullable=False)
    ars_id = Column(BIGINT, ForeignKey(Ars.id), nullable=False)
    request_id = Column(BIGINT, ForeignKey(Request.id))

    ars = relationship(Ars, back_populates="occupations")
    request = relationship(Request, back_populates="occupations")

    def __str__(self):
        return f"{self.ars}/{self.request}/{self.time}"
