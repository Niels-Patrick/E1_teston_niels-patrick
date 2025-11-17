"""
User routes module.

This file contains all the routes required to fetch User objects' data
from the database and to manage CRUD operations.
"""

import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from flask import Blueprint, Response, jsonify
from flask_jwt_extended import jwt_required
from src.app.logger_manager import logger_manager
from src.models.players import get_players
from src.models.schemas.serializer import serialize_users


# Defining a Blueprint for the User page routes
user_management = Blueprint("user_management", __name__)

load_dotenv()

key = os.getenv("FERN_KEY")
fernet = Fernet(key)
if not fernet:
    logger_manager.error("Error fetching FERN_KEY")
    raise ValueError("FERN_KEY environment variable is not set")


@user_management.route("/", methods=["GET"])
@jwt_required()
def get_all_users() -> Response:
    """
    Gets all the Users' data from the database.
    ---
    tags:
        - Users
    security:
        - Bearer: []
    responses:
        200:
            description: Returns a list of Users and a success message.
        404:
            description: Returns an error message if no Users are found
                         in the database.
    """
    try:
        users = get_players()

        if not users:
            return jsonify(message="No users found in database."), 404

        users_dump = serialize_users(users)

        return jsonify({
            "users": users_dump,
            "message": "Users list successfully fetched from database."
            }), 200
    except Exception as e:
        logger_manager.error(f"Error while fetching users: {str(e)}")
        raise
