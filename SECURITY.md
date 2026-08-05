# Security Policy

## Reporting a vulnerability

ComptaRAG is under active development, and we take security issues seriously, especially given the upcoming authentication and user-management components.

If you discover a serious security vulnerability (e.g. authentication bypass, data exposure, injection vulnerability, credential leakage, or anything that could compromise users or the system), **please do not open a public GitHub issue**. Public issues are visible to everyone, including anyone who might exploit the vulnerability before it's fixed.

Instead, report it privately by emailing the maintainer:

📧 **elhammemi001@gmail.com**

When reporting, please include as much of the following as you can:

- A clear description of the vulnerability and its potential impact.
- Steps to reproduce it (or a proof of concept, if you have one).
- The affected component/service (frontend, FastAPI RAG service, Spring auth service, etc.) and version/commit, if known.
- Any suggested mitigation, if you have one in mind.

## What to expect

- We'll acknowledge your report as soon as possible.
- We'll investigate and keep you updated as we work on a fix.
- Once a fix is available, we'll coordinate with you on responsible disclosure timing before any public write-up, if applicable.

## Scope

This project is currently in a dev/pre-release phase, some components (auth service, Firebase integration, etc.) are still being built. If you're testing early builds, please treat any staging/test deployment credentials as private and avoid testing against services you don't own.

Thank you for helping keep ComptaRAG and its future users safe.