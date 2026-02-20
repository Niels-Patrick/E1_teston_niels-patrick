"""
Tests for the Opening model's methods and functions in the openings file.
"""

from flask_jwt_extended import JWTManager
import pytest
import sys
import os
from src.models.openings import Opening, get_openings
from src.app.db_manager import init_db, db, database_uri
from tests.utils import create_opening

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
    opening = create_opening(db)
    result = {
        "id_opening": opening.id_opening,
        "name": opening.name,
        "eco": opening.eco,
        "moves": opening.moves
    }

    assert opening.to_json() == result


def test_get_all_openings(client):
    openings = Opening.query.all()

    assert get_openings() == openings
