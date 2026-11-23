---
title: Game Research
description: "Research notes on adventure and visual novel games, their engines, and their formats."
type: index
status: stable
confidence: observed
tags: []
sources: []
last_verified: 2026-11-22
ai_assisted: true
---

# Game Research

A single place for my research on adventure and visual novel games: the engines they run on, the formats they use, and the evidence behind each finding.

## Engines

| Engine | Kind | Games | Notes |
| --- | --- | --- | --- |
| [Scooby-Doo! Case File #3: Flash runtime](engines/scooby-doo-case-file-3-flash.md) | Multimedia runtime / SWF | *Scooby-Doo! Case File #3: Frights! Camera! Mystery!* | 117 SWFs, all v8/AVM1; stock Flash Player 8 projector; runs well in Ruffle. |
| [Soalo (Zero no Tsukaima PS2 engine)](engines/zero-no-tsukaima-soalo.md) | Adventure engine / Squirrel (Socio Art Logic library) | *Zero no Tsukaima* PS2 trilogy, plus *Kazeiro Surf* (PS2) and *GA Geijutsuka* (PSP) | `.BIN`/`.HD` record pairs, Squirrel 2.1.2–2.2.4 scripting, compressed TIM2 blocks on PS2; internal name only. |

## Games

| Game | Engine | Notes |
| --- | --- | --- |
| [*Zero no Tsukaima: Koakuma to Harukaze no Concerto*](https://vndb.org/v104) | [Soalo](engines/zero-no-tsukaima-soalo.md) | Marvelous Entertainment; PlayStation 2; 2007-02-15, limited edition `SLPS-25708`. |
| [*Zero no Tsukaima: Muma ga Tsumugu Yokaze no Fantasy*](https://vndb.org/v216) | [Soalo](engines/zero-no-tsukaima-soalo.md) | Marvelous Entertainment; PlayStation 2; 2007-11-29, `SLPS-25830`/`SLPS-25831`. |
| [*Zero no Tsukaima: Maigo no Period to Ikusen no Symphony*](https://vndb.org/v1275) | [Soalo](engines/zero-no-tsukaima-soalo.md) | Marvelous Entertainment; PlayStation 2; 2008-11-06, `SLPS-25898`, limited `SLPS-25897`, Best `SLPS-25948`. |
| *Scooby-Doo! Case File #3: Frights! Camera! Mystery!* | [Scooby-Doo! Case File #3: Flash runtime](engines/scooby-doo-case-file-3-flash.md) | The Learning Company branding; Windows 2000/XP; 2007 CD-ROM re-release; disc required. |

## How to read these notes

- **Observed** — checked directly against a file, binary, disc, or reproducible test.
- **Inferred** — follows from observed evidence, but the conclusion itself was not directly checked.
- **Unverified** — a lead from correspondence, a catalog, or a secondary source.

Every page carries a confidence value and a last-verified date. Corrections stay visible instead of being quietly rewritten.

## What belongs here

- Engine and runtime notes.
- File-format notes backed by samples and hashes.
- Game notes that connect a title to its engine and formats.
- Method notes for dumping, parsing, testing, and preserving the above.

## What does not belong here

- Game data, executables, ISOs, SWF/FLV files, audio, video, or extracted assets.
- Decompiled code or leaked source.
- Private correspondence, invite links, or credentials.
