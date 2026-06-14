# translator

A simple full-stack text translator. It ships with an offline dictionary-based
translation engine (no API keys required) and an optional online provider.

- **Server** (`packages/server`): Express + TypeScript REST API.
- **Client** (`packages/client`): React + Vite + TypeScript UI.

Supported languages: English, Spanish, French, German.

## Requirements

- Node.js >= 20
- npm >= 10

## Setup

```bash
npm install
```

This is an npm workspaces monorepo; the single install at the repo root installs
dependencies for both packages.

## Development

Run the API and the web UI together:

```bash
npm run dev
```

- API: http://localhost:3001
- Web UI: http://localhost:5173 (proxies `/api` to the server)

Run them individually if you prefer:

```bash
npm run dev:server
npm run dev:client
```

## Scripts

| Command         | Description                                  |
| --------------- | -------------------------------------------- |
| `npm run dev`   | Run server + client in watch mode            |
| `npm run build` | Type-check and build both packages           |
| `npm run lint`  | Lint both packages                           |
| `npm test`      | Run the server test suite (vitest)           |

## API

- `GET /api/health` → `{ "status": "ok" }`
- `GET /api/languages` → list of supported languages
- `POST /api/translate` → body `{ "text": "hello", "from": "en", "to": "es" }`

Example:

```bash
curl -s -X POST http://localhost:3001/api/translate \
  -H 'Content-Type: application/json' \
  -d '{"text":"hello world","from":"en","to":"es"}'
# {"translatedText":"hola mundo","from":"en","to":"es","provider":"offline"}
```

## Translation providers

By default the server uses the bundled **offline** dictionary (English as the
pivot language), so it works with no network access or API keys.

To use the free online MyMemory provider instead, set:

```bash
TRANSLATION_PROVIDER=mymemory npm run dev:server
```
