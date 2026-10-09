# Web Solution Sydney

Static multi-page website, with a prepared Cloudflare Pages email endpoint. Public assets are in `dist`.

## Editing and validation

`content.md` preserves the original strategy and copy. `seo-pages.json` is the current keyword-to-page map and contains the revised headings and service content used by `build.py`. Its keyword metrics are explicitly unverified because Semrush reported insufficient API units on 12 September 2026. Do not label any cluster low competition until it is measured.

Edit those sources or `privacy.md`, then run `python3 build.py`. CSS and JavaScript are maintained in `dist`. Run `node --check dist/site.js` and `node --test tests/enquiry.test.mjs` after relevant changes. `seo-validation.json` records the latest static route and metadata checks; it is not a Google indexing or performance report.

## Current review hosting

The registered Sites project remains static and owner-private. The deployed archive includes `dist` only. Its contact form explicitly opens an email draft; it does not claim server delivery. The direct-send endpoint is prepared in source for Cloudflare Pages and is not active on the Sites review URL. Canonical URLs and sitemap target `https://websolutionsydney.com.au` for the eventual public-domain launch.

## Prepared Cloudflare Pages deployment

The repository includes `functions/api/enquiry.js`, `server/enquiry.mjs`, `wrangler.toml` and `.dev.vars.example`. There are no production API credentials in source. Use a Pages deployment with Functions support (Wrangler or Git integration), not dashboard drag-and-drop of `dist`, to activate the endpoint. See [Cloudflare's Direct Upload documentation](https://developers.cloudflare.com/pages/get-started/direct-upload/).

Set `ENQUIRY_TO` to the owner's confirmed inbox and `ENQUIRY_FROM` to an address on a domain verified in Resend. Configure `RESEND_API_KEY` and `TURNSTILE_SECRET_KEY` as secrets, and `TURNSTILE_SITE_KEY` as the public widget key. The endpoint accepts the main `websolutionsydney.com.au` domain, its subdomains, and this project's Pages hostname; the Turnstile widget must allow each hostname where the form is used. Do not paste secret values into chat or commit them.

The frontend starts in email-draft mode. It enables direct sending only when the endpoint is available and configured for the current origin and the Turnstile script loads. The server requires the approved origin, bounded valid input and a verified Turnstile token for that hostname and action. It sends plain text to the configured recipient, uses the visitor address only as reply-to and uses an idempotency key. It reports provider acceptance only after Resend returns a successful response with an ID.

Automated tests use mocked providers and send no email. Real widget behaviour and inbox receipt still need end-to-end testing on the chosen public host after account configuration. Provider acceptance alone is not proof of inbox delivery.

## Migration and measurement

The observed old `/packages` route has a prepared redirect to `/website-packages/`. Existing `/about` and `/contact` correspond to the new static directories, subject to hosting slash normalization. The redesign now includes `/portfolio/` with the public project references and `/designs/` with the catalogue directions. Old `/services` and `/pay` still require an owner-reviewed migration decision; do not perform a DNS cutover until any live payment workflow has been addressed.

No analytics script or Search Console verification has been added without account details. Public crawl access, HTTPS, redirects, form receipt, analytics events and Search Console submission remain launch checks. The privacy notice describes the prepared integrations and must be reviewed against the final hosting/email arrangement.
