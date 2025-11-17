"""
Event routes module.

This file contains all the routes required to fetch Event objects' data
from the database and to manage CRUD operations.
"""

import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from flask import Blueprint, Response, jsonify
from flask_jwt_extended import jwt_required
from src.models.events import get_events
from src.app.logger_manager import logger_manager
from src.models.schemas.schemas_events import ReadEventSchema
from src.app.db_manager import db


# Defining a Blueprint for the Event page routes
event_management = Blueprint("event_management", __name__)

load_dotenv()

key = os.getenv("FERN_KEY")
fernet = Fernet(key)
if not fernet:
    logger_manager.error("Error fetching FERN_KEY")
    raise ValueError("FERN_KEY environment variable is not set")


@event_management.route("/", methods=["GET"])
@jwt_required()
def get_all_events() -> Response:
    """
    Gets all the Events' data from the database.
    ---
    tags:
        - Events
    security:
        - Bearer: []
    responses:
        200:
            description: Returns a list of Events and a success message.
        404:
            description: Returns an error message if no Events are found
                         in the database.
    """
    try:
        events = get_events()

        if not events:
            return jsonify(message="No events found in database."), 404

        events_dump = ReadEventSchema(
                session=db.session,
                many=True
            ).dump(events)

        return jsonify({
            "events": events_dump,
            "message": "Events list successfully fetched from database."
            }), 200
    except Exception as e:
        logger_manager.error(f"Error while fetching events: {str(e)}")
        raise
