# AGENTS.md

This repository is a public research notebook about adventure and visual novel games. It is built as a MkDocs Material site and deployed to GitHub Pages. The Markdown in `docs/` is the source of truth; `site/` is generated and never edited by hand.

The goal is not to collect games. The goal is to explain how they work, what their files contain, and what the evidence is.

## Current scope

The only content page is `docs/engines/scooby-doo-case-file-3-flash.md`.

Do not add engines, games, formats, companies, guides, or notes unless the user explicitly asks for them. Do not expand scope from a reference repository, a catalog lead, or a passing mention. A single strong page is better than a site full of stubs.

When the user does ask for a new page, follow the page rules below and add it to the landing page and `mkdocs.yml` nav.

## Non-negotiables

1. **Evidence before prose.** Every factual claim must be observed, inferred with stated reasoning, or marked unverified. Do not turn a lead into a finding.
2. **Never fabricate.** No invented playtests, hashes, offsets, version numbers, source quotes, or compatibility results. If something was not checked, say so.
3. **No game data.** Do not commit executables, ISOs, disc images, SWF/FLV files, audio, video, extracted assets, screenshots of copyrighted material, or save files.
4. **No decompiled code or leaked source.** Discuss behaviour and formats in original prose. Do not paste decompiler output, disassembly, or reconstructed source.
5. **No copying from reference repositories.** Reference material is for orientation only. Write original prose, cite public sources, and do not reproduce another project's structure, wording, code, or assets.
6. **Do not name reference material in site content** unless the user explicitly asks for that citation.
7. **Corrections stay visible.** If a claim changes, add a dated correction. Do not silently rewrite a reviewed finding.
8. **No upstream claims.** Do not imply that a runtime, emulator, or upstream project has accepted, merged, or endorsed anything here.
9. **Private stays private.** Do not publish private correspondence, invite links, email addresses, credentials, or unannounced repositories.
10. **Credit the human.** The maintainer is Simeon Armenchev (monyarm). AI assistance is disclosed in frontmatter, not used to claim authorship of research.

## Repository layout

```text
.
├── AGENTS.md
├── README.md
├── LICENSE
├── mkdocs.yml
├── pyproject.toml
├── uv.lock
├── docs/
│   ├── index.md
│   └── engines/
│       └── scooby-doo-case-file-3-flash.md
├── .github/
│   └── workflows/
│       └── pages.yml
└── work/                 # local scratch, gitignored
```

- `docs/` — published Markdown. This is the source of truth.
- `docs/index.md` — landing page. It lists every engine and game that has a page or a substantive note.
- `docs/engines/` — engine and runtime pages.
- `docs/games/` — game pages, when they exist.
- `docs/formats/` — file-format pages, when they exist.
- `work/` — gitignored scratch for notes, dumps, and test output. Nothing here is published until it is promoted into `docs/` with evidence.
- `site/` — generated output. Never edit or commit it.

## Frontmatter

Every page starts with YAML frontmatter. Use these enums exactly.

### Common fields

```yaml
---
title: "Scooby-Doo! Case File #3: Flash runtime"
description: "One sentence that explains what the page covers."
type: engine
status: draft
confidence: mixed
tags:
  - flash
  - swf
aliases:
  - Flash
sources:
  - title: Ruffle
    url: https://ruffle.rs/
last_verified: 2026-11-22
ai_assisted: true
---
```

- `title` — matches the page's single H1.
- `description` — one sentence, plain text, quoted if it contains `:`.
- `type` — `index`, `engine`, `game`, `format`, `company`, `guide`, or `note`.
- `status` — `stub`, `draft`, `reviewed`, or `stable`.
- `confidence` — `observed`, `mixed`, `inferred`, or `unverified`.
- `tags` — lowercase kebab-case strings.
- `aliases` — optional alternate names.
- `sources` — list of `{title, url}` objects. Use public, stable URLs.
- `last_verified` — absolute date, `YYYY-MM-DD`.
- `ai_assisted` — `true` if an AI helped draft or edit the page, otherwise `false`.

### Engine fields

```yaml
platforms:
  - Web
  - Windows
games: []
formats: []
maturity: documented
```

