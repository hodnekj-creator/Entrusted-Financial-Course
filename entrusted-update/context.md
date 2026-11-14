# Entrusted: Managing God's Money — Site Context

## What this is

A static website for a Bible-based financial literacy course called **Entrusted**. It teaches money management through a church class or small group, following **Dave Ramsey's Baby Steps** (six of his seven; the college-fund step is left out on purpose), with scripture for each step and giving and a written budget at every step.

**Live site:** https://hodnekj-creator.github.io/Entrusted-Financial-Course/
**Repo:** https://github.com/hodnekj-creator/Entrusted-Financial-Course (public)
**GitHub Pages:** Deploys from `main` branch, `/ (root)`.

## How the site is built

- `content.py` — All teaching content: Baby Steps, course notes, sessions, money basics, scripture references, discussion questions, article links. This is the source of truth for words and numbers.
- `graphics.py` — Inline SVG charts and diagrams (stdlib only). Numbers are computed from the same formulas as the calculators.
- `build.py` — Python static site generator (stdlib only). Imports `content.py` and `graphics.py` and writes a flat `entrusted/` folder with relative links. Run with `python3 build.py`; it builds, then runs the checks.
- The built files in `entrusted/` are what get uploaded to the repo root. No subfolders: flat HTML + one `style.css`.

### To rebuild and deploy
```bash
cd /path/to/site
python3 build.py          # builds into ./entrusted/ and prints "All checks passed."
# Upload the contents of entrusted/ to the repo root
```

## File inventory (54 files)

### Core pages
- `index.html` — Homepage (Baby Steps staircase graphic, money basics chart)
- `steps.html` — The Baby Steps with scripture, why, how you know you are done, and the two course notes
- `basics.html` — Money Basics: compound interest, rule of 72, debt at 24%, APR vs APY, tax brackets, 401(k) match, stocks and index funds, cheat sheets, articles
- `about.html` — About the course (Ramsey credit and not-affiliated line)
- `scripture.html` — All scripture references grouped by session, each linked to the NIV
- `scripture-handout.html` — Printable: every passage once, in Bible order, with summary, where it is used, and a read checkbox (one sheet front and back)
- `step-card.html` — Printable Baby Steps card (two per sheet)
- `handouts.html` — Index of all handouts
- `leader.html` — Leader preparation index
- `tools.html` — Calculators
- `compound.html` — Compound interest calculator (chart, year-by-year spreadsheet, opportunity cost)
- `style.css` — All styles

### Track pages (3 tracks)
- `one-night.html`, `campus.html` (4 Weeks), `church.html` (8 Weeks)

### Session pages (13 sessions × 3 pages each = 39 files)
- `{track}-{n}.html` — Presentation slides (PageDown/arrow key navigation)
- `{track}-{n}-handout.html` — Printable handout (one sheet front and back)
- `{track}-{n}-leader.html` — Leader guide
- night (1 session): `night.html`, `night-handout.html`, `night-leader.html`
- campus (4 sessions): `campus-1` to `campus-4`
- church (8 sessions): `church-1` to `church-8`

## The Baby Steps (content.STEPS)

Ramsey's wording, credited to him. The course deliberately omits his college-fund step (the owner disagrees with it), so our steps 5 and 6 are his 6 and 7. Do not add it back:
1. Save $1,000 for your starter emergency fund.
2. Pay off all debt (except the house) using the debt snowball.
3. Save 3–6 months of expenses in a fully funded emergency fund.
4. Invest 15% of your household income in retirement.
5. Pay off your home early.
6. Build wealth and give.

Steps 1–3 are done one at a time, in order; steps 4 and 5 are worked at the same time.

**Course notes (not steps), in content.STEP_NOTES:**
- Take the employer match at every step, even during steps 1–3 (Ramsey teaches pausing all investing until step 4; the course says so plainly).
- Credit cards: skipping them is wise; if you keep one, pay the full statement balance every month.

## Key constraints

