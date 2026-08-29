#!/usr/bin/env bash
set -euo pipefail

echo "==> ESLint"
npx eslint "src/**/*.ts" "tests/**/*.ts"

echo "==> Prettier (check)"
npx prettier --check "src/**/*.{ts,html,scss}" "tests/**/*.ts"
