"""The SVGs are the interface; native Markdown preserves readable, searchable text."""
from common import ROOT, config, esc, write_changed


def render() -> str:
    c = config()
    images = {
        "hero.svg": "SURGE — animated terminal boot and original systems identity",
        "info-card.svg": "Current focus: AI agents, accounting automation, GST reconciliation and business systems",
        "projects.svg": "ELVARC, FORGE, AccuTax and AI Review Platform — systems in development",
        "contribution-heatmap.svg": f"Actual public GitHub contribution calendar for {c['username']}",
    }
    def image(name: str) -> str:
        return f'<p align="center">\n  <img src="./assets/{name}" width="640" alt="{esc(images[name])}" />\n</p>\n'
    parts = ["<!-- Generated from profile.json by scripts/generate_readme.py. Edit the config, not this file. -->\n",
             image("hero.svg"),
             f'<p align="center"><b>{esc(c["positioning"])}</b></p>\n',
             f'<p align="center">{esc(c["statement"])}</p>\n',
             "I work with accounting operations and build software and AI systems around real-world business workflows.\n",
             image("info-card.svg"), image("projects.svg"),
             "### Systems in progress\n"]
    for item in c["projects"]:
        name = f'[{item["name"]}]({item["url"]})' if item.get("url") else f'**{item["name"]}**'
        parts.append(f'- {name} · {item["status"].lower()} — {item["description"]}\n')
    parts += ["\n### Accounting automation\n",
              "Tally automation · Zoho Books · GST reconciliation · Bank reconciliation · Financial statement preparation · Data processing · Accounting workflow automation · AI-assisted accounting review · n8n automation · API integrations.\n",
              "\n### Engineering\n",
              "Repository-backed tools: **" + " · ".join(c["verified_stack"]) + "**.\n",
              "Profile tooling: **" + " · ".join(c["profile_stack"]) + "**. Self-contained assets, reproducible builds, daily activity refresh.\n",
              image("contribution-heatmap.svg"),
              f'Activity comes from [@{c["username"]}](https://github.com/{c["username"]})’s public GitHub calendar and is refreshed daily. It reflects what GitHub makes visible, not a claim of project deployment or a productivity score.\n',
              "\n<details>\n<summary>Static / reduced-motion version and profile architecture</summary>\n\n",
              "Animations honor reduced-motion preferences in supporting browsers. Fully static alternatives:\n\n",
              "[Identity](./assets/static/hero.svg) · [Focus](./assets/static/info-card.svg) · [Projects](./assets/static/projects.svg) · [Activity](./assets/static/contribution-heatmap.svg)\n\n",
              "[How this profile works](./docs/DEVELOPMENT.md) · [Research and accuracy notes](./docs/REFERENCE.md)\n\n</details>\n"]
    return "\n".join(parts)


if __name__ == "__main__":
    changed = write_changed(ROOT / "README.md", render())
    print("README.md: " + ("generated" if changed else "unchanged"))
