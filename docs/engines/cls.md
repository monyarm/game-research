---
title: "CLS engine"
description: "The in-house engine behind Code Geass: Lost Colors, named after the cls prefixed framework classes in the PSP executable, with a scene container whose compression is still unsolved."
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
| Scene container | `OOCH` files, fixed `0x800` header, compressed payload |
| Image container | `pack` files holding GIM images |
| Scripting | Not established — the scene payloads are compressed with a scheme not yet identified |
| Audio | CRI ADX (`.ADX`, `.AFS`, `PPHD`/`PBD` banks) |
| Video | `PSMF` (`.PMF`) |
| Modern runtime | PPSSPP, from a disc image |
| Status here | Executable and containers documented; text layer undecoded, and the container is shared with games from other studios |
| Confidence | Mixed |

## Why it matters

The game is a licensed PlayStation Portable title from a small studio, and its executable separates three layers unusually cleanly. CRI supplies the audio and video and says so in its own version strings. The game itself is built on a `clsOO*` framework. Everything between those two — the scene files, the image packs, the state machine — is in-house and undocumented.

That makes it a good subject for one specific question: where does the middleware stop and the game begin? The scene container is the answer, and it is also the obstacle. Every one of the 1,454 `OOCH` files carries a payload compressed with a scheme that no standard decoder accepts, so the dialogue, the scene scripts and the graphics for the game's own screens are all behind it. Until that stream is understood, this page can describe the packaging and the executable but not the game's content.

## Evidence from this project

| Claim | Level | Basis |
| --- | --- | --- |
| The engine is an in-house `clsOO*` framework over a `clsPSP*` shim | Observed | 16 framework class names in the plaintext PSP executable |
| Audio and video are CRI middleware, not engine code | Observed | `ADXT/PSP Ver.10.05`, `ADXF Ver.7.63`, `ADXRT Ver.3.1.1` in the executable; `.ADX`, `.AFS`, `.PMF` files on the disc |
| Scene files are `OOCH` with a fixed `0x800` header | Observed | 1,454 files, `payload size = file size − 0x800` in every one, no mismatches |
| Images are `GIM` inside `pack` containers | Observed | 650 `pack` sub-blocks start `MIG.00.1PSP` |
| `ScStr` holds per-scene font resources, not script | Observed | `FONTDATF` metrics, a GIM atlas and `FONTSTLB` in every sample; no readable text in a CP932 scan |
| `OOCH` payload compression is not zlib, LZMA, bzip2, LZSS or the Socio codec | Observed | Decoder attempts listed on [Decoding the scene containers](cls/decoding.md) |
| The `OOCH` container is shared with other studios' games | Inferred | A public thread on *Sonic Riders: Zero Gravity* (PS2, Wii) reports the same magic and the same `38 18 4c 66` payload prologue, and that game ships an `OOCH` file beside a plain `.P` of the same kind |
| The `OOCH` strings in the executable are referenced nowhere | Observed | No absolute reference, no `$gp`-relative reference with `$gp = 0xf57fc`, and no pointer word in `.data`; dispatch must key off the type word at `0x04` |
| A PlayStation 2 release exists | Unverified | Catalogue data only; not inspected |

## Running it today

PPSSPP boots the game from a disc image, and also from an extracted tree of the kind inspected here, so nothing has to be repacked. That was not needed for this page: the tree carries both executables, `SYSDIR/EBOOT.BIN` encrypted (`~PSP`) and `SYSDIR/BOOT.BIN` the same program decrypted, and every finding below comes from the plaintext one.

Emulation is not a preservation answer on its own regardless — the game runs, but its text stays unreadable to anyone who is not playing it.

## Known use

| Game | Platform | Released | Notes |
| --- | --- | --- | --- |
| *Code Geass: Lelouch of the Rebellion: Lost Colors* | PSP | 2008-03-27 | Inspected. Disc `ULJS00135`, version 1.01 |
| *Code Geass: Lelouch of the Rebellion: Lost Colors* | PS2 | 2008 | Not inspected; listed by [VNDB](https://vndb.org/v1502) as a second platform |

The developer credited by VNDB is CRAFTS & MEISTER. No game page exists yet for either release.

## What to record next

1. Identify the `OOCH` payload stream. The header points at a decoded size and a small parameter block, the executable is plaintext, and a decoded container should open with the `pack` magic — so the decoder can be read out of the executable, or caught at runtime with a debugger, rather than guessed at.
2. Establish where dialogue lives once the stream decodes: in the 1,454 scene containers, or in a subset of them.
3. Check whether the PlayStation 2 release ships the same `clsOO*` framework and the same containers, or an earlier set.
4. Work out what `SE/*.PHD` and `ScStr` contribute to a scene, since both are addressed per scene name and neither holds text.

## Sources

- [VNDB — Code Geass ~Hangyaku no Lelouch~ Lost Colors](https://vndb.org/v1502) — release date, platforms, credited developer.
