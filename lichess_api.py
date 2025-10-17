from io import StringIO
import json
from pathlib import Path
from typing import Dict, List
import chess
import chess.pgn
import requests


username = "Kastorcito"
BASE_URL = "https://lichess.org/api/games/user/"
params = {
    "max": 1000,
    "moves": True
}


def _game_to_dict(game: chess.pgn.Game) -> Dict[str, any]:
    headers = {key: value for key, value in game.headers.items()}

    node = game
    board = game.board()
    moves: List[Dict[str, any]] = []

    while node.variations:
        next_node = node.variation(0)
        move = next_node.move

        moves.append(board.uci(move))

        board.push(move)
        node = next_node

    result = {
        "event": headers.get("Event", "*"),
        "site": headers.get("Site", "*"),
        "date": headers.get("Date", "*"),
        "white": headers.get("White", "*"),
        "black": headers.get("Black", "*"),
        "white_elo": headers.get("WhiteElo", "*"),
        "black_elo": headers.get("BlackElo", "*"),
        "eco": headers.get("ECO", "*"),
        "moves": moves
    }
    return result


def pgn_to_json(pgn_file: chess.pgn.Game) -> List[Dict[str, any]]:
    """
    Reads all games from a pgn file and returns a list of dict as json file,
    each entry representing one game.
    """
    games: List[Dict[str, any]] = []

    while True:
        game = chess.pgn.read_game(pgn_file)
        if game is None:
            break
        games.append(_game_to_dict(game))

    return games


if __name__ == "__main__":
    r = requests.get(
        f"{BASE_URL}{username}",
        params=params,
        headers={"Accept": "application/x-chess-pgn"}
        )

    pgn_file = StringIO(r.text)

    json_data = pgn_to_json(pgn_file)

    out_path = Path("data/games_lichess").with_suffix(".json")
    out_path.write_text(
        json.dumps(json_data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    out_path = Path("data/pgn_lichess").with_suffix(".pgn")
    out_path.write_text(
        r.text,
        encoding="utf-8"
    )

    print(f"\n Saved {len(json_data)} games to {out_path}")
