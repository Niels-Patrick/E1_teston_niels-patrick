"""
Marshmallow Schema for Opening file.

This file contains the Marshmallow Schema for the Opening model.
"""

from marshmallow import EXCLUDE, fields
from src.models.openings import Opening
from src.models.schemas.utils import CamelCaseSQLAlchemyAutoSchema


class CreateOpeningSchema(CamelCaseSQLAlchemyAutoSchema):
    class Meta:
        model = Opening
        load_instance = True
        unknown = EXCLUDE
        exclude = (
            "id_opening",
            )

    name = fields.String(required=False, allow_none=True)
    eco = fields.String(required=False, allow_none=True)
    moves = fields.String(required=True)


class UpdateOpeningSchema(CamelCaseSQLAlchemyAutoSchema):
    class Meta:
        model = Opening
        load_instance = True
        unknown = EXCLUDE
        exclude = (
            "id_opening",
            )

    name = fields.String(required=False, allow_none=True)
    eco = fields.String(required=False, allow_none=True)
    moves = fields.String()


class ReadOpeningSchema(CamelCaseSQLAlchemyAutoSchema):
    class Meta:
        model = Opening
        load_instance = True

    id_opening = fields.UUID()
    name = fields.String()
    eco = fields.String()
    moves = fields.String()
