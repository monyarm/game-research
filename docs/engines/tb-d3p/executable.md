---
title: "TB_D3P: executable"
description: "What the decrypted EBOOT.BIN of Tiger & Bunny — Hero's Day contains: a stripped ELF with no engine banner, its embedded path table, and how the encrypted module was decrypted."
type: engine
status: draft
confidence: observed
tags:
  - playstation-portable
  - executable
  - elf
  - tiger-and-bunny
platforms:
  - PlayStation Portable
games:
  - tiger-and-bunny-heros-day
maturity: partial
sources: []
last_verified: 2026-11-23
ai_assisted: true
---

# TB_D3P: executable

The game ships two executables and only one of them is real. `SYSDIR/BOOT.BIN` is 4,758,273 bytes of zeros — a placeholder, not a truncated program. `SYSDIR/EBOOT.BIN` is the actual module, encrypted, and it decrypts to a valid 32-bit MIPS ELF.

The decrypted ELF is the usual place to look for a middleware banner, and it has none. What it does have is the complete list of data files the engine loads, which is what these pages were built from.

## Getting the ELF

The encrypted module was decrypted with PPSSPP's own EBOOT dump, which writes the decrypted image to the emulator's dump directory as `<disc id>_EBOOT.BIN`. No external tool is involved, and the encrypted copy on the disc is untouched.

The result is the file described below. `BOOT.BIN` does not need decryption: it has no content to decrypt.

## Structure

| Property | Value |
| --- | --- |
| Format | ELF32, little-endian, MIPS |
| Entry point | `0x837f8` |
| Section headers | 54 |
| Section-name table | Empty — fully stripped |
| Symbol names | None; `SYMTAB` is present but `STRTAB` is one byte |

| Section | Address | File offset | Size |
| --- | ---: | ---: | ---: |
| `.text` | 0 | `0x100` | `0x9a224` |
| `.rodata` | `0x9ade0` | `0x9aee0` | `0x52b20` |
| `.data` | `0xed900` | `0xeda00` | `0x373611` |
| bss | — | — | `0x129edc4` |

The bss is about 19.4 MB, which is the game's working heap rather than anything recoverable from the file.

`.rodata` is almost entirely images. It opens with a PNG signature (`89 50 4e 47`), holds a 0x90 × 0x50 IHDR, repeats `MiCCPPhotoshop ICC profile` throughout, and ends an image at `0xe36ac`. These are the interface graphics the game draws itself, not text.

## No identifying strings

Searches of the decrypted ELF for `Metrowerks`, `MW `, `ProDG`, `gcc`, `libstdc`, `cygwin`, `Sony`, `SN Systems`, `Copyright`, `(C)`, `Co.`, `Inc.` and `Ltd` all return nothing. The only compiler fingerprint is the literal string `C++ runtime abort`, the Sony C++ runtime's message.

`.text` contains no ASCII runs longer than six characters apart from a handful of garbage sequences — no assertion messages, no source file names, no engine banner. So the executable cannot name the engine, and the name used here comes from the data files instead.

The one text the ELF does store in a readable form is its own save-data strings, and they are **UTF-8**: `』のプレイセーブデータです。`, `新規インストールデータ`, `ユーザーデータ`, `プレイセーブデータ`, `プレイデータ`. That is a useful negative result for the data files: the engine's own literals are UTF-8, while the game content is Shift-JIS, so a UTF-8 scan of the data files is not a test for stored text.

## The path table

`.data` holds the load paths the engine uses, with the prefix `disc0:/PSP_GAME/USRDIR/`:

```text
resident/loading0%02d.bin        resident/ResidentData.bin
event/ch%02d_00.evt              phase/bin/ev%02dData.bin
phase/texture/%s                 texture/%s
timesheet/sheet.bin              timesheet/tscom.bin
staffroll/rollpack.bin           menu/cutin.bin
menu/HeroSelectData.bin          menu/LunaticFire.bin
menu/keepout/keepout%02d.bin     menu/talk/TalkUiData.bin
menu/talk/CmxSelData.bin         menu/title/CopyLogo_Data.bin
menu/title/TitleMenu_Data.bin    menu/title/NewGame_Data.bin
menu/title/eyecatch%03d.bin      gallery/scene.bin
gallery/GalleryChrDatabaseText.bin   gallery/GalleryChrDatabaseThum.bin
gallery/GalleryMusicList.bin         gallery/GalleryPictureList.bin
gallery/GalleryPictureThum.bin       gallery/GalleryScore.bin
gallery/gcdb_pic.bin                 gallery/RsecAnz.bin
sound/se/SeData%02d.snd          sound/sysvoice/SysVoice%02dConfig.bin
sound/sysvoice/SysVoice%02dTitle.bin
/BGM/TM%03d.at3   /Voice/%03d/vo%03d%03d.at3   /EffSE/e%04d.at3
Data/SE/EffSeData%02d.dat
```

The format strings also give the asset naming conventions — `cha%02d%02d%02d.tpl`, `face%02d%02d%02d.tpl`, `face%02d%02d%02dnext.tpl` — plus enumerated lists of roughly 300 character and 200 face entries.

Audio is `.at3`, which is Sony's ATRAC3; the codec is not part of the engine. Video is `.pmf`, played through the separate `MODULES/PSMF.PRX`.

## What the engine is called

`TB_D3P` comes from a build path left in the chapter data: `D:/PSP/TB_D3P/deliver_tb_d3/event/csv/00/ev00000.csv`. The event scripts were authored as CSV files and compiled into the `.BIN` chunks, and the compiler kept the source path.

`TB_D3P` therefore reads as a project and deliverable name, not a product name. It is used here as an interim label and is not claimed to be the engine's real name.

## Detection

| File | Size (bytes) | MD5 (first 5,000 bytes) | SHA-256 |
| --- | ---: | --- | --- |
| `EBOOT.BIN` | 4758624 | `8362e7ed79c424f0febfdae9296a7c93` | `2e181ceabc905e733de9f4dbf65f03c9ce03db2dac5f949c4781a323cd39626e` |
| `BOOT.BIN` | 4758273 | `6bf95a48f366bdf8af3a198c7b723c77` | `cb362771ac2494a8a098d2c3ef0d3c49da021a6d0539907505e0dc00efc77f72` |

`BOOT.BIN`'s hashes identify the all-zero placeholder, not code. The two files differ by 351 bytes, so the placeholder is not a copy of `EBOOT.BIN` with the header stripped.

## Unknowns

- No compiler identification beyond `C++ runtime abort`. The section layout and the absence of names are consistent with a stripped commercial toolchain, but no specific toolchain is claimed.
- The gcc-style `$gp`-relative small-data model was not confirmed for this binary; no data-reference resolution was attempted.
- No second executable was inspected, so nothing is claimed about how much of this code other titles share.

## Sources

No public documentation of this executable was found. The description above comes from the inspected copy.
