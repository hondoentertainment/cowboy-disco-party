#!/usr/bin/env python3
"""Apply a confirmed party date across config, HTML pages, and assets."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "js" / "config.js"
TZ = ZoneInfo("America/Los_Angeles")

DISPLAY_FMT = "%A, %B %-d, %Y" if hasattr(datetime, "strftime") else None


def parse_date(value: str) -> datetime:
    for fmt in ("%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(value, fmt).replace(tzinfo=TZ)
        except ValueError:
            continue
    raise SystemExit(f"Could not parse date: {value}")


def iso_at(day: datetime, hour: int, minute: int = 0) -> str:
    dt = day.replace(hour=hour, minute=minute, second=0, microsecond=0)
    return dt.isoformat(timespec="seconds")


def display_date(day: datetime) -> str:
    return day.strftime("%A, %B %d, %Y").replace(" 0", " ")


def short_date(day: datetime) -> str:
    return f"{day.strftime('%b')} {day.day}, {day.year}"


def update_config(day: datetime) -> None:
    party = iso_at(day, 18, 30)
    end = iso_at(day, 22, 0)
    vote_close = iso_at(day, 21, 0)
    label = display_date(day)
    short = short_date(day)

    text = CONFIG.read_text(encoding="utf-8")
    text = re.sub(r"PARTY_DATE_TBD:\s*true", "PARTY_DATE_TBD: false", text)
    text = re.sub(r'PARTY_DATE:\s*null', f'PARTY_DATE: "{party}"', text)
    text = re.sub(r'PARTY_END:\s*null', f'PARTY_END: "{end}"', text)
    text = re.sub(r'VOTE_CLOSE_TIME:\s*null', f'VOTE_CLOSE_TIME: "{vote_close}"', text)
    text = re.sub(
        r'Cowboy Disco Party — date TBD!',
        f"Cowboy Disco Party — {short}!",
        text,
    )
    CONFIG.write_text(text, encoding="utf-8")
    print(json.dumps({"display": label, "party": party, "end": end, "voteClose": vote_close}, indent=2))


def replace_in_html(day: datetime) -> None:
    label = display_date(day)
    short = short_date(day)
    hero = f"{short} · 6:00 PM"
    title = f"Cowboy Disco Party | {short}"

    replacements = [
        ("Date TBD · 6:00 PM", hero),
        ("Date TBD", short),
        ("date TBD", short),
        ("Date TBD —", f"{short} —"),
        ("Party schedule — date TBD", f"Party schedule — {short}"),
        ("Cowboy Disco Party | Date TBD", title),
        ("Party schedule — date TBD", f"Party schedule — {short}"),
        ("<td>TBD</td>", f"<td>{short}</td>"),
        ("Date Coming Soon", "Party Countdown"),
        ("Check back for the official party date — saddle up now.", f"See you {label} at 6:00 PM — saddle up now."),
        ("Mark your calendar and break out the boots.", f"Mark your calendar for {label} and break out the boots."),
        (f"Date TBD — here's how the night unfolds once we set it.", f"{short} — here's how the night unfolds."),
    ]

    for path in ROOT.glob("*.html"):
        content = path.read_text(encoding="utf-8")
        original = content
        for old, new in replacements:
            content = content.replace(old, new)
        if content != original:
            path.write_text(content, encoding="utf-8")
            print(f"updated {path.name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply party date across the site.")
    parser.add_argument("date", help="Party date (YYYY-MM-DD)")
    args = parser.parse_args()
    day = parse_date(args.date)
    update_config(day)
    replace_in_html(day)
    print(f"\nNext: python scripts/generate-cowboy-disco-assets.py")
    print("      python scripts/generate-qr.py")
    print("      npx vercel env add VOTE_CLOSE_TIME production")


if __name__ == "__main__":
    main()
