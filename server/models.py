# -*- coding: utf-8 -*-
"""
SQLAlchemy database models.

Defines the database schema using SQLAlchemy ORM classes.
Includes models for tournaments, users, access permissions,
and tournament-related data. Features hybrid properties for
computed attributes and cached properties for performance.
"""
from datetime import datetime, timedelta
from functools import cache
import os

from flask_login import UserMixin
from sqlalchemy import Enum, ForeignKey, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import String
from sqlalchemy.ext.hybrid import hybrid_property

from config import BASEDIR
from oauth_setup import firestore_client, logging, Role

_missing = object()  # sentinel object for missing values


class cached_hybrid_property(hybrid_property):
    def __get__(self, instance, owner):
        if instance is None:
            # getting the property for the class
            return self.expr(owner)
        else:
            # getting the property for an instance
            name = self.fget.__name__
            value = instance.__dict__.get(name, _missing)
            if value is _missing:
                value = self.fget(instance)
                instance.__dict__[name] = value
            return value


class Base(DeclarativeBase):
    pass


metadata = Base.metadata


class Access(Base):
    __tablename__ = "access"
    user_email: Mapped[str] = mapped_column(ForeignKey("user.email"), primary_key=True)
    tournament_id: Mapped[int] = mapped_column(
        ForeignKey("tournament.id"), primary_key=True
    )
    role: Mapped[Role] = mapped_column(
        Enum(Role),
        nullable=False,
        default=Role.editor,
    )

    user: Mapped["User"] = relationship(back_populates="tournaments")
    tournament: Mapped["Tournament"] = relationship(back_populates="users")

    def __init__(self, user_email, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_email = user_email.lower()


class Tournament(Base):
    __tablename__ = "tournament"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    google_doc_id: Mapped[str]
    title: Mapped[str]
    web_directory: Mapped[str]
    firebase_doc: Mapped[str | None]
    users: Mapped[list[Access]] = relationship(back_populates="tournament")
    past_data: Mapped[list["PastTournamentData"]] = relationship(
        back_populates="tournament", uselist=False
    )
    players: Mapped[list["TournamentPlayer"]] = relationship(
        back_populates="tournament"
    )

    @hybrid_property
    def full_web_directory(self):
        return os.path.join(BASEDIR, self.web_directory)

    @cached_hybrid_property
    def status(self):
        tournament_ref = firestore_client.collection("tournaments").document(
            self.firebase_doc
        )
        tournament_data = tournament_ref.get().to_dict()
        if tournament_data is None:
            return "past" if self.past_data else None
        return tournament_data.get("status")


class User(Base, UserMixin):
    __tablename__ = "user"
    email: Mapped[str] = mapped_column(String, primary_key=True)
    live_tournament_id: Mapped[int | None] = mapped_column(
        ForeignKey(Tournament.id),
    )
    tournaments: Mapped[list[Access]] = relationship(back_populates="user")
    live_tournament: Mapped[Tournament] = relationship(
        "Tournament",
        foreign_keys=[live_tournament_id],
    )

    def get_id(self):
        return self.email

    def get_tournaments(self, session):
        return (
            session.query(Tournament)
            .join(Access)
            .filter(Access.user_email == self.email)
            .all()
        )

    @hybrid_property
    def live_tournament_role(self) -> Role | None:
        if not self.live_tournament:
            return None
        access = next(
            (a for a in self.tournaments if a.tournament_id == self.live_tournament.id),
            None,
        )
        return access.role if access else None

    def __init__(self, email, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.email = email.lower()


class PastTournamentData(Base):
    __tablename__ = "past_tournament_data"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tournament_id: Mapped[int] = mapped_column(ForeignKey("tournament.id"))
    data: Mapped[str]  # JSON string containing all tournament data
    archived_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    tournament: Mapped["Tournament"] = relationship(back_populates="past_data")


class ArchivedPlayer(Base):
    __tablename__ = "archived_player"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str]
    # Additional fields that could help with matching:
    country: Mapped[str | None]
    ema_id: Mapped[str | None]

    tournament_appearances: Mapped[list["TournamentPlayer"]] = relationship(
        back_populates="player"
    )


class TournamentPlayer(Base):
    __tablename__ = "tournament_player"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tournament_id: Mapped[int] = mapped_column(ForeignKey("tournament.id"))
    player_id: Mapped[int] = mapped_column(ForeignKey("archived_player.id"))
    seating_id: Mapped[str]
    registration_id: Mapped[str]

    tournament: Mapped["Tournament"] = relationship(back_populates="players")
    player: Mapped["ArchivedPlayer"] = relationship(
        back_populates="tournament_appearances"
    )
    results: Mapped[list["Hanchan"]] = relationship(back_populates="player")


class Hanchan(Base):
    __tablename__ = "hanchan"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tournament_id: Mapped[int] = mapped_column(ForeignKey("tournament.id"))
    player_id: Mapped[int] = mapped_column(ForeignKey("tournament_player.id"))
    hanchan_number: Mapped[int]
    table_number: Mapped[str]
    seat: Mapped[int]
    points: Mapped[int]
    placement: Mapped[int]
    chombo: Mapped[int | None]

    tournament: Mapped["Tournament"] = relationship()
    player: Mapped["TournamentPlayer"] = relationship(back_populates="results")
