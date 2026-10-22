"""
Keyword-based topic tagging of Steam reviews.

The dictionary lives in config/review_topics.csv (topic, language, keyword).
It is applied to the review text at collection time; only the resulting 0/1
flags are stored, the text itself is thrown away (privacy by design).

Keyword syntax:
    crash      whole word only           ("crash", not "crashes")
    crash*     word that starts with it  ("crash", "crashes", "crashing")
    full price phrase; any whitespace between the words
For Chinese, Japanese and Korean there are no spaces between words, so
keywords there are matched anywhere in the text.

Every change of the dictionary (or of these matching rules) produces a new
TOPICS_VERSION. The collector stores it in each row and re-collects the
review history when it changes, so all reviews are tagged by the same rules.
"""

import csv
import hashlib
import re
from pathlib import Path

TOPICS_FILE = Path(__file__).resolve().parent.parent / "config" / "review_topics.csv"

TOPICS = ["bugs", "performance", "price", "story", "content"]   # column order in the output
NO_SPACE_LANGUAGES = {"schinese", "tchinese", "japanese", "koreana"}
RULES_REVISION = "2"   # bump when the matching logic below changes
APOSTROPHES = str.maketrans({"\u2019": "'", "\u2018": "'", "\u02bc": "'", "`": "'"})


def _keyword_regex(keyword: str, language: str) -> str:
    prefix = keyword.endswith("*")
    word = keyword.rstrip("*").strip()
    body = r"\s+".join(re.escape(part) for part in word.split())
    if language in NO_SPACE_LANGUAGES:
        return body
    return r"(?<!\w)" + body + (r"\w*" if prefix else r"(?!\w)")


def load_dictionary(path: Path = TOPICS_FILE) -> tuple[dict, str]:
    """
    Returns ({language: {topic: compiled regex}}, version).
    Version = rules revision + first 8 hex digits of the dictionary's SHA-256.
    """
    raw = path.read_bytes().replace(b"\r\n", b"\n")      # same hash on Windows and Mac
    version = f"r{RULES_REVISION}-{hashlib.sha256(raw).hexdigest()[:8]}"

    patterns: dict[str, dict[str, list[str]]] = {}
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            topic = row["topic"].strip().lower()
            language = row["language"].strip().lower()
            keyword = row["keyword"].strip().lower()
            if topic not in TOPICS:
                raise ValueError(f"{path.name}: unknown topic '{topic}' (allowed: {', '.join(TOPICS)})")
            if not keyword or not language:
                raise ValueError(f"{path.name}: empty language or keyword in row {row}")
            patterns.setdefault(language, {}).setdefault(topic, []).append(
                _keyword_regex(keyword, language))

    compiled = {
        language: {topic: re.compile("|".join(regexes), re.IGNORECASE)
                   for topic, regexes in by_topic.items()}
        for language, by_topic in patterns.items()
    }
    return compiled, version


def tag(text: str, language: str, dictionary: dict) -> tuple[dict, int]:
    """
    Returns ({topic: 0/1}, scanned). scanned = 1 if the review language is
    covered by the dictionary and the text is not empty; otherwise all flags
    are 0 and the review must not count in topic shares.
    """
    rules = dictionary.get(language)
    text = (text or "").strip().translate(APOSTROPHES)   # won’t -> won't
    if not rules or not text:
        return {t: 0 for t in TOPICS}, 0
    return {t: 1 if (t in rules and rules[t].search(text)) else 0 for t in TOPICS}, 1
