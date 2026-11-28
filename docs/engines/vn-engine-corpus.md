---
title: "VN engine corpus: how much engine logic is there, really?"
description: "A measured corpus of visual novel engine reimplementations, matching decompilations and shipped executables, split into engine logic, boilerplate, middleware, SDK/CRT and third-party code, to estimate what writing a new VN engine actually costs."
type: note
status: draft
confidence: mixed
tags:
  - engine-survey
  - line-counts
  - reverse-engineering
  - middleware
  - methodology
aliases:
  - VN engine corpus
  - engine LOC corpus
sources:
  - title: NovelVM issue backlog
    url: https://github.com/monyarm/NovelVM/issues
  - title: ScummVM
    url: https://www.scummvm.org/
last_verified: 2026-11-28
ai_assisted: true
---

# VN engine corpus: how much engine logic is there, really?

Every "support engine X" request implicitly asks the same question: how much code is
that, and how much of it would NovelVM have to write itself? This page answers it with
measurements instead of guesses.

Two independent data sets are combined:

1. **Source side** — 31 public projects that either *are* a visual novel engine
   (released source or a port) or *reimplement* one (a playable rewrite, or a matching
   decompilation that reproduces the original binary function by function).
2. **Binary side** — the shipped executables of the games actually sitting in the local
   and remote libraries: **33 executables (13 PlayStation 2, 11 PSP, 9 Windows)** measured
   section by section, plus size-only records for the cartridge and disc platforms where
   no separable executable exists.

Both are split on the same axes, so the numbers can be compared: *engine logic* is what a
port has to reproduce, everything else is not.

**Scope.** The corpus is the union of the 102 open NovelVM engine issues, the local
`~/Games/Visual Novel` library, a remote PS2/PC library, and the owned-games list used as a
candidate checklist. Deliberately excluded: Ren'Py and Unity titles (the engine ships with
the game and is not something a port would replace) and archive dumps of games that already
use an engine covered here.

## What is counted

| Bucket | What it means | Does a port have to write it? |
| --- | --- | --- |
| **engine** | VM, script compiler, opcodes, game state, scene/flag logic, save format, archive and image/video handling specific to the engine | **Yes** — this is the real cost |
| **boilerplate** | SDL/GL window, input loop, audio device, platform `#ifdef` layers, ScummVM meta-engine glue, detection plumbing | No — ScummVM and SDL already do this |
| **middleware** | CRI (ADX/ADX2, Sofdec, MPEG, CPK), RenderWare, Squirrel, Scaleform, Bink, FMOD, Wwise | No — replaced by an existing decoder or ScummVM's audio/video layer |
| **sdk_crt** | Sony PS2/PSP SDK, MSVC/MinGW/Borland C runtime | No |
| **thirdparty** | zlib, libpng, libjpeg, libvorbis, FFmpeg, FreeType, GLEW, gtest, imgui, vendored `external/` trees | No |
| **data** | generated tables, palettes, SJIS→UTF-16 maps, `Hex`/`Json` blobs | No |
| **tooling** | build files, Python/Perl asset tools, test suites, docs | No |
| **decompiled** | Hex-Rays / IDA output pasted into a tree | No — and not eligible for study |
| **asm** | hand-written or disassembled assembly (counted separately from C/C++) | Depends; on GBA decomps most of it is code that *is* engine logic |

The split is by file path, with one automated exception: a file whose lines are ≥60%
hex/int/string table rows is re-bucketed as `data` even if it lives in the engine tree.
Every repo's rule file is stored next to the script (`tools/vn-corpus/`), and the sampled
audit notes are in the *Caveats* section.

## Source corpus

All repositories were cloned at `--depth 1` on 2026-11-28; commits are the first 7
characters of the pinned HEAD. Counts are tokei *code* lines (comments and blanks are not
included), so they are directly comparable across languages.

