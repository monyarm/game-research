---
title: "AliceSoft System 3.x: forks and patches"
description: "Every open descendant of the System 3.x runtimes, what each one actually changes, and the handful of changes worth folding into a new port."
type: engine
status: draft
confidence: observed
tags:
  - alicesoft
  - system3
  - porting
  - forks
aliases:
  - System3 forks
  - SysEng
platforms:
  - Windows
games: []
formats: []
maturity: partial
sources:
  - title: kichikuou/system3-sdl2
    url: https://github.com/kichikuou/system3-sdl2
  - title: kichikuou/xsystem35-sdl2
    url: https://github.com/kichikuou/xsystem35-sdl2
  - title: AliceSoft Wiki — SysEng 0.8
    url: https://alicesoft.miraheze.org/wiki/User_blog:RottenBlock/SysEng_0.8
  - title: AliceSoft Wiki — System Programming Resources
    url: https://alicesoft.miraheze.org/wiki/User_blog:RottenBlock/System_Programming_Resources
  - title: GameBrew — system3 for PSP
    url: https://www.gamebrew.org/wiki/System3_for_PSP
  - title: monyarm/NovelVM — issue 5
    url: https://github.com/monyarm/NovelVM/issues/5
last_verified: 2026-11-25
ai_assisted: true
---

# AliceSoft System 3.x: forks and patches

There are two bases and six descendants, and only one of the descendants contains anything a new loader would not already have to write. This page measures what each one changes, so the port can take the base and lift the small patches rather than adopting a tree.

## The two bases

| Base | Covers | Licence |
| --- | --- | --- |
| `system3-sdl2` | System 1–3.0, the DOS-era VM | GPL-2.0, 19,600 lines in `src/` |
| `xsystem35-sdl2` | System 3.5–3.9 | GPL-2.0-or-later, ≈49,300 portable lines |

`system3-sdl2` is an SDL port of Takeda Toshiya's `system3 for win32`; `xsystem35-sdl2` is an independent implementation descended from Chikama's xsystem35. Neither is a fork of the other and neither is a fork of the other's base, so a permission or licence question about one does not carry to the other.

## Descendants, measured

| Project | Author, date | What it changes | Verdict |
| --- | --- | --- | --- |
| `system3-sdl2` | kichikuou, active | Port of the DOS-era archive to SDL2/3 with UTF-8, game detection, save states, modern audio, Android and Emscripten targets | **base** |
| `xsystem35-sdl2` | kichikuou, active | Independent 3.5–3.9 runtime, Unicode output, built-in debugger | **base** |
| SysEng 0.8 | RottenBlock, 2026-02-10 | ≈400 changed lines over `system3-sdl2` v1.7.2: six font slots, `Y 242`–`Y 247`, font sizes above 5, `x_coord` override, experimental System 2 rendering, new CRC table | **lift two patches** |
| system3 for SDL / PSP | shinshin319, 2006-09-29 | Same file set as Takeda's `src/sys/`, rewritten around SDL; drops `ags_bmp`, `ags_gm3`, `ags_vsp2l`, `mako_midi`, `nact_sys1`, `nact_sys2`; its README gives up save/load and sound | ignore |
| System3 for OS/2 Warp | SofiyaCat, 2006-12-22 | Backend swap of the above to OS/2 Warp 4, Open Watcom 1.5 | ignore, and unreachable |
| XSystem35 Lite | shinshin319, 2006-10-03 | Chikama's 3.5 tree with the X11 and SDL dependencies stripped out; all `cmd*.c` retained | ignore |
| nine GitHub forks of `system3-sdl2` | various | Nothing ahead of upstream except one CI tweak and one stale localisation branch | ignore |

## What SysEng actually changes

Measured by diffing the 0.8 source against `system3-sdl2` at tag `v1.7.2`. Changed-line counts, ignoring `.bak` files:

| File | Changed lines |
| --- | ---: |
| `src/sys/nact.cpp` | 129 |
| `src/sys/nact_sys2.cpp` | 107 |
| `src/sys/nact_sys1.cpp` | 74 |
| `src/sys/ags_text.cpp` | 30 |
| `src/sys/nact.h` | 17 |
| `src/sdlmain.cpp`, `src/sys/ags_window.cpp`, `src/config.*` | under 10 each |

