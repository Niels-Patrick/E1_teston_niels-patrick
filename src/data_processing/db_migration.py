import os
from dotenv import load_dotenv
import psycopg2
import psycopg2.extras
from cryptography.fernet import Fernet
from src.data_processing.data_processing_games import data_aggregation


load_dotenv()
cipher = Fernet(os.getenv("FERN_KEY").encode())


def migration():
    conn = psycopg2.connect(os.getenv("DB_CONNECTION_STRING"))
    cur = conn.cursor()

    json_list = data_aggregation()

    username_list = []
    event_list = []
    for row in json_list["games"]:

        try:
            if row["white"] not in username_list:
                cur.execute("""
                            INSERT INTO players (username)
                            VALUES (%s)
                            """,
                            (
                                cipher.encrypt(row["white"].encode("utf-8")),
                            ))
                username_list.append(row["white"])
        except Exception as e:
            print(f"Error: {str(e)}")

        try:
            if row["black"] not in username_list:
                cur.execute("""
                            INSERT INTO players (username)
                            VALUES (%s)
                            """,
                            (
                                cipher.encrypt(row["black"].encode("utf-8")),
                            ))
                username_list.append(row["black"])
        except Exception as e:
            print(f"Error: {str(e)}")

        try:
            if row["event"] not in event_list:
                cur.execute("""
                            INSERT INTO events (name)
                            VALUES (%s)
                            """,
                            (
                                row['event'],
                            ))
                event_list.append(row["event"])
        except Exception as e:
            print(f"Error: {str(e)}")

        try:
            # Converting games moves list to store it as JSONB
            moves = row["moves"]
            moves_json = psycopg2.extras.Json(moves)

            date_str = str(row["date"])

            if "??" in date_str or not date_str:
                date_value = None
            else:
                # normalize from "2001.01.31" to "2001-01-31"
                date_value = date_str.replace(".", "-")

            cur.execute("""
                        INSERT INTO games (game_date, game_result, moves,
                                           white_elo, black_elo)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (
                            date_value,
                            row['result'],
                            moves_json,
                            row['white_elo'] or None,
                            row['black_elo'] or None,
                        ))
        except Exception as e:
            print(f"Error: {str(e)}")

        conn.commit()

    for row in json_list["openings"]:
        try:
            # Converting openings moves list to store it as JSONB
            moves = row["moves"]
            moves_json = psycopg2.extras.Json(moves)

            cur.execute("""
                        INSERT INTO openings (name, eco, moves)
                        VALUES (%s, %s, %s)
                        """,
                        (
                            row['name'],
                            row['eco'],
                            moves_json,
                        ))
        except Exception as e:
            print(f"Error: {str(e)}")

        conn.commit()

    cur.close()
    conn.close()


if __name__ == "__main__":
    migration()
