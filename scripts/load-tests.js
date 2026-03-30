// Auto-discovery test loader.
// Reads every *.yaml file in this directory, parses each one, and sets
// `metric` on every assertion to the filename (minus extension) so that
// promptfoo aggregates scores per test file.

const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

const testsDir = path.join(__dirname, '..', 'tests');

const testFiles = fs
  .readdirSync(testsDir)
  .filter((f) => f.endsWith('.yaml'))
  .sort();

const allTests = [];

for (const file of testFiles) {
  const metric = path.basename(file, '.yaml');
  const raw = fs.readFileSync(path.join(testsDir, file), 'utf8');
  const tests = yaml.load(raw);

  if (!Array.isArray(tests)) continue;

  for (const test of tests) {
    if (!Array.isArray(test.assert)) continue;
    for (const assertion of test.assert) {
      assertion.metric = metric;
    }
  }

  allTests.push(...tests);
}

module.exports = allTests;
