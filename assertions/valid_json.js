/**
 * Custom assertion: checks that the output is valid, parseable JSON.
 *
 * Optionally validates that specific top-level keys are present by setting
 * the `required_keys` variable in the test case (comma-separated string or
 * an array of strings).
 *
 * Usage in a test case:
 *   assert:
 *     - type: javascript
 *       value: file://assertions/valid_json.js
 *
 * With required-key validation:
 *   vars:
 *     required_keys: 'name,age,email'
 *   assert:
 *     - type: javascript
 *       value: file://assertions/valid_json.js
 *
 * @param {string} output - The LLM output text.
 * @param {object} context - { vars, prompt, test, provider, providerResponse }
 * @returns {{ pass: boolean, score: number, reason: string }}
 */
module.exports = (output, context) => {
  // Strip markdown code fences if the model wrapped the JSON in them
  const stripped = output
    .replace(/^```(?:json)?\s*/i, '')
    .replace(/\s*```$/, '')
    .trim();

  let parsed;
  try {
    parsed = JSON.parse(stripped);
  } catch (err) {
    return {
      pass: false,
      score: 0,
      reason: `Output is not valid JSON: ${err.message}`,
    };
  }

  const rawKeys = context.vars?.required_keys;
  if (!rawKeys) {
    return {
      pass: true,
      score: 1,
      reason: 'Output is valid JSON.',
    };
  }

  const requiredKeys = Array.isArray(rawKeys)
    ? rawKeys
    : String(rawKeys)
        .split(',')
        .map((k) => k.trim())
        .filter(Boolean);

  const missing = requiredKeys.filter((k) => !(k in parsed));
  if (missing.length > 0) {
    return {
      pass: false,
      score: 0,
      reason: `Valid JSON but missing required top-level key(s): ${missing.join(', ')}`,
    };
  }

  return {
    pass: true,
    score: 1,
    reason: `Valid JSON with all required key(s) present: ${requiredKeys.join(', ')}`,
  };
};
