"""Actual public GitHub activity, split into two readable calendar bands."""
from __future__ import annotations

import datetime as dt
import json

from common import ROOT, bar, config, esc, finish, reveal, save_asset, start_svg, text
from fetch_contributions import validate_data

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
COLORS = ["#19232f", "#20483f", "#307665", "#4aa58e", "#78d5c2"]


def grid(days: list[dict]) -> list[list[dict | None]]:
    first = dt.date.fromisoformat(days[0]["date"])
    sunday = first - dt.timedelta(days=(first.weekday() + 1) % 7)
    columns: list[list[dict | None]] = []
    for day in days:
        date = dt.date.fromisoformat(day["date"])
        index = (date - sunday).days
        column, row = divmod(index, 7)
        while len(columns) <= column:
            columns.append([None] * 7)
        columns[column][row] = day
    return columns


def render(data: dict, static: bool = False) -> str:
    cfg = config()
    validate_data(data, cfg["username"])
    p = cfg["palette"]
    total = data["total_contributions"]
    out = start_svg(620, f"{cfg['username']} — actual public GitHub contributions",
                    f"{total} contributions from {data['range']['start']} to {data['range']['end']}. "
                    "Source: GitHub's public profile calendar. No private repository details are fetched.", static=static)
    out.append(bar("activity / real public data", "04"))
    out.append(text(28, 95, "PUBLIC GITHUB ACTIVITY", size=23, weight=600))
    out.append(text(26, 151, f"{total:,}", size=50, weight=700, color=p["accent"]))
    label_x = 28 + len(f"{total:,}") * 31 + 23
    out.append(text(label_x, 137, "ACTUAL CONTRIBUTIONS", size=17, mono=True, color=p["muted"]))
    out.append(text(28, 181, f"{data['range']['start']} → {data['range']['end']}",
                    size=18, mono=True, color=p["muted"]))
    columns = grid(data["days"])
    for panel, offset in enumerate(range(0, len(columns), 27)):
        chunk = columns[offset:offset+27]
        top = 230 + panel * 174
        out.append(text(28, top - 27, f"{panel+1:02} / CALENDAR", size=14, mono=True, color=p["dim"]))
        for row, label in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
            out.append(text(28, top + row * 19 + 12, label, size=14, color=p["muted"]))
        last_label_x = -100
        previous_month = None
        for ci, column in enumerate(chunk):
            x = 78 + ci * 19
            present = [d for d in column if d is not None]
            if present:
                date = dt.date.fromisoformat(present[0]["date"])
                key = (date.year, date.month)
                if key != previous_month and x - last_label_x >= 48:
                    out.append(text(x, top - 8, MONTHS[date.month-1], size=14, color=p["muted"]))
                    last_label_x = x
                previous_month = key
            cells = []
            for ri, day in enumerate(column):
                if day is None:
                    continue
                y = top + ri * 19
                count = day["count"]
                tooltip = f"{day['date']}: {count} contribution{'s' if count != 1 else ''}"
                cells.append(f'<rect x="{x}" y="{y}" width="14" height="14" rx="3" '
                             f'fill="{COLORS[day["level"]]}"><title>{esc(tooltip)}</title></rect>')
            out.append(reveal("".join(cells), (offset + ci) * .015, .5, static))
    out.append(f'<path d="M24 551H616" stroke="{p["border"]}"/>')
    out.append(text(28, 588, f"{data['active_days']} active days", size=21, color=p["muted"]))
    out.append(text(395, 587, "LESS", size=13, mono=True, color=p["dim"], anchor="end"))
    for i, color in enumerate(COLORS):
        out.append(f'<rect x="{408+i*20}" y="573" width="14" height="14" rx="3" fill="{color}"/>')
    out.append(text(516, 587, "MORE", size=13, mono=True, color=p["dim"]))
    return finish(out)


if __name__ == "__main__":
    data = json.loads((ROOT / "data" / "contributions.json").read_text(encoding="utf-8"))
    save_asset("contribution-heatmap.svg", render(data), render(data, True))
    print(f"contribution-heatmap.svg: rendered {len(data['days'])} verified days")
