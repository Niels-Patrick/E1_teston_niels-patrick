from datetime import date, timedelta
import uuid
from flask_jwt_extended import create_refresh_token, decode_token
from flask_sqlalchemy import SQLAlchemy
from src.models.events import Event
from src.models.openings import Opening
from src.models.players import get_player_by_username
from src.models.users import User
from src.models.refresh_token import RefreshToken
from src.models.schemas.schemas_players import ReadPlayerSchema
from src.models.games import Game
from src.utils.functions_routes import hash_password


def create_refresh(
        db: SQLAlchemy,
        username: str
        ) -> list[RefreshToken, uuid.UUID]:
    """
    Creates a test refresh token and stores it in the database.

    :param db: The database session to store the newly created user in.
    :type db: SQLAlchemy
    :param username: The username of the user to create a refresh token for.
    :type username: str

    :return: The newly created test refresh token and the unique UUID of the
             newly created test refresh token.
    :rtype: list[RefreshToken, uuid.UUID]
    """
    user = get_player_by_username(username)
    user_dict = ReadPlayerSchema(
            session=db.session
            ).dump(user)

    id = uuid.uuid4()

    new_refresh_token = create_refresh_token(
                    identity=str(id),
                    expires_delta=timedelta(days=7),
                    additional_claims=user_dict
                )

    refresh_token = RefreshToken(new_refresh_token)

    db.session.add(refresh_token)
    db.session.commit()

    return refresh_token, id


def create_user(db: SQLAlchemy) -> User:
    """
    Creates a test user and stores it in the database.

    :param db: The database session to store the newly created user in.
    :type db: SQLAlchemy

    :return: The newly created test user.
    :rtype: User
    """
    user = User(
        username="tuser",
        password=hash_password('password'),
        email="test.user@gmail.com",
        elo=700
    )

    db.session.add(user)
    db.session.commit()

    return user


def get_refresh_token_by_username(username: str) -> RefreshToken:
    """
    Gets a specific refresh token based on a username.

    :param username: The username of the user to find their token.
    :type username: str

    :return: The refresh token.
    :rtype: RefreshToken
    """
    tokens = RefreshToken.query.all()
    for refresh_token in tokens:
        token = decode_token(refresh_token.token, allow_expired=True)

        if token.get("username") == username:
            return refresh_token


def create_event(db: SQLAlchemy) -> Event:
    """
    Creates a test event and stores it in the database.

    :param db: The database session to store the newly created event in.
    :type db: SQLAlchemy

    :return: The newly created test event.
    :rtype: Event
    """
    event = Event(
        name="test"
    )

    db.session.add(event)
    db.session.commit()

    return event


def create_opening(db: SQLAlchemy) -> Opening:
    """
    Creates a test opening and stores it in the database.

    :param db: The database session to store the newly created opening in.
    :type db: SQLAlchemy

    :return: The newly created test opening.
    :rtype: Opening
    """
    opening = Opening(
        name="test",
        eco="test_eco",
        moves=[]
    )

    db.session.add(opening)
    db.session.commit()

    return opening


def create_game(
        db: SQLAlchemy,
        event_id: str,
        opening_id: str,
        player_id: str
        ) -> Game:
    """
    Creates a test "game" and stores it in the database.

    :param db: The database session to store the newly created game in.
    :type db: SQLAlchemy

    :return: The newly created game.
    :rtype: Game
    """
    game = Game(
        game_date=date(2000, 1, 1),
        game_result="0-1",
        moves=[],
        id_event=event_id,
        id_opening=opening_id,
        id_player_white=player_id,
        id_player_black=player_id
    )

    db.session.add(game)
    db.session.commit()

    return game
