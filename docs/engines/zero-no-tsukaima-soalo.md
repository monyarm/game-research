---
title: "Soalo (Zero no Tsukaima PS2 engine)"
description: "The Squirrel-based adventure engine behind the three Zero no Tsukaima PlayStation 2 games, documented from its executables and its .BIN/.HD data pairs and since confirmed on two games from other studios."
type: engine
status: draft
confidence: mixed
tags:
  - playstation-2
  - playstation-portable
  - squirrel
  - bin-hd
  - visual-novel
  - zero-no-tsukaima
platforms:
  - PlayStation 2
  - PlayStation Portable
games: []
formats: []
maturity: partial
aliases:
  - Soalo
  - SoaloPS2
  - Socio Art Logic
sources:
  - title: VNDB — Zero no Tsukaima -Koakuma to Harukaze no Concerto-
    url: https://vndb.org/v104
  - title: VNDB — Zero no Tsukaima -Muma ga Tsumugu Yokaze no Fantasy-
    url: https://vndb.org/v216
  - title: VNDB — Zero no Tsukaima -Maigo no Period to Ikusen no Symphony-
    url: https://vndb.org/v1275
  - title: Wikipedia — Squirrel (programming language)
    url: https://en.wikipedia.org/wiki/Squirrel_(programming_language)
  - title: Squirrel programming language
    url: https://www.squirrel-lang.org/
  - title: 有限会社ソシオ・アートロジック (Socio Art Logic) — company site
    url: https://artlogic.jp/
  - title: Socio Art Logic — Game Developer Research Institute
    url: https://gdri.smspower.org/wiki/index.php/Socio_Art_Logic
  - title: Socio Art Logic — OGDB company entry
    url: https://ogdb.eu/index.php?companyid=15610&section=company
  - title: Connect Wizard — OGDB company entry
    url: https://ogdb.eu/index.php?companyid=22959&section=company
  - title: Zero no Tsukaima staff roll (raido.moe)
    url: https://raido.moe/staff/ps2/ps2_zero_no_tsukaima_1.html
  - title: punk7890/PS2-Visual-Novel-Tool
    url: https://github.com/punk7890/PS2-Visual-Novel-Tool
  - title: "[PS2] Need help figuring out what to do next! (VG Resource forum)"
    url: https://vg-resource.com/threads/ps2-need-help-figuring-out-what-to-do-next.42169/
  - title: TM2/TIM2 Image (Reverse Engineering Wiki)
    url: https://rewiki.miraheze.org/wiki/TM2_TIM2_Image
last_verified: 2026-11-23
ai_assisted: true
---

# Soalo (Zero no Tsukaima PS2 engine)

