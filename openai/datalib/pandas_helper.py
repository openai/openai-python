from openai.datalib.common import INSTRUCTIONS, MissingDependencyError, DependencyUnchecked


pandas = DependencyUnchecked()
HAS_PANDAS = False

PANDAS_INSTRUCTIONS = INSTRUCTIONS.format(library="pandas")


def assert_has_pandas():
    global pandas, HAS_PANDAS
    if isinstance(pandas, DependencyUnchecked):
        try:
            import pandas as pd
            pandas = pd
        except ImportError:
            pandas = None
        HAS_PANDAS = bool(pandas)

    if not HAS_PANDAS:
        raise MissingDependencyError(PANDAS_INSTRUCTIONS)
