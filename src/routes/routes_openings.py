"""
Openings routes module.

This file contains all the routes required to fetch Opening objects' data
from the database and to manage CRUD operations.
"""

import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from flask import Blueprint, Response, jsonify
from flask_jwt_extended import jwt_required
from src.models.openings import get_openings
from src.app.logger_manager import logger_manager
from src.models.schemas.schemas_openings import ReadOpeningSchema
from src.app.db_manager import db


# Defining a Blueprint for the Opening page routes
opening_management = Blueprint("opening_management", __name__)

load_dotenv()

key = os.getenv("FERN_KEY")
fernet = Fernet(key)
if not fernet:
    logger_manager.error("Error fetching FERN_KEY")
    raise ValueError("FERN_KEY environment variable is not set")


@opening_management.route("/", methods=["GET"])
@jwt_required()
def get_all_openings() -> Response:
    """
    Gets all the Openings' data from the database.
    ---
    tags:
        - Openings
    security:
        - Bearer: []
    responses:
        200:
            description: Returns a list of Openings and a success message.
        404:
            description: Returns an error message if no Openings are found
                         in the database.
    """
    try:
        openings = get_openings()

        if not openings:
            return jsonify(message="No openings found in database."), 404

        openings_dump = ReadOpeningSchema(
                session=db.session,
                many=True
            ).dump(openings)

        return jsonify({
            "openings": openings_dump,
            "message": "Openings list successfully fetched from database."
            }), 200
    except Exception as e:
        logger_manager.error(f"Error while fetching openings: {str(e)}")
        raise