That is the whole delta. Everything else in the tree is `system3-sdl2` v1.7.2 with backups beside it, which is why the author's own manual says "if you're not interested in these features, system3-sdl2 is probably the better choice".

### The x-coordinate override

The one change that corrects observed behaviour rather than presentation. System 2 and 3.0 commands that place text support "column mode", which rounds to the nearest 8 pixels; with column mode off, the `system3-sdl2` implementation does not always match the original AliceSoft output — the author names *Rance 4.1* and *Rance 4.2* as examples — and the override corrects it.

It is one configuration flag, `x_coord = true` in the `[CONFIG]` section of `system3.ini`, and the author warns that enabling it for a game that does not need it introduces a different set of errors. So it has to be per-game, decided by whatever detection the runtime already does, not a global default.

Value to a port: real fidelity for the DOS-era family, small enough to read in an afternoon. It does nothing for System 3.5–3.9 titles.

### Six font slots and the `Y` commands

Upstream supports one monospace font file. SysEng supports three monospace and three variable-width slots, loaded from extra `system3.ini` keys:

| Key | Slot |
| --- | --- |
| `fontfile`, `fontfile1`, `fontfile2` | monospace 0, 1, 2 |
| `vfontfile`, `vfontfile1`, `vfontfile2` | variable-width 0, 1, 2 |

Switching happens through new extend commands:

| Command | Effect |
| --- | --- |
| `Y 242, X` | menu: monospace (1) or variable-width (0) |
| `Y 243, X` | message box: monospace or variable-width |
| `Y 244, X` / `Y 245, X` | menu / message box monospace font slot, 0–2 |
| `Y 246, X` / `Y 247, X` | menu / message box variable-width font slot, 0–2 |

A missing or unloadable font falls back to the default monospace face in that slot, purely to avoid a crash; using a monospace face in a variable-width slot produces kerning errors. Changing the slot affects only text emitted afterwards — already-rendered text keeps its font until the message box or menu is redrawn.

Value to a port: none for playing retail titles, since no shipped game emits `Y 242`–`Y 247`. It matters for a translation build that wants a proportional face, and for understanding how variable-width text is measured and wrapped. Read it; do not port it wholesale.

### Font sizes above 5

Upstream accepts `Y 25`/`Y 26` sizes 1–5 (16, 24, 32, 48, 64 points). SysEng accepts any larger number and generates the face on demand. Same category as the slots: a localisation convenience, not engine behaviour.

### What not to carry

- **The experimental System 2 hunks.** The manual calls them "experimental and unstable" and says to copy upstream's code back if they misbehave. The 74 and 107 changed lines in `nact_sys1.cpp` and `nact_sys2.cpp` are that experiment; a port should start from upstream and take specific fixes only with a title that shows the fault.
- **The CRC table.** `nact_crc32.cpp` is game detection data, not engine logic.
- **The 2006 ports.** They are fourteen years older than the current base, implement less, and in shinshin319's case drop save/load and sound by design. Their only interest is historical: they show the code was portable and public years before GitHub.

## Using them with a base

The practical shape is: implement from the base, then carry SysEng's `x_coord` logic as a per-game option and consult its font code only when text layout needs to be proportional. Nothing here justifies forking either base or vendoring SysEng's tree.

Licence note: SysEng is a fork of a GPL-2.0 runtime and inherits it. Its own distribution is a zip on a wiki blog, so there is no repository and no commit history to cite — the version is "0.8, last edited 2026-02-10".

## Sources

- [kichikuou/system3-sdl2](https://github.com/kichikuou/system3-sdl2) — base, and tag `v1.7.2` used for the diff
- [kichikuou/xsystem35-sdl2](https://github.com/kichikuou/xsystem35-sdl2) — System 3.5–3.9 base
- [AliceSoft Wiki — SysEng 0.8](https://alicesoft.miraheze.org/wiki/User_blog:RottenBlock/SysEng_0.8) — source and EXE archives
- [AliceSoft Wiki — System Programming Resources](https://alicesoft.miraheze.org/wiki/User_blog:RottenBlock/System_Programming_Resources) — the listing this page's custody of SysEng's manual comes from
- [GameBrew — system3 for PSP](https://www.gamebrew.org/wiki/System3_for_PSP) — mirror of shinshin319's 2006 port
- [NovelVM issue 5](https://github.com/monyarm/NovelVM/issues/5) — where the port work is tracked
