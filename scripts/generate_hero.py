"""Original SURGE identity: a short terminal boot, then an architectural S mark."""
from common import bar, config, finish, reveal, save_asset, text, start_svg


def render(static: bool = False) -> str:
    cfg = config()
    p = cfg["palette"]
    css = ("@keyframes boot{0%,64%{opacity:1}78%,100%{opacity:0}}"
           ".boot{animation:boot 2.1s linear forwards;pointer-events:none}"
           "@keyframes trace{from{stroke-dashoffset:316}to{stroke-dashoffset:0}}"
           ".trace{animation:trace 1.2s ease-out 1.45s both}")
    out = start_svg(390, "SURGE — AI, automation and accounting systems",
                    cfg["statement"] + " An original terminal boot transitions to a geometric S monogram.",
                    static=static, extra_css=css)
    out.append(bar("surge / systems interface", "01"))
    # Quiet engineering grid, no glow, filters, photos or external fonts.
    for x in range(370, 610, 30):
        out.append(f'<path d="M{x} 80V290" stroke="{p["border"]}" opacity=".25"/>')
    for y in range(80, 300, 30):
        out.append(f'<path d="M370 {y}H610" stroke="{p["border"]}" opacity=".25"/>')
    identity = [text(28, 94, "INTELLIGENCE / OPERATIONS", size=17, mono=True, color=p["accent"]),
                text(26, 181, cfg["identity"], size=74, weight=750),
                text(28, 234, "AI • AUTOMATION", size=25, weight=600, color=p["muted"]),
                text(28, 271, "ACCOUNTING SYSTEMS", size=25, weight=600, color=p["muted"])]
    out.append(reveal("".join(identity), 1.45, .8, static))
    mark = (f'<rect x="412" y="103" width="170" height="170" rx="28" '
            f'fill="{p["background"]}" stroke="{p["border"]}"/>'
            f'<path class="{"trace" if not static else ""}" '
            'd="M548 139H480C458 139 445 152 445 170C445 188 459 200 480 200H516C538 200 551 212 551 231C551 249 537 261 516 261H446" '
            f'fill="none" stroke="{p["accent"]}" stroke-width="13" '
            'pathLength="316" stroke-linecap="square" stroke-dasharray="316" stroke-dashoffset="0"/>'
            + text(497, 301, "[ S / SYSTEMS ]", size=17, mono=True,
                   color=p["dim"], anchor="middle"))
    out.append(reveal(mark, 1.45, .7, static))
    out += [f'<path d="M24 322H616" stroke="{p["border"]}"/>',
            text(28, 358, "surge@systems:~$ build --with-purpose", size=18, mono=True,
                 color=p["accent"])]
    if not static:
        out.append(f'<rect class="cursor motion-only" x="438" y="342" '
                   f'width="10" height="20" fill="{p["accent"]}"/>')
        boot = [f'<rect x="8" y="62" width="624" height="253" fill="{p["background"]}"/>',
                text(28, 96, "$ initialize surge.profile", size=21, mono=True,
                     color=p["text"])]
        for i, label in enumerate(["AI SYSTEMS", "AUTOMATION ENGINE", "ACCOUNTING ENGINE", "PROJECT REGISTRY"]):
            row = text(28, 140 + i * 37, label, size=20, mono=True, color=p["muted"])
            row += text(594, 140 + i * 37, "READY", size=18, mono=True,
                        color=p["accent"], anchor="end")
            boot.append(reveal(row, .13 + i * .22, .2))
        out.append('<g class="boot motion-only">' + "".join(boot) + '</g>')
    return finish(out)


if __name__ == "__main__":
    save_asset("hero.svg", render(), render(True))
    print("hero.svg: original boot and identity generated")
