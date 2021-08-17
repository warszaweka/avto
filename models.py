from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import (BIGINT, BOOLEAN, JSONB, NUMERIC,
                                            SMALLINT, VARCHAR)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.schema import Column

DeclarativeBase = declarative_base()

TITLE_LENGTH = 128
DESCRIPTION_LENGTH = 2048
ADDRESS_LENGTH = 64


class User(DeclarativeBase):
    __tablename__ = "user"

    id = Column(BIGINT, autoincrement=True, primary_key=True)
    tg_id = Column(BIGINT, index=True, nullable=False, unique=True)
    tg_message_id = Column(BIGINT, nullable=False)
    state_id = Column(VARCHAR(48), nullable=False)
    state_args = Column(JSONB, nullable=False)

    callbacks = relationship("Callback", back_populates="user")
    arses = relationship("Ars", back_populates="user")
    requests = relationship("Request", back_populates="user")
    feedbacks = relationship("Feedback", back_populates="user")


class Callback(DeclarativeBase):
    __tablename__ = "callback"

    id = Column(BIGINT, autoincrement=True, primary_key=True)
    data = Column(VARCHAR(64), nullable=False)
    user_id = Column(BIGINT, ForeignKey(User.id), nullable=False)

    user = relationship(User, back_populates="callbacks")


class Spec(DeclarativeBase):
    __tablename__ = "spec"

    id = Column(BIGINT, autoincrement=True, primary_key=True)
    title = Column(VARCHAR(32), nullable=False)

    ars_specs = relationship("ArsSpec", back_populates="spec")
    request_specs = relationship("RequestSpec", back_populates="spec")


class Ars(DeclarativeBase):
    __tablename__ = "ars"

    id = Column(BIGINT, autoincrement=True, primary_key=True)
    title = Column(VARCHAR(TITLE_LENGTH), nullable=False)
    description = Column(VARCHAR(DESCRIPTION_LENGTH), nullable=False)
    address = Column(VARCHAR(ADDRESS_LENGTH), nullable=False)
    latitude = Column(NUMERIC, nullable=False)
    longitude = Column(NUMERIC, nullable=False)
    phone = Column(VARCHAR(10), nullable=False)
    picture = Column(VARCHAR(128))
    user_id = Column(BIGINT, ForeignKey(User.id), nullable=False)

    user = relationship(User, back_populates="arses")
    ars_specs = relationship("ArsSpec", back_populates="ars")
    ars_vendors = relationship("ArsVendor", back_populates="ars")
    offers = relationship("Offer", back_populates="ars")
    feedbacks = relationship("Feedback", back_populates="ars")


class ArsSpec(DeclarativeBase):
    __tablename__ = "ars_spec"

    ars_id = Column(BIGINT, ForeignKey(Ars.id), primary_key=True)
    spec_id = Column(BIGINT, ForeignKey(Spec.id), primary_key=True)
    cost_floor = Column(BIGINT, nullable=False)
    cost_ceil = Column(BIGINT)

    ars = relationship(Ars, back_populates="ars_specs")
    spec = relationship(Spec, back_populates="ars_specs")


class Request(DeclarativeBase):
    __tablename__ = "request"

    id = Column(BIGINT, autoincrement=True, primary_key=True)
    title = Column(VARCHAR(TITLE_LENGTH), nullable=False)
    description = Column(VARCHAR(DESCRIPTION_LENGTH), nullable=False)
    phone = Column(VARCHAR(10), nullable=False)
    picture = Column(VARCHAR(128))
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

    request_id = Column(BIGINT, ForeignKey(Request.id), primary_key=True)
    ars_id = Column(BIGINT, ForeignKey(Ars.id), primary_key=True)
    cost_floor = Column(BIGINT, nullable=False)
    cost_ceil = Column(BIGINT)
    description = Column(VARCHAR(DESCRIPTION_LENGTH), nullable=False)
    winner = Column(BOOLEAN, nullable=False)

    ars = relationship(Ars, back_populates="offers")
    request = relationship(Request, back_populates="offers")


class Vendor(DeclarativeBase):
    __tablename__ = "vendor"

    id = Column(BIGINT, autoincrement=True, primary_key=True)
    title = Column(VARCHAR(32), nullable=False)

    ars_vendors = relationship("ArsVendor", back_populates="vendor")


class ArsVendor(DeclarativeBase):
    __tablename__ = "ars_vendor"

    ars_id = Column(BIGINT, ForeignKey(Ars.id), primary_key=True)
    vendor_id = Column(BIGINT, ForeignKey(Vendor.id), primary_key=True)

    ars = relationship(Ars, back_populates="ars_vendors")
    vendor = relationship(Vendor, back_populates="ars_vendors")


class Feedback(DeclarativeBase):
    __tablename__ = "feedback"

    ars_id = Column(BIGINT, ForeignKey(Ars.id), primary_key=True)
    user_id = Column(BIGINT, ForeignKey(User.id), primary_key=True)
    stars = Column(SMALLINT, nullable=False)
    title = Column(VARCHAR(TITLE_LENGTH), nullable=False)
    description = Column(VARCHAR(DESCRIPTION_LENGTH), nullable=False)

    user = relationship(User, back_populates="feedbacks")
    ars = relationship(Ars, back_populates="feedbacks")
