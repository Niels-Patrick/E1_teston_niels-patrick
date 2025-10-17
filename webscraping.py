from realtime import List
import requests
from bs4 import BeautifulSoup
import re
import chess


url = "https://en.wikipedia.org/wiki/Game_of_the_Century_(chess)"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/116.0.0.0 Safari/537.36"
}


def convert_to_uci(san_moves: List) -> List:
    board = chess.Board()
    uci_moves = []

    for san in san_moves:
        try:
            move = board.parse_san(san)
            uci_moves.append(move.uci())
            board.push(move)
        except ValueError:
            print(f"Skipping invalid move: {san}")

    return uci_moves


def execute_scraping() -> List:
    url = "https://www.pgnmentor.com/players/Mikenas/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find the script tag containing the PGN data
    script_tag = soup.find("script", text=re.compile("var games ="))

    # Extract the PGN data using a regular expression
    pgn_data = re.search(r"var games = (\[.*?\]);", script_tag.string, re.DOTALL).group(1)

    # Clean up the PGN data
    pgn_data = pgn_data.replace("'", '"')  # Replace single quotes with double quotes for valid JSON
    pgn_data = pgn_data.replace("},", "},\n")  # Add newlines for better readability

    san_moves = []

    for p in pgn_data["moves"]:
        san_moves.append(p)

    return convert_to_uci(san_moves)


if __name__ == "__main__":
    print(execute_scraping())
