from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base


class City(Base):
    __tablename__ = "city"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    day: Mapped[int] = mapped_column(default=1)


class Neighborhood(Base):
    __tablename__ = "neighborhoods"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    x: Mapped[int]
    y: Mapped[int]


class Building(Base):
    __tablename__ = "buildings"
    id: Mapped[int] = mapped_column(primary_key=True)
    kind: Mapped[str] = mapped_column(String(20))
    name: Mapped[str] = mapped_column(String(100))
    x: Mapped[int]
    y: Mapped[int]
    neighborhood_id: Mapped[int] = mapped_column(ForeignKey("neighborhoods.id"))
    is_open: Mapped[bool] = mapped_column(default=True)
    money: Mapped[int] = mapped_column(default=1000)


class Resident(Base):
    __tablename__ = "residents"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    age: Mapped[int]
    gender: Mapped[str] = mapped_column(String(10))
    job: Mapped[str] = mapped_column(String(50))
    traits: Mapped[str] = mapped_column(String(100))
    home_id: Mapped[int] = mapped_column(ForeignKey("buildings.id"))
    workplace_id: Mapped[int | None] = mapped_column(ForeignKey("buildings.id"), nullable=True)
    partner_id: Mapped[int | None] = mapped_column(nullable=True)
    alive: Mapped[bool] = mapped_column(default=True)


class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(primary_key=True)
    day: Mapped[int]
    kind: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(Text)