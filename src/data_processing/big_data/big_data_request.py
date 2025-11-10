from cassandra.cluster import Cluster
from src.data_processing.utils import san_to_uci

cluster = Cluster(['127.0.0.1'])
session = cluster.connect('foxchess')


def fetch_games_big_data():
    try:
        rows = session.execute('''SELECT *
                                    FROM chess_games
                                    LIMIT 1000
                                    ALLOW FILTERING;
                                ''')

        rows = [dict(row._asdict()) for row in rows]

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
    rows = fetch_games_big_data()
