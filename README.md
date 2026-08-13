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
- The contact form uses `action="mailto:"`, which relies on the visitor having a
  desktop mail client configured. It does not work for most mobile or webmail
  users. Worth replacing with a form service if inbound contact matters.
- DNS is managed at Squarespace (the registrar). Google Workspace handles email
  for this domain — do not remove the MX, SPF, DKIM, or DMARC records.
