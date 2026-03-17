#!/usr/bin/env python3
"""
Generate a runtime promptfoo config by patching tests, providers, and scenarios.

Reads promptfooconfig.yaml, replaces the three selection keys based on
environment variables, and writes promptfooconfig-run.yaml.

Environment variables:
  TESTS_INPUT      Comma-separated test names.
                   Options: knowledge, reasoning, robustness, safety,
                            structured-output, suggestibility
  PROVIDERS_INPUT  Comma-separated provider keys.
                   Options: gpt-4.1-mini, meta-llama-3.1-8b,
                            claude-3.5-haiku, gpt-4o
  SCENARIOS_INPUT  Comma-separated scenario names.
                   Options: multi-language
  SUITE_INPUT      Optional metadata suite tag to filter test cases by
                   (e.g. smoke). Empty or unset means run all test cases.
"""

import os
import sys
import yaml

KNOWN_TESTS = [
    'knowledge', 'reasoning', 'robustness',
    'safety', 'structured-output', 'suggestibility',
]
KNOWN_PROVIDERS = [
    'gpt-4.1-mini', 'meta-llama-3.1-8b',
    'claude-3.5-haiku', 'gpt-4o',
]
KNOWN_SCENARIOS = ['multi-language']


def parse(raw, known):
    s = raw.strip()
    if s == 'all':
        return known
    values = [x.strip() for x in s.split(',') if x.strip()]
    unknown = [v for v in values if v not in known]
    if unknown:
        print(f'Error: unknown value(s): {unknown}. Known: {known}', file=sys.stderr)
        sys.exit(1)
    return values


def filter_tests_by_suite(test_names, suite):
    """Load test YAML files and return only cases tagged with *suite*."""
    filtered = []
    for name in test_names:
        path = f'tests/{name}.yaml'
        with open(path) as fh:
            cases = yaml.safe_load(fh) or []
        filtered.extend(
            case for case in cases
            if case.get('metadata', {}).get('suite') == suite
        )
    return filtered


def main():
    with open('promptfooconfig.yaml') as f:
        cfg = yaml.safe_load(f)

    test_names = parse(os.environ['TESTS_INPUT'], KNOWN_TESTS)
    suite = os.environ.get('SUITE_INPUT', '').strip()

    if suite:
        cfg['tests'] = filter_tests_by_suite(test_names, suite)
    else:
        cfg['tests'] = [f'file://tests/{t}.yaml' for t in test_names]

    cfg['providers'] = [
        f'file://providers/openrouter-{p}.yaml'
        for p in parse(os.environ['PROVIDERS_INPUT'], KNOWN_PROVIDERS)
    ]
    cfg['scenarios'] = [
        f'file://scenarios/{s}.yaml'
        for s in parse(os.environ['SCENARIOS_INPUT'], KNOWN_SCENARIOS)
    ]

    with open('promptfooconfig-run.yaml', 'w') as f:
        yaml.dump(cfg, f, default_flow_style=False, allow_unicode=True)


if __name__ == '__main__':
    main()
