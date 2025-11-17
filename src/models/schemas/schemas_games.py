"""
Marshmallow Schema for Game file.

This file contains the Marshmallow Schema for the Game model.
"""

from marshmallow import EXCLUDE, fields
from src.models.games import Game
from src.models.schemas.schemas_openings import ReadOpeningSchema
from src.models.schemas.schemas_events import ReadEventSchema
from src.models.schemas.schemas_players import ReadPlayerSchema
from src.models.schemas.utils import CamelCaseSQLAlchemyAutoSchema


class CreateGameSchema(CamelCaseSQLAlchemyAutoSchema):
    class Meta:
        model = Game
        load_instance = True
        include_fk = True
        unknown = EXCLUDE
        exclude = (
            "id_game",
            "event",
            "opening",
            "player_white",
            "player_black"
            )

    game_date = fields.Date(required=False, allow_none=True)
    game_result = fields.String(required=True)
    moves = fields.String(required=True)
    id_event = fields.UUID(required=False, allow_none=True)
    id_opening = fields.UUID(required=False, allow_none=True)
    id_player_white = fields.UUID(required=False, allow_none=True)
    id_player_black = fields.UUID(required=False, allow_none=True)


class UpdateGameSchema(CamelCaseSQLAlchemyAutoSchema):
    class Meta:
        model = Game
        load_instance = True
        include_relationships = True
        include_fk = True
        unknown = EXCLUDE
        exclude = (
            "id_game",
            "event",
            "opening",
            "player_white",
            "player_black"
            )

    game_date = fields.Date(required=False, allow_none=True)
    game_result = fields.String()
    moves = fields.String()
    id_event = fields.UUID(required=False, allow_none=True)
    id_opening = fields.UUID(required=False, allow_none=True)
    id_player_white = fields.UUID(required=False, allow_none=True)
    id_player_black = fields.UUID(required=False, allow_none=True)


class ReadGameSchema(CamelCaseSQLAlchemyAutoSchema):
    class Meta:
        model = Game
        load_instance = True
        include_relationships = True
        include_fk = True
        unknown = EXCLUDE

    id_game = fields.UUID()
    game_date = fields.Date()
    game_result = fields.String()
    moves = fields.String()
    id_event = fields.UUID()
    id_opening = fields.UUID()
    id_player_white = fields.UUID()
    id_player_black = fields.UUID()
    event = fields.Nested(ReadEventSchema)
    opening = fields.Nested(ReadOpeningSchema)
    player_white = fields.Nested(ReadPlayerSchema)
    player_black = fields.Nested(ReadPlayerSchema)
