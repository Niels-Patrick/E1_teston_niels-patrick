from realtime import List
import requests
from bs4 import BeautifulSoup
import json
import chess
import re
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser


URL = "https://en.wikipedia.org/wiki/Game_of_the_Century_(chess)"
HEADERS = {"User-Agent": "SchoolProjectBot/1.0 (+niels.teston@gmail.com)"}


def convert_to_uci(san_moves: List) -> List:
    """
    Converts a list of san moves to a list of uci moves.
    """
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


def can_fetch(url: str, user_agent: str="*") -> bool:
    """
    Checks if a webscraping request is allowed on a webpage.
    """
    rp = RobotFileParser()
    rp.set_url(urljoin(URL, "/robots.txt"))
    rp.read()
    return rp.can_fetch(user_agent, url)


def clean_text(s: str) -> str:
    """
    Normalizes whitespace and strip arrows/extra markers.
    """
    s = s.replace("\xa0", " ")
    s = s.strip()
    # Removes leading arrows and odd bullet markers
    s = re.sub(r'^[\u2192\u00BB\-\->\s]+', '', s)
    # Collapses multiple spaces
    s = re.sub(r'\s+', '', s)
    return s.strip()


def parse_line_content(text: str) -> List:
    """
    Given a content snippet like
        "-> Andersen, Polish Gambit: 1.a3 a5 2.b4"
    Returns a list of (name, moves) for each 'variant' in the snippet.
    """
    results = []
    # Splits on the '->' arrow symbol or on '-> ->' sequences, but keep also
    # plain parts
    parts = [
        p.strip() for p in re.split(r'[\u2192\u00BB]|→', text) if p.strip()
        ]
    for part in parts:
        # Expected form: "Name: moves", or "Name, Subname: moves" or just
        # "Name moves"
        part = part.strip(" -–—") # Strip dashes around
        # Tries match "Name: moves"
        m = re.match(r'^(?P<name>[^:]+?)\s*:\s*(?P<moves>.+)$', part)
        if m:
            name = clean_text(m.group('name'))
            moves = clean_text(m.group('moves'))
            results.append((name, moves))
        else:
            # Fallback: splits by last occurrence of a move-like token
            # (e.g. "1." or a move)
            if "1." in part:
                idx = part.find("1.")
                name = clean_text(part[:idx].rstrip(':, '))
                moves = clean_text(part[idx:])
                results.append((name or None, moves))
            else:
                # If no clear moves, treat entire part as name (no moves)
                results.append((clean_text(part), ""))

    return results


def scrape_openings():
    """
    Main function.
    Scrapes all of the openings listed on the "List of chess openings"
    Wikipedia page.
    """
    # Politeness: Checks the Wikipedia Robots.txt
    if not can_fetch(URL, HEADERS["User-Agent"]):
        raise SystemExit("""
                         Robots.txt disallows scraping this page with your
                         user-agent. Change user-agent or respect robots.txt.
                         """)

    # Fetches the web page
    resp = requests.get(URL, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Finds the main content div
    content = soup.find("div", class_="mw-parser-output")
    if content is None:
        raise RuntimeError(
            "Could not find main content div; page structure changed."
            )

    openings = []
    current_eco = None

    # Iterates over all of mw-parser-output children
    for node in content.find_all(recursive=False):
        # Looks for headings that start with an ECO code like "A00", "B20–B99"
        # or "A00–A09"
        if node.name and node.name.startswith("h"):
            heading_text = node.get_text(" ", strip=True)
            # Look for an ECO code at beginning like "A00", "A10–A39",
            # "A00–A09", etc.
            eco_match = re.match(
                r'^([A-E]\d{2})(?:[–\u2013\u2014]\w+)?',
                heading_text
                )
            if eco_match:
                # Sets the current ECO group
                current_eco = eco_match.group(1)
                continue
            else:
                continue

        if node.name in ("p", "ul", "ol", "dl", "div"):
            text = node.get_text("\n", strip=True)
            if not text:
                continue
            # Splits into lines (some nodes contain many numbered lines)
            lines = [
                line.strip() for line in text.splitlines() if line.strip()
                ]

            for line in lines:
                # Discards lines that are just section headings such as "A00
                # Irregular Openings" already handled
                # Matches leading numbering "1." etc
                num_match = re.match(r'^\d+\.\s*(.*)$', line)
                content_part = line
                if num_match:
                    content_part = num_match.group(1)
                # Skips lines that are only arrows or only references
                content_part = content_part.strip()
                if not content_part or re.match(r'^[\[\]0-9]+$', content_part):
                    continue

                # Splits variants (->)
                entries = parse_line_content(content_part)
                for name, moves in entries:
                    if not name and not moves:
                        continue
                    # If moves is empty, tries to see if name contains moves
                    if moves == "" and re.search(r'\b1\.', name):
                        # tries to split at '1.'
                        idx = name.find('1.')
                        moves = clean_text(name[idx:])
                        name = clean_text(name[:idx].rstrip(':, '))
                    if moves:
                        openings.append({
                            "name": name,
                            "eco": current_eco,
                            "moves": moves
                        })
    return openings


def main():
    openings = scrape_openings()
    print(f"Found {len(openings)} openings.")
    with open("data/chess_openings.json", "w", encoding="utf-8") as f:
        json.dump(openings, f, indent=2, ensure_ascii=False)
    print("Saved to chess_openings.json")


if __name__ == "__main__":
    main()
