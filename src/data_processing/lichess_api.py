from io import StringIO
import json
from pathlib import Path
import requests
from src.data_processing.utils import pgn_to_json


username = "Kastorcito"
BASE_URL = "https://lichess.org/api/games/user/"
params = {
    "max": 1000,
    "moves": True
}


if __name__ == "__main__":
    r = requests.get(
        f"{BASE_URL}{username}",
        params=params,
        headers={"Accept": "application/x-chess-pgn"},
        timeout=120
        )

    pgn_file = StringIO(r.text)

    json_data = pgn_to_json(pgn_file)

    out_path = Path("data/games_lichess").with_suffix(".json")
    out_path.write_text(
        json.dumps(json_data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    out_path = Path("data/pgn_lichess").with_suffix(".pgn")
    out_path.write_text(
        r.text,
        encoding="utf-8"
    )

    print(f"\n Saved {len(json_data)} games to {out_path}")
