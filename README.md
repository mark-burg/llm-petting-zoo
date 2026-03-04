# LLM Petting Zoo

A [promptfoo](https://www.promptfoo.dev/) project for systematically testing and comparing how different LLM models perform across various prompts.

## Project Structure

```
├── .github/
│   └── workflows/
│       └── prompt-eval.yml   # CI: runs eval on PRs that touch prompts/tests/providers
├── promptfooconfig.yaml      # Main config (auto-loaded by promptfoo)
├── prompts/                  # Prompt templates (use {{input}} variable)
│   ├── baseline.txt          # Simple, minimal prompt
│   └── enhanced.txt          # Detailed prompt with instructions
├── providers/                # Model/provider configs (one per file)
│   ├── openai-gpt4-mini.yaml# GPT-4.1-mini
│   └── meta-llama-3.1-8b.yaml# Meta-Llama-3.1-8B-Instruct
├── tests/                    # Test cases organised by category
│   ├── basic_functionality.yaml
│   ├── edge_cases.yaml
│   └── regression.yaml
├── scenarios/                # Grouped data × test matrices
│   └── multi-language.yaml
├── assertions/               # Custom JS assertion functions
│   └── custom_assert.js
├── transforms/               # Output transform functions
│   └── output_transform.js
├── extensions/               # Lifecycle hooks (before/after each/all)
│   └── hooks.js
├── .env.example              # Template for API keys
```

## Prerequisites

- **Node.js** ≥ 18
- Some way to call the LLM APIs for the models under test (just add them in `providers/`). Note that I'm using GitHub's free models which are subject to rate limiting and usage caps. This directly results in a few different sacrifices in this project: keeping the test suite small, rarely utilizing concurrency, and ommitting tests that relied on llm-rubric grading.

## Quick Start

```bash
# 1. Install dependencies
npm install

# 2. Configure API keys
cp .env.example .env
# Edit .env and add your real API keys

# 3. Run the evaluation
npx promptfoo eval

# 4. View results in the browser
npx promptfoo view
```

## Adding New Tests

Create a new YAML file in `tests/` following this structure:

```yaml
- description: 'Describe what you are testing'
  vars:
    input: 'The question or prompt input'
  assert:
    - type: contains
      value: 'expected substring'
  metadata:
    category: your-category
    priority: high
```

Then add it to `promptfooconfig.yaml` under `tests:`:

```yaml
tests:
  - file://tests/your_new_tests.yaml
```

Or use a glob to auto-include everything:

```yaml
tests:
  - file://tests/*.yaml
```

## Adding New Prompts

Add a `.txt` file in `prompts/` using `{{input}}` (or any variable name) as a placeholder, then reference it in the config:

```yaml
prompts:
  - file://prompts/your_prompt.txt
```

## Adding New Providers

Create a YAML file in `providers/`:

```yaml
id: openai:gpt-4.1
label: gpt-4.1
config:
  temperature: 0
```

Then add to the config:

```yaml
providers:
  - file://providers/your_provider.yaml
```

## Filtering Tests

```bash
# Run only tests with "factual" in the description
npx promptfoo eval --filter-pattern 'factual'

# Run only tests matching specific metadata
npx promptfoo eval --filter-metadata category=edge-case

# Run only against a specific provider
npx promptfoo eval --filter-providers 'gpt-4.1-mini'
```

## Useful Commands

| Command | Description |
|---|---|
| `npx promptfoo eval` | Run the full evaluation matrix |
| `npx promptfoo eval -c config.yaml` | Run with a specific config |
| `npx promptfoo view` | Open the web UI to view results |
| `npx promptfoo cache clear` | Clear the response cache |
| `npx promptfoo eval --no-cache` | Run without caching |
| `npx promptfoo eval --repeat 3` | Run each test 3 times for consistency |

## Documentation

- [promptfoo Getting Started](https://www.promptfoo.dev/docs/getting-started/) — installation, first eval, basic config
- [Configuration Guide](https://www.promptfoo.dev/docs/configuration/guide/) — prompts, providers, tests, vars, transforms, Nunjucks templates, CSV/Sheets
- [Configuration Reference](https://www.promptfoo.dev/docs/configuration/reference/) — full type definitions for all config fields and evaluation I/O
- [Modular Configs](https://www.promptfoo.dev/docs/configuration/modular-configs/) — splitting configs across files, JS/TS configs, env-specific overrides
- [Assertions & Metrics](https://www.promptfoo.dev/docs/configuration/expected-outputs/) — assertion types (deterministic & model-graded), weights, named/derived metrics
- [Scenarios](https://www.promptfoo.dev/docs/configuration/scenarios/) — data × test matrices using shared variable sets
