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
| [A98SYS (Active engine)](engines/a98sys.md) | Visual novel engine (in-house, Windows) | *Bible Black* and about 20 more Active titles | Flat PAK archives with a 16-byte index, HGO bytecode, `.TRUE`/`.8Bit` images; voice archives still unread. |
| [AliceSoft System 3.x](engines/alicesoft-system3-x.md) | Visual novel engine (in-house, Windows) | Around 100 releases, including *Kichikuou Rance*, *Daiakuji*, *Tsumamigui 2* | Compiled bytecode with a per-title `.ain` module manifest; two open GPL runtimes, plus a handful of patches worth lifting. |
| [HoneyBee (Sugar Sugar Rune engine)](engines/honeybee.md) | Visual-novel / dress-up adventure engine (in-house) | *Sugar Sugar Rune: Koi mo Oshare mo Pick-Up!* | Four CRI AFS archives named from an executable manifest, `#AM*` object and texture blocks, `.PAC` command bytecode; internal name only. |
| [Bothtec PC-98 adventure engine (working title)](engines/bothtec-pc98.md) | Adventure engine (in-house) | *Ranma ½: Hiryuu Densetsu* (PC-9801, MSX turboR) | Loose files on eight floppies, plain DOS executables; headerless four-plane pictures decoded, `.A98`/`.ANI` containers partly mapped. |

## Games

| Game | Engine | Notes |
| --- | --- | --- |
| [*Zero no Tsukaima: Koakuma to Harukaze no Concerto*](https://vndb.org/v104) | [Soalo](engines/zero-no-tsukaima-soalo.md) | Marvelous Entertainment; PS2; 2007-02-15, `SLPS-25708`. |
| [*Zero no Tsukaima: Muma ga Tsumugu Yokaze no Fantasy*](https://vndb.org/v216) | [Soalo](engines/zero-no-tsukaima-soalo.md) | Marvelous Entertainment; PS2; 2007-11-29, `SLPS-25830`/`SLPS-25831`. |
| [*Zero no Tsukaima: Maigo no Period to Ikusen no Symphony*](https://vndb.org/v1275) | [Soalo](engines/zero-no-tsukaima-soalo.md) | Marvelous Entertainment; PS2; 2008-11-06, `SLPS-25898`. |
| [*Code Geass: Lost Colors*](https://vndb.org/v1502) | [CLS](engines/cls.md) | Crafts & Meister; PSP `ULJS-00135` (inspected) and PS2; 2008-03-27. |
| [*Tiger & Bunny — Hero's Day*](https://vndb.org/v7899) | [TB_D3P](engines/tb-d3p.md) | D3Publisher; PSP `NPJH50753` (inspected); 2013-03-20. |
| [*Bible Black -La Noche de Walpurgis-*](https://vndb.org/v9) | [A98SYS](engines/a98sys.md) | ActiveSoft; Windows; 2000-07-14; English release inspected. |
| [*Bible Black -The Infection-*](https://vndb.org/v1030) | [A98SYS](engines/a98sys.md) | ActiveSoft; Windows; not inspected. |
| *Scooby-Doo! Case File #3: Frights! Camera! Mystery!* | [Scooby-Doo! Case File #3: Flash runtime](engines/scooby-doo-case-file-3-flash.md) | The Learning Company; Windows 2000/XP; 2007 CD-ROM; disc required. |
| [*Sugar Sugar Rune: Koi mo Oshare mo Pick-Up!*](https://vndb.org/v27013) | [HoneyBee](engines/honeybee.md) | Dimps Corporation; PS2; 2005-12-15, `SLPS-25587`. |
| [*Ranma ½: Hiryuu Densetsu*](engines/bothtec-pc98.md) | [Bothtec PC-98 engine](engines/bothtec-pc98.md) | Bothtec; PC-9801 (inspected), MSX turboR; headerless four-plane pictures decoded. |

## Notes

| Note | Covers |
| --- | --- |
| [VN engine corpus](engines/vn-engine-corpus.md) | 29 reimplementations/decompilations and 26 shipped executables, split into engine logic vs boilerplate vs middleware; what a new engine actually costs. |
| [Open questions](notes/open-questions.md) | What is still not established on each engine page, and what evidence would close it. |

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
