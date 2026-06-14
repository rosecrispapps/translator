# AGENTS.md

## Project overview

`translator` is an npm **workspaces monorepo** with two packages:

- `packages/server` — Express + TypeScript REST API (port **3001**).
- `packages/client` — React + Vite + TypeScript UI (port **5173**).

Translation runs through a pluggable provider. The default **offline** provider
uses a bundled dictionary (`packages/server/src/dictionary.ts`) with English as
the pivot language, so the app works with no network access or API keys.

## Common commands

Run from the repo root (see `README.md` and root `package.json` `scripts`):

- Install: `npm install`
- Dev (both services): `npm run dev` (or `npm run dev:server` / `npm run dev:client`)
- Lint: `npm run lint`
- Test: `npm test` (server-only vitest suite)
- Build: `npm run build`

## Cursor Cloud specific instructions

- The update script only runs `npm install`. Start services yourself with
  `npm run dev` (root); it launches the API and the Vite UI together via
  `concurrently`. Do not add service startup to the update script.
- The Vite dev server proxies `/api` → `http://localhost:3001`, so always start
  the server too (or use `npm run dev`) when testing the UI end-to-end.
- The server runs under `tsx watch`, so edits to `packages/server/src` hot-reload
  automatically; no manual restart is needed after code changes.
- No secrets are required. The default offline provider is fully self-contained.
  To exercise the real online provider, set `TRANSLATION_PROVIDER=mymemory`
  (requires outbound network); this is optional and not needed for tests.
- The offline dictionary covers a small curated word/phrase set; unknown tokens
  pass through unchanged by design, so partial translations are expected for
  text outside the dictionary.
