#!/usr/bin/env bash
# Explicitly invoked by the repository owner; never called by a legal skill.
# Default PRIVATE. --public is an intentional publication decision.
set -euo pipefail
visibility=private
case "${1:-}" in
  '') ;;
  --public) visibility=public ;;
  *) printf '%s\n' 'Usage: bash scripts/publish_github.sh [--public]' >&2; exit 2 ;;
esac
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"
command -v gh >/dev/null || { echo 'GitHub CLI (gh) is required.' >&2; exit 2; }
command -v git >/dev/null || exit 2
python3 scripts/validate_br.py
python3 - <<'PY'
import json,subprocess
lock=json.load(open('upstream.lock.json'))
if lock['mode']!='pinned-upstream-with-br-overlay':
    raise SystemExit('Assemble the upstream clone before publishing this derivative.')
subprocess.run(['git','merge-base','--is-ancestor',lock['commit'],'HEAD'],check=True)
PY
gh auth status --hostname github.com >/dev/null
login="$(gh api user --jq .login)"
[[ "$login" == 'oalexandrebelo' ]] || { echo 'Wrong authenticated owner; publication stopped.' >&2; exit 2; }
[[ "$(git branch --show-current)" == 'main' ]] || { echo 'Use the assembled main branch.' >&2; exit 2; }
[[ -z "$(git status --porcelain)" ]] || { echo 'Review and commit the BR changes before publication.' >&2; exit 2; }
if git remote get-url origin >/dev/null 2>&1; then
  echo 'An origin remote already exists; publication stopped to avoid overwriting a repository.' >&2
  exit 2
fi
# gh repo create fails rather than replacing an existing repository. No force push.
# Local auth stays with gh; this script never prints or stores an access token.
gh repo create 'oalexandrebelo/claude-for-legal-br' "--$visibility" \
  --description 'Camada brasileira independente: skills jurídicas, evidências e governança temporal. Não oficial Anthropic.' \
  --source . --remote origin --push
gh repo view 'oalexandrebelo/claude-for-legal-br' --json nameWithOwner,url,visibility
