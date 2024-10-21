# -*- coding: utf-8 -*-
"""

"""
from datetime import datetime, timedelta
from enum import Enum as PyEnum
from typing import List, Optional
import os
from functools import lru_cache

from flask_login import UserMixin
from sqlalchemy import Enum, ForeignKey, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import String
from sqlalchemy.ext.hybrid import hybrid_property

from config import BASEDIR
from oauth_setup import firestore_client


class Base(DeclarativeBase):
    pass


metadata = Base.metadata


class Role(PyEnum):
    admin = "admin"
    editor = "editor"
    scorer = "scorer"


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


class Hanchan(Base):
    # we store these so that we can spot when a scorer changes the hanchan
    # times in the googlesheet
    # and then we can notify the players accordingly
    __tablename__ = "hanchan"
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    tournament_id: Mapped[int] = mapped_column(ForeignKey("tournament.id"))
    hanchan_number: Mapped[int] = mapped_column(Integer)
    start_time: Mapped[Optional[datetime]]
    tournament: Mapped["Tournament"] = relationship(
        back_populates="hanchans",
        foreign_keys=[tournament_id],
    )


class FirestoreCache:
    def __init__(self, ttl_seconds=300):
        self.cache = {}
        self.ttl = timedelta(seconds=ttl_seconds)

    def get(self, key):
        if key in self.cache:
            value, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.ttl:
                return value
        return None

    def set(self, key, value):
        self.cache[key] = (value, datetime.now())


firestore_cache = FirestoreCache()


@lru_cache(maxsize=None)
def get_tournament_status(firebase_doc):
    cached_status = firestore_cache.get(firebase_doc)
    if cached_status:
        return cached_status

    tournament_ref = firestore_client.collection("tournaments").document(firebase_doc)
    tournament_data = tournament_ref.get().to_dict()
    status = tournament_data.get("status")
    firestore_cache.set(firebase_doc, status)
    return status


class Tournament(Base):
    __tablename__ = "tournament"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    google_doc_id: Mapped[str]  # google sheet id
    title: Mapped[str]
    web_directory: Mapped[str]  # Store only the short name
    firebase_doc: Mapped[Optional[str]]
    users: Mapped[List[Access]] = relationship(back_populates="tournament")
    hanchans: Mapped[List[Hanchan]] = relationship(
        "Hanchan",
        back_populates="tournament",
    )

    @property
    def full_web_directory(self):
        return os.path.join(BASEDIR, self.web_directory)

    @hybrid_property
    def status(self):
        return get_tournament_status(self.firebase_doc)

    @status.setter
    def status(self, value):
        tournament_ref = firestore_client.collection("tournaments").document(
            self.firebase_doc
        )
        tournament_ref.update({"status": value})
        # Invalidate cache
        firestore_cache.set(self.firebase_doc, value)
        get_tournament_status.cache_clear()


class User(Base, UserMixin):
    __tablename__ = "user"
    email: Mapped[str] = mapped_column(String, primary_key=True)
    live_tournament_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(Tournament.id),
    )
    tournaments: Mapped[List[Access]] = relationship(back_populates="user")
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

    @property
    def live_tournament_role(self) -> Optional[Role]:
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
