#!/usr/bin/env bash
set -euo pipefail

echo "==> Unit + integration tests (Jest)"
npx jest --coverage

echo "==> End-to-end tests (Playwright)"
npx playwright test
