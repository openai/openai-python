#!/usr/bin/env bash
set -exuo pipefail

FILENAME=$(basename dist/*.whl)

RESPONSE=$(curl -X POST "$URL?filename=$FILENAME" \
  -H "Authorization: Bearer $AUTH" \
  -H "Content-Type: application/json")

SIGNED_URL=$(echo "$RESPONSE" | jq -r '.url')

if [[ "$SIGNED_URL" == "null" ]]; then
  echo -e "\033[31mFailed to get signed URL.\033[0m"
  exit 1
fi

UPLOAD_RESPONSE=$(curl -v -X PUT \
  -H "Content-Type: binary/octet-stream" \
  --data-binary "@dist/$FILENAME" "$SIGNED_URL" 2>&1)

if echo "$UPLOAD_RESPONSE" | grep -q "HTTP/[0-9.]* 200"; then
  echo -e "\033[32mUploaded build to Stainless storage.\033[0m"
  echo -e "\033[32mInstallation: pip install 'https://pkg.stainless.com/s/openai-python/$SHA/$FILENAME'\033[0m"
else
  echo -e "\033[31mFailed to upload artifact.\033[0m"
  exit 1
fi
