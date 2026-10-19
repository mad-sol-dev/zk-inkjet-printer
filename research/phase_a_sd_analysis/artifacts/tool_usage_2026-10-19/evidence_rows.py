#!/usr/bin/env python3
"""What the evidence of recent O2/O3 rows names, judged by the validator's own test.

For every living row with Oracle O2 or O3 and Updated >= --since, runs
check_truth.beleg_pruefen (rule 11 in CLAUDE.md) over Evidence_E0 and reports
whether it names a repeatable call, a scratchpad script, a computation in
words, or a script missing from the repository. check_truth.py enforces this
only for O2 rows changed from BELEG_AB on; this listing shows the state before
that date. Run from the repository root:

    python3 research/phase_a_sd_analysis/artifacts/tool_usage_2026-10-19/evidence_rows.py \\
        --since 2026-10-15 --out research/phase_a_sd_analysis/artifacts/tool_usage_2026-10-19

Writes rows.tsv to --out. Read-only on TRUTH.csv.
"""
import argparse, csv, os, sys

sys.path.insert(0, 'tools/scripts')
import check_truth as ct  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--since', default='2026-10-15')
    ap.add_argument('--out')
    a = ap.parse_args()
    rows = list(csv.DictReader(open(ct.P, encoding='utf-8')))
    out = ['claim\toracle\tupdated\tcall\tscratch\tprose\tmissing_script']
    n = {'rows': 0, 'no_call': 0, 'scratch': 0, 'prose': 0, 'missing': 0}
    for r in rows:
        e = (r.get('Evidence_E0') or '').strip()
        if r['Superseded_By'] or r.get('Oracle') not in ('O2', 'O3') or r.get('Updated', '') < a.since:
            continue
        if e in ('', '0'):
            call, scratch, prose, missing = False, [], False, []
        else:
            call, scratch, prose, missing = ct.beleg_pruefen(e)
        n['rows'] += 1
        n['no_call'] += not call
        n['scratch'] += bool(scratch)
        n['prose'] += prose
        n['missing'] += bool(missing)
        out.append('\t'.join([r['Claim_ID'], r['Oracle'], r['Updated'], 'yes' if call else 'NO',
                              ' '.join(os.path.basename(x) for x in scratch), 'yes' if prose else '',
                              ' '.join(missing)]))
    head = ('# evidence_rows.py --since %s: %d living O2/O3 rows, %d without a repeatable call, '
            '%d with a scratchpad script, %d with a computation in words, %d naming a missing script'
            % (a.since, n['rows'], n['no_call'], n['scratch'], n['prose'], n['missing']))
    print(head)
    print('\n'.join(out))
    if a.out:
        with open(os.path.join(a.out, 'rows.tsv'), 'w', encoding='utf-8') as fh:
            fh.write(head + '\n' + '\n'.join(out) + '\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
