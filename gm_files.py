import json
from pathlib import Path
from typing import Dict, List
import chess
import chess.pgn

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


def pgn_to_json(pgn_path: str) -> List[Dict[str, any]]:
    """
    Reads all games from a pgn file and returns a list of dict as json file,
    each entry representing one game.
    """
    games: List[Dict[str, any]] = []

    with open(pgn_path, encoding="utf-8") as f:
        while True:
            game = chess.pgn.read_game(f)
            if game is None:
                break
            games.append(_game_to_dict(game))

    return games


if __name__ == "__main__":
    pgn_path = "data/Carlsen.pgn"

    json_data = pgn_to_json(pgn_path)

    out_path = Path(pgn_path).with_suffix(".json")
    out_path.write_text(
        json.dumps(json_data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(f"\n Saved {len(json_data)} games to {out_path}")
