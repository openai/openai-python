import datetime
import json
import os
import signal
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
            **kwargs,
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
        params = {
            "query": args.query,
            "max_rerank": args.max_rerank,
            "return_metadata": args.return_metadata,
        }
        if args.documents:
            params["documents"] = args.documents
        if args.file:
            params["file"] = args.file

        resp = openai.Engine(id=args.id).search(**params)
        scores = [
            (search_result["score"], search_result["document"])
            for search_result in resp["data"]
        ]
        scores.sort(reverse=True)
        dataset = (
            args.documents if args.documents else [x["text"] for x in resp["data"]]
        )
        for score, document_idx in scores:
            print("=== score {:.3f} ===".format(score))
            print(dataset[document_idx])
            if (
                args.return_metadata
                and args.file
                and "metadata" in resp["data"][document_idx]
            ):
                print(f"METADATA: {resp['data'][document_idx]['metadata']}")

    @classmethod
    def list(cls, args):
        engines = openai.Engine.list()
        display(engines)


class Completion:
    @classmethod
    def create(cls, args):
        if args.n is not None and args.n > 1 and args.stream:
            raise ValueError("Can't stream completions with n>1 with the current CLI")

        if args.engine and args.model:
            warnings.warn(
                "In most cases, you should not be specifying both engine and model."
            )

        resp = openai.Completion.create(
            engine=args.engine,
            model=args.model,
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


class File:
    @classmethod
    def create(cls, args):
        resp = openai.File.create(
            file=open(args.file),
            purpose=args.purpose,
        )
        print(resp)

    @classmethod
    def get(cls, args):
        resp = openai.File.retrieve(id=args.id)
        print(resp)

    @classmethod
    def delete(cls, args):
        file = openai.File(id=args.id).delete()
        print(file)

    @classmethod
    def list(cls, args):
        file = openai.File.list()
        print(file)


class FineTune:
    @classmethod
    def list(cls, args):
        resp = openai.FineTune.list()
        print(resp)

    @classmethod
    def _get_or_upload(cls, file):
        try:
            openai.File.retrieve(file)
        except openai.error.InvalidRequestError as e:
            if e.http_status == 404 and os.path.isfile(file):
                resp = openai.File.create(file=open(file), purpose="fine-tune")
                sys.stdout.write(
                    "Uploaded file from {file}: {id}\n".format(file=file, id=resp["id"])
                )
                return resp["id"]
        return file

    @classmethod
    def create(cls, args):
        create_args = {
            "training_file": cls._get_or_upload(args.training_file),
        }
        if args.validation_file:
            create_args["validation_file"] = cls._get_or_upload(args.validation_file)
        if args.model:
            create_args["model"] = args.model
        if args.hparams:
            try:
                hparams = json.loads(args.hparams)
            except json.decoder.JSONDecodeError:
                sys.stderr.write(
                    "--hparams must be JSON decodable and match the hyperparameter arguments of the API"
                )
                sys.exit(1)
            create_args.update(hparams)

        resp = openai.FineTune.create(**create_args)

        if args.no_wait:
            print(resp)
            return

        sys.stdout.write(
            "Created fine-tune: {job_id}\n"
            "Streaming events until fine-tuning is complete...\n\n"
            "(Ctrl-C will interrupt the stream, but not cancel the fine-tune)\n".format(
                job_id=resp["id"]
            )
        )
        cls._stream_events(resp["id"])

    @classmethod
    def get(cls, args):
        resp = openai.FineTune.retrieve(id=args.id)
        print(resp)

    @classmethod
    def events(cls, args):
        if not args.stream:
            resp = openai.FineTune.list_events(id=args.id)  # type: ignore
            print(resp)
            return
        cls._stream_events(args.id)

    @classmethod
    def _stream_events(cls, job_id):
        def signal_handler(sig, frame):
            status = openai.FineTune.retrieve(job_id).status
            sys.stdout.write(
                "\nStream interrupted. Job is still {status}. "
                "To cancel your job, run:\n\n"
                "openai api fine_tunes.cancel -i {job_id}\n".format(
                    status=status, job_id=job_id
                )
            )
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        events = openai.FineTune.stream_events(job_id)
        # TODO(rachel): Add a nifty spinner here.
        for event in events:
            sys.stdout.write(
                "[%s] %s"
                % (
                    datetime.datetime.fromtimestamp(event["created_at"]),
                    event["message"],
                )
            )
            sys.stdout.write("\n")
            sys.stdout.flush()

        resp = openai.FineTune.retrieve(id=job_id)
        status = resp["status"]
        if status == "succeeded":
            sys.stdout.write("\nJob complete! Status: succeeded 🎉")
            sys.stdout.write(
                "\nTry out your fine-tuned model:\n\n"
                "openai api completions.create -m {model} -p <YOUR_PROMPT>".format(
                    model=resp["fine_tuned_model"]
                )
            )
        elif status == "failed":
            sys.stdout.write(
                "\nJob failed. Please contact support@openai.com if you need assistance."
            )
        sys.stdout.write("\n")

    @classmethod
    def cancel(cls, args):
        resp = openai.FineTune.cancel(id=args.id)
        print(resp)


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
        help="List of documents to search over. Only one of `documents` or `file` may be supplied.",
        required=False,
    )
    sub.add_argument(
        "-f",
        "--file",
        help="A file id to search over.  Only one of `documents` or `file` may be supplied.",
        required=False,
    )
    sub.add_argument(
        "--max_rerank",
        help="The maximum number of documents to be re-ranked and returned by search. This flag only takes effect when `file` is set.",
        type=int,
        default=200,
    )
    sub.add_argument(
        "--return_metadata",
        help="A special boolean flag for showing metadata. If set `true`, each document entry in the returned json will contain a 'metadata' field. Default to be `false`. This flag only takes effect when `file` is set.",
        type=bool,
        default=False,
    )
    sub.add_argument("-q", "--query", required=True, help="Search query")
    sub.set_defaults(func=Engine.search)

    # Completions
    sub = subparsers.add_parser("completions.create")
    sub.add_argument(
        "-e",
        "--engine",
        help="The engine to use. See https://beta.openai.com/docs/engines for more about what engines are available.",
    )
    sub.add_argument(
        "-m",
        "--model",
        help="The model to use. At most one of `engine` or `model` should be specified.",
    )
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

    # Snapshots
    sub = subparsers.add_parser("snapshots.list")
    sub.set_defaults(func=Snapshot.list)

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

    # Files
    sub = subparsers.add_parser("files.create")

    sub.add_argument(
        "-f",
        "--file",
        required=True,
        help="File to upload",
    )
    sub.add_argument(
        "-p",
        "--purpose",
        help="Why are you uploading this file? (see https://beta.openai.com/docs/api-reference/ for purposes)",
        required=True,
    )
    sub.set_defaults(func=File.create)

    sub = subparsers.add_parser("files.get")
    sub.add_argument("-i", "--id", required=True, help="The files ID")
    sub.set_defaults(func=File.get)

    sub = subparsers.add_parser("files.delete")
    sub.add_argument("-i", "--id", required=True, help="The files ID")
    sub.set_defaults(func=File.delete)

    sub = subparsers.add_parser("files.list")
    sub.set_defaults(func=File.list)

    # Finetune
    sub = subparsers.add_parser("fine_tunes.list")
    sub.set_defaults(func=FineTune.list)

    sub = subparsers.add_parser("fine_tunes.create")
    sub.add_argument(
        "-t",
        "--training_file",
        required=True,
        help="JSONL file containing prompt-completion examples for training. This can "
        "be the ID of a file uploaded through the OpenAI API (e.g. file-abcde12345) "
        "or a local file path.",
    )
    sub.add_argument(
        "-v",
        "--validation_file",
        help="JSONL file containing prompt-completion examples for validation. This can "
        "be the ID of a file uploaded through the OpenAI API (e.g. file-abcde12345) "
        "or a local file path.",
    )
    sub.add_argument(
        "-m",
        "--model",
        help="The model to start fine-tuning from",
    )
    sub.add_argument(
        "--no_wait",
        action="store_true",
        help="If set, returns immediately after creating the job. Otherwise, waits for the job to complete.",
    )
    sub.add_argument("-p", "--hparams", help="Hyperparameter JSON")
    sub.set_defaults(func=FineTune.create)

    sub = subparsers.add_parser("fine_tunes.get")
    sub.add_argument("-i", "--id", required=True, help="The id of the fine-tune job")
    sub.set_defaults(func=FineTune.get)

    sub = subparsers.add_parser("fine_tunes.events")
    sub.add_argument("-i", "--id", required=True, help="The id of the fine-tune job")
    sub.add_argument(
        "-s",
        "--stream",
        action="store_true",
        help="If set, events will be streamed until the job is done. Otherwise, "
        "displays the event history to date.",
    )
    sub.set_defaults(func=FineTune.events)

    sub = subparsers.add_parser("fine_tunes.cancel")
    sub.add_argument("-i", "--id", required=True, help="The id of the fine-tune job")
    sub.set_defaults(func=FineTune.cancel)
