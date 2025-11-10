import json
from pathlib import Path
from src.data_processing.utils import pgn_to_json


if __name__ == "__main__":
    pgn_path = "data/Carlsen.pgn"

    with open(pgn_path, 'r', encoding="utf-8") as pgn_file:
        json_data = pgn_to_json(pgn_file)

    out_path = Path(pgn_path).with_suffix(".json")
    out_path.write_text(
        json.dumps(json_data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(f"\n Saved {len(json_data)} games to {out_path}")
