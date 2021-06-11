import os

from setuptools import setup

if os.getenv("OPENAI_UPLOAD") != "y":
    raise RuntimeError(
        "This package is a placeholder package on the public PyPI instance, and is not the correct version to install. If you are having trouble figuring out the correct package to install, please contact us."
    )

setup(name="openai", description="Placeholder package", version="0.0.1")
