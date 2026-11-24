---
title: "Soalo: scripts"
description: "The two Squirrel script layers in the Zero no Tsukaima PS2 engine (.nut modules and .ks scene scripts), how Squirrel was modified, and a quickbms script that recovers the script text."
type: engine
status: draft
confidence: mixed
tags:
  - playstation-2
  - squirrel
  - scripting
  - quickbms
  - zero-no-tsukaima
platforms:
  - PlayStation 2
games: []
formats: []
maturity: partial
sources:
  - title: Wikipedia — Squirrel (programming language)
    url: https://en.wikipedia.org/wiki/Squirrel_(programming_language)
  - title: Squirrel programming language
    url: https://www.squirrel-lang.org/
  - title: Squirrel reference manual
    url: https://www.squirrel-lang.org/squirreldoc/
last_verified: 2026-11-24
ai_assisted: true
---

# Soalo: scripts

The games are written in [Squirrel](https://www.squirrel-lang.org/), but not in plain Squirrel. That these three titles use Squirrel is already stated publicly, on Wikipedia's [Squirrel article](https://en.wikipedia.org/wiki/Squirrel_(programming_language)); what follows is the part that is not published — which version, and how the scripts are stored. Two separate script layers are visible in the data, and the interpreter itself was modified in ways that matter for anyone trying to read or rebuild the scripts.

## At a glance

| | |
| --- | --- |
| Language | Squirrel 2.1.2 (`Squirrel 2.1.2 stable` in the Fantasy and Symphony executables) |
| Layer 1 | `.nut` modules — engine object model, loaded with `dofile` |
| Layer 2 | `.ks` scene scripts — per-scene content, referenced by name from a scene table |
| Compilation | Offline; source ships either as pages in `SYSTEM` or compressed in `SCENE_ID`, alongside compiled units |
| Serialisation | Squirrel closure streams (`FA FA` + `SQIR` reversed), plus plain `.nut` source |
| Debug support | Present in Concerto, stripped from Fantasy and Symphony |

## Layer 1: the `.nut` module set

Symphony's `SYSTEM.BIN` yields 340,446 bytes of source across 36 `dofile` modules, 65 `class` and 972 `function` declarations. Fantasy ships the same module list with 57 classes and 806 functions. The structure is a small scene-graph framework:

| Group | Modules |
| --- | --- |
| Core | `main.nut`, `game.nut`, `scenes.nut`, `variables.nut`, `util.nut`, `Object.nut`, `override.nut` |
| Rendering | `BasicLayer.nut`, `GraphicLayer.nut`, `translayer.nut`, `TEXTLAYER.NUT`, `multilayers.nut`, `EnvImage.nut` |
| Environment | `Environment.nut`, `envinit.nut`, `EnvObject.nut`, `EnvBase.nut`, `EnvLayer.nut`, `EnvBackLayer.nut`, `EnvStageLayer.nut`, `EnvLevelLayer.nut`, `EnvEventLayer.nut`, `EnvSimpleLayer.nut`, `EnvCharacter.nut` |
| Player | `player.nut`, `GamePlayer.nut`, `ScenePlayer.nut`, `action.nut` |
| Interface | `msgwindow.nut`, `dialogwindow.nut`, `selectwindow.nut`, `buttonlayer.nut` |
| Audio | `EnvBGM.nut`, `EnvSE.nut`, `voices.nut`, `sysvoices.nut` |

The modules are loaded by name at startup:

```text
sysvoices <- dofile("sysvoices.nut")
dofile("util.nut", true);
dofile("Object.nut", true);
```

`dofile` is Squirrel's own standard-library function, so the engine relies on stock source-file loading for this layer rather than on a custom loader.

The `action.nut` layer is the most characteristic part of the framework: it declares `ActionInfo`, `ActionLoopInfo`, `ActionSequense`, `ActionHandler`, `AbsoluteActionHandler`, `RelativeActionHandler`, `DefaultAction`, `MoveAction`, `LoopMoveAction`, and `VibrateAction`, which is how screen and character motion is expressed in script rather than in native code.

## Layer 2: the `.ks` scene scripts

`.ks` is a second script format, and it is where the scene content lives. The names appear in `SYSTEM`'s string pool as tagged strings sitting next to short slot labels:

```text
... main TRAP Y ... TRAP \x10\x00\x00\x08 \n\x00\x00\x00 ST01_06.ks
    \x10\x00\x00\x08 \x04\x00\x00\x00 next
    \x10\x00\x00\x08 \x0c\x00\x00\x00 ST10E_M03.ks ...
```

Reading that as a table: each scene entry consists of a **slot label** and a **`.ks` file name**. The recurring labels are:

| Slot | Reading |
| --- | --- |
| `main` | The scene's default script |
| `TRAP` | An alternate script for a scene branch |
| `TRAPY` | A third branch of the same idea |
| `next` | The script that hands off to the following scene |

The names themselves follow a scene-id pattern: `ST01_06.ks`, `ST10E_M03.ks`, `ST09C_M01.ks`, `ST09G_01.ks`, `st02_08.ks`, `BK3B_M01.ks`, `BK4B_M01.ks`, `TU_05C.ks`. The `ST`/`BK`/`TU` prefixes and the trailing `_Mxx`-style suffixes look like a chapter/branch/shot scheme; that reading is **inferred** from the name shapes and not confirmed by anything in the data.

Three things follow from the evidence:

1. **Each scene entry names a `.ks` file, and `SCENE_ID` holds one module per scene.** The pairing is a slot label plus a file name. Every `SCENE_ID` record carries a single `DataMake/SCENE/<name>.nut` build path, and the names — `bk1a_00.nut`, `bk1b_01.nut`, `bk4a_09.nut` — sit in the same prefix/suffix scheme as the `.ks` names. The bodies are compiled Squirrel closures on Fantasy and Symphony and source on Concerto. On the inspected Symphony pair, 596 of the 600 records share a stem with a `.ks` name in `SYSTEM` once the extension is dropped; the four that do not (`st08_00`, `tu_chk`, `tu_yost`, `tun_staff`) are scenes the narrative table leaves out. So the two layers carry the same names under two extensions, and neither container spells the other's.
2. **Scenes were generated by a build tool.** `SYSTEM`'s string list contains `DataMake/SCENE/LESSON.NUT`, and the executable's string pool has `/DataMake/` immediately beside `%s\%s.HD;1`. So `DataMake` was the tool that turned authored `.ks` scenes into `SCENE_ID` records, and `LESSON.NUT` is one of its own control scripts.
3. **The slot labels give the runtime its entry points.** `main`, `TRAP`, `TRAPY`, and `next` are what the scene player selects between, which matches the native calls `getScene(%d)`, `setStartScene`, and `isExistScene` in the executable.

Symphony's `SYSTEM` references 624 `.ks` names; Fantasy's references one. The difference is not a counting artefact — Fantasy's container is a third smaller, its record map is shorter, and the scene table has plainly moved or been trimmed between the two builds. That is one more reason to treat the `.ks` table as a build artefact rather than a fixed structure.

## How modified is the Squirrel?

| Aspect | Stock Squirrel | Soalo |
| --- | --- | --- |
| Language syntax | `<-`, `class`, `function`, `local` | Same, in shipped source |
| Source loading | `dofile` on `.nut` at runtime | Same for the module layer |
| Compiled units | `.cnut` from `sqcompiler`, opening `FA FA` + `SQIR` | Same stream shape, tag stored reversed as `RIQS`; units sit in the compressed blocks |
| String resources in packed data | Squirrel string objects | Length-prefixed strings behind the tag `0x08000010` |
| Block compression | none | Socio Art Logic command stream, 2048-byte-aligned blocks; see [textures](textures.md) |
| Scene content | n/a | Separate `.ks` layer, not Squirrel's own file type |
| Host API | registered C functions | Registered `tkl*` classes, e.g. `tklVTextBox`, `tklTim2Data` |
| Debug support | serializer, stdio, `CALLSTACK`/`LOCALS` identifiers | Present in Concerto; stripped from Fantasy and Symphony |

So the answer to "is it really just Squirrel" is: the language and the VM are stock, but the packaging is not. There are no loose `.cnut` files — the closure streams are packed into `SYSTEM` or into compressed blocks — string resources use a house tag, content is authored in a second script dialect (`.ks`), and Concerto still contains the debug machinery that Fantasy and Symphony removed. The version is not constant either: Symphony and Fantasy carry 2.1.2, while *Kazeiro Surf*, a 2009 game from the same developer, carries 2.2.2. A Squirrel version string is therefore not a family test.

## Extracting the `.nut` source

Fantasy and Symphony keep the source as one complete file per record inside `SYSTEM.BIN`, so the splitter below is enough: it walks the index, appends the text records in order and skips the compiled ones. Concerto has no `SYSTEM` pair at all — its modules sit in `SCENE_ID.BIN` as compressed, interleaved blocks, and the scene-module extractor on the [payload](payload.md#extracting-the-scene-modules) page decodes them, with no record walk on top. Decoding one gives plain Squirrel source, not scene data: the first block at offset 2048 declares 34,593 bytes and begins `/** * レイヤアクションモジュール関係クラス */ class LayerModule {`, and roughly a third of its blocks contain `function` definitions.

```quickbms
# zero-no-tsukaima-nut-dump.bms
#
# Recovers the Squirrel script text from a Soalo container.
#
#   quickbms zero-no-tsukaima-nut-dump.bms SYSTEM.HD out/
#
# Input : a .HD index; the matching .BIN is opened from the same folder.
# Output: scripts_dump.nut in the output folder.
#
# The records hold two kinds of module. Ones shipped as source are plain
# Shift-JIS text. Ones shipped compiled open with the closure head
# FA FA 52 49 51 53 (SQIR reversed as RIQS) and are skipped here. Text
# records are appended in record order with their 0xFF fill removed,
# so the result is one continuous script stream, not one file per record.
#
# Measured with QuickBMS 0.12.0:
#   Symphony (SLPS_258.98)  SYSTEM.HD   31 text records, 339,371 bytes
#   Fantasy  (SLPS_258.30)  SYSTEM.HD   30 text records, 285,957 bytes
#
# Concerto (SLPS_257.08) ships no SYSTEM pair. Its modules sit in SCENE_ID.BIN as
# compressed, interleaved blocks; the scene-module extractor on the payload page
# decodes those into plain Squirrel source.
#
# The text is Shift-JIS with ASCII syntax, so the output is readable source
# with Japanese comments.

endian little

set MIN_PRINT_PERCENT long 50
set SAMPLE long 8192

get HD_SIZE asize 0
math REC_COUNT = HD_SIZE
math REC_COUNT /= 4

get HD_NAME basename
string BASE_NAME = HD_NAME
string BASE_NAME -= ".HD"
string BIN_NAME = BASE_NAME
string BIN_NAME += ".BIN"

open FDSE BIN_NAME 1
get BIN_SIZE asize 1

append
set OUT_NAME string "scripts_dump.nut"
set TOTAL long 0
set TEXT_RECS long 0
set COMPILED_RECS long 0

set REC_START long 0

for i = 0 < REC_COUNT
    get REC_SIZE long 0

    set COMPILED long 0
    if REC_SIZE >= 8
        goto REC_START 1
        get B1 byte 1
        get B2 byte 1
        if B1 == 0xFA
            if B2 == 0xFA
                get TAG long 1
                if TAG == 0x53514952
                    set COMPILED long 1
                endif
            endif
        endif
    endif

    set WANT long REC_SIZE
    if WANT > SAMPLE
        set WANT long SAMPLE
    endif

    set GOOD long 0
    if WANT > 0
        goto REC_START 1
        For P = 0 < WANT
            get B byte 1
            math P += 1
            if B >= 0x20
                if B <= 0x7E
                    math GOOD += 1
                elif B >= 0x81
                    if B <= 0x9F
                        math GOOD += 1
                    elif B >= 0xE0
                        if B <= 0xFC
                            math GOOD += 1
                        endif
                    endif
                endif
            elif B >= 0x09
                if B <= 0x0D
                    if B != 0x0B
                        if B != 0x0C
                            math GOOD += 1
                        endif
                    endif
                endif
            endif
        Next
    endif

    set PERCENT long 0
    if WANT > 0
        set PERCENT long GOOD
        math PERCENT *= 100
        math PERCENT /= WANT
    endif

    if COMPILED == 0
        if PERCENT >= MIN_PRINT_PERCENT
            set REC_END long REC_START
            math REC_END += REC_SIZE

            set RUN_START long REC_START
            goto REC_START 1
            set P long REC_START
            For P = P < REC_END
                get B byte 1
                math P += 1
                if B == 0xFF
                    math LEN = P
                    math LEN -= 1
                    math LEN -= RUN_START
                    if LEN > 0
                        log OUT_NAME RUN_START LEN 1
                        math TOTAL += LEN
                    endif
                    set IN_RUN long 1
                    For IN_RUN = IN_RUN == 1
                        if P >= REC_END
                            set IN_RUN long 0
                            break
                        endif
                        get B byte 1
                        math P += 1
                        if B != 0xFF
                            set IN_RUN long 0
                        endif
                    Next
                    if P >= REC_END
                        math RUN_START = REC_END
                    else
                        math RUN_START = P
                        math RUN_START -= 1
                    endif
                endif
            Next

            math LEN = REC_END
            math LEN -= RUN_START
            if LEN > 0
                log OUT_NAME RUN_START LEN 1
                math TOTAL += LEN
            endif
            math TEXT_RECS += 1
        endif
    else
        math COMPILED_RECS += 1
    endif

    math STEP = REC_SIZE
    math STEP += 2047
    math STEP /= 2048
    math STEP *= 2048
    math REC_START += STEP
next i

if TOTAL > 0
    string MSG p= "appended %d text records, skipped %d compiled, %d bytes" TEXT_RECS COMPILED_RECS TOTAL
    print "%MSG%"
else
    print "no text records found"
endif
```

Both games open with the same module: `// XXX 画面サイズ定義`, then `SCWIDTH  <- 640;` and `SCHEIGHT <- 448;`, and both end with the `TextLayer` class definition. Symphony yields 339,371 bytes from 31 records, Fantasy 285,957 bytes from 30. Everything else in the pair is either a compiled unit — ten in Symphony, six in Fantasy — or the one zero-length record that each index carries.

Because the text is Shift-JIS, open the output with an encoding-aware editor or convert it first:

```sh
iconv -f CP932 -t UTF-8 scripts_dump.nut > scripts_dump.utf8.nut
```

## Unknowns

- The `.ks` grammar. Only the name table is visible; the dialect itself is described nowhere in the data.
- Whether `TRAP`/`TRAPY` are literally trap events or unrelated branch labels.
- The table that turns a `.ks` name into a `SCENE_ID` record number. The names match, but scripts address records numerically, so a lookup exists and has not been read.
- Whether Symphony compiles `.nut` at runtime or only deserialises packed units; the retained serializer and `dofile` strings support either reading.