### Content rules
- Use "Baby Steps" and credit Dave Ramsey. Say the course is not affiliated with or endorsed by Ramsey Solutions.
- Scripture is given as references and short paraphrases, never quoted in full. **Every reference links to the NIV on Bible Gateway** (build.py does this automatically with `refs()` / `ref_a()`; references inside teaching text are linked too).
- Do not print NIV text on the site or handouts (copyright). The scripture handout uses paraphrases. The owner asked about quoting scripture; if he wants verse text, use a public-domain translation (WEB or KJV) and keep the NIV links.
- Investing advice carried from the owner: never do something with your money you do not understand, and find an adviser with the heart of a teacher (invest step and stocks basic).
- Tax brackets use round-number teaching figures labeled as such; never hard-code real IRS brackets or limits. IRS link allowed (`www.irs.gov`).
- Use a 7% return assumption and always note returns are not guaranteed (build adds the footnote wherever "7%" appears).
- Make no specific investment recommendations.
- Do not hard-code IRS contribution limits; they change yearly. Say "look up the current numbers."
- One Night never meets again: its wrap-up says "In the next 30 days" / "To take home", never "this week" or "before we meet again".

### Technical rules
- No external scripts, fonts or stylesheets — everything is self-contained.
- Nothing stored or sent — no cookies, no analytics, no network calls.
- Outside **links** are allowed only to: biblegateway.com, investor.gov, consumerfinance.gov, ramseysolutions.com (`EXTERNAL_HOSTS` in build.py). They open in a new tab with `rel="noopener"`. The check fails on any other outside link.
- Standard library only for build.py and graphics.py.
- Flat folder structure, relative internal links only.
- Each handout must fit one sheet front and back.

### What build.py checks
- Internal links and anchors, three pages per session, required pages present
- No old Stewardship Steps wording ("Stewardship Step", "starter buffer", "full reserve", "consumer debt", "before we meet next")
- One Night does not say "Before we meet again"
- Every session scripture reference is linked to the NIV; every scripture-handout entry has a paraphrase and link
- Calculator numbers:
  - $200/month from age 22–65 at 7%: **$655,226**
  - $200/month from age 32–65 at 7%: **$308,813**
  - Debt: $5,000 at 24% with $200/month: 36 months, $2,001 interest; with $100/month: never paid off
  - Opportunity cost: $1,000 once for 20 years at 7%: **$4,038.74**
- Money basics numbers (and that the text states them):
  - Sam ($200/mo 22–32, then stops) ≈ $346,000 at 65; Jordan ($200/mo 32–65) ≈ $309,000
  - $10,000 at 7%: about $20,000 / $40,000 / $81,000 / $163,000 at 32 / 42 / 52 / 62
  - 24% APR compounded daily ≈ 27.1%; 4% compounded daily = 4.08% APY

## Graphics (graphics.py)

Keys used in content.py (third item of a teaching point, or a money-basics `graphic`):
`staircase`, `compound`, `early_late`, `doubling`, `debt_trap`, `apr_apy`, `match`, `shares`, `budget`, `efund`, `snowball`, `gap`.
Colors: green #157a4b (growth / good outcome), ochre #b8862b (money put in or owed), gray #7d837e dashed (comparison), dark green #1d5640.
On wide screens, slides with a graphic put the text on the left and the picture on the right.

## One Night structure (90 minutes)
Open 0–10 · Owner and manager 10–25 · Work and giving 25–35 · The Baby Steps 35–50 · The long view 50–55 · Money basics (7 slides, ~3 min each) 55–78 · Discuss and commit 78–90. Ends with a "Where to go from here" slide.

## Navigation structure

```
Home | Baby Steps | Money Basics | One Night | 4 Weeks | 8 Weeks | Handouts | Leader Prep | Tools | About
```

## Design

- Warm neutral palette: cream background (#f7f4ec), dark green accents (#1d5640), muted text
- Serif headings, system sans-serif body
- Print CSS with @page margin .5in and break-before for handouts
- Presentation slides use PageDown/arrow navigation with 900ms target memory

## Site URL in content

`SITE_URL = "hodnekj-creator.github.io/Entrusted-Financial-Course"` in build.py, printed on the step card, One Night handout and scripture handout.

## Known content notes (flagged but left unchanged)

- K1 and NIGHT sessions omit "and you have never given a tenth"
- The About page has no author name or usage permission statement
