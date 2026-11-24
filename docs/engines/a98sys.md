---
title: "A98SYS (Active engine)"
description: "The A98SYS engine behind Bible Black and the rest of Active's Windows visual novels: its PAK archives, HGO scripts and image payloads."
type: engine
status: draft
confidence: mixed
tags:
  - windows
  - visual-novel
  - pak-archive
  - hgo
aliases:
  - A98SYS
  - A98 engine
  - Active engine
platforms:
  - Windows
games: []
formats: []
maturity: partial
sources:
  - title: VNDB — A98SYS engine
    url: https://vndb.org/r/engines?m=A98SYS
  - title: VNDB — Bible Black -La Noche de Walpurgis-
    url: https://vndb.org/v9
  - title: RikuKH3/bblack_transkit
    url: https://github.com/RikuKH3/bblack_transkit
  - title: HIllya51/LunaTranslator — A98SYS text hook
    url: https://github.com/HIllya51/LunaTranslator
  - title: jyxjyx1234/misc_game-chs — Negaposi translation tooling
    url: https://github.com/jyxjyx1234/misc-game-chs
  - title: Crass 0.4.14.1 — A98SYS ENGINE module
    url: https://github.com/shangjiaxuan/Crass-source/blob/master/crass-0.4.14.1/cui/A98SYS%20ENGINE/A98SYS%20ENGINE.cpp
  - title: morkt/GARbro — ArcADPACK.cs
    url: https://github.com/morkt/GARbro
  - title: monyarm/NovelVM — issue 64
    url: https://github.com/monyarm/NovelVM/issues/64
last_verified: 2026-11-24
ai_assisted: true
---

# A98SYS (Active engine)

A98SYS is the engine Active (ActiveSoft) used for its Windows visual novels. The name is the engine's own: the inspected executable carries the string `A98SYS Engine Ver.1.000701` next to `Copyright 1999-2000 (C) Active.`, and the engine reads its configuration from files named `A98SYS.ENV`, `A98CFG` and `A98PAT`.

It is a 32-bit Windows engine, not a PC-98 one, despite the `A98` prefix. It draws through DirectDraw and GDI, plays audio through DirectSound and DirectMusic, stores everything in flat PAK archives, and runs its scenes from a two-byte-opcode bytecode called HGO.

## At a glance

| Field | Value |
| --- | --- |
| Kind | In-house Windows visual-novel engine |
| Developer | Active (ActiveSoft) |
| First release tagged with it | *Tania*, 1996-11-01 (VNDB tagging, not inspected) |
| Inspected copy | *Bible Black -La noche de walpurgis-*, English release |
| Executable | `bin/bblack.exe`, PE32 i386, 319,488 bytes |
| Archives | `A98SYS.PAK`, `A98FAST.PAK`, `STREAM.PAK`; flat 16-byte-entry index, no compression |
| Scripts | `HGO`, 2-byte opcodes with typed operands, Shift-JIS strings |
| Images | `EDT` (`.TRUE` magic, 34-byte header), `SAL` and `ED8` (`.8Bit` magic, 26-byte header, palette) |
| Status here | Archives, both index variants, script header and image headers documented; HGO opcode semantics open |
| Confidence | Mixed — formats observed, engine spread partly third-party |

## Why it matters

The engine is widely used and thinly documented. VNDB tags 22 releases with it, and Crass's support list groups roughly forty more under the same heading. Container knowledge exists, but almost all of it lives inside unpackers: a Crass module last touched in 2009, a GARbro parser, and two translation toolchains. None of it is written as prose documentation, and no page anywhere states the archive or image headers as a layout.

That makes it a useful case for this notebook. The archive layout, the voice index and the image headers can all be stated from our own copy and matched field by field against those implementations; the payloads (`.EDT`, `.SAL`, `.ED8`) and the voice archives have no published description, so anything said about them here is measured, not borrowed. The HGO bytecode is the one layer where the public tooling is visibly incomplete: Crass still lists the scripts as encrypted work it never finished.

