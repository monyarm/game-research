---
title: "Soalo: executable findings"
description: "What the three Zero no Tsukaima PlayStation 2 executables reveal: the loader, the embedded Squirrel VM, the tkl* engine classes, and the differences between builds."
type: engine
status: draft
confidence: mixed
tags:
  - playstation-2
  - squirrel
  - executable
  - zero-no-tsukaima
platforms:
  - PlayStation 2
games: []
formats: []
maturity: partial
sources:
  - title: Squirrel programming language
    url: https://www.squirrel-lang.org/
last_verified: 2026-11-23
ai_assisted: true
---

# Soalo: executable findings

The three games ship one PlayStation 2 ELF each. All three are the same engine built three times: the loader, the script VM, and the engine class set are identical in substance, while the data names and the amount of retained debug support change from build to build.

## At a glance

| Game | Executable | Size (bytes) |
| --- | --- | ---: |
| *Koakuma to Harukaze no Concerto* (2007-02-15) | `SLPS_257.08` | 1386560 |
| *Muma ga Tsumugu Yokaze no Fantasy* (2007-11-29) | `SLPS_258.30` | 1232184 |
| *Maigo no Period to Ikusen no Symphony* (2008-11-06) | `SLPS_258.98` | 1292816 |

## Detection

| File | Size (bytes) | MD5 (first 5,000 bytes) | SHA-256 |
| --- | ---: | --- | --- |
| `SLPS_257.08` | 1386560 | `17a99f182e771f4a51f6b5ca4b35244c` | `f60ee07a7218347945f2e2ca48761abc21f5b4b923e07357c9d54913e6347947` |
| `SLPS_258.30` | 1232184 | `73089599a51dcdb5af3e5e207e64384f` | `143c42a1f6b42292135e9a0f71b9987af53cb4ccc2d1365027547de515796679` |
| `SLPS_258.98` | 1292816 | `b08f8a67dacc99910f5a935c2497c2c7` | `1214a80193ae7108dcd188c008cb75cc776a283d9a0283d4c28eb3f70e4385e4` |

The whole-file MD5 of `SLPS_258.98` is `9afa0f13a185058060f856eee60523e2`, recorded here only because the full file was hashed; detection uses the size and first-5,000-byte pair above.

## The loader

All three executables build their data file names by substitution. The literal format strings are the clearest statement of how the engine organises its data:

```text
cdrom0:%s\%s.BIN;1
cdrom0:%s\%s.HD;1
%s\%s.BIN;1
%s\%s.HD;1
cdrom0:\IOP\
cdrom0:/MOVIE/%s
```

The same fragment `%s\%s.HD;1` appears next to `/DataMake/` in the string pool, which is the only remaining trace of the build tool that produced the data.

The five data names shared by all three executables are `NORMAL`, `SCENEDAT`, `SCENE_ID`, `SOUND_ID`, and `VOICE_ID`. Symphony and Fantasy add a sixth, `SYSTEM`. Concerto does not: its only `SYSTEM` strings are memory-card paths (`MEMORYCARD:SYSTEMDATA`, `MEMCARD:SYSTEMSAVE`). That is the strongest evidence that Concerto folded the script library into a different container — see [payload layout](payload.md).

### The three archives and how a record is addressed

In Symphony's executable the container layer registers three archives at `0x1155e8`, each bound to a name string in the pool: archive 0 to `NORMAL`, 1 to `SCENE_ID`, and 2 to `SCENEDAT`. A record is addressed by a single word, `(archive << 24) | record`, which is why the script source names its targets as `(0x01000000 + 1861)` and `(0x02000000 + 1)` — `SCENE_ID` record 1861 and `SCENEDAT` record 1.

The read path is short and separate from the scripting layer:

| Routine | Role |
| --- | --- |
| `0x117af0` | Record size, in 2048-byte units |
| `0x117aa8` | Record start, in the same units |
| `0x117cd8` | Copies the record into a caller buffer; branches on an archive mode field at `+0x120` (direct copy, compressed, or table lookup) and can serve from a preloaded image when `+0x2d8` is set |
| `0x115960` | Whole-record read: takes the address word, allocates the rounded size, calls the reader, and prints `data2size:%8d  ReadCh = %3d` from the string at `0x2286a8` |
| `0x1163d8` | Block decode: reads the decoded size at `+0`, allocates, runs the codec on the stream at `+8`, then calls `0x116348` |
| `0x116348` | Transpose by the interleave factor at `+4`, described on the [payload](payload.md) page |

Records with a declared size above 64 KB leave the single-shot path and go through a chunked channel set (`0x120e58`, `0x121910`, `0x125b20`, `0x11d948`), which is the machinery behind the `ReadCh` counter in that debug line.

These addresses are from the inspected Symphony copy; the two later builds were not compared routine by routine.

