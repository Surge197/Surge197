"""Fetch GitHub's public contribution calendar, without a token or fabricated counts.

Markup is an upstream dependency. A missing tooltip, invalid count, incomplete
calendar or HTTP error aborts before the last good JSON/SVG is overwritten.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from common import ROOT, config, write_changed


class ContributionError(ValueError):
    pass


class CalendarParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.cells: list[dict] = []
        self.tooltips: dict[str, str] = {}
        self._tooltip: str | None = None
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        classes = (a.get("class") or "").split()
        if tag == "td" and "ContributionCalendar-day" in classes and a.get("data-date"):
            self.cells.append({"date": a["data-date"], "id": a.get("id"),
                               "level": a.get("data-level")})
        if tag == "tool-tip" and a.get("for"):
            self._tooltip = a["for"]
            self._parts = []

    def handle_data(self, data: str) -> None:
        if self._tooltip is not None:
            self._parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "tool-tip" and self._tooltip is not None:
            self.tooltips[self._tooltip] = " ".join("".join(self._parts).split())
            self._tooltip = None
            self._parts = []


def parse_count(tooltip: str) -> int:
    if re.match(r"^No contributions\b", tooltip, re.IGNORECASE):
        return 0
    match = re.match(r"^(\d[\d,]*)\s+contributions?\b", tooltip, re.IGNORECASE)
    if not match:
        raise ContributionError("A contribution tooltip is missing or unrecognized")
    count = int(match.group(1).replace(",", ""))
    if count < 0:
        raise ContributionError("Negative contribution count")
    return count


def validate_days(days: list[dict], *, minimum: int = 350) -> None:
    if len(days) < minimum or len(days) > 380:
        raise ContributionError(f"Incomplete/unexpected calendar: {len(days)} days")
    previous = None
    seen = set()
    for day in days:
        try:
            date = dt.date.fromisoformat(day["date"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ContributionError("Invalid contribution date") from exc
        if date.isoformat() in seen:
            raise ContributionError("Duplicate contribution date")
        seen.add(date.isoformat())
        if previous is not None and date != previous + dt.timedelta(days=1):
            raise ContributionError("Calendar days are missing or out of order")
        previous = date
        count, level = day.get("count"), day.get("level")
        if type(count) is not int or count < 0:
            raise ContributionError("Count must be a nonnegative integer")
        if type(level) is not int or level not in range(5):
            raise ContributionError("GitHub intensity level must be 0..4")
        if (count == 0) != (level == 0):
            raise ContributionError("Tooltip count and calendar intensity disagree")


def parse_calendar(markup: str, *, minimum: int = 350) -> list[dict]:
    parser = CalendarParser()
    parser.feed(markup)
    days = []
    for cell in parser.cells:
        try:
            date = dt.date.fromisoformat(cell["date"]).isoformat()
            level = int(cell["level"])
        except (ValueError, TypeError) as exc:
            raise ContributionError("Invalid contribution cell metadata") from exc
        tooltip = parser.tooltips.get(cell["id"], "")
        days.append({"date": date, "count": parse_count(tooltip), "level": level})
    days.sort(key=lambda d: d["date"])
    validate_days(days, minimum=minimum)
    return days


def build_data(username: str, days: list[dict]) -> dict:
    validate_days(days)
    return {"schema_version": 1, "username": username,
            "source": f"https://github.com/users/{username}/contributions",
            "visibility": "public-profile-calendar",
            "range": {"start": days[0]["date"], "end": days[-1]["date"]},
            "total_contributions": sum(d["count"] for d in days),
            "active_days": sum(d["count"] > 0 for d in days), "days": days}


def validate_data(data: dict, expected_username: str | None = None) -> None:
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ContributionError("Unsupported contribution data schema")
    username = data.get("username")
    if expected_username and username != expected_username:
        raise ContributionError("Contribution username does not match profile")
    if data.get("source") != f"https://github.com/users/{username}/contributions":
        raise ContributionError("Contribution source is not the expected public endpoint")
    if data.get("visibility") != "public-profile-calendar":
        raise ContributionError("Unexpected contribution visibility scope")
    days = data.get("days")
    if not isinstance(days, list):
        raise ContributionError("Missing contribution days")
    validate_days(days)
    if data.get("range") != {"start": days[0]["date"], "end": days[-1]["date"]}:
        raise ContributionError("Contribution date range mismatch")
    if data.get("total_contributions") != sum(d["count"] for d in days):
        raise ContributionError("Contribution total mismatch")
    if data.get("active_days") != sum(d["count"] > 0 for d in days):
        raise ContributionError("Active day total mismatch")


def fetch_markup(username: str) -> str:
    url = f"https://github.com/users/{username}/contributions"
    request = Request(url, headers={"User-Agent": "surge-profile/1.0", "Accept": "text/html",
                                    "Accept-Language": "en-US,en;q=0.9"})
    for attempt in range(3):
        try:
            with urlopen(request, timeout=35) as response:
                content = response.read(2_000_001)
                if len(content) > 2_000_000:
                    raise ContributionError("Unexpectedly large calendar response")
                return content.decode("utf-8")
        except HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == 2:
                raise ContributionError(f"GitHub calendar HTTP error {exc.code}; prior data kept") from exc
        except (URLError, TimeoutError) as exc:
            if attempt == 2:
                raise ContributionError("GitHub calendar unavailable; prior data kept") from exc
        time.sleep(2 ** (attempt + 1))
    raise ContributionError("Calendar unavailable")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html-file", type=Path, help="Use previously fetched real HTML for offline validation")
    args = parser.parse_args()
    username = config()["username"]
    markup = args.html_file.read_text(encoding="utf-8") if args.html_file else fetch_markup(username)
    days = parse_calendar(markup)
    if not args.html_file:
        today = dt.datetime.now(dt.timezone.utc).date()
        last = dt.date.fromisoformat(days[-1]["date"])
        if abs((today - last).days) > 2:
            raise ContributionError("Live calendar is stale or has an unexpected future date")
    data = build_data(username, days)
    validate_data(data, username)
    changed = write_changed(ROOT / "data" / "contributions.json",
                            json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"{username}: {data['total_contributions']} actual contributions across "
          f"{len(days)} days; {'updated' if changed else 'unchanged'}")


if __name__ == "__main__":
    try:
        main()
    except ContributionError as exc:
        raise SystemExit(str(exc)) from exc
