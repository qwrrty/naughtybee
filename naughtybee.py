#! /usr/bin/env python3

import argparse
import json
import re

from html.parser import HTMLParser
from pprint import pprint

import requests


SPELLINGBEE_URL = "https://www.nytimes.com/puzzles/spelling-bee"
NAUGHTY_WORDS_FILE = "wordlist.txt"


class SpellingBeeScraper(HTMLParser):
    """A dumb HTML scraper for extracting the window.gameData from a Spelling Bee game."""
    in_script: bool = False
    gamedata = None

    def handle_starttag(self, tag, attrs):
        if tag == "script" and ("type", "text/javascript") in attrs:
            self.in_script = True

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_script = False

    def handle_data(self, data):
        if self.in_script:
            if data.startswith("window.gameData = "):
                self.gamedata = json.loads(data[18:])


class NaughtyBee():
    puzzle_words: list[str] = []
    naughty_words: list[str] = []

    def __init__(self, wordfile=NAUGHTY_WORDS_FILE):
        with open(wordfile) as f:
            self.naughty_words = [w.strip() for w in f.readlines()]

    def fetch_words(self, date="", base_url=SPELLINGBEE_URL):
        """Fetch the Spelling Bee answer words for the specified date (default: today)"""
        url = f"{base_url}/{date}"
        r = requests.get(url)
        p = SpellingBeeScraper()
        p.feed(r.text)
        self.puzzle_words = p.gamedata["today"]["answers"]

    def find_naughty_words(self):
        if not self.puzzle_words:
            self.fetch_words()
        return set(self.puzzle_words) & set(self.naughty_words)


def main(date: str = ""):
    bee = NaughtyBee()
    naughty_words = bee.find_naughty_words()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=str, help="date of the puzzle in YYYY-MM-DD format")
    args = parser.parse_args()
    if args.date:
        if not re.fullmatch(r"\d\d\d\d-\d\d-\d\d", args.date):
            print("date must be in the format YYYY-MM-DD")
            exit(1)

    main(args.date)

