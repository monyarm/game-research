#!/usr/bin/env python3
"""Assemble the committed CSV tables for the VN engine corpus note.

Reads the raw tokei bucket output in /tmp/opencode/vn-corpus/data and writes
docs/data/vn-corpus/*.csv in the game-research repo.  Run from that repo.

    python3 tools/vn-corpus/make-tables.py <raw-data-dir>
"""
import csv
import os
import sys

RAW = sys.argv[1] if len(sys.argv) > 1 else "/tmp/opencode/vn-corpus/data"
OUT = "docs/data/vn-corpus"

# project key -> (display name, url, licence, commit, engine target, kind)
META = {
    "persona4-decomp": ("Persona 4 decompilation", "https://github.com/Raikaru/Persona4-Decompilation", "none", "3a28140", "Atlus SMT/Persona (PS2)", "matching decomp"),
    "persona3fes-decomp": ("Persona 3 FES decompilation", "https://github.com/Raikaru/Persona3-FES-Decompilation", "CC0-1.0", "81da989", "Atlus SMT/Persona (PS2)", "matching decomp"),
    "hotel-dusk-decomp": ("Hotel Dusk decompilation", "https://github.com/usename00/hotel-dusk-decomp", "none", "dcd74d8", "Cing (DS)", "matching decomp"),
    "pwaa1": ("Ace Attorney decompilation", "https://github.com/atasro2/pwaa1", "none", "744219a", "Capcom AA (GBA)", "matching decomp"),
    "pwaa2": ("Ace Attorney 2 decompilation", "https://github.com/atasro2/pwaa2", "none", "91cd5f6", "Capcom AA (GBA)", "matching decomp"),
    "ai5-sdl2": ("ai5-sdl2", "https://github.com/b-stack/ai5-sdl2", "GPL-3.0", "ad7a703", "Elf ai5 (PC-98/Win)", "reimplementation"),
    "libai5": ("libai5", "https://github.com/b-stack/libai5", "GPL-3.0", "779913d", "Elf ai5 (PC-98/Win)", "reimplementation"),
    "onscripter": ("ONScripter", "https://github.com/onscripter/onscripter", "GPL-2.0", "848a608", "NScripter", "reimplementation"),
    "vilevn": ("VileVN", "https://sourceforge.net/p/vilevn/", "GPL-3.0", "f6e48d6", "TLove / GSS", "released source"),
    "krkrz": ("KiriKiri Z", "https://github.com/krkrz/krkrz", "BSD-3-Clause (W.Dee)", "fd5c4ba", "KiriKiri", "released source"),
    "krkrsdl2": ("KiriKiri SDL2 port", "https://github.com/krkrz/krkrsdl2", "MIT", "8cea182", "KiriKiri", "port of released source"),
    "rlvm": ("rlvm", "https://github.com/eglaysher/rlvm", "GPL-3.0", "e38cda7", "RealLive", "reimplementation"),
    "xsystem35": ("xsystem35-sdl2", "https://github.com/kichikuou/xsystem35-sdl2", "GPL-2.0", "4cabebf", "AliceSoft System 3.x", "reimplementation"),
    "xsystem4": ("xsystem4", "https://github.com/nunuhara/xsystem4", "GPL-2.0", "d3f93bc", "AliceSoft System 4", "reimplementation"),
    "openbgi": ("OpenBGI", "https://github.com/uyjulian/openbgi", "GPL-2.0", "e6e9e24", "BGI/Ethornell", "reimplementation"),
    "libnpengine": ("libnpengine", "https://github.com/TriggerRokko/libnpengine", "LGPL-3.0", "da1a175", "Nitroplus", "reimplementation"),
    "impacto": ("Impacto", "https://github.com/CommitteeOfZero/impacto", "ISC", "ad20204", "MAGES./5pb.", "reimplementation"),
    "xlvns": ("Xuse engine sources", "(no public repository)", "none", "7a4bc8f", "Xuse XLVNS", "released source"),
    "siglus_rs": ("siglus-rs", "https://github.com/Lulzx/siglus-rs", "MPL-2.0", "88f9cee", "Siglus / RealLive / UK2 / AVG32", "reimplementation"),
    "cmvs-rs": ("cmvs-rs", "https://github.com/astudyinyellow/cmvs-rs", "Apache-2.0 OR MIT", "af64920", "CMVS", "reimplementation"),
    "shiinario_rs": ("shiinario-rs", "https://github.com/kiKiRei/ShiinaRio", "MIT", "3e560c6", "ShiinaRio", "reimplementation"),
    "DISTRUST": ("Danganronpa decompilation", "https://github.com/Pucas01/DISTRUST", "CC0-1.0", "5526cd4", "Spike Chunsoft Danganronpa (PSP)", "matching decomp"),
    "dds-decomp": ("Digital Devil Saga decompilation", "https://github.com/Megami-Decomps/dds-decomp", "none", "e714912", "Atlus SMT (PS2)", "matching decomp"),
    "smt3-decomp": ("Shin Megami Tensei III decompilation", "https://github.com/Megami-Decomps/smt3-decomp", "none", "08ecf20", "Atlus SMT (PS2)", "matching decomp"),
    "persona-psx": ("Persona decompilation (PS1)", "https://github.com/daanhenke/persona-psx", "none", "dfd1cd4", "Atlus Persona (PS1)", "matching decomp"),
    "smt1dasm": ("Shin Megami Tensei disassembly", "https://github.com/spannerisms/smt1dasm", "GPL-3.0", "6d950c0", "Atlus SMT (SFC)", "disassembly"),
    "tokimemo-ps1-decomp": ("Tokimeki Memorial decompilation", "https://github.com/CosmicScribe64/tokimemo-ps1-decomp", "CC0-1.0", "3c60705", "Konami Tokimeki Memorial (PS1)", "matching decomp"),
    "ghost-trick-vita": ("Ghost Trick decompilation", "https://github.com/liambsulliva/ghost-trick-vita", "none", "1b614d0", "Cing (DS)", "matching decomp"),
    "ethornell-rs": ("ethornell-rs", "https://github.com/xmoezzz/ethornell-rs", "MPL-2.0", "0b870c3", "BGI/Ethornell", "reimplementation"),
    "ikuradroid": ("ikuradroid", "https://github.com/VienDesuPorting/ikuradroid", "GPL-3.0", "2dbde94", "Ikura / VileVN port", "port of released source"),
    "krkr2": ("KiriKiri 2", "https://github.com/krkrz/krkr2", "GPL-2.0", "dec49af", "KiriKiri", "released source"),
}

