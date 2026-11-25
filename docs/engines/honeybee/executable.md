---
title: "HoneyBee — executable findings"
description: "What SLPS_255.87 exposes: a stripped MIPS ELF, the CRI middleware version set, the engine's own source-file names, and the 7,113-entry filename manifest that names every archive member."
type: engine
status: draft
confidence: observed
tags:
  - playstation-2
  - mips
  - cri
  - filename-manifest
sources:
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

# HoneyBee — executable findings

`SLPS_255.87` is the whole engine: 3,096,752 bytes of stripped r5900 code with the CRI middleware linked in statically, and — the useful part — a filename manifest for every archive member, stored as plain strings.

## At a glance

| | |
| --- | --- |
| File | `SLPS_255.87`, 3,096,752 bytes |
| Type | ELF32, little-endian, `ET_EXEC`, `EM_MIPS` |
| Flags | `0x20924000` (`EF_MIPS_ARCH_3`, EABI64, r5900) |
| Entry | `0x100008` |
| Symbols | none — fully stripped, 8 section headers |
| Compiler | `MW MIPS C Compiler (2.4.1.01)`, `PlayStation2` |
| Strings | 10,534 of four characters or more |
| Filename manifest | 7,113 names, NUL-terminated, 16-byte-aligned slots from `0x28f920` |

## Detection

| File | Size (bytes) | MD5 (first 5,000 bytes) | SHA-256 |
| --- | ---: | --- | --- |
| `SLPS_255.87` | 3096752 | `f894b59303681550f177f4ff81ab3201` | `f65f78f7820bdfa5d2c8c2eb14281c7c3994d812577e4c869d66204179a10f5f` |
| `SYSTEM.CNF` | 57 | `5f6455c5cfa0b9d4eb19607ff98a3d1a` | `caf70bd90028d66044b1ffbd33b4a892957a37963e5e18289bc73312a6bc337a` |

`SYSTEM.CNF` is three lines: `BOOT2 = cdrom0:\SLPS_255.87;1`, `VER = 1.03`, `VMODE = NTSC`.

## CRI middleware

The executable names the middleware it was linked against. Every component below is present as a version string, and the I/O side also ships as an IOP module:

| Component | Version | Build |
| --- | --- | --- |
| CFG | 1.002 | 2005-02-08 |
| CFT | 1.57 | 2004-09-17 |
| M2V | 1.945 | 2004-09-17 |
| MPS | 1.924 | 2004-09-17 |
| MPV | 1.933 | 2004-09-17 |
| SFD | 1.946 | 2004-09-17 |
| SFH | 1.19 | 2004-09-17 |
| SFX | 2.08 | 2004-09-17 |
| SUD | 0.05 | 2004-09-17 |

All carry `Copyright (c) 1999-2004 CRI-MW`. `MODULES/` on the disc holds the matching IOP side: `CRI_ADXI.IRX` plus the standard set (`MCSERV`, `PADMAN`, `LIBSD`, `MODMIDI`, `MODHSYN`, `MODSEIN`, `MODSESQ`, `AMSOUND`, `SDRDRV`, `SIO2MAN`, `MCMAN`, `USBD`, `USBKB`, `AMMOUSE`) and `IOPRP300.IMG`.

The AFS streaming layer's own error strings are also present — `adxf_GetPtStat`, `adxt_EntryAfs`, a message about the 128 MB per-file ceiling, and "It is impossible to load AFS files in parallel" — which is why the game uses four archives rather than one.

## The engine's own source files

The build embedded its object-file paths or trace tags, and they survive the strip. They fall into three groups:

| Group | Names |
| --- | --- |
| Core library, `am` prefix | `amCdFs.c`, `amMc.c`, `amMotion.c`, `amObject.c`, `amTexture.c` |
| Support | `Heap.cpp`, `DefaultHeap.cpp`, `ListHeap.cpp`, `BstRand.cpp`, `pof.cpp`, `WindowRenderer.cpp`, `OrderingTable.inl` |
| Project | `HoneyBee.cpp` |

`amCdFs` is the CD/file-system layer, `amMc` the memory-card layer, and `amMotion`/`amObject`/`amTexture` the three content classes. `ListHeap`/`DefaultHeap` and `BstRand` (a binary search tree) are general-purpose containers. `WindowRenderer.cpp` and `OrderingTable.inl` point at a 2D/UI renderer with a GS packet ordering table.

Further state-machine vocabulary appears as plain strings: `EXECCMD`, `commandEndOperation`, `commandEndGuard`, `commandEnterFSM`, `commandChangeState`, `getGameStartState`, and the FSM names `DOLL_FSM_01.PAC` … `DOLL_FSM_03.PAC`. The script layer is therefore state-machine driven, and the `DOLL_*` scripts are the state machines.

## The filename manifest

The manifest sits immediately after the two strings `amCdFs.c` and `MC: sceMcInit error`, starting at ELF offset `0x28f920` with `ADV_BGD_001.AMT`. Names are NUL-terminated and each is padded into a **16-byte-aligned slot**, so they can be read with a plain fixed-stride walk:

```text
0000000028f920  ADV_BGD_001.AMT\0  ADV_BGD_001_01.TWF\0  ADV_BGD_002.AMT\0 …
```

Reading every printable run of three characters or more that ends in `.` plus two to four letters, followed by NUL, yields **7,113** names.

### Mapping names to AFS entries

The first 36 names are engine and system strings, not archive members:

```text
data_ps2.AFS · /bee/BGM_AFS.afs · /bee/VO_AFS.afs · /bee/SE_AFS.afs
cdrom0:\MODULES\*.IRX  (11 entries)
CACHE.LST · HoneyBee.cpp · Heap.cpp · pof.cpp · ListHeap.cpp · BstRand.cpp
WindowRenderer.cpp · DefaultHeap.cpp · icon0.ico · icon.sys (5 pairs) · OrderingTable.inl
```

After that the order is the AFS entry order: **entry *i* is `names[36 + i]`**. That was established by aligning the extension sequence of the manifest against the magic sequence of `DATA_PS2.AFS` with `difflib.SequenceMatcher`; the alignment is monotonic and near-perfect, and every residual mismatch has a reason (a `.BIN` whose magic is `EFFE`, a `.PAC` whose first bytes are the `0x25` opcode tag rather than a magic, `FONT.FNB`, `ICON0.ICO`). Two spot checks agree: manifest index 36 is `ADV_BGD_001.AMT` at 0x4b4a0, and 37 is `ADV_BGD_001_01.TWF` at 0x1c4.

The pairing in the manifest itself is informative: every `.AMT` texture is immediately followed by a `.TWF` whose name is `<texture>_01`, so `.TWF` is a per-texture companion record rather than a standalone image.

If the alignment is ever doubted, it can be re-derived: the same walk gives the exact AFS entry for any named file, so any decoded member can be checked against its own header.

## What this does not establish

- Whether "HoneyBee" is the engine's name, the project's code name, or one translation unit in the engine. `HoneyBee.cpp` is the only candidate the binary offers.
- Which compiler units are `am*` library code and which are project code; the split above is from file names, not from code.
- Any behaviour of the engine. Nothing was disassembled beyond locating strings.

## Sources

- [NovelVM issue #60](https://github.com/monyarm/NovelVM/issues/60) — tracking issue for a loader.
