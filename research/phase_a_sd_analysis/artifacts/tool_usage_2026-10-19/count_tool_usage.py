#!/usr/bin/env python3
"""How Claude Code sessions reach the firmware: bridge, versioned scripts or inline code.

Reads Claude Code transcripts (JSONL, main sessions and their subagents),
dedupes tool calls by tool_use id (a forked session repeats the prefix of its
parent; a shared call counts once, for the first file in sorted order),
keeps calls in [--since, --until), and classifies each call:

  bridge      a GhidraMCPd tool (mcp__zk-inkjet-ghidramcpd__*), run_script apart
  inline      a Bash call that runs Python from a heredoc, -c or stdin
  scratch     a Bash call that runs a .py file outside tools/scripts/
  versioned   a Bash call that runs tools/scripts/<x>.py, split into the
              register tools (truth.py, next.py, check_truth.py, ...) and the rest
  fw          inline or scratch code that reads firmware bytes (APP.bin,
              BOOT.bin, card images, .bin dumps); 'fw unversioned' = fw code
              that does not import a module from tools/scripts

Columns without _runs count Bash calls. scratch_runs and fw_runs* count runs:
one per inline body and one per scratch file a call starts (one call can run
an inline body and several scratch files). The figures quoted in the commits
of 2026-10-19 (201 scratch runs, 516 runs over firmware bytes, 461 of them
without a versioned import) are in this unit.

Classification is by regular expressions over the command text, so the counts
are close, not exact. Written for the count of 2026-10-19 (rule 11 in
CLAUDE.md); run it again later with the same options to compare.

    python3 research/phase_a_sd_analysis/artifacts/tool_usage_2026-10-19/count_tool_usage.py \\
        --since 2026-10-08 --until 2026-10-19T20:45 --exclude fa403293 \\
        --out research/phase_a_sd_analysis/artifacts/tool_usage_2026-10-19 \\
        ~/.claude/projects/<project transcript dir>*

Each positional argument is a transcript directory. Writes sessions.tsv and
daily.tsv to --out (only counts, session-id prefixes and model names; no
command text, paths or titles). Read-only on the transcripts.
"""
import argparse, collections, glob, json, os, re, sys

GH = 'mcp__zk-inkjet-ghidramcpd__'
REGISTER_TOOLS = {'truth.py', 'next.py', 'check_truth.py', 'truth_ansicht.py', 'card_map.py',
                  'truth_selbsttest.py', 'check_privat.py', 'check_privat_selbsttest.py',
                  'truth_mcp.py', 'truth_local.py'}

PY = r'\bpython3?(?:\.\d+)?\s+(?:-u\s+)?'
RE_INLINE = re.compile(PY + r'(?:-\s*(?:<<|"|\')|<<|-c\s|-\s*$|-\s+[^-])', re.M)
RE_HEREDOC_PY = re.compile(PY + r'-?\s*<<-?\s*[\'"]?(\w+)', re.M)
RE_EXEC_VERSIONED = re.compile(r'(?:' + PY + r'|(?:^|[\s;&|(])\./)\S*?tools/scripts/(?:[\w-]+/)*([\w-]+\.py)')
RE_PYFILE = re.compile(PY + r'([^\s\-<|;&][^\s|;&]*\.py)\b')
RE_HEREDOC_BODY = re.compile(PY + r'(?:-\s+)?(?:[^\n<|;&]*?\s)?-?\s*<<-?\s*([\'"]?)(\w+)\1[^\n]*\n(.*?)\n\s*\2\s*$',
                             re.S | re.M)
RE_DASH_C = re.compile(PY + r'-c\s+')
RE_CAT_PY = re.compile(r'cat\s+>\s*(\S+\.py)\s*<<-?\s*([\'"]?)(\w+)\2[^\n]*\n(.*?)\n\3\s*$', re.S | re.M)
FW = re.compile(r'APP\.bin|BOOT\.bin|firmware/bin|firmware/image|\.img\b|sd_?dump|card.*\.bin|_dump\.bin|'
                r'block\.bin|\.bin[\'"]')
VERS = re.compile(r'tools/scripts|import (neg_recheck|bridge_recheck|boot_listing|live_image|card_map|'
                  r'truth_local|app_disasm)\b|from (neg_recheck|bridge_recheck|boot_listing|live_image|'
                  r'app_disasm) import')


