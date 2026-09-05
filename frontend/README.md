# ComptaRAG frontend

Angular app for [ComptaRAG](../README.md), an agentic RAG assistant for accounting and financial-law questions. This document covers the frontend specifically, for the project overview, backend, and Firebase setup, see the [root README](../README.md).

## Table of contents

1. [Stack](#1-stack)
2. [Getting started](#2-getting-started)
3. [Project structure](#3-project-structure)
4. [Theming](#4-theming)
5. [Responsive layout](#5-responsive-layout)
6. [Testing](#6-testing)
7. [Available scripts](#7-available-scripts)

## 1. Stack

Angular 21, standalone components and signals throughout, no `NgModule`. Styling is Sass with CSS custom properties for anything that needs to change at runtime (see [section 4](#4-theming)). Unit and integration tests run on Jest with Testing Library, end-to-end tests run on Playwright.

## 2. Getting started

```bash
npm install
npm start
```

The app comes up at `http://localhost:4200`. It expects the backend to be running and needs a Firebase web config filled in before anyone can sign in, both are covered in the [root README's getting started section](../README.md#4-getting-started).

## 3. Project structure

```
src/app/
  core/            Singletons: services, guards, interceptors, models. No UI.
  layout/          App shell: header, footer.
  shared/          Reusable, feature-agnostic pieces: components, directives, pipes.
  features/
    home/          Public landing page.
    auth/          Sign-in and sign-up.
    chat/          Chat shell, sidebar, message list, composer.
    account/       Profile modal.
    admin/         User role management.
  styles/          Design tokens: _variables.scss, _themes.scss, _mixins.scss.
```

Each feature is self-contained: routes, components, and any feature-specific services live together under `features/<name>/`. Anything shared across features, such as the modal, button, and role-badge components, lives under `shared/components/`.

## 4. Theming

The app supports light, dark, and system themes, controlled by `core/services/theme.service.ts` and toggled from the switch in the header, which is visible whether or not you are signed in.

Colors, shadows, and glass-panel tints are defined as CSS custom properties in `styles/_themes.scss`, set on `:root` for light and on `html[data-theme='dark']` for dark, so switching themes needs no recompilation. Spacing, radii, fonts, and easing curves stay as plain Sass variables in `styles/_variables.scss`, since they do not change between themes.

Where a color needs an alpha-blended tint (for hover states, subtle backgrounds, and so on), use the `tint($color, $percent)` helper in `styles/_mixins.scss` rather than `rgba()`, since `rgba()` cannot take a CSS custom property as its color argument.

`ThemeService` applies `data-theme` to `<html>` directly at each mutation point (on construction, on a `prefers-color-scheme` change, and when the user picks a theme), rather than through an `effect()`, which keeps it synchronous and avoids timing issues under Angular's zoneless change detection in tests.

## 5. Responsive layout

Breakpoints live in `styles/_variables.scss` (`$breakpoint-sm: 576px`, `$breakpoint-md: 768px`, `$breakpoint-lg: 1024px`), and `styles/_mixins.scss` provides a `respond-above($breakpoint)` mixin for `min-width` queries. Most component-level responsive rules are written mobile-first with `max-width` media queries directly in the component's stylesheet.

Two patterns worth knowing about if you are extending the UI:

- **Chat sidebar**: on desktop it is a permanent column that can collapse to a narrow icon rail. Below `$breakpoint-md` it instead becomes an off-canvas drawer with a backdrop, opened with the hamburger button in the chat view and closed by selecting a chat, starting a new one, tapping the backdrop, or pressing Escape.
- **Modal**: below `$breakpoint-sm` it switches from a centered floating card to a bottom sheet anchored to the viewport's bottom edge, with squared-off bottom corners and tighter padding.

Form inputs (`login`, `profile-modal`, the chat composer) hold their font size at 16px or above below `$breakpoint-sm`. Below that size, iOS Safari zooms the whole viewport in when a field gains focus, keeping every input at or above that threshold avoids the jump.

## 6. Testing

```bash
npm test               # unit + integration (Jest)
npm run test:unit       # unit only
npm run test:integration # integration only
npm run test:coverage   # with coverage report
npm run e2e              # end-to-end (Playwright, needs the backend and a real Firebase project running)
```

Unit and integration tests live under `tests/unit/` and `tests/integration/`, mirroring the `src/app/` structure, and run against a mocked backend. End-to-end tests live under `tests/e2e/` and drive a real running app against `http://localhost:4200`, they are not part of CI since they need live Firebase and backend credentials, run them locally when you need to check a full user flow.

## 7. Available scripts

| Script | What it does |
| --- | --- |
| `npm start` | Dev server at `http://localhost:4200` |
| `npm run build` | Development build |
| `npm run build:prod` | Production build |
| `npm run lint` | ESLint (TypeScript and templates) |
| `npm run lint:fix` | ESLint with autofix |
| `npm run typecheck` | TypeScript, no emit |
| `npm run format` | Prettier, write |
| `npm run format:check` | Prettier, check only |
