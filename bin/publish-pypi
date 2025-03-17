#!/usr/bin/env bash

set -eux
mkdir -p dist
rye build --clean
rye publish --yes --token=$PYPI_TOKEN
