"""
SQLAlchemy User model file.

This file contains the SQLAlchemy User model as well as its functions.
"""

from sqlalchemy import Column, String, Integer, ForeignKey
from dataclasses import dataclass
from src.models.players import Player


@dataclass
class User(Player):
    __tablename__ = 'users'
    id_player = Column(
        Integer,
        ForeignKey("players.id_player"),
        primary_key=True
        )
    password = Column(String(500), nullable=False)
    email = Column(String(250), nullable=False)

    __mappers_args__ = {
        "polymorphic_identity": "user"
    }
