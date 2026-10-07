"""Validate SVG XML, image references, Python syntax and deterministic generated output."""
from __future__ import annotations

import ast
import json
import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

from common import ROOT, config
from fetch_contributions import validate_data

SVG_NS = "http://www.w3.org/2000/svg"
FORBIDDEN_TAGS = {"script", "foreignObject", "iframe", "image", "audio", "video"}


def validate_svg(path: Path) -> None:
    raw = path.read_text(encoding="utf-8")
    if len(raw.encode("utf-8")) > 130_000:
        raise ValueError(f"SVG exceeds size budget: {path.name}")
    if "<!DOCTYPE" in raw or "<!ENTITY" in raw:
        raise ValueError("SVG external entities are forbidden")
    root = ET.fromstring(raw)
    if root.tag != f"{{{SVG_NS}}}svg" or root.get("viewBox", "").split()[2] != "640":
        raise ValueError(f"Bad SVG namespace/viewBox: {path.name}")
    tags = {el.tag.rsplit("}", 1)[-1] for el in root.iter()}
    if tags & FORBIDDEN_TAGS:
        raise ValueError(f"Unsupported SVG content: {tags & FORBIDDEN_TAGS}")
    if root.find(f"{{{SVG_NS}}}title") is None or root.find(f"{{{SVG_NS}}}desc") is None:
        raise ValueError("SVG needs a title and description")
    ids = [el.attrib["id"] for el in root.iter() if "id" in el.attrib]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate SVG IDs")
    for target in re.findall(r"url\(#([^\)]+)\)", raw):
        if target not in ids:
            raise ValueError(f"Unresolved SVG paint/clip reference: {target}")
    for el in root.iter():
        for attr, value in el.attrib.items():
            local = attr.rsplit("}", 1)[-1]
            if local.lower().startswith("on"):
                raise ValueError("SVG event handlers are forbidden")
            if local in ("href", "src") and not value.startswith("#"):
                raise ValueError("External SVG resources are forbidden")
    if path.parent.name == "static" and ("animation:" in raw or "@keyframes" in raw or "animate" in tags):
        raise ValueError("Static SVG contains animation")


class MarkdownHTML(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.images: list[dict] = []
        self.forbidden: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "img":
            self.images.append(dict(attrs))
        if tag in ("script", "style", "iframe", "object", "embed", "svg", "form"):
            self.forbidden.append(tag)
        if any((key.startswith("on") or key == "style") for key, _ in attrs):
            self.forbidden.append("unsupported inline attribute")


def validate_markdown(path: Path) -> None:
    md = path.read_text(encoding="utf-8")
    if md.count("```") % 2:
        raise ValueError("Unclosed Markdown fence")
    parser = MarkdownHTML()
    parser.feed(md)
    if parser.forbidden:
        raise ValueError(f"Unsupported README content: {parser.forbidden}")
    if path.name == "README.md" and len(parser.images) != 4:
        raise ValueError("Expected exactly four GitHub-compatible profile images")
    targets = [image.get("src", "") for image in parser.images]
    targets += re.findall(r"\[[^\]]+\]\(([^\s)]+)\)", md)
    for image in parser.images:
        if not image.get("alt") or image.get("width") != "640":
            raise ValueError("Images need meaningful alt text and the constrained width")
    for target in targets:
        if target.startswith("#"):
            continue
        parsed = urlparse(target)
        if parsed.scheme:
            if parsed.scheme != "https":
                raise ValueError("Only HTTPS external links are allowed")
            continue
        local = (path.parent / parsed.path).resolve()
        if not local.is_relative_to(ROOT.resolve()) or not local.exists():
            raise ValueError(f"Missing/unsafe local link: {target}")


def main() -> None:
    import generate_hero
    import generate_info_card
    import generate_projects
    import generate_readme
    import render_heatmap
    c = config()
    data = json.loads((ROOT / "data" / "contributions.json").read_text(encoding="utf-8"))
    validate_data(data, c["username"])
    for path in (ROOT / "scripts").glob("*.py"):
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for path in (ROOT / "tests").glob("*.py"):
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for path in (ROOT / "assets").rglob("*.svg"):
        validate_svg(path)
    validate_markdown(ROOT / "README.md")
    if (ROOT / "README.md").read_text(encoding="utf-8") != generate_readme.render():
        raise ValueError("README does not match the current config")
    for name, module in [("hero.svg", generate_hero), ("info-card.svg", generate_info_card), ("projects.svg", generate_projects)]:
        for static in [False, True]:
            path = ROOT / "assets" / ("static" if static else "") / name
            if path.read_text(encoding="utf-8") != module.render(static):
                raise ValueError(f"Outdated generated asset: {path}")
    for static in [False, True]:
        path = ROOT / "assets" / ("static" if static else "") / "contribution-heatmap.svg"
        if path.read_text(encoding="utf-8") != render_heatmap.render(data, static):
            raise ValueError("Contribution SVG does not match source data")
    print("PASS: Python syntax, SVG XML/safety/size, Markdown paths and deterministic output")


if __name__ == "__main__":
    main()
