"""
Password Variation Toolkit (lab-safe)
- Modular mutation pipeline (leet, patterns, filters)
- Entropy & policy analyzer
- Safe local "lab" simulation against local SHA256-hash files (requires explicit --lab and --confirm)
- TUI skeleton (curses) to preview and adjust pipeline
- STYLECARD writer and README helper

Usage examples (CLI):
  python password_tool.py write-style                # writes STYLECARD.txt
  python password_tool.py gen KEYWORD --leet 2 --max-len 14 --preview 50 --out list.txt
  python password_tool.py analyze candidate.txt      # analyze each password's entropy & policy
  python password_tool.py lab-sim --hashes hashes.txt --candidates list.txt --lab --confirm
  python password_tool.py tui                         # interactive terminal UI (local)

Safety: This tool is explicitly for defensive/educational use in a lab. It DOES NOT perform network attacks.
"""

from __future__ import annotations
import argparse
import itertools
import random
import re
import sys
import os
import time
import hashlib
import logging
import math
from typing import List, Iterable, Set, Dict, Tuple

# Lightweight color fallback
try:
    from termcolor import colored
except Exception:
    def colored(s, _color=None):
        return s

# ---------------------- CONFIG / STYLECARD ----------------------
STYLECARD = '''STYLECARD v1
AESTHETIC: DOT-MATRIX / MONO / MINIMAL / PERFORATION / CARBON-COPY SHADOW / SCANLINE / GRID-INDEX
TONE: ALL-CAPS, DRY, PRECISE, INDUSTRIAL
TYPOGRAPHY: MONOSPACE ONLY, TIGHT LEADING, NO LIGATURES
LAYOUT: THIN RULES, 3x3 GRID THUMBS, PAGE XX/YY, RIGHT BOX UTC+DATE
DO: SHORT LABELS, ASCII DIVIDERS (\\\\ ★ ////////), COORDS AS 27.7676° N, 82.6403° W
DON'T: SERIF, COLOR NOISE, ROUNDED UI, MARKETING FLOOF
OUTPUT RULES: KEEP CAPS; 12PX~14PX; BREATHY MARGINS; TRIM ADJECTIVES
'''

README_SNIPPET = '''Password Variation Generator (lab-safe)

Purpose: generate keyword-based variations for password-strength testing and defensive wordlist creation.
Important: Use only on systems you own or are explicitly authorized to test. Unauthorized access is illegal.

Quick start:
  python -m pip install -r requirements.txt
  python password_tool.py gen KEYWORD --preview 50

See STYLECARD.txt for repo branding and visual guidelines.
'''

REQUIREMENTS = """termcolor>=1.1.0
"""