def bodies(cmd):
    """Python source run inline by a Bash command (heredoc bodies and -c strings)."""
    out = [m.group(3) for m in RE_HEREDOC_BODY.finditer(cmd)]
    for m in RE_DASH_C.finditer(cmd):
        rest = cmd[m.end():]
        if rest[:1] in ('"', "'"):
            q, i, buf = rest[0], 1, []
            while i < len(rest) and rest[i] != q:
                if q == '"' and rest[i] == '\\' and i + 1 < len(rest):
                    i += 1
                buf.append(rest[i])
                i += 1
            out.append(''.join(buf))
        elif rest:
            out.append(rest.split()[0])
    return out or [cmd]


def classify_bash(cmd, scratch_src):
    c = {}
    if RE_INLINE.search(cmd) or RE_HEREDOC_PY.search(cmd):
        c['inline'] = True
        body = '\n'.join(bodies(cmd))
        c['fw'] = bool(FW.search(body))
        c['imports_versioned'] = bool(VERS.search(body))
    ex = [m.group(1) for m in RE_EXEC_VERSIONED.finditer(cmd)]
    if any(s in REGISTER_TOOLS for s in ex):
        c['versioned_register'] = True
    if any(s not in REGISTER_TOOLS for s in ex):
        c['versioned_analysis'] = True
    others = [m.group(1) for m in RE_PYFILE.finditer(cmd) if 'tools/scripts/' not in m.group(1)]
    # per-run view: one record per inline body and per scratch file started
    runs = []
    if c.get('inline'):
        runs.append((c['fw'], c['imports_versioned']))
    if others:
        c['scratch'] = True
        for p in others:
            src = scratch_src.get(os.path.basename(p), '')
            runs.append((bool(FW.search(src)), bool(VERS.search(src))))
        src = '\n'.join(scratch_src.get(os.path.basename(p), '') for p in others)
        c['fw'] = c.get('fw') or bool(FW.search(src))
        c['imports_versioned'] = c.get('imports_versioned') or bool(VERS.search(src))
    c['scratch_runs'] = len(others)
    c['fw_runs'] = sum(1 for f, _ in runs if f)
    c['fw_runs_unversioned'] = sum(1 for f, v in runs if f and not v)
    return c


def result_text(block):
    cont = block.get('content')
    if isinstance(cont, list):
        return '\n'.join(x.get('text', '') for x in cont if isinstance(x, dict))
    return cont if isinstance(cont, str) else ''


def load(dirs, exclude):
    files = []
    for d in dirs:
        files += sorted(glob.glob(os.path.join(d, '*.jsonl')))
        files += sorted(glob.glob(os.path.join(d, '*', 'subagents', '*.jsonl')))
    calls, order = {}, []
    for f in files:
        parts = f.split(os.sep)
        sid = parts[-3] if parts[-2] == 'subagents' else parts[-1][:-6]
        if any(sid.startswith(x) for x in exclude):
            continue
        for line in open(f, encoding='utf-8'):
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if d.get('type') == 'assistant':
                m = d.get('message', {})
                for b in m.get('content') or []:
                    if b.get('type') == 'tool_use' and b['id'] not in calls:
                        calls[b['id']] = {'session': sid, 'ts': d.get('timestamp') or '',
                                          'model': m.get('model') or '', 'name': b['name'],
                                          'input': b.get('input') or {}}
                        order.append(b['id'])
            elif d.get('type') == 'user':
                cont = (d.get('message') or {}).get('content')
                for b in cont if isinstance(cont, list) else []:
                    if isinstance(b, dict) and b.get('type') == 'tool_result':
                        c = calls.get(b.get('tool_use_id'))
                        if c is not None and 'is_error' not in c:
                            c['is_error'] = bool(b.get('is_error'))
                            c['result'] = result_text(b)[:2000]
    return [calls[i] for i in order]


