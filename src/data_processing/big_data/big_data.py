import csv
from datetime import datetime
import uuid
from cassandra.cluster import Cluster

cluster = Cluster(['127.0.0.1'])
session = cluster.connect('foxchess')
path = "D:\\Niels-Patrick\\Documents\\Etudes et Formations\\Simplon\\FoxChess\\archive\\chess_games.csv"


with open(path, newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        utc_date = row['UTCDate']
        formatted_date = datetime.strptime(utc_date, '%Y.%m.%d').date()
        white_elo_int = int(row['WhiteElo'])
        black_elo_int = int(row['BlackElo'])
        value = row['WhiteRatingDiff'].strip()
        white_rating_diff_float = float(value) if value else 0.0
        value = row['BlackRatingDiff'].strip()
        black_rating_diff_float = float(value) if value else 0.0

        session.execute(
            """
            INSERT INTO chess_games (
                id,
                event,
                white,
                black,
                result,
                utcdate,
                utctime,
                whiteelo,
                blackelo,
                whiteratingdiff,
                blackratingdiff,
                eco,
                opening,
                timecontrol,
                termination,
                an
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """,
            (
                uuid.uuid4(),
                row['Event'],
                row['White'],
                row['Black'],
                row['Result'],
                formatted_date,
                row['UTCTime'],
                white_elo_int,
                black_elo_int,
                white_rating_diff_float,
                black_rating_diff_float,
                row['ECO'],
                row['Opening'],
                row['TimeControl'],
                row['Termination'],
                row['AN']
            )
        )
