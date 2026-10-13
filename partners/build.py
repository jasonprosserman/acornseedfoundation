#!/usr/bin/env python3
"""Generate the partner profile pages from partners/partners.json.

    python3 partners/build.py

Writes partners/<slug>/index.html for each partner and partners/index.html
(the directory of all partners). No dependencies beyond the standard library.
Logos are read from source-assets/partner-logos/transparent/ (backgrounds stripped) and inlined as base64, the
same way index.html inlines them, so each page stays self-contained. The
shared stylesheet partners/partner.css is copied from the design-system
<style> block in index.html plus the page scaffolding at the bottom of this
file, so a retune of the tokens in index.html flows through on the next build.

The pages are plain HTML. If you'd rather edit one by hand, that works too;
just don't run this script afterwards without copying the change back into
partners.json.
"""
import base64
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PARTNERS = ROOT / "partners"
LOGOS = ROOT / "source-assets" / "partner-logos" / "transparent"
INDEX = ROOT / "index.html"

# slug -> logo file in source-assets/partner-logos
LOGO_FILES = {
    "black-creek-community-farm": "black_creek_community_farm.png",
    "community-justice-collective": "cjc.png",
    "homeless-connect-toronto": "hct.png",
    "maggies-toronto-sex-workers-action-project": "maggies.png",
    "the-reading-partnership": "trp.png",
    "toronto-alliance-to-end-homelessness": "taeh.png",
    "toronto-black-farmers": "toronto_black_farmers.png",
    "thunder-woman-healing-lodge-society": "thunder_woman.png",
    "wanasah": "wanasah.png",
    "enagb-indigenous-youth-agency": "enagb.png",
    "black-esteem": "black_esteem.png",
    "mind-program": "mind.png",
    "oasis-youth-care-programs": "oasis_youth_care.png",
    "power-to-girls-foundation": "power_to_girls.png",
    "sawubona-africentric-circle-of-support": "sawubona.png",
}


def esc(s):
    return html.escape(s, quote=True)


def data_uri(path):
    b = path.read_bytes()
    return "data:image/png;base64," + base64.b64encode(b).decode("ascii")


def asf_logo():
    """The foundation wordmark, lifted from index.html so the two stay identical."""
    src = INDEX.read_text(encoding="utf-8")
    m = re.search(r'<a class="nav-brand"[^>]*><img src="([^"]+)"', src)
    return m.group(1)


def system_css():
    src = INDEX.read_text(encoding="utf-8")
    return re.search(r"<style>(.*?)</style>", src, re.S).group(1)


def initials(name):
    words = [w for w in re.sub(r"[^A-Za-z ]", "", name).split() if w.lower() not in ("the", "of", "to", "and")]
    return "".join(w[0] for w in words[:2]).upper() or "AS"


def nav(logo):
    return f"""<nav class="nav" data-theme="light">
  <div class="wrap">
    <a class="nav-brand" href="/" aria-label="Acorn Seed Foundation home"><img src="{logo}" alt="Acorn Seed Foundation" /></a>
    <div class="nav-links">
      <a href="/#mission">About Us</a>
      <a href="/#how-we-work">Approach</a>
      <a href="/partners/" aria-current="page">Partners</a>
      <a href="/#contact">Contact</a>
    </div>
  </div>
</nav>"""


FOOTER = """<footer class="foot band-deep" data-theme="dark">
  <div class="wrap">
    <div class="foot-grid">
      <div>
        <div class="wordmark">Acorn Seed Foundation</div>
        <p>A GTA-based family foundation collaborating with communities to build a more resilient, equitable, and just society.</p>
      </div>
      <div>
        <div class="eyebrow">Registration</div>
        <p style="margin-top: var(--space-3)">Registered Canadian Charity<br />BN <a href="https://www.charitydata.ca/charity/acorn-seed-foundation/731980736RR0001/" target="_blank" rel="noopener">731980736RR0001</a></p>
        <p><a href="https://apps.cra-arc.gc.ca/ebci/hacc/srch/pub/dsplyBscSrch?request_locale=en" target="_blank" rel="noopener">CRA charity listing</a></p>
      </div>
    </div>
    <div class="foot-bottom meta">
      <span>&copy; <span id="year">2026</span> Acorn Seed Foundation</span>
      <span>Founded 2021</span>
    </div>
  </div>
</footer>"""

