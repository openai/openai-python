import json
import sys
import warnings

import openai


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def organization_info(obj):
    organization = getattr(obj, "organization", None)
    if organization is not None:
        return "[organization={}] ".format(organization)
    else:
        return ""


def display(obj):
    sys.stderr.write(organization_info(obj))
    sys.stderr.flush()
    print(obj)


def display_error(e):
    extra = (
        " (HTTP status code: {})".format(e.http_status)
        if e.http_status is not None
        else ""
    )
    sys.stderr.write(
        "{}{}Error:{} {}{}\n".format(
            organization_info(e), bcolors.FAIL, bcolors.ENDC, e, extra
        )
    )


class Engine:
    @classmethod
    def get(cls, args):
        engine = openai.Engine.retrieve(id=args.id)
        display(engine)

    @classmethod
    def update(cls, args):
        engine = openai.Engine(id=args.id)
        engine.replicas = args.replicas
        engine.save()
        display(engine)

    @classmethod
    def generate(cls, args):
        warnings.warn(
            "Engine.generate is deprecated, use Completion.create", DeprecationWarning
        )
        if args.completions and args.completions > 1 and args.stream:
            raise ValueError("Can't stream multiple completions with openai CLI")

        kwargs = {}
        if args.model is not None:
            kwargs["model"] = args.model
        resp = openai.Engine(id=args.id).generate(
            completions=args.completions,
            context=args.context,
            length=args.length,
            stream=args.stream,
            temperature=args.temperature,
            top_p=args.top_p,
            logprobs=args.logprobs,
            stop=args.stop,
            **kwargs
        )
        if not args.stream:
            resp = [resp]

        for part in resp:
            completions = len(part["data"])
            for c_idx, c in enumerate(part["data"]):
                if completions > 1:
                    sys.stdout.write("===== Completion {} =====\n".format(c_idx))
                sys.stdout.write("".join(c["text"]))
                if completions > 1:
                    sys.stdout.write("\n")
                sys.stdout.flush()

    @classmethod
    def search(cls, args):
        # Will soon be deprecated and replaced by a Search.create
        resp = openai.Engine(id=args.id).search(
            documents=args.documents, query=args.query
        )
        scores = [
            (search_result["score"], search_result["document"])
            for search_result in resp["data"]
        ]
        scores.sort(reverse=True)
        for score, document_idx in scores:
            print("=== score {:.3f} ===".format(score))
            print(args.documents[document_idx])

    @classmethod
    def list(cls, args):
        engines = openai.Engine.list()
        display(engines)


class Completion:
    @classmethod
    def create(cls, args):
        if args.n is not None and args.n > 1 and args.stream:
            raise ValueError("Can't stream completions with n>1 with the current CLI")

        resp = openai.Completion.create(
            engine=args.engine,
            n=args.n,
            max_tokens=args.max_tokens,
            logprobs=args.logprobs,
            prompt=args.prompt,
            stream=args.stream,
            temperature=args.temperature,
            top_p=args.top_p,
            stop=args.stop,
            echo=True,
        )
        if not args.stream:
            resp = [resp]

        for part in resp:
            choices = part["choices"]
            for c_idx, c in enumerate(sorted(choices, key=lambda s: s["index"])):
                if len(choices) > 1:
                    sys.stdout.write("===== Completion {} =====\n".format(c_idx))
                sys.stdout.write(c["text"])
                if len(choices) > 1:
                    sys.stdout.write("\n")
                sys.stdout.flush()


class Snapshot:
    @classmethod
    def create(cls, args):
        resp = openai.Snapshot.create(
            engine=args.engine,
            branch=args.branch,
            description=args.description,
            timeout=args.timeout,
        )
        print(resp)

    @classmethod
    def get(cls, args):
        resp = openai.Snapshot.retrieve(
            engine=args.engine, id=args.id, timeout=args.timeout
        )
        print(resp)

    @classmethod
    def delete(cls, args):
        snapshot = openai.Snapshot(id=args.id).delete()
        print(snapshot)

    @classmethod
    def list(cls, args):
        snapshots = openai.Snapshot.list()
        print(snapshots)


class Tag:
    @classmethod
    def create(cls, args):
        resp = openai.Tag.create(id=args.id, model=args.model, force=args.force)
        print(resp)

    @classmethod
    def get(cls, args):
        resp = openai.Tag.retrieve(id=args.id)
        print(resp)

    @classmethod
    def delete(cls, args):
        tag = openai.Tag(id=args.id).delete()
        print(tag)

    @classmethod
    def list(cls, args):
        tags = openai.Tag.list()
        print(tags)


