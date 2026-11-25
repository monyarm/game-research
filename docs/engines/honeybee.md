---
title: "HoneyBee (Sugar Sugar Rune engine)"
description: "The in-house PlayStation 2 engine behind Sugar Sugar Rune: CRI AFS archives with an embedded filename manifest, #AM* object and texture blocks, and a streamed command bytecode."
type: engine
status: draft
confidence: mixed
tags:
  - playstation-2
  - cri
  - afs
  - adx
  - in-house-engine
aliases:
  - HoneyBee
  - am library
sources:
  - title: VNDB — Sugar Sugar Rune: Koi mo Oshare mo Pick-Up!
    url: https://vndb.org/v27013
  - title: NovelVM issue #60 — Support Sugar Sugar Rune engine
    url: https://github.com/monyarm/NovelVM/issues/60
platforms:
  - PlayStation 2
games: []
formats: []
maturity: partial
last_verified: 2026-11-25
ai_assisted: true
---

# HoneyBee (Sugar Sugar Rune engine)

The engine behind the PlayStation 2 release of *Sugar Sugar Rune: Koi mo Oshare mo Pick-Up!* (Dimps, 2005-12-15). It is an in-house engine built on CRI middleware: content lives in CRI **AFS** archives, models and textures use a family of `#AM*` blocks, and scenes run from a streamed command bytecode in `.PAC` files.

**HoneyBee is a working title, not a published engine name.** The inspected executable is fully stripped and names no engine anywhere; the only engine-level identifiers it does expose are the source file names it was built from: `HoneyBee.cpp` alongside `Heap.cpp`, `DefaultHeap.cpp`, `ListHeap.cpp`, `BstRand.cpp`, `pof.cpp` and `WindowRenderer.cpp`, plus an `am`-prefixed core library (`amCdFs.c`, `amMc.c`, `amMotion.c`, `amObject.c`, `amTexture.c`). Whether "HoneyBee" named the project, the engine, or one translation unit inside it is not established.

## At a glance

| | |
| --- | --- |
| Kind | Visual-novel / dress-up adventure engine, in-house |
| Primary format | CRI AFS archives, `#AM*` object and texture blocks, `.PAC` command streams |
| Scripting | Custom streamed command bytecode (`0x25`-tagged records) |
| Middleware | CRI ADXI, SFD/SFH, MPV/M2V, MPS, SUD (2004–2005 builds) |
| Modern runtime | None. No open implementation of the engine exists |
| Status here | Archives and name mapping solved; container formats partly mapped; script grammar partly decoded |
| Confidence | mixed — everything structural is observed, the engine name and the script operand grammar are inferred |

## Why it matters

Two things make this title worth writing down.

The first is the archive layer. All four CRI AFS archives ship **without filenames** — that is normal for AFS — but the executable carries a 7,113-entry filename manifest, and the manifest's order matches the AFS entry order. So a complete, correctly named extraction is possible without heuristics, and the manifest doubles as a full inventory of the game's content, including the names of every scene script.

The second is the size of the gap. There is no public tooling and no format documentation for any of it: no extractor for `#AMT`/`#AMB`/`#AMO`/`#AMM`/`.TWF`, no description of the `.PAC` command stream, and no dated reverse-engineering notes. The CRI half (AFS, ADX, Sofdec, MPEG) is well covered by existing work; the `#AM*` half and the script layer are not.

## Evidence from this project

| Claim | Level | Basis |
| --- | --- | --- |
| The four archives are CRI AFS v1 with no stored filenames | observed | `AFS\0` magic, `u32` count at offset 4, `u32` offset/size pairs from offset 8, data 0x800-aligned; entry counts 7,077 / 26 / 124 / 6,209 |
| The executable carries a 7,113-name manifest | observed | NUL-terminated strings in 16-byte-aligned slots from ELF offset `0x28f920`; first four are the AFS files themselves |
| AFS entry *i* maps to manifest name *36 + i* | inferred | Extension-class sequence of the manifest aligns monotonically with the magic-class sequence of `DATA_PS2.AFS`; the four residual mismatches are all explained (`.BIN` files whose magic is `EFFE`, `.PAC` files whose first bytes are the `0x25` opcode tag, `FNB`/`ICO` headers) |
| Gameplay code and data are split between four AFS archives | observed | `DATA_PS2.AFS` 440,100,864 bytes of models, textures, scripts and video; `BGM_AFS.AFS`, `SE_AFS.AFS` and `VO_AFS.AFS` contain only ADX audio |
| Objects, textures and animation use `#AM*` blocks | observed | `#AMT` 1,359 · `#AMP` 2,377 · `#AMM` 2,734 · `#AMO` 174 · `#AMB` 14 · `#AMG` embedded in `#AMO` |
| Scenes are a streamed command bytecode | observed | `.PAC` files begin at byte 0 with `u16 0x0025` + `u16` command + operands; 45 scene scripts and 6 binary tables |
| The engine is built on CRI middleware | observed | Version strings for CFG 1.002, CFT 1.57, M2V 1.945, MPS 1.924, MPV 1.933, SFD 1.946, SFH 1.19, SFX 2.08, SUD 0.05, all `Copyright (c) 1999-2004 CRI-MW`, plus `CRI_ADXI.IRX` in `MODULES/` |
| The developer is Dimps | unverified from the disc | VNDB release record for v27013; the executable names no company |
| The engine is called HoneyBee | inferred | `HoneyBee.cpp` is the only engine-level name in the binary; the `am` prefix names the library layer, not the engine |

