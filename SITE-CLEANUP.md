# Site clean-up recommendations

Review of [cowboy-disco-party.vercel.app](https://cowboy-disco-party.vercel.app) and this repo. The site is a single-event landing page plus party-night tools, but **23 HTML pages** and a guest nav that still pointed at host/print tools made it feel like a control panel.

This PR applies the guest-facing fixes (P0). Everything below is the remaining punch list.

## What this PR already does

- Guest nav on `index.html` now matches the other guest pages: The Party, Schedule, Gallery, Vote, Ice Breakers, plus a guest-only Info menu.
- Host/print links removed from the homepage Info dropdown, menu, location, and QR section.
- Footer host strip reduced to a single **Hosts** link (`host.html`).
- Vote page no longer links guests to `numbers.html`.
- `robots.txt` + `noindex` on leftover print pages (`signs.html`, `qr.html`).
- Ice breakers no longer load `main.js` / `config.js`.
- Gallery Admin added to the host dashboard quick links.

## Page map

| Keep for guests | Keep for hosts (unlink from guests) | Merge or retire later |
|-----------------|-------------------------------------|------------------------|
| `index.html` | `host.html` (hub) | `party-night.html` → fold into host |
| `gallery.html` | `admin.html` | `print-pack.html` → fold into party-kit |
| `vote.html` | `poll-results.html` | `mobile-test.html` → fold into host checklist |
| `ice-breaker.html` | `plan.html` | |
| `poll.html` | `party-kit.html` + print leaves | |
| `slideshow.html` (TV) | `invite.html` | |
| `404.html` | `signs.html`, `qr.html`, `qr-pack.html`, `lookbook.html`, `numbers.html`, `invite-card.html`, `schedule-card.html` | |

## Remaining recommendations

### P1 — Host surface area

1. **Merge `party-night.html` into `host.html`** as a “Run of show” block. It repeats the host checklist.
2. **Merge `print-pack.html` into `party-kit.html`.** Print pack is a thin index of the same signs, QR, labels, and numbers.
3. **Keep print leaf pages** (`signs`, `qr`, `qr-pack`, `lookbook`, `numbers`, `invite-card`, `schedule-card`) but reach them only from `host.html` / `party-kit.html`.
4. **Fold `mobile-test.html`** into the host checklist (or keep it, but only as a host quick link — already true).

### P2 — Homepage weight

`index.html` is ~980 lines. The guest path does not need all of it.

5. **Dress-code lookbook** (~450 lines) is duplicated in `lookbook.html`. Keep the six looks on the homepage; generate both from `scripts/build-lookbook.py` (already marked `LOOKBOOK:START/END`) and avoid hand-editing twice.
6. **`#moments` and `#party-night` overlap** — both send guests to gallery / vote / ice breakers / schedule. Consider dropping one card grid or making Moments photography-only.
7. **Hero has five actions** (Partiful, Directions, Calendar, Learn More, Share). Fine for invites; drop “Learn More” if the fold still feels busy.
8. **`#date-tbd` is leftover markup.** Date is set (`PARTY_DATE_TBD: false`). Rename or remove the block so TBD mode is not implied.
9. **Empty features are correctly hidden** (`SPOTIFY_PLAYLIST_URL`, `AMBIENT_AUDIO_URL`). Either add the playlist or delete the unused DOM when you are sure you will not use them.

### P3 — Weight and duplication

10. Guest pages load ~106 KB of CSS (`styles.css` + `premium.css`). Deduplicate the `.js-motion .reveal` rules in `premium.css` (defined twice).
11. Drop `js/premium.js` from print-only pages unless a print toolbar depends on it.
12. `scripts/sync-guest-chrome.py` only syncs footers and is already out of date vs `index.html`. Either teach it the header nav too, or replace copy-pasted chrome with a small include/build step.
13. Party date/address is hardcoded in 15+ HTML files. `scripts/apply-party-date.py` exists — run it whenever the date moves, or generate those strings from `js/config.js` at build time.

### P4 — Assets, scripts, docs

14. **Unused (or unused-on-site) assets to delete or wire up:**
    - `assets/editorial-dancefloor.jpg` (site uses `editorial-dance.jpg`)
    - `assets/poster-og.jpg` (OG uses `og-card.jpg`)
    - `assets/drink-list.*` (cached in `sw.js`, never shown; menu uses `editorial-cocktails.jpg`)
15. Remove `drink-list.*` from `sw.js` if you delete those files. Bump the cache name (`cdp-v46`).
16. **Migration scripts** that look finished: `apply-premium-sitewide.py`, `apply-brand-snippets.py`, `update-nav-brand.py`, `update-favicon.py`. Archive or document them so they are not mistaken for the current pipeline.
17. Document `scripts/remove-gallery-entries.js` and `scripts/refresh-gallery.js` in the README ops section, or move them next to the other Blob tools.
18. README still describes `PARTY_DATE_TBD: true` as the default. Update it to match `js/config.js`.

### P5 — Platform

19. There is no `vercel.json`. Optional: map unknown paths to `404.html`, cache `/assets/*`, and add basic security headers. Vercel already serves `404.html` by convention.
20. Host/admin HTML is in the service worker cache. That is convenient offline on party night; it is not a secret (admin is code-gated). Leave it unless you want a slimmer guest cache.

## Suggested end state

Guests see five pages plus the homepage: **party info, gallery, vote, ice breakers, poll**, and the TV slideshow. Hosts bookmark **`/host.html`**, which unlocks planning, prints, moderation, and run-of-show.

That continues #14 (venue signs) and #18 (lookbook) — keep host tools, just stop advertising them on the invite site.
