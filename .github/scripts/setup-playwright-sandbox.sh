#!/usr/bin/env bash
set -euo pipefail

# Ubuntu restricts user namespaces for downloaded Chromium. Keep Chromium's
# sandbox enabled and allow only the two executables installed for this CI job.
: "${RUNNER_TEMP:?RUNNER_TEMP is required}"
: "${PLAYWRIGHT_BROWSERS_PATH:?PLAYWRIGHT_BROWSERS_PATH is required}"
expected_root="$RUNNER_TEMP/openai-python-playwright"
if [[ "$PLAYWRIGHT_BROWSERS_PATH" != "$expected_root" || ! -d "$expected_root" ]]; then
  echo "Playwright must be installed inside this job's RUNNER_TEMP." >&2
  exit 1
fi
runner_root="$(realpath "$RUNNER_TEMP")"
install_root="$(realpath "$expected_root")"
# AppArmor uses these paths in its policy syntax, without globs or expansions.
if [[ "$install_root" != "$runner_root/openai-python-playwright" || ! "$install_root" =~ ^/[a-zA-Z0-9_./-]+$ ]]; then
  echo "Playwright installation escaped RUNNER_TEMP or contains unexpected path characters." >&2
  exit 1
fi
shopt -s nullglob
chromiums=("$install_root"/chromium-*/chrome-linux64/chrome)
headless_shells=("$install_root"/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell)
if [[ "${#chromiums[@]}" -ne 1 || "${#headless_shells[@]}" -ne 1 ]]; then
  echo "Expected one installed Chromium and one installed headless shell." >&2
  exit 1
fi
binaries=("${chromiums[0]}" "${headless_shells[0]}")
for index in "${!binaries[@]}"; do
  binary="$(realpath "${binaries[index]}")"
  if [[ ! -x "$binary" || "$binary" != "$install_root/"* || ! "$binary" =~ ^/[a-zA-Z0-9_./-]+$ ]]; then
    echo "Chromium executable is absent or outside this job's installation." >&2
    exit 1
  fi
  binaries[index]="$binary"
done
{
  printf 'abi <abi/4.0>,\ninclude <tunables/global>\n'
  for index in "${!binaries[@]}"; do
    printf 'profile openai-python-playwright-%s "%s" flags=(unconfined) {\n  userns,\n}\n' "$index" "${binaries[index]}"
  done
} | sudo tee /etc/apparmor.d/openai-python-playwright >/dev/null
sudo apparmor_parser -r /etc/apparmor.d/openai-python-playwright
