from supabase import create_client
from dotenv import load_dotenv
import os
import psycopg2
import pandas as pd


# Charger variables d'environnement
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
connect = os.getenv("SUPABASE_CONNECT")
path = os.getenv("CHESS_FILE_PATH")

supabase = create_client(url, key)


def main():
    conn = psycopg2.connect(connect)
    cur = conn.cursor()

    chunk_size= 100000
    for i, chunk in enumerate(pd.read_csv(path, chunksize=chunk_size)):
        temp_file = f"data\\temp_files\\part_{i}.csv"
        chunk.to_csv(temp_file, index=False)

        with open(temp_file, "r", encoding="utf-8") as f:
            next(f)
            cur.copy_expert("""
                            COPY games(Event, White, Black, Result, UTCDate,
                                UTCTime, WhiteElo, BlackElo, WhiteRatingDiff,
                                BlackRatingDiff, ECO, Opening, TimeControl,
                                Termination, AN)
                            FROM STDIN
                            WITH CSV HEADER
                            """, f)

        conn.commit()
        os.remove(temp_file)
        print(f"Chunk {i} imported and file deleted.")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
