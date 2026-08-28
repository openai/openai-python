'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const { test } = require('node:test');
const repository = path.resolve(__dirname, '..');

function fixture(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'openai-node-tooling-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  for (const file of ['package.json', 'scripts/bootstrap-node', 'scripts/run-pyright', 'scripts/run-steady', 'scripts/test', 'scripts/utils/node-tooling.cjs']) {
    fs.mkdirSync(path.dirname(path.join(root, file)), { recursive: true });
    fs.copyFileSync(path.join(repository, file), path.join(root, file));
  }
  // Exercise launcher behavior independently of the host's Node version.
  const manifest = JSON.parse(fs.readFileSync(path.join(root, 'package.json')));
  manifest.engines.node = process.versions.node;
  fs.writeFileSync(path.join(root, 'package.json'), JSON.stringify(manifest));
  return root;
}

function installFake(root, version = JSON.parse(fs.readFileSync(path.join(root, 'package.json'))).devDependencies.pyright) {
  const directory = path.join(root, 'node_modules/pyright');
  fs.mkdirSync(directory, { recursive: true });
  fs.writeFileSync(path.join(directory, 'package.json'), JSON.stringify({ version }));
  fs.writeFileSync(path.join(directory, 'index.js'), 'console.log(JSON.stringify(process.argv.slice(2))); process.exit(7);');
}

function run(root, args = ['pyright'], env = {}) {
  return spawnSync(process.execPath, ['scripts/utils/node-tooling.cjs', ...args], {
    cwd: root, encoding: 'utf8', env: { ...process.env, PATH: '', ...env },
  });
}

test('missing or stale tools fail without a package manager on PATH', (t) => {
  const root = fixture(t);
  let result = run(root);
  assert.equal(result.status, 1);
  assert.match(result.stderr, /Missing local pyright/);
  assert.match(result.stderr, /scripts\/bootstrap/);
  installFake(root, '0.0.0');
  result = run(root);
  assert.equal(result.status, 1);
  assert.match(result.stderr, /Expected pyright/);
});

test('local launcher forwards arguments and exit status without npm', (t) => {
  const root = fixture(t);
  installFake(root);
  const result = run(root, ['pyright', '-p', 'config with spaces.json', '--version']);
  assert.equal(result.status, 7);
  assert.deepEqual(JSON.parse(result.stdout), ['-p', 'config with spaces.json', '--version']);
});

test('wrong Node version fails before loading a tool', (t) => {
  const root = fixture(t);
  const file = path.join(root, 'package.json');
  const manifest = JSON.parse(fs.readFileSync(file));
  manifest.engines.node = '0.0.0';
  fs.writeFileSync(file, JSON.stringify(manifest));
  const result = run(root);
  assert.equal(result.status, 1);
  assert.match(result.stderr, /Expected Node.js 0.0.0/);
});

test('bootstrap refuses a wrong pnpm without attempting an install', (t) => {
  const root = fixture(t);
  const bin = path.join(root, 'bin');
  fs.mkdirSync(bin);
  fs.symlinkSync(process.execPath, path.join(bin, 'node'));
  fs.symlinkSync('/usr/bin/dirname', path.join(bin, 'dirname'));
  fs.writeFileSync(path.join(bin, 'pnpm'), '#!/bin/sh\n[ "$1" = --version ] || exit 90\nprintf "0.0.0\\n"\n', { mode: 0o755 });
  const result = spawnSync('/bin/bash', ['scripts/bootstrap-node'], {
    cwd: root, encoding: 'utf8', env: { ...process.env, PATH: bin },
  });
  assert.equal(result.status, 1);
  assert.match(result.stderr, /Expected pnpm/);
});

