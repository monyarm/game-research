---
title: "TB_D3P engine"
description: "The in-house engine behind Tiger & Bunny — Hero's Day on the PlayStation Portable: its section container, palette textures, event bytecode and dialogue format."
type: engine
status: draft
confidence: mixed
tags:
  - playstation-portable
  - visual-novel
  - section-container
aliases:
  - TB_D3P
platforms:
  - PlayStation Portable
games: []
formats: []
maturity: partial
sources:
  - title: VNDB — Tiger & Bunny: Hero's Day
    url: https://vndb.org/v7899
last_verified: 2026-11-24
ai_assisted: true
---

# TB_D3P engine

TB_D3P is the engine that runs *Tiger & Bunny — Hero's Day*, a visual novel released for the PlayStation Portable in 2013. The name is taken from the build path the game leaves inside its own data files — `D:/PSP/TB_D3P/deliver_tb_d3/event/csv/...` — and is used here as an interim label. It is not a published name, no public source uses it, and nothing establishes that the engine shipped with any other title.

Only one release has been inspected. Everything on these pages was measured from that copy.

## At a glance

| Field | Value |
| --- | --- |
| Kind | In-house engine with a shared container and a text bytecode |
| Platform | PlayStation Portable |
| Year | 2013 |
| Developer | D3Publisher |
| Publisher | D3Publisher |
| Disc id | `NPJH50753`, `APP_VER` 1.02 |
| Executable | `EBOOT.BIN`, encrypted `~PSP`; `BOOT.BIN` is an all-zero placeholder |
| Container | Section container: a `u32` offset table terminated by the file size |
| Textures | `.TPL`, 8-bit paletted images with an inline 256-colour RGBA palette |
| Script | Tagged Shift-JIS bytecode inside the section container |
| Audio | ATRAC3 (`.at3`); video in `.pmf` |
| Status here | Containers, textures and dialogue documented; event opcode set partial |
| Confidence | Mixed — formats are observed, engine ownership is inferred |

## What it is

A dialogue-driven adventure with a choice-and-evaluation loop, based on the *Tiger & Bunny* anime. The player takes the role of a hero agency's staff member, picks answers in conversation, and the chapter ends with an evaluation of how well the choice matched the character being spoken to. Answering badly produces a specific failure line rather than a game over, which is why the disc carries a block of outcome text per choice.

The structure explains the files. `EVENT/` holds the answers the player can pick, `PHASE/BIN/` holds the prose those answers lead into, and `TIMESHEET/` holds the prompts and results the game shows between scenes.

## Why it matters

The interesting property of this engine is that it does almost none of the things a modern engine makes visible. It has no middleware banner in the executable, no symbol names, no case-insensitive archive index, and no compression on its dialogue: the script is plaintext Shift-JIS sitting in a container, wrapped around a bytecode whose control bytes are all below `0x21` so they can never be mistaken for text.

That makes it a good demonstration of how much can be recovered from a commercial PSP title without any decompilation. Every structure on the subpages was read out of the files themselves. The one thing that could not be read — the event opcode set — is recorded as unresolved rather than guessed.

## Evidence from this project

| Claim | Evidence level | Basis |
| --- | --- | --- |
| The engine name is `TB_D3P` | Inferred | Source paths embedded in `PHASE/BIN/*.BIN` contain `D:/PSP/TB_D3P/deliver_tb_d3/`; the name is not published |
| All data files share one section container | Observed | The same header shape parses 60+ files; see [Containers](tb-d3p/containers.md) |
| Textures are 8-bit paletted images with an inline palette | Observed | Width × height + 1,152 bytes reproduces file sizes exactly; see [Textures](tb-d3p/textures.md) |
| Dialogue is plaintext Shift-JIS in a tagged bytecode | Observed | Speaker names, voice ids and lines decode from `PHASE/BIN/EVnnDATA.BIN`; see [Script](tb-d3p/script.md) |
| Event scripts are choice branches, not dialogue | Observed | All 11 `EVENT/*.EVT` files yield only answer options; see [Event scripts](tb-d3p/events.md) |
| The event opcode set is not fully decoded | Observed | A fixed opcode-to-length table cannot walk `CH00_00.EVT` past offset `0x9f` |
| The executable is MetroWorks-free of identifying strings | Observed | No toolchain, middleware or engine banner survives in the decrypted ELF; see [Executable](tb-d3p/executable.md) |
| `BOOT.BIN` is 4,758,273 zero bytes | Observed | Stripping NUL bytes leaves an empty file |
| `EBOOT.BIN` decrypts to a stripped MIPS ELF | Observed | Decrypted with PPSSPP's EBOOT dump; valid ELF32, entry `0x837f8` |
| The event scripts were authored as CSV files | Observed | Source paths `D:/PSP/TB_D3P/deliver_tb_d3/event/csv/NN/evNNNNN.csv` remain inside the compiled chunks |
| The release is `NPJH50753` version 1.02, requiring PSP 6.60 | Observed | `UMD_DATA.BIN` and `PARAM.SFO` at the disc root |

