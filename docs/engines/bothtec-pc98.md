---
title: "Bothtec PC-98 adventure engine (working title)"
description: "The in-house engine behind Bothtec's PC-9801 adventure games, documented from Ranma ½: Hiryuu Densetsu."
type: engine
status: draft
confidence: mixed
tags:
  - bothtec
  - pc-98
  - adventure
aliases:
  - Bothtec engine
platforms:
  - PC-9801
games: []
formats: []
maturity: partial
sources:
  - title: "MAME msxr_flop software list"
    url: https://github.com/mamedev/mame/blob/master/hash/msxr_flop.xml
  - title: "Hoot driver notes for Bothtec"
    url: https://kurohane.net/hoot/txt/bothtec.txt
  - title: "TCRF: Ranma ½ Hiryuu Densetsu (MSX turboR)"
    url: https://tcrf.net/Ranma_%C2%BD:_Hiryuu_Densetsu_(MSX_turbo-R)
last_verified: 2026-11-24
ai_assisted: true
---

# Bothtec PC-98 adventure engine (working title)

Bothtec's own adventure system for the PC-9801: plain real-mode DOS executables, loose data files instead of a single archive, and a picture format built directly on PC-98 video memory. It has no published name. "Bothtec PC-98 adventure engine" is a working title taken from the only developer string the executables carry, `bothtec` in `OPENING.APL`.

## At a glance

| Field | Value |
| --- | --- |
| Kind | Adventure engine, in-house, closed |
| Platform | PC-9801 |
| Distribution | Eight floppy disks; loose files, one extension per data type |
| Code | Real-mode DOS `MZ` executables; no bytecode layer found |
| Pictures | Headerless four-plane 640 × 400 sets, and `.A98`/`.ANI` files with a small header |
| Music | `.MDS` songs played through `FMTONE.COM` / `PSGTONE.COM` / `SEDATA.COM` |
| Status here | Picture format decoded and converted; containers partly mapped; text location unknown |
| Maturity | partial |
| Confidence | mixed |

## Why it matters

The PC-98 adventure library is large and mostly undocumented, and this engine is a gap in the published lists: the usual PC-98 engine surveys skip Bothtec entirely, and `.A98` is documented elsewhere only for an unrelated archive format that happens to share the extension. A game that keeps its data in loose, individually named files is also unusually readable — 456 animation files, 47 pictures and 60 songs are each addressable without an archive layer, so the only real work is per-format layout rather than container cracking.

It also has a self-documenting corner. Disk 8 of the inspected copy holds three pictures that were cut from the game, `VIEW.COM` to display them, and `README.DOC` explaining the naming and the palette. Bothtec shipped that deliberately, which gives a first-party reference for the picture format and a model for what the rest of the data probably looks like.

## Evidence from this project

| Claim | Level | Basis |
| --- | --- | --- |
| Engine runs plain DOS `MZ` executables, not a bytecode VM | observed | `file(1)` on `MAIN.APL` and `OPENING.APL`; both are `MS-DOS executable, MZ` |
| Developer string `bothtec` at offset 24,778 in `OPENING.APL` | observed | ASCII and Shift-JIS string search |
| Engine is not Ides, KENJI, Panda House, Compile or Wolf Team | observed | Signature sweep for `TC0`, `KENJI`, `PIYO`, `WOLF`, `Programed by` across all eight disks: no hits |
| Pictures on disk 8 are four raw planes plus one palette | observed | 32,000-byte files, plus `README.DOC` naming them, `VIEW.COM` and `ranma.alg` |
| A four-plane set converts to the expected 640 × 400 artwork | observed | Converter output checked visually |
| `.A98`/`.ANI` carry a 6-byte count and size prefix | inferred | The `u32` equals file size minus six on the two `.A98` samples; trailing six bytes unexplained |
| `.A98`/`.ANI` payloads are uncompressed | inferred | One file probed against LZSS in eight configurations; all produced fill bytes |
| No public documentation exists for this engine | observed | Searches of format trackers, PC-98 engine surveys and extractor collections returned nothing for Bothtec |
| PC-98 release 1991-12-20 | unverified | VGMdb product entry, not independently confirmed |
| PC-98 version developed by Quest Corporation | unverified | Same entry; contradicts the `bothtec` string in the executable |

## Running it today

- Mount the eight `.d88` images in a PC-98 emulator; the set is ordered and requests each disk in turn.
- To see the picture format without the game, boot MS-DOS on the extras disk, keep `RANMA.ALG` in the current directory and run `view RANMA1`. `VIEW.COM` is a first-party decoder, so anything else that reads the format can be checked against it.
- The [picture converter](bothtec-pc98/textures.md) writes BMPs from the disk 8 sets without an emulator.
- **Loader work.** [NovelVM issue #58](https://github.com/monyarm/NovelVM/issues/58) tracks a reimplementation for this engine.

## Known use

| Title | Platform | Notes |
| --- | --- | --- |
| *Ranma ½: Hiryuu Densetsu* | PC-9801 | Inspected copy: eight 1,281,968-byte `.d88` images, media marker 2HD. 1991 (VGMdb dates it 1991-12-20, unverified). |
| *Ranma ½: Hiryuu Densetsu* | MSX turboR | Separate redrawn release on eight 737,280-byte 3.5-inch disks, listed by MAME as 1992, publisher Bothtec. Not inspected. |

No dedicated game page exists for either title; the engine page carries the findings.

## What to record next

1. **Inspect the MSX turboR copy.** It is the priority for the next pass: it keeps Bothtec's habit of shipping developer notes, and its extras use formats that are already documented — a Graph Saurus `.SR7`/`.PL7` picture pair, `.DOC` files and `.RCP` music. A second Bothtec release with known-format data is the cheapest way to find out what the PC-98 `.A98`/`.ANI` payload really is.
2. Decode one `.A98` file completely and compare its payload against the four-plane layout. If it matches, one converter covers the whole game instead of 503 files.
3. Find the text. `.DAT`, `.SYS` and `.PAT` are the only files left that could hold dialogue; none has been opened.
4. Map one `.MDS` song past the `M1` name field.

## Sources

- [MAME `msxr_flop` software list](https://github.com/mamedev/mame/blob/master/hash/msxr_flop.xml) — the MSX turboR release, its publisher and disk set.
- [monyarm/NovelVM — issue #58](https://github.com/monyarm/NovelVM/issues/58) — loader work for this engine.
- [Hoot driver notes for Bothtec](https://kurohane.net/hoot/txt/bothtec.txt) — sound driver cut offsets for the MSX release.
- [TCRF: Ranma ½ Hiryuu Densetsu (MSX turboR)](https://tcrf.net/Ranma_%C2%BD:_Hiryuu_Densetsu_(MSX_turbo-R)) — the extras on the MSX disks, its Graph Saurus pictures and `.RCP` music.
