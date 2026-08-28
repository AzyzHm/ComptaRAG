#!/usr/bin/env bash
# Runs the full test suite with coverage, same as CI.
set -euo pipefail

echo "==> Unit + integration tests (Jest)"
npx jest --coverage

echo "==> End-to-end tests (Playwright)"
npx playwright test
