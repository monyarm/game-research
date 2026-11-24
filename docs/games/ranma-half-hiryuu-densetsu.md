---
title: "Ranma ½: Hiryuu Densetsu"
description: "Bothtec's 1991 PC-9801 Ranma ½ adventure game, and what its eight floppy images contain."
type: game
status: draft
confidence: mixed
tags:
  - pc-98
  - bothtec
  - ranma
  - adventure
year: 1991
developers:
  - Bothtec
publishers:
  - Bothtec
platforms:
  - PC-9801
engine: []
formats:
  - bothtec-pc98-picture
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

# Ranma ½: Hiryuu Densetsu

A floppy-based adventure game that Bothtec wrote and published for the PC-9801. The inspected copy is eight `.d88` images. It runs from two plain MS-DOS executables, keeps its pictures in its own headerless four-plane format, and ships a small self-documenting extras disk that gives away part of that format.

## At a glance

| Field | Value |
| --- | --- |
| Year | 1991 (VGMdb lists 1991-12-20; not independently confirmed) |
| Developer | Bothtec |
| Publisher | Bothtec |
| Platform | PC-9801 |
| Media | Eight `.d88` images of 1,281,968 bytes each, media marker 2HD |
| Engine | In-house Bothtec system, no published name; the only developer string is `bothtec` in `OPENING.APL` |
| Pictures | `.A98` and `.ANI` with a small header; `.{R,G,E,B}1` plane sets for the extras disk |
| Music | `.MDS` songs driven by `FMTONE.COM` / `PSGTONE.COM` / `SEDATA.COM` |
| Confidence | mixed |

## What it is

An adventure game based on Rumiko Takahashi's *Ranma ½*, distributed on eight floppy disks. The executable is real-mode DOS: `MAIN.APL` and `OPENING.APL` are both plain `MZ` images, so the game logic is ordinary 16-bit x86 rather than a bytecode interpreter.

Disk 8 is an extras disk. `README.DOC` there explains that it holds three pictures that were cut from the game — `AKANE1`, `RANMA1` and `TSUBASA1` — plus `VIEW.COM` to display them and `RANMA.ALG` as their palette. No part of that path is used by the game itself, which makes it a clean reference set for the picture format.

## Engine and formats

The system is Bothtec's own and has no published name or documentation. It splits into image code, sound drivers and data:

| Part | Files | Notes |
| --- | --- | --- |
| [Four-plane picture](../formats/bothtec-pc98-picture.md) | `NAME.R1/.G1/.E1/.B1`, `.ALG` | Headerless 640 × 400 4-bit planes plus a 96-byte palette; converter published |
| Picture with header | 47 `.A98`, 456 `.ANI` | 6-byte prefix observed, payload not decoded |
| Music | 60 `.MDS` | `M1` plus a 32-byte name field, e.g. `M1GIN-EI-DEN2 START MUSIC 01` |
| Sound drivers | `FMTONE.COM`, `PSGTONE.COM`, `SEDATA.COM` | Plain `.COM` files, `file(1)` sees them as data |
| Executables | `MAIN.APL`, `OPENING.APL` | `MS-DOS executable, MZ` |

### Files on the eight disks

| Extension | Count | Role |
| --- | ---: | --- |
| `.ANI` | 456 | Animations and character graphics |
| `.COM` | 85 | Utilities and sound drivers |
| `.MDS` | 60 | Music |
| `.A98` | 47 | Full-screen pictures |
| `.ID` | 8 | One per disk |
| `.R1`/`.G1`/`.E1`/`.B1` | 3 each | The three extras-disk pictures |
| `.APL` | 3 | Executables |
| `.DAT` | 2 | Data |
| `.SYS`, `.PAT`, `.DOC`, `.BAT`, `.ALG` | 1 each | System, pattern, documentation, batch, palette |

### The `.A98` and `.ANI` header

Both extensions start with a six-byte prefix that reads as a frame count and a payload size, then six bytes that have not been identified:

| File | Size | First 12 bytes |
| --- | ---: | --- |
| `OPEN001.A98` | 27,674 | `01 00` `00 00 14 6c` `00 00 50 00 c8 00` |
| `LOGO00.A98` | 9,582 | `01 00` `00 00 68 25` `00 00 32 00 6e 00` |
| `MAIN00A1.ANI` | — | `01 00` `38 42 00 00` `00 00 27 00 c8 00` |

For the two `.A98` files the `u32` equals the file size minus six, which fits a `u16` frame count followed by a `u32` payload size. What the trailing six bytes mean is unverified, and the payload was not tested for compression beyond one probe: `lzss-tool -d` on `OPEN001.A98` with all eight parameter combinations returned 80,638 to 89,410 bytes of `0x20`/`0x00` fill from a 27,674-byte input, so these pictures are not LZSS in any of the usual configurations. `0xFFFF` appears as a transparent fill value.

