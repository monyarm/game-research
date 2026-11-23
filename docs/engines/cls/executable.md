---
title: "CLS executable"
description: "What the Code Geass: Lost Colors PSP executable contains: a stripped Metrowerks ELF, an in-house clsOO framework, and CRI audio and video middleware."
type: note
status: draft
confidence: observed
tags:
  - playstation-portable
  - elf
sources:
  - title: VNDB — Code Geass ~Hangyaku no Lelouch~ Lost Colors
    url: https://vndb.org/v1502
last_verified: 2026-11-23
ai_assisted: true
---

# CLS executable

The inspected copy of *Lost Colors* is an extracted disc tree, and it ships the program twice: `SYSDIR/BOOT.BIN` is a plaintext ELF, and `SYSDIR/EBOOT.BIN` is the same build encrypted the way the hardware requires. All of the findings below come from the plaintext copy, so no emulator or decryption step was involved.

## Detection

| File | Size (bytes) | MD5 (first 5,000 bytes) | SHA-256 |
| --- | ---: | --- | --- |
| `BOOT.BIN` | 1543164 | `40afbc56d7cd1fd3ed729ed8497c5f11` | `e45ded7e8bfab91cb99e2c8bca3d95e5690fe66e455e5e3a01a79a30698758ba` |
| `EBOOT.BIN` | 1543504 | `6e3fdf33b24d7f35ba82650f278f941c` | `ae8d0315427ef4811d6804d3e30466b06084e10babca7d02743cd6fae28d12a8` |

The two differ in size because the encrypted form carries a `~PSP` header over the same program.

## Shape

ELF32, little-endian, MIPS. Type `0xffa0`, entry `0x3895c`, flags `0x10a23001`, 24 sections. `.text` sits at file offset `0x54` with a virtual address of 0, size `0xec320`; `.data` follows at `0xed4a8`, virtual address `0xed454`, size `0x3d28c`. `.comment` reads `MW MIPS C Compiler (2.4.1.01)` and `PSP`, so this is a Metrowerks CodeWarrior build.

There is no symbol table. `readelf -s` returns nothing and `.symtab` is absent, which matters for the decoding work: the container names and class names survive as strings, but the functions around them do not have names.

## The framework

Sixteen class-name strings survive, and they split cleanly into two layers.

| Layer | Classes |
| --- | --- |
| Game framework | `clsOOSystem`, `clsOOGraphics`, `clsOOFontSystem`, `clsOOPeripheral`, `clsOOMainHeap`, `clsOOVramHeap`, `clsOOVecCalc`, `clsOOTimer`, `clsWindowObj` |
| Platform shim | `clsPSPSystem`, `clsPSPCriticalSection` |

A static initialiser for at least one of these is present as `clsOOSystem::clsOOSystem`, so the names are real class symbols rather than log tags. The split is the interesting part: graphics, fonts, heaps, timing and windowing all live in the game layer, and the PSP layer is thin enough to be a portability shim. That is why the engine is named after the `cls` prefix rather than after the game.

## Middleware

CRI supplies audio and video, and names its own versions in the binary:

- `ADXT/PSP Ver.10.05`
- `ADXF/PSP Ver.7.63 Build:Mar 15 2007`
- `ADXRT Ver.3.1.1`
- `ADXPSP Ver.1.06`

The container names the executable expects are `root.cvm`, `Movie.cvm`, `Voice.cvm` and `ScStr.cvm`. All four appear as expanded folders in the inspected tree, so the tree is a CVM set unpacked.

## Naming and scene addressing

Two format strings build the file names the engine asks for:

- `%s%03dB%s.p`
- `%s%03d%s.p`

Both take a prefix, a three-digit number and a language letter, which is how files like `000J.P` and `BG_A00B.P` are formed. The `J` is a language selector, so a build for another region would ask for the same scene number with a different letter.

## What is not in the executable

No scripting runtime is identifiable. There is no Squirrel, Lua or other interpreter banner, and no class names of the shape a script binding would leave behind. Either the script layer is compiled into the game code, or the scene data is interpreted by tables in `.data` — the container work on [Decoding the scene containers](decoding.md) is what will tell which.

## Sources

- [VNDB — Code Geass ~Hangyaku no Lelouch~ Lost Colors](https://vndb.org/v1502)
