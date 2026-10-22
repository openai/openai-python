// File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.
// Execute the real workflow script with an offline GitHub API and capture writes.
const fs = require('node:fs');
const data = JSON.parse(fs.readFileSync(0, 'utf8'));
const writes = [];
const github = {
  rest: {
    actions: {
      getWorkflowRun: async ({ run_id }) => {
        if (data.run_errors?.[run_id])
          throw Object.assign(new Error('Workflow run lookup failed'), { status: data.run_errors[run_id] });
        return { data: data.runs_by_id?.[run_id] || data.run };
      },
      getWorkflow: async ({ workflow_id }) => ({
        data: {
          id: workflow_id === 'castiron-custom-code-comment.yml' ? 789 : 456,
          path: `.github/workflows/${workflow_id}`,
        },
      }),
      listWorkflowRuns: 'workflow-runs',
      reRunWorkflow: async (value) => {
        if (data.fail_rerun) throw new Error('Simulated dispatch failure');
        writes.push({ operation: 'rerun', ...value });
      },
    },
    pulls: {
      get: async ({ pull_number }) => ({
        data: data.current_sequence?.shift() || data.pulls_by_number?.[pull_number] || data.current,
      }),
      list: 'pulls',
      listReviews: 'reviews',
      listFiles: 'files',
    },
    git: {
      getRef: async ({ ref }) => ({
        data: {
          object: {
            sha: ref.startsWith('pull/')
              ? data.merge_sha
              : ref === 'heads/main' && data.main_sha
                ? data.main_sha
                : data.current.base.sha,
          },
        },
      }),
    },
    repos: {
      getCommit: async () => ({ data: data.merge_commit }),
      createCommitStatus: async (value) => {
        writes.push(value);
        data.statuses_by_sha ||= {};
        data.statuses_by_sha[value.sha] = [
          { ...value, creator: { login: 'github-actions[bot]' } },
          ...(data.statuses_by_sha[value.sha] || data.previous_statuses || []),
        ];
      },
      listCommitStatusesForRef: 'statuses',
      listPullRequestsAssociatedWithCommit: 'associations',
    },
    issues: {
      listComments: 'comments',
      createComment: async (value) => writes.push({ operation: 'create', ...value }),
      updateComment: async (value) => writes.push({ operation: 'update', ...value }),
    },
  },
  graphql: async (_query, { branch, cursor, number }) => {
    if (_query.includes('reviews(first:100')) {
      const page = data.review_pages?.shift();
      if (page && page.expected_cursor !== cursor) throw new Error('Wrong review cursor');
      return {
        repository: {
          pullRequest: {
            reviews: page || {
              nodes: data.review_nodes_by_number?.[number] || data.review_nodes || [],
              pageInfo: { hasNextPage: false, endCursor: null },
            },
          },
        },
      };
    }
    if (data.forbid_queue) throw new Error('Unexpected queue discovery');
    if ((branch || 'next') !== data.current.base.ref) throw new Error('Wrong queue target');
    const page = data.queue_pages?.shift();
    if (page && page.expected_cursor !== cursor) throw new Error('Wrong queue cursor');
    return {
      repository: {
        mergeQueue: {
          entries: page || {
            nodes:
              data.queue_nodes || (data.queue_absent ? [] : [{ headCommit: { oid: data.run.head_sha } }]),
            pageInfo: { hasNextPage: false, endCursor: null },
          },
        },
      },
    };
  },
  paginate: async (method, params) => {
    if (method === 'files') return data.files || [{ filename: '.castiron-ratchet.json' }];
    if (method === 'workflow-runs') return data.runs_by_sha?.[params.head_sha] || [];
    if (method === 'reviews') return data.reviews_by_number?.[params.pull_number] || data.reviews || [];
    if (method === 'statuses') return data.statuses_by_sha?.[params.ref] || data.previous_statuses || [];
    if (method === 'comments') return data.comments || [];
    if (method === 'associations') return data.associated_pulls || [];
    if (method === 'pulls' && params.head === 'contributor:sdk' && params.state === 'open') {
      return data.fallback_pulls || [];
    }
    throw new Error(`Unexpected GitHub lookup: ${method}`);
  },
};
const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
new AsyncFunction('github', 'context', 'process', 'require', data.script)(
  github,
  data.context,
  { env: data.env || {} },
  require,
)
  .then(() => process.stdout.write(JSON.stringify(writes)))
  .catch((error) => {
    if (data.capture_writes) fs.writeFileSync(data.capture_writes, JSON.stringify(writes));
    console.error(error);
    process.exitCode = 1;
  });
