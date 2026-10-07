"""Shared deterministic, self-contained SVG primitives. Python standard library only."""
from __future__ import annotations

import html
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
SANS = "-apple-system, BlinkMacSystemFont, Segoe UI, Arial, sans-serif"


def config() -> dict:
    data = json.loads((ROOT / "profile.json").read_text(encoding="utf-8"))
    username = data["username"]
    if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?", username):
        raise ValueError("Invalid GitHub username")
    return data


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def write_changed(path: Path, content: str) -> bool:
    """Atomic writes; identical output leaves the file untouched."""
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = content.encode("utf-8")
    if path.exists() and path.read_bytes() == raw:
        return False
    temp = path.with_name(path.name + ".tmp")
    try:
        temp.write_bytes(raw)
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)
    return True


def text(x: float, y: float, value: str, *, size: int = 22,
         color: str = "#f0f4f7", weight: int = 400, mono: bool = False,
         anchor: str = "start", extra: str = "") -> str:
    font = MONO if mono else SANS
    return (f'<text x="{x:g}" y="{y:g}" font-family="{font}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}" '
            f'text-anchor="{anchor}" {extra}>{esc(value)}</text>')


def reveal(markup: str, delay: float = 0.0, duration: float = 0.55,
           static: bool = False) -> str:
    if static:
        return markup
    return (f'<g class="reveal" style="animation-delay:{delay:.2f}s;'
            f'animation-duration:{duration:.2f}s">{markup}</g>')


def start_svg(height: int, title: str, description: str, *,
              static: bool = False, extra_defs: str = "", extra_css: str = "") -> list[str]:
    """Content is visible if animation is unsupported; reduced-motion stays static."""
    p = config()["palette"]
    css = "" if static else (
        "@keyframes reveal{from{opacity:0}to{opacity:1}}"
        ".reveal{animation:reveal .55s ease-out both}"
        "@keyframes cursor{0%,45%{opacity:1}46%,100%{opacity:0}}"
        ".cursor{animation:cursor 1.2s step-end 4}"
        + extra_css
        + "@media(prefers-reduced-motion:reduce){*{animation:none!important;"
          "transition:none!important;opacity:1}.motion-only{display:none}}"
    )
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="640" height="{height}" '
           f'viewBox="0 0 640 {height}" role="img" aria-labelledby="title desc">',
           f'<title id="title">{esc(title)}</title>',
           f'<desc id="desc">{esc(description)}</desc>']
    if css:
        out.append(f"<style>{css}</style>")
    out += ['<defs><linearGradient id="surface" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0" stop-color="{p["panel"]}"/>'
            f'<stop offset="1" stop-color="{p["background"]}"/>'
            f'</linearGradient>{extra_defs}</defs>',
            f'<rect width="640" height="{height}" rx="18" fill="url(#surface)"/>',
            f'<rect x=".75" y=".75" width="638.5" height="{height - 1.5}" '
            f'rx="18" fill="none" stroke="{p["border"]}" stroke-width="1.5"/>']
    return out


def bar(label: str, number: str) -> str:
    p = config()["palette"]
    return (f'<path d="M24 52H616" stroke="{p["border"]}"/>'
            + text(26, 33, number, size=16, mono=True, color=p["accent"])
            + text(66, 33, label, size=16, mono=True, color=p["muted"]))


def finish(out: list[str]) -> str:
    return "".join(out) + "</svg>\n"


def save_asset(name: str, animated: str, static: str) -> None:
    write_changed(ROOT / "assets" / name, animated)
    write_changed(ROOT / "assets" / "static" / name, static)
