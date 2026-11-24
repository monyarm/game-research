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
| [Scooby-Doo! Case File #3: Flash runtime](engines/scooby-doo-case-file-3-flash.md) | Multimedia runtime / SWF | *Scooby-Doo! Case File #3: Frights! Camera! Mystery!* | 117 v8/AVM1 SWFs in a stock Flash Player 8 projector; runs well in Ruffle. |
| [Soalo (Zero no Tsukaima PS2 engine)](engines/zero-no-tsukaima-soalo.md) | Adventure engine / Squirrel (Socio Art Logic library) | *Zero no Tsukaima* PS2 trilogy, plus *Kazeiro Surf* (PS2) and *GA Geijutsuka* (PSP) | `.BIN`/`.HD` record pairs, Squirrel scripting, compressed TIM2 blocks; internal name only. |
| [CLS engine](engines/cls.md) | Adventure engine (in-house PSP/PS2 framework) | *Code Geass: Lost Colors* | `OOCH` scene containers (decoded), glyph-indexed dialogue in `ScStr`, CRI ADX audio. |
| [TB_D3P engine](engines/tb-d3p.md) | Visual novel engine (in-house) | *Tiger & Bunny — Hero's Day* | Section containers, paletted `.TPL` textures, Shift-JIS dialogue in a tagged bytecode; event opcodes partly decoded. |

## Games

| Game | Engine | Notes |
| --- | --- | --- |
| [*Zero no Tsukaima: Koakuma to Harukaze no Concerto*](https://vndb.org/v104) | [Soalo](engines/zero-no-tsukaima-soalo.md) | Marvelous Entertainment; PS2; 2007-02-15, `SLPS-25708`. |
| [*Zero no Tsukaima: Muma ga Tsumugu Yokaze no Fantasy*](https://vndb.org/v216) | [Soalo](engines/zero-no-tsukaima-soalo.md) | Marvelous Entertainment; PS2; 2007-11-29, `SLPS-25830`/`SLPS-25831`. |
| [*Zero no Tsukaima: Maigo no Period to Ikusen no Symphony*](https://vndb.org/v1275) | [Soalo](engines/zero-no-tsukaima-soalo.md) | Marvelous Entertainment; PS2; 2008-11-06, `SLPS-25898`. |
| [*Code Geass: Lost Colors*](https://vndb.org/v1502) | [CLS](engines/cls.md) | Crafts & Meister; PSP `ULJS-00135` (inspected) and PS2; 2008-03-27. |
| [*Tiger & Bunny — Hero's Day*](games/tiger-and-bunny-heros-day.md) | [TB_D3P](engines/tb-d3p.md) | D3Publisher; PSP `NPJH50753` (inspected); 2013-03-20. |
| *Scooby-Doo! Case File #3: Frights! Camera! Mystery!* | [Scooby-Doo! Case File #3: Flash runtime](engines/scooby-doo-case-file-3-flash.md) | The Learning Company; Windows 2000/XP; 2007 CD-ROM; disc required. |

## How to read these notes

- **Observed** — checked directly against a file, binary, disc, or reproducible test.
- **Inferred** — follows from observed evidence, but the conclusion itself was not directly checked.
- **Unverified** — a lead from correspondence, a catalog, or a secondary source.

Every page carries a confidence value and a last-verified date.

## What belongs here

- Engine and runtime notes.
- File-format notes backed by samples and hashes.
- Game notes that connect a title to its engine and formats.
- Method notes for dumping, parsing, testing, and preserving the above.

## What does not belong here

- Game data, executables, ISOs, SWF/FLV files, audio, video, or extracted assets.
- Decompiled code or leaked source.
- Private correspondence, invite links, or credentials.
