"""
Tests for the Test Request model's methods and functions in the test_request
file.
"""

from flask_jwt_extended import JWTManager
import pytest
import sys
import os

from src.models.events import Event
from src.models.openings import Opening
from src.models.games import Game, get_game_by_id, get_games
from src.app.db_manager import init_db, db, database_uri
from tests.utils import create_game
from src.models.players import get_player_by_username

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


def test_get_game_by_id(client):
    test_event: Event = Event.query.filter_by(
            name='test'
        ).first()
    test_opening: Opening = Opening.query.filter_by(name='test').first()
    test_player = get_player_by_username("tuser")

    game = create_game(
            db,
            test_event.id_event,
            test_opening.id_opening,
            test_player.id_player
        )

    assert get_game_by_id(game.id_game) == game  # noqa


def test_get_all_games(client):
    games = Game.query.all()

    assert get_games() == games

    test_event: Event = Event.query.filter_by(
        name='test'
    ).first()
    test_opening: Opening = Opening.query.filter_by(
            name='test'
        ).first()

    db.session.delete(test_event)
    db.session.commit()

    db.session.delete(test_opening)
    db.session.commit()
