'use strict';

/**
 * Content-Filter-Safe OpenAI-compatible Provider
 *
 * Wraps any OpenAI-compatible chat endpoint and converts HTTP 400 content-filter
 * errors into a ProviderResponse with a top-level `guardrails` object instead
 * of a ProviderResponse error, enabling the built-in `not-guardrails` assertion.
 *
 * Why this is necessary (not replaced by the built-in `github:` provider):
 * The `github:` provider is literally `new OpenAiChatCompletionProvider(model,
 * { apiBaseUrl: 'https://models.github.ai/inference', apiKeyEnvar: 'GITHUB_TOKEN'})`.
 * Its `callApiInternal` only converts HTTP 400 errors with `error.code === 'invalid_prompt'`
 * to `{ isRefusal: true, guardrails }`. GitHub Models is backed by Azure and returns
 * `error.code === 'content_filter'` for policy blocks — a different code that falls through
 * to `{ error }`. When promptfoo receives `{ error }` it skips all assertions, so neither
 * `not-guardrails` nor `llm-rubric` ever runs. This provider catches those `content_filter`
 * 400s and returns `{ output, guardrails: { flagged: true } }` so assertions can evaluate.
 *
 * Usage in provider YAML (do NOT use file:// prefix -- it causes Nunjucks to
 * inline the file content rather than require() it as a module):
 *   id: providers/content-filter-safe.js
 *   label: <display name>
 *   config:
 *     model: <model id>
 *     apiKeyEnvar: <env var holding the API key>
 *     apiBaseUrl: https://models.github.ai/inference  # no /v1 — the OpenAI JS SDK
 *                                                       # appends paths verbatim
 *     temperature: 0   # optional, defaults to 0
 *
 * Docs: https://www.promptfoo.dev/docs/configuration/expected-outputs/guardrails/
 *       https://www.promptfoo.dev/docs/providers/custom-api/
 *
 */

const { OpenAI } = require('openai');

/**
 * Returns true if the OpenAI SDK error is a provider content-filter block.
 * Covers Azure OpenAI "content management policy" and GitHub Models safety filter.
 */
function isContentFilterError(err) {
  const status = err && err.status;
  if (status !== 400) return false;
  const code = err && err.error && err.error.code;
  if (code === 'content_filter') return true;
  const msg = String((err && err.message) || '');
  return /content.{0,40}(filter|management|policy)|filtered due to|triggered azure/i.test(msg);
}

class ContentFilterSafeProvider {
  /**
   * promptfoo instantiates custom class providers with a single merged options
   * object: new Class({ ...providerOptions, id: providerId })
   * (see promptfoo evaluator source, providerMap JS factory)
   */
  constructor(options) {
    this._id = (options && options.id) || 'content-filter-safe';
    this.config = (options && options.config) || {};
  }

  id() {
    return this._id;
  }

  async callApi(prompt) {
    const cfg = this.config;
    const apiKey = process.env[cfg.apiKeyEnvar];
    const baseURL = cfg.apiBaseUrl;
    const model = cfg.model;
    const temperature = (cfg.temperature != null) ? cfg.temperature : 0;

    const client = new OpenAI({ apiKey, baseURL });

    let response;
    try {
      response = await client.chat.completions.create({
        model,
        messages: [{ role: 'user', content: prompt }],
        temperature,
      });
    } catch (err) {
      if (isContentFilterError(err)) {
        // Return a guardrails-flagged response so the built-in `not-guardrails`
        // assertion can evaluate it. The evaluator skips assertions on { error },
        // so we must return { output, guardrails } instead.
        // See: https://www.promptfoo.dev/docs/configuration/expected-outputs/guardrails/
        const reason = (err && err.message) || String(err);
        return {
          output: reason,
          guardrails: {
            flagged: true,
            flaggedInput: true,
            flaggedOutput: false,
            reason,
          },
        };
      }
      return {
        error: 'API error: ' + ((err && err.status) || '') + ' ' + ((err && err.message) || String(err)),
      };
    }

    const choice = response.choices && response.choices[0];
    const text = (choice && choice.message && choice.message.content) || '';
    return {
      output: text,
      tokenUsage: response.usage
        ? {
            prompt: response.usage.prompt_tokens,
            completion: response.usage.completion_tokens,
            total: response.usage.total_tokens,
          }
        : undefined,
    };
  }
}

module.exports = ContentFilterSafeProvider;
