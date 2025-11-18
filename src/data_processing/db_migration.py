import os
import re
from dotenv import load_dotenv
import psycopg2
import psycopg2.extras
from psycopg2 import IntegrityError
from cryptography.fernet import Fernet
from src.data_processing.data_processing_games import data_aggregation


load_dotenv()
cipher = Fernet(os.getenv("FERN_KEY").encode())


def migration():
    conn = psycopg2.connect(os.getenv("DB_CONNECTION_STRING"))
    cur = conn.cursor()

    json_list = data_aggregation()

    opening_cache = {}

    for row in json_list["openings"]:
        eco_raw = row["eco"].strip()

        # Skip grouped ECO codes like "A00-A09"
        if not re.match(r"^[A-E][0-9]{2}$", eco_raw):
            print(f"Skipping grouped ECO code: {eco_raw}")
            continue

        eco = eco_raw

        # already cached?
        if eco in opening_cache:
            continue  # nothing to do

        moves_json = psycopg2.extras.Json(row["moves"])

        try:
            cur.execute("""
                INSERT INTO openings (name, eco, moves)
                VALUES (%s, %s, %s)
                ON CONFLICT (eco) DO NOTHING
                RETURNING id_opening;
            """, (row["name"], eco, moves_json))

            result = cur.fetchone()

            if result is not None:
                opening_id = result[0]
            else:
                # conflict happened → fetch existing record
                cur.execute("SELECT id_opening FROM openings WHERE eco = %s", (eco,))
                existing = cur.fetchone()

                if existing is None:
                    raise Exception(f"Opening '{eco}' exists but can't be retrieved!")

                opening_id = existing[0]

        except IntegrityError:
            conn.rollback()
            # retry select after rollback
            cur.execute("SELECT id_opening FROM openings WHERE eco = %s", (eco,))
            opening_id = cur.fetchone()[0]

        # ALWAYS fill cache
        opening_cache[eco] = opening_id

        conn.commit()

    event_cache = {}
    player_white_cache = {}
    player_black_cache = {}
    for row in json_list["games"]:
        try:
            # White player
            if row["white"] in player_white_cache:
                player_white_id = player_white_cache[row["white"]]
            else:
                cur.execute("""
                    INSERT INTO players (username)
                    VALUES (%s)
                    ON CONFLICT (username) DO NOTHING
                    RETURNING id_player
                """, (row["white"],))
                res = cur.fetchone()
                if res:
                    player_white_id = res[0]
                else:
                    # fetch existing
                    cur.execute("SELECT id_player FROM players WHERE username = %s", (row["white"],))
                    player_white_id = cur.fetchone()[0]

                player_white_cache[row["white"]] = player_white_id  # ✅ cache it
        except Exception as e:
            print(f"Error while inserting white players: {str(e)}")
        
        conn.commit()

        try:
            # Black player
            if row["black"] in player_black_cache:
                player_black_id = player_black_cache[row["black"]]
            else:
                cur.execute("""
                    INSERT INTO players (username)
                    VALUES (%s)
                    ON CONFLICT (username) DO NOTHING
                    RETURNING id_player
                """, (row["black"],))
                res = cur.fetchone()
                if res:
                    player_black_id = res[0]
                else:
                    # fetch existing
                    cur.execute("SELECT id_player FROM players WHERE username = %s", (row["black"],))
                    player_black_id = cur.fetchone()[0]

                player_black_cache[row["black"]] = player_black_id  # ✅ cache it
        except Exception as e:
            print(f"Error while inserting black players: {str(e)}")

        conn.commit()

        try:
            if row["event"] in event_cache:
                event_id = event_cache[row["event"]]
            else:
                cur.execute("""
                            INSERT INTO events (name)
                            VALUES (%s)
                            RETURNING id_event;
                            """,
                            (
                                row['event'],
                            ))
                event_id = cur.fetchone()[0]
        except IntegrityError:
            conn.rollback()   # MUST rollback since the transaction is broken

            # Fetch the existing row
            cur.execute("SELECT id_event FROM events WHERE name = %s", (row["event"],))
            event_row = cur.fetchone()

            if event_row is None:
                raise Exception(f"Event '{row['event']}' exists but cannot be retrieved!")
            event_id = event_row[0]

        conn.commit()

        try:
            print(json_list["games"][0])
            print(type(json_list["games"][0]))

            # Converting games moves list to store it as JSONB
            moves = row["moves"]
            moves_json = psycopg2.extras.Json(moves)

            date_str = str(row["date"])

            if "??" in date_str or not date_str:
                date_value = None
            else:
                # normalize from "2001.01.31" to "2001-01-31"
                date_value = date_str.replace(".", "-")

            opening_id = opening_cache.get(row["eco"])  # maps ECO → opening_id

            cur.execute("""
                        INSERT INTO games (game_date, game_result, moves,
                                           white_elo, black_elo, id_event,
                                           id_opening, id_player_white,
                                           id_player_black)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            date_value,
                            row['result'],
                            moves_json,
                            row['white_elo'] or None,
                            row['black_elo'] or None,
                            event_id,
                            opening_id,
                            player_white_id,
                            player_black_id
                        ))
        except Exception as e:
            print(f"Error: {str(e)}")

        conn.commit()

    cur.close()
    conn.close()


if __name__ == "__main__":
    migration()