Two strings are unexplained and left alone: every build carries `cdrom0:\SLPM_654.48;1`, a serial that matches none of these three games, and Concerto carries a Shift-JIS disc-access message (`…ディスクアクセスにトランスポートしました。`) beside the loader strings.

## Embedded scripting: Squirrel 2.1.2

Symphony and Fantasy contain the literal version string `Squirrel 2.1.2 stable`. All three contain the stock Squirrel translation unit names:

```text
sqapi.cpp          sqcompiler.cpp     sqfuncstate.cpp
sqlexer.cpp        sqobject.cpp       sqobject.h
sqstate.cpp        sqstdaux.cpp       sqstdstring.cpp
sqtable.cpp        sqvm.cpp
```

The game logic is exposed to script through engine classes, not the other way around. The `tkl` prefix covers the drawing and resource layer:

```text
tklVTextBox     tklDrawContext   tklTim2Data      tklPs2DrawDriver
tklVComponent   tklVComposite    tklVPlane        tklVRectangle
tklVImage       tklVPoint        tklVColor        tklVClipper
tklFSEffect     tklFSAF          tklRand          tklIntpMove*
tklMemory       tklData          tklSifAlloc*     tklSpuAllocIopHeap
```

Other engine-side translation units visible in the string pool are `VComponent.cpp`, `VTextBox.cpp`, `MatrixStack.cpp`, and `IntpMove.h`, and the include path `../SoaloPS2/Bit.h` gives the engine the internal name this notebook uses — `Soalo` being *Socio Art Logic* (有限会社ソシオ・アートロジック) compressed to its initials.

The visual-novel vocabulary is native code, not script text. The strings that show the dialogue model are:

```text
Talk(ch(%d),voiceid(%d))
getScene(%d)          setStartScene        isExistScene
SeqStart              McGetSeqEvent
No channel seq        TalkFade Voice channel over
tklVTextBox::formatStrCat: string too long!!!
******* TEXT LENGTH OVER ********
```

`Talk` takes a character id and a voice id, which is why every dialogue entry in the data carries a speaker tag and a `RUZ300xx` voice id.

` <- ` — Squirrel's slot assignment operator — does not occur in any of the three executables, so no script source is embedded in any binary. The script text lives entirely in the data files.

## Build differences

| Observation | Concerto (2007-02) | Fantasy (2007-11) | Symphony (2008-11) |
| --- | --- | --- | --- |
| `SYSTEM` as a data name | absent | present | present |
| Version string `Squirrel 2.1.2 stable` | absent | present | present |
| `.nut` string in executable | absent | present | present |
| Squirrel serializer and debug identifiers | present | stripped | stripped |
| `dofile`, `.sb`, `.sc`, stdio registration | present | stripped | stripped |
| Standard pad-button table `KEY_*` / `KEY2_*` | absent | present | present |
| `DLGMD_*`, `MC_EVT_*`, `CREATEFILE`, `CHDIR`, `GETINFO` | absent | present | present |

Note the direction: Concerto keeps Squirrel's serializer and standard library registrations and has no `SYSTEM` data name, while Fantasy and Symphony strip that support and gain a `SYSTEM` container. Retention of the serializer in Concerto is consistent with the engine still compiling or deserialising script at that stage rather than only consuming a prepared container.

Concerto also carries strings the other two builds do not: the twelve character codes `HARU`, `HARUNA`, `HENRIETTA`, `KIRCHE`, `LUIZ`, `SIESTA`, `TABITHA`, `KURU`, `SIES`, `TABA`, `ANLI`, `FLUG`, the battle movie names `BTLMOV00`–`BTLMOV23`, the action table `EFC_ANM_END`, `EFC_ANM_EXEC`, `EFC_ANM_READING`, `EFC_ANM_STANDBY`, and the `CLEAR`, `LOAD`, `SAVE`, `_INIT` state labels. That build has a battle sequence with its own movies; Fantasy and Symphony have no `BTLMOV` references at all.

## Movies and audio

Movies are opened through `cdrom0:/MOVIE/%s` and are plain PS2 MPEG-2 `.PSS`, in all three builds. Audio is sequenced rather than streamed, which is why `SOUND_ID` holds banks instead of music files — see [payload layout](payload.md).

## What is not in the executables

- No company name, copyright line, or developer credit. A string search for publisher and studio names returns nothing, so release attribution comes from external catalogues only.
- No engine name beyond the `../SoaloPS2/` include path and the `tkl` class prefix.
- No embedded script source, as noted above.

## Unknowns

- What `cdrom0:\SLPM_654.48;1` refers to, and why it survived into all three builds.
- Whether Concerto compiles or deserialises script at runtime. The retained serializer and standard-library registrations suggest one of the two; the data layout suggests the compile path was still live.
- The build ordering implied by the strings (serializer present in the 2007-02 build, stripped later) has not been confirmed against the games' own behaviour.
