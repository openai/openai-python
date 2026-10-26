'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const http = require('node:http');
const os = require('node:os');
const path = require('node:path');
const { spawn } = require('node:child_process');
const { test } = require('node:test');
const repository = path.resolve(__dirname, '..');

// Exercise the actual pinned resolver against a local metadata-only registry.
// No package tarball or install script should be fetched or executed.
test('pnpm rejects missing and recent publication dates', async (t) => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'openai-release-age-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  let published;
  let tarballRequests = 0;
  const server = http.createServer((request, response) => {
    if (request.url !== '/release-age-fixture') {
      if (request.url === '/fixture.tgz') tarballRequests++;
      response.writeHead(404).end();
      return;
    }
    const metadata = {
      name: 'release-age-fixture',
      'dist-tags': { latest: '1.0.0' },
      versions: {
        '1.0.0': {
          name: 'release-age-fixture', version: '1.0.0',
          dist: { tarball: `${registry}/fixture.tgz`, integrity: 'sha512-' + Buffer.alloc(64).toString('base64') },
        },
      },
    };
    if (published) metadata.time = { '1.0.0': published };
    response.writeHead(200, { 'content-type': 'application/json' }).end(JSON.stringify(metadata));
  });
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  t.after(() => new Promise((resolve) => server.close(resolve)));
  const registry = `http://127.0.0.1:${server.address().port}`;
  const manifest = JSON.parse(fs.readFileSync(path.join(repository, 'package.json')));

  for (const [label, date, succeeds] of [
    ['missing', undefined, false],
    ['recent', new Date().toISOString(), false],
    ['mature', '2020-01-01T00:00:00.000Z', true],
  ]) {
    published = date;
    const directory = path.join(root, label);
    fs.mkdirSync(directory);
    fs.writeFileSync(path.join(directory, 'package.json'), JSON.stringify({
      name: 'release-age-test', private: true, packageManager: manifest.packageManager,
      dependencies: { 'release-age-fixture': '1.0.0' },
    }));
    fs.copyFileSync(path.join(repository, 'pnpm-workspace.yaml'), path.join(directory, 'pnpm-workspace.yaml'));
    const result = await new Promise((resolve, reject) => {
      const child = spawn('pnpm', ['install', '--lockfile-only', '--ignore-scripts', '--registry', registry,
        '--store-dir', path.join(directory, 'store'), '--cache-dir', path.join(directory, 'cache')], {
        cwd: directory, env: { ...process.env, COREPACK_ENABLE_NETWORK: '0', NO_PROXY: '127.0.0.1',
          pnpm_config_pm_on_fail: 'error', pnpm_config_runtime_on_fail: 'error' },
        stdio: ['ignore', 'pipe', 'pipe'],
      });
      let output = '';
      child.stdout.on('data', (chunk) => { output += chunk; });
      child.stderr.on('data', (chunk) => { output += chunk; });
      child.on('error', reject);
      child.on('close', (status) => resolve({ status, output }));
    });
    assert.equal(result.status === 0, succeeds, `${label}: ${result.output}`);
    if (!succeeds) assert.match(result.output, /release.?age|matur|publish|timestamp/i);
  }
  assert.equal(tarballRequests, 0);
});
