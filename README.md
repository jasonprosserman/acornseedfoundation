# Acorn Seed Foundation — website

The public site for [acornseedfoundation.com](https://acornseedfoundation.com), hosted on GitHub Pages.

## How it works

`index.html` is the entire site — a single self-contained file. All CSS lives in one
`<style>` block and every image is base64-inlined, so there are no external asset
files to keep in sync. The only outbound requests are to Google Fonts and to
partner websites linked from the page.

To edit the site, edit `index.html`. Committing to `main` publishes it
automatically, usually within a minute.

## Local preview

Open `index.html` in a browser. That's it — no build step, no dependencies.

## Deployment

GitHub Pages serves `main` from the repository root. The `CNAME` file binds the
custom domain; do not delete it, or the site will fall back to the
`*.github.io` address.

## source-assets/

Original PNGs for the foundation logo and partner logos. These are **not** used by
the live page — they're already inlined into `index.html`. They're kept here so
future edits don't require hunting down the originals.

## Notes

- The filename must stay lowercase `index.html`. GitHub Pages is case-sensitive
  and will not serve `Index.html` as the site root.
- The contact form posts to Formspree (`https://formspree.io/f/xwleqljo`), which
  forwards submissions by email. It previously used `action="mailto:"`, which
  silently failed for mobile and webmail visitors. Two hidden fields support this:
  `_subject` sets the notification subject line, and `_gotcha` is a honeypot that
  bots fill in and humans never see — Formspree discards anything with it set.
  The free tier allows roughly 50 submissions per month.
- The form submits via `fetch()` so the visitor stays on the page and sees an
  inline confirmation, rather than being redirected to Formspree's own thank-you
  page (custom redirects are a paid Formspree feature; Ajax submission is not).
  If JavaScript is unavailable the form still posts normally and falls back to
  Formspree's hosted confirmation — nothing is lost, it's just less elegant.
  On failure the visitor is shown a direct mailto: fallback and their typed
  message is deliberately *not* cleared.
- DNS is managed at Squarespace (the registrar). Google Workspace handles email
  for this domain — do not remove the MX, SPF, DKIM, or DMARC records.
