# Research and accuracy notes

## Reference architecture studied

- [Build an animated GitHub profile README — Avi Vashishta](https://www.avivashishta.com/blog/build-animated-github-profile-readme)
- [Reference profile repository](https://github.com/AVIVASHISHTA29/AVIVASHISHTA29)
- Reviewed the reference README, ASCII generator, public contribution fetcher, contribution renderer, requirements, and GitHub Actions workflow.

The article's portrait preparation uses background removal, local contrast enhancement and grayscale sampling. Its ASCII generator downsamples a photo into rows, maps brightness through a density ramp, and uses staggered SVG clipping and cursors to reveal text. The information card is a hand-authored terminal/neofetch composition with a static mode. The contribution architecture uses public GitHub calendar HTML and daily repository commits to avoid third-party statistics servers.

The live reference repository is not identical to every snippet in the article: the inspected tree has stats generators rather than the article's information-card filename, and its workflow invokes a different contribution renderer. Architecture was used as inspiration, not as code to reproduce.

## Original implementation

- An original geometric S identity replaces a portrait; no photo was supplied, and no identity is inferred from an avatar.
- Generation and tests use the Python standard library. No photo-processing or scraping dependencies are required.
- Short restrained animation inside self-contained SVG images replaces elaborate per-character portrait markup.
- Actual counts are required for every date; missing tooltip text is never converted to a fake zero.
- GitHub intensity levels are preserved instead of mapping guessed count thresholds.
- Two compact calendar bands, static alternatives and native Markdown improve small-screen readability.
- Content-aware output omits changing generation timestamps and avoids no-op commits.
- Actions are SHA-pinned, pull requests are read-only, the refresh target is guarded, and no force-push occurs.

No reference code, portrait, branding, or personal profile text was copied. The inspected repository did not declare a license; the implementation was written independently.

## Account and content inspection

The confirmed account is [Surge197](https://github.com/Surge197). Before implementation, the public inventory and authenticated accessible-repository inventory were checked. There was no existing username-matching profile repository to overwrite. Public repositories were not identified as ELVARC, FORGE, or AccuTax; those project descriptions remain user-provided developing concepts without invented links. Private repository details are not published in this document or profile.

React, TypeScript, Node.js and the Gemini API are repository-backed tools, not claims of expertise. Python, SVG and GitHub Actions describe this profile implementation.

## GitHub requirements verified

- [Profile README requirements](https://docs.github.com/en/account-and-profile/how-tos/profile-customization/managing-your-profile-readme)
- [Built-in token and least-privilege permissions](https://docs.github.com/en/actions/tutorials/authenticate-with-github_token)
- [Workflow events and schedule limitations](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)

The username-matching repository must be public with a nonempty root README. Schedules run on the default branch and can be delayed or disabled after inactivity. Contribution HTML can change; refreshing must fail safely and retain the prior verified snapshot.
