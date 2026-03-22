"""
Tests for the user routes.
"""

from datetime import timedelta
import json
import uuid
from flask_jwt_extended import JWTManager, create_access_token
import pytest
import sys
import os
from src.app.db_manager import init_db, database_uri, db
from src.models.players import Player, get_player_by_username

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


def test_add_user(client):
    with open("access_token.json", "r") as json_file:
        data = json.load(json_file)

    user = {
        "username": "utest",
        "password": 'password',
        "email": "user.test@gmail.com",
        "elo": 700
    }

    response = client.post(
            "/api/player/",
            json=user,
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 200

    response = client.post(
            "/api/player/",
            json={},
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 400

    user["username"] = "tuser"
    response = client.post(
            "/api/player/",
            json=user,
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 409


def test_get_a_user(client):
    with open("access_token.json", "r") as json_file:
        data = json.load(json_file)

    user = get_player_by_username("utest")
    response = client.get(
            f"/api/player/{user.id_player}",
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 200

    response = client.get(
            f"/api/player/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 404

    user = Player.query.filter_by(username="utest").first()
    db.session.delete(user)
    db.session.commit()


def test_get_users_list(client, monkeypatch):
    class FakeQuery:
        def all(self):
            return []

    with open("access_token.json", "r") as json_file:
        data = json.load(json_file)

    response = client.get(
            "/api/player/",
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 200

    monkeypatch.setattr("src.models.players.Player.query", FakeQuery())
    response = client.get(
            "/api/player/",
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 404


def test_edit_user(client):
    response = client.post(
        "/api/login/",
        json={
            "username": "tuser",
            "password": "password"
        }
    )

    # Saving access token in json file for routes tests
    data = response.get_json()
    token = {
            "access_token": data["access_token"]
        }
    with open("access_token.json", "w") as json_file:
        json.dump(token, json_file)
    with open("access_token.json", "r") as json_file:
        data = json.load(json_file)

    user = {
        "username": "tuser",
        "password": 'password',
        "email": "test.user@gmail.com",
        "elo": 800
    }

    response = client.put(
            "/api/player/",
            json=user,
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 200

    response = client.put(
            "/api/player/",
            json={},
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 400

    access_token = create_access_token(
            identity=str(uuid.uuid4()),
            expires_delta=timedelta(minutes=15),
            additional_claims=user
            )
    response = client.put(
            "/api/player/",
            json=user,
            headers={"Authorization": f"Bearer {access_token}"}
        )
    assert response.status_code == 404


def test_edit_password(client):
    with open("access_token.json", "r") as json_file:
        data = json.load(json_file)

    password_json = {
        "username": "tuser",
        "password": "newPassword",
        "old_password": "password"
    }

    response = client.put(
            "/api/player/edit-password",
            json=password_json,
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 200

    response = client.put(
            "/api/player/edit-password",
            json={},
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 400

    user = {
        "username": "tuser",
        "password": 'password',
        "email": "test.user@gmail.com",
        "elo": 800
    }
    access_token = create_access_token(
            identity=str(uuid.uuid4()),
            expires_delta=timedelta(minutes=15),
            additional_claims=user
            )
    response = client.put(
            "/api/player/edit-password",
            json=password_json,
            headers={"Authorization": f"Bearer {access_token}"}
        )
    assert response.status_code == 404


def test_delete_user(client):
    response = client.post(
        "/api/login/",
        json={
            "username": "tuser",
            "password": "newPassword"
        }
    )

    # Saving access token in json file for routes tests
    data = response.get_json()
    token = {
            "access_token": data["access_token"]
        }
    with open("access_token.json", "w") as json_file:
        json.dump(token, json_file)
    with open("access_token.json", "r") as json_file:
        data = json.load(json_file)

    response = client.delete(
            "/api/player/",
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 200

    response = client.delete(
            "/api/player/",
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 404
