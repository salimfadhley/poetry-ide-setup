#!/usr/bin/env bash
set -euo pipefail

# Monitor the latest CI run for this repo using GitHub CLI.
# Usage: bash scripts/ci-watch.sh [owner/repo]

REPO="${1:-}"
if [ -z "$REPO" ]; then
  REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
fi

echo "Watching latest workflow run for $REPO ..."
gh run watch --repo "$REPO" --exit-status