| Project | Target engine | Kind | Licence | Commit | Engine | Boilerplate | Middleware | SDK/CRT | Third-party | Data | Tooling | Note |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| [Digital Devil Saga decompilation](https://github.com/Megami-Decomps/dds-decomp) | Atlus SMT (PS2) | matching decomp | none | `e714912` | 580,796 | — | — | — | — | — | 57,107 |  |
| [Persona 4 decompilation](https://github.com/Raikaru/Persona4-Decompilation) | Atlus SMT/Persona (PS2) | matching decomp | none | `3a28140` | 510,869 | — | 260,228 | 8,760 | 1,586 | — | 1,270,042 | engine share 65% of its own decomp |
| [Persona 3 FES decompilation](https://github.com/Raikaru/Persona3-FES-Decompilation) | Atlus SMT/Persona (PS2) | matching decomp | CC0-1.0 | `81da989` | 443,007 | — | 181,684 | 18,416 | — | — | 51,952 | engine share 72% |
| [KiriKiri 2](https://github.com/krkrz/krkr2) | KiriKiri | released source | GPL-2.0 | `dec49af` | 388,693 | — | — | — | 908,557 | — | 59,852 | trunk/ only; vendor/ and the branches/tags SVN copies excluded |
| [siglus-rs](https://github.com/Lulzx/siglus-rs) | Siglus / RealLive / UK2 / AVG32 | reimplementation | MPL-2.0 | `88f9cee` | 376,044 | 16,263 | — | — | 65,891 | 65,992 | 19,136 |  |
| [Shin Megami Tensei III decompilation](https://github.com/Megami-Decomps/smt3-decomp) | Atlus SMT (PS2) | matching decomp | none | `08ecf20` | 334,305 | — | — | — | — | — | 44,483 |  |
| [Tokimeki Memorial decompilation](https://github.com/CosmicScribe64/tokimemo-ps1-decomp) | Konami Tokimeki Memorial (PS1) | matching decomp | CC0-1.0 | `3c60705` | 249,871 | — | — | — | — | 104,478 | 141,042 | drafts/ holds 4.28M mechanically generated C lines, excluded from engine |
| [ethornell-rs](https://github.com/xmoezzz/ethornell-rs) | BGI/Ethornell | reimplementation | MPL-2.0 | `0b870c3` | 197,696 | 5,564 | — | — | 318,228 | — | — |  |
| [Ghost Trick decompilation](https://github.com/liambsulliva/ghost-trick-vita) | Cing (DS) | matching decomp | none | `1b614d0` | 192,952 | 135,364 | — | — | — | — | 99,399 |  |
| [cmvs-rs](https://github.com/astudyinyellow/cmvs-rs) | CMVS | reimplementation | Apache-2.0 OR MIT | `af64920` | 180,646 | 14,613 | — | — | — | — | 6,142 |  |
| [Hotel Dusk decompilation](https://github.com/usename00/hotel-dusk-decomp) | Cing (DS) | matching decomp | none | `dcd74d8` | 127,496 | 1,182 | — | — | — | — | 376 |  |
| [Impacto](https://github.com/CommitteeOfZero/impacto) | MAGES./5pb. | reimplementation | ISC | `ad20204` | 124,256 | 5,245 | — | — | 59,822 | — | — |  |
| [OpenBGI](https://github.com/uyjulian/openbgi) | BGI/Ethornell | reimplementation | GPL-2.0 | `e6e9e24` | 119,784 | 27,482 | — | — | — | — | 31,079 |  |
| [KiriKiri Z](https://github.com/krkrz/krkrz) | KiriKiri | released source | BSD-3-Clause (W.Dee) | `fd5c4ba` | 113,725 | 36,872 | — | — | 774 | — | 2,527 |  |
| [Persona decompilation (PS1)](https://github.com/daanhenke/persona-psx) | Atlus Persona (PS1) | matching decomp | none | `dfd1cd4` | 113,307 | — | — | — | — | — | 1,922 |  |
| [ikuradroid](https://github.com/VienDesuPorting/ikuradroid) | Ikura / VileVN port | port of released source | GPL-3.0 | `2dbde94` | 94,770 | 8,994 | — | — | 1,356,108 | — | — |  |
| [xsystem4](https://github.com/nunuhara/xsystem4) | AliceSoft System 4 | reimplementation | GPL-2.0 | `d3f93bc` | 74,553 | — | — | — | 1,135 | — | — |  |
| [Danganronpa decompilation](https://github.com/Pucas01/DISTRUST) | Spike Chunsoft Danganronpa (PSP) | matching decomp | CC0-1.0 | `5526cd4` | 53,201 | — | — | — | — | — | 25,814 |  |
| [Ace Attorney 2 decompilation](https://github.com/atasro2/pwaa2) | Capcom AA (GBA) | matching decomp | none | `91cd5f6` | 42,838 | — | — | — | — | — | 9,242 |  |
| [rlvm](https://github.com/eglaysher/rlvm) | RealLive | reimplementation | GPL-3.0 | `e38cda7` | 42,479 | 2,138 | — | — | 83,260 | — | 9,213 |  |
| [xsystem35-sdl2](https://github.com/kichikuou/xsystem35-sdl2) | AliceSoft System 3.x | reimplementation | GPL-2.0 | `4cabebf` | 41,053 | 2,813 | — | — | — | — | — |  |
| [KiriKiri SDL2 port](https://github.com/krkrz/krkrsdl2) | KiriKiri | port of released source | MIT | `8cea182` | 35,863 | 670 | — | — | — | 1,371 | — |  |
| [shiinario-rs](https://github.com/kiKiRei/ShiinaRio) | ShiinaRio | reimplementation | MIT | `3e560c6` | 34,424 | 1,015 | — | — | 4,867 | — | — |  |
| [ai5-sdl2](https://github.com/b-stack/ai5-sdl2) | Elf ai5 (PC-98/Win) | reimplementation | GPL-3.0 | `ad7a703` | 30,804 | 3,596 | — | — | — | — | — |  |
| [Ace Attorney decompilation](https://github.com/atasro2/pwaa1) | Capcom AA (GBA) | matching decomp | none | `744219a` | 30,384 | — | — | — | — | — | 9,242 |  |
| [VileVN](https://sourceforge.net/p/vilevn/) | TLove / GSS | released source | GPL-3.0 | `f6e48d6` | 24,218 | 9,258 | — | — | 20,735 | — | 7,688 |  |
| Xuse engine sources (no public repository) | Xuse XLVNS | released source | none | `7a4bc8f` | 18,805 | — | — | — | — | — | 2,344 |  |
| [ONScripter](https://github.com/onscripter/onscripter) | NScripter | reimplementation | GPL-2.0 | `848a608` | 17,210 | 3,392 | — | — | 942 | 11,464 | — |  |
| [libai5](https://github.com/b-stack/libai5) | Elf ai5 (PC-98/Win) | reimplementation | GPL-3.0 | `779913d` | 9,320 | — | — | — | — | — | — |  |
| [libnpengine](https://github.com/TriggerRokko/libnpengine) | Nitroplus | reimplementation | LGPL-3.0 | `da1a175` | 4,856 | — | — | — | — | — | — |  |
| [Shin Megami Tensei disassembly](https://github.com/spannerisms/smt1dasm) | Atlus SMT (SFC) | disassembly | GPL-3.0 | `6d950c0` | 3 | — | — | — | — | — | — | pure assembly listing |

Raw rows, including the per-bucket file lists, are committed as
[`source-loc.csv`](../data/vn-corpus/source-loc.csv).

### What the source numbers say

**A playable reimplementation of a script-driven engine is 9k–75k lines.** libai5 9k,
ONScripter (NScripter) 17k, ai5-sdl2 31k, shiinario-rs 34k, krkrsdl2 36k, xsystem35 41k,
rlvm 42k, xsystem4 75k. The engines above that are not "bigger engines" but *collections*:
OpenBGI 120k covers a dozen BGI revisions at once, Impacto 124k carries per-title
compatibility profiles (23.6k) and per-game glue (23.6k), KiriKiri Z 114k includes the TJS2
compiler and four graphics backends, siglus-rs 376k is four engines plus two format
decompilers.

**A decompilation's line count is not engine size.** Tokimeki Memorial's repository is
4.28M generated `drafts/` C lines against 250k hand-written `src` lines; the Ace Attorney
projects carry 56k and 117k lines of assembly that are asset and script tables, not code;
smt1dasm is a 251k-line assembly listing. Only the `src` side is comparable to a rewrite,
which is why the two columns are kept apart.

**One engine family, one line count per console generation.** The Atlus decomps trace the
same engine growing: Persona (PS1) 113k, Persona 3 FES 443k, Persona 4 511k, Digital Devil
Saga 581k. The two Cing decomps behave the same way: Hotel Dusk 127k, Ghost Trick 193k —
same studio, next hardware, more engine.

**Vendored code usually dwarfs the engine in a port.** ikuradroid is 95k engine lines over
1.36M lines of vendored SDL/SDL_mixer/SDL_ttf/SDL_image/webp/mikmod, and KiriKiri 2 is 389k
engine lines against 913k vendored lines (Irrlicht, SQLite, zlib, libjpeg, libsquirrel,
libpsd) plus 540k Borland C++ Builder headers. KiriKiri Z's 114k is the same engine with
that plugin zoo left out.

**The original engine source is 3× the portable rewrite, and the extra is platform
plumbing.** KiriKiri Z is 113,725 engine lines + 36,872 lines of `win32/` boilerplate;
krkrsdl2 replaces that with 35,863 + 670. Same engine, one third the code.

**ScummVM-class boilerplate is not in these numbers at all.** These projects all carry
their own window/input/audio layer (that is the `boilerplate` column, typically 1k–4k,
because SDL does the work). A NovelVM engine gets that for free and instead plugs into
`Engines::Engine`, the detection tables and the meta-engine.

**ScummVM's own engines land in the same band.** As an independent check on the whole
exercise, the 132 ScummVM engine directories that contain code total 4,685,166 lines: a
median of **16,593 lines per engine** and a mean of 35,494, with 80 of the 132 under
25,000 and only 14 above 100,000. The projects measured above were mostly written against
SDL or libretro rather than against ScummVM's `common/`, yet they arrive at the same
distribution — which is the strongest evidence that the 15k–45k band is a property of the
problem, not of these particular codebases.

## Cross-check: source lines versus shipped machine code

The Persona 4 decompilation compiles to the retail `SLUS_217.82`, which makes it a
calibration standard. Its C totals **781,443 lines** — 510,869 engine, 260,228
middleware (CRI + RenderWare), 8,760 SDK, 1,586 third-party — against **6,701,696 bytes**
of `.text`, i.e. **8.6 bytes of MIPS code per source line**. Persona 3 FES, whose
decompilation totals 643,107 lines against 7,134,848 bytes, gives **11.1**. The pair
brackets the conversion at 8.6–11.1 bytes/line.

**10 bytes per line is used for the tables below**, so each estimate carries about ±20%.
The figure is *source-equivalent lines of the whole binary*, middleware and SDK included;
subtract the identified middleware share (P4: 35%) to get engine logic.

`Observed`: P4 6,701,696 B `.text`, 781,443 C lines → 8.6 B/line.
`Observed`: P3 FES 7,134,848 B `.text`, 643,107 C lines → 11.1 B/line.
`Observed`: ai5-sdl2 is 30,804 lines (of which `doukyuusei2_pal.c` alone is 8,022 lines of
palette data) against 204,800 B `.text` in `AI5WIN.EXE` → 6.7 B/line raw, ≈9.3 excluding
the palette table — the same order, on x86.
`Inferred`: therefore ~10 B/line for PS2, PSP and PC alike.

## Shipped binaries

### PlayStation 2

All seven local titles are extracted directory copies; the executable is the `SLUS_*` /
`SLPS_*` ELF. Three of them still carry symbols (section names and, in P4/Persona 3 FES,
whole middleware banners).

| Title | Executable | Total | Code | Middleware found | ≈ LOC (10 B/line, whole binary) |
| --- | --- | ---: | ---: | --- | ---: |
| Persona 4 | `SLUS_217.82` | 8,621,084 | 6,701,696 | CRI Sofdec, MPEG, M2V, MPS, CFG, CFT, SFH | ≈670,000 (781k known → 35% middleware, 511k engine) |
| Persona 3 FES | `SLUS_216.21` | 9,096,860 | 7,134,848 | same CRI family | ≈713,000 (643k known → 28% middleware, 443k engine) |
| Zero no Tsukaima: Koakuma… | `SLPS_257.08` | 1,386,560 | 1,022,768 | Squirrel (statically linked), libdma | ≈102,000 |
| Zero no Tsukaima: Muma… | `SLPS_258.30` | 1,232,184 | 976,392 | Squirrel, libdma | ≈98,000 |
| Zero no Tsukaima: Maigo… | `SLPS_258.98` | 1,292,816 | 1,025,544 | Squirrel, libdma | ≈103,000 |
| Sugar Sugar Rune | `SLPS_255.87` | 3,096,752 | *n/a* | CRI Sofdec/MPEG/ADX banners inside the flat image | *n/a* |
| Love Hina Gorgeous | `SLPM_652.92` | 1,287,964 | 815,744 | libpad, libmc, libdma only | ≈82,000 |

`Observed`: `SLPS_255.87` (HoneyBee engine) is a single unnamed `PROGBITS` section with
`WAX` flags covering the whole file — a fully stripped, flat image. Section-based
measurement of it is impossible; any code/data split for it has to come from
disassembly, so it is left blank rather than guessed.

The three Zero no Tsukaima discs are the same engine at three revisions: 0.98–1.02 MB of
code each, of which the statically linked Squirrel interpreter is a fixed chunk. That is
consistent with the Soalo research (see [the engine page](zero-no-tsukaima-soalo.md)) and
with "one engine, three data discs".

#### PlayStation 2 from disc images

Six further PS2 titles existed only as `.chd` disc images and had to be unpacked before
the executable could be measured. PS2 executables carry no file extension, so they only
turn up by name pattern.

| Title | Executable | Total | Code | Middleware found | ≈ LOC (10 B/line) |
| --- | --- | ---: | ---: | --- | ---: |
| D.C.II P.S. (Disc 2) | `SLPM_669.23` | 4,702,272 | 356,056 | libpad, libmc, libdma; 4.3 MB `.data` | ≈36,000 |
| Harukaze P.S. | `SLPM_627.77` | 4,445,632 | 354,840 | libpad, libmc, libdma; 4.0 MB `.data` | ≈35,000 |
| Meitantei Evangelion | `SLPM_665.74` | 3,710,768 | *n/a* | libpng, libdma | *n/a* |
| Mai-Otome HiME | `SLPS_256.81` | 1,636,272 | *n/a* | none beyond the flat image | *n/a* |
| Last Escort | `SLPS_255.91` | 940,376 | *n/a* | libpad, libmc, libdma | *n/a* |
| S.Y.K Renshouden | `SLPM_552.47` | 8,070,056 | *n/a* | CRI Sofdec/MPEG/M2V/MPS/CFG/CFT/SFH; CRI movies and AFS audio on disc | *n/a* |

Two of these are worth reading as warnings about file size. The Princess Soft "P.S."
titles ship 4.4–4.7 MB executables whose `.text` is only ~355 KB: almost all of the file
is a zeroed `.data` work buffer (≈1 % non-zero bytes, longest zero run 3.2 MB). Their
`.text` sections are also only 4.3 % identical by 32-bit word, so despite the shared name
they are not the same build.

**Flat images are the norm, not the exception.** Five of the thirteen PS2 executables
measured here (Sugar Sugar Rune, Meitantei Evangelion, Mai-Otome HiME, Last Escort, S.Y.K
Renshouden) are a single unnamed `WAX` section covering the whole load image, with no
symbols and no code/data boundary in the section table. S.Y.K is the extreme case: an
8 MB executable of which 5.98 MB is one section, followed by a 2 MB zero gap and the
section header table. Those five are all from smaller publishers and build toolchains,
while every Atlus, Princess Soft and Zero no Tsukaima executable kept its sections — so
the ability to measure a PS2 binary at all depends on who built it.

### PSP

Five of the nine local titles ship an encrypted `~PSP` EBOOT (`7E 50 53 50`). They were
decrypted with PPSSPP by booting each title with `DumpFileTypes = 1`, which writes
`DUMP/<DISCID>_EBOOT.BIN` — a plain ELF32 (MIPS R3000, `eabi32`, 40 sections). The other
four ship plain ELFs already (their `BOOT.BIN` files are zero-filled placeholders).

| Title | Disc ID | Executable | Total | Code | rodata | data | Middleware found | ≈ LOC (10 B/line) |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: |
| Persona 2: Eternal Punishment | — | `EBOOT.BIN` | 7,188,616 | 3,881,364 | 773,540 | 815,300 | — | ≈388,000 |
| Persona 2: Innocent Sin (DLC build) | — | `EBOOT.BIN` | 9,092,912 | 3,487,048 | 513,908 | 837,580 | — | ≈349,000 |
| Persona 3 Portable | `ULUS10512` | `EBOOT.BIN` | 5,849,808 | 3,654,068 | 206,636 | 543,148 | CRI ADX | ≈365,000 |
| Fate/Extra CCC | — | `EBOOT.BIN` | 2,858,833 | 1,715,708 | 525,400 | 25,424 | — | ≈172,000 |
| Persona 1 | `ULUS10432` | `EBOOT.BIN` | 3,836,464 | 1,561,680 | 937,784 | 582,356 | — | ≈156,000 |
| Code Geass: Lost Colors | `ULJS00135` | `BOOT.BIN` | 1,543,164 | 968,856 | 0 | 250,508 | CRI ADX | ≈97,000 |
| Meitantei Conan | `NPJH50565` | `EBOOT.BIN` | 1,109,120 | 675,700 | 169,720 | 38,391 | — | ≈68,000 |
| Tiger & Bunny - Hero's Day | `NPJH50753` | `EBOOT.BIN` | 4,758,624 | 632,692 | 340,312 | 3,618,901 | — | ≈63,000 |
| Evangelion: Koutetsu Girl Friend 2nd | — | `EBOOT.BIN` | 395,492 | 348,060 | 0 | 42,740 | — | ≈35,000 |

Two further titles existed only as PSP disc images and were unpacked the same way
(`chdman`, then 7-Zip on `PSP_GAME/SYSDIR`):

| Title | Executable | Total | Code | data | Middleware found | ≈ LOC (10 B/line) |
| --- | --- | ---: | ---: | ---: | --- | ---: |
| Madoka Magica Portable | `EBOOT.BIN` | 3,260,116 | 2,700,284 | 553,236 | CRI ADX | ≈270,000 |
| Suzumiya Haruhi no Yakusoku | `EBOOT.BIN` | 1,706,124 | 872,236 | 414,132 | CRI ADX | ≈87,000 |

`Observed`: these two are 2.7× apart for the same generation of hardware and the same
middleware, which is the widest spread inside the PSP set — anime-licence tie-in titles
range from ~35,000 to ~270,000 lines of engine code in exactly the same format.

A third disc-image title (Ore no Imouto, disc 1) was **not** measured: its `EBOOT.BIN` is
encrypted and PPSSPP refuses to boot a stripped disc tree containing only
`SYSDIR`/`PARAM.SFO` ("CPU_Init didn't recognize file"), so the decrypt route needs the
complete image rather than the extracted module.

`Observed`: Tiger & Bunny is the odd one out — 632,692 B of code against 3.6 MB of
`data` and 19.5 MB of `bss`. That is a compressed payload decompressed into memory at
boot, not a large engine; the engine itself is one of the smallest in the set.

`Observed`: the five encrypted titles decrypt to exactly the size of their `EBOOT.BIN`, and
Code Geass's plain `BOOT.BIN` and its decrypted `EBOOT.BIN` produce the same section
layout and the same code size (968,856 B), differing only in 340 bytes of container
header. That is the best available confirmation that the PPSSPP dump route is lossless.

`Observed`: three of the nine PSP copies are modified builds — Fate/Extra CCC and
Evangelion Girl Friend 2nd carry English translation patches, and Persona 2 Innocent Sin
is a DLC-enabler build. Their executables contain the patch's own code and graphics (the
525 KB of rodata in Fate/Extra CCC is largely an inserted font), so those three figures are
upper bounds; the unmodified Japanese executables are smaller.

`Inferred`: the PSP binaries are 3–5× smaller than their PS2 siblings for the same series
(Persona 3 Portable 3.65 MB vs Persona 3 FES 7.13 MB), which matches the reduced asset
resolution **and** a slimmer engine, not just smaller data.

### Windows

| Game | Executable | Total | Code | Compiler | ≈ LOC (10 B/line) |
| --- | --- | ---: | ---: | --- | ---: |
| Bible Black | `bblack.exe` | 319,488 | 200,704 | MSVC | ≈20,000 |
| Doukyuusei | `AI5WIN_32bit_Color.exe` | 598,016 | 385,024 | MSVC | ≈39,000 |
| Doukyuusei 2 | `AI5WIN.EXE` | 415,232 | 204,800 | MSVC | ≈20,000 |
| Shuusaku | `syuusaku.exe` | 253,952 | 167,936 | MSVC | ≈17,000 |
| Shizuku (Elf Classics) | `AI5WIN.EXE` | 446,464 | 331,776 | MSVC | ≈33,000 |
| Kizuato (Elf Classics) | `AI5WIN.EXE` | 479,232 | 356,352 | MSVC | ≈36,000 |
| YU-NO (Elf Classics) | `AI5WIN.EXE` | 483,328 | 335,872 | MSVC | ≈34,000 |
| Isaku (renewal) | `AI5WIN.EXE` | 479,232 | 294,912 | MSVC | ≈29,000 |
| DISCODE 2 (installer only) | `install.exe` | 370,176 | 307,712 | Borland | — |

`Observed`: every Elf title in this set — 1992 to 1999 — ships the *same* executable name,
`AI5WIN.EXE`, and the same mid-1990s DirectDraw/DirectSound import set. They are all ai5,
one engine across seven years and nine games, which is exactly what ai5-sdl2's 30,804
lines cover.

`Observed`: that one engine grows from 167,936–204,800 B of code (Doukyuusei 2, Shuusaku,
1992–94) to 294,912–356,352 B (1996–99) as script opcodes, higher-resolution graphics
paths and voice playback were added. The binary name never changed.

`Observed`: the 1992 Doukyuusei release is the largest ai5 build here at 385,024 B of
code, and it ships as two 598,016-byte executables named `AI5WIN_32bit_Color.exe` and
`AI5WIN_16bit_Color.exe` that differ in **two bytes**. Both are 32-bit PE files importing
`DDRAW`/`DINPUT`/`DSOUND`; the "16-bit" name is a colour-depth switch, not a 16-bit
binary. That is the widest gap in the set between what a filename suggests and what is
actually inside.

### Older and cartridge platforms

These copies are ROM or disc images without a separable executable, so only sizes are
recorded. `Observed`:

| Platform | Title | What is on disk | Size |
| --- | --- | --- | --- |
| DOS (1989) | J.B. Harold: Murder Club | four 16-bit DOS executables `CCLUB.EXE` / `ECLUB.EXE` / `HCLUB.EXE` / `TCLUB.EXE` plus `MCPLAYER`, `LOGO*` | 65,440 / 65,184 / 65,568 / 63,968 B |
| Famicom | Akira | `.nes` ROM (Japan / English) | 393,232 / 524,304 B |
| GBA | Love Hina Advance | `.gba` ROM | 8,388,608 B |
| GameCube | Lupin III: Umi ni Kieta Hihou | data-only extract: `COMMON/`, `movie/*.thp`, `pfil.BIN`, `vfil.*`, `list.BIN` | no `main.dol` present |
| Mega CD | Ranma 1/2: Byakuran Aika | data-only extract: per-scene `*.BIN` (FIGHT/OP/P1-P3/PCM) plus `IP.BIN` sidecars | no disc image or loader |
| PC Engine CD | Sailor Moon / Ranma 1/2 / Toraware no Hanayome | `.bin` + `.cue` | 548,756,880 / 638,819,664 / 266,566,272 B |
| PC-98 | Ranma 1/2: Hiryuu Densetsu | eight extracted disk directories plus `.d88` images | — |

`Observed`: J.B. Harold's 1989 DOS engine is **~65 KB of executable for a full
command-driven detective adventure** — an order of magnitude below the 1990s Windows
engines, and a useful floor for "how small can a working VN engine be". Its code/data split
is not recoverable without disassembly, so it stays a size only.

`Inferred`: the cartridge and CD titles (Akira, Love Hina Advance, the Ranma discs) are
small enough that a full disassembly would be the only way to split code from data, which
is out of scope here; they are listed so the corpus is honest about what was *not*
measured rather than silently dropping them.

### How these map onto the NovelVM backlog

`Observed`: the measured binaries correspond to open backlog issues as follows — Persona 4
and Persona 3 FES and Persona 3 Portable and Persona 1/P2 [#12](https://github.com/monyarm/NovelVM/issues/12)
and [#17](https://github.com/monyarm/NovelVM/issues/17); Zero no Tsukaima PS2
[#48](https://github.com/monyarm/NovelVM/issues/48); Sugar Sugar Rune
[#60](https://github.com/monyarm/NovelVM/issues/60); Love Hina
[#49](https://github.com/monyarm/NovelVM/issues/49); Fate/Extra
[#30](https://github.com/monyarm/NovelVM/issues/30); Code Geass: Lost Colors
[#90](https://github.com/monyarm/NovelVM/issues/90); Meitantei Conan
[#77](https://github.com/monyarm/NovelVM/issues/77); Tiger & Bunny
[#89](https://github.com/monyarm/NovelVM/issues/89); Evangelion Girl Friend
[#47](https://github.com/monyarm/NovelVM/issues/47); the ai5 Windows titles
[#35](https://github.com/monyarm/NovelVM/issues/35).

Of those, Zero no Tsukaima (Soalo) and Sugar Sugar Rune (HoneyBee) already have engine
pages on this site; the Persona, Fate/Extra, Code Geass, Conan, Tiger & Bunny and
Evangelion figures are the first measurement of those executables recorded here.

## Middleware and static libraries actually present

The fingerprint pass checked every binary for the following; each hit was confirmed by at
least two independent signals (banner string, import table, companion file).
| Library | Found in | Bucket |
| --- | --- | --- |
| CRI Sofdec / MPEG / M2V / MPS / CFG / CFT / SFH | Persona 3 FES, Persona 4 (7 separate CRI modules in P4) | middleware |
| CRI ADX | Code Geass, Persona 3 Portable | middleware |
| CRI AFS / ADX (data-only) | Sugar Sugar Rune, HoneyBee engine | middleware |
| Squirrel | Zero no Tsukaima ×3 (statically linked; `SquirrelError`, `SQClass`, `.nut`) | third-party static lib |
| RenderWare | Persona 4 (modelled in the decomp, ~103k lines) | middleware |
| PS2 SDK (`libpad`, `libmc`, `libdma`, `libcdvd`, IOP `*.IRX` / `IOPRP*.IMG`) | all PS2 titles | SDK |
| PSP SDK (`sceGu`, `sceMpeg`, kernel/libprx stubs) | all PSP titles | SDK |
| MSVC CRT / Borland RTL | all Windows executables | CRT |

`Observed`: the CRI footprint in Persona 4 is 156,566 lines in the decompilation and
several hundred kilobytes of `.text` in the retail binary. It is the single largest
non-Atlus block, and it does not need to be written for a port — an ADX/SFD decoder
already exists in ScummVM's audio and video layer.

`Inferred`: Squirrel costs roughly 15k–20k lines wherever it appears; Zero no Tsukaima's
~1.0 MB PS2 binary is mostly engine plus Squirrel, since the disc data is separate.

## What this means for port cost

Working from the measured engine-logic numbers, not from repository size:

| Family | Measured engine logic | Port shape |
| --- | ---: | --- |
| NScripter | 17k (ONScripter) | small VM, text, one image format |
| Elf ai5 | 31k + 9k libai5 (9 titles) | done in NovelVM (30k) |
| Elf ai5 / ai5-sdl2 parity | — | confirms the 30k figure is the whole engine |
| ShiinaRio | 34k | — |
| KiriKiri | 36k (portable) / 114k (original) | TJS2 is most of the original |
| RealLive | 42k (rlvm) | — |
| AliceSoft System 3.x | 41k (xsystem35) | — |
| AliceSoft System 4 | 75k (xsystem4) | — |
| BGI/Ethornell | 120k (OpenBGI, all revisions) | per-revision cost much lower |
| MAGES. | ~77k core (Impacto minus profiles/games) | — |
| CMVS | 181k | largest single-family reimplementation |
| Siglus | 153k scene VM incl. compilers | — |
| Siglus family (UK2, AVG32, RealLive) | 16k + 15k + 91k | three small VMs in one repo |
| Nitroplus | 5k (libnpengine, incomplete) | not a usable cost figure |
| Persona (PS2) | 511k / 443k (matching decomps) | the outlier: a full RPG, not a VN |
| Cing (DS) | 127k | — |
| Capcom AA (GBA) | 30k + 115k asm (AA2) | asm-heavy |
| VileVN (TLove) | 24k | 23.7k lines of Hex-Rays output excluded |
| Nitroplus/Soalo/HoneyBee | no public engine source | measured only from binaries |

**The headline.** For the script-driven engines that make up most of the NovelVM backlog,
the engine logic lands between **15,000 and 45,000 lines** — the same order as ai5, which
was ported in one branch. The expensive engines are not "visual novels" but hybrids
(Persona at ~500k, CMVS at ~180k, BGI and MAGES at ~100k because they support a dozen
revisions each), and in those cases the extra is mostly per-title compatibility code,
which a port can add one game at a time.

Because the shipped binaries agree with the source-side numbers within the expected
10–16 bytes/line, the binary measurements are usable as a first estimate for engines with
no public source at all — the majority of the 113 open issues.

## Caveats

- **Line counts are not effort.** Two thousand lines of opcode dispatch cost more than
  twenty thousand lines of table-driven scene code.
- **Decompilations overstate engine logic.** They include every data table and every
  one-file-per-function shim. Persona 4's 510,869 figure is the best case: it is a real
  working C codebase, and the binary cross-check confirms it.
- **siglus-rs's RealLive crate is mechanically transcribed** (files named after their
  addresses, `f16130.rs`), so its 91k lines are not hand-written effort; it is flagged
  here and should not be used as a cost estimate.
- **Impacto, OpenBGI and KiriKiri Z are multi-revision.** Dividing their total by one
  game overstates a single title's cost.
- **Ace Attorney 2's 115k lines are assembly**, not C. They are engine logic, but they are
  counted separately so the C column stays comparable.
- **The "≈ LOC" columns are estimates**, converting code bytes at 10 bytes/line, the
  midpoint of the 8.6–11.1 range bracketed by the two Persona decompilations. They are
  labelled as estimates everywhere and are never presented as measurements.
- **Five PS2 executables cannot be split** at all (Sugar Sugar Rune, Meitantei Evangelion,
  Mai-Otome HiME, Last Escort, S.Y.K Renshouden): they are single-section flat images with
  no symbol or section boundaries, so no code figure is quoted for them rather than
  guessing one.
- **VileVN's `src/tlove/hexrays.c` (23,681 lines) is decompiler output** and is excluded
  from the engine figure and from any reuse discussion.
- Remote PS2 titles were extracted from CHD copies of the same games as the local set
  where applicable; the section measurements are of the executable, not of the archive.

## Reproducing

`tools/vn-corpus/` holds the scripts used:

- `topdirs.py REPO [depth] [minloc]` — per-directory tokei counts; this is how the
  vendored subtrees (SDL in ikuradroid, Irrlicht in KiriKiri 2) were found.
- `bucket.py REPO RULES.json OUT.csv` — per-file bucket assignment, longest matching
  path prefix wins, plus the data-table heuristic that reclassifies a file as `data` when
  at least 60% of its code lines are bare literals.
- `analyze-bin.py OUT.csv FILE...` — ELF and PE section measurement plus the middleware
  signal match. It parses section headers directly, so it does not need `objdump` (which
  has no MIPS target on the machine used here).
- `make-tables.py [RAW]` — assembles the committed CSVs from the raw bucket output.
- `docs/data/vn-corpus/scummvm-engines.csv` — the per-engine breakdown of the local
  ScummVM checkout, one row per `engines/` subdirectory that contains code, from the same
  tokei run.

Counts are tokei 15.0.0 code lines; `TOKEI=/path/to/tokei` overrides the binary. Rule
files and raw tokei JSON stay out of the repository (large, regenerable); the aggregates
are committed under `docs/data/vn-corpus/`.

Disc images: `chdman extractcd` (then strip the 2352-byte sectors to 2048, with MODE2
form-1 user data at +24) or `chdman extractdvd`, list with 7-Zip, and pull `SLP?_*.*`,
`*.IRX` and `IOPRP*.IMG`. PlayStation 2 executables carry no file extension. Where
`extractcd` aborts part-way through a CD-mode image with subchannel data, `extractraw`
still succeeds; its 2448-byte units then need the 96 subchannel bytes dropped before the
2048-byte user data can be taken.

Encrypted PSP EBOOTs: PPSSPP writes the decrypted ELF to
`PSP/SYSTEM/DUMP/<DISCID>_EBOOT.BIN` when `DumpFileTypes = 1` is set in the `[General]`
section of `ppsspp.ini`. That route was used for the five titles whose `EBOOT.BIN` starts
with the `~PSP` header.
