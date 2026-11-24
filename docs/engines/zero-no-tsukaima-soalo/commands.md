---
title: "Soalo: scene command lists"
description: "How the Zero no Tsukaima PS2 scene scripts compile into one branchless Squirrel function of table constructors, the instruction encoding, the statement grammar the tables rebuild, and a quickbms script that writes out every scene's command list."
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
  - title: Squirrel programming language
    url: https://www.squirrel-lang.org/
  - title: Squirrel reference manual
    url: https://www.squirrel-lang.org/squirreldoc/
last_verified: 2026-11-24
ai_assisted: true
---

# Soalo: scene command lists

A `SCENE_ID` record on Symphony and Fantasy is one compiled Squirrel function, and an unusual one: it has no branches, no calls and no arithmetic. Every instruction either loads a literal into a slot, opens a table, stores one key and one value into that table, or appends the finished table to an array. The scene script is therefore carried as data, and the array the function returns is the scene's command list — one table per statement.

That makes the scene readable without a decompiler. A straight-line walk of the instruction array rebuilds every statement, and the tables show the script's own vocabulary: `tagname` tells you the statement, the remaining keys are its attributes.

## At a glance

| Question | Answer |
| --- | --- |
| What a scene record holds | One compiled Squirrel 2.1.2 function that returns an array of tables, one table per statement |
| Instruction size | 8 bytes |
| Opcodes the scenes use | 9 of the 61 the interpreter dispatches on |
| Statements recovered | 291,087 on Symphony, 346,695 on Fantasy |
| Where the strings come from | The literal table of each record, no separate string file |
| Confidence | observed, byte-checked against an independent parser |

## The closure stream

Each record starts with the game's own two-byte tag, then Squirrel's closure serialisation. The parts, as found in the inspected records:

| Offset | What is there |
| --- | --- |
| `0x00` | `FA FA`, the game's wrapper tag |
| `0x02` | `52 49 51 53`, Squirrel's closure-stream head |
| `0x06` | Character size, always `1` |
| `0x0a` | A part marker, then the build path of the source module |
| — | The prototype name, `main` |
| — | A part marker, then seven counts |
| — | Part marker and section for the literals |
| — | Part marker and section for the parameters |
| — | Part marker and section for the outer values |
| — | Part marker and section for the local variables |
| — | Part marker and section for the line table |
| — | Part marker and section for the instructions |
| — | Part marker and section for nested functions |
| — | A six-byte trailer, then `4c 49 41 54`, the stream tail |

The part marker is the ASCII text `TRAP` on disk, which is the little-endian form of Squirrel's part constant. Values in the literal and parameter sections are tagged objects:

| Tag | Payload |
| --- | --- |
| `0x08000010` | A string: `u32` length, then that many bytes, no terminator |
| Low byte `0x02` | An integer, `u32` |
| Low byte `0x04` | A float, 8 bytes |
| Low byte `0x08` | A boolean, `u32` |
| Low byte `0x01` | Null, no payload |

