#!/usr/bin/env bash
# Explicit owner operation for the standalone layer, never called by legal skills.
set -euo pipefail
visibility=private
case "${1:-}" in
 '') ;;
 --public) visibility=public ;;
 *) echo 'Usage: bash scripts/publish_independent.sh [--public]' >&2; exit 2 ;;
esac
[[ $# -le 1 ]] || exit 2
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"
command -v gh >/dev/null || { echo 'GitHub CLI is required.' >&2; exit 2; }
command -v git >/dev/null || exit 2
python3 scripts/validate_br.py
python3 - <<'PY'
import json
from pathlib import Path
lock=json.loads(Path('upstream.lock.json').read_text())
if not lock['mode'].startswith('standalone-br-overlay'):
    raise SystemExit('Use publish_github.sh for an assembled upstream derivative.')
PY
gh auth status --hostname github.com >/dev/null
[[ "$(gh api user --jq .login)" == 'oalexandrebelo' ]] || { echo 'Wrong authenticated account.' >&2; exit 2; }
[[ "$(git branch --show-current)" == 'main' ]] || { echo 'Expected main branch.' >&2; exit 2; }
[[ -z "$(git status --porcelain)" ]] || { echo 'Review and commit changes before publication.' >&2; exit 2; }
if git remote get-url origin >/dev/null 2>&1; then
 echo 'An origin already exists; stopped to avoid changing an existing repository.' >&2; exit 2
fi
# Fails rather than replacing an existing repository; no force or protection change.
gh repo create oalexandrebelo/claude-for-legal-br "--$visibility" --source . --remote origin --push \
 --description 'Claude para Jurídico: camada BR independente, evidências, privacidade e documentação React Flow. Não oficial Anthropic.'
gh repo view oalexandrebelo/claude-for-legal-br --json nameWithOwner,url,visibility
