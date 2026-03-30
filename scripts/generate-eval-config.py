#!/usr/bin/env python3
"""
Generate a runtime promptfoo config by patching tests, providers, and scenarios.

Reads promptfooconfig.yaml, replaces the three selection keys based on
environment variables, and writes promptfooconfig-run.yaml.

Environment variables:
  TESTS_INPUT      Comma-separated test names.
                   Options: conflict-of-interest, context, hallucinations,
                            knowledge, probability, reasoning, robustness,
                            safety, structured-output, suggestibility
  PROVIDERS_INPUT  Comma-separated provider keys.
                   Options: gpt-4.1-mini, meta-llama-3.1-8b,
                            claude-3.5-haiku, gpt-4o
  SCENARIOS_INPUT  Comma-separated scenario names.
                   Options: localization
  SUITE_INPUT      Optional metadata suite tag to filter test cases by
                   (e.g. smoke). Empty or unset means run all test cases.
"""

import os
import sys
import yaml

KNOWN_TESTS = [
    'conflict-of-interest', 'context', 'hallucinations',
    'knowledge', 'probability', 'reasoning', 'robustness',
    'safety', 'structured-output', 'suggestibility',
]
KNOWN_PROVIDERS = [
    'gpt-4.1-mini', 'meta-llama-3.1-8b',
    'claude-3.5-haiku', 'gpt-4o',
]
KNOWN_SCENARIOS = ['localization']


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


def load_provider_info(provider_paths):
    """Load id and label from each provider YAML file."""
    providers = []
    for path in provider_paths:
        filepath = path.replace('file://', '')
        with open(filepath) as fh:
            p = yaml.safe_load(fh) or {}
        providers.append({'id': p.get('id', ''), 'label': p.get('label', '')})
    return providers


def provider_ref_matches(ref, provider):
    """Return True if a per-test provider ref matches a configured provider.

    Supports:
      exact label:       claude-3.5-haiku
      exact id:          openrouter:anthropic/claude-3-5-haiku
      full-id wildcard:  openrouter:anthropic/*  (service-qualified)
      path wildcard:     anthropic/*             (service-agnostic)
    """
    if ref == provider['label']:
        return True
    if ref == provider['id']:
        return True
    if ref.endswith('/*'):
        prefix = ref[:-2]
        # Full-qualified: openrouter:anthropic/* matches openrouter:anthropic/...
        if provider['id'].startswith(prefix + '/'):
            return True
        # Path-only: anthropic/* matches *:anthropic/... regardless of service
        if ':' not in prefix:
            path = provider['id'].split(':', 1)[-1]
            if path.startswith(prefix + '/'):
                return True
    return False


def load_tests(test_names, suite=None):
    """Load test cases from YAML files, optionally filtering by suite tag."""
    cases = []
    for name in test_names:
        path = f'tests/{name}.yaml'
        with open(path) as fh:
            file_cases = yaml.safe_load(fh) or []
        if suite:
            file_cases = [
                c for c in file_cases
                if c.get('metadata', {}).get('suite') == suite
            ]
        cases.extend(file_cases)
    return cases


def filter_tests_by_providers(tests, configured_providers):
    """Filter and resolve per-test provider references.

    - Tests without a providers field are kept as-is (run on all providers).
    - Tests with a providers field are kept only if at least one ref matches a
      configured provider. The providers field is rewritten to the matched
      provider labels so promptfoo's own validation sees only exact references.
    """
    result = []
    for test in tests:
        refs = test.get('providers')
        if refs is None:
            result.append(test)
            continue
        matched_labels = [
            p['label'] or p['id']
            for p in configured_providers
            if any(provider_ref_matches(ref, p) for ref in refs)
        ]
        if matched_labels:
            result.append({**test, 'providers': matched_labels})
    return result


def main():
    with open('promptfooconfig.yaml') as f:
        cfg = yaml.safe_load(f)

    test_names = parse(os.environ['TESTS_INPUT'], KNOWN_TESTS)
    suite = os.environ.get('SUITE_INPUT', '').strip()

    provider_paths = [
        f'file://providers/openrouter-{p}.yaml'
        for p in parse(os.environ['PROVIDERS_INPUT'], KNOWN_PROVIDERS)
    ]
    configured_providers = load_provider_info(provider_paths)

    tests = load_tests(test_names, suite or None)
    cfg['tests'] = filter_tests_by_providers(tests, configured_providers)
    cfg['providers'] = provider_paths
    cfg['scenarios'] = [
        f'file://scenarios/{s}.yaml'
        for s in parse(os.environ['SCENARIOS_INPUT'], KNOWN_SCENARIOS)
    ]

    with open('promptfooconfig-run.yaml', 'w') as f:
        yaml.dump(cfg, f, default_flow_style=False, allow_unicode=True)


if __name__ == '__main__':
    main()
