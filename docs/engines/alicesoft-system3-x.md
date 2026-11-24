---
title: "AliceSoft System 3.x"
description: "AliceSoft's Windows-era visual-novel engine family, its AIN module system, and the open ports that reimplement it."
type: engine
status: draft
confidence: mixed
tags:
  - alicesoft
  - windows
  - visual-novel
  - ain
  - ald
aliases:
  - System 3.5
  - System 3.9
  - System35
  - xsystem35
platforms:
  - Windows
games: []
formats: []
maturity: partial
sources:
  - title: VNDB — AliceSoft System3.X engine
    url: https://vndb.org/r/engines?m=AliceSoft%20System3.X
  - title: kichikuou/xsystem35-sdl2
    url: https://github.com/kichikuou/xsystem35-sdl2
  - title: kichikuou/system3-sdl2
    url: https://github.com/kichikuou/system3-sdl2
  - title: Takeda Toshiya — AliceSoft page
    url: http://takeda-toshiya.my.coocan.jp/alice/index.html
  - title: AliceSoft — 著作権ガイドライン
    url: https://www.alicesoft.com/annai.html
  - title: monyarm/NovelVM — issue 5
    url: https://github.com/monyarm/NovelVM/issues/5
last_verified: 2026-11-25
ai_assisted: true
---

# AliceSoft System 3.x

System 3.x is the Windows-era generation of AliceSoft's in-house engine, covering System 3.5 through 3.9. It is a different virtual machine from the DOS-era System 1, 2 and 3.0, with a different file format, and the two families are not interchangeable: Takeda's own readme warns that his System 3 port is 別物 from 鬼畜王ランス and later.

The engine runs a compiled scenario bytecode, draws through its own graphics layer rather than a third-party library, and — from 3.5 onwards — loads optional DLL-style modules named in a per-title `System39.ain` manifest. Documenting the engine properly means documenting that module system, because the module list is what separates a title that runs from a title that does not.

## At a glance

| Field | Value |
| --- | --- |
| Kind | In-house Windows visual-novel engine |
| Generation | System 3.5–3.9 (the DOS-era System 1/2/3.0 is a separate VM) |
| Scripts | Compiled bytecode, per-title `.ain` manifest naming DLL modules |
| Archives | `.ALD` resource archives |
| Modules | Declared in `System39.ain`; implemented in the runtime as loadable module code |
| Open runtimes | `xsystem35-sdl2` (3.5–3.9), `system3-sdl2` (System 1–3.0) |
| Reference licence | GPL-2.0-or-later for both runtimes |
| Status here | Module system and per-title module use measured; forks and patches catalogued; formats not yet written up |

## Why it matters

There are around a hundred System 3.x releases on VNDB, more than any other engine family this project has looked at, and running it today depends on one actively maintained GPL codebase. Two things follow.

First, the port is tractable in stages. A title's `System39.ain` names the modules it wants, and an entry with no functions resolves to nothing, so the practical cost is the per-title function table rather than the name list. That makes a lowest-common-subset runtime possible: base first, then the modules the early titles actually call.

Second, the work is not self-contained. The engine's behaviour is documented by Takeda's emulator source and by the two kichikuou runtimes rather than by a format specification, so assembling a loader means reading those, plus the small patches other people have written on top of them.

## The module system

Each title ships a manifest under `GAMEDATA/`, usually `System39.ain`. It is obfuscated: from offset 4, every byte is rotated right by two bits. Once decoded, `HEL0` sits at offset 8, the DLL count at offset 16, and then each entry carries a name, a function count and a function table.

`xsystem35` reads the same file in `src/s39ain.c` and resolves names in `modules/modules.c`, but resolution is advisory: an unknown name logs `Cannot resolve DLL` and returns false, and the caller at `src/s39ain.c:167` ignores the result. A zero-function entry therefore costs nothing at all, which is why most of the unfamiliar names in real manifests — `Graph`, `SurfaceFactory`, `GLStretch`, `FileControl`, `StreamMusic` — are link-map noise rather than modules to write.