test('Steady is local-only and receives the original arguments', (t) => {
  const root = fixture(t);
  const missing = run(root, ['steady', '--version']);
  assert.equal(missing.status, 1);
  assert.match(missing.stderr, /Missing local steady/);
  const directory = path.join(root, 'node_modules/@stdy/cli');
  const manifest = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8'));
  fs.mkdirSync(directory, { recursive: true });
  fs.writeFileSync(path.join(directory, 'package.json'), JSON.stringify({ version: manifest.devDependencies['@stdy/cli'] }));
  fs.writeFileSync(path.join(directory, 'steady.js'), 'console.log(JSON.stringify(process.argv.slice(2)));');
  const result = run(root, ['steady', 'spec with spaces.yml', '--version']);
  assert.equal(result.status, 0);
  assert.deepEqual(JSON.parse(result.stdout), ['spec with spaces.yml', '--version']);
});

function executable(root, file, content) {
  const target = path.join(root, file);
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.writeFileSync(target, '#!/bin/sh\nset -e\n' + content + '\n', { mode: 0o755 });
}

for (const mode of ['start', 'running', 'override']) {
  test(`scripts/test preserves ${mode} mock-server behavior and both Python lanes`, (t) => {
    const root = fixture(t);
    const log = path.join(root, 'calls');
    const ready = path.join(root, 'ready');
    if (mode === 'running') fs.writeFileSync(ready, '');
    executable(root, 'bin/curl', '[ -f "$READY" ]');
    executable(root, 'bin/lsof', 'exit 0');
    executable(root, 'bin/uv', 'printf "uv %s\\n" "$*" >> "$CALLS"');
    executable(root, 'scripts/mock', 'printf "mock %s\\n" "$*" >> "$CALLS"\n: > "$READY"');
    executable(root, 'scripts/test-pydantic-v1', 'printf "v1 %s\\n" "$*" >> "$CALLS"');
    const result = spawnSync('/bin/bash', ['scripts/test', '-q', 'tests/test_client.py'], {
      cwd: root, encoding: 'utf8', env: {
        ...process.env, PATH: path.join(root, 'bin') + ':/usr/bin:/bin', CALLS: log, READY: ready,
        TEST_API_BASE_URL: mode === 'override' ? 'http://example.invalid' : '',
      },
    });
    assert.equal(result.status, 0, result.stderr);
    const calls = fs.readFileSync(log, 'utf8');
    assert.equal(calls.includes('mock --daemon'), mode === 'start');
    assert.match(calls, /uv run --locked --all-extras pytest -q tests\/test_client.py/);
    assert.match(calls, /v1 -q tests\/test_client.py/);
  });
}

test('Node dependency policy stays fail-closed', () => {
  const policy = fs.readFileSync(path.join(repository, 'pnpm-workspace.yaml'), 'utf8');
  for (const setting of [
    'minimumReleaseAge: 11520',
    'minimumReleaseAgeStrict: true',
    'minimumReleaseAgeIgnoreMissingTime: false',
    'trustPolicy: no-downgrade',
    'trustLockfile: false',
    'blockExoticSubdeps: true',
    'pmOnFail: error',
    'runtimeOnFail: error',
    'verifyDepsBeforeRun: error',
    'ignoreScripts: true',
    'strictDepBuilds: true',
    'allowBuilds: {}',
  ]) assert.ok(policy.split(/\r?\n/).includes(setting), `Missing policy: ${setting}`);
});

test('devcontainer installs the pinned toolchain and bootstraps local tools', (t) => {
  const file = path.join(repository, '.devcontainer/devcontainer.json');
  if (!fs.existsSync(file)) {
    t.skip('Devcontainer configuration is not included in source distributions');
    return;
  }
  // This checked-in JSONC file uses only whole-line comments.
  const config = JSON.parse(fs.readFileSync(file, 'utf8').split(/\r?\n/)
    .filter((line) => !line.trimStart().startsWith('//')).join('\n'));
  const manifest = JSON.parse(fs.readFileSync(path.join(repository, 'package.json')));
  const feature = config.features['ghcr.io/devcontainers/features/node:1'];
  assert.equal(feature.version, manifest.engines.node);
  assert.equal(feature.version, fs.readFileSync(path.join(repository, '.node-version'), 'utf8').trim());
  assert.equal(`pnpm@${feature.pnpmVersion}`, manifest.packageManager);
  assert.equal(config.postStartCommand, './scripts/bootstrap');
});
