# IDAT-GPT rebrand tools

Re-run these after each merge from upstream `onyx-dot-app/onyx`.

1. `python tools/rebrand/rebrand.py` — replace the standalone product name "Onyx" with
   "IDAT-GPT" in `web/src` string literals and the i18n message files. Vendor references
   ("Powered by Onyx", "Onyx Cloud", "Onyx team", ...) stay. Identifiers are not touched.
2. `cd web && SCRATCH=/tmp bun ../tools/rebrand/gen_assets.mjs` — render `web/public/logo.svg`
   to the PNG assets in `web/public` and `backend/static/images`.
3. `SCRATCH=/tmp python tools/rebrand/make_ico.py web/public/onyx.ico` — build the favicon.

The React logo lives in `web/lib/opal/src/logos/idat-gpt-*.tsx`; the default product name in
`web/src/lib/constants.ts` (`DEFAULT_APPLICATION_NAME`) and
`backend/onyx/configs/constants.py` (`ONYX_DEFAULT_APPLICATION_NAME`).
