import json
import os
from dotenv import load_dotenv
import psycopg2
import psycopg2.extras


load_dotenv()


def migration():
    conn = psycopg2.connect(os.getenv("DB_CONNECTION_STRING"))
    cur = conn.cursor()

    with open("data/foxchess_data.json", "r", encoding="utf-8") as f:
        json_list = json.load(f)

    for row in json_list:
        # Converting openings moves list to store it as JSONB
        moves = row["openings"]["moves"]
        moves_json = psycopg2.extras.Json(moves)

        cur.execute("""
                    INSERT INTO openings (name, eco, moves)
                    VALUES (%s, %s, %s)
                    """,
                    (
                        row['openings']['name'],
                        row['openings']['eco'],
                        moves_json
                    ))

        # Converting games moves list to store it as JSONB
        moves = row["games"]["moves"]
        moves_json = psycopg2.extras.Json(moves)

        cur.execute("""
                    INSERT INTO games (event, game_date, game_result, moves, white, black, white_elo, black_elo)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        row['games']['event'],
                        row['games']['date'],
                        row['games']['result'],
                        moves_json,
                        row['games']['white'],
                        row['games']['black'],
                        row['games']['white_elo'],
                        row['games']['black_elo']
                    ))


if __name__ == "__main__":
    migration()
