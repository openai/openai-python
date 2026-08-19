'use strict';

// Resolve only this checkout's tools. Never invoke a package manager here.
const fs = require('node:fs');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const root = path.resolve(__dirname, '../..');
const manifest = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8'));

function fail(message) {
  console.error(`${message}\nRun ./scripts/bootstrap after installing the versions documented in CONTRIBUTING.md.`);
  process.exit(1);
}

if (process.versions.node !== manifest.engines.node) {
  fail(`Expected Node.js ${manifest.engines.node}, found ${process.versions.node}.`);
}

const [tool, ...args] = process.argv.slice(2);
if (tool === '--check-node') process.exit(0);
const tools = {
  pyright: { package: 'pyright', entry: 'index.js' },
  steady: { package: '@stdy/cli', entry: 'steady.js' },
};
if (!Object.hasOwn(tools, tool)) fail(`Unknown repository tool: ${tool}`);
const selected = tools[tool];

const directory = path.join(root, 'node_modules', selected.package);
let installed;
try {
  installed = JSON.parse(fs.readFileSync(path.join(directory, 'package.json'), 'utf8'));
} catch {
  fail(`Missing local ${tool}.`);
}
if (installed.version !== manifest.devDependencies[selected.package]) {
  fail(`Expected ${tool} ${manifest.devDependencies[selected.package]}, found ${installed.version}.`);
}
const entry = path.join(directory, selected.entry);
if (!fs.existsSync(entry)) fail(`Missing local ${tool} executable.`);
if (tool === 'steady') {
  // The upstream wrapper owns its native child and forwards termination signals.
  // Run it in this process so mock-server cleanup reaches that child.
  process.argv = [process.execPath, entry, ...args];
  require(entry);
} else {
  // Calling Node explicitly also avoids upstream 1.1.399's CRLF shebang issue.
  const result = spawnSync(process.execPath, [entry, ...args], { stdio: 'inherit' });
  if (result.error) fail(`Could not start ${tool}: ${result.error.message}`);
  process.exit(result.status ?? 1);
}