## Detection

Per-file hashes from the extracted disk trees. The eight `.d88` container images are not listed.

| File | Size (bytes) | MD5 (first 5,000 bytes) | SHA-256 |
| --- | ---: | --- | --- |
| `MAIN.APL` | 392410 | `cf28cd0f8259f779e2bcb6054d20469c` | `18cf843f26d2bb030e7d066084714072e33c7b26d27e83ad153a0f1b24dae996` |
| `README.DOC` | 914 | `5aec7ffa0244900a2d35530dffa717ba` | `fd8133120507e7c80aa8d824772bbd56f4b0f426fc027155c0bf9e701ec60726` |
| `RANMA1.R1` | 32000 | `b355078e1ccd025e226b1bdd0c7cfc99` | `3920b77676030d399aecabb7fdc19ae0a13193c29a5590dcc4d96c8bc58a9769` |
| `RANMA.ALG` | 96 | `291d1d66eb7e0edfc0ede57b8add9713` | `e635828d72f2e4e721428740cf009afcf1af62aaae42469a51002c8ea8bc2244` |

## Evidence

| Observation | Level | Basis |
| --- | --- | --- |
| Eight `.d88` images, 1,281,968 bytes each, media byte `0x20` at `0x1b` | observed | Read from the container headers |
| `MAIN.APL` and `OPENING.APL` are plain `MZ` DOS executables | observed | `file(1)` on both files |
| `bothtec` appears at offset 24,778 in `OPENING.APL` | observed | String search, Shift-JIS and ASCII |
| No `KENJI`, `PIYO`, `TC0` or Wolf Team signature on any disk | observed | Same sweep across all eight disk trees |
| Pictures on disk 8 are four 32,000-byte planes plus a 96-byte palette | observed | File sizes, plus `README.DOC` naming them as the `.?1` set with `ranma.alg` |
| The planes decode to a 640 × 400 16-colour image | observed | Converter output checked visually against the expected character art |
| `.A98`/`.ANI` carry a 6-byte count and size prefix | inferred | The `u32` matches file size minus six on the two `.A98` samples |
| `.A98`/`.ANI` payloads are uncompressed | inferred | One file probed against LZSS; other files untested |
| PC-98 release date 1991-12-20 | unverified | VGMdb product entry, not independently confirmed |
| PC-98 version developed by Quest Corporation | unverified | VGMdb entry; contradicts the `bothtec` string in the executable |

Searches for existing work came back empty for this engine: the format trackers, the published PC-98 adventure-engine lists and the usual extractor collections have nothing for Bothtec, and the `.A98` extension is documented only for AliceSoft's unrelated A98SYS archive.

## Running or preserving it

- The game needs the `.d88` set mounted in a PC-98 emulator or written back to floppies; the eight images are one set and the disks are requested in order.
- `VIEW.COM` is the cheapest way to see the picture format working: boot MS-DOS, keep `RANMA.ALG` in the current directory, run `view RANMA1`.
- The published [quickbms converter](../formats/bothtec-pc98-picture.md) turns any of the disk 8 sets into a BMP without the emulator.

## Open questions

- **The MSX turboR version is the priority for the next pass.** It is a separate, redrawn release on eight 737,280-byte 3.5-inch disks (MAME lists it as 1992, Bothtec), and its extras are documented on its own terms: a Graph Saurus `.SR7`/`.PL7` picture pair, developer `.DOC` files and `.RCP` music. Because those formats are known and the release keeps Bothtec's habit of shipping its own notes, it is the better place to look for script and data layout than the PC-98 copy. That release has not been inspected yet.
- **Where the game text lives.** No file on the eight disks has been identified as holding dialogue or scene scripts. The `.DAT`, `.SYS` and `.PAT` files are the obvious next candidates.
- **What `.A98`/`.ANI` hold after the header.** If the payload is the same four planes with a header, the published converter can be extended to cover the whole game; this needs one file decoded, not all 503.
- **How `.MDS` songs are laid out.** The `M1` name field is readable, the data after it is not.
- **Whether the engine has a name.** The only developer string in the executable is `bothtec`; the VGMdb credit to Quest Corporation is unverified and may refer to another part of the work.

## Sources

- [MAME `msxr_flop` software list](https://github.com/mamedev/mame/blob/master/hash/msxr_flop.xml) — the MSX turboR release, publisher and disk set.
- [Hoot driver notes for Bothtec](https://kurohane.net/hoot/txt/bothtec.txt) — sound driver cut offsets for the MSX release.
- [TCRF: Ranma ½ Hiryuu Densetsu (MSX turboR)](https://tcrf.net/Ranma_%C2%BD:_Hiryuu_Densetsu_(MSX_turbo-R)) — the extras on the MSX disks, its Graph Saurus pictures and `.RCP` music.
