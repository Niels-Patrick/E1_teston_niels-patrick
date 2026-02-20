"""
Tests for the Event model's methods and functions in the events file.
"""

from flask_jwt_extended import JWTManager
import pytest
import sys
import os
from src.models.events import Event, get_events
from src.app.db_manager import init_db, db, database_uri
from tests.utils import create_event

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

from main import create_app  # noqa


@pytest.fixture
def app():
    app = create_app()
    init_db(app.flask, database_uri)
    jwt = JWTManager(app.flask)  # noqa
    with app.flask.app_context():
        yield app.flask


@pytest.fixture
def client(app):
    return app.test_client()


def test_to_json(client):
    event = create_event(db)
    result = {
        "id_event": event.id_event,
        "name": event.name
    }

    assert event.to_json() == result


def test_get_all_events(client):
    events = Event.query.all()

    assert get_events() == events
