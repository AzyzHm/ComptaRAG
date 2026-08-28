#!/usr/bin/env bash
# Runs the same lint + format checks enforced in CI.
set -euo pipefail

echo "==> ESLint"
npx eslint "src/**/*.ts" "tests/**/*.ts"

echo "==> Prettier (check)"
npx prettier --check "src/**/*.{ts,html,scss}" "tests/**/*.ts"