NAV_SCRIPT = """<script>
document.getElementById('year').textContent = new Date().getFullYear();
/* Nav theme follows the band behind it (same as index.html). */
(function () {
  const nav = document.querySelector('.nav');
  if (!nav) return;
  const sections = [...document.querySelectorAll('[data-theme]')].filter(el => el !== nav);
  let raf = null;
  function update() {
    raf = null;
    const y = nav.getBoundingClientRect().bottom + 1;
    for (const sec of sections) {
      const r = sec.getBoundingClientRect();
      if (r.top <= y && r.bottom > y) {
        const theme = sec.getAttribute('data-theme');
        if (nav.getAttribute('data-theme') !== theme) nav.setAttribute('data-theme', theme);
        return;
      }
    }
  }
  const schedule = () => { if (!raf) raf = requestAnimationFrame(update); };
  window.addEventListener('scroll', schedule, { passive: true });
  window.addEventListener('resize', schedule);
  update();
})();
</script>"""


def host(url):
    return re.sub(r"^https?://(www\.)?", "", url).rstrip("/")


def partner_page(p, logo_uri, asf):
    name = esc(p["name"])
    tags = "".join(f'<span class="tag tag-neutral">{esc(t)}</span>' for t in p["tags"])
    cohort = esc(p["cohort"]) if p["cohort"] else "Partner"

    facts = [("Partnership", esc(p["term"]) if p["term"] else "Multi-year, unrestricted")]
    if p["cohort"]:
        facts.insert(0, ("Cohort", esc(p["cohort"])))
    if p["led_by"]:
        facts.append(("Led by", esc(p["led_by"])))
    facts.append(("Website", f'<a href="{esc(p["url"])}" target="_blank" rel="noopener">{esc(host(p["url"]))}</a>'))
    facts_html = "".join(f'<div><div class="eyebrow">{k}</div><p>{v}</p></div>' for k, v in facts)

    offers = ""
    if p["offers"]:
        offers = '<ul class="offers">' + "".join(f"<li>{esc(o)}</li>" for o in p["offers"]) + "</ul>"

    serves = f'<p class="lede">{esc(p["serves"])}</p>' if p["serves"] else ""
    what = f'<p>{esc(p["what"])}</p>' if p["what"] else ""
    why = f'<p>{esc(p["why"])}</p>' if p["why"] else ""

    photo = ""
    if p["photo"]:
        photo = f'<figure class="photo plain"><img src="{esc(p["photo"])}" alt="{name}" /></figure>'

    quote = ""
    if p["quote"]["text"]:
        quote = f"""<section class="sec band-deep quote" data-theme="dark">
  <div class="wrap">
    <div class="eyebrow">In their words</div>
    <blockquote>
      <p>&ldquo;{esc(p["quote"]["text"])}&rdquo;</p>
      <footer class="meta"><span>{esc(p["quote"]["who"])}</span></footer>
    </blockquote>
  </div>
</section>"""

    funding = ""
    if p["funding"]:
        funding = f"""<div class="row">
      <div class="eyebrow">What the funding makes possible</div>
      <div><p class="lede">{esc(p["funding"])}</p></div>
    </div>"""

    numbers = ""
    if p["numbers"]:
        cells = "".join(f'<div><div class="num">{esc(n["value"])}</div><div class="eyebrow">{esc(n["label"])}</div></div>' for n in p["numbers"])
        numbers = f"""<div class="row stack">
      <div class="eyebrow">By the numbers</div>
      <div class="numbers">{cells}</div>
    </div>"""

    links = [f'<a class="btn btn-primary" href="{esc(p["url"])}" target="_blank" rel="noopener">Visit {esc(host(p["url"]))} &rarr;</a>']
    if p["donate"] and p["donate"] != p["url"]:
        links.append(f'<a class="btn btn-secondary" href="{esc(p["donate"])}" target="_blank" rel="noopener">Donate</a>')
    if p["contact"]:
        links.append(f'<a class="btn btn-secondary" href="mailto:{esc(p["contact"])}">{esc(p["contact"])}</a>')
    links_html = "".join(links)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{name} &middot; Acorn Seed Foundation</title>