One naming trap worth stating once: `A98` also appears as a file extension in the Bothtec PC-98 game documented on the [Bothtec PC-98 page](bothtec-pc98.md). That is a picture format, not an archive. Format trackers that map `A98` to `GameRes.Formats.AdPack.PakOpener` are describing *this* engine's PAK, not AliceSoft's A98SYS resources — the two spellings collide, the engines do not.

## Evidence from this project

| Claim | Evidence level | Basis |
| --- | --- | --- |
| The engine is named A98SYS | Observed | `A98SYS Engine Ver.1.000701` and `A98SYS.ENV` in `bin/bblack.exe`; VNDB uses the same name |
| Archives use a flat 16-byte-entry index | Observed | `u16` count, then `count × 16` bytes; first data offset equals `2 + count × 16` in all three inspected archives; see [Archives](a98sys/archives.md) |
| The extractor reproduces an archive exactly | Observed | 193 files, 5,327,077 bytes from a 5,330,183-byte `A98FAST.PAK`; the difference is the 3,106-byte index |
| Two public implementations agree on the index layout | Observed | `RikuKH3/bblack_transkit` (`bblack_paktool.dpr`) and `jyxjyx1234/misc_game-chs` (`pack.py`) read the same fields |
| `VOICE.PAK` and `VOICE2.PAK` use a numbered index instead of names | Observed | `u16` `0x4000` marker, real count at 2, `8 × count` key/offset records, then `16 × count` name records; index end plus member bytes equals the file size in both; see [Archives](a98sys/archives.md#the-voice-archives) |
| `VOICE2.PAK` extracts exactly | Observed | 3,330 files, 133,077,883 bytes from a 133,157,807-byte archive, the difference being the 79,924-byte index |
| HGO files begin with a function count and 0x1c-byte names | Observed | `01.HGO` in `A98SYS.PAK`: `u32` 16, then `$sel_01`, `u32` 2, `u32` offset |
| HGO opcodes are two bytes with typed operands | Unverified | Stated by `jyxjyx1234/misc_game-chs` `HGO_FILE.py` and `opdict.py`; not yet walked against our copy |
| Dialogue is drawn through GDI `ExtTextOutA` | Inferred | `LunaTranslator`'s `engine32/A98SYS.*` hooks that call for this engine; implies system font rendering, not a bitmap font |
| Images carry `.TRUE` and `.8Bit` magics | Observed | First bytes of `EDT`, `SAL` and `ED8` members; see [Payloads](a98sys/payloads.md) |
| `EDT` members carry a 34-byte header whose three length fields reconcile | Observed | `ACTIVE.EDT` 135,128 = 34 + 0 + 91,708 + 43,386, `ARF.EDT` 3,829, `BLACK.EDT` 56 |
| `.8Bit` members carry a 26-byte header, then a 768-byte palette | Observed | `ARF_.ED8` 9,874 = 26 + 768 + 9,080, with matching arithmetic on three more members |
| A public module already decodes both image formats | Observed | Crass `A98SYS ENGINE` v0.8.0 (2009-06-06), module source in `cui/A98SYS ENGINE/`; GARbro `ArcADPACK.cs` (MIT) |
| The engine's HGO text layer is not fully solved publicly | Observed | Crass's module TODO still lists "decrypt the encrypted `.HGO` script", which would explain why the published opcode table does not walk our `01.HGO` |
| The engine shipped in the late 1990s and 2000s | Inferred | Earliest VNDB-tagged release is *Tania* (1996), latest *Bible Black: The Game II* (2011) |

## Running it today

The engine is a Windows 9x-era 32-bit program with no reimplementation here or elsewhere. Nothing on these pages replaces running it, and no emulator project lists A98SYS support.

- **Windows or Wine.** The game expects its own directory layout: `bin/bblack.exe` alongside the PAK files, and it refuses to start without `a98sys.env`.
- **Reading the content.** [Archives](a98sys/archives.md) carries a quickbms script that unpacks any PAK; [Payloads](a98sys/payloads.md) describes what the unpacked members are.
- **Text.** Dialogue lives in HGO strings, which are Shift-JIS; [Scripts](a98sys/scripts.md) documents the container and points at the public tooling that already disassembles it.
- **Loader work.** [NovelVM issue #64](https://github.com/monyarm/NovelVM/issues/64) tracks the reimplementation; it already opens the three plain archives through one `PAKFactory` and reads BGM from `STREAM.PAK`.

## Known use

VNDB's engine page lists 22 releases. The ones that matter to this notebook are the two Bible Black entries and the Negaposi discs, because public tooling exists for them.

| Title | Basis |
| --- | --- |
| *Bible Black -La Noche de Walpurgis-* (2000-07-14, r182; regular edition r12097) | VNDB tag; inspected copy here |
| *Bible Black: The Game* (2006-11-21, r183) | VNDB tag; not inspected |
| *Bible Black -The Infection-* | VNDB tag and Crass grouping; not inspected |
| *Bible Black: The Game II* (2011-06-28, r9110) | VNDB tag; not inspected |
| *Discipline -The Record of a Crusade-* (2002-08-30, r78; 2007-12-18, r96) | VNDB tag; not inspected |
| *Discipline LS* (2009-05-29) | VNDB tag; not inspected |
| *Negapoji* and its fandiscs (2008-01-25, r26906; download edition 2017-11-02, r71017) | VNDB tag; translation tooling published |
| *Arabica* (2003-11-14; download edition 2006-08-24) | VNDB tag; not inspected |
| *FEARLESS]* (2002-05-10, r4613; download edition 2006-08-24) | VNDB tag; not inspected |
| *Koi no Floating Mine* (1998-06-18) and *Designer's Collection 02* (2001-06-22) | VNDB tag; not inspected |
| *Tania* (1996-11-01, r18282; PC-9821 CD edition r18283) | VNDB tag; not inspected |
| *Tokyo Nyoshuu Shuukanjo* (1999-09-10, r22268) | VNDB tag; not inspected |
| *Which girl should I choose?* (2008-07-10, r1775) | VNDB tag; not inspected |

Crass's support list adds four producer groups under an `【A98SYS ENGINE】` heading. It is the only source that groups these titles, so treat the rows as unverified:

| Group | Titles |
| --- | --- |
| Kururi Active (くるりアクティブ) | *Discipline LS*, *Bible Black -The Infection-*, *Negapoji* & fandisc slim edition, *Mahjong Gensoukyoku* I-III slim edition, *Discipline Excellent*, *Bible Black -La noche de walpurgis-* slim edition |
| Active | *SEVEN -Sympathy for the Fairies-*, *Arabica*, *Discipline*, *Primo*, *FEARLESS]*, *Kanne no Mori*, *Negapoji* fandisc, *Active Mahjong Premium Pack*, *Meippai Asurito*, *Assassin Ann*, *Mahjong Gensoukyoku III 2001 Edition*, *Negapoji*, *Mahjong Gensoukyoku 2 2001 Edition*, *Hello Again*, *Girigiri Diet*, *Star Graduation*, *Lost Mind*, *Mahjong Gensoukyoku III*, *Bible Black* North American release, *Bible Black The Game* Japanese localisation |
| Haoh Darkness (覇王Darkness) | *Nyotai Saishuu*, *Hard Scandal* |
| Haoh (覇王) | *Kokuin* (discount edition), *Himitsu Seikatsu* (discount edition), *Boku no Miko wa Chiisana Koimai*, *Okaasan to Naisho*, *Ryoujoku Shioinin* episode 1, *Himitsu Seikatsu*, *Kokuin*, *Tsuukin Kairaku 1-2 Pack*, *Hitozuma Choukanki Club*, *Shikkoku ni Nureru Seijaku*, *Tsuukin Kairaku 2* DVD and regular, *Aigangu*, *Ura Kazoku Yuugi* |

