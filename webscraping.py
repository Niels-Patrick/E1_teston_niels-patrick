from realtime import List
import requests
from bs4 import BeautifulSoup
import json
import chess
import re
import time
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


def parse_line_content(text: str):
    """
    Given a content snippet like
        "-> Andersen, Polish Gambit: 1.a3 a5 2.b4"
    Returns a list of (name, moves) for each 'variant' in the snippet.
    """
    results = []
    # Splits on the '->' arrow symbol or on '-> ->' sequences, but keep also
    # plain parts
    parts = [p.strip() for p in re.split(r'[\u2192\u00BB]|→', text) if p.strip()]
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


if __name__ == "__main__":
    execute_scraping()
