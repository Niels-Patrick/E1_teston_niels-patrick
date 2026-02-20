"""
Tests for the user routes.
"""

import json
import uuid
from flask_jwt_extended import JWTManager
import pytest
import sys
import os
from src.app.db_manager import init_db, database_uri
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
            f"/api/player/{user.id}",
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 200

    response = client.get(
            f"/api/player/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 404


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

    monkeypatch.setattr("src.models.user.User.query", FakeQuery())
    response = client.get(
            "/api/player/",
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 404


def test_edit_user(client):
    with open("access_token.json", "r") as json_file:
        data = json.load(json_file)

    user = {
        "username": "utest",
        "password": 'password',
        "email": "user.test@gmail.com",
        "elo": 700
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

    user["username"] = "wrong_username"
    response = client.put(
            "/api/player/",
            json=user,
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 404


def test_edit_password(client):
    with open("access_token.json", "r") as json_file:
        data = json.load(json_file)

    password_json = {
        "username": "utest",
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

    password_json["username"] = "wrong_username"
    response = client.put(
            "/api/player/edit-password",
            json=password_json,
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 404


def test_delete_user(client):
    with open("access_token.json", "r") as json_file:
        data = json.load(json_file)

    response = client.delete(
            "/api/player/utest",
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 200

    response = client.delete(
            "/api/player/utest",
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 404
