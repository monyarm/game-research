#!/usr/bin/env python3
"""Print LOC per top-level (and src/ sub) directory for a repo, from tokei JSON."""
import json, os, subprocess, sys, collections

TOKEI = os.environ.get('TOKEI', 'tokei')

repo = sys.argv[1]
depth = int(sys.argv[2]) if len(sys.argv) > 2 else 2
minloc = int(sys.argv[3]) if len(sys.argv) > 3 else 300
out = subprocess.run([TOKEI, '--output', 'json',
                      '--hidden', '-e', '.git', '-e', '*.sf2', '-e', '*.ttf', repo],
                     capture_output=True, text=True)
data = json.loads(out.stdout)
agg = collections.Counter()
tot = collections.Counter()
for lang, ldata in data.items():
    for r in ldata.get('reports', []):
        rel = os.path.relpath(r['name'], repo)
        parts = rel.split(os.sep)
        key = os.sep.join(parts[:depth]) if len(parts) > depth else (os.sep.join(parts[:-1]) or '.')
        agg[key] += r['stats']['code']
        tot[lang] += r['stats']['code']
print(f'== {repo}')
for k, v in sorted(agg.items(), key=lambda x: -x[1]):
    if v >= minloc:
        print(f'{v:>9,}  {k}')
print('-- by language:', ', '.join(f'{k}={v:,}' for k, v in tot.most_common(8)))
print(f'-- total {sum(tot.values()):,}')
