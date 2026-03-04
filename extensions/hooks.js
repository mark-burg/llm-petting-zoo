/**
 * Extension hooks for promptfoo evaluation lifecycle.
 *
 * Register in promptfooconfig.yaml:
 *   extensions:
 *     - file://extensions/hooks.js:extensionHook
 *
 * All hook types are dispatched to this single function.
 * Return the (optionally mutated) context to persist changes.
 *
 * @param {'beforeAll'|'afterAll'|'beforeEach'|'afterEach'} hookName
 * @param {object} context
 */
async function extensionHook(hookName, context) {
  switch (hookName) {
    case 'beforeAll':
      console.log(
        `\n🚀 Starting eval suite: ${context.suite.description || '(unnamed)'}`,
      );
      console.log(`   Tests: ${context.suite.tests.length}`);
      break;

    case 'afterAll':
      console.log(
        `\n✅ Eval complete: ${context.results.length} result(s) collected.`,
      );
      break;

    case 'beforeEach':
      // Example: log each test as it starts
      if (process.env.LOG_LEVEL === 'debug') {
        console.log(
          `   ▶ Running: ${context.test.description || '(no description)'}`,
        );
      }
      break;

    case 'afterEach':
      // Example: warn on failures
      if (!context.result.success) {
        console.warn(
          `   ⚠ FAILED: ${context.test.description || '(no description)'}`,
        );
      }
      break;
  }
}

module.exports = extensionHook;
