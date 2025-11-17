"""
Marshmallow Schema for Event file.

This file contains the Marshmallow Schema for the Event model.
"""

from marshmallow import EXCLUDE, fields
from src.models.events import Event
from src.models.schemas.utils import CamelCaseSQLAlchemyAutoSchema


class CreateEventSchema(CamelCaseSQLAlchemyAutoSchema):
    class Meta:
        model = Event
        load_instance = True
        unknown = EXCLUDE
        exclude = (
            "id_event",
            )

    name = fields.String(required=True)


class UpdateEventSchema(CamelCaseSQLAlchemyAutoSchema):
    class Meta:
        model = Event
        load_instance = True
        unknown = EXCLUDE
        exclude = (
            "id_event",
            )

    name = fields.String()


class ReadEventSchema(CamelCaseSQLAlchemyAutoSchema):
    class Meta:
        model = Event
        load_instance = True

    id_event = fields.UUID()
    name = fields.String()