<meta name="description" content="{esc(p["tagline"])}" />
<link rel="canonical" href="https://acornseedfoundation.com/partners/{p["slug"]}/" />
<meta property="og:title" content="{name} &middot; Acorn Seed Foundation partner" />
<meta property="og:description" content="{esc(p["tagline"])}" />
<link rel="stylesheet" href="../partner.css" />
</head>
<body>

{nav(asf)}

<section class="hero band" data-theme="light">
  <div class="wrap">
    <p class="crumbs meta"><a href="/partners/">Partners</a><span class="sep" aria-hidden="true"></span><span>{cohort}</span></p>
    <div class="hero-grid">
      <div>
        <h1>{name}</h1>
        <p class="lede">{esc(p["tagline"])}</p>
        <div class="partner-tags">{tags}</div>
      </div>
      <div class="hero-logo"><img src="{logo_uri}" alt="{esc(p.get("logo_alt") or name + " logo")}" data-initials="{initials(p["name"])}" /></div>
    </div>
    <div class="facts">{facts_html}</div>
  </div>
</section>

<section class="sec band-surface" data-theme="light">
  <div class="wrap">
    <div class="row">
      <div class="eyebrow">What they do</div>
      <div>
        {serves}
        {what}
        {offers}
        {photo}
      </div>
    </div>
    <div class="row stack">
      <div class="eyebrow">Why we fund them</div>
      <div>{why}</div>
    </div>
  </div>
</section>

{quote}

<section class="sec band" data-theme="light">
  <div class="wrap">
    {funding}
    {numbers}
    <div class="row stack">
      <div class="eyebrow">Get involved</div>
      <div>
        <p class="lede">The best way to support {name} is directly.</p>
        <div class="hero-ctas">{links_html}</div>
        <p class="text-muted">Acorn Seed Foundation is a funder of {name}. This page is maintained by Acorn Seed Foundation together with {name}. <a href="/#how-we-work">How we fund &rarr;</a></p>
      </div>
    </div>
  </div>
</section>

{FOOTER}
{NAV_SCRIPT}
</body>
</html>
"""


def directory_page(partners, logos, asf):
    cohorts = []
    for p in partners:
        if p["cohort"] not in cohorts:
            cohorts.append(p["cohort"])
    cohorts.sort(reverse=True)  # newest first

    def card(p):
        return f"""<a class="partner card" href="/partners/{p["slug"]}/">
          <div class="partner-logo"><img src="{logos[p["slug"]]}" alt="{esc(p.get("logo_alt") or p["name"] + " logo")}" data-initials="{initials(p["name"])}" /></div>
          <div class="name">{esc(p["name"])}</div>
          <p class="desc">{esc(p["tagline"])}</p>
          <div class="partner-tags">{"".join(f'<span class="tag tag-neutral">{esc(t)}</span>' for t in p["tags"])}</div>
        </a>"""

    def group(title, items):
        if not items:
            return ""
        return f"""<div class="group">
      <div class="eyebrow">{esc(title)}</div>
      <div class="grid">{"".join(card(p) for p in items)}</div>
    </div>"""

    groups = "".join(group(c, [p for p in partners if p["cohort"] == c]) for c in cohorts)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Partners &middot; Acorn Seed Foundation</title>
<meta name="description" content="The community-led organizations Acorn Seed Foundation funds with multi-year, unrestricted grants across the Greater Toronto Area." />
<link rel="canonical" href="https://acornseedfoundation.com/partners/" />
<link rel="stylesheet" href="partner.css" />
</head>
<body>

{nav(asf)}

<section class="hero band" data-theme="light">
  <div class="wrap">
    <div class="eyebrow">Partners</div>
    <h1>The organizations we fund.</h1>
    <p class="lede">Current partners receive a five-year, unrestricted grant; earlier cohorts received multi-year grants on the same terms. These pages are written with the organizations, in their words, and are theirs to share with other funders, press, or anyone curious about the work.</p>
  </div>
</section>

<section class="sec band-surface" data-theme="light">
  <div class="wrap">
    {groups}
  </div>
</section>

{FOOTER}
{NAV_SCRIPT}
</body>
</html>
"""


