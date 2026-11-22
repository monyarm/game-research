# Game Research

A single place for my research on adventure and visual novel games: the engines they run on, the formats they use, and the evidence behind each finding.

**Read the site:** <https://monyarm.github.io/game-research/>

## What this repo is

This is a research notebook, not a game archive or an engine implementation. The Markdown in `docs/` is the source of truth. MkDocs Material turns it into a searchable static site, and GitHub Actions publishes that site to GitHub Pages.

The notes are meant to answer questions like:

- What engine or runtime does a game use?
- What do its files contain, and how are they structured?
- What is needed to run or preserve it today?
- Which parts are directly observed, which are inferred, and which are still leads?

## Current coverage

- **Flash** — SWF-based runtime; runs well in Ruffle.

The landing page at `docs/index.md` lists every engine and game with a page or a substantive note. It is updated by hand until there are enough pages to justify generated indexes.

## Evidence model

Each page carries a confidence value and a last-verified date. Claims are labelled in the body where it matters:

| Level | Meaning |
| --- | --- |
| **Observed** | Checked directly against a file, binary, disc, or reproducible test. |
| **Inferred** | Follows from observed evidence, but the conclusion itself was not directly checked. |
| **Unverified** | A lead from correspondence, a catalog, or a secondary source. |

Corrections stay visible. If a claim changes, the page records the correction instead of quietly rewriting history.

## What does not belong here

- Game data, executables, ISOs, SWF/FLV files, audio, video, or extracted assets.
- Decompiled code or leaked source.
- Private correspondence, invite links, or credentials.
- Claims that an upstream project has accepted work when it has not.

Samples are cited by name, size, and SHA-256 where possible, not committed to the repo.

## Local development

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```sh
uv sync
uv run mkdocs serve
```

Build the site exactly as CI does:

```sh
uv run mkdocs build --strict
```

`--strict` turns broken links, missing nav entries, and other warnings into build failures.

After changing dependencies, refresh the lock file:

```sh
uv lock
```

## Deployment

The workflow in `.github/workflows/pages.yml` runs on every push to `main` and on pull requests. Pull requests build and validate the site; `main` also deploys it.

In the GitHub repository settings, set **Pages → Build and deployment → Source** to **GitHub Actions**.

## License

MIT. See [LICENSE](LICENSE).

Game titles, trademarks, and any referenced assets belong to their respective owners. This repository does not distribute game data.
