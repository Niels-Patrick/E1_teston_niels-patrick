from pathlib import Path
import chess
from realtime import List
import json
import pandas as pd
from src.data_processing.big_data.big_data_request import fetch_games_big_data
from src.data_processing.data_from_database.db_request import fetch_games_db
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv


load_dotenv()


def clean_empty(json_data: List) -> List:
    df = pd.DataFrame(json_data)

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
        df[['result', 'moves']].notna().all(axis=1) &
        (df[['result', 'moves']] != "").all(axis=1)
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
    print(f"All games with empty moves or result have been removed. {len(json_list)} games remaining.")
    json_list = clean_illegal_moves(json_list)
    print(f"All illegal games have been removed. {len(json_list)} games remaining.")

    return json_list


def save_in_database(json_list: List) -> None:
    conn = psycopg2.connect(os.getenv("DB_CONNECTION_STRING"))
    cur = conn.cursor()

    for row in json_list:
        # Converting moves list to store it as JSONB
        moves = row["moves"]
        moves_json = psycopg2.extras.Json(moves)

        cur.execute("""
                    INSERT INTO openings (name, eco, moves)
                    VALUES (%s, %s, %s)
                    """,
                    (
                        row.get('name'),
                        row.get('eco'),
                        row.get('moves')
                    ))

        cur.execute("""
                    INSERT INTO players (username, password, email, elo)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        row.get('username'),
                        row.get('password'),
                        row.get('email'),
                        row.get('elo')
                    ))

        cur.execute("""
                    INSERT INTO games (event, game_date, game_result, moves, white, black, white_elo, black_elo)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        row.get('event'),
                        row.get('date'),
                        row.get('result'),
                        moves_json,
                        row.get('white'),
                        row.get('black'),
                        row.get('white_elo'),
                        row.get('black_elo')
                    ))


def data_aggregation() -> None:
    aggregated_data = {
        "games": [],
        "openings": []
    }

    # Files
    with open("data/Carlsen.json", "r", encoding="utf-8") as f:
        json_list = json.load(f)
    json_list = clean_process(json_list)
    for data in json_list:
        aggregated_data["games"].append(data)

    # API
    with open("data/games_lichess.json", "r", encoding="utf-8") as f:
        json_list = json.load(f)
    json_list = clean_process(json_list)
    for data in json_list:
        aggregated_data["games"].append(data)

    # Database
    rows = fetch_games_db()
    json_list = clean_process(rows)
    for data in json_list:
        aggregated_data["games"].append(data)

    # Big Data
    rows = fetch_games_big_data()
    json_list = clean_process(rows)
    for data in json_list:
        aggregated_data["games"].append(data)

    # Webscraping
    with open("data/chess_openings.json", "r", encoding="utf-8") as f:
        json_list = json.load(f)
    # Cleaning illegal moves only -> empty rows cleaned in webscraping script
    print(f"Starting with {len(json_list)} games.")
    json_list = clean_illegal_moves(json_list)
    print(f"All illegal games have been removed. {len(json_list)} games remaining.")
    for data in json_list:
        aggregated_data["openings"].append(data)

    out_path = Path("data/foxchess_data").with_suffix(".json")
    out_path.write_text(
        json.dumps(
            aggregated_data,
            indent=2,
            ensure_ascii=False,
            default=lambda o: o.isoformat() if hasattr(o, "isoformat") else str(o)
            ),
        encoding="utf-8"
    )


if __name__ == "__main__":
    data_aggregation()
