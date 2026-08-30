# Contributing to ComptaRAG

Thanks for your interest in contributing! ComptaRAG is still under active development, so check open issues and the `main` branch before starting significant work, to avoid overlapping with in-progress changes.

## Before you start

- Search [existing issues](../../issues) to see if your bug, idea, or question has already been raised.
- For anything non-trivial (a new feature, a refactor, a change to the pipeline), open an issue first to discuss the approach before writing code. It saves everyone rework.
- Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) in all interactions.

## Reporting a bug or requesting something

Click "New Issue" on GitHub and pick the form that fits: bug report, feature request, or documentation. Each form walks you through the fields we need, area affected, description, repro steps for bugs, and so on.

## Reporting a security vulnerability

Do **not** open a public issue for security vulnerabilities. See [SECURITY.md](SECURITY.md) for how to report those privately.

## Submitting changes

1. Fork the repo and create a branch off `main`.
2. Keep pull requests focused: one bug fix or one feature per PR is much easier to review than a bundle of unrelated changes.
3. Fill out the PR template, what changed, why, and how you tested it, and link the issue it resolves, if any.
4. Be responsive to review feedback. This is a small project and reviews may take a little time, but we'll get there.

## Code style

Backend: `ruff check .`, `ruff format --check .`, and `mypy .`, run from `backend/`. Frontend: `npm run lint`, `npm run format:check`, and `npm run typecheck`, run from `frontend/`. All four run in CI on every push and pull request to `main`. Match the conventions already used in the file you're editing, and keep changes readable and well-commented where the logic isn't obvious.

## Questions?

If something is unclear, open an issue with the `[Docs]` prefix rather than guessing, it also helps us know what to document next.