PAGE_CSS = """
/* ─── Partner profile pages: scaffolding only. Every color, font, radius and
   rule comes from the design-system block above (copied from index.html by
   partners/build.py). Nothing here re-declares a token. ─── */
html { scroll-behavior: smooth; scroll-padding-top: 76px; }
body { -webkit-font-smoothing: antialiased; }
.wrap { max-width: 1240px; margin: 0 auto; padding: 0 40px; }
@media (max-width: 720px) { .wrap { padding: 0 24px; } }
@media (max-width: 430px) { .wrap { padding: 0 20px; } }

/* nav — same treatment as the home page */
.nav { display: block; position: sticky; top: 0; z-index: 20; padding: 0; transition: background 300ms var(--ease), border-color 300ms var(--ease), color 300ms var(--ease); }
.nav > .wrap { display: flex; align-items: center; gap: var(--space-6); width: 100%; padding-top: var(--space-3); padding-bottom: var(--space-3); }
.nav[data-theme="dark"] { background: color-mix(in srgb, var(--color-deep) 88%, transparent); border-bottom-color: color-mix(in srgb, #f1ece3 18%, transparent); color: var(--color-on-deep); }
.nav-links { display: flex; gap: var(--space-6); margin-left: auto; }
.nav-brand img { width: 142px; height: 54px; transition: filter 400ms var(--ease); }
.nav[data-theme="dark"] .nav-brand img { filter: invert(1) hue-rotate(180deg) saturate(1.2) brightness(0.95); }
@media (max-width: 720px) { .nav-brand img { width: 112px; height: 43px; } .nav-links { gap: var(--space-3); } .nav-links a { font-size: 12.8px; } }
@media (max-width: 430px) { .nav > .wrap { gap: var(--space-3); } .nav-brand img { width: 96px; height: 37px; } .nav-links { gap: 11px; } .nav-links a { font-size: 11.8px; letter-spacing: 0; } }

/* section rhythm */
.sec { padding: 120px 0; }
.row { display: grid; grid-template-columns: 5fr 7fr; gap: 80px; align-items: start; }
.row.stack { margin-top: 96px; }
@media (max-width: 880px) { .sec { padding: 84px 0; } .row { grid-template-columns: 1fr; gap: var(--space-4); } .row.stack { margin-top: 64px; } }
@media (max-width: 560px) { .sec { padding: 64px 0; } }
.row p { max-width: 62ch; }

/* hero */
.hero { padding: 72px 0 88px; }
.crumbs { margin: 0 0 var(--space-6); }
.crumbs a { color: inherit; text-decoration: none; }
.hero-grid { display: grid; grid-template-columns: 7fr 5fr; gap: 64px; align-items: center; }
.hero h1 { font-size: clamp(31px, 4.6vw, 60px); line-height: 1.05; max-width: 18ch; margin: 0 0 var(--space-4); }
.hero .lede { font-size: clamp(17px, 1.4vw, 20px); max-width: 52ch; }
.hero .partner-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: var(--space-4); }
.hero-logo { display: flex; justify-content: flex-end; }
.hero-logo img { max-height: 104px; max-width: 260px; width: auto; height: auto; object-fit: contain; background: none; }
.hero-logo span { display: grid; place-items: center; width: 96px; height: 96px; border-radius: var(--radius-md); background: var(--color-neutral-200); color: var(--color-accent); font-size: 28px; font-family: var(--font-heading); }
.facts { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--space-6); margin-top: 64px; padding-top: var(--space-6); border-top: 1px solid var(--color-divider); }
.facts p { margin: var(--space-2) 0 0; font-size: 15px; }
@media (max-width: 880px) { .hero-grid { grid-template-columns: 1fr; gap: var(--space-6); } .hero-logo { justify-content: flex-start; } .hero-logo img { max-height: 72px; max-width: 220px; } .facts { grid-template-columns: 1fr 1fr; } }
@media (max-width: 480px) { .facts { grid-template-columns: 1fr; gap: var(--space-4); } }

/* what they do */
.offers { list-style: none; padding: 0; margin: var(--space-4) 0 0; max-width: 62ch; border-top: 1px solid var(--color-divider); }
.offers li { padding: var(--space-3) 0; border-bottom: 1px solid var(--color-divider); font-size: 15px; }
.photo { margin-top: var(--space-8); max-width: 62ch; }

/* quote band */
.quote blockquote { margin: var(--space-6) 0 0; max-width: 34ch; }
.quote blockquote p { font-size: clamp(22px, 2.6vw, 34px); line-height: 1.3; letter-spacing: -0.015em; font-family: var(--font-heading); font-weight: var(--font-heading-weight); margin: 0 0 var(--space-6); }
.quote footer { margin-top: var(--space-4); }

/* numbers */
.numbers { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: var(--space-6); border-top: 1px solid var(--color-divider); padding-top: var(--space-6); }
.num { font-family: var(--font-heading); font-weight: var(--font-heading-weight); font-size: clamp(34px, 4vw, 52px); line-height: 1; letter-spacing: -0.02em; margin-bottom: var(--space-2); }

/* get involved */
.hero-ctas { display: flex; gap: var(--space-3); flex-wrap: wrap; margin: var(--space-6) 0; }
@media (max-width: 720px) { .hero-ctas .btn { flex: 1 1 auto; } }

/* directory */
.group + .group { margin-top: 96px; }
.group .eyebrow { margin-bottom: var(--space-6); }
.grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-4); }
@media (max-width: 1000px) { .grid { grid-template-columns: 1fr 1fr; } }
.grid .partner { width: auto; padding: var(--space-6); border-right: 0; }
.grid .partner:hover { opacity: 1; border-color: var(--color-neutral-700); }
.partner { text-decoration: none; color: inherit; display: block; transition: opacity 150ms var(--ease), border-color 150ms var(--ease); }
.partner-logo { height: 56px; display: flex; align-items: center; margin-bottom: var(--space-4); }
.partner-logo img { max-height: 56px; max-width: 150px; width: auto; height: auto; object-fit: contain; background: none; }
.partner-logo span { display: grid; place-items: center; width: 48px; height: 48px; border-radius: var(--radius-sm); background: var(--color-neutral-200); color: var(--color-accent); font-size: 17px; }
.partner .name { font-family: var(--font-heading); font-weight: var(--font-heading-weight); font-size: 18.4px; letter-spacing: -0.015em; line-height: 1.25; }
.partner .desc { font-size: 14px; margin: var(--space-2) 0 var(--space-4); color: color-mix(in srgb, var(--color-text) 70%, transparent); }
.partner-tags { display: flex; flex-wrap: wrap; gap: 6px; }
@media (max-width: 720px) { .grid { grid-template-columns: 1fr; } }

/* footer */
.foot { padding: 96px 0 48px; }
.foot-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 64px; }
.foot .wordmark { font-family: var(--font-heading); font-weight: var(--font-heading-weight); font-size: 18.4px; margin-bottom: var(--space-4); }
.foot p { font-size: 14px; max-width: 46ch; color: var(--color-on-deep-muted); }
.foot-bottom { display: flex; justify-content: space-between; flex-wrap: wrap; gap: var(--space-3); margin-top: 64px; padding-top: var(--space-6); border-top: 1px solid color-mix(in srgb, #f1ece3 12%, transparent); }
@media (max-width: 720px) { .foot { padding: 72px 0 40px; } .foot-grid { grid-template-columns: 1fr; gap: var(--space-8); } .foot-bottom { margin-top: 48px; } }
"""


def main():
    data = json.loads((PARTNERS / "partners.json").read_text(encoding="utf-8"))
    partners = data["partners"]
    asf = asf_logo()
    (PARTNERS / "partner.css").write_text(system_css().strip() + "\n" + PAGE_CSS, encoding="utf-8")

    logos = {}
    for p in partners:
        f = LOGOS / LOGO_FILES[p["slug"]]
        logos[p["slug"]] = data_uri(f)
        out = PARTNERS / p["slug"]
        out.mkdir(exist_ok=True)
        (out / "index.html").write_text(partner_page(p, logos[p["slug"]], asf), encoding="utf-8")
        print("wrote", out / "index.html")

    (PARTNERS / "index.html").write_text(directory_page(partners, logos, asf), encoding="utf-8")
    print("wrote", PARTNERS / "index.html")


if __name__ == "__main__":
    main()
