# Cowboy Disco Party

Event website for the Cowboy Disco Party. Static multi-page site (plain HTML/CSS/vanilla JS)
plus a small set of Vercel serverless functions in `api/` backed by Vercel Blob storage.
See `README.md` for the product overview, page list, and standard commands.

## Cursor Cloud specific instructions

### What runs, and what needs secrets

- **Static site (primary dev workflow, no secrets):** serve the repo root and open
  `http://localhost:3000`. Use `npx --yes serve .` — the `--yes` avoids the interactive
  "Ok to proceed?" prompt `npx` shows the first time it fetches `serve` (which is not a
  project dependency). `python3 -m http.server 3000` also works. `serve` 301-redirects
  `/foo.html` to the clean URL `/foo`; browsers follow it, so pages work either way.
- **API routes (`/api/*`) need `vercel dev`, which is blocked without secrets.** `vercel dev`
  requires interactive Vercel authentication (device login) to start, and the functions call
  Vercel Blob, which needs a `BLOB_READ_WRITE_TOKEN` from a linked Vercel Blob store. Without
  a Vercel login + Blob token you cannot exercise vote/poll/gallery submission locally. The
  plain static server does not run `/api/*` (returns 404), which is expected.
- Some API GETs degrade gracefully: `GET /api/vote` and `GET /api/poll` catch Blob errors and
  return empty results, but all writes (`POST /api/vote`, `POST /api/poll`, gallery upload)
  require a working Blob token.
- `POST /api/vote` returns 403 once past `VOTE_CLOSE_TIME` (env var; defaults to
  `2026-09-19T21:00:00-07:00` in `api/_lib/admin.js`). Host/admin pages
  (`admin.html`, `poll-results.html`, `plan.html`) require `GALLERY_ADMIN_CODE` to be set.

### Lint / test / build

- There is **no linter, no automated test suite, and no build step** — it is a zero-config
  Vercel static site (no `vercel.json`). Do not look for `npm run build`/`test`.
- Closest verification tool: `SITE_URL=http://localhost:3000 python3 scripts/smoke-test.py`
  (Python stdlib only). Against the static server all 35 pages/assets return 200; the 4
  `/api/*` checks fail because functions need `vercel dev` + Blob (expected). Without
  `SITE_URL` it targets the production URL.

### Optional Python asset toolchain

- `scripts/*.py` that regenerate committed assets (poster, QR codes, signs, lookbook, planning
  workbook) need `Pillow`, `qrcode`, `openpyxl`, and optionally `fpdf`. These are **not
  installed by default and are not needed to run or develop the site** — the generated assets
  are already committed under `assets/`. Install them only if you need to regenerate assets.
