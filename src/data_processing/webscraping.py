import time
from realtime import List
import requests
from bs4 import BeautifulSoup
import json
import chess
import re
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser


URL = "https://en.wikipedia.org/wiki/List_of_chess_openings"
HEADERS = {"User-Agent": "SchoolProjectScraper/1.0 (+niels.teston@gmail.com)"}


def can_fetch(url: str, user_agent: str="*") -> bool:
    """
    Checks if a webscraping request is allowed on a webpage.
    """
    rp = RobotFileParser()
    domain = urlparse(url).scheme + "://" + urlparse(url).netloc
    rp.set_url(domain + "/robots.txt")
    rp.read()
    return rp.can_fetch(user_agent, url)


def clean_name(name: str) -> str:
    if not name or not isinstance(name, str):
        return None

    name = name.strip()
    name = re.sub(r'^[\u2192→]\s*', '', name)  # remove arrow
    name = re.sub(r',\s*', ', ', name)

    return name if name else None


def scrape_openings() -> None:
    # Fetches the web page
    time.sleep(10)
    r = requests.get(URL, headers=HEADERS, timeout=30)
    html = r.text
    print(r.status_code)
    print(r.text[:500])

    soup = BeautifulSoup(html, "html.parser")
    content = soup.find("div", class_="mw-parser-output")
    openings = []

    for node in content.find_all(["p", "li"]):
        text = node.get_text(" ", strip=True)
        if "1." not in text:
            continue  # skip anything without moves

        # Extract ECO code if present
        eco_match = re.search(r"\(([A-E]\d{2}(?:–[A-E]?\d{2})?)\)", text)
        eco = eco_match.group(1) if eco_match else None

        # Split at the first '1.' to get name vs moves
        parts = text.split("1.", 1)
        name = parts[0].strip(" ––-:,.") if parts[0].strip() else None
        moves = "1." + parts[1].strip()  # add back the 1.

        openings.append({
            "name": name,
            "eco": eco,
            "moves": moves
        })

        cleaned_openings = []
        current_eco = None
        for entry in openings:
            name = clean_name(entry["name"])

            if not name:
                continue  # skip entries without a valid name

            if entry['eco']:
                entry['eco'] = entry['eco'].replace('\u2013', '-')

            eco = entry["eco"]
            if eco:
                current_eco = eco
            else:
                eco = current_eco

            cleaned_openings.append({
                "name": name,
                "eco": eco,
                "moves": entry["moves"]
            })

    with open("chess_openings.json", "w", encoding="utf-8") as f:
        json.dump(cleaned_openings, f, indent=2, ensure_ascii=False)

    return cleaned_openings


def clean_moves(moves: str) -> str:
    # Removing ECO garbage like (A00–A39)
    moves = re.sub(r"\([A-E]\d{2}[^)]*\)", "", moves)

    # Removing stray punctuation
    moves = moves.replace(",", " ").replace(":", " ")

    # Fixing castling
    moves = re.sub(r"0-0-0|0-0-0|0-0-0", "O-O-O", moves)
    moves = re.sub(r"0-0|0-0|0-0|0-", "O-O", moves)

    # Ensuring space before move numbers: 2.Nf3 → 2. Nf3
    moves = re.sub(r"(\d+)\.", r" \1. ", moves)

    # Fixing glued rank numbers: e52. → e5 2.
    moves = re.sub(r"([a-h])([1-8])(\d+\.)", r"\1\2 \3", moves)

    # Fixing glued pieces and ranks: Nc65. → Nc6 5.
    moves = re.sub(r"([NBRQK])([a-h]?[1-8])(\d+\.)", r"\1\2 \3", moves)

    # Collapsing whitespace
    moves = re.sub(r"\s+", " ", moves).strip()

    return moves


def convert_to_uci(san_moves: str) -> List[str]:
    """
    Converts a list of san moves to a list of uci moves.
    """
    board = chess.Board()
    uci_moves = []

    for san in san_moves.split():
        # Skips turn numbers
        if re.match(r"^\d+\.$", san):
            continue

        try:
            move = board.parse_san(san)
            uci_moves.append(move.uci())
            board.push(move)
        except ValueError:
            print(f"Skipping invalid move: {san}")

    return uci_moves


def clean_data(entry):
    # Safe copy
    name = entry.get("name")
    eco = entry.get("eco")
    moves = entry.get("moves")

    if not isinstance(name, str):
        name = ""

    # Normalizing moves to string
    if isinstance(moves, list):
        moves = " ".join(moves)
    if not isinstance(moves, str):
        moves = ""

    moves = moves.replace(",", " ").strip()

    raw_moves = moves

    # Running clean_moves if possible
    try:
        cleaned_san = clean_moves(raw_moves)
    except:
        cleaned_san = raw_moves

    # If still N° "1." then skip
    if "1." not in cleaned_san:
        return None

    # Trying to convert to uci
    try:
        uci = convert_to_uci(cleaned_san)
        if len(uci) < 2:
            return None
    except:
        return None

    return {
        "name": re.sub(r"\s+", " ", name.replace(",", ", ")).strip(),
        "eco": eco,
        "moves": uci
    }


def main():
    """
    The main function of the script.
    """
    openings = scrape_openings()
    print(f"Found {len(openings)} openings.")

    with open("data/chess_openings.json", "w", encoding="utf-8") as f:
        json.dump(openings, f, indent=2, ensure_ascii=False)
    print("Saved to chess_openings.json")

    with open("data/chess_openings.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    final = []
    for entry in data:
        cleaned = clean_data(entry)
        if cleaned:
            final.append(cleaned)

    with open("data/chess_openings.json", "w", encoding="utf-8") as f:
        json.dump(final, f, indent=2)

    print("Saved to chess_openings_cleaned.json")


if __name__ == "__main__":
    main()
