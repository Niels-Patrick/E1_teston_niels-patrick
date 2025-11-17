"""
Game routes module.

This file contains all the routes required to fetch Game objects' data
from the database and to manage CRUD operations.
"""

import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from flask import Blueprint, Response, jsonify
from flask_jwt_extended import jwt_required
from src.models.games import get_games
from src.app.logger_manager import logger_manager
from src.models.schemas.schemas_games import ReadGameSchema
from src.app.db_manager import db


# Defining a Blueprint for the Game page routes
game_management = Blueprint("game_management", __name__)

load_dotenv()

key = os.getenv("FERN_KEY")
fernet = Fernet(key)
if not fernet:
    logger_manager.error("Error fetching FERN_KEY")
    raise ValueError("FERN_KEY environment variable is not set")


@game_management.route("/", methods=["GET"])
@jwt_required()
def get_all_games() -> Response:
    """
    Gets all the Games' data from the database.
    ---
    tags:
        - Games
    security:
        - Bearer: []
    responses:
        200:
            description: Returns a list of Games and a success message.
        404:
            description: Returns an error message if no Games are found
                         in the database.
    """
    try:
        games = get_games()

        if not games:
            return jsonify(message="No games found in database."), 404

        games_dump = ReadGameSchema(
                session=db.session,
                many=True
            ).dump(games)

        return jsonify({
            "games": games_dump,
            "message": "Games list successfully fetched from database."
            }), 200
    except Exception as e:
        logger_manager.error(f"Error while fetching games: {str(e)}")
        raise
