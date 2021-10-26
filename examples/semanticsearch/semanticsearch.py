#!/usr/bin/env python
import argparse
import logging
import sys
from typing import List

import openai

logger = logging.getLogger()
formatter = logging.Formatter("[%(asctime)s] [%(process)d] %(message)s")
handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(formatter)
logger.addHandler(handler)

DEFAULT_COND_LOGP_TEMPLATE = (
    "<|endoftext|>{document}\n\n---\n\nThe above passage is related to: {query}"
)
SCORE_MULTIPLIER = 100.0


class SearchScorer:
    def __init__(
        self, *, document, query, cond_logp_template=DEFAULT_COND_LOGP_TEMPLATE
    ):
        self.document = document
        self.query = query
        self.cond_logp_template = cond_logp_template
        self.context = self.cond_logp_template.format(
            document=self.document, query=self.query
        )

    def get_context(self):
        return self.context

    def get_score(self, choice) -> float:
        assert choice.text == self.context
        logprobs: List[float] = choice.logprobs.token_logprobs
        text = choice.logprobs.tokens
        text_len = sum(len(token) for token in text)
        if text_len != len(self.context):
            raise RuntimeError(
                f"text_len={text_len}, len(self.context)={len(self.context)}"
            )
        total_len = 0
        last_used = len(text)
        while total_len < len(self.query):
            assert last_used > 0
            total_len += len(text[last_used - 1])
            last_used -= 1
        max_len = len(self.context) - self.cond_logp_template.index("{document}")
        assert total_len + len(self.document) <= max_len
        logits: List[float] = logprobs[last_used:]
        return sum(logits) / len(logits) * SCORE_MULTIPLIER


def semantic_search(engine, query, documents):
    # add empty document as baseline
    scorers = [
        SearchScorer(document=document, query=query) for document in [""] + documents
    ]
    completion = openai.Completion.create(
        engine=engine,
        prompt=[scorer.get_context() for scorer in scorers],
        max_tokens=0,
        logprobs=0,
        echo=True,
    )
    # put the documents back in order so we can easily normalize by the empty document 0
    data = sorted(completion.choices, key=lambda choice: choice.index)
    assert len(scorers) == len(
        data
    ), f"len(scorers)={len(scorers)} len(data)={len(data)}"
    scores = [scorer.get_score(choice) for scorer, choice in zip(scorers, data)]
    # subtract score for empty document
    scores = [score - scores[0] for score in scores][1:]
    data = {
        "object": "list",
        "data": [
            {
                "object": "search_result",
                "document": document_idx,
                "score": round(score, 3),
            }
            for document_idx, score in enumerate(scores)
        ],
        "model": completion.model,
    }
    return data


def main():
    parser = argparse.ArgumentParser(description=None)
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        dest="verbosity",
        default=0,
        help="Set verbosity.",
    )
    parser.add_argument("-e", "--engine", default="ada")
    parser.add_argument("-q", "--query", required=True)
    parser.add_argument("-d", "--document", action="append", required=True)
    parser.add_argument("-s", "--server-side", action="store_true")
    args = parser.parse_args()

    if args.verbosity == 1:
        logger.setLevel(logging.INFO)
    elif args.verbosity >= 2:
        logger.setLevel(logging.DEBUG)

    if args.server_side:
        resp = openai.Engine(id=args.engine).search(
            query=args.query, documents=args.document
        )
        resp = resp.to_dict_recursive()
        print(f"[server-side semantic search] {resp}")
    else:
        resp = semantic_search(args.engine, query=args.query, documents=args.document)
        print(f"[client-side semantic search] {resp}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
