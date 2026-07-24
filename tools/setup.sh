#!/usr/bin/env sh
# Replace the YOUR-USERNAME placeholders with your GitHub account.
#   ./tools/setup.sh your-github-username
set -eu

if [ $# -ne 1 ]; then
  echo "usage: $0 <github-username>" >&2
  exit 1
fi

USER=$1
FILES="README.md README.zh-TW.md CONTRIBUTING.md CITATION.cff"

for f in $FILES; do
  [ -f "$f" ] || continue
  # BSD and GNU sed disagree on -i; write via temp file instead.
  sed "s/YOUR-USERNAME/$USER/g" "$f" > "$f.tmp" && mv "$f.tmp" "$f"
  echo "updated $f"
done

echo
echo "Done. Next:"
echo "  git add -A && git commit -m 'Set repository URLs'"
echo "  git remote add origin https://github.com/$USER/submission-desk.git"
echo "  git push -u origin main"
echo
echo "Then enable Settings -> Pages -> Source: GitHub Actions."
