#!/usr/bin/env sh
# Deploy Submission Desk to Cloudflare Pages from your machine.
#
#   1. cp .env.example .env   (once)
#   2. paste your CLOUDFLARE_API_TOKEN into .env
#   3. ./tools/deploy.sh
#
# If .env has no API token but you have run `wrangler login`, the OAuth
# session is used instead. Account ID comes from .env or your wrangler login.
set -eu

ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"

# Load .env if present (auto-export every assignment).
if [ -f .env ]; then
  set -a
  . ./.env
  set +a
fi

# An empty token would break the OAuth fallback — drop it if blank.
if [ -z "${CLOUDFLARE_API_TOKEN:-}" ]; then
  unset CLOUDFLARE_API_TOKEN 2>/dev/null || true
  echo "No CLOUDFLARE_API_TOKEN in .env — falling back to your wrangler login." >&2
fi

PROJECT=${CF_PAGES_PROJECT:-submission-desk}
WRANGLER="npx --yes wrangler@latest"

# Assemble a clean two-file static site.
rm -rf dist
mkdir -p dist/zh-TW
cp index.html dist/index.html
cp zh-TW/index.html dist/zh-TW/index.html

# Create the Pages project on first run; ignore "already exists".
$WRANGLER pages project create "$PROJECT" --production-branch=main >/dev/null 2>&1 \
  || echo "Pages project '$PROJECT' already exists (or creation skipped)."

# Deploy the production branch.
$WRANGLER pages deploy dist --project-name="$PROJECT" --branch=main