## Running it today

There is nothing to run. No emulator-level compatibility notes and no engine reimplementation exist, and this page documents no playable route.

Extraction is practical, because the container layer is CRI AFS and the CRI formats (ADX audio, Sofdec video) are already covered by existing CRI tooling. The missing pieces are the `#AM*` object and texture readers and the `.PAC` script interpreter.

What was done here, on the inspected copy:

1. Read `SYSTEM.CNF` for the boot target and version.
2. Walked the four AFS tables directly (offset/size pairs; no filenames in the container).
3. Recovered the filename manifest from `SLPS_255.87` and aligned it to the archive entries to get named members.
4. Classified members by magic and by extension, then read the block headers of `#AMT`, `#AMB`, `#AMO`, `#AMP`, `#AMM`, `.TWF`, `EFFE` and `Path`.
5. Walked the `.PAC` command stream from byte 0 to recover the record shape and the text command.

The pages linked below carry the details.

| Page | Covers |
| --- | --- |
| [Executable findings](honeybee/executable.md) | `SLPS_255.87` layout, the CRI version set, the build's own module list, and the filename manifest with its AFS mapping |
| [Archives](honeybee/archives.md) | CRI AFS v1 layout for the four archives, entry counts and sizes, and the member inventory by extension |
| [Objects and textures](honeybee/objects.md) | The `#AM*` block family, `.TWF` draw descriptors, `EFFE` particle definitions, `Path` camera nodes, and the six binary `*_TABLE.PAC` files |
| [Scripts](honeybee/scripts.md) | The `.PAC` command stream: record shape, commands read so far, the dialogue text command, and what breaks a linear walk |

## Known use

*Sugar Sugar Rune: Koi mo Oshare mo Pick-Up!* — PlayStation 2, `SLPS-25587`, 2005-12-15, Dimps Corporation. This is the only title known to use the engine. The inspected copy is the Japanese release; no other platform release was checked.

No other game is claimed to use it. The `#AM*` block family is not attested anywhere else in this project's material.

## What to record next

- **Finish the command grammar.** Record widths are known for 13 commands and unknown for the rest; a linear walk dies at `0x457f` of `50,168` in `ADVENTURE_MAIN.PAC` on a record whose tag byte is still `0x25` but whose following byte is `0x06`, not `0x00`. Locating the interpreter's dispatch in `SLPS_255.87` (search for the `0x25` compare on the tag byte, then the command table) would settle every width at once. Until then the text command is the only reliably extractable layer.
- **Map `#AMT`.** One block reads as a 640×480 header followed by a 307,200-byte 8-bit payload, i.e. uncompressed indexed colour. Confirm the palette's location, whether the other `#AMT` files are compressed (CRI's own `MPS` decoder is present in the binary), and what the paired `.TWF` entry points at.
- **Map `#AMM` and `#AMP`.** Both are offset tables (stride `0x2c` and `0x14`). Establishing whether they hold model, animation or motion references turns 5,285 unnamed blocks into a usable index.
- **Find the voice-line index.** `VO_AFS.AFS` holds 6,209 identical-size ADX files, so the line table and the per-line name mapping are somewhere in `DATA_PS2.AFS`; the `SCE_*` scripts are the obvious candidates.
- **Check the `am*` naming against other Dimps titles.** If a second Dimps PS2 title ships `#AMT` and `HoneyBee.cpp`, the engine has a family and a second sample; if it does not, this stays a one-title engine. Not checked.

## Sources

- [VNDB — Sugar Sugar Rune: Koi mo Oshare mo Pick-Up!](https://vndb.org/v27013) — release date, platform and developer.
- [NovelVM issue #60](https://github.com/monyarm/NovelVM/issues/60) — the engine's loader tracking issue; links back to this page.