## What to record next

1. **Walk an HGO file with our own reader.** The header is measured; the opcode set is only known from public tooling, and that tooling does not walk our `01.HGO` (`0480` never lands on a valid offset). Crass's note that the scripts are "encrypted" is the most concrete lead: compare the same function across `01.HGO` and its equivalent in the Negaposi copy to see what varies.
2. **Re-derive one image decoder.** Crass and GARbro already decompress `.EDT` and `.8Bit`, but neither has been run against our members here. `ACTIVE.EDT` and `ARF_.ED8` are small and have exact length arithmetic to check against.
3. **Resolve the voice key.** Every voice record pairs a `u32` key with an offset; the HGO call sites must name those keys. Finding one line number and its key would give the mapping.
4. **Read the `SAL`/`ED8` distinction.** Both use the `.8Bit` magic, but `SAL` members are small and numerous (264) while `ED8` members are few (33) and larger. Names suggest sprite sheets against backgrounds; that is a guess.
5. **Confirm the Haoh (覇王) attribution.** Crass groups thirteen titles under A98SYS that VNDB does not tag. One inspected Haoh executable would settle it.

## Sources

- [VNDB — A98SYS engine page](https://vndb.org/r/engines?m=A98SYS) — 22 tagged releases and their dates.
- [VNDB — Bible Black -La Noche de Walpurgis-](https://vndb.org/v9) — release data for the inspected title.
- [Wikipedia — バイブルブラック](https://ja.wikipedia.org/wiki/%E3%83%90%E3%82%A4%E3%83%96%E3%83%AB%E3%83%96%E3%83%A9%E3%83%83%E3%82%AF) — developer, publisher and release date.
- [HonestGamers — ActiveSoft](https://www.honestgamers.com/company/20116/activesoft.html) — publisher listing.
- [Crass 0.4.14.1 — `A98SYS ENGINE` module](https://github.com/shangjiaxuan/Crass-source/blob/master/crass-0.4.14.1/cui/A98SYS%20ENGINE/A98SYS%20ENGINE.cpp) — the only published decoder for `.EDT`, `.ED8` and `.sal`, and the source of the "engine developed by GEAR/Active" wording. Module version 0.8.0, 2009-06-06, alpha.
- [morkt/GARbro](https://github.com/morkt/GARbro) — `ArcFormats/ActiveSoft/ArcADPACK.cs`, MIT; handles the plain and numbered PAK variants.
- [RikuKH3/bblack_transkit](https://github.com/RikuKH3/bblack_transkit) — Delphi PAK packer, HGO text injector and per-chapter text dumps. No licence is stated in the repository.
- [HIllya51/LunaTranslator](https://github.com/HIllya51/LunaTranslator) — `engine32/A98SYS`, a text hook for this engine, GPL-3.0.
- [jyxjyx1234/misc_game-chs](https://github.com/jyxjyx1234/misc-game-chs) — Negaposi translation pipeline with `pack.py`, `HGO_FILE.py`, `opdict.py`, `dump.py`. No licence is stated in the repository.
- [Artikash/Textractor PR #1138](https://github.com/Artikash/Textractor/pull/1138) — an A98SYS hook, merged into community builds.
- [sugoi-toolkit-official/sugoi-hook](https://github.com/sugoi-toolkit-official/sugoi-hook) — lists `A98sys` with an `A98sysHook`.
- [Visual Novel Compatibility List](https://vnwiki.xyz/visual-novel-compatibility-list.html) — runs the two Bible Black-era titles through Docker/Caffe with `directmusic`.
- [Crass support list](https://github.com/sealist/Arianrhod/blob/master/Source/sources/Crass-source/crass-0.4.14.1/support_list.txt) — third-party engine grouping, section `【A98SYS ENGINE】`.
- [monyarm/NovelVM — issue #64, "Support Bible Black engine family"](https://github.com/monyarm/NovelVM/issues/64) — the loader work for this engine.
