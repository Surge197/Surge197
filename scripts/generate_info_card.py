"""Generated terminal-inspired information card; no unverified bio claims."""
from common import bar, config, finish, reveal, save_asset, start_svg, text


def render(static: bool = False) -> str:
    cfg = config()
    p = cfg["palette"]
    out = start_svg(440, "SURGE — current focus and systems", "Current focus: "
                    + ", ".join(cfg["focus"]) + ". Current systems: "
                    + ", ".join(item["name"] for item in cfg["projects"]), static=static)
    out.append(bar("whoami / current focus", "02"))
    out += [text(28, 98, cfg["identity"], size=34, weight=700),
            text(28, 127, "BUILDING SYSTEMS, NOT JUST DEMOS.", size=17, mono=True,
                 color=p["accent"])]
    for i, focus in enumerate(cfg["focus"]):
        y = 180 + i * 43
        row = text(28, y, f"0{i + 1}", size=18, mono=True, color=p["dim"])
        row += text(82, y, focus.upper(), size=25, weight=550)
        row += f'<path d="M82 {y+15}H606" stroke="{p["border"]}" opacity=".6"/>'
        out.append(reveal(row, .12 + i * .12, .45, static))
    out += [text(28, 378, "CURRENT SYSTEMS", size=17, mono=True, color=p["accent"]),
            text(28, 409, "ELVARC / FORGE / AccuTax / AI Review", size=21,
                 color=p["muted"])]
    return finish(out)


if __name__ == "__main__":
    save_asset("info-card.svg", render(), render(True))
    print("info-card.svg: focus and system registry generated")
