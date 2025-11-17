"""
SQLAlchemy Event model file.

This file contains the SQLAlchemy Event model as well as its functions.
"""

import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from dataclasses import dataclass
from src.app.db_manager import db
from src.app.logger_manager import logger_manager
from sqlalchemy.orm import relationship


@dataclass
class Event(db.Model):
    """SQLAlchemy Event model"""

    __tablename__ = 'events'
    id_event = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(250), nullable=False)

    game = relationship(
        "Game",
        foreign_keys="Game.id_event",
        back_populates="event"
        )

    def to_json(self) -> dict:
        """
        Returns an Event's data as JSON.
        """
        json_event = {
            "id_event": self.id_event,
            "name": self.name
        }

        logger_manager.info("Event's information successfully fetched")
        return json_event


def get_events() -> list[Event]:
    """
    Gets a list of all of the events.

    Returns:
        events (list[Event]): a list of all of the events.
    """
    try:
        events = Event.query.all()

        logger_manager.info("Events successfully fetched")
        return events
    except Exception as e:
        logger_manager.error(f"Error fetching Events in database: {str(e)}")
        raise
