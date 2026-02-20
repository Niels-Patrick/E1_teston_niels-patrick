"""
SQLAlchemy Opening model file.

This file contains the SQLAlchemy Opening model as well as its functions.
"""

from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID
from dataclasses import dataclass
from src.app.db_manager import db
from src.app.logger_manager import logger_manager


@dataclass
class Opening(db.Model):
    """SQLAlchemy Opening model"""

    __tablename__ = 'openings'
    id_opening = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
        )
    name = Column(String(250), nullable=True)
    eco = Column(String(50), nullable=False)
    moves = Column(Text, nullable=True)

    game = relationship(
        "Game",
        back_populates="opening",
        foreign_keys="Game.id_opening"
        )

    def __init__(self, name: str, eco: str, moves: list[str]):
        self.name = name
        self.eco = eco,
        self.moves = moves

    def to_json(self) -> dict:
        """
        Returns an Opening's data as JSON.
        """
        json_opening = {
            "id_opening": self.id_opening,
            "name": self.name,
            "eco": self.eco,
            "moves": self.moves
        }

        logger_manager.info("Opening's information successfully fetched")
        return json_opening


def get_openings() -> list[Opening]:
    """
    Gets a list of all of the openings.

    Returns:
        openings (list[Opening]): a list of all of the openings.
    """
    try:
        openings = db.query(Opening).all()

        return openings
    except Exception as e:
        logger_manager.error(f"Error fetching Openings in database: {str(e)}")
        raise
