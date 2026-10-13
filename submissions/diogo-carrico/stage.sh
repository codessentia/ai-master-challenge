#!/usr/bin/env bash
# Stage this submission despite the upstream rule that ignores submissions/.
# Force-adds new and changed files under this folder, skipping anything matched by ./.gitignore,
# then refuses to continue if a staged path falls outside the folder or looks like a secret.
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
root="$(git -C "$here" rev-parse --show-toplevel)"
# Ask git for the folder's repo-relative path: on Windows, pwd (/d/...) and git (D:/...) spell paths differently.
rel="$(git -C "$here" rev-parse --show-prefix)"
rel="${rel%/}"
cd "$root"

mapfile -t files < <(git ls-files --others --modified --exclude-from="$rel/.gitignore" -- "$rel")
if ((${#files[@]})); then
  git add -f -- "${files[@]}"
fi

outside=$(git diff --cached --name-only | grep -v "^$rel/" || true)
if [[ -n "$outside" ]]; then
  echo "Refusing: staged files outside $rel/ (G4 rejects PRs that touch other files):" >&2
  echo "$outside" >&2
  exit 1
fi

secrets=$(git diff --cached -U0 | grep -nE '(sk-[A-Za-z0-9_-]{20,}|sk-ant-[A-Za-z0-9_-]{20,}|AIza[0-9A-Za-z_-]{35}|KGAT_[0-9A-Za-z]{16,}|"key"\s*:\s*"[0-9a-f]{32}")' || true)
if [[ -n "$secrets" ]]; then
  echo "Refusing: something that looks like an API key is staged:" >&2
  echo "$secrets" >&2
  exit 1
fi

git diff --cached --stat
