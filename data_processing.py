import chess
from realtime import List
import json


def check_illegal_moves(json_data: dict) -> List:
    board = chess.Board()
    illegal_moves = []
    uci_list = json_data["moves"]

    for uci in uci_list:
        move = chess.Move.from_uci(uci)

        if board.is_legal(move):
            board.push(move)
        else:
            illegal_moves.append(uci)

    if illegal_moves:
        return True
    else:
        return False


if __name__ == "__main__":
    with open("data/Carlsen.json", "r", encoding="utf-8") as f:
        json_list = json.load(f)

    illegal_games = 0
    total = len(json_list)

    for i, data in enumerate(json_list):
        if check_illegal_moves(data):
            illegal_games += 1
            del json_list[i]

    print(f"{illegal_games} illegal games detected over {total} games.")
    if illegal_games > 0:
        print(f"All illegal games have been removed. {len(json_list)} games remaining.")