Soalo is the name this notebook uses for the unnamed PlayStation 2 engine that runs the three *Zero no Tsukaima* adventure games published by Marvelous Entertainment between 2007 and 2008. All three games use the same executable code base, the same `<NAME>.BIN` + `<NAME>.HD` data containers, and the same Squirrel scripting layer. Two later games from other studios — *Kazeiro Surf* on PlayStation 2 and *GA Geijutsuka Art Design Class* on PlayStation Portable — carry that same container pair and scripting layer and are counted as the same engine here. The name belongs to the layer under the game: `Soalo` is 有限会社ソシオ・アートロジック's own abbreviation for its library. Whether that library *is* the engine or sits as middleware beneath someone else's is not settled by these three games — see [Whose engine is it?](#whose-engine-is-it).

That these three titles are Squirrel games is already public knowledge: Wikipedia's [Squirrel article](https://en.wikipedia.org/wiki/Squirrel_(programming_language)) lists all three under "Games using Squirrel". What this notebook adds is the part that listing does not cover — which Squirrel version, how the scripts are packaged, and what the surrounding containers look like.

!!! note "Why 'Soalo'"
    All three executables contain the C++ include path `../SoaloPS2/Bit.h`, and nothing else in them names the engine. Those initials belong to the studio that wrote it: 有限会社ソシオ・アートロジック, **So**cio **A**rt **Lo**gic, a one-man contracting house in Setagaya, Tokyo, incorporated on 1995-04-05 by Shinichi Kondo (近藤慎一). `SoaloPS2` is its PlayStation 2 library, so `Soalo` is the engine's own short form rather than a name invented here. The page title carries the game family so the entry is not read as a general PlayStation 2 runtime.

    The company's own work list is explicit about where the boundary sat. For Concerto it claims the main programming and "adventure library development excluding script control" — so the `tkl*` display and container layer is Socio Art Logic's, while the script control system that drives Squirrel came from someone else. The same work list names Concerto only; company databases credit the studio on the other two games as additional programming, which fits a library reused rather than rebuilt.

    None of the games corroborate any of this. Searching every container of all three games finds no `Socio`, `Art Logic`, or other expansion — not in Shift-JIS, half-width katakana, or full-width Latin, and not in the 1,396 decompressed script and scene blocks either. The only engine-name string anywhere in the set is the `../SoaloPS2/Bit.h` include path in the three executables. The three VNDB entries list Marvelous Inc. as developer and say nothing about the engine.

## At a glance

| | |
| --- | --- |
| Kind | Visual-novel engine family on PlayStation 2 and PlayStation Portable; the display, container and codec layer is the `Soalo` library from Socio Art Logic, whether as engine or as middleware is unresolved |
| Data container | `<NAME>.BIN` payload + `<NAME>.HD` size table, six standard pairs |
| Scripting | [Squirrel](https://www.squirrel-lang.org/) — 2.1.2 on the trilogy, 2.2.2 and 2.2.4 on the two later games — with offline compilation, closure streams, and a second `.ks` scene-script layer |
| Graphics | TIM2 images wrapped in 2048-byte-aligned blocks and compressed with the Socio Art Logic stream |
| Audio | PS2 SPU ADPCM voices; sequenced music rather than pre-rendered tracks |
| Movies | PS2 MPEG-2 `.PSS` |
| Status here | Core containers, script layer, and the image/script block codec documented; the compiled scene payload still open |
| Confidence | Mixed — executables and containers are observed, several payload interpretations are inferred |

## Why it matters

Three commercial visual novels share one engine, and that engine ships most of its own script source as readable text. That makes the family unusually tractable for a documentation project: you can read the game's scene logic, its window and dialogue classes, its voice and music wrappers, and its per-character costume tables without decompiling anything.

The interesting problems are the ones still unsolved. Nothing in `SCENEDAT.BIN` or `NORMAL.BIN` is a plain TIM2 file, even though every image block decodes to one, and Concerto keeps its script library compressed inside `SCENE_ID.BIN` instead of shipping a `SYSTEM` pair. Both are real format questions, not just extraction chores.

## Evidence from this project

| Claim | Level | Basis |
| --- | --- | --- |
| The three games share one engine | Observed | Same loader strings, same `tkl*` classes, same `../SoaloPS2/Bit.h` path, same five data names in all three executables |
| The `.BIN`/`.HD` pair is a payload plus a size table | Observed | The loader opens `<NAME>.BIN` and `<NAME>.HD` by literal name; the `.HD` files are u32 size arrays that match record boundaries |
| Squirrel 2.1.2 is embedded | Observed | `Squirrel 2.1.2 stable` plus `sqapi.cpp`, `sqcompiler.cpp`, `sqvm.cpp`, `sqtable.cpp` in the Symphony and Fantasy executables; that these titles *use* Squirrel was already listed on Wikipedia, the version is measured here |
| Script source is shipped, not just bytecode | Observed | `SYSTEM.BIN` records 0–32 (Symphony) and 0–31 (Fantasy) are Shift-JIS `.nut` source with `class`, `function`, and `dofile` |
| Compiled units are stock Squirrel closure streams | Observed | The stream opens `FA FA 52 49 51 53 01` — Squirrel's closure head, then `SQIR` written backwards as `RIQS`; string resources inside it use the house tag `0x08000010` |
| Concerto keeps its library in `SCENE_ID` | Observed / inferred | Concerto's executable has no `SYSTEM` data name, and 120 sampled `SCENE_ID` blocks decode to plain Squirrel source; that it *replaces* `SYSTEM` is inferred from the missing name and the matching content |
| Image blocks decode to TIM2 | Observed | 1,950 of 1,955 `SCENEDAT` blocks in Symphony decode to a `TIM2` v4 header, and 434 of 435 in `NORMAL`; the same holds for the other two games |
| The block codec is the Socio Art Logic stream | Observed / inferred | A third-party MIT tool and a forum thread give the same command scheme, and a reimplementation of it decodes the blocks; that the company name applies to these games is external attribution |
| Socio Art Logic wrote the adventure library | Observed (external) | The studio's own work list credits Concerto to it as "main programmer, adventure library development excluding script control"; GDRI and OGDB credit it on all three games |
| The `tkl*` library appears outside the trilogy | Observed | *Kazeiro Surf* (PS2, 2009) carries thirty `tkl*` identifiers, the same six containers and the same codec, and its own Squirrel build (2.2.2) |
| The same engine runs on PSP | Observed | *GA Geijutsuka Art Design Class* (PSP, 2010) ships six `.BIN`/`.HD` pairs with the same one-word-per-record index, and its decrypted executable carries `MYZIP` and `Squirrel 2.2.4`; its payloads are MYZIP+zlib and its graphics are `GIM` rather than `TIM2` |
| Marvelous produced the series and Connect Wizard built the games | Observed (external) | Concerto's staff roll separates 製作 マーベラスインタラクティブ from ゲーム制作 コネクト・ウィザード, and lists Socio Art Logic and Wamsoft under 制作協力 |

## The three titles

| Title | Released | Serial | Script payload found |
| --- | --- | --- | --- |
| *Zero no Tsukaima: Koakuma to Harukaze no Concerto* | 2007-02-15 | `SLPS_257.08` | `SCENE_ID.BIN`, compressed source blocks |
| *Zero no Tsukaima: Muma ga Tsumugu Yokaze no Fantasy* | 2007-11-29 | `SLPS_258.30` / `SLPS_258.31` | `SYSTEM.BIN`, `.nut` source + compiled scene data |
| *Zero no Tsukaima: Maigo no Period to Ikusen no Symphony* | 2008-11-06 | `SLPS_258.98` (limited `SLPS-25897`, Best `SLPS-25948`) | `SYSTEM.BIN`, `.nut` source + compiled scene data |

The release order runs backwards against the file numbering: the 2007-02 title is `SLPS_257.08`, the 2007-11 title `SLPS_258.30`, the 2008-11 title `SLPS_258.98`. The data layout changes with it. Concerto has no `SYSTEM` pair at all, Fantasy splits into a `SYSTEM` with fewer records, and Symphony has the largest `SYSTEM`. That progression is the strongest single piece of evidence that this is one engine iterated across three releases rather than three unrelated products.

Catalogs transliterate the subtitles in more than one way. The Squirrel article and GameFAQs call the 2007-02 title "Shou-akuma to Harukaze no Concerto" and the 2007-11 title "Muma ga Tsumugu Yokaze no Nocturne"; both refer to the same games as the spellings used here.

### Credits

Nothing in the executables names a company, so these credits come from Socio Art Logic's own work list and from company databases. Treat them as catalogue data, not as something measured from the files.

| Title | Developer | Production | Programming | Publisher |
| --- | --- | --- | --- | --- |
| Concerto | Connect Wizard | — | Socio Art Logic (main), Wamsoft | Marvelous Interactive |
| Fantasy | Connect Wizard | Russel | Socio Art Logic (additional), Wamsoft | Marvelous Entertainment |
| Symphony | Connect Wizard | Russel | Socio Art Logic (additional), Wamsoft | Marvelous Entertainment |

The distinction matters for reading the binaries: the adventure library is Socio Art Logic's, while the script control system — the part that binds Squirrel to the `Talk(ch, voiceid)` call surface — is explicitly outside its contribution. Graphic and audio work is credited to other outside studios, which is consistent with the containers holding only what the library needs.

Concerto's staff roll separates the layers more precisely than the company databases do. It credits **プログラム** to A・REY and 渡邊 剛, **スクリプトワーク** to 尾上 尚志, **制作協力** to ソシオ・アートロジック, ワムソフト, スティングレイ, J.C.STAFF, アストロビジョン, スタナー and Tプロダクションスタジオ, **ゲーム制作** to コネクト・ウィザード, and **製作** to マーベラスインタラクティブ. A・REY is Shinichi Kondo's handle, so the lead programmer credit is the middleware author's; 渡邊剛 is Wamsoft, which explains the second `tkl*` programmer in the binary. The script work is Connect Wizard's.

### Whose engine is it?

This is unresolved. The measurements on this page come from three *Zero no Tsukaima* games plus two later games from another studio — *Kazeiro Surf* (PlayStation 2) and *GA Geijutsuka Art Design Class* (PlayStation Portable), both credited to Russell — and what they establish is that the `Soalo` library, the `tkl*` classes, the `.BIN`/`.HD` containers and the block codec are present in all five. Who owned the engine around that library is not something any of them can answer, and the attributions below are catalogue data rather than measurements. Two readings fit, and this notebook does not settle between them:

- **Socio Art Logic wrote the engine.** The `tkl*` classes, the `.BIN`/`.HD` containers and the block codec are all its work, and the game-specific layer is thin enough to look like configuration on top.
- **Marvelous owns the engine and licenses Soalo as middleware.** Marvelous Interactive carried the 製作 credit — the production line of a Japanese staff roll, which names the company financing and releasing the game rather than the one that programmed it — and held the series for three releases. The library would then sit where CriWare's middleware sits in hundreds of PlayStation 2 titles: a licensed component under a publisher's own engine. The staff roll supports this reading as readily as the first, since it credits three companies on three different layers.

The second reading is the harder one to argue against, because the same block codec turns up in games from unrelated publishers — TENKY, Caramel BOX, Lump of Sugar, SkyFish and Russell. A publisher's in-house engine does not travel to five competitors; a contract library does, and neither of the two inspected games outside the trilogy was published by Marvelous. What none of the games show is where the boundary sits: whether the Squirrel binding, the scene model and the action layer belong to the middleware or to whoever wrote the game. Settling that would need a build of the library itself, or a title that credits the studio while carrying none of these containers.

The third player is **Connect Wizard, Ltd.** (有限会社コネクトウィザード), a Tokyo studio founded 2001-12-06 that is credited with ゲーム制作 on all three games. Its PlayStation 2 and Portable output is small and overlaps the codec group almost exactly, which is the strongest single hint that the container set moved with one developer rather than with one publisher:

| Title | Platform | Released |
| --- | --- | --- |
| *Sotsugyou ~Next Graduation~* | PS2 | 2005-06-24 |
| *Hakarena Heart ~Ta ga Tame ni Kimi wa Aru?~* | PS2 | 2007-02-23 |
| *Sumomomo Momomo ~Chijou Saikyou no Yome~* | PS2 | 2007-06-21 |
| *Zero no Tsukaima* Concerto / Fantasy / Symphony | PS2 | 2007–2008 |
| *Kazeiro Surf* | PS2 | 2009-05-28 |
| *Strike Witches: Anata to Dekiru Koto* | PS2 | 2010-05-27 |
| *GA Geijutsuka Art Design Class: Slapstick Wonderland* | PSP | 2010-07-29 |

Five of those seven are already in the codec group below. The PSP entry matters because it is the only known PlayStation Portable title from the studio. Another 17 games credit Connect Wizard for scenario, graphics or production rather than development, which says nothing about their containers.

## Games likely to use the engine

Socio Art Logic is a one-person contracting house rather than a game studio, so its credit list runs well past this trilogy, and the block codec turns up in games from unrelated publishers. The rows below are candidates for the same library or a variant of it, confined to PlayStation 2 and PlayStation Portable, the only two platforms the library is known on. **Three of them have been inspected: *Kazeiro Surf* and *GA Geijutsuka Art Design Class* carry the same container pair and the same Squirrel layer and are counted as the same engine; *Sotsugyou* turned out to be the Windows port. Everything else is unverified.**

| Title | Platform | Released | Credited developer | Basis |
| --- | --- | --- | --- | --- |
| *Cambrian QTS ~Kaseki ni Nattemo~* | PS2 | 2003-12-11 | TENKY | shared block codec, [v16696](https://vndb.org/v16696) |
| *Shuumatsu Shoujo Gensou Alicematic* | PS2 | 2006-10-27 | Caramel BOX | shared block codec, [v492](https://vndb.org/v492) |
| *Itsuka, Todoku, Ano Sora ni.* | PS2 | 2007-01-26 | Lump of Sugar | shared block codec, [v23](https://vndb.org/v23) |
| *Hakarena Heart ~Ta ga Tame ni Kimi wa Aru?~* | PS2 | 2007-02-23 | Russell.pure | shared block codec, [v3548](https://vndb.org/v3548) |
| *Shirogane no Soleil -Successor of Wyrd-* | PS2 | 2007-03-30 | SkyFish | shared block codec, [v451](https://vndb.org/v451) |
| *Sumomomo Momomo ~Chijou Saikyou no Yome~* | PS2 | 2007-06-21 | Marvelous | shared block codec, [v26312](https://vndb.org/v26312) |
| *Kazeiro Surf* | PS2 | 2009-05-28 | Russell.pure | inspected: same containers, 30 `tkl*` names, Squirrel 2.2.2, [v4047](https://vndb.org/v4047) |
| *Strike Witches: Anata to Dekiru Koto - A Little Peaceful Days* | PS2 | 2010-05-27 | Russell | shared block codec, [v5312](https://vndb.org/v5312) |
| *Tokimeki Memorial: Girl's Side* | PS2 | 2002-06-20 | Konami, TENKY | studio credit only, [v857](https://vndb.org/v857) |
| *Tennis no Ouji-sama: Sweat & Tears 2* | PS2 | 2003-09-25 | Konami | studio credit only, [v52429](https://vndb.org/v52429) |
| *Twelve: Sengoku Fuushinden* | PSP | 2005-08-25 | TENKY | studio credit only |
| *Sotsugyou ~Next Graduation~* | PS2 | 2005-06-24 | Wonderfarm | inspected: the copy was the Windows port, no `.HD` pairs, [v4673](https://vndb.org/v4673) |
| *GA Geijutsuka Art Design Class: Slapstick Wonderland* | PSP | 2010-07-29 | Russell | inspected: same `.HD`/`.BIN` pairs, Squirrel 2.2.4 in the decrypted `EBOOT.BIN`, [v7899](https://vndb.org/v7899) |
| *Mai-HiME -Unmei no Keitouju-* | PS2 | 2005-06-30 | Marvelous, CIRCUS | publisher-era sibling, [v65](https://vndb.org/v65) |
| *School Rumble: Neru Ko wa Sodatsu.* | PS2 | 2005-07-21 | Marvelous | publisher-era sibling, [v30272](https://vndb.org/v30272) |
| *Kashimashi ~Girl Meets Girl~* | PS2 | 2006-03-30 | Marvelous, Vridge | publisher-era sibling, [v16152](https://vndb.org/v16152) |
| *School Rumble Nigakki* | PS2 | 2006-07-20 | Marvelous | publisher-era sibling, [v30273](https://vndb.org/v30273) |
| *Cluster Edge ~Kimi o Matsu Mirai e no Akashi~* | PS2 | 2006-09-14 | Marvelous | publisher-era sibling, [v23557](https://vndb.org/v23557) |
| *Princess Princess: Hime-tachi no Abunai Houkago* | PS2 | 2006-10-26 | Marvelous | publisher-era sibling, [v7855](https://vndb.org/v7855) |
| *Simoun Ibara Sensou ~Fuuin no Ri Maajon~* | PS2 | 2007-06-21 | Marvelous | publisher-era sibling, [v14637](https://vndb.org/v14637) |
| *Junjou Romantica ~Koi no Dokidoki Daisakusen~* | PS2 | 2008-11-27 | Marvelous | publisher-era sibling, [v1426](https://vndb.org/v1426) |

"Shared block codec" means punk7890's MIT tool routes the game through the same handler it labels `SocioArtLogic`, the code path it uses for the trilogy's `NORMAL.BIN`, `SCENE_ID.BIN`, and `SCENEDAT.BIN`. "Studio credit only" means the studio lists or is credited on the title, with no structural evidence either way. "Publisher-era sibling" means Marvelous published it in the same window as the trilogy but nothing ties it to the containers yet. None of those three is a measurement: the first is a third-party tool's grouping, the other two are catalogue data.

The family test applied to the two inspected games is the container pair plus the scripting layer: a game that keeps `.BIN`/`.HD` records and a Squirrel layer is the same engine, whatever the executable has been stripped of. An engine-name string and a Squirrel version number are not part of that test — the trilogy carries 2.1.2, *Kazeiro Surf* 2.2.2 and *GA Geijutsuka* 2.2.4.

### What the inspected games showed

*Kazeiro Surf* (PS2, 2009, Russell) is the cleanest confirmation: it keeps the codec and the script layer while breaking the name. It carries seven pairs — the six standard containers plus `LIST`, whose first bytes are a plain-text manifest, `[NORMAL]\r\nNORMAL\SJIS.LST`. The `.HD` sums reproduce every `.BIN` exactly under the same 2048-byte rounding, and its `TIM2` count equals the `\xE6TIM2\x04\x00\x01` marker count exactly (3,502 in `SCENEDAT`, 336 in `NORMAL`, zero elsewhere). Nothing in the executable says `Soalo`, `Socio`, or `Artlogic` — but thirty `tkl*` identifiers are present, including `tklVTextBox`, `tklDrawContext`, `tklTim2Data`, `tklPs2DrawDriver`, `tklFSAF`, `tklVImage`, `tklVClipper`, `tklMemory`, and `tklSifAllocIopHeap`. It also runs **Squirrel 2.2.2**, not 2.1.2, and its `SYSTEM.BIN` is a bare closure stream (`FA FA 52 49 51 53 01`, then `DataMake/SYSTEM/INIT.NUT` and `main`) rather than the paged source layout of the trilogy.

*GA Geijutsuka Art Design Class* (PSP, 2010, Russell) keeps the same idea with different packaging: six pairs, one `.HD` word per record with exact counts (476 scenario blocks, 2,090 images), and records beginning `00 FF "MYZIP" 00 00 00` followed by zlib, placed on 0x800-byte sector boundaries and padded with `0xFF`. The inflated records are either manifests or Squirrel closures holding readable source (`scenario/pr_00.nut`, function `main`). Graphics are `GIM`, not `TIM2` — 244 in the image container and no TIM2 at all — so the marker test is a PS2-only test. Its `EBOOT.BIN` is encrypted (`~PSP`), and the emulator's own decrypt writes it out as a 1,573,264-byte ELF, which closes the two gaps a name string would have covered: the executable carries `MYZIP`, `Squirrel 2.2.4 stable`, the `squirrel system start`/`squirrel system done` pair and the binding class `SquirrelObject`. It contains no `Soalo`, `Socio` or `tkl*` text in ASCII, Shift-JIS, UTF-16LE or UTF-8 — but it is stripped, with no symbol table and no `__FILE__` paths, so the assert file names that leak engine names on the PS2 games were never going to survive a 2010 release build. The containers and the script layer are the evidence; the absent string is not a counter-argument.

*Sotsugyou ~Next Graduation~* was a false start: the copy inspected was the Windows port, which ships `STNEXT.EXE` and `DATA/*.WBP` archives instead of `.BIN`/`.HD` pairs. It says nothing about the PS2 release and the row stays unverified.

The other nineteen rows stay unverified: *Sotsugyou* was inspected, but only as a Windows port, and the rest were not inspected at all, so they rest on credits or on a third-party tool's grouping. The three *Zero no Tsukaima* games are the reference set rather than candidate rows — what carries over to the table is their container layout and script layer, which is what the two inspected games were measured against.

The publisher-era rows are the test of the middleware reading. If a game Marvelous published with a different developer turns out to carry the same `.BIN`/`.HD` pairs and `TIM2` blocks, the library is middleware licensed under a publisher's engine rather than one studio's engine. If none of them do, the containers travelled with Connect Wizard instead. The cheapest check on an image is presence of the pairs plus the `\xE6TIM2\x04\x00\x01` marker.

One row has no VNDB entry, and that is expected rather than a gap: *Twelve: Sengoku Fuushinden* is a strategy RPG, and VNDB indexes visual novels only. The rows that do carry links are there because they are narrative games.

*Twelve* needs a caveat: the studio's own work list gives it as a PlayStation 2 title, while every catalogue records the 2005 release as the PSP title `ULJM-05031`. The PSP platform is used here, and the discrepancy is unexplained.

The Russell entries line up with the production credit on Fantasy and Symphony, and TENKY, the developer of *Cambrian QTS* and *Twelve*, is also credited alongside Konami on *Tokimeki Memorial: Girl's Side*, so the group is not a coincidence of unrelated publishers alone.

The studio's earlier console and computer credits — PlayStation, Mega Drive, DS, PC-88, FM-Towns — are left out on purpose, and so are two localisation jobs on *Armored Core 2: Another Age* (EU) and *Lupin III: Majutsuou no Isan* (US), which say nothing about the engine.

## How the data is organised

Six containers, all opened by name from the executable:

| File | Contents |
| --- | --- |
| `SYSTEM` | Script library: `.nut` source pages, then binary tables, scene-script name tables, and dialogue text |
| `SCENEDAT` | Scene graphics as compressed TIM2 blocks on 2048-byte boundaries |
| `SCENE_ID` | Per-scene compressed blocks: compiled scene data on Fantasy and Symphony, script source on Concerto |
| `NORMAL` | UI and shared textures, same block layout as `SCENEDAT`, plus `BITH` records |
| `SOUND_ID` | Audio banks, record 0 carrying a 20-byte header |
| `VOICE_ID` | Headerless PS2 SPU ADPCM voices, one record per line |

Each pair is explained in detail on the subpages:

- [Executable findings](zero-no-tsukaima-soalo/executable.md) — what the three ELFs contain and how they differ.
- [Payload layout](zero-no-tsukaima-soalo/payload.md) — record maps for every container in all three games.
- [Archives](zero-no-tsukaima-soalo/archives.md) — the `.BIN`/`.HD` pair and a quickbms splitter.
- [Scripts](zero-no-tsukaima-soalo/scripts.md) — the `.nut` module layer, the `.ks` scene layer, and a quickbms extractor.
- [Textures](zero-no-tsukaima-soalo/textures.md) — the compressed TIM2 blocks, the codec, and the tool that decodes them.

## Running it today

There is no reimplementation of this engine, and none is described here. The only ways to run the games are original hardware or a PlayStation 2 emulator such as PCSX2.

Running the games is out of scope for now: the games have not been played through for this notebook, so no compatibility claim is made. What has been inspected is the installed data — the executables and the data containers — not gameplay.

## Known use

The engine is documented here from these three titles. No game page exists yet for any of them. Twenty-one other games are listed under [Games likely to use the engine](#games-likely-to-use-the-engine) — two inspected and counted as the same engine, one that turned out to be a different platform, and the rest on credits or publisher-era grounds.

- *Zero no Tsukaima: Koakuma to Harukaze no Concerto* (Marvelous Entertainment, 2007-02-15, PlayStation 2) — first release, limited edition serial `SLPS-25708`.
- *Zero no Tsukaima: Muma ga Tsumugu Yokaze no Fantasy* (Marvelous Entertainment, 2007-11-29, PlayStation 2) — regular and limited editions.
- *Zero no Tsukaima: Maigo no Period to Ikusen no Symphony* (Marvelous Entertainment, 2008-11-06, PlayStation 2) — plus a 2009 Best re-release.

## What to record next

- Decode the compiled payload that `SCENE_ID.BIN` holds on Fantasy and Symphony, starting from the `fa 00 00 74 43` prefix that opens every sampled block.
- Work out the second header word in `SCENE_ID` blocks: `8` on Fantasy and Symphony, `1` on Concerto, and `1` in every image block.
- Work out how the `.ks` slot names in `SYSTEM` map onto `SCENE_ID` block offsets; the scene table is present, the join key is not yet identified.
- Identify the script control system. Socio Art Logic's work list excludes it from its own contribution, and the Squirrel binding is the most distinctive part of the engine, so the author of that layer is still unknown.

## Sources

- [VNDB — Zero no Tsukaima: Koakuma to Harukaze no Concerto](https://vndb.org/v104)
- [VNDB — Zero no Tsukaima: Muma ga Tsumugu Yokaze no Fantasy](https://vndb.org/v216)
- [VNDB — Zero no Tsukaima: Maigo no Period to Ikusen no Symphony](https://vndb.org/v1275)
- [有限会社ソシオ・アートロジック](https://artlogic.jp/) — company site; the work list credits Concerto to it as "main programmer, adventure library development excluding script control"
- [Socio Art Logic — Game Developer Research Institute](https://gdri.smspower.org/wiki/index.php/Socio_Art_Logic) — staff, founding date, and per-title credits
- [Socio Art Logic — OGDB](https://ogdb.eu/index.php?companyid=15610&section=company) — company entry and credit list
- [Connect Wizard — OGDB](https://ogdb.eu/index.php?companyid=22959&section=company) — company entry and development credits
- [Zero no Tsukaima staff roll](https://raido.moe/staff/ps2/ps2_zero_no_tsukaima_1.html) — the Concerto end credits, reproduced in Japanese
- [Wikipedia — Squirrel (programming language)](https://en.wikipedia.org/wiki/Squirrel_(programming_language)) — lists all three titles under "Games using Squirrel"
- [Squirrel programming language](https://www.squirrel-lang.org/)
- [punk7890/PS2-Visual-Novel-Tool](https://github.com/punk7890/PS2-Visual-Novel-Tool) — MIT licence; its Socio Art Logic handler decodes the block stream and the TIM2 images
- [[PS2] Need help figuring out what to do next! (VG Resource forum)](https://vg-resource.com/threads/ps2-need-help-figuring-out-what-to-do-next.42169/) — thread where the block codec was worked out, January 2024
- [TM2/TIM2 Image (Reverse Engineering Wiki)](https://rewiki.miraheze.org/wiki/TM2_TIM2_Image) — TIM2 header layout, and it lists Concerto
