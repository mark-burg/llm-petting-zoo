#!/usr/bin/env python3
"""
Reads promptfoo output.json and writes a Markdown results summary to stdout.

Usage:
  python3 scripts/generate-summary.py output.json >> "$GITHUB_STEP_SUMMARY"
"""

import json
import sys


def get_desc(r):
    """Return a short display description for a result row."""
    return (
        (r.get('testCase') or {}).get('description')
        or str((r.get('vars') or {}).get('input', ''))[:60]
        or '-'
    )


def get_provider(r, fallback='unknown'):
    return r.get('provider', {}).get('label') or r.get('provider', {}).get('id') or fallback


def main():
    if len(sys.argv) < 2:
        print('Usage: generate-summary.py <output.json>', file=sys.stderr)
        sys.exit(1)

    try:
        with open(sys.argv[1]) as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f'Error: file not found: {sys.argv[1]}', file=sys.stderr)
        sys.exit(1)

    raw = data.get('results', {})
    results = raw.get('results', raw) if isinstance(raw, dict) else raw

    # --- Overall stats ---
    total = len(results)
    passed = sum(1 for r in results if r.get('success'))
    failed = total - passed
    pass_rate = f'{(passed / total * 100):.1f}' if total else '0.0'
    status_icon = ':white_check_mark:' if failed == 0 else ':x:'

    lines = [
        f'## {status_icon} Evaluation Results',
        '',
        f'**{passed}/{total}** tests passed ({pass_rate}%)',
        '',
    ]

    # --- Per-provider summary ---
    by_provider = {}
    for r in results:
        provider = get_provider(r)
        counts = by_provider.setdefault(provider, {'passed': 0, 'failed': 0})
        if r.get('success'):
            counts['passed'] += 1
        else:
            counts['failed'] += 1

    lines += [
        '### Provider Summary',
        '',
        '| Provider | Passed | Failed | Rate |',
        '|----------|-------:|-------:|-----:|',
    ]
    for provider, counts in by_provider.items():
        prov_total = counts['passed'] + counts['failed']
        rate = f'{(counts["passed"] / prov_total * 100):.1f}'
        lines.append(f'| {provider} | {counts["passed"]} | {counts["failed"]} | {rate}% |')
    lines.append('')

    # --- Detailed results table (one row per test, one column per provider) ---
    # Collect providers in first-appearance order.
    providers = list(dict.fromkeys(get_provider(r) for r in results))

    # Group results by test description, keyed by provider.
    by_test = {}
    for r in results:
        desc = get_desc(r)
        by_test.setdefault(desc, {})[get_provider(r)] = r

    provider_headers = ' | '.join(f'{p} Result' for p in providers)
    provider_sep = ' | '.join(':----:' for _ in providers)
    lines += [
        '### Detailed Results',
        '',
        f'| Test | {provider_headers} |',
        f'|------|{provider_sep}|',
    ]
    for desc, by_prov in by_test.items():
        cells = []
        for p in providers:
            r = by_prov.get(p)
            if r is None:
                cells.append(':next_track_button:')
            else:
                cells.append(':white_check_mark:' if r.get('success') else ':x:')
        lines.append(f'| {desc} | {" | ".join(cells)} |')
    lines.append('')

    # --- Failed assertion details ---
    failures = [r for r in results if not r.get('success')]
    if failures:
        lines += ['<details>', '<summary>Failed test details</summary>', '']
        for r in failures:
            lines += [f'#### {get_desc(r)} ({get_provider(r, "-")})', '']
            components = (r.get('gradingResult') or {}).get('componentResults', [])
            for c in components:
                if not c.get('pass'):
                    assertion = c.get('assertion') or {}
                    metric = assertion.get('metric') or assertion.get('type') or 'assertion'
                    lines.append(f'- **{metric}**: {c.get("reason") or "failed"}')
            lines.append('')
        lines += ['</details>', '']

    print('\n'.join(lines))


if __name__ == '__main__':
    main()
