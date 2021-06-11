import os

from setuptools import find_packages, setup

version_contents = {}
version_path = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), "openai/version.py"
)
with open(version_path, "rt") as f:
    exec(f.read(), version_contents)

setup(
    name="openai",
    description="Python client library for the OpenAI API",
    version=version_contents["VERSION"],
    install_requires=[
        "requests>=2.20",  # to get the patch for CVE-2018-18074
        "tqdm",  # Needed for progress bars
    ],
    extras_require={"dev": ["black==20.8b1", "pytest==6.*"]},
    python_requires=">=3.6",
    scripts=["bin/openai"],
    packages=find_packages(exclude=["tests", "tests.*"]),
    package_data={
        "openai": [
            "data/ca-certificates.crt",
            "py.typed",
        ]
    },
    author="OpenAI",
    author_email="support@openai.com",
    url="https://github.com/openai/openai-python",
)
