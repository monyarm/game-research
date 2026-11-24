---
title: "CLS engine"
description: "The in-house engine behind Code Geass: Lost Colors, named after the cls prefixed framework classes in the PSP executable, with a scene container that decodes to a plain pack file."
type: engine
status: draft
confidence: mixed
tags:
  - playstation-portable
  - playstation-2
  - adventure-game
aliases:
  - CLS
  - clsOO
sources:
  - title: VNDB — Code Geass ~Hangyaku no Lelouch~ Lost Colors
    url: https://vndb.org/v1502
last_verified: 2026-11-23
ai_assisted: true
platforms:
  - PlayStation Portable
  - PlayStation 2
games: []
formats: []
maturity: partial
---

# CLS engine

CLS is the engine that runs *Code Geass: Lelouch of the Rebellion: Lost Colors*, an adventure game released on 2008-03-27 for the PlayStation Portable and the PlayStation 2. The name is taken from the class prefix it puts on its own framework — `clsOOGraphics`, `clsOOSystem`, `clsOOFontSystem`, `clsOOVramHeap`, and a thin `clsPSP*` layer under them. It is not a published name and no public source uses it.

Only the PSP release has been inspected. The PlayStation 2 release exists and is listed under [Known use](#known-use), but nothing here was measured from it.

## At a glance

| | |
| --- | --- |
| Kind | Adventure-game engine, in-house, layered over CRI middleware |
| Platforms | PlayStation Portable (inspected), PlayStation 2 (not inspected) |
| Scene container | `OOCH` files, fixed `0x800` header, LZSS payload that decodes to a `pack` file |
| Image container | `pack` files holding GIM images |
| Scripting | Not established — text is stored as glyph indices in `ScStr/<scene>.P`, but the control flow around it is not read |
| Audio | CRI ADX (`.ADX`, `.AFS`, `PPHD`/`PBD` banks) |
| Video | `PSMF` (`.PMF`) |
| Modern runtime | PPSSPP, from a disc image |
| Status here | Executable, containers, the `OOCH` codec and the scene text documented; the cell attributes and the scene containers' own records unread; the container is shared with games from other studios |
| Confidence | Mixed |

## Why it matters

The game is a licensed PlayStation Portable title from a small studio, and its executable separates three layers unusually cleanly. CRI supplies the audio and video and says so in its own version strings. The game itself is built on a `clsOO*` framework. Everything between those two — the scene files, the image packs, the state machine — is in-house and undocumented.

That makes it a good subject for one specific question: where does the middleware stop and the game begin? The scene container is the answer. Every one of the 1,454 `OOCH` files carries a compressed payload, and all of them decode to a plain `pack` file, so the dialogue, the scene scripts and the graphics for the game's own screens are one documented transform away rather than locked. What the decoded files contain is the next question, not a blocked one.

## Evidence from this project

| Claim | Level | Basis |
| --- | --- | --- |
| The engine is an in-house `clsOO*` framework over a `clsPSP*` shim | Observed | 16 framework class names in the plaintext PSP executable |
| Audio and video are CRI middleware, not engine code | Observed | `ADXT/PSP Ver.10.05`, `ADXF Ver.7.63`, `ADXRT Ver.3.1.1` in the executable; `.ADX`, `.AFS`, `.PMF` files on the disc |
| Scene files are `OOCH` with a fixed `0x800` header | Observed | 1,454 files, `payload size = file size − 0x800` in every one, no mismatches |
| Images are `GIM` inside `pack` containers | Observed | 650 `pack` sub-blocks start `MIG.00.1PSP` |
| `ScStr` holds the scene's text as glyph indices | Observed | All 646 files parse as three blocks; `FONTDATF` maps index to codepoint and `FONTSTLB` holds 29,461 lines, decoded by the script on [CLS archives and containers](cls/archives.md) |
| `OOCH` payloads decode to `pack` with a bit-flagged LZSS stream | Observed | All 1,454 files reach the declared size and start with the `pack` magic; the script is on [Decoding the scene containers](cls/decoding.md) |
| The `OOCH` container is shared with other studios' games | Inferred | A public thread on *Sonic Riders: Zero Gravity* (PS2, Wii) reports the same magic and the same `38 18 4c 66` payload prologue, and that game ships an `OOCH` file beside a plain `.P` of the same kind |
| The container is dispatched by comparing its magic | Observed | The routine at file offset `0x2d704` compares the first word with the `OOCH` string at file offset `0xed814`; the `pack` counterpart is at `0x2e480` with `0xed81c` |
| A PlayStation 2 release exists | Unverified | Catalogue data only; not inspected |

## Running it today

PPSSPP boots the game from a disc image, and also from an extracted tree of the kind inspected here, so nothing has to be repacked. That was not needed for this page: the tree carries both executables, `SYSDIR/EBOOT.BIN` encrypted (`~PSP`) and `SYSDIR/BOOT.BIN` the same program decrypted, and every finding below comes from the plaintext one.

Emulation is not a preservation answer on its own regardless — the game runs, but its text stays unreadable to anyone who is not playing it.

**Loader work.** [NovelVM issue #90](https://github.com/monyarm/NovelVM/issues/90) tracks a reimplementation for this engine.

## Known use

| Game | Platform | Released | Notes |
| --- | --- | --- | --- |
| *Code Geass: Lelouch of the Rebellion: Lost Colors* | PSP | 2008-03-27 | Inspected. Disc `ULJS00135`, version 1.01 |
| *Code Geass: Lelouch of the Rebellion: Lost Colors* | PS2 | 2008 | Not inspected; listed by [VNDB](https://vndb.org/v1502) as a second platform |

The developer credited by VNDB is CRAFTS & MEISTER. No game page exists yet for either release.

## What to record next

1. Read the 4-byte cell attribute that precedes every glyph index in `FONTSTLB`. It is `0` almost everywhere, with `1` and `9` scattered through the records, and it is the only field in the text that is still unexplained.
2. Establish what the per-glyph `u32` metrics in `FONTDATF` mean, and why the `u16` at `FONTSTLB + 0x0c` is `101` in all 646 files.
3. Map scene ids to file names: `root/` and `ScStr/` use the same families (`A###`, `F###`, `G###`, `J###`, `K###`, `BTL###`, `OP`, `OMKALL`) with different prefixes, and the pairing is not established.
4. Read the scene containers themselves (`A###J.P` and the rest). They hold no strings, but they are the only candidate for the control flow that drives the text.
5. Check whether the PlayStation 2 release ships the same `clsOO*` framework and the same containers, or an earlier set.

## Sources

- [VNDB — Code Geass ~Hangyaku no Lelouch~ Lost Colors](https://vndb.org/v1502) — release date, platforms, credited developer.
- [monyarm/NovelVM — issue #90](https://github.com/monyarm/NovelVM/issues/90) — loader work for this engine.
