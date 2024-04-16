# -*- coding: utf-8 -*-
"""

"""
from datetime import datetime
from enum import Enum as PyEnum
from typing import List, Optional

from flask_login import UserMixin
from sqlalchemy import Enum, ForeignKey, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import String


class Base(DeclarativeBase):
    pass

metadata = Base.metadata

class Role(PyEnum):
    admin = "admin"
    editor = "editor"


class Access(Base):
    __tablename__ = "access"
    user_email: Mapped[str] = mapped_column(
        ForeignKey("user.email"), primary_key=True)
    tournament_id: Mapped[str] = mapped_column(
        ForeignKey("tournament.id"), primary_key=True)
    role: Mapped[Role] = mapped_column(
        Enum(Role),
        nullable=False,
        default=Role.editor,
        )

    user: Mapped["User"] = relationship(back_populates="tournaments")
    tournament: Mapped["Tournament"] = relationship(back_populates="users")


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
    tournament_id: Mapped[str] = mapped_column(ForeignKey("tournament.id"))
    hanchan_number: Mapped[int] = mapped_column(Integer)
    start_time: Mapped[Optional[datetime]]
    tournament: Mapped["Tournament"] = relationship(
        back_populates="hanchans",
        foreign_keys=[tournament_id],
        )


class Tournament(Base):
    __tablename__ = "tournament"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    our_template_id: Mapped[Optional[str]]
    title: Mapped[str]
    outdir: Mapped[Optional[str]]
    firebase_doc: Mapped[Optional[str]]
    users: Mapped[List[Access]] = relationship(back_populates="tournament")
    hanchans: Mapped[List[Hanchan]] = relationship(
       "Hanchan",
       back_populates="tournament",
    )


class User(Base, UserMixin):
    __tablename__ = "user"
    email: Mapped[str] = mapped_column(String, primary_key=True)
    live_tournament_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey(Tournament.id),)
    tournaments: Mapped[List[Access]] = relationship(back_populates="user")
    live_tournament: Mapped[Tournament] = relationship(
        "Tournament", foreign_keys=[live_tournament_id],)

    def get_id(self):
        return self.email