COLS = ["project", "target", "kind", "licence", "commit", "url",
        "engine", "boilerplate", "middleware", "sdk_crt", "thirdparty",
        "data", "tooling", "decompiled", "asm", "note"]

NOTES = {
    "persona4-decomp": "engine share 65% of its own decomp",
    "persona3fes-decomp": "engine share 72%",
    "tokimemo-ps1-decomp": "drafts/ holds 4.28M mechanically generated C lines, excluded from engine",
    "krkr2": "trunk/ only; vendor/ and the branches/tags SVN copies excluded",
    "smt1dasm": "pure assembly listing",
}


def read_buckets(key):
    path = os.path.join(RAW, "loc-%s.csv" % key)
    out = {}
    if not os.path.exists(path):
        return out
    with open(path) as fh:
        for row in csv.DictReader(fh):
            b = row["bucket"]
            kind = row["kind"]
            n = int(row["code"])
            if kind == "asm":
                out["asm"] = out.get("asm", 0) + n
            else:
                out[b] = out.get(b, 0) + n
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for key, (name, url, lic, commit, target, kind) in META.items():
        b = read_buckets(key)
        rows.append({
            "project": name,
            "target": target,
            "kind": kind,
            "licence": lic,
            "commit": commit,
            "url": url,
            "engine": b.get("engine", 0),
            "boilerplate": b.get("boilerplate", 0),
            "middleware": b.get("middleware", 0),
            "sdk_crt": b.get("sdk", 0),
            "thirdparty": b.get("thirdparty", 0),
            "data": b.get("data", 0),
            "tooling": b.get("tooling", 0),
            "decompiled": b.get("decompiled", 0),
            "asm": b.get("asm", 0),
            "note": NOTES.get(key, ""),
        })
    rows.sort(key=lambda r: -r["engine"])
    with open(os.path.join(OUT, "source-loc.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    # executable side, straight copy of the raw measurements
    for src, dst in (("exe-ps2-win.csv", "executables-ps2-win.csv"),
                     ("exe-ps2-remote.csv", "executables-ps2-remote.csv"),
                     ("exe-psp.csv", "executables-psp.csv")):
        p = os.path.join(RAW, src)
        if os.path.exists(p):
            with open(p) as fh, open(os.path.join(OUT, dst), "w") as out:
                out.write(fh.read())
    print("wrote", OUT, len(rows), "source rows")


if __name__ == "__main__":
    main()