# ---------------------- LOGGER & SAFETY ----------------------
logging.basicConfig(filename='runs.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

def audit_log(msg: str):
    logging.info(msg)

# ---------------------- MUTATION PIPELINE ----------------------
leet_substitutions: Dict[str, List[str]] = {
    'a': ['@', '4'],
    'b': ['8'],
    'c': ['('],
    'e': ['3'],
    'g': ['9'],
    'i': ['1', '!'],
    'o': ['0'],
    's': ['$', '5'],
    't': ['7']
}

COMMON_PATTERNS = ['123', '2023', '!', '@', '#', 'admin', 'secure']


def generate_leetspeak_variations(word: str, level: int = 1, max_results: int = 2000) -> List[str]:
    """Generate controlled leet substitutions.
    level=0 -> none, level=1 -> single substitutions, level=2 -> pairs, level>=3 -> limited triples
    Caps: we include lower/upper/capitalized as base variations.
    """
    base = {word, word.lower(), word.upper(), word.capitalize()}
    w = word.lower()
    indices = [i for i, ch in enumerate(w) if ch in leet_substitutions]

    variations = set(base)
    if level >= 1:
        # single substitutions
        for i in indices:
            for sub in leet_substitutions[w[i]]:
                lst = list(w)
                lst[i] = sub
                variations.add(''.join(lst))
    if level >= 2:
        # pair substitutions
        for a, b in itertools.combinations(indices, 2):
            for sa in leet_substitutions[w[a]]:
                for sb in leet_substitutions[w[b]]:
                    lst = list(w)
                    lst[a] = sa
                    lst[b] = sb
                    variations.add(''.join(lst))
    if level >= 3:
        # limited triples (cap results)
        triples = list(itertools.combinations(indices, 3))[:50]
        for (a, b, c) in triples:
            for sa in leet_substitutions[w[a]][:1]:
                for sb in leet_substitutions[w[b]][:1]:
                    for sc in leet_substitutions[w[c]][:1]:
                        lst = list(w)
                        lst[a], lst[b], lst[c] = sa, sb, sc
                        variations.add(''.join(lst))

    results = sorted(variations)
    return results[:max_results]


def add_common_patterns(words: Iterable[str], patterns: List[str] = COMMON_PATTERNS) -> List[str]:
    result = set(words)
    for w in words:
        for p in patterns:
            result.add(f"{w}{p}")
            result.add(f"{p}{w}")
            result.add(f"{w}_{p}")
    return sorted(result)


def generate_common_passwords(keyword: str) -> List[str]:
    variations = [keyword, keyword.lower(), keyword.upper(), keyword.capitalize()]
    common_patterns = ['123', 'password', 'admin', 'user', 'secure', 'qwerty', 'letmein']
    out = set()
    for v in variations:
        for p in common_patterns:
            out.add(f"{v}{p}")
            out.add(f"{p}{v}")
    return sorted(out)


def filter_by_charset(words: Iterable[str], min_len: int = 4, max_len: int = 64, regex_allow: str = None) -> List[str]:
    out = []
    for w in words:
        if len(w) < min_len or len(w) > max_len:
            continue
        if regex_allow and not re.search(regex_allow, w):
            continue
        out.append(w)
    return out

# ---------------------- ENTROPY & POLICY ----------------------

def estimate_entropy_bits(password: str) -> float:
    """Rudimentary entropy estimate: log2(charset_size ** length) with deductions for dictionary substrings.
    This is simplistic but useful for teaching."""
    charset = 0
    if re.search(r'[a-z]', password):
        charset += 26
    if re.search(r'[A-Z]', password):
        charset += 26
    if re.search(r'[0-9]', password):
        charset += 10
    if re.search(r'[^A-Za-z0-9]', password):
        charset += 32
    if charset == 0:
        return 0.0
    bits = len(password) * math.log2(charset)
    # small heuristic penalty for common patterns
    if re.search(r'(123|password|qwerty|admin|letmein)', password.lower()):
        bits -= 10
    return max(bits, 0.0)


def policy_check(password: str, policy: Dict = None) -> Tuple[bool, List[str]]:
    # default policy
    if policy is None:
        policy = {
            'min_length': 8,
            'require_upper': True,
            'require_digit': True,
            'ban_substrings': ['password', '1234']
        }
    failures = []
    if len(password) < policy['min_length']:
        failures.append('too_short')
    if policy.get('require_upper') and not re.search(r'[A-Z]', password):
        failures.append('missing_upper')
    if policy.get('require_digit') and not re.search(r'[0-9]', password):
        failures.append('missing_digit')
    lower = password.lower()
    for b in policy.get('ban_substrings', []):
        if b in lower:
            failures.append(f'contains_{b}')
    return (len(failures) == 0, failures)

# ---------------------- LAB SIMULATION (SAFE) ----------------------

def load_local_sha256_hashes(path: str) -> Dict[str, str]:
    """Expect file with `username:hex_sha256` lines (simple lab format)."""
    out = {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or ':' not in line:
                continue
            user, hh = line.split(':', 1)
            out[user.strip()] = hh.strip().lower()
    return out


def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


def lab_simulate_match(hashes_path: str, candidates_path: str, max_checks: int = 100000) -> List[Tuple[str, str, str]]:
    """Compare candidate passwords hashed with SHA256 against local hashes. Returns hits list of (user, candidate, hash).
    This function is intentionally local-only and requires the operator to pass --lab and --confirm when invoking.
    """
    targets = load_local_sha256_hashes(hashes_path)
    candidates = []
    with open(candidates_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= max_checks:
                break
            candidates.append(line.strip())

    hits = []
    # simple loop: compute hash for each candidate and compare
    for cand in candidates:
        h = sha256_hex(cand)
        for user, th in targets.items():
            if h == th:
                hits.append((user, cand, h))
    return hits

# ---------------------- I/O HELPERS ----------------------

def write_list(words: Iterable[str], path: str):
    with open(path, 'w', encoding='utf-8') as f:
        for w in words:
            f.write(w + '\n')

# ---------------------- TUI SKELETON (curses) ----------------------

def run_tui():
    try:
        import curses
    except Exception:
        print(colored('curses not available on this platform (Windows?). TUI requires a Unix-like terminal.', 'red'))
        return

    def tui_main(stdscr):
        curses.curs_set(0)
        leet_level = 1
        preview_count = 50
        keyword = 'password'
        while True:
            stdscr.clear()
            h, w = stdscr.getmaxyx()
            header = 'PASSWORD TOOL — TUI (LAB MODE)'
            stdscr.addstr(0, 0, header.upper())
            stdscr.addstr(1, 0, '-' * min(w, 80))
            stdscr.addstr(3, 0, f'Keyword: {keyword}  |  Leet level: {leet_level}  |  Preview: {preview_count}')
            stdscr.addstr(5, 0, 'Commands: (g)enerate  (l)evel+  (k)eyword  (p)review++  (q)uit')
            stdscr.refresh()
            c = stdscr.getch()
            if c in (ord('q'), 27):
                break
            if c == ord('l'):
                leet_level = min(3, leet_level + 1)
            if c == ord('g'):
                # generate and show top preview
                gens = generate_leetspeak_variations(keyword, level=leet_level, max_results=preview_count)
                stdscr.clear()
                stdscr.addstr(0, 0, 'PREVIEW — top candidates')
                for i, g in enumerate(gens[:preview_count]):
                    stdscr.addstr(2 + i, 0, g[:w-1])
                stdscr.addstr(h-1, 0, 'Press any key to return')
                stdscr.getch()
            if c == ord('k'):
                curses.echo()
                stdscr.addstr(7, 0, 'Enter keyword: ')
                kw = stdscr.getstr(7, 15, 40).decode('utf-8')
                if kw:
                    keyword = kw
                curses.noecho()
            if c == ord('p'):
                preview_count = min(500, preview_count + 50)

    import curses
    curses.wrapper(tui_main)

# ---------------------- CLI ----------------------

def cmd_write_style(args):
    with open('STYLECARD.txt', 'w', encoding='utf-8') as f:
        f.write(STYLECARD)
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(README_SNIPPET)
    with open('requirements.txt', 'w', encoding='utf-8') as f:
        f.write(REQUIREMENTS)
    print(colored('Wrote STYLECARD.txt, README.md, requirements.txt', 'green'))
    audit_log('STYLECARD and README written')


def cmd_gen(args):
    keyword = args.keyword
    leet_level = args.leet
    max_len = args.max_len
    preview = args.preview
    outfile = args.outfile

    audit_log(f'gen called: keyword={keyword} leet={leet_level} max_len={max_len} preview={preview} out={outfile}')

    base = generate_common_passwords(keyword)
    leet = generate_leetspeak_variations(keyword, level=leet_level)
    combined = base + leet
    patterned = add_common_patterns(combined)
    filtered = filter_by_charset(patterned, min_len=1, max_len=max_len)
    # lightweight enhancement
    final = []
    for w in filtered:
        final.append(w)
    final = sorted(set(final))

    if preview:
        print(colored(f'Top {preview} candidates:', 'cyan'))
        for p in final[:preview]:
            print(p)
    if outfile:
        write_list(final, outfile)
        print(colored(f'Wrote {len(final)} candidates to {outfile}', 'yellow'))
    audit_log(f'Generated {len(final)} candidates')


def cmd_analyze(args):
    path = args.path
    if not os.path.exists(path):
        print(colored('Candidates file not found', 'red'))
        return
    print(colored('password,entropy_bits,policy_ok,failures', 'cyan'))
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            pw = line.strip()
            bits = estimate_entropy_bits(pw)
            ok, failures = policy_check(pw)
            print(f'{pw},{bits:.1f},{ok},{";".join(failures)}')


def cmd_lab_sim(args):
    if not args.lab or not args.confirm:
        print(colored('Lab simulation requires --lab and --confirm flags to run. This prevents accidental use.', 'red'))
        return
    hashes = args.hashes
    candidates = args.candidates
    if not os.path.exists(hashes) or not os.path.exists(candidates):
        print(colored('Hashes or candidates file missing', 'red'))
        return
    audit_log(f'Lab sim started: hashes={hashes} candidates={candidates}')
    hits = lab_simulate_match(hashes, candidates)
    if not hits:
        print(colored('No hits found in local simulation.', 'yellow'))
    else:
        print(colored('HITS:', 'red'))
        for user, cand, h in hits:
            print(f'{user}:{cand}:{h}')
    audit_log(f'Lab sim finished, hits={len(hits)}')


def main():
    p = argparse.ArgumentParser(prog='password_tool')
    sub = p.add_subparsers(dest='cmd')

    w = sub.add_parser('write-style')
    w.set_defaults(func=cmd_write_style)

    g = sub.add_parser('gen')
    g.add_argument('keyword')
    g.add_argument('--leet', type=int, default=1, help='leet level 0-3')
    g.add_argument('--max-len', type=int, default=32)
    g.add_argument('--preview', type=int, default=20)
    g.add_argument('--outfile', type=str, default='generated_passwords.txt')
    g.set_defaults(func=cmd_gen)

    a = sub.add_parser('analyze')
    a.add_argument('path')
    a.set_defaults(func=cmd_analyze)

    l = sub.add_parser('lab-sim')
    l.add_argument('--hashes', required=True, help='local hashes file (user:sha256hex per line)')
    l.add_argument('--candidates', required=True)
    l.add_argument('--lab', action='store_true', help='explicit lab mode')
    l.add_argument('--confirm', action='store_true', help='confirm operator intent')
    l.set_defaults(func=cmd_lab_sim)

    t = sub.add_parser('tui')
    t.set_defaults(func=lambda args: run_tui())

    args = p.parse_args()
    if not args.cmd:
        p.print_help()
        return
    args.func(args)

if __name__ == '__main__':
    main()