## Detection

| File | Size (bytes) | MD5 (first 5,000 bytes) | SHA-256 |
| --- | ---: | --- | --- |
| `EBOOT.BIN` | 4758624 | `8362e7ed79c424f0febfdae9296a7c93` | `2e181ceabc905e733de9f4dbf65f03c9ce03db2dac5f949c4781a323cd39626e` |
| `BOOT.BIN` | 4758273 | `6bf95a48f366bdf8af3a198c7b723c77` | `cb362771ac2494a8a098d2c3ef0d3c49da021a6d0539907505e0dc00efc77f72` |

`EBOOT.BIN` is the encrypted `~PSP` module; `BOOT.BIN` is an all-zero placeholder. Both are listed because a detection table that keys on file size alone would accept the placeholder. The rows come from `tools/sample-hashes.py`, so the byte count and both hashes come from the same read.

## Running it today

The game has no reimplementation here, and none is planned. What exists is enough to read its content:

- **Containers.** [Containers](tb-d3p/containers.md) carries a quickbms script that splits any section container into its parts, and it is the entry point for everything else.
- **Textures.** [Textures](tb-d3p/textures.md) describes the `.TPL` layout in full; the palette is ordinary RGBA8, so a small conversion step produces viewable images.
- **Script.** [Script](tb-d3p/script.md) documents the bytecode tags, the record layout and the voice-id convention that maps each line to an `.at3` file.
- **Events.** [Event scripts](tb-d3p/events.md) covers the choice tables, which hold the branching answers but not the prose.

Emulation remains the only way to run the game: it boots under PPSSPP from either the disc image or an extracted tree, and nothing here changes that. For reading the content the order is: split a container, split a `.TPL` if the file holds textures, then read the dialogue straight out of `PHASE/BIN/EVnnDATA.BIN`, which needs no decoder.

## Known use

| Game | Platform | Relationship |
| --- | --- | --- |
| *Tiger & Bunny — Hero's Day* | PlayStation Portable | The only title this engine is known from |

No other title is claimed. The engine carries no public name and no studio banner, so a second game using it would have to be recognised by its container shape, not by its strings.

## What to record next

1. **Decode the `EVENT` opcode set.** `CH00_00.EVT` is only 955 bytes and its instruction stream starts at `0x97`. Either the widths are context-dependent or one opcode takes a variable-length operand; a second pass over `CH10_00.EVT` (the largest file, 74 choice strings) should make the pattern obvious.
2. **Establish the `EV00DATA.BIN` record body.** Section 0 of the first chapter is not text and is not the bytecode the other chapters use, so it is either a data table or a packed stream. It is the only chunk on the disc that resists reading.
3. **Check whether the two non-container GALLERY files are the same engine.** `GALLERYCHRDATABASETEXT.BIN` and `GALLERYMUSICLIST.BIN` use a count-based table instead of a section table, which is a different shape from everything else.
4. **Read the `EG` and `ED` texture families.** 97 and 8 files respectively, using prefixes that appear in no path string.
5. **Look for a second title.** The container is simple enough that another Japanese PSP release could plausibly use it; without a name, the test is the offset table terminated by the file size.

## Sources

- [VNDB — Tiger & Bunny: Hero's Day](https://vndb.org/v7899) — release data and platform list.
