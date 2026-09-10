'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawn } = require('node:child_process');
const publish = require('./publish.cjs');

const root = fs.mkdtempSync(path.join(os.tmpdir(), 'steady-publication-'));
const rename = fs.renameSync;

async function main() {
  const winner = path.join(root, 'winner');
  fs.mkdirSync(winner);
  fs.writeFileSync(path.join(winner, 'content'), 'verified winner');
  const linked = path.join(root, 'linked-winner');
  fs.symlinkSync(winner, linked, 'junction');
  for (const code of ['EPERM', 'EACCES', 'EEXIST', 'ENOTEMPTY']) {
    const error = Object.assign(new Error(code), { code });
    fs.renameSync = () => { throw error; };
    publish('loser', winner);
    assert.throws(() => publish('loser', linked), (actual) => actual === error);
    assert.equal(fs.readFileSync(path.join(winner, 'content'), 'utf8'), 'verified winner');
    assert.throws(() => publish('loser', path.join(root, 'absent')), (actual) => actual === error);
    assert.throws(() => publish('loser', path.join(winner, 'content')), (actual) => actual === error);
  }
  const denied = Object.assign(new Error('unrelated failure'), { code: 'EIO' });
  fs.renameSync = () => { throw denied; };
  assert.throws(() => publish('loser', winner), (actual) => actual === denied);
  fs.renameSync = rename;

  // Real competing processes publish complete directories to the same destination.
  const destination = path.join(root, 'concurrent');
  const attempts = Array.from({ length: 4 }, (_, index) => {
    const staged = path.join(root, `staged-${index}`);
    fs.mkdirSync(staged);
    fs.writeFileSync(path.join(staged, 'content'), String(index));
    return new Promise((resolve, reject) => {
      const child = spawn(process.execPath, [path.join(__dirname, 'publish.cjs'), staged, destination]);
      let output = '';
      child.stderr.on('data', (data) => { output += data; });
      child.on('error', reject);
      child.on('exit', (code) => code === 0 ? resolve() : reject(new Error(output)));
    });
  });
  await Promise.all(attempts);
  assert.match(fs.readFileSync(path.join(destination, 'content'), 'utf8'), /^[0-3]$/);
  assert.equal(fs.readdirSync(root).filter((name) => name.startsWith('staged-')).length, 3);
  console.log('Steady concurrent publication and Windows loser errors passed.');
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
}).finally(() => {
  fs.renameSync = rename;
  if (fs.rmSync) fs.rmSync(root, { recursive: true, force: true });
  else fs.rmdirSync(root, { recursive: true });
});
