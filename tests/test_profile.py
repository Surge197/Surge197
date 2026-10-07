"""Synthetic fixtures are used only in unit tests, never as published activity."""
from __future__ import annotations

import copy
import datetime as dt
import importlib
import json
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from common import config, write_changed
from fetch_contributions import (ContributionError, build_data, parse_calendar,
                                 parse_count, validate_data, validate_days)
from render_heatmap import grid
from validate import validate_svg


def fixture_days() -> list[dict]:
    start = dt.date(2025, 1, 1)
    return [{"date": (start + dt.timedelta(days=i)).isoformat(),
             "count": 3 if i % 19 == 0 else 0,
             "level": 2 if i % 19 == 0 else 0} for i in range(365)]


def calendar_cell(date: str, count_text: str | None, level: int, ident: str) -> str:
    cell = f'<td class="ContributionCalendar-day" data-date="{date}" id="{ident}" data-level="{level}"></td>'
    tooltip = f'<tool-tip for="{ident}">{count_text}</tool-tip>' if count_text is not None else ""
    return cell + tooltip


class ContributionTests(unittest.TestCase):
    def test_exact_zero(self):
        self.assertEqual(parse_count("No contributions on October 1st."), 0)

    def test_singular_plural_and_commas(self):
        self.assertEqual(parse_count("1 contribution on October 1st."), 1)
        self.assertEqual(parse_count("1,234 contributions on October 1st."), 1234)

    def test_unknown_count_is_not_zero(self):
        for text in ["", "Contributions unavailable", "Loading", "-2 contributions"]:
            with self.subTest(text=text), self.assertRaises(ContributionError):
                parse_count(text)

    def test_tooltip_join_and_sort(self):
        html = calendar_cell("2025-01-02", "2 contributions on January 2nd.", 2, "b")
        html += calendar_cell("2025-01-01", "No contributions on January 1st.", 0, "a")
        days = parse_calendar(html, minimum=1)
        self.assertEqual([d["date"] for d in days], ["2025-01-01", "2025-01-02"])
        self.assertEqual([d["count"] for d in days], [0, 2])

    def test_missing_tooltip_rejected(self):
        with self.assertRaises(ContributionError):
            parse_calendar(calendar_cell("2025-01-01", None, 0, "a"), minimum=1)

    def test_inconsistent_level_rejected(self):
        with self.assertRaises(ContributionError):
            parse_calendar(calendar_cell("2025-01-01", "3 contributions", 0, "a"), minimum=1)

    def test_partial_calendar_rejected(self):
        with self.assertRaises(ContributionError):
            parse_calendar(calendar_cell("2025-01-01", "No contributions", 0, "a"))

    def test_missing_day_rejected(self):
        days = fixture_days()
        del days[20]
        with self.assertRaises(ContributionError):
            validate_days(days)

    def test_duplicate_date_rejected(self):
        days = fixture_days()
        days[20]["date"] = days[19]["date"]
        with self.assertRaises(ContributionError):
            validate_days(days)

    def test_invalid_level_rejected(self):
        days = fixture_days()
        days[0]["level"] = 5
        with self.assertRaises(ContributionError):
            validate_days(days)

    def test_invalid_date_rejected(self):
        days = fixture_days()
        days[0]["date"] = "not-a-date"
        with self.assertRaises(ContributionError):
            validate_days(days)

    def test_totals_are_derived(self):
        days = fixture_days()
        data = build_data("Surge197", days)
        self.assertEqual(data["total_contributions"], sum(d["count"] for d in days))
        validate_data(data, "Surge197")
        data["total_contributions"] += 1
        with self.assertRaises(ContributionError):
            validate_data(data, "Surge197")

    def test_wrong_username_rejected(self):
        with self.assertRaises(ContributionError):
            validate_data(build_data("someone-else", fixture_days()), "Surge197")

    def test_wrong_source_rejected(self):
        data = build_data("Surge197", fixture_days())
        data["source"] = "https://example.com"
        with self.assertRaises(ContributionError):
            validate_data(data, "Surge197")

    def test_calendar_week_alignment(self):
        columns = grid(fixture_days())
        self.assertIsNone(columns[0][0]) # 2025-01-01 was a Wednesday.
        self.assertEqual(columns[0][3]["date"], "2025-01-01")
        self.assertEqual(sum(d is not None for c in columns for d in c), 365)


class AssetTests(unittest.TestCase):
    def test_profile_identity_consistent(self):
        identity = config()["identity"]
        for name in ["generate_hero", "generate_info_card", "generate_projects"]:
            module = importlib.import_module(name)
            self.assertIn(identity, module.render(True))
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn(identity, readme)
        self.assertNotIn("LORD", readme)

    def test_config_has_no_fake_project_links(self):
        self.assertTrue(all(project["url"] is None for project in config()["projects"]))

    def test_deterministic_identity_assets(self):
        for name in ["generate_hero", "generate_info_card", "generate_projects"]:
            module = importlib.import_module(name)
            with self.subTest(module=name):
                self.assertEqual(module.render(), module.render())
                ET.fromstring(module.render())
                ET.fromstring(module.render(True))

    def test_reduced_motion_and_static_fallbacks(self):
        for name in ["generate_hero", "generate_info_card", "generate_projects"]:
            module = importlib.import_module(name)
            self.assertIn("prefers-reduced-motion", module.render())
            self.assertNotIn("@keyframes", module.render(True))
            self.assertNotIn("animation:", module.render(True))

    def test_all_generated_assets_are_safe(self):
        paths = list((ROOT / "assets").rglob("*.svg"))
        self.assertEqual(len(paths), 8)
        for path in paths:
            with self.subTest(path=path.name):
                validate_svg(path)

    def test_block_unsafe_svg(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "bad.svg"
            file.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 400"><title>x</title><desc>x</desc><script>alert(1)</script></svg>', encoding="utf-8")
            with self.assertRaises(ValueError):
                validate_svg(file)

    def test_atomic_noop_write(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "asset.svg"
            self.assertTrue(write_changed(file, "original"))
            timestamp = file.stat().st_mtime_ns
            self.assertFalse(write_changed(file, "original"))
            self.assertEqual(timestamp, file.stat().st_mtime_ns)
            self.assertTrue(write_changed(file, "updated"))
            self.assertEqual(file.read_text(), "updated")

    def test_checked_in_data_is_actual_source(self):
        data = json.loads((ROOT / "data" / "contributions.json").read_text(encoding="utf-8"))
        validate_data(data, config()["username"])


if __name__ == "__main__":
    unittest.main()