The seven counts are literals, parameters, outer values, local variables, line infos, instructions and nested functions. [Squirrel](https://www.squirrel-lang.org/) itself writes eight counts in its current release, because a default-parameter section was added after 2.1.2; the layout above is the one measured in these records, and the number of counts is what distinguishes the versions. Every record on Symphony has zero nested functions, so one scene is exactly one prototype.

## Instructions

An instruction is 8 bytes: a signed `arg1`, then four bytes `op`, `a0`, `a2`, `a3`. The encoding was not guessed from the data — it is what the interpreter does. In the inspected Symphony executable the dispatcher reads the opcode from byte 4 of the instruction the instruction pointer holds and advances the pointer by two 32-bit words per instruction, and the operand bytes it uses are `a0`, `a2` and `a3` while `arg1` comes from the leading word.

Only nine opcodes occur across the 600 inspected Symphony scenes, and all nine were read out of that dispatcher:

| Opcode | Count | What it does |
| --- | ---: | --- |
| `0x1f` | 600 | Opens the result array in `a0`; the first instruction of every scene, and its `arg1` is the array's capacity |
| `0x1e` | 291,087 | Opens a table in `a0`; `arg1` is the initial slot count |
| `0x3c` | 546,113 | Stores into the table held in `a1`: key from slot `a2`, value from slot `a3` |
| `0x20` | 291,087 | Appends the finished table held in `a1` to the result array |
| `0x01` | 38,965 | Slot `a0` = the literal numbered `arg1` |
| `0x02` | 24,163 | Slot `a0` = the integer `arg1` |
| `0x04` | 514,548 | Two loads at once: slot `a0` = literal `arg1`, slot `a2` = literal `a3` |
| `0x14` | 2 | Fills `arg1` slots with nulls from `a0` |
| `0x13` | 1,200 | Returns; the final one of every scene carries `a0 = 0xFF` |

The opcodes the scenes do not use — calls, jumps, comparisons, arithmetic — are not tabulated here; the interpreter has 61 cases and only these nine were read in full. The numbering is 2.1.2's own and does not match the current release's list, so a table copied from current Squirrel would be wrong.

## Structural checks

Four properties hold on all 600 Symphony records, and together they are strong enough to say the slicing is right rather than merely plausible:

- All 600 records parse to exactly one prototype with zero failures, 1,707,765 instructions in total.
- The first instruction of every scene is `0x1f`, and its `arg1` equals both the number of `0x1e` instructions and the number of `0x20` instructions in that scene.
- Every `0x1e` that declares capacity `N` is followed by exactly `N` `0x3c` stores before the next table is opened. That holds for all 291,087 tables and all 546,113 stores.
- No branch, jump or call opcode occurs anywhere, and every scene ends on `0x13` with `a0 = 0xFF`.

Because there is no control flow, simulation is exact rather than approximate: opening a table resets a line, each store appends `key=value` to it, and each append flushes it. The number of lines that comes out equals the number of `0x20` instructions, which is itself the number of `0x1e` instructions.

## The statement grammar

Rebuilding the tables gives the scene text back, one statement per line. The first lines of `bk1a_00` on Symphony:

```text
count=0 page=BK1A_00 label=*start line=0 tagname=label
edgecolor=0xEEEEEE color=0x000000 shadow=false tagname=deffont
left=0 namebaseleft=42 cursorxpos=598 visible=false top=312 marginl=40 marginb=0 namebase=main_name marginr=36 nametop=-20 transparent=true namewidth=172 namecenter=true frame=main_win nameleft=58 nameheight=24 cursorypos=92 margint=0 tagname=msgwin cursorimage=main_cursor namebasetop=-25
linespacing=6 tagname=defstyle
tagname=init
top=40 height=200 tagname=selopt
name=『サバイバルアイランド』 tagname=title
tagname=msgoff
opacity=0 noshift=true level=3 nocamera=true name=layblackbase file=flblack origin=1 tagname=newlay vorigin=1
```

Reading those tables gives the statement shape, and each rule below is observed rather than assumed:

- **One table is one statement.** A statement is a first token followed by attributes; the compiler stores the first token under the key `tagname` and emits it last.
- **A bare attribute is true.** `noshift`, `nocamera`, `nosync` and `transparent` appear as keys with the value `true`; `level=3` and `time=2500` appear as keys with a value.
- **Labels are statements too**, and the compiler adds bookkeeping to them: `count`, `page` and `line` travel with `label=*start`.
- **A character or place name can be the first token**, so `tagname` is not always a command. A table like `出=true 水着=true 呆れ=true ポーズＢ=true tagname=ルイズ 中=true` is an actor statement whose attributes are state flags, not a command with parameters.
- **Scenes chain by name.** `storage=BK1A_01.ks` together with `next` names the scene that follows.

That the source form is bracket tags — `[command attr=value]`, `*label`, `[storage]` — is inferred, not observed: no `.ks` file ships, and the compiler discards the punctuation. What the tables show is the vocabulary and the association, and the shipped Squirrel source in `SYSTEM` confirms that a statement's keys are offered one by one to a command table before the tag name itself is used as a fallback, which is why an unrecognised tag name is legal.

## Vocabulary

| | Symphony | Fantasy |
| --- | ---: | ---: |
| Records | 600 | 775 |
| Statements | 291,087 | 346,695 |
| Distinct tag names | 183 | 83 |
| Most common | `ch` 44,235 · `savepoint` 30,728 · `er` 25,065 · `msgon` 25,035 | `ch` 60,194 · `msgon` 33,260 · `dispname` 33,085 · `p` 33,085 |
| Choices | `select` 282 · `seladd` 846 | `select` 390 · `seladd` 1,165 |
| Scene jumps | `next` 303 · `goto` 589 | `next` 523 · `goto` 877 |

`ch` is the dialogue statement, and it is by far the most common: `text=サイ……。 tagname=ch`. `savepoint`, `msgon`, `msgoff`, `p` and `afterpage` are message-flow bookkeeping. The two builds differ in how finely they cut the vocabulary — Fantasy reaches the same statement kinds with fewer distinct tag names — but both use the same instruction set and the same container, which is one more piece of evidence that the three discs share this engine.

## Extracting the command lists

The script walks the index, decodes each block, undoes the interleave, parses the closure stream and simulates the nine opcodes. It writes one text file per record.

```quickbms
# zero-no-tsukaima-scene-cmds.bms
#
# Rebuilds the command list of every scene in a Soalo SCENE_ID container.
#
#   quickbms zero-no-tsukaima-scene-cmds.bms SCENE_ID.HD out/
#
# Input : a .HD index; the matching .BIN is opened from the same folder.
# Output: rec_NNNN.txt, one line per scene statement, keys in script order.
#
# Each record is a compressed, interleaved block, so the first half of this
# script is the same decode the scene-module extractor does: read the declared
# size and interleave factor, run the command codec, undo the interleave.
#
# The decoded record is a Squirrel closure stream (the game ships Squirrel
# 2.1.2) holding one function proto:
#
#   FA FA | "RIQS" | charsize | PART src name | PART counts[7]
#   PART literals | PART parameters | PART outervalues | PART localvars
#   PART lineinfos | PART instructions | PART functions | trailer | "LIAT"
#
# Objects are a u32 tag then a payload, dispatched on the low tag byte:
#   0x10 string  u32 length + bytes, no terminator
#   0x02 integer i32
#   0x04 float   8 bytes
#   0x08 boolean u32
#   0x01 null    no payload
#
# Instructions are 8 bytes: a signed arg1, then op, a0, a2, a3. Only nine
# opcodes occur in these scenes, and none of them branches:
#   0x01  slot[a0] = literals[arg1]
#   0x02  slot[a0] = arg1
#   0x04  slot[a0] = literals[arg1]; slot[a2] = literals[a3]
#   0x1e  open a table in slot[a0]
#   0x3c  table from slot[a1]: key from slot[a2], value from slot[a3]
#   0x20  append the finished table, closing the line
#   0x1f  open the result array (always the first instruction)
#   0x14  fill slots with nulls
#   0x13  return (always the last instruction, a0 = 0xFF)
# Because there is no control flow, a straight-line walk of the instruction
# array rebuilds the statements exactly.
#
# Measured with QuickBMS 0.12.0 on the three inspected discs:
#   Symphony (SLPS_258.98)   600 records, 291,087 statements, 68 s, 8.9 MB
#   Fantasy  (SLPS_258.30)   775 records, 346,695 statements, 86 s,  11 MB
#   Concerto (SLPS_257.08)  1920 records, none: its records hold source, not
#                           closures, so they produce empty files
# Output was checked byte for byte against an independent parser on three
# Symphony records.
#
# Text is Shift-JIS, kept as-is, so convert if needed:
#   iconv -f CP932 -t UTF-8 rec_0000.txt > rec_0000.utf8.txt

endian little

get HD_NAME basename
string BASE_NAME = HD_NAME
string BASE_NAME -= ".HD"
string BIN_NAME = BASE_NAME
string BIN_NAME += ".BIN"

open FDSE BIN_NAME 1

log MEMORY_FILE3 0 0
For GI = 0 < 1024
    put 0 byte MEMORY_FILE3
    math GI += 1
Next
log MEMORY_FILE5 0 0
For GI = 0 < 32768
    put 0 byte MEMORY_FILE5
    math GI += 1
Next

get HD_SIZE asize 0
math REC_COUNT = HD_SIZE
math REC_COUNT /= 4

set REC_START long 0
set MADE long 0
set SKIPPED long 0
set TRUNCATED long 0

For IDX = 0 < REC_COUNT
    math IOFF = IDX
    math IOFF *= 4
    goto IOFF 0
    get PACKED long 0

    math PAD = PACKED
    math PAD += 2047
    math PAD /= 2048
    math PAD *= 2048

    set DONE long 0

    if PACKED > 8
        goto REC_START 1
        get OUTLEN long 1
        get WORD long 1

        if OUTLEN > 0
            if OUTLEN <= 0x4000000
                if WORD < 1
                    math WORD = 1
                endif
                if WORD <= 64

                    math SEND = REC_START
                    math SEND += PAD

                    # --- command stream -------------------------------------
                    log MEMORY_FILE 0 0
                    math V0 = REC_START
                    math V0 += 8
                    set POS long 0

                    math H0 = 0x7FFFFF00
                    math H1 = 0x7FFFFF01
                    math H2 = 0x7FFFFFff
                    math H3 = 0x7FFFFF80
                    math H4 = 0x7FFFFF7f
                    math H5 = 0x7FFFFFfe

                    set KEEP long 1
                    For KEEP == 1
                        if POS >= OUTLEN
                            set KEEP long 0
                            break
                        endif
                        if V0 >= SEND
                            set KEEP long 0
                            break
                        endif

                        goto V0 1
                        get CMD byte 1
                        math BEF = V0
                        math LEN5 = CMD
                        math LEN5 &= 0x1F
                        math CLS = CMD
                        math CLS &= 0xE0

                        if CLS == 0xC0
                            math T = V0
                            math T += 1
                            goto T 1
                            get OPB byte 1
                            math N = LEN5
                            math N += 2
                            For R = 0 < N
                                put OPB byte MEMORY_FILE
                                math R += 1
                            Next
                            math POS += N
                            math V0 += 2
                            math H5 = H4
                            math H4 = H3
                            math H3 = H2
                            math H2 = H1
                            math H1 = H0
                            math H0 = BEF
                            set DONE long 1

                        elif CLS == 0xE0
                            math N = LEN5
                            math N += 1
                            math T = V0
                            math T += 1
                            goto T 1
                            For R = 0 < N
                                get OPB byte 1
                                put OPB byte MEMORY_FILE
                                math R += 1
                            Next
                            math POS += N
                            math V0 += 1
                            math V0 += N
                            math H5 = H4
                            math H4 = H3
                            math H3 = H2
                            math H2 = H1
                            math H1 = H0
                            math H0 = BEF
                            set DONE long 1

                        else
                            math M = CMD
                            math M >>= 5

                            math E = H0
                            if M == 1
                                math E = H1
                            elif M == 2
                                math E = H2
                            elif M == 3
                                math E = H3
                            elif M == 4
                                math E = H4
                            elif M == 5
                                math E = H5
                            endif

                            set SEED long 0
                            if E >= 0x70000000
                                set SEED long 1
                                math C2 = 0xDF
                                math OPB = E
                                math OPB &= 0xFF
                            else
                                goto E 1
                                get C2 byte 1
                            endif

                            math C2CLS = C2
                            math C2CLS &= 0xE0

                            if C2CLS == 0xC0
                                if SEED == 0
                                    math T = E
                                    math T += 1
                                    goto T 1
                                    get OPB byte 1
                                endif
                                math N = LEN5
                                math N += 2
                                For R = 0 < N
                                    put OPB byte MEMORY_FILE
                                    math R += 1
                                Next
                                math POS += N
                                set DONE long 1
                            elif C2CLS == 0xE0
                                math N = LEN5
                                math N &= 3
                                math N += 1
                                math T = LEN5
                                math T >>= 2
                                math T += 1
                                math T += E
                                goto T 1
                                For R = 0 < N
                                    get OPB byte 1
                                    put OPB byte MEMORY_FILE
                                    math R += 1
                                Next
                                math POS += N
                                set DONE long 1
                            endif

                            if M == 1
                                math H1 = H0
                                math H0 = E
                            elif M == 2
                                math H2 = H1
                                math H1 = H0
                                math H0 = E
                            elif M == 3
                                math H3 = H2
                                math H2 = H1
                                math H1 = H0
                                math H0 = E
                            elif M == 4
                                math H4 = H3
                                math H3 = H2
                                math H2 = H1
                                math H1 = H0
                                math H0 = E
                            elif M == 5
                                math H5 = H4
                                math H4 = H3
                                math H3 = H2
                                math H2 = H1
                                math H1 = H0
                                math H0 = E
                            endif

                            math V0 += 1
                        endif
                    Next

                    # --- de-interleave --------------------------------------
                    log MEMORY_FILE2 0 0
                    math ROW = OUTLEN
                    math ROW /= WORD
                    math BODY = ROW
                    math BODY *= WORD

                    For K = 0 < ROW
                        For M = 0 < WORD
                            math SRC = M
                            math SRC *= ROW
                            math SRC += K
                            goto SRC MEMORY_FILE
                            get OPB byte MEMORY_FILE
                            put OPB byte MEMORY_FILE2
                            math M += 1
                        Next
                        math K += 1
                    Next

                    if BODY < OUTLEN
                        math T = BODY
                        For I = T < OUTLEN
                            goto I MEMORY_FILE
                            get OPB byte MEMORY_FILE
                            put OPB byte MEMORY_FILE2
                            math I += 1
                        Next
                    endif

                    # --- closure stream -------------------------------------
                    # Layout of the de-interleaved record:
                    #   FA FA | "RIQS" | charsize | PART src name | PART counts[7]
                    #   PART literals | PART parameters | PART outervalues
                    #   PART localvars | PART lineinfos | PART instructions
                    #   PART functions | slack | "LIAT"
                    log MEMORY_FILE4 0 0
                    log MEMORY_FILE6 0 0

                    goto 0 MEMORY_FILE2
                    getdstring MAGIC 2 MEMORY_FILE2
                    get CHDR long MEMORY_FILE2
                    get CSIZE long MEMORY_FILE2

                    set OK long 0
                    if CHDR == 0x53514952
                        math OK = 1
                    endif

                    if OK == 1
                        get PART long MEMORY_FILE2

                        # source name
                        get OTAG long MEMORY_FILE2
                        math OL = OTAG
                        math OL &= 0xFF
                        if OL == 0x10
                            get OVL long MEMORY_FILE2
                            if OVL > 0
                                getdstring OVS OVL MEMORY_FILE2
                            endif
                        elif OL == 0x04
                            getdstring OVS 8 MEMORY_FILE2
                        elif OL != 0x01
                            get OVI long MEMORY_FILE2
                        endif

                        # proto name
                        get OTAG long MEMORY_FILE2
                        math OL = OTAG
                        math OL &= 0xFF
                        if OL == 0x10
                            get OVL long MEMORY_FILE2
                            if OVL > 0
                                getdstring OVS OVL MEMORY_FILE2
                            endif
                        elif OL == 0x04
                            getdstring OVS 8 MEMORY_FILE2
                        elif OL != 0x01
                            get OVI long MEMORY_FILE2
                        endif

                        get PART long MEMORY_FILE2
                        get NLIT long MEMORY_FILE2
                        get NPAR long MEMORY_FILE2
                        get NOUT long MEMORY_FILE2
                        get NLOC long MEMORY_FILE2
                        get NLINE long MEMORY_FILE2
                        get NINST long MEMORY_FILE2
                        get NFUNC long MEMORY_FILE2

                        # literals: strings go to a pool (MEMORY_FILE4), the index
                        # lives in MEMORY_FILE5 as 8 bytes per literal (offset, len)
                        get PART long MEMORY_FILE2
                        For LI = 0 < NLIT
                            get OTAG long MEMORY_FILE2
                            math OL = OTAG
                            math OL &= 0xFF
                            math IOFF = LI
                            math IOFF *= 8
                            goto IOFF MEMORY_FILE5
                            if OL == 0x10
                                get OVL long MEMORY_FILE2
                                get POFF asize MEMORY_FILE4
                                put POFF long MEMORY_FILE5
                                put OVL long MEMORY_FILE5
                                if OVL > 0
                                    getdstring OVS OVL MEMORY_FILE2
                                    putct OVS string -1 MEMORY_FILE4
                                endif
                            else
                                put 0 long MEMORY_FILE5
                                put 0 long MEMORY_FILE5
                                if OL == 0x04
                                    getdstring OVS 8 MEMORY_FILE2
                                elif OL != 0x01
                                    get OVI long MEMORY_FILE2
                                endif
                            endif
                            math LI += 1
                        Next

                        # parameters
                        get PART long MEMORY_FILE2
                        For PI = 0 < NPAR
                            get OTAG long MEMORY_FILE2
                            math OL = OTAG
                            math OL &= 0xFF
                            if OL == 0x10
                                get OVL long MEMORY_FILE2
                                if OVL > 0
                                    getdstring OVS OVL MEMORY_FILE2
                                endif
                            elif OL == 0x04
                                getdstring OVS 8 MEMORY_FILE2
                            elif OL != 0x01
                                get OVI long MEMORY_FILE2
                            endif
                            math PI += 1
                        Next

                        # outervalues: u32 type, then two objects
                        get PART long MEMORY_FILE2
                        For OI = 0 < NOUT
                            getdstring OVI 4 MEMORY_FILE2
                            For OJ = 0 < 2
                                get OTAG long MEMORY_FILE2
                                math OL = OTAG
                                math OL &= 0xFF
                                if OL == 0x10
                                    get OVL long MEMORY_FILE2
                                    if OVL > 0
                                        getdstring OVS OVL MEMORY_FILE2
                                    endif
                                elif OL == 0x04
                                    getdstring OVS 8 MEMORY_FILE2
                                elif OL != 0x01
                                    get OVI long MEMORY_FILE2
                                endif
                                math OJ += 1
                            Next
                            math OI += 1
                        Next

                        # localvarinfos: object, then 12 bytes
                        get PART long MEMORY_FILE2
                        For VI = 0 < NLOC
                            get OTAG long MEMORY_FILE2
                            math OL = OTAG
                            math OL &= 0xFF
                            if OL == 0x10
                                get OVL long MEMORY_FILE2
                                if OVL > 0
                                    getdstring OVS OVL MEMORY_FILE2
                                endif
                            elif OL == 0x04
                                getdstring OVS 8 MEMORY_FILE2
                            elif OL != 0x01
                                get OVI long MEMORY_FILE2
                            endif
                            getdstring OVI 12 MEMORY_FILE2
                            math VI += 1
                        Next

                        # line info: 8 bytes per entry
                        get PART long MEMORY_FILE2
                        math SKIPL = NLINE
                        math SKIPL *= 8
                        if SKIPL > 0
                            getdstring OVS SKIPL MEMORY_FILE2
                        endif

                        # instructions: 8 bytes each, arg1 then op, a0, a2, a3
                        get PART long MEMORY_FILE2
                        set LINE string ""
                        For II = 0 < NINST
                            get ARG1 long MEMORY_FILE2
                            get OP byte MEMORY_FILE2
                            get A0 byte MEMORY_FILE2
                            get A2 byte MEMORY_FILE2
                            get A3 byte MEMORY_FILE2

                            if OP == 0x13
                                break
                            elif OP == 0x1f
                                set LINE string ""
                            elif OP == 0x1e
                                set LINE string ""
                            elif OP == 0x02
                                math SOFF = A0
                                math SOFF *= 8
                                goto SOFF MEMORY_FILE3
                                put 2 long MEMORY_FILE3
                                put ARG1 long MEMORY_FILE3
                            elif OP == 0x03
                                math SOFF = A0
                                math SOFF *= 8
                                goto SOFF MEMORY_FILE3
                                put 2 long MEMORY_FILE3
                                put ARG1 long MEMORY_FILE3
                            elif OP == 0x01
                                math SOFF = A0
                                math SOFF *= 8
                                goto SOFF MEMORY_FILE3
                                put 1 long MEMORY_FILE3
                                put ARG1 long MEMORY_FILE3
                            elif OP == 0x04
                                math SOFF = A0
                                math SOFF *= 8
                                goto SOFF MEMORY_FILE3
                                put 1 long MEMORY_FILE3
                                put ARG1 long MEMORY_FILE3
                                math SOFF = A2
                                math SOFF *= 8
                                goto SOFF MEMORY_FILE3
                                put 1 long MEMORY_FILE3
                                put A3 long MEMORY_FILE3
                            elif OP == 0x3c
                                # key from slot A2
                                math SOFF = A2
                                math SOFF *= 8
                                goto SOFF MEMORY_FILE3
                                get KIND long MEMORY_FILE3
                                get SVAL long MEMORY_FILE3
                                if KIND == 1
                                    math LIO = SVAL
                                    math LIO *= 8
                                    goto LIO MEMORY_FILE5
                                    get POFF long MEMORY_FILE5
                                    get PLEN long MEMORY_FILE5
                                    if PLEN > 0
                                        goto POFF MEMORY_FILE4
                                        getdstring KEY PLEN MEMORY_FILE4
                                    else
                                        set KEY string ""
                                    endif
                                elif KIND == 2
                                    string KEY p= "%d" SVAL
                                else
                                    set KEY string "?"
                                endif
                                # value from slot A3
                                math SOFF = A3
                                math SOFF *= 8
                                goto SOFF MEMORY_FILE3
                                get KIND long MEMORY_FILE3
                                get SVAL long MEMORY_FILE3
                                if KIND == 1
                                    math LIO = SVAL
                                    math LIO *= 8
                                    goto LIO MEMORY_FILE5
                                    get POFF long MEMORY_FILE5
                                    get PLEN long MEMORY_FILE5
                                    if PLEN > 0
                                        goto POFF MEMORY_FILE4
                                        getdstring VAL PLEN MEMORY_FILE4
                                    else
                                        set VAL string ""
                                    endif
                                elif KIND == 2
                                    string VAL p= "%d" SVAL
                                else
                                    set VAL string "?"
                                endif
                                string LINE p= "%s%s=%s " LINE KEY VAL
                            elif OP == 0x20
                                string LINE p= "%s%c" LINE 10
                                putct LINE string -1 MEMORY_FILE6
                                set LINE string ""
                            endif
                            math II += 1
                        Next
                    endif

                    get OSZ asize MEMORY_FILE6
                    string OUT_TXT p= "rec_%04d.txt" IDX
                    log OUT_TXT 0 OSZ MEMORY_FILE6
                    math MADE += 1
                endif
            endif
        endif
    endif

    if DONE == 0
        math SKIPPED += 1
    endif

    math REC_START += PAD
Next IDX

string MSG p= "%d records written, %d skipped, %d short" MADE SKIPPED TRUNCATED
print "%MSG%"
```

Measured with QuickBMS 0.12.0 on the three inspected discs:

| Build | Records | Statements written | Time | Output |
| --- | ---: | ---: | ---: | ---: |
| Symphony | 600 | 291,087 | 68 s | 8.9 MB |
| Fantasy | 775 | 346,695 | 86 s | 11 MB |
| Concerto | 1,920 | none | 15 s | 68 KB of empty files |

Concerto's `SCENE_ID` records are Squirrel source rather than compiled closures, so the script finds no closure head and writes an empty file for each. That build needs no decoding at all: its scenes are text once the block is decoded, and the scene-module extractor on the [payload](payload.md#extracting-the-scene-modules) page already produces it.

The output is Shift-JIS, so convert it before reading:

```sh
iconv -f CP932 -t UTF-8 rec_0000.txt > rec_0000.utf8.txt
```

## Unknowns

- The six bytes between the last section and the stream tail. They carry a small number that differs per record, and nothing in the scenes reads them.
- What each bare flag on an actor statement means. The flags are the vocabulary of the shipped Squirrel classes, so the answer is in that source rather than in the bytecode.
- Why ten Symphony records rebuild to zero statements. Each is a prologue and an empty-array return: a valid scene with nothing in it, but whether those are stubs or genuinely empty scenes is not established.
- The 52 opcodes the scenes never use. They belong to the interpreter, not to what ships, and were not tabulated.

## Sources

- [Squirrel](https://www.squirrel-lang.org/) — the language and its reference manual, including the closure serialisation layout this page annotates.
- [Squirrel on Wikipedia](https://en.wikipedia.org/wiki/Squirrel_(programming_language)) — background and the fact that these titles are stated publicly to use it.
