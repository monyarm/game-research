---
title: "Tiger & Bunny — Hero's Day"
description: "The 2013 PlayStation Portable visual novel by D3Publisher, and what its files contain."
type: game
status: draft
confidence: mixed
tags:
  - visual-novel
  - playstation-portable
  - tiger-and-bunny
year: 2013
developers:
  - D3Publisher
publishers:
  - D3Publisher
platforms:
  - PlayStation Portable
engine: tb-d3p
formats: []
sources:
  - title: VNDB — Tiger & Bunny: Hero's Day
    url: https://vndb.org/v7899
last_verified: 2026-11-23
ai_assisted: true
---

# Tiger & Bunny — Hero's Day

*Tiger & Bunny — Hero's Day* is a visual novel for the PlayStation Portable, released in Japan in March 2013 and based on the *Tiger & Bunny* anime. The player takes the role of a hero agency's staff member, picks answers in conversation, and the chapter ends with an evaluation of how well the choice matched the character being spoken to.

It is the only title known to use the engine documented here.

## At a glance

| Field | Value |
| --- | --- |
| Year | 2013 |
| Developer | D3Publisher |
| Publisher | D3Publisher |
| Platforms | PlayStation Portable |
| Disc id | `NPJH50753`, `APP_VER` 1.02 |
| Engine | [TB_D3P](../engines/tb-d3p.md) |
| Text | Shift-JIS, uncompressed, inside the chapter data files |
| Audio | ATRAC3 (`.at3`); video in `.pmf` |
| Confidence | Mixed — formats observed, engine name inferred |

## What it is

A dialogue-driven adventure with a choice-and-evaluation loop. Each scene presents a conversation, the player picks one of several replies, and the chapter's closing screen reports whether the reply suited the character. Answering badly produces a specific failure line rather than a game over, which is why the disc carries a block of outcome text per choice.

The structure explains the files. `EVENT/` holds the answers the player can pick, `PHASE/BIN/` holds the prose those answers lead into, and `TIMESHEET/` holds the prompts and results the game shows between scenes.

## Engine and formats

The engine is documented as [TB_D3P](../engines/tb-d3p.md), an interim name taken from the build path inside the game's own data files. It is not a published name.

| Page | Covers |
| --- | --- |
| [Containers](../engines/tb-d3p/containers.md) | The section container used by nearly every data file, and a quickbms splitter |
| [Script format](../engines/tb-d3p/script.md) | The four-section chapter data file, its branch graph, outcome text and dialogue bytecode |
| [Event scripts](../engines/tb-d3p/events.md) | The choice-label files and their partially decoded bytecode |
| [Textures](../engines/tb-d3p/textures.md) | The `.TPL` paletted image format and a splitter |
| [Executable](../engines/tb-d3p/executable.md) | The stripped ELF, its path table and the missing engine banner |

No format pages exist yet for the individual structures; they are described on the engine subpages instead.

## Detection

| File | Size (bytes) | MD5 (first 5,000 bytes) | SHA-256 |
| --- | ---: | --- | --- |
| `EBOOT.BIN` | 4758624 | `8362e7ed79c424f0febfdae9296a7c93` | `2e181ceabc905e733de9f4dbf65f03c9ce03db2dac5f949c4781a323cd39626e` |
| `BOOT.BIN` | 4758273 | `6bf95a48f366bdf8af3a198c7b723c77` | `cb362771ac2494a8a098d2c3ef0d3c49da021a6d0539907505e0dc00efc77f72` |

`EBOOT.BIN` is the encrypted `~PSP` module; `BOOT.BIN` is an all-zero placeholder. Both are listed because a detection table that keys on file size alone would accept the placeholder.

The disc root also carries `UMD_DATA.BIN` and `PARAM.SFO`, which identify the release as `NPJH50753` version 1.02, requiring PSP system software 6.60.

## Evidence

Everything below was measured from one inspected copy of the Japanese release.

| Observation | Level | Basis |
| --- | --- | --- |
| `BOOT.BIN` is 4,758,273 zero bytes | Observed | Stripping NUL bytes leaves an empty file |
| `EBOOT.BIN` decrypts to a stripped MIPS ELF | Observed | Decrypted with PPSSPP's EBOOT dump; valid ELF32, entry `0x837f8` |
| The executable contains no engine or middleware banner | Observed | No toolchain or company strings survive; see [Executable](../engines/tb-d3p/executable.md) |
| Nearly every data file is one section container | Observed | Header shape parses 60+ files; see [Containers](../engines/tb-d3p/containers.md) |
| Dialogue is plaintext Shift-JIS | Observed | Speaker names, voice ids and lines decode from `PHASE/BIN/EV01DATA.BIN` |
| Textures are 8-bit paletted with an inline palette | Observed | `width × height + 1,152` equals the file size exactly |
| The event scripts were authored as CSV files | Observed | Source paths `D:/PSP/TB_D3P/deliver_tb_d3/event/csv/NN/evNNNNN.csv` remain inside the compiled chunks |
| The engine is called `TB_D3P` | Inferred | Taken from that build path; not a published name |
| The `EVENT` opcode set is partly decoded | Observed | A fixed opcode-width table cannot walk `CH00_00.EVT` past `0x9f` |

The detection rows above were produced with `tools/sample-hashes.py`, so the byte count and both hashes come from the same read.

## Running or preserving it

The game runs under PPSSPP from either the disc image or an extracted tree. Nothing on these pages changes that, and no reimplementation exists.

For reading the content, the order is:

1. Split a container with the [quickbms script](../engines/tb-d3p/containers.md) to see what a file holds.
2. Split a `.TPL` with the [texture script](../engines/tb-d3p/textures.md) to get its palette and index plane.
3. Read the dialogue directly from `PHASE/BIN/EVnnDATA.BIN`; it needs no decoder.

## Open questions

- **What the `EV00DATA.BIN` section 0 record is.** It is the only chunk on the disc that neither reads as text nor matches the chapter bytecode, and it contains repeating `ed f0` pairs with embedded asset names split by single high bytes.
- **Whether the `EVENT` opcode widths depend on context.** `CH10_00.EVT` is the largest file and the best case for a second pass.
- **What `EG` and `ED` textures are.** 97 and 8 files respectively, using prefixes that appear in no path string.
- **Whether the engine shipped with any other title.** It has no public name, so a second game would have to be recognised by its container shape.

## Sources

- [VNDB — Tiger & Bunny: Hero's Day](https://vndb.org/v7899) — release data and platform list.
