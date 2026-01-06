#! /usr/bin/env python3

import argparse
import json
import re

from html.parser import HTMLParser

import requests

from atproto import Client


SPELLINGBEE_URL = "https://www.nytimes.com/puzzles/spelling-bee"
NAUGHTY_WORDS_FILE = "wordlist.txt"
BSKY_CREDS_FILE = "creds.json"


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


def main(date="", dry_run=False):
    bee = NaughtyBee()
    naughty_words = bee.find_naughty_words()
    post_text = "\n".join([w.upper() for w in sorted(naughty_words)])

    with open(BSKY_CREDS_FILE, "r") as f:
        creds = json.load(f)
    client = Client()
    client.login(creds["username"], creds["password"])
    if dry_run:
        print(f"Successful login as {creds['username']}")
        print("Posting:")
        print(post_text)
    else:
        client.send_post(text=post_text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=str, help="date of the puzzle in YYYY-MM-DD format")
    parser.add_argument("--dry-run", "-n", action="store_true", help="only print out results")
    args = parser.parse_args()
    if args.date:
        if not re.fullmatch(r"\d\d\d\d-\d\d-\d\d", args.date):
            print("date must be in the format YYYY-MM-DD")
            exit(1)

    main(args.date, args.dry_run)

