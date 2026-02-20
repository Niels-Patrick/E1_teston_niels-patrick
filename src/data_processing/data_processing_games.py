from pathlib import Path
import chess
from realtime import List
import json
import pandas as pd
from src.data_processing.big_data.big_data_request import fetch_games_big_data
from src.data_processing.data_from_database.db_request import fetch_games_db
from dotenv import load_dotenv


load_dotenv()


def clean_empty(json_data: List) -> List:
    df = pd.DataFrame(json_data)

    for key, row in df.iterrows():
        if key in [
            "event",
            "date",
            "white",
            "black",
            "result",
            "white_elo",
            "black_elo",
            "eco",
            "moves"
        ]:
            return []

    df = df[[
        "event",
        "date",
        "white",
        "black",
        "result",
        "white_elo",
        "black_elo",
        "eco",
        "moves"
    ]]

    df = df[
        df[[
            'event',
            'white',
            'black',
            'result',
            'white_elo',
            'black_elo',
            'eco',
            'moves'
        ]].notna().all(axis=1) &
        (df[[
            'event',
            'white',
            'black',
            'result',
            'white_elo',
            'black_elo',
            'eco',
            'moves'
        ]] != "").all(axis=1)
    ]

    data = df.to_dict(orient="records")

    return data


def clean_illegal_moves(json_data: List) -> List:
    indexes_list = []

    for i, data in enumerate(json_data):
        uci_list = data["moves"]
        board = chess.Board()
        illegal_moves = []

        for uci in uci_list:
            move = chess.Move.from_uci(uci)

            if board.is_legal(move):
                board.push(move)
            else:
                illegal_moves.append(uci)
                indexes_list.append(i)

    for index in sorted(indexes_list, reverse=True):
        del json_data[index]

    return json_data


def clean_process(json_list: List) -> List:
    print(f"Starting with {len(json_list)} games.")
    json_list = clean_empty(json_list)
    if json_list == []:
        return []

    print(f"All games with empty moves or result have been removed. {len(json_list)} games remaining.")  # noqa

    json_list = clean_illegal_moves(json_list)
    print(f"All illegal games have been removed. {len(json_list)} games remaining.")  # noqa

    return json_list


def data_aggregation() -> None:
    aggregated_data = {
        "games": [],
        "openings": []
    }

    # Files
    with open("data/Carlsen.json", "r", encoding="utf-8") as f:
        json_list = json.load(f)
    json_list = clean_process(json_list)
    if json_list != []:
        for data in json_list:
            aggregated_data["games"].append(data)

    # API
    with open("data/games_lichess.json", "r", encoding="utf-8") as f:
        json_list = json.load(f)
    json_list = clean_process(json_list)
    if json_list != []:
        for data in json_list:
            aggregated_data["games"].append(data)

    # Database
    rows = fetch_games_db()
    json_list = clean_process(rows)
    if json_list != []:
        for data in json_list:
            aggregated_data["games"].append(data)

    # Big Data
    rows = fetch_games_big_data()
    json_list = clean_process(rows)
    if json_list != []:
        for data in json_list:
            aggregated_data["games"].append(data)

    # Webscraping
    with open("data/chess_openings.json", "r", encoding="utf-8") as f:
        json_list = json.load(f)
    # Cleaning illegal moves only -> empty rows cleaned in webscraping script
    print(f"Starting with {len(json_list)} games.")
    json_list = clean_illegal_moves(json_list)
    print(f"All illegal games have been removed. {len(json_list)} games remaining.")  # noqa
    if json_list != []:
        for data in json_list:
            aggregated_data["openings"].append(data)

    out_path = Path("data/foxchess_data").with_suffix(".json")
    out_path.write_text(
        json.dumps(
            aggregated_data,
            indent=2,
            ensure_ascii=False,
            default=lambda o: o.isoformat() if hasattr(o, "isoformat") else str(o)  # noqa
            ),
        encoding="utf-8"
    )


if __name__ == "__main__":
    data_aggregation()
