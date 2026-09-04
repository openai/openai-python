'use strict';

const fs = require('node:fs');

// The caller must authenticate the published directory before using it.
function publish(source, destination) {
  try {
    fs.renameSync(source, destination);
  } catch (error) {
    if (!['EEXIST', 'ENOTEMPTY', 'EPERM', 'EACCES'].includes(error.code)) throw error;
    let winner;
    try {
      winner = fs.lstatSync(destination);
    } catch {
      throw error;
    }
    if (!winner.isDirectory() || winner.isSymbolicLink()) throw error;
  }
}

module.exports = publish;
if (require.main === module) publish(process.argv[2], process.argv[3]);
