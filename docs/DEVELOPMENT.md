# SURGE profile — developer notes

An original, repository-hosted animated profile for `Surge197`. All identity and project copy comes from `profile.json`. There are no external image services, JavaScript, hosted statistics widgets, bundled photos, proficiency ratings, or invented metrics.

## Architecture

```text
profile.json → Python generators → README.md + assets/*.svg
GitHub public calendar → strict parser → data/contributions.json → contribution SVG
GitHub Actions → tests → live refresh → commit only changed generated files
```

- `scripts/generate_hero.py`: short, one-shot terminal boot, original architectural S monogram, restrained finite cursor animation. No portrait is implied.
- `scripts/generate_info_card.py`: current focus and systems registry.
- `scripts/generate_projects.py`: project cards with explicit development labels.
- `scripts/fetch_contributions.py`: reads GitHub’s public contribution calendar. Joins each date/intensity cell to its tooltip to obtain the actual count. Counts are never guessed from intensity. Unknown/missing tooltips, inconsistent levels, partial calendars, stale live responses, or HTTP failures stop the build and preserve prior data.
- `scripts/render_heatmap.py`: keeps GitHub’s actual intensity levels and splits the calendar into two compact week bands. Totals are calculated from the same verified day data used in the image.
- `scripts/generate_readme.py`: accessible, searchable native Markdown with complete project descriptions and local image links.
- `scripts/common.py`: deterministic SVG primitives and atomic content-aware writes.
- `scripts/validate.py`: validates XML, SVG safety, size budgets, generated content, Python syntax, and local Markdown references.
- `tests/test_profile.py`: standard-library unit tests; synthetic fixtures exist only in tests and never populate the published calendar.

Each SVG has a 640px viewBox, meaningful title/description, local system-font fallbacks, and a compact dark graphite surface. CSS keyframe animations are contained inside image SVGs, not README HTML. Reveals run once; no glow loops or aggressive flashing. Final content is the default state if animation support is absent. Supporting browsers honor `prefers-reduced-motion`; `assets/static/` provides fully static alternatives. Native Markdown remains readable on mobile, to assistive tools, and if images are unavailable.

## Local regeneration

Python 3.12 recommended. Runtime and tests use only the Python standard library: **no dependency installation is needed**.

```text
python scripts/build.py
python -m unittest discover -s tests -v
python scripts/validate.py
```

Without network access, preserve the verified data snapshot:

```text
python scripts/build.py --offline
```

Each individual generator can also be run directly. To validate an already fetched real calendar offline:

```text
python scripts/fetch_contributions.py --html-file path/to/real-calendar.html
```

The JSON deliberately does not contain a wall-clock generation timestamp. Identical source content produces identical files, rather than unnecessary commits. The displayed calendar end date makes the snapshot’s coverage visible. Public-calendar data can include anonymized private activity only when the owner has chosen to expose it through GitHub; the fetcher does not authenticate or retrieve private repository details.

## GitHub Actions

`.github/workflows/update-profile.yml` runs around **03:23 UTC / 08:53 IST daily**, manually via **Run workflow**, and on relevant source changes to `main`. Pull requests validate with read-only permissions; they do not refresh or push. Refresh is guarded to `Surge197/Surge197` so forks cannot accidentally publish back.

1. Checkout and set up Python using immutable action SHA pins.
2. Run unit tests and validate the checked-in profile.
3. Confirm the offline build is reproducible.
4. Fetch live public activity and generate/validate images.
5. Stage only `README.md`, `assets/`, and `data/contributions.json`.
6. Commit only when the staged content really changed; push without force.

The refresh job has `contents: write`; other jobs have `contents: read`. Only the built-in `GITHUB_TOKEN` is used by checkout/Git, and no PAT, secret value or email address is written into profile content. No repository secret needs to be created.

GitHub may delay scheduled runs, and can disable schedules in public repositories after 60 days of inactivity. Re-enable in Actions if necessary. A protected default branch can block direct bot pushes: permit the approved bot workflow or change the process to reviewed pull requests. Failed refreshes leave the last good committed profile intact. The workflow does not force-push or erase unrelated work.

## Customization

Edit `profile.json`, run the build, and commit the changed config/output. Add a project URL only after verifying that it is a real public destination. Keep AccuTax scoped to GST reconciliation. Keep AI Review marked as developing unless its actual deployment status changes.

To change accounts, update `username` in the config, the workflow’s exact repository guard, and publish into a **public** repository whose name exactly matches the account username. Keep a nonempty `README.md` in the root. To make the whole profile permanently static, change the README generator’s image paths to `assets/static/` and rebuild.

## Rendering limits

GitHub sanitizes README HTML, but linked SVG images can contain their own animation. Relative image paths are resolved by GitHub. GitHub image caching can delay new artwork, and a browser may replay a one-shot animation when an image reloads. This is not an interactive application and embeds no runtime code. GitHub’s public contribution HTML is not a stable API; the parser deliberately fails rather than fabricating data when markup changes.

Project descriptions are user-supplied concepts, not evidence of public repositories, customers, revenue, or deployment. The profile adds no fake public project URLs and exposes no private repository source.
