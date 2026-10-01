// Execute the real workflow script with an offline GitHub API and capture writes.
const fs = require('node:fs');
const data = JSON.parse(fs.readFileSync(0, 'utf8'));
const writes = [];
const github = {
  rest: {
    actions: {getWorkflowRun: async () => ({data: data.run})},
    pulls: {get: async () => ({data: data.current}), list: 'pulls'},
    git: {getRef: async () => ({data: {object: {sha: data.current.base.sha}}})},
    repos: {
      createCommitStatus: async value => writes.push(value),
      listCommitStatusesForRef: 'statuses',
      listPullRequestsAssociatedWithCommit: 'associations',
    },
    issues: {
      listComments: 'comments',
      createComment: async value => writes.push({operation: 'create', ...value}),
      updateComment: async value => writes.push({operation: 'update', ...value}),
    },
  },
  paginate: async (method, params) => {
    if (method === 'statuses') return data.previous_statuses || [];
    if (method === 'comments') return data.comments || [];
    if (method === 'associations') return [];
    if (method === 'pulls' && params.head === 'contributor:sdk' && params.state === 'open') {
      return data.fallback_pulls || [];
    }
    throw new Error(`Unexpected GitHub lookup: ${method}`);
  },
};
const AsyncFunction = Object.getPrototypeOf(async function() {}).constructor;
new AsyncFunction('github', 'context', 'process', data.script)(github, data.context, {env: data.env || {}})
  .then(() => process.stdout.write(JSON.stringify(writes)))
  .catch(error => { console.error(error); process.exitCode = 1; });
