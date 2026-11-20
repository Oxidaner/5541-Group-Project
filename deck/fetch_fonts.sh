#!/bin/bash
set -e
cd "$(dirname "$0")"
mkdir -p fonts
cd fonts
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
dl() {
  local fam="$1"; local file="$2"
  curl -sS -m 15 -A "$UA" "https://fonts.googleapis.com/css2?family=${fam}&display=swap" -o "$file.css"
  grep -o 'https://[^)]*\.woff2' "$file.css" | sort -u > "$file.urls"
  local i=0
  while read -r u; do
    [ -z "$u" ] && continue
    curl -sS -m 15 -A "$UA" -o "$(basename "$u")" "$u" || true
    i=$((i+1))
  done < "$file.urls"
  echo "$fam -> $i files"
}
dl "Space+Grotesk:wght@400;500;600;700" space
dl "Inter:wght@400;500;600" inter
dl "JetBrains+Mono:wght@400;500;700" mono
dl "Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700" fraunces
ls -la
