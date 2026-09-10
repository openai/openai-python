#!/usr/bin/env bash

set -euo pipefail
set -C # Refuse to overwrite an existing fixture, including a symlink.
umask 077

# Generate random text and a sparse upload fixture (1 GiB by default).
# Pass a smaller byte count for a quick test. Print only the directory to stdout.
wanted_size=${1-1073741824}
if [[ $# -gt 1 || ! $wanted_size =~ ^[1-9][0-9]{0,9}$ ]] || (( wanted_size > 1073741824 )); then
  echo "Usage: bash examples/generate_file.sh [bytes: 1..1073741824]" >&2
  exit 2
fi
file_size=$(( ((wanted_size/12)+1)*12 ))
read_size=$((file_size*3/4))

fixture_dir=$(mktemp -d "${TMPDIR:-/tmp}/openai-upload.XXXXXXXXXX")
trap 'rm -rf -- "$fixture_dir"' EXIT
trap 'exit 1' HUP INT TERM

head -c "$read_size" /dev/urandom | base64 > "$fixture_dir/small_test_file.txt"
: > "$fixture_dir/big_test_file.txt"
truncate -s "$wanted_size" "$fixture_dir/big_test_file.txt"

printf '%s\n' "$fixture_dir"
# Successful fixtures belong to the caller; see uploads.py for cleanup.
trap - EXIT
