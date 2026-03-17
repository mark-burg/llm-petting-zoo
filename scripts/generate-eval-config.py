#!/usr/bin/env python3
"""
Generate a runtime promptfoo config by patching tests, providers, and scenarios.

Reads promptfooconfig.yaml, replaces the three selection keys based on
environment variables, and writes promptfooconfig-run.yaml.

Environment variables:
  TESTS_INPUT      Comma-separated test names, or "all"
  PROVIDERS_INPUT  Comma-separated provider keys, or "all"
  SCENARIOS_INPUT  Comma-separated scenario names, or "all"
"""

import os
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
    return known if s == 'all' else [x.strip() for x in s.split(',') if x.strip()]


with open('promptfooconfig.yaml') as f:
    cfg = yaml.safe_load(f)

cfg['tests'] = [
    f'file://tests/{t}.yaml'
    for t in parse(os.environ['TESTS_INPUT'], KNOWN_TESTS)
]
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
