# semanticsearch

A client-side implementation of our semantic search endpoint (https://beta.openai.com/docs/api-reference/search).

Our endpoint has a special fast implementation of this logic which
makes it very fast for calls involving many documents, so we recommend
using our implementation rather than this one for latency-sensitive
workloads.

We encourage you to try different variants of this client-side logic
-- we don't think our setup is likely optimal at all!

## Sample usage

The following usage will run a client-side semantic search. This
formats each document into a prompt asking the API for the document's
relevance, and then post-processes the logprobs to derive relevance
scores:

```
$ ./semanticsearch.py -q 'positive emotion' -d happy -d sad
[client-side semantic search] {'object': 'list', 'data': [{'object': 'search_result', 'document': 0, 'score': 204.448}, {'object': 'search_result', 'document': 1, 'score': 108.208}], 'model': 'ada:2020-05-03'}
```

We run the exact same logic server-side:

```
$ ./semanticsearch.py -q 'positive emotion' -d happy -d sad -s
[server-side semantic search] {'object': 'list', 'data': [{'object': 'search_result', 'document': 0, 'score': 204.448}, {'object': 'search_result', 'document': 1, 'score': 108.208}], 'model': 'ada:2020-05-03'}
```