def bridge_failed(c):
    r = c.get('result', '')
    return c.get('is_error') or bool(re.search(r'"ok":\s*false|"timed_out":\s*true|"error":\s*"|'
                                               r'"state":\s*"LOADING"', r)) or not r.strip().startswith('{')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('dirs', nargs='+', help='transcript directories')
    ap.add_argument('--since', default='2026-10-08')
    ap.add_argument('--until', default='9999')
    ap.add_argument('--exclude', action='append', default=[], help='session-id prefix to skip')
    ap.add_argument('--out', help='directory for sessions.tsv and daily.tsv')
    a = ap.parse_args()

    allcalls = load(a.dirs, a.exclude)
    scratch_src = {}
    for c in allcalls:              # sources of scratch scripts, by file name
        if c['name'] == 'Write' and str(c['input'].get('file_path', '')).endswith('.py'):
            scratch_src[os.path.basename(c['input']['file_path'])] = c['input'].get('content', '')
        elif c['name'] == 'Bash':
            for m in RE_CAT_PY.finditer(c['input'].get('command', '')):
                scratch_src[os.path.basename(m.group(1).strip('\'"'))] = m.group(4)
    calls = [c for c in allcalls if a.since <= c['ts'] < a.until]

    keys = ['calls', 'bash', 'bridge', 'bridge_queries', 'bridge_failed', 'run_script', 'inline', 'scratch',
            'scratch_runs', 'fw', 'fw_unversioned', 'fw_runs', 'fw_runs_unversioned', 'versioned_analysis',
            'versioned_register', 'truth_mcp']
    per = collections.OrderedDict()
    day = collections.defaultdict(collections.Counter)
    for c in sorted(calls, key=lambda c: c['ts']):
        s = per.setdefault(c['session'], {'first': c['ts'][:10], 'models': collections.Counter(),
                                          'n': collections.Counter()})
        n, k = s['n'], {}
        if c['name'] == 'Bash':
            k = classify_bash(c['input'].get('command', ''), scratch_src)
            n['bash'] += 1
        elif c['name'] == GH + 'run_script':
            k = {'run_script': True}
        elif c['name'].startswith(GH):
            k = {'bridge': True}
            n['bridge_queries'] += len(c['input'].get('queries') or []) if c['name'] == GH + 'collect' else 1
        elif c['name'].startswith('mcp__zk-inkjet-truth__'):
            k = {'truth_mcp': True}
        if (k.get('bridge') or k.get('run_script')) and bridge_failed(c):
            n['bridge_failed'] += 1
        n['calls'] += 1
        for key in ('bridge', 'run_script', 'inline', 'scratch', 'fw', 'versioned_analysis',
                    'versioned_register', 'truth_mcp'):
            n[key] += bool(k.get(key))
        for key in ('scratch_runs', 'fw_runs', 'fw_runs_unversioned'):
            n[key] += k.get(key, 0)
        fw_unv = bool(k.get('fw') and not k.get('imports_versioned'))
        n['fw_unversioned'] += fw_unv
        if c['model'] and not c['model'].startswith('<'):
            s['models'][c['model'].replace('claude-', '')] += 1
        dd = day[c['ts'][:10]]
        dd['bridge'] += bool(k.get('bridge') or k.get('run_script'))
        dd['fw_unversioned'] += fw_unv
        dd['fw_runs_unversioned'] += k.get('fw_runs_unversioned', 0)
        dd['versioned_analysis'] += bool(k.get('versioned_analysis'))

    lines = ['\t'.join(['session', 'first_day', 'models'] + keys)]
    tot = collections.Counter()
    for sid, s in per.items():
        tot.update(s['n'])
        lines.append('\t'.join([sid[:8], s['first'], '/'.join(m for m, _ in s['models'].most_common())]
                               + [str(s['n'][k]) for k in keys]))
    lines.append('\t'.join(['TOTAL', '', ''] + [str(tot[k]) for k in keys]))
    dlines = ['day\tbridge_incl_run_script\tfw_unversioned\tfw_runs_unversioned\tversioned_analysis'] + \
             ['%s\t%d\t%d\t%d\t%d' % (d, v['bridge'], v['fw_unversioned'], v['fw_runs_unversioned'],
                                     v['versioned_analysis'])
              for d, v in sorted(day.items())]
    head = '# count_tool_usage.py --since %s --until %s, %d sessions, %d calls' % (a.since, a.until, len(per),
                                                                                 len(calls))
    print(head)
    print('\n'.join(lines))
    print()
    print('\n'.join(dlines))
    if a.out:
        for name, body in (('sessions.tsv', lines), ('daily.tsv', dlines)):
            with open(os.path.join(a.out, name), 'w', encoding='utf-8') as fh:
                fh.write(head + '\n' + '\n'.join(body) + '\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
