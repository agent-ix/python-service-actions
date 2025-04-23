#!/bin/bash
set -euo pipefail

IMAGE_FULL="$1"
TAG="$2"
PER_PAGE=20
PAGE=1

IFS='/' read -r ORG IMAGE <<< "$IMAGE_FULL"

while :; do
  echo "::debug::Checking page $PAGE"
  response=$(gh api -H "Accept: application/vnd.github+json" \
    "/orgs/$ORG/packages/container/$IMAGE/versions?per_page=$PER_PAGE&page=$PAGE")

  cat $response

  id=$(echo "$response" | jq -r --arg TAG "$TAG" --arg ORG "$ORG" --arg IMAGE "$IMAGE" '
    .[] |
    select(
      .metadata.container.tags | index($TAG) and
      .package_html_url == ("https://github.com/orgs/" + $ORG + "/packages/container/package/" + $IMAGE)
    ) | .id' | head -n1)

  if [[ -n "$id" ]]; then
    echo "image_id=$id"
    exit 0
  fi

  count=$(echo "$response" | jq 'length')
  if (( count < PER_PAGE )); then
    echo "::error::Tag '$TAG' not found for image '$IMAGE_FULL'"
    exit 1
  fi

  ((PAGE++))
done
