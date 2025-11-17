"""
Player routes module.

This file contains all the routes required to fetch Player objects' data
from the database and to manage CRUD operations.
"""

import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from flask import Blueprint, Response, jsonify
from flask_jwt_extended import jwt_required
from src.models.players import get_players
from src.app.logger_manager import logger_manager
from src.models.schemas.serializer import serialize_players


# Defining a Blueprint for the Player page routes
player_management = Blueprint("player_management", __name__)

load_dotenv()

key = os.getenv("FERN_KEY")
fernet = Fernet(key)
if not fernet:
    logger_manager.error("Error fetching FERN_KEY")
    raise ValueError("FERN_KEY environment variable is not set")


@player_management.route("/", methods=["GET"])
@jwt_required()
def get_all_players() -> Response:
    """
    Gets all the Players' data from the database.
    ---
    tags:
        - Players
    security:
        - Bearer: []
    responses:
        200:
            description: Returns a list of Players and a success message.
        404:
            description: Returns an error message if no Players are found
                         in the database.
    """
    try:
        players = get_players()

        if not players:
            return jsonify(message="No players found in database."), 404

        players_dump = serialize_players(players)

        return jsonify({
            "players": players_dump,
            "message": "Players list successfully fetched from database."
            }), 200
    except Exception as e:
        logger_manager.error(f"Error while fetching players: {str(e)}")
        raise
