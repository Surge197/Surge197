"""Project registry SVG generated exclusively from the supplied project brief."""
from common import bar, config, finish, reveal, save_asset, start_svg, text


def render(static: bool = False) -> str:
    cfg = config()
    p = cfg["palette"]
    out = start_svg(728, "SURGE — systems in progress", " ".join(
        item["name"] + ": " + item["description"] for item in cfg["projects"]), static=static)
    out.append(bar("projects / systems in progress", "03"))
    for i, project in enumerate(cfg["projects"]):
        y = 75 + i * 158
        card = [f'<rect x="20" y="{y}" width="600" height="142" rx="12" '
                f'fill="{p["background"]}" stroke="{p["border"]}"/>',
                f'<path d="M20 {y+18}V{y+124}" stroke="{p["accent"]}" stroke-width="3"/>',
                text(39, y + 26, project["category"], size=15, mono=True, color=p["accent"]),
                text(39, y + 61, project["name"], size=29, weight=700),
                text(597, y + 61, project["status"], size=14, mono=True,
                     color=p["muted"], anchor="end")]
        for j, line in enumerate(project["lines"]):
            card.append(text(39, y + 93 + j * 28, line, size=22, color=p["muted"]))
        out.append(reveal("".join(card), .15 + i * .15, .55, static))
    return finish(out)


if __name__ == "__main__":
    save_asset("projects.svg", render(), render(True))
    print("projects.svg: four original project panels generated")