A name is also not globally classifiable: `Math` and `S3xMusic` appear with five to ten functions in some titles and none in others, so the per-title function table decides cost.

Per-title module counts measured across eight 3.9 titles are collected in the [forks and patches](alicesoft-system3-x/forks.md) subpage's context and in the NovelVM tracking issue; the largest observed is *Daiakuji* at nine modules and 188 functions, the smallest *Rance 5D* at one module and 114.

## Evidence from this project

| Claim | Evidence | Basis |
| --- | --- | --- |
| System 3.x is a different VM from System 1/2/3.0 | Takeda's `system3 for win32` readme calls it 別物 from 鬼畜王ランス onwards; his source ships separate `system1`/`system2`/`system3` projects | Observed |
| The `.ain` manifest is a rotate-right-2 obfuscation with a `HEL0` header | Decoded the eight titles' manifests; `HEL0` at offset 8, DLL count at 16 after decoding | Observed |
| Zero-function DLL entries have no cost | `resolve_module()` returns true before lookup when the function count is zero; the caller ignores the result | Observed |
| Both open runtimes are GPL-2.0-or-later | 238 files in `xsystem35-sdl2` carry an "any later version" clause; `system3-sdl2`'s `COPYING.txt` is GPL v2 | Observed |
| System 1–3.0 executables for 32-bit Windows came from Takeda, then kichikuou | Takeda's readme credits Chikama's xsystem35 and his own `system3` projects; `system3-sdl2`'s README calls itself an SDL port of Takeda's archive | Observed |

## Running it today

`xsystem35-sdl2` runs System 3.5–3.9 titles on Linux, macOS, Windows and mobile targets, with Unicode text and a built-in debugger. `system3-sdl2` does the same for the DOS-era family. SysEng, a fork of `system3-sdl2`, adds multi-slot font support and an x-coordinate override for System 2/3.0 rendering; its non-backend changes are catalogued on the subpage.

None of the three is a general emulator of the original: each reimplements the engine in portable C or C++, and each carries its own per-game quirks.

## Known use

Around a hundred releases, including *Kichikuou Rance*, *Daiakuji*, *Tsumamigui 2*, *Rance 5D*, *Yoru ga Kuru!*, *Night Demon*, *Ore no Shita de Agake* and *Shell Creaill*. No dedicated game pages yet.

## Forks and patches

[Forks and patches worth carrying](alicesoft-system3-x/forks.md) catalogues every open descendant of the two runtimes, measures what each one actually changes, and separates the handful of changes a port would want from the backend swaps that a ScummVM-style host supplies for free.

## What to record next

- Write up `.ALD` archive layout and the `.ain` manifest as format pages.
- Confirm which modules the pre-3.9 discs need, if any: three checked discs (PERSIOM, Kakurezuki, See In Ao) ship `System36/38.exe` and no `.ain`, so the module question takes a different shape there.
- Establish whether the `System39.ain` function table is a link-time import list or a to-be-loaded list, by watching what a running title actually calls.
- Close the `NIGHTDLL` gap: 68 functions used only by *Yoru ga Kuru!*, the one module with no implementation in either runtime.

## Sources

- [VNDB engine index — AliceSoft System3.X](https://vndb.org/r/engines?m=AliceSoft%20System3.X)
- [kichikuou/xsystem35-sdl2](https://github.com/kichikuou/xsystem35-sdl2)
- [kichikuou/system3-sdl2](https://github.com/kichikuou/system3-sdl2)
- [Takeda Toshiya's AliceSoft page](http://takeda-toshiya.my.coocan.jp/alice/index.html)
- [AliceSoft 著作権ガイドライン](https://www.alicesoft.com/annai.html)
- [NovelVM issue 5 — Support AliceSoft System 3.x engine](https://github.com/monyarm/NovelVM/issues/5)
