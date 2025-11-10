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
    try:
        conn = psycopg2.connect(connect)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM games LIMIT 1000;")
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
