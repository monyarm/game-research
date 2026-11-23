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
games:
  - tiger-and-bunny-heros-day
formats: []
maturity: partial
sources:
  - title: VNDB — Tiger & Bunny: Hero's Day
    url: https://vndb.org/v7899
last_verified: 2026-11-23
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
| Executable | `EBOOT.BIN`, encrypted `~PSP`; `BOOT.BIN` is an all-zero placeholder |
| Container | Section container: a `u32` offset table terminated by the file size |
| Textures | `.TPL`, 8-bit paletted images with an inline 256-colour RGBA palette |
| Script | Tagged Shift-JIS bytecode inside the section container |
| Status here | Containers, textures and dialogue documented; event opcode set partial |
| Confidence | Mixed — formats are observed, engine ownership is inferred |

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

## Running it today

The game has no reimplementation here, and none is planned. What exists is enough to read its content:

- **Containers.** [Containers](tb-d3p/containers.md) carries a quickbms script that splits any section container into its parts, and it is the entry point for everything else.
- **Textures.** [Textures](tb-d3p/textures.md) describes the `.TPL` layout in full; the palette is ordinary RGBA8, so a small conversion step produces viewable images.
- **Script.** [Script](tb-d3p/script.md) documents the bytecode tags, the record layout and the voice-id convention that maps each line to an `.at3` file.
- **Events.** [Event scripts](tb-d3p/events.md) covers the choice tables, which hold the branching answers but not the prose.

Emulation remains the only way to run the game. Nothing here changes that.

## Known use

| Game | Platform | Relationship |
| --- | --- | --- |
| [*Tiger & Bunny — Hero's Day*](../games/tiger-and-bunny-heros-day.md) | PlayStation Portable | The only title this engine is known from |

No other title is claimed. The engine carries no public name and no studio banner, so a second game using it would have to be recognised by its container shape, not by its strings.

## What to record next

1. **Decode the `EVENT` opcode set.** `CH00_00.EVT` is only 955 bytes and its instruction stream starts at `0x97`. Either the widths are context-dependent or one opcode takes a variable-length operand; a second pass over `CH10_00.EVT` (the largest file, 74 choice strings) should make the pattern obvious.
2. **Establish the `EV00DATA.BIN` record body.** Section 0 of the first chapter is not text and is not the bytecode the other chapters use, so it is either a data table or a packed stream. It is the only chunk on the disc that resists reading.
3. **Check whether the two non-container GALLERY files are the same engine.** `GALLERYCHRDATABASETEXT.BIN` and `GALLERYMUSICLIST.BIN` use a count-based table instead of a section table, which is a different shape from everything else.
4. **Look for a second title.** The container is simple enough that another Japanese PSP release could plausibly use it; without a name, the test is the offset table terminated by the file size.

## Sources

- [VNDB — Tiger & Bunny: Hero's Day](https://vndb.org/v7899) — release data and platform list.
