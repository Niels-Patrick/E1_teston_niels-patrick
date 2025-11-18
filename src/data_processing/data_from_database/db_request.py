from typing import List
from supabase import create_client
from dotenv import load_dotenv
import os
import psycopg2
import psycopg2.extras
from src.data_processing.utils import san_to_uci


load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
connect = os.getenv("SUPABASE_CONNECT")

supabase = create_client(url, key)


def fetch_games_db() -> List:
    """
    Executes extraction request from the Supabase (PostgreSQL) database.

    There is only one table in the Supabase database: games.

    The selected fields are the ones necessary to prepare the dataset for the
    model training.

    The selected fields are:
        - event: the name of the event or the type of the game.
        - utcdate: the date of the game.
        - white: name of the white player.
        - black: name of the black player.
        - result: the result of the game (who won and lost).
        - whiteelo: the white player's elo (at the time the game happened).
        - blackelo: the black player's elo (at the time the game happened).
        - eco: the ECO number of the game's opening.
        - an: the entire game's moves in SAN notation.

    Returns:
        rows (list[dict]): A list of dicts containing all games' data (one
                           game per dict).
    """
    try:
        conn = psycopg2.connect(connect)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
                    SELECT event, utcdate, white, black, result, whiteelo,
                           blackelo, eco, an
                    FROM games;
                    """)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        rows = [dict(row) for row in rows]

        rename_keys = {
            "utcdate": "date",
            "whiteelo": "white_elo",
            "blackelo": "black_elo",
            "an": "moves"
        }

        for row in rows:
            for old, new in rename_keys.items():
                if old in row:
                    row[new] = row.pop(old)

            row['moves'] = san_to_uci(row['moves'])

        return rows
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    rows = fetch_games_db()
