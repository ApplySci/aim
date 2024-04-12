# -*- coding: utf-8 -*-
"""

"""
import enum
from typing import List, Optional


from flask_login import UserMixin
from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import String


class Base(DeclarativeBase):
    pass

metadata = Base.metadata

class RoleEnum(enum.Enum):
    admin = "admin"
    editor = "editor"

Role: RoleEnum = Enum(
    RoleEnum,
    name="roles",
    create_constraint=True,
    metadata=Base.metadata,
    validate_strings=True,
    )


class Access(Base):
    __tablename__ = "access"
    user_email: Mapped[str] = mapped_column(
        ForeignKey("user.email"), primary_key=True)
    tournament_id: Mapped[str] = mapped_column(
        ForeignKey("tournament.id"), primary_key=True)
    role: Mapped[str] = mapped_column(Role, nullable=False)

    user: Mapped["User"] = relationship(back_populates="tournaments")
    tournament: Mapped["Tournament"] = relationship(back_populates="users")


class Tournament(Base):
    __tablename__ = "tournament"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str]
    users: Mapped[List[Access]] = relationship(back_populates="tournament")


class User(Base, UserMixin):
    __tablename__ = "user"
    email: Mapped[str] = mapped_column(String, primary_key=True)
    live_tournament_id: Mapped[Optional[str]] = mapped_column(ForeignKey(Tournament.id))
    tournaments: Mapped[List[Access]] = relationship(back_populates="user")
    live_tournament: Mapped[Tournament] = relationship(
        "Tournament", foreign_keys=[live_tournament_id],)

    def get_id(self):
        return self.email
