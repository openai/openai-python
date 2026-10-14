# Ask a question about local pages

On Linux, `OPENAI_EXAMPLE_BROWSER_CHANNEL=chrome` selects an installed Chrome.
Leave it unset to use the Playwright Chromium installed below.

This small example reads a three-page visitor guide and answers your question.
Responses chooses which pages to read. The driver exposes only page text, tabs
and navigation to those three pages. It cannot submit a form or change a record.
Playwright serves the pages from memory and blocks every other browser request.

From the Python SDK checkout or source archive root, install this source and
the browser dependency:

```sh
python3 -m venv .venv-browser
.venv-browser/bin/python -m pip install -e . playwright==1.63.0
.venv-browser/bin/python -m playwright install chromium
```

Set `OPENAI_API_KEY` and `OPENAI_MODEL` in your shell, then ask a question:

```sh
.venv-browser/bin/python examples/browser/read_only.py "Can a group of 14 visit on Monday? Which entrance is accessible?"
```

The answer should explain that the museum is closed on Monday, a group of 14
needs a reservation, and the accessible entrance is in the East Courtyard. It
should cite the local guide pages. The example cannot make a reservation.

Try a different question, such as "When is quiet hour?" To change the source
material, edit `reader-site.json`. The next run reads the current file. The model
does not receive a hidden answer table.

## Adapt the driver

Open `read_only.py`. `open_reader` owns the browser and supplies three local pages.
`ReadOnlyBrowser` defines the small driver. `answer_question` gives that driver
to `AsyncResponsesToolRunner`. The `async with` block keeps the browser alive
until the run finishes and closes it on exit.

For your application, replace the documents and the exact allowed URLs. Keep the
operation list explicit. Add an editing method only when you also have a current
target check, an approval policy and an independent check of the saved result.

## Check it without a key

```sh
.venv-browser/bin/python examples/browser/exercise_read_only.py
```

The check uses real Chromium and the installed SDK with controlled local API
replies. It asks two different questions, checks changed page content, refuses
outside navigation and rejects a disabled click. It does not measure a model's
answer quality or call an API provider.

The reader scans at most 2,000 DOM nodes and returns at most 16 KiB of UTF-8
text. This is the reader's own document budget, not an SDK limit. If content exceeds either budget, the result
ends with `[Some document content was omitted.]`. Links that do not fit are
omitted completely so a partial URL cannot be used for navigation. Split large
documents into linked pages to make the rest accessible.

Custom document paths must produce a full `http://reader.invalid/` URL of at
most 16 KiB. The reader refuses longer URLs before opening Chromium; it never
shortens a destination. Tab titles use up to 1 KiB of UTF-8 text. Keep paths
short so the URL and surrounding guide text can fit together in a read.