- `platforms` — human-readable platform names.
- `games` — slugs of game pages in this repo. Leave empty until a game page exists.
- `formats` — slugs of format pages in this repo. Leave empty until a format page exists.
- `maturity` — `unknown`, `identified`, `partial`, `documented`, or `implemented`.

### Game fields

```yaml
year: 2003
developers:
  - Example Studio
publishers:
  - Example Publisher
platforms:
  - Windows
engine: flash
formats: []
```

- `engine` — slug of an engine page in this repo.
- `formats` — slugs of format pages in this repo.

### Format fields

```yaml
extension: .swf
engines:
  - flash
games: []
maturity: documented
samples:
  - name: example.swf
    size: 123456
    md5_first_5k: "00000000000000000000000000000000"
    sha256: "0000000000000000000000000000000000000000000000000000000000000000"
```

- `extension` — include the leading dot.
- `samples` — cite samples by metadata only. Never commit the sample.
- `size` — exact size in bytes. This is part of the ScummVM detection pair and is not optional when a hash is present.
- `md5_first_5k` — MD5 of the first 5,000 bytes, lowercase hex. This is the hash ScummVM detection uses, paired with `size`.
- `sha256` — SHA-256 of the whole file, lowercase hex. Use it as the stable sample identity.

### Index fields

`docs/index.md` uses `type: index` and may omit engine, game, and format fields.

## Page anatomy

### Engine or runtime page

1. H1 matching `title`.
2. A short definition: what the engine is, what it runs, and why it matters.
3. `## At a glance` table: kind, primary format, scripting, modern runtime, status here, confidence.
4. `## Why it matters` — the research or preservation problem.
5. `## Evidence from this project` — a table with claim, evidence level, and basis.
6. `## Running it today` — practical steps and known limits.
7. `## Known use` — titles, only when relevant. Link a game page if one exists; otherwise say "No dedicated game page yet."
8. `## What to record next` — concrete, checkable next steps.
9. `## Sources` — public links.

### Game page

1. H1 matching `title`.
2. `## At a glance` table: year, developer, publisher, platforms, engine, formats.
3. `## What it is` — one paragraph, no marketing copy.
4. `## Engine and formats` — link the engine and format pages.
5. `## Detection` — file name, exact size, MD5 of the first 5,000 bytes, SHA-256.
6. `## Evidence` — what was checked, with hashes or paths where safe.
7. `## Running or preserving it` — practical notes.
8. `## Open questions`.
9. `## Sources`.

### Format page

1. H1 matching `title`.
2. `## At a glance` table: extension, used by, sample, maturity.
3. `## Layout` — tables for headers and records.
4. `## Fields` — one table per structure.
5. `## Detection` — sample name, exact size, MD5 of the first 5,000 bytes, SHA-256, and what was checked.
6. `## Unknowns`.
7. `## Sources`.

Detection tables pair the exact byte count with both hashes:

```markdown
| File | Size (bytes) | MD5 (first 5,000 bytes) | SHA-256 |
| --- | ---: | --- | --- |
| `example.swf` | 123456 | `00000000000000000000000000000000` | `0000...` |
```

The size/MD5 pair is what ScummVM detection tables use. The SHA-256 is the whole-file identity used by this repository.

## Evidence model

Use these labels in the body when a claim's status is not obvious:

- **Observed** — directly checked against a file, binary, disc, or reproducible test. Include the sample name, exact size, MD5 of the first 5,000 bytes, full-file SHA-256, offset, or command where safe.
- **Inferred** — follows from observed evidence, but the conclusion itself was not directly checked. State the reasoning.
- **Unverified** — a lead from correspondence, a catalog, or a secondary source. Do not present it as a finding.

Page-level `confidence`:

- `observed` — all material claims are observed.
- `mixed` — a mix of observed and inferred or unverified claims.
- `inferred` — the page is mostly reasoning from other evidence.
- `unverified` — the page is a lead or a stub.

Engine and format `maturity`:

- `unknown` — not identified.
- `identified` — named and versioned, but not documented.
- `partial` — some structures or behaviour documented.
- `documented` — core structures and behaviour documented.
- `implemented` — a loader, parser, or runtime in this project handles it.

## Writing rules

