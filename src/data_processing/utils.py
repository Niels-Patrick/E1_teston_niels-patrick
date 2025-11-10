import re
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
        "date": headers.get("Date", "*"),
        "white": headers.get("White", "*"),
        "black": headers.get("Black", "*"),
        "result": headers.get("Result", "*"),
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


def san_to_uci(moves_san: str) -> List[str]:
    board = chess.Board()
    uci_moves = []

    moves_san = re.sub(r"\{[^}]*\}", "", moves_san)
    moves_san = re.sub(r"\d+\.(\.\.)?", "", moves_san)
    moves_san = re.sub(r"1-0|0-1|1/2-1/2|\*", "", moves_san)
    tokens = moves_san.split()

    for token in tokens:
        token = token.strip()
        if not token:
            continue

        token = re.sub(r'[?!]+$', '', token)

        try:
            move = board.parse_san(token)
            uci_moves.append(move.uci())
            board.push(move)
        except Exception as e:
            print(f"Error: {str(e)}")

    return uci_moves
