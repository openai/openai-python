'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const http = require('node:http');
const net = require('node:net');
const { spawn, spawnSync } = require('node:child_process');

const root = path.resolve(__dirname, '../..');
const temporary = fs.mkdtempSync(path.join(os.tmpdir(), 'steady fork test '));
const fixture = path.join(temporary, 'checkout');
let child;

function run(args = ['--version']) {
  return spawnSync('bash', [path.join(fixture, 'scripts/run-steady'), ...args], {
    cwd: temporary, encoding: 'utf8', timeout: 30000,
  });
}

function rejects(pattern) {
  const result = run();
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, pattern);
}

function health(port) {
  return new Promise((resolve) => {
    const request = http.get(`http://127.0.0.1:${port}/_x-steady/health`, (response) => {
      response.resume();
      resolve(response.statusCode === 200);
    });
    request.setTimeout(1000, () => request.destroy());
    request.on('error', () => resolve(false));
  });
}

async function main() {
  const publication = spawnSync(process.execPath, [path.join(__dirname, 'publication.test.cjs')], { stdio: 'inherit' });
  assert.equal(publication.status, 0, 'Concurrent publication must succeed');
  fs.mkdirSync(path.join(fixture, 'scripts/steady'), { recursive: true });
  for (const file of ['scripts/run-steady', 'scripts/steady/settings', 'scripts/steady/source-sha256.cjs', 'scripts/steady/manifest.json']) {
    fs.copyFileSync(path.join(root, file), path.join(fixture, file));
  }
  rejects(/Missing/);

  const installed = spawnSync('bash', [path.join(root, 'scripts/steady/install')], { stdio: 'inherit' });
  assert.equal(installed.status, 0, 'Pinned source installation must succeed');
  const copied = spawnSync('cp', ['-R', path.join(root, 'scripts/steady/.cache'), path.join(fixture, 'scripts/steady/.cache')]);
  assert.equal(copied.status, 0);
  const version = run();
  assert.equal(version.status, 0, version.stderr);
  assert.match(version.stdout, /^steady \d+\.\d+\.\d+\s*$/);

  const configured = spawnSync('bash', [
    '-c',
    'STEADY_ROOT="$1"; source "$STEADY_ROOT/scripts/steady/settings"; printf "%s\\n%s\\n" "$STEADY_SOURCE" "$DENO_DIRECTORY"',
    'steady-settings', fixture,
  ], { encoding: 'utf-8' });
  assert.equal(configured.status, 0, configured.stderr);
  const [source, runtime] = configured.stdout.trim().split(/\r?\n/);
  const gitConfig = path.join(source, '.git/config');
  const originalConfig = fs.readFileSync(gitConfig);
  const marker = path.join(temporary, 'hook-ran');
  const hook = path.join(source, '.git/test-fsmonitor');
  fs.writeFileSync(hook, `#!/bin/sh\nprintf called > "${marker}"\n`, { mode: 0o755 });
  fs.appendFileSync(gitConfig, `\n[core]\n\tfsmonitor = ${JSON.stringify(hook)}\n`);
  assert.equal(run().status, 0, 'Cached Git metadata must not affect verification');
  assert.equal(fs.existsSync(marker), false, 'Verification must not execute cached Git hooks');
  fs.writeFileSync(gitConfig, originalConfig);
  fs.unlinkSync(hook);

  const entry = path.join(source, 'cmd/steady.ts');
  const original = fs.readFileSync(entry);
  fs.appendFileSync(entry, '\nthrow new Error("unexpected source execution");\n');
  rejects(/Steady source has local changes/);
  fs.writeFileSync(entry, original);

  const binary = path.join(runtime, process.platform === 'win32' ? 'deno.exe' : 'deno');
  fs.renameSync(binary, `${binary}.saved`);
  fs.writeFileSync(binary, '#!/bin/sh\necho unexpected-runtime-execution\n', { mode: 0o755 });
  rejects(/Deno executable checksum mismatch/);
  fs.unlinkSync(binary);
  fs.renameSync(`${binary}.saved`, binary);

  const archive = path.join(runtime, 'deno.zip');
  fs.renameSync(archive, `${archive}.saved`);
  fs.writeFileSync(archive, 'invalid archive');
  rejects(/Deno archive checksum mismatch/);
  fs.unlinkSync(archive);
  fs.renameSync(`${archive}.saved`, archive);

  assert.notEqual(run(['missing spec.yaml']).status, 0);
  const spec = 'spec with spaces.json';
  fs.writeFileSync(path.join(temporary, spec), JSON.stringify({
    openapi: '3.0.3', info: { title: 'Synthetic test', version: '1' },
    paths: { '/hello': { get: { responses: { 200: {
      description: 'OK', content: { 'application/json': { example: { hello: 'world' } } },
    } } } } },
  }));
  const listener = net.createServer();
  await new Promise((resolve) => listener.listen(0, '127.0.0.1', resolve));
  const port = listener.address().port;
  await new Promise((resolve) => listener.close(resolve));
  child = spawn('bash', [path.join(fixture, 'scripts/run-steady'), spec, '--host', '127.0.0.1', '-p', String(port)], {
    cwd: temporary, stdio: ['ignore', 'pipe', 'pipe'],
  });
  let output = '';
  child.stdout.on('data', (data) => { output += data; });
  child.stderr.on('data', (data) => { output += data; });
  let ready = false;
  for (let attempt = 0; attempt < 150; attempt++) {
    if (await health(port)) { ready = true; break; }
    if (child.exitCode !== null) break;
    await new Promise((resolve) => setTimeout(resolve, 100));
  }
  assert.ok(ready, output);
  const exited = new Promise((resolve) => child.once('exit', resolve));
  child.kill('SIGTERM');
  await Promise.race([exited, new Promise((_, reject) => {
    const timer = setTimeout(() => reject(new Error('Steady did not stop after SIGTERM')), 5000);
    timer.unref();
  })]);
  assert.equal(await health(port), false, 'SIGTERM must stop the server');
  console.log('Pinned Steady: install, offline launch, integrity, relative paths, health, and cleanup passed.');
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
}).finally(() => {
  if (child && child.exitCode === null) child.kill('SIGKILL');
  fs.rmSync(temporary, { recursive: true, force: true });
});
