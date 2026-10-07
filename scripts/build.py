"""Regenerate the profile. No third-party runtime dependencies or secrets required."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys

from common import ROOT, save_asset, write_changed
import generate_hero
import generate_info_card
import generate_projects
import generate_readme
import render_heatmap


def build(offline: bool = False) -> None:
    if not offline:
        subprocess.run([sys.executable, str(ROOT / "scripts" / "fetch_contributions.py")], check=True)
    data = json.loads((ROOT / "data" / "contributions.json").read_text(encoding="utf-8"))
    # All dynamic data is validated before any art is changed.
    render_heatmap.validate_data(data, render_heatmap.config()["username"])
    for name, module in [("hero.svg", generate_hero), ("info-card.svg", generate_info_card),
                         ("projects.svg", generate_projects)]:
        save_asset(name, module.render(), module.render(True))
    save_asset("contribution-heatmap.svg", render_heatmap.render(data), render_heatmap.render(data, True))
    write_changed(ROOT / "README.md", generate_readme.render())
    subprocess.run([sys.executable, str(ROOT / "scripts" / "validate.py")], check=True)
    print("Profile build complete: 4 animated SVGs, 4 static SVGs and README.md")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true", help="Use the last verified contribution JSON")
    build(parser.parse_args().offline)
