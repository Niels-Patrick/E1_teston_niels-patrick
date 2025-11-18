from cassandra.cluster import Cluster
from src.data_processing.utils import san_to_uci

cluster = Cluster(['localhost'], port=9042)
session = cluster.connect('foxchess')


def fetch_games_big_data() -> list[dict]:
    """
    Executes extraction request from the Cassandra database.

    There is only one table in the Cassandra database: chess_games.

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
        rows = session.execute('''SELECT event, utcdate, white, black, result,
                                         whiteelo, blackelo, eco, an
                                  FROM chess_games;
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