def register(parser):
    # Engine management
    subparsers = parser.add_subparsers(help="All API subcommands")

    def help(args):
        parser.print_help()

    parser.set_defaults(func=help)

    sub = subparsers.add_parser("engines.list")
    sub.set_defaults(func=Engine.list)

    sub = subparsers.add_parser("engines.get")
    sub.add_argument("-i", "--id", required=True)
    sub.set_defaults(func=Engine.get)

    sub = subparsers.add_parser("engines.update")
    sub.add_argument("-i", "--id", required=True)
    sub.add_argument("-r", "--replicas", type=int)
    sub.set_defaults(func=Engine.update)

    sub = subparsers.add_parser("engines.generate")
    sub.add_argument("-i", "--id", required=True)
    sub.add_argument(
        "--stream", help="Stream tokens as they're ready.", action="store_true"
    )
    sub.add_argument("-c", "--context", help="An optional context to generate from")
    sub.add_argument("-l", "--length", help="How many tokens to generate", type=int)
    sub.add_argument(
        "-t",
        "--temperature",
        help="""What sampling temperature to use. Higher values means the model will take more risks. Try 0.9 for more creative applications, and 0 (argmax sampling) for ones with a well-defined answer.

Mutually exclusive with `top_p`.""",
        type=float,
    )
    sub.add_argument(
        "-p",
        "--top_p",
        help="""An alternative to sampling with temperature, called nucleus sampling, where the considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10%% probability mass are considered.

            Mutually exclusive with `temperature`.""",
        type=float,
    )
    sub.add_argument(
        "-n",
        "--completions",
        help="How many parallel completions to run on this context",
        type=int,
    )
    sub.add_argument(
        "--logprobs",
        help="Include the log probabilites on the `logprobs` most likely tokens. So for example, if `logprobs` is 10, the API will return a list of the 10 most likely tokens. If `logprobs` is supplied, the API will always return the logprob of the generated token, so there may be up to `logprobs+1` elements in the response.",
        type=int,
    )
    sub.add_argument(
        "--stop", help="A stop sequence at which to stop generating tokens."
    )
    sub.add_argument(
        "-m",
        "--model",
        required=False,
        help="A model (most commonly a snapshot ID) to generate from. Defaults to the engine's default snapshot.",
    )
    sub.set_defaults(func=Engine.generate)

    sub = subparsers.add_parser("engines.search")
    sub.add_argument("-i", "--id", required=True)
    sub.add_argument(
        "-d",
        "--documents",
        action="append",
        help="List of documents to search over",
        required=True,
    )
    sub.add_argument("-q", "--query", required=True, help="Search query")
    sub.set_defaults(func=Engine.search)

    ## Completions
    sub = subparsers.add_parser("completions.create")
    sub.add_argument("-e", "--engine", required=True, help="The engine to use")
    sub.add_argument(
        "--stream", help="Stream tokens as they're ready.", action="store_true"
    )
    sub.add_argument("-p", "--prompt", help="An optional prompt to complete from")
    sub.add_argument(
        "-M", "--max-tokens", help="The maximum number of tokens to generate", type=int
    )
    sub.add_argument(
        "-t",
        "--temperature",
        help="""What sampling temperature to use. Higher values means the model will take more risks. Try 0.9 for more creative applications, and 0 (argmax sampling) for ones with a well-defined answer.

Mutually exclusive with `top_p`.""",
        type=float,
    )
    sub.add_argument(
        "-P",
        "--top_p",
        help="""An alternative to sampling with temperature, called nucleus sampling, where the considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10%% probability mass are considered.

            Mutually exclusive with `temperature`.""",
        type=float,
    )
    sub.add_argument(
        "-n",
        "--n",
        help="How many sub-completions to generate for each prompt.",
        type=int,
    )
    sub.add_argument(
        "--logprobs",
        help="Include the log probabilites on the `logprobs` most likely tokens, as well the chosen tokens. So for example, if `logprobs` is 10, the API will return a list of the 10 most likely tokens. If `logprobs` is 0, only the chosen tokens will have logprobs returned.",
        type=int,
    )
    sub.add_argument(
        "--stop", help="A stop sequence at which to stop generating tokens."
    )
    sub.set_defaults(func=Completion.create)

    ## Snapshots
    sub = subparsers.add_parser("snapshots.list")
    sub.set_defaults(func=Snapshot.list)

    sub = subparsers.add_parser("snapshots.create")
    sub.add_argument(
        "-e", "--engine", required=True, help="The engine this snapshot is running on"
    )
    sub.add_argument(
        "-b", "--branch", required=True, help="The branch to turn into a snapshot"
    )
    sub.add_argument(
        "-d", "--description", help="A human-readable description of this snapshot"
    )
    sub.add_argument(
        "-t",
        "--timeout",
        help="An optional amount of time to block for the snapshot to transition from pending. If the timeout expires, a pending snapshot will be returned.",
        type=float,
    )
    sub.set_defaults(func=Snapshot.create)

    sub = subparsers.add_parser("snapshots.get")
    sub.add_argument("-e", "--engine", help="The engine this snapshot is running on")
    sub.add_argument("-i", "--id", required=True, help="The snapshot ID")
    sub.add_argument(
        "-t",
        "--timeout",
        help="An optional amount of time to block for the snapshot to transition from pending. If the timeout expires, a pending snapshot will be returned.",
        type=float,
    )
    sub.set_defaults(func=Snapshot.get)

    sub = subparsers.add_parser("snapshots.delete")
    sub.add_argument("-i", "--id", required=True, help="The snapshot ID")
    sub.set_defaults(func=Snapshot.delete)

    # Tags
    sub = subparsers.add_parser("tags.create")
    sub.add_argument("-i", "--id", help="The ID of the tag to create", required=True)
    sub.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Whether to overwrite an existing tag with this ID",
    )
    sub.add_argument(
        "-m",
        "--model",
        help="Which model (most commonly a snapshot ID) to tag",
        required=True,
    )
    sub.set_defaults(func=Tag.create)

    sub = subparsers.add_parser("tags.get")
    sub.add_argument("-i", "--id", required=True, help="The tag ID")
    sub.set_defaults(func=Tag.get)

    sub = subparsers.add_parser("tags.delete")
    sub.add_argument("-i", "--id", required=True, help="The tag ID")
    sub.set_defaults(func=Tag.delete)

    sub = subparsers.add_parser("tags.list")
    sub.set_defaults(func=Tag.list)
