---
title: "Bothtec PC-98 engine payload"
description: "What the eight disks of the inspected Bothtec release contain: executables, sound drivers, songs, pictures and the extras disk."
type: engine
status: draft
confidence: mixed
tags:
  - bothtec
  - pc-98
platforms:
  - PC-9801
games: []
formats: []
maturity: partial
sources: []
last_verified: 2026-11-24
ai_assisted: true
---

# Bothtec PC-98 engine payload

*Ranma ½: Hiryuu Densetsu* ships as loose files: no archive layer, one extension per data type, the game logic in two plain DOS executables. The census below covers all eight disks of the inspected copy, which arrived as eight 1,281,968-byte `.d88` images with media marker `0x20` (2HD) at `0x1b`.

## At a glance

| Field | Value |
| --- | --- |
| Discs | 8 `.d88` images, 1,281,968 bytes each |
| Files | Loose, no archive container |
| Executables | `MAIN.APL` 392,410 bytes, `OPENING.APL` 31,646 bytes, both `MS-DOS executable, MZ` |
| Largest data class | 456 `.ANI`, 47 `.A98` pictures |
| Confidence | mixed |

## File census

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

## Executables

| File | Size (bytes) | Observation |
| --- | ---: | --- |
| `MAIN.APL` | 392410 | `MS-DOS executable, MZ`; game logic, real-mode x86 |
| `OPENING.APL` | 31646 | `MS-DOS executable, MZ`; carries `bothtec` at offset 24,778 |
| `STARTUP.COM` | — | DOS `.COM` launcher |

No interpreter is involved: there is no bytecode container and no script file type among the eight extensions, so dialogue and scene logic live in the executables and in the two `.DAT` files rather than in a portable script layer.

## Sound

| File | Size (bytes) | Observation |
| --- | ---: | --- |
| `FMTONE.COM` | 3200 | FM sound driver |
| `PSGTONE.COM` | 1536 | PSG sound driver |
| `SEDATA.COM` | 1666 | Sound effect data/driver |

Songs are `.MDS` files with a text-ish header: `M1` followed by a 32-byte name field, for example `M1GIN-EI-DEN2 START MUSIC 01` in `GEDS15F.MDS` and `M1bokutati ha korekara3` in `BOKUTATI.MDS`, then a short pattern like `30 8a 55 04 04` and long zero runs. Disk 8 adds `BOKU_END.MDS` and `EM_01` to `EM_76`.

## Pictures

| Format | Count | State |
| --- | ---: | --- |
| [Four-plane set](textures.md) | 3 | Decoded, converter published |
| `.A98` | 47 | Header partly mapped, payload not decoded |
| `.ANI` | 456 | Header partly mapped, payload not decoded |

`.A98` and `.ANI` start with a six-byte prefix that reads as a frame count and a payload size, followed by six unidentified bytes:

| File | Size | First 12 bytes |
| --- | ---: | --- |
| `OPEN001.A98` | 27,674 | `01 00` `00 00 14 6c` `00 00 50 00 c8 00` |
| `LOGO00.A98` | 9,582 | `01 00` `00 00 68 25` `00 00 32 00 6e 00` |
| `MAIN00A1.ANI` | — | `01 00` `38 42 00 00` `00 00 27 00 c8 00` |

In the two `.A98` samples the `u32` equals the file size minus six. `0xFFFF` appears throughout as a transparent fill value. One file was probed with `lzss-tool -d` in all eight parameter combinations and produced only `0x20`/`0x00` fill, so these payloads are not LZSS in the usual configurations; the rest of the files were not probed.

## The extras disk

Disk 8 is not used by the game. `README.DOC` (914 bytes, Shift-JIS) states that it holds three pictures cut from the game — `akane1.?1`, `ranma1.?1`, `tsubasa1.?1` — with `view.com` to display them, and that `ranma.alg` is read as analog palette data and must sit in the current directory. `VIEW.COM` ships on the same disk.

| File | Size (bytes) |
| --- | ---: |
| `{AKANE1,RANMA1,TSUBASA1}.{R1,G1,E1,B1}` | 32000 each |
| `RANMA.ALG` | 96 |
| `README.DOC` | 914 |

The README is the only first-party description of the format in this project, and `VIEW.COM` is a reference decoder for it.

## Detection

| File | Size (bytes) | MD5 (first 5,000 bytes) | SHA-256 |
| --- | ---: | --- | --- |
| `MAIN.APL` | 392410 | `cf28cd0f8259f779e2bcb6054d20469c` | `18cf843f26d2bb030e7d066084714072e33c7b26d27e83ad153a0f1b24dae996` |
| `README.DOC` | 914 | `5aec7ffa0244900a2d35530dffa717ba` | `fd8133120507e7c80aa8d824772bbd56f4b0f426fc027155c0bf9e701ec60726` |

Per-file hashes from the extracted disk trees; the `.d88` container images are not listed.

## Unknowns

- **Text location.** Neither `.DAT` file has been opened, and no other file type is large enough to hold a full script.
- **`.A98`/`.ANI` payload.** Whether it is the same four planes the extras disk uses is the open question that would unlock 503 files at once.
- **The six bytes after the size field.** Candidates are position, dimensions and flags; `0x0050`/`0x00c8` and `0x0032`/`0x006e` read plausibly as 80 × 200 and 50 × 110 pixels, but that is untested.
- **`.MDS` song body.** Only the name field is understood.
- **Engine name.** No string in the payload names the engine; `bothtec` is the publisher's own name.

## Sources

No public source documents these containers. The observations come from the inspected copy; `README.DOC` is the only first-party text.