- One entity per page. Do not merge two engines or two games into one page.
- Use one H1, matching the frontmatter `title`.
- Use sentence case for headings.
- Use exact game titles in italics, for example *Scooby-Doo! Case File #3: Frights! Camera! Mystery!*.
- Hex values use `0x` and lowercase digits: `0x45F3DC`.
- File sizes are decimal bytes unless a binary unit is explicitly useful.
- SHA-256 values are lowercase hex, in backticks.
- MD5 values are lowercase hex, in backticks. Never give an MD5 without saying which bytes it covers. For ScummVM detection, record the MD5 of the first 5,000 bytes and the exact file size together.
- Dates are absolute: `2026-11-22`, not "last week".
- Prefer tables for fields, offsets, and evidence.
- Link sources inline; do not leave bare URLs in body prose.
- No marketing language, no "revolutionary", no "obviously", no "clearly proves".
- Do not use a footnote to hide a weak claim. Put the evidence level in the sentence or table.
- Do not write "TODO" on a `reviewed` or `stable` page. Use `## Open questions` instead.
- Keep corrections visible:

```markdown
!!! correction "Correction (2026-11-22)"
    Earlier versions of this page said X. The observed value is Y.
```

## Landing page and navigation

`docs/index.md` is the public index. It must list:

- Every engine page under `## Engines`.
- Every game page under `## Games`.
- A game that is only covered inside an engine page, with a note that no dedicated page exists yet.

When adding a page:

1. Add the Markdown file under the correct directory.
2. Add a row to the matching table in `docs/index.md`.
3. Add a nav entry in `mkdocs.yml`.
4. Run `uv run mkdocs build --strict`.

Do not hand-edit generated output in `site/`. There is no generated index yet; the landing page is manual on purpose.

## Commands

```sh
uv sync
uv run mkdocs serve
uv run mkdocs build --strict
```

- `uv sync` installs the locked dependencies into `.venv`.
- `uv run mkdocs serve` serves the site at `http://127.0.0.1:8000/`.
- `uv run mkdocs build --strict` is the gate. It must pass before a commit is considered done.
- After changing `pyproject.toml`, run `uv lock` and commit the updated `uv.lock`.

## Git and deployment

- Work on `main` for small docs changes; use a branch for anything larger.
- Commit messages describe the research change, not the tooling: `docs: add Case File #3 Flash runtime note`.
- Do not commit `site/`, `.venv/`, `work/`, caches, or game data.
- The Pages workflow builds on pull requests and deploys on `main`.
- GitHub Pages source must be set to **GitHub Actions** in repository settings.
- Do not force-push `main` after the site is live.

## Gotchas

- MkDocs paths are case-sensitive on Linux. Use lowercase kebab-case filenames.
- Relative links are resolved from the current page's directory. From `docs/games/foo.md`, an engine page is `../engines/scooby-doo-case-file-3-flash.md`.
- A link to a page that is not in `nav` still builds, but it will not appear in navigation. Add the nav entry.
- `mkdocs build --strict` fails on broken internal links and unrecognized nav entries. Fix the link; do not disable strict mode.
- YAML frontmatter breaks on unquoted `:` and `!`. Quote descriptions and titles that contain them.
- Do not add a second H1 to create a subtitle. Use `##`.
- Do not put game data in `docs/assets/`. Text and diagrams only.
- Do not use an image of a game screen as evidence unless the user explicitly asks and the rights situation is clear.
- Do not mention private repositories, private branches, or unpublished correspondence.

## AI policy

- AI may draft prose, scaffolding, and checks.
- AI must not invent research results, hashes, playtests, quotes, or source contents.
- AI-assisted pages set `ai_assisted: true`.
- This repository does not contain AI-authored engine code. It is a documentation project.
- If a note discusses ScummVM or another upstream project, follow that project's AI guidelines. This repository does not imply upstream acceptance, authorship, or maintainership.

## Definition of done

A docs change is done when:

- The page follows the frontmatter schema and page anatomy.
- Every material claim has an evidence level or a source.
- `docs/index.md` and `mkdocs.yml` are updated.
- `uv run mkdocs build --strict` passes.
- No game data, secrets, private links, or copied reference material were added.
- `ai_assisted` is set correctly.
