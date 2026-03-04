/**
 * Output transform: trims whitespace and normalises line breaks.
 *
 * Usage in promptfooconfig.yaml:
 *   defaultTest:
 *     options:
 *       transform: file://transforms/output_transform.js
 *
 * @param {string} output - Raw LLM output.
 * @param {object} context - { vars, prompt, metadata }
 * @returns {string} Cleaned output.
 */
module.exports = (output, context) => {
  if (typeof output !== 'string') {
    return output;
  }

  return output
    .trim()
    .replace(/\r\n/g, '\n') // normalise Windows line endings
    .replace(/\n{3,}/g, '\n\n'); // collapse excessive blank lines
};
