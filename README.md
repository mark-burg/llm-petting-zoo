# LLM Bullshit — Prompt & Model Evaluation Suite

A [promptfoo](https://www.promptfoo.dev/) project for systematically testing and comparing how different LLM models perform across various prompts.

## Project Structure

```
├── promptfooconfig.yaml      # Main config (auto-loaded by promptfoo)
├── .env.example              # Template for API keys
├── prompts/                  # Prompt templates (use {{input}} variable)
│   ├── baseline.txt          # Simple, minimal prompt
│   └── enhanced.txt          # Detailed prompt with instructions
├── providers/                # Model/provider configs (one per file)
│   ├── openai-gpt4.yaml     # GPT-4.1
│   └── openai-gpt4-mini.yaml# GPT-4.1-mini
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
└── extensions/               # Lifecycle hooks (before/after each/all)
    └── hooks.js
```

## Prerequisites

- **Node.js** ≥ 18
- An **OpenAI API key** (or keys for whichever providers you configure)

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

- [promptfoo Getting Started](https://www.promptfoo.dev/docs/getting-started/)
- [Configuration Guide](https://www.promptfoo.dev/docs/configuration/guide/)
- [Configuration Reference](https://www.promptfoo.dev/docs/configuration/reference/)
- [Assertions & Metrics](https://www.promptfoo.dev/docs/configuration/expected-outputs/)
- [Scenarios](https://www.promptfoo.dev/docs/configuration/scenarios/)
