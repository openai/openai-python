'use strict';

const { createHash } = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');

const files = [];
function visit(directory, relative = '') {
  for (const name of fs.readdirSync(directory).sort()) {
    if (relative === '' && name === '.git') {
      if (!fs.lstatSync(path.join(directory, name)).isDirectory()) {
        throw new Error('Unexpected Git metadata entry');
      }
      continue;
    }
    const file = path.join(directory, name);
    const filename = relative ? `${relative}/${name}` : name;
    const stat = fs.lstatSync(file);
    if (stat.isDirectory()) {
      visit(file, filename);
    } else if (stat.isFile()) {
      files.push([filename, createHash('sha256').update(fs.readFileSync(file)).digest('hex')]);
    } else {
      throw new Error(`Unexpected source entry: ${filename}`);
    }
  }
}

visit(process.argv[2]);
console.log(createHash('sha256').update(JSON.stringify(files)).digest('hex'));
