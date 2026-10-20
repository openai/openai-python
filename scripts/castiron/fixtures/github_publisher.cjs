// File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.
// Execute the real workflow script with an offline GitHub API and capture writes.
const fs = require('node:fs');
const data = JSON.parse(fs.readFileSync(0, 'utf8'));
const writes = [];
const github = {
  rest: {
    actions: { getWorkflowRun: async () => ({ data: data.run }) },
    pulls: {
      get: async ({ pull_number }) => ({
        data: data.current_sequence?.shift() || data.pulls_by_number?.[pull_number] || data.current,
      }),
      list: 'pulls',
    },
    git: {
      getRef: async ({ ref }) => ({
        data: {
          object: { sha: ref === 'heads/main' && data.main_sha ? data.main_sha : data.current.base.sha },
        },
      }),
    },
    repos: {
      createCommitStatus: async (value) => writes.push(value),
      listCommitStatusesForRef: 'statuses',
      listPullRequestsAssociatedWithCommit: 'associations',
    },
    issues: {
      listComments: 'comments',
      createComment: async (value) => writes.push({ operation: 'create', ...value }),
      updateComment: async (value) => writes.push({ operation: 'update', ...value }),
    },
  },
  graphql: async (_query, { branch, cursor }) => {
    if (branch !== data.current.base.ref) throw new Error('Wrong queue target');
    const page = data.queue_pages?.shift();
    if (page && page.expected_cursor !== cursor) throw new Error('Wrong queue cursor');
    return {
      repository: {
        mergeQueue: {
          entries: page || {
            nodes: data.queue_absent ? [] : [{ headCommit: { oid: data.run.head_sha } }],
            pageInfo: { hasNextPage: false, endCursor: null },
          },
        },
      },
    };
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
const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
new AsyncFunction('github', 'context', 'process', data.script)(github, data.context, { env: data.env || {} })
  .then(() => process.stdout.write(JSON.stringify(writes)))
  .catch((error) => {
    console.error(error);
    process.exitCode = 1;
  });
