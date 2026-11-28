#!/usr/bin/env python3
"""Bucket a repo's LOC into engine logic / boilerplate / middleware / third-party.

Usage: bucket.py REPO_DIR RULES_JSON OUT_CSV

RULES_JSON shape:
  {
    "repo": "name",
    "buckets": [ ["glob/prefix", "bucket"], ... ],   # longest match wins
    "default": "engine"
  }
Matching: the pattern is checked against the repo-relative path. A pattern
ending in "/" is a directory prefix. Otherwise fnmatch glob on the path.
"""
import json, os, re, subprocess, sys, fnmatch

TOKEI = os.environ.get('TOKEI', 'tokei')

CODE_EXTS = {'.c', '.cc', '.cpp', '.cxx', '.h', '.hh', '.hpp', '.hxx', '.m', '.mm',
             '.s', '.S', '.asm', '.cs', '.java', '.js', '.ts', '.py', '.nut', '.lua'}

def tokei(repo):
    out = subprocess.run([TOKEI,
                          '--output', 'json', '--hidden', '-e', '.git', repo],
                         capture_output=True, text=True)
    if out.returncode != 0:
        sys.stderr.write(out.stderr)
        raise SystemExit(1)
    return json.loads(out.stdout)

def lang_of(path):
    return os.path.splitext(path)[1]

def is_asm(path):
    e = lang_of(path)
    return e in ('.s', '.S', '.asm')

def bucket_for(rel, rules):
    best, best_len = rules.get('default', 'engine'), -1
    for pat, b in rules['buckets']:
        if pat.endswith('/'):
            hit = rel == pat[:-1] or rel.startswith(pat)
            ln = len(pat)
        else:
            hit = fnmatch.fnmatch(rel, pat)
            ln = len(pat)
        if hit and ln > best_len:
            best, best_len = b, ln
    return best

def table_ratio(path):
    """Fraction of 'code' lines that look like pure data table rows."""
    try:
        with open(path, 'rb') as f:
            txt = f.read(400000).decode('utf-8', 'replace')
    except OSError:
        return 0.0
    pat = re.compile(r'^\s*(0x[0-9A-Fa-f]+|\d+|"[^"]*"|\'[^\']*\')\s*,?\s*$')
    n = hit = 0
    for line in txt.splitlines():
        s = line.strip()
        if not s or s.startswith(('//', '/*', '*', '#')):
            continue
        n += 1
        if pat.match(line):
            hit += 1
    return hit / n if n > 32 else 0.0


def main():
    repo, rules_path, out_csv = sys.argv[1], sys.argv[2], sys.argv[3]
    rules = json.load(open(rules_path))
    data = tokei(repo)
    rows = []
    for lang, ldata in data.items():
        for r in ldata.get('reports', []):
            name = r['name']
            if name.startswith(repo):
                rel = os.path.relpath(name, repo)
            else:
                rel = name
            st = r['stats']
            rows.append((name, rel, lang, st['code'], st['blanks'],
                         st['comments'], st['code'] + st['comments'] + st['blanks']))
    agg = {}
    datafiles = []
    for name, rel, lang, code, blanks, comments, lines in rows:
        b = bucket_for(rel, rules)
        if b in ('engine', 'boilerplate') and code >= 200 and lang in ('C', 'C++', 'C Header'):
            if table_ratio(name) >= 0.6:
                b = 'data'
                datafiles.append((code, rel))
        kind = 'asm' if is_asm(rel) else 'src'
        k = (b, kind)
        a = agg.setdefault(k, {'files': 0, 'code': 0, 'blanks': 0, 'comments': 0, 'lines': 0, 'langs': {}})
        a['files'] += 1
        a['code'] += code
        a['blanks'] += blanks
        a['comments'] += comments
        a['lines'] += lines
        a['langs'][lang] = a['langs'].get(lang, 0) + code
    with open(out_csv, 'w') as f:
        f.write('repo,bucket,kind,files,code,comments,blanks,lines,top_langs\n')
        for (b, kind), a in sorted(agg.items()):
            langs = ';'.join(f'{k}:{v}' for k, v in sorted(a['langs'].items(), key=lambda x: -x[1])[:6])
            f.write(f"{rules.get('repo', os.path.basename(repo.rstrip('/')))},{b},{kind},{a['files']},{a['code']},{a['comments']},{a['blanks']},{a['lines']},\"{langs}\"\n")
    # console summary
    tot = {}
    for (b, kind), a in agg.items():
        tot[(b, kind)] = tot.get((b, kind), 0) + a['code']
    print(f"== {rules.get('repo')}")
    for k in sorted(tot):
        print(f'  {k[0]:<14} {k[1]:<4} {tot[k]:>9,}')
    if datafiles:
        print('  -- data-detected:', ', '.join(f'{p} ({c:,})' for c, p in sorted(datafiles, reverse=True)[:8]))

if __name__ == '__main__':
    main()
