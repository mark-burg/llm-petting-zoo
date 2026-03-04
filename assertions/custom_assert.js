/**
 * Custom assertion: checks that the output does not contain hallucinated URLs.
 *
 * Usage in promptfooconfig.yaml or test files:
 *   assert:
 *     - type: javascript
 *       value: file://assertions/custom_assert.js
 *
 * @param {string} output - The LLM output text.
 * @param {object} context - { vars, prompt, test, provider, providerResponse }
 * @returns {{ pass: boolean, score: number, reason: string }}
 */
module.exports = (output, context) => {
  // Simple heuristic: flag any URL that looks fabricated
  const urlPattern = /https?:\/\/[^\s)]+/g;
  const urls = output.match(urlPattern) || [];

  if (urls.length === 0) {
    return {
      pass: true,
      score: 1,
      reason: 'No URLs found in output — no hallucinated links.',
    };
  }

  // If the prompt did not ask for links, flag any URLs as suspicious
  const promptMentionsLinks =
    context.vars.input &&
    /\b(link|url|website|http|source)\b/i.test(context.vars.input);

  if (!promptMentionsLinks) {
    return {
      pass: false,
      score: 0,
      reason: `Output contains ${urls.length} URL(s) but the prompt did not ask for links: ${urls.join(', ')}`,
    };
  }

  return {
    pass: true,
    score: 1,
    reason: `Output contains ${urls.length} URL(s), which is acceptable since the prompt requested links.`,
  };
};
