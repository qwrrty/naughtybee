#! /usr/bin/env python3

import argparse
import json
import re

from html.parser import HTMLParser
from pprint import pprint

import requests


SPELLINGBEE_URL = "https://www.nytimes.com/puzzles/spelling-bee"
NAUGHTY_WORDS = [
    "sexy", "sexual", "sexually", "sexuality",
    "cock", "penis", "prick", "dick", "erection", "dong", "wang", "phallus", "pecker", "bone", "boner", "boned", "boning",
    "ball", "balls", "testicle", "ballsack",
    "vagina", "vulva", "labia", "pussy", "cunt", "snatch", "beaver", "fanny", "muff", "twat", "poon", "poontang",
    "quim", "yoni", "minge", "punani", "clit", "clitoris", "clitty",
    "arse", "butt", "arsehole", "butthole", "asshole", "anal", "anally", "tush", "tushy", "buttock", "backside", "derriere", "booty", "bung", "bunghole", "taint",
    "shit", "crap", "shitty", "crappy", "poop", "poopy", "pooping", "scat",
    "peeing", "piss", "pissing", "pissed", "urine", "urinate", "urination",
    "fart", "farting",
    "boob", "breast", "titty", "teat", "mammary", "bosom", "nipple", "topless",
    "fuck", "fucking", "fucker", "fucked", "bang", "banging", "banged", "screw", "screwing", "screwed", "hump", "humping", "humped",
    "coitus", "copulate", "lovemaking", "nookie", "poontang", "shag", "shagging", "bareback",
    "fellatio", "fellator", "blowjob", "blowing", "blow",
    "lick", "licking", "licked", "suck", "sucking", "sucked", "sucker", "cocksucker", "cocksucking",
    "sadism", "sadist", "kink", "kinky", "orgy", "sodomy", "sodomize", "voyeur",
    "naked", "nude", "nudist", "nudity", "porn", "porno", "smut", "shaved",
    "dyke", "bulldyke", "lesbian", "faggot", "faggy", "queer", "twink", "twinkie", "bitch",
    "slut", "slutty", "swinging", "swinger", "whore",
    "vibrator", "dildo", "pegged", "pegging", "strapon", "bugger",
    "jerkoff", "jackoff", "wank", "wanker", "wanking",
    "come", "cream", "creamed", "creaming", "squirt", "squirting", "orgasm", "climax", "jizz", "semen", "spunk",
    "felch", "incest", "raping", "rapist", "rape", "raped",
]


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


def fetch_sb_words(date: str = ""):
    """Fetch the Spelling Bee answer words for the specified date (default: today)"""
    url = SPELLINGBEE_URL
    if date:
        url += "/" + date
    r = requests.get(url)
    p = SpellingBeeScraper()
    p.feed(r.text)
    return p.gamedata["today"]["answers"]


def main(date: str = ""):
    sb_words = fetch_sb_words(date)

    matches = set(NAUGHTY_WORDS) & set(sb_words)
    print(matches)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=str, help="date of the puzzle in YYYY-MM-DD format")
    args = parser.parse_args()
    if args.date:
        if not re.fullmatch(r"\d\d\d\d-\d\d-\d\d", args.date):
            print("date must be in the format YYYY-MM-DD")
            exit(1)

    main(args.date)

