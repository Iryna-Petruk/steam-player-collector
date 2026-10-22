"""
Check how well the keyword topics work, on real reviews, by hand.

Step 1 - download a sample WITH text into the local/ folder (ignored by git,
never committed or published):

    python collector/topic_check.py sample 1091500 --language english --negative --n 100

Step 2 - open the CSV (Excel, Numbers, Google Sheets), read each review and
fill the label_* columns with 1 (the review is about this topic) or 0.
Leave the auto_* columns as they are: that is what the dictionary decided.

Step 3 - score the dictionary against your labels:

    python collector/topic_check.py score local/topic_sample_1091500_english_negative.csv

Precision = of the reviews the dictionary tagged, how many really are about the topic.
Recall    = of the reviews really about the topic, how many the dictionary found.
Improve config/review_topics.csv, re-run step 1 or 3, repeat. Every change of
the dictionary makes the collector re-tag the full history automatically.
"""

import argparse
import csv
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import collect_reviews as cr  # noqa: E402
import review_topics as rt  # noqa: E402

LOCAL_DIR = cr.REPO_ROOT / "local"
MAX_PAGES = 100   # up to 10,000 reviews scanned to find enough negative ones


def sample(appid: str, language: str, negative: bool, n: int) -> int:
    params = cr.base_params(appid) | {
        "filter": cr.FILTER_RECENT,
        "languages": [language],
        "review_type": "negative" if negative else "all",
        "cursor": "*",
    }
    reviews = []
    for _ in range(MAX_PAGES):
        if len(reviews) >= n:
            break
        resp = cr.call_api(params)
        page = resp.get("reviews", []) or []
        if not page:
            break
        # Filter here as well: GetAppReviews may ignore review_type and
        # return positive reviews too.
        reviews += [r for r in page if (r.get("review") or "").strip()
                    and not (negative and r.get("voted_up"))]
        cursor = resp.get("cursor")
        if not cursor or cursor == params["cursor"]:
            break
        params["cursor"] = cursor
        time.sleep(cr.PAUSE_BETWEEN_REQUESTS)
    reviews = reviews[:n]
    if not reviews:
        print("No reviews found for these settings.")
        return 1

    LOCAL_DIR.mkdir(exist_ok=True)
    kind = "negative" if negative else "all"
    out = LOCAL_DIR / f"topic_sample_{appid}_{language}_{kind}.csv"
    header = (["recommendation_id", "language", "voted_up", "text"]
              + [f"auto_{t}" for t in rt.TOPICS] + [f"label_{t}" for t in rt.TOPICS])
    # utf-8-sig: Excel then shows Polish, Cyrillic and Chinese letters correctly.
    with out.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in reviews:
            flags, _ = rt.tag(r.get("review", ""), r.get("language", ""), cr.TOPIC_DICTIONARY)
            text = " ".join((r.get("review") or "").split())        # one line per review
            w.writerow([r.get("recommendationid"), r.get("language"), 1 if r.get("voted_up") else 0, text]
                       + [flags[t] for t in rt.TOPICS] + [""] * len(rt.TOPICS))
    print(f"Saved {len(reviews)} reviews to {out.relative_to(cr.REPO_ROOT)}")
    print("This file contains review text: it stays on your computer (local/ is in .gitignore).")
    return 0


def read_rows(path: Path) -> list[dict]:
    raw = path.read_text(encoding="utf-8-sig")
    # Excel with Polish or Ukrainian regional settings saves CSV with ';'.
    dialect = csv.Sniffer().sniff(raw.splitlines()[0], delimiters=",;\t")
    return list(csv.DictReader(raw.splitlines(), dialect=dialect))


def score(path: Path) -> int:
    rows = read_rows(path)
    labelled = [r for r in rows if any((r.get(f"label_{t}") or "").strip() for t in rt.TOPICS)]
    if not labelled:
        print("No labels yet: fill the label_* columns with 1 or 0 first.")
        return 1
    print(f"{len(labelled)} labelled reviews of {len(rows)}  (dictionary {cr.TOPICS_VERSION})\n")
    print(f"{'topic':<12} {'tagged':>6} {'true':>5} {'hit':>4} {'false+':>6} {'missed':>6} "
          f"{'precision':>9} {'recall':>7}")
    for t in rt.TOPICS:
        # Re-tag with the CURRENT dictionary, so edits can be checked without a new sample.
        tp = fp = fn = 0
        for r in labelled:
            flags, _ = rt.tag(r["text"], r["language"], cr.TOPIC_DICTIONARY)
            auto = flags[t] == 1
            truth = (r.get(f"label_{t}") or "").strip() == "1"
            tp += auto and truth
            fp += auto and not truth
            fn += truth and not auto
        prec = f"{tp / (tp + fp):.0%}" if tp + fp else "-"
        rec = f"{tp / (tp + fn):.0%}" if tp + fn else "-"
        print(f"{t:<12} {tp + fp:>6} {tp + fn:>5} {tp:>4} {fp:>6} {fn:>6} {prec:>9} {rec:>7}")
    print("\nfalse+ : tagged but not about the topic -> a keyword is too broad")
    print("missed : about the topic but not tagged -> a keyword is missing")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sample", help="download reviews with text into local/ for labelling")
    s.add_argument("appid")
    s.add_argument("--language", default="english", help="Steam language code, e.g. english, polish, schinese")
    s.add_argument("--negative", action="store_true", help="only negative reviews")
    s.add_argument("--n", type=int, default=100)
    c = sub.add_parser("score", help="precision and recall against your labels")
    c.add_argument("file", type=Path)
    a = p.parse_args()
    if a.cmd == "sample":
        return sample(a.appid, a.language, a.negative, a.n)
    return score(a.file)


if __name__ == "__main__":
    sys.exit(main())
