# LLM Petting Zoo

A [promptfoo](https://www.promptfoo.dev/) project for systematically testing and comparing how different LLM models perform across various prompts.

## Project Structure

```
├── .github/
│   └── workflows/
│       └── prompt-eval.yml                 # CI: runs eval on PRs that touch prompts/tests/providers
├── promptfooconfig.yaml                    # Main config (auto-loaded by promptfoo)
├── prompts/                                # Prompt templates (use {{input}} variable)
│   ├── baseline.txt                        # Simple, minimal prompt
│   └── enhanced.txt                        # Detailed prompt with instructions
├── providers/                              # Model/provider configs (one per file)
│   ├── openrouter-gpt-4.1-mini.yaml        # GPT-4.1-mini (OpenRouter)
│   ├── openrouter-meta-llama-3.1-8b.yaml   # Meta-Llama-3.1-8B-Instruct (OpenRouter)
│   ├── openrouter-claude-3.5-haiku.yaml    # Claude 3.5 Haiku (OpenRouter)
│   └── openrouter-gpt-4o.yaml              # GPT-4o (OpenRouter)
├── tests/                                  # Test cases organised by domain
│   ├── knowledge.yaml                      # Factual recall
│   ├── reasoning.yaml                      # Applied reasoning & arithmetic
│   ├── robustness.yaml                     # Input-handling edge cases
│   ├── safety.yaml                         # Jailbreak, identity honesty, misinformation refusal
│   └── structured-output.yaml              # JSON validity and structure
├── scenarios/                              # Grouped data × test matrices
│   └── multi-language.yaml
├── assertions/                             # Custom JS assertion functions
│   └── valid_json.js
├── transforms/                             # Output transform functions
│   └── output_transform.js
├── extensions/                             # Lifecycle hooks (before/after each/all)
│   └── hooks.js
├── .env.example                            # Template for API keys
```

## Prerequisites

- **Node.js** ≥ 18
- API keys for the active providers (see `.env.example`). The default configuration uses OpenRouter for all providers (GPT-4.1-mini, Meta-Llama-3.1-8B-Instruct, Claude 3.5 Haiku, and GPT-4o). OpenRouter is subject to rate limits, so the test suite is kept small and concurrency is set to 1.

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
    category: knowledge  # knowledge | reasoning | robustness | safety
    priority: medium     # high | medium | low
    suite: smoke         # smoke | regression
```

The glob `file://tests/*.yaml` in `promptfooconfig.yaml` auto-includes any new file you add — no config change needed.

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
# Run only tests with a matching description
npx promptfoo eval --filter-pattern 'Shakespeare'

# Filter by metadata fields
npx promptfoo eval --filter-metadata category=safety
npx promptfoo eval --filter-metadata priority=high
npx promptfoo eval --filter-metadata suite=regression
npx promptfoo eval --filter-metadata suite=smoke --filter-metadata category=robustness

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

## Design Notes

**Cost assertion** — The native `type: cost` assertion throws a hard error on providers that do not return cost data. `defaultTest` uses a `javascript` assertion instead, which reads `context.providerResponse?.cost` and skips gracefully when the field is absent while still enforcing the $0.10 limit on providers that do report cost (OpenRouter providers report cost natively).

## Documentation

- [promptfoo Getting Started](https://www.promptfoo.dev/docs/getting-started/) — installation, first eval, basic config
- [Configuration Guide](https://www.promptfoo.dev/docs/configuration/guide/) — prompts, providers, tests, vars, transforms, Nunjucks templates, CSV/Sheets
- [Configuration Reference](https://www.promptfoo.dev/docs/configuration/reference/) — full type definitions for all config fields and evaluation I/O
- [Modular Configs](https://www.promptfoo.dev/docs/configuration/modular-configs/) — splitting configs across files, JS/TS configs, env-specific overrides
- [Assertions & Metrics](https://www.promptfoo.dev/docs/configuration/expected-outputs/) — assertion types (deterministic & model-graded), weights, named/derived metrics
- [Scenarios](https://www.promptfoo.dev/docs/configuration/scenarios/) — data × test matrices using shared variable sets
