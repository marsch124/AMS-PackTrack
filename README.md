# AMS PackTrack

An offline home-screen app (PWA) for following up on things ordered from Amazon and
everywhere else — from the confirmation mail all the way to the parcel in your hands.

**Live:** https://marsch124.github.io/AMS-PackTrack/

## The idea

1. Hand the confirmation mail to the app.
2. The app reads it — shop, items and their pictures, promised delivery date,
   delivery service, tracking number and the tracking link.
3. Tick each item off as it actually turns up, and keep your own follow-ups
   ("return the small one", "register the warranty") on the order.

## Two ways to get a mail in

- **Copy & paste** (the main road): in Mail, Select All → Copy, then paste into the
  app's dashed box. Pasting rich text is what carries the **product pictures** across.
- **A one-tap Apple Shortcut** from the mail's share sheet, which opens
  `index.html?add=<the mail as text>`. Faster, but iOS only hands a Shortcut plain
  text — so no pictures. The full recipe is inside the app under
  *Settings → The one-tap Shortcut*.

## What it reads

Shop (from the links in the mail), order number, order date, items + pictures,
total, promised delivery date or date range, delivery service — DHL, Deutsche Post,
Österreichische Post, DPD, GLS, Hermes, UPS, FedEx, PostNL, TNT, Amazon Logistics —
tracking number, and the tracking link straight out of the mail. German and English
mails, and German or ISO date formats.

Nothing is ever saved without showing what was found first, and every field is editable.

Send the **dispatch** mail the same way later: if the order number matches one you
already have, the app offers to fold it into that order instead of making a second one.

## Files

| file | what it is |
|---|---|
| `index.html` | the whole app — markup, styles, icons and logic |
| `service-worker.js` | offline cache; bump `CACHE` on every release |
| `version.json` | the version the app compares itself against for self-updating |
| `manifest.webmanifest` | home-screen install metadata |
| `tools/make_icons.py` | redraws the app icons (stdlib only, no dependencies) |

## Release checklist — all four must stay in sync

1. New entry at the **top** of `VERSIONLOG` in `index.html` (`[0].v` is the app version)
2. `version.json` set to the same version
3. `CACHE` bumped in `service-worker.js` (`ams-packtrack-vN`)
4. The in-app **"How this works"** guide updated if behaviour changed

## Your data

Everything lives in `localStorage` on the one device — nothing is synced or sent
anywhere. Settings → *Your data* holds export / copy / restore, plus the app's own
daily snapshots (the last 10) and a button that proves the safety net works with
real numbers.
