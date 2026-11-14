#!/usr/bin/env python3
"""Build the Entrusted course site from content.py.

    python3 build.py

Writes every page into ./entrusted/ (one flat folder, relative links only),
then runs the checks: internal links, three pages per session, calculator
numbers, and banned phrases. Standard library only. Teaching content lives
in content.py; this file only turns it into HTML.
"""
import html
import json
import re
import shutil
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import content as C  # noqa: E402
import graphics as G  # noqa: E402

OUT = HERE / "entrusted"

COURSE = "Entrusted: Managing God's Money"
VISION = "God owns it all, we manage it, and He will ask for an account."
# Printed on the step card and scripture handout. Change it if the site moves.
SITE_URL = "hodnekj-creator.github.io/Entrusted-Financial-Course"
TRACK_ORDER = ["night", "campus", "church"]
RETURN_NOTE = "The 7% return is an assumption for illustration. Returns are not guaranteed."
# Outside sites the pages may link to (opened in a new tab). Anything else fails the check.
EXTERNAL_HOSTS = ("www.biblegateway.com", "www.investor.gov", "www.consumerfinance.gov", "www.ramseysolutions.com", "www.irs.gov")

NAV = [
    ("index.html", "Home"),
    ("steps.html", "Baby Steps"),
    ("basics.html", "Money Basics"),
    ("one-night.html", "One Night"),
    ("campus.html", "4 Weeks"),
    ("church.html", "8 Weeks"),
    ("handouts.html", "Handouts"),
    ("leader.html", "Leader Prep"),
    ("tools.html", "Tools"),
    ("about.html", "About"),
]

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
           "%3Crect width='32' height='32' rx='5' fill='%231d5640'/%3E"
           "%3Ctext x='16' y='23.5' font-family='Georgia,serif' font-size='21' text-anchor='middle' "
           "fill='%23f7f4ec'%3EE%3C/text%3E%3C/svg%3E")


def esc(s):
    return html.escape(s, quote=False)


def attr(s):
    return html.escape(s, quote=True)


# ---------------------------------------------------------------- sessions

SESSIONS = []
for _key in TRACK_ORDER:
    _t = C.TRACKS[_key]
    for _i, (_sid, _data, _plan) in enumerate(_t["sessions"], 1):
        SESSIONS.append(dict(id=_sid, key=_key, track=_t, num=_i, count=len(_t["sessions"]),
                             d=_data, plan=_plan))


def where(s):
    """Where a session sits, in words."""
    if s["count"] == 1:
        return s["track"]["name"]
    return f"{s['track']['name']}, session {s['num']} of {s['count']}"


def track_sessions(key):
    return [s for s in SESSIONS if s["key"] == key]


def split_ref(entry):
    ref, _, para = entry.partition("|")
    return ref.strip(), para.strip()


def first_ref(refs):
    return refs.split(";")[0].strip()


def prep_worksheet(markup):
    """Tag each worksheet table with its column count, and mark reference tables
    (no blank cells) so the stylesheet can size columns and writing space."""
    def fix(m):
        table = m.group(0)
        cols = len(re.findall(r"<th>", table.split("</thead>")[0]))
        cls = f"cols-{cols}" + ("" if "<td></td>" in table else " filled")
        return table.replace("<table>", f'<table class="{cls}">', 1)
    return link_refs(re.sub(r"<table>.*?</table>", fix, markup, flags=re.S))


def needs_return_note(text):
    return re.search(r"(?<![\d.])7%", text) is not None


# ---------------------------------------------------------------- scripture references

BOOKS = ("Genesis Exodus Leviticus Numbers Deuteronomy Joshua Judges Ruth Samuel Kings Chronicles "
         "Ezra Nehemiah Esther Job Psalms Psalm Proverbs Ecclesiastes Isaiah Jeremiah Lamentations "
         "Ezekiel Daniel Hosea Joel Amos Obadiah Jonah Micah Nahum Habakkuk Zephaniah Haggai Zechariah "
         "Malachi Matthew Mark Luke John Acts Romans Corinthians Galatians Ephesians Philippians "
         "Colossians Thessalonians Timothy Titus Philemon Hebrews James Peter Jude Revelation").split()
REF_RE = re.compile(r"\b((?:[123] )?(?:" + "|".join(BOOKS) + r")) (\d+)(?::(\d+)(?:-(\d+))?)?\b")


def parse_refs(text):
    out = []
    for m in REF_RE.finditer(text):
        book, ch, v1, v2 = m.group(1), int(m.group(2)), m.group(3), m.group(4)
        v1 = int(v1) if v1 else None
        v2 = int(v2) if v2 else v1
        out.append((m.group(0), book, ch, v1, v2))
    return out


BIBLE_URL = "https://www.biblegateway.com/passage/?search={}&version=NIV"


def bible_url(ref):
    return BIBLE_URL.format(quote(ref))


def ref_a(ref):
    """One reference, linked to the NIV on Bible Gateway in a new tab."""
    return (f'<a class="bible" href="{attr(bible_url(ref))}" target="_blank" rel="noopener" '
            f'title="Read {attr(ref)} in the NIV">{esc(ref)}</a>')


def link_refs(escaped):
    """Link every scripture reference inside text that is already HTML-escaped."""
    return REF_RE.sub(lambda m: ref_a(m.group(0)), escaped)


def refs(text):
    """Escape plain text and link the references in it."""
    return link_refs(esc(text))


def out_a(key):
    """An article from content.LINKS, opened in a new tab."""
    title, source, url = C.LINKS[key]
    return (f'<a href="{attr(url)}" target="_blank" rel="noopener">{esc(title)}</a>'
            f' <span class="src">{esc(source)}</span>')


def fig(key, uid):
    return G.render(key, uid)


def step_what(s):
    """Ramsey's wording for a step, unless it only repeats the short name (the last step)."""
    name, what = s[0], s[1]
    return "" if what.rstrip(".").lower() == name.lower() else what


def teach_parts(item):
    """Teaching points are (heading, text) or (heading, text, graphic)."""
    return item[0], item[1], (item[2] if len(item) > 2 else None)


def covered(mention, listed):
    _, book, ch, v1, v2 = mention
    for _, lb, lc, lv1, lv2 in listed:
        if lb != book or lc != ch:
            continue
        if v1 is None or lv1 is None:
            return True
        if lv1 <= v1 and v2 <= lv2:
            return True
    return False


def session_text(d):
    parts = [d["opener"], d["skill"][1], d["guard"]]
    parts += [t for item in d["teach"] for t in item[:2]]
    for key in d.get("basics", []):
        b = C.BASICS[key]
        parts += [b["text"]] + b["more"]
    parts += [t for pair in d["objections"] for t in pair]
    parts += d["discuss"] + d["action"] + d["prep"]
    parts.append(re.sub(r"<[^>]+>", " ", d["worksheet"]))
    return "\n".join(parts)


def also_mentioned(d):
    listed = []
    for entry in d["scripture"]:
        listed += parse_refs(split_ref(entry)[0])
    seen, extra = set(), []
    for m in parse_refs(session_text(d)):
        if m[0] in seen or covered(m, listed):
            continue
        seen.add(m[0])
        extra.append(m[0])
    return extra


# ---------------------------------------------------------------- page shell

def nav_html(current):
    items = []
    for href, label in NAV:
        cur = ' aria-current="page"' if href == current else ""
        items.append(f'<li><a href="{href}"{cur}>{label}</a></li>')
    return "".join(items)


def page(title, body, *, current="", kind="", desc="", script=""):
    full_title = title if title == COURSE else f"{title} | Entrusted"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{attr(desc or VISION)}">
<link rel="icon" href="{FAVICON}">
<link rel="stylesheet" href="style.css">
</head>
<body class="{kind}">
<a class="skip" href="#main">Skip to content</a>
<header class="site-head">
<div class="wrap head-inner">
<a class="brand" href="index.html"><span class="brand-name">Entrusted</span><span class="brand-sub">Managing God's Money</span></a>
<nav class="site-nav" aria-label="Main"><ul>{nav_html(current)}</ul></nav>
</div>
</header>
<main id="main">
{body}
</main>
<footer class="site-foot">
<div class="wrap">
<p class="foot-name">{esc(COURSE)}</p>
<p>Teaching for churches and small groups, not professional financial advice. Every scripture reference opens the passage in the NIV on Bible Gateway, or read it in your own Bible. The Baby Steps are Dave Ramsey's; this course is not affiliated with Ramsey Solutions. <a href="about.html">About this course</a></p>
</div>
</footer>
{script}
</body>
</html>
"""


def toolbar(note):
    return (f'<div class="toolbar"><button class="print-btn" type="button" onclick="window.print()">Print</button>'
            f'<p>{note}</p></div>')


# ---------------------------------------------------------------- home

def build_index():
    formats = []
    for key in TRACK_ORDER:
        t = C.TRACKS[key]
        formats.append(f"""<article class="format">
<h3><a href="{t['page']}">{esc(t['name'])}</a></h3>
<p class="format-length">{esc(t['length'])}</p>
<p class="format-who">{esc(t['who'])}</p>
<p>{esc(t['blurb'])}</p>
<p class="format-link"><a href="{t['page']}">See the {'session' if len(t['sessions']) == 1 else 'sessions'}</a></p>
</article>""")

    ladder = []
    for i, s in enumerate(C.STEPS, 1):
        ladder.append(f'<li><span class="num" aria-hidden="true">{i}</span><div>'
                      f'<h3><span class="vh">Baby Step {i}: </span>{esc(s[0])}</h3><p>{esc(step_what(s))}</p></div></li>')
    ev = C.EVERY_STEP

    body = f"""<section class="hero">
<div class="wrap">
<p class="hero-course">{esc(COURSE)}</p>
<h1 class="hero-vision">{esc(VISION)}</h1>
<p class="hero-refs">{refs("Psalm 24:1; Matthew 25:14-30")}</p>
<p class="lede">Entrusted is a Bible-based course on handling money as a manager of what belongs to God. It is written for church classes and small groups, and it follows Dave Ramsey's Baby Steps, from a $1,000 starter emergency fund to building wealth and giving, with scripture for each step and giving and a written budget at every one. Every session has a page to present, a printable handout and a leader guide.</p>
</div>
</section>

<section class="band">
<div class="wrap">
<h2>Three ways to teach it</h2>
<div class="formats">
{''.join(formats)}
</div>
</div>
</section>

<section class="band band-steps">
<div class="wrap">
<h2>{esc(C.STEPS_NAME)}</h2>
<p class="band-lede">{esc(C.STEPS_CREDIT)} {esc(C.STEPS_ORDER)}</p>
{fig("staircase", "home-stairs")}
</div>
<div class="wrap split">
<div class="split-side">
<p class="every-line"><strong>{esc(ev[0])}:</strong> {esc(ev[1])}</p>
<p><a href="steps.html">Read each step with its scripture</a></p>
<p><a href="step-card.html">Print the step card</a></p>
</div>
<ol class="ladder ladder-compact">
{''.join(ladder)}
</ol>
</div>
</section>

<section class="band band-basics">
<div class="wrap split">
<div class="split-side">
<h2>Money basics</h2>
<p>The practical side: compound interest, APR and APY, how tax brackets work, the 401(k) match, and what the stock market is.</p>
<p><a href="basics.html">Read the money basics</a></p>
</div>
{fig("early_late", "home-early")}
</div>
</section>

<section class="band">
<div class="wrap leaders">
<h2>For leaders</h2>
<ul class="leader-links">
<li><a href="handouts.html">Handouts</a><span>Printable sheets for every session, the step card and the scripture handout.</span></li>
<li><a href="leader.html">Leader prep</a><span>Prep lists, timed plans, teaching notes, cautions and likely questions.</span></li>
<li><a href="tools.html">Tools</a><span>Calculators for the sessions, plus a growth chart, a year-by-year spreadsheet and an opportunity cost calculator.</span></li>
</ul>
</div>
</section>"""
    return page(COURSE, body, current="index.html", kind="home")


# ---------------------------------------------------------------- steps

def build_steps():
    items = []
    for i, s in enumerate(C.STEPS, 1):
        name, what, refs_, why, done = s
        items.append(f"""<li id="step-{i}">
<span class="num" aria-hidden="true">{i}</span>
<div class="step-body">
<h2><span class="vh">Baby Step {i}: </span>{esc(name)}</h2>
{f'<p class="step-what">{esc(step_what(s))}</p>' if step_what(s) else ''}
<p class="step-ref">{refs(refs_)}</p>
<p class="step-why">{esc(why)}</p>
<div class="done"><h3>How you know you are done</h3><p>{esc(done)}</p></div>
</div>
</li>""")
    ev = C.EVERY_STEP
    notes = "".join(f"<div><h3>{esc(h)}</h3><p>{esc(t)}</p></div>" for h, t in C.STEP_NOTES)
    body = f"""<header class="page-head wrap">
<h1>{esc(C.STEPS_NAME)}</h1>
<p class="lede">{esc(C.STEPS_ORDER)} Giving and a written budget apply at every one of them.</p>
<p class="credit">{esc(C.STEPS_CREDIT)} <a href="{attr(C.STEPS_URL)}" target="_blank" rel="noopener">The Baby Steps at Ramsey Solutions</a></p>
<p class="head-links"><a href="step-card.html">Print the step card</a></p>
</header>
<div class="wrap">
{fig("staircase", "steps-stairs")}
<div class="steps-asides">
<aside class="every" aria-labelledby="every-h">
<h2 id="every-h">{esc(ev[0])}</h2>
<p class="step-what">{esc(ev[1])}</p>
<p class="step-ref">{refs(ev[2])}</p>
<p class="step-why">{esc(ev[3])}</p>
</aside>
<aside class="every course-notes" aria-labelledby="notes-h">
<h2 id="notes-h">Two notes from this course</h2>
{notes}
</aside>
</div>
<ol class="ladder ladder-full">
{''.join(items)}
</ol>
</div>"""
    return page(C.STEPS_NAME, body, current="steps.html", kind="steps",
                desc="Dave Ramsey's Baby Steps with scripture for each, the reason for each, and how you know you are done.")


# ---------------------------------------------------------------- track pages

def build_track(key):
    t = C.TRACKS[key]
    rows = []
    for s in track_sessions(key):
        d = s["d"]
        label = "The session" if s["count"] == 1 else f"Session {s['num']}"
        rows.append(f"""<li>
<span class="num" aria-hidden="true">{s['num']}</span>
<div>
<p class="sess-label">{label}</p>
<h3><a href="{s['id']}.html">{esc(d['title'])}</a></h3>
<p>{esc(d['big'])}</p>
<p class="sess-links"><a href="{s['id']}.html">Present</a><a href="{s['id']}-handout.html">Handout</a><a href="{s['id']}-leader.html">Leader guide</a></p>
</div>
</li>""")
    extra = f'<p class="track-extra">{t["extra"]}</p>' if t.get("extra") else ""
    heading = "Session" if len(rows) == 1 else "Sessions"
    body = f"""<header class="page-head wrap">
<h1>{esc(t['name'])}</h1>
<p class="lede">{esc(t['blurb'])}</p>
<dl class="facts">
<div><dt>Who it is for</dt><dd>{esc(t['who'])}</dd></div>
<div><dt>Length</dt><dd>{esc(t['length'])}</dd></div>
</dl>
{extra}
</header>
<section class="wrap">
<h2>{heading}</h2>
<ol class="session-list">
{''.join(rows)}
</ol>
<aside class="track-aside">
<h2>Print for the group</h2>
<p>Each session has its own handout. Everyone also needs <a href="step-card.html">the Baby Steps card</a>, and <a href="scripture-handout.html">the scripture handout</a> is handy for reading ahead. Leaders: start with <a href="leader.html">how to prepare</a>.</p>
</aside>
</section>"""
    return page(t["name"], body, current=t["page"], kind="track", desc=t["blurb"])


# ---------------------------------------------------------------- session (present)

SESSION_JS = """<script>
(function () {
  var slides = [].slice.call(document.querySelectorAll('.slide'));
  if (!slides.length) return;
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function top(el) { return el.getBoundingClientRect().top + window.pageYOffset; }
  function current() {
    var y = window.pageYOffset + 12, idx = 0;
    for (var i = 0; i < slides.length; i++) { if (top(slides[i]) <= y) idx = i; }
    return idx;
  }
  var target = 0, lastMove = 0;
  function go(step) {
    var from = (Date.now() - lastMove < 900) ? target : current();
    target = Math.min(slides.length - 1, Math.max(0, from + step));
    lastMove = Date.now();
    slides[target].scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
  }
  document.addEventListener('keydown', function (e) {
    if (e.altKey || e.ctrlKey || e.metaKey) return;
    var tag = (e.target && e.target.tagName) || '';
    if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;
    if (e.key === 'PageDown' || e.key === 'ArrowRight') { e.preventDefault(); go(1); }
    else if (e.key === 'PageUp' || e.key === 'ArrowLeft') { e.preventDefault(); go(-1); }
  });
})();
</script>"""


def action_labels(s):
    """A one-session track never meets again, so its take-home is not 'this week'."""
    if s["count"] == 1:
        return "To take home", "In the next 30 days"
    return "Before we meet again", "This week"


def slide(sid, margin, inner, extra_cls=""):
    m = f'<p class="margin">{margin}</p>' if margin else '<p class="margin" aria-hidden="true"></p>'
    return (f'<section class="slide {extra_cls}" id="{sid}"><div class="slide-inner">{m}'
            f'<div class="slide-body">{inner}</div></div></section>')


def build_session(s):
    d, t = s["d"], s["track"]
    n_teach = len(d["teach"])
    parts = [f"""<section class="slide slide-title" id="start"><div class="slide-inner"><p class="margin" aria-hidden="true"></p><div class="slide-body">
<p class="where"><a href="{t['page']}">{esc(where(s))}</a></p>
<h1>{esc(d['title'])}</h1>
<p class="big-idea">{esc(d['big'])}</p>
<p class="present-hint">Presenting? Page Down or the right arrow moves one section at a time.</p>
</div></div></section>"""]

    ref_items = "".join(f'<li><span class="ref">{ref_a(r)}</span><span class="para">{esc(p)}</span></li>'
                        for r, p in map(split_ref, d["scripture"]))
    parts.append(slide("scripture", "Read these aloud. Tap a reference to open it in the NIV.",
                       f'<h2>Scripture</h2><ul class="refs">{ref_items}</ul>'))
    parts.append(slide("open", "Everyone answers.",
                       f'<h2>Opening question</h2><p class="opener">{esc(d["opener"])}</p>'))
    for i, item in enumerate(d["teach"], 1):
        head, text, graphic = teach_parts(item)
        note = f'<p class="footnote">{RETURN_NOTE}</p>' if needs_return_note(text) else ""
        g = fig(graphic, f"t{i}-{graphic}") if graphic else ""
        parts.append(slide(f"teach-{i}", f"Teaching point {i} of {n_teach}",
                           f'<h2>{esc(head)}</h2><p>{refs(text)}</p>{g}{note}', "has-fig" if g else ""))
    basics = d.get("basics", [])
    for k, key in enumerate(basics, 1):
        b = C.BASICS[key]
        note = f'<p class="footnote">{RETURN_NOTE}</p>' if needs_return_note(b["text"] + b["title"]) else ""
        more = "".join(f"<li>{out_a(x)}</li>" for x in b["links"])
        parts.append(slide(f"basics-{k}", f"Money basics, {k} of {len(basics)}",
                           f'<h2>{esc(b["title"])}</h2><p>{refs(b["text"])}</p>{fig(b["graphic"], "b-" + key)}{note}'
                           f'<div class="read-more"><p>Read more</p><ul>{more}<li><a href="basics.html#{key}">More on the Money Basics page</a></li></ul></div>',
                           "has-fig basics-slide"))
    tools = (' <a href="tools.html">Open the calculators</a>'
             if "calculator" in d["skill"][1].lower() else "")
    parts.append(slide("practice", "Practical step",
                       f'<h2>{esc(d["skill"][0])}</h2><p>{esc(d["skill"][1])}</p>'
                       f'<p class="slide-links"><a href="{s["id"]}-handout.html">The worksheet is on the handout</a>{tools}</p>'))
    qs = "".join(f"<li>{refs(q)}</li>" for q in d["discuss"])
    parts.append(slide("discuss", "In the group", f'<h2>Discuss</h2><ol class="discuss">{qs}</ol>'))
    acts = "".join(f"<li>{esc(a)}</li>" for a in d["action"])
    margin, heading = action_labels(s)
    parts.append(slide("action", margin, f'<h2>{heading}</h2><ul class="checks big-checks">{acts}</ul>'))
    if s["count"] == 1:
        nxt = "".join(f'<li><a href="{h}">{esc(t)}</a><span>{esc(why)}</span></li>' for h, t, why in C.NEXT_STEPS)
        nxt += (f'<li><a href="{attr(C.STEPS_URL)}" target="_blank" rel="noopener">The Baby Steps at Ramsey Solutions</a>'
                f'<span>Dave Ramsey\'s own explanation of each step.</span></li>')
        parts.append(slide("next", "Where to go from here",
                           f'<h2>Keep going</h2><p>Tonight was the whole picture in one sitting. Everything is on the site, and the longer tracks take each piece one week at a time.</p>'
                           f'<ul class="next-list">{nxt}</ul>'))

    sibs = track_sessions(s["key"])
    idx = sibs.index(s)
    prev_link = (f'<a class="prev" href="{sibs[idx-1]["id"]}.html">Previous: {esc(sibs[idx-1]["d"]["title"])}</a>'
                 if idx > 0 else "")
    next_link = (f'<a class="next" href="{sibs[idx+1]["id"]}.html">Next: {esc(sibs[idx+1]["d"]["title"])}</a>'
                 if idx < len(sibs) - 1 else "")
    end = f"""<nav class="session-end wrap" aria-label="Session">
<p class="end-links"><a href="{s['id']}-handout.html">Handout</a><a href="{s['id']}-leader.html">Leader guide</a><a href="{t['page']}">All {esc(t['name'])} sessions</a></p>
<p class="end-seq">{prev_link}{next_link}</p>
</nav>"""
    body = "\n".join(parts) + end
    return page(d["title"], body, current=t["page"], kind="session", desc=d["big"], script=SESSION_JS)


# ---------------------------------------------------------------- handout

def build_handout(s):
    d = s["d"]
    ref_items = "".join(f'<li><span class="ref">{ref_a(split_ref(e)[0])}</span><span class="line"></span></li>'
                        for e in d["scripture"])
    basics = d.get("basics", [])
    dense = " dense" if len(d["scripture"]) > 5 else ""
    lines = '<div class="write"></div>' * (1 if basics else 2 if dense else 3)
    points = "".join(f'<div class="pt"><h3>{esc(item[0])}</h3>{lines}</div>' for item in d["teach"])
    qs = "".join(f"<li>{refs(q)}</li>" for q in d["discuss"])
    acts = "".join(f"<li>{esc(a)}</li>" for a in d["action"])
    _, heading = action_labels(s)
    glance = ""
    if basics:
        rows = "".join(f'<div><dt>{esc(C.BASICS[k]["short"])}</dt><dd>{esc(C.BASICS[k]["glance"])}</dd></div>' for k in basics)
        glance = (f'<section class="ho-block ho-basics"><h2>Money basics</h2><dl class="glance">{rows}</dl>'
                  f'<p class="ho-hint">More on each, with charts and articles: {SITE_URL}/basics.html</p></section>')
    body = f"""{toolbar("Prints on one sheet, front and back.")}
<article class="paper handout{dense}{' with-basics' if basics else ''}">
<header class="ho-head">
<p class="ho-where"><span>{esc(COURSE)}</span><span>{esc(where(s))}</span></p>
<h1>{esc(d['title'])}</h1>
<p class="ho-big">{esc(d['big'])}</p>
</header>
<section class="ho-block"><h2>Scripture</h2><p class="ho-hint">Read each passage in your Bible and note what stands out. On the site, each reference opens in the NIV.</p><ul class="ho-refs">{ref_items}</ul></section>
<section class="ho-block ho-points"><h2>Teaching notes</h2>{points}</section>
{glance}
<section class="ho-block"><h2>Discuss</h2><ol class="ho-discuss">{qs}</ol></section>
<section class="ho-block"><h2>{heading}</h2><ul class="checks">{acts}</ul></section>
<section class="ho-back">
<h2 class="ho-back-title">{esc(d['skill'][0])}</h2>
<p class="ho-skill">{esc(d['skill'][1])}</p>
{prep_worksheet(d['worksheet'])}
</section>
</article>"""
    return page(f"Handout: {d['title']}", body, current="handouts.html", kind="print-page",
                desc=f"Printable handout for {d['title']}.")


# ---------------------------------------------------------------- leader guide

def build_leader(s):
    d, t = s["d"], s["track"]
    prep = "".join(f"<li>{refs(p)}</li>" for p in d["prep"])
    plan = "".join(f"<tr><td>{esc(m)}</td><th scope=\"row\">{esc(seg)}</th><td>{refs(what)}</td></tr>"
                   for m, seg, what in s["plan"])
    extra = f'<p class="plan-extra">{t["extra"]}</p>' if t.get("extra") else ""
    ref_list = "".join(f"<dt>{ref_a(r)}</dt><dd>{esc(p)}</dd>" for r, p in map(split_ref, d["scripture"]))
    teach = ""
    for item in d["teach"]:
        h, text, _ = teach_parts(item)
        note = f'<p class="footnote">{RETURN_NOTE}</p>' if needs_return_note(text) else ""
        teach += f"<li><h4>{esc(h)}</h4><p>{refs(text)}</p>{note}</li>"
    basics = ""
    if d.get("basics"):
        items = ""
        for key in d["basics"]:
            b = C.BASICS[key]
            note = f'<p class="footnote">{RETURN_NOTE}</p>' if needs_return_note(b["text"]) else ""
            items += f"<li><h4>{esc(b['title'])}</h4><p>{refs(b['text'])}</p>{note}</li>"
        basics = (f'<h3>Money basics</h3><p>Show each slide\'s picture, say the one idea, and move on. '
                  f'The <a href="basics.html">Money Basics page</a> has more on each for questions.</p><ol class="teach-list">{items}</ol>')
    qs = "".join(f"<li>{refs(q)}</li>" for q in d["discuss"])
    acts = "".join(f"<li>{esc(a)}</li>" for a in d["action"])
    action_h = "Take-home action" if s["count"] == 1 else "This week's action"
    objs = "".join(f"<dt>{esc(q)}</dt><dd>{refs(a)}</dd>" for q, a in d["objections"])
    minutes = s["plan"][-1][0].split("-")[-1]
    body = f"""{toolbar("Print this guide, or keep it open while you prepare.")}
<article class="doc leader">
<header class="doc-head">
<p class="where"><a href="{t['page']}">{esc(where(s))}</a></p>
<h1>Leader guide: {esc(d['title'])}</h1>
<p class="ho-big">{esc(d['big'])}</p>
<p class="doc-links"><a href="{s['id']}.html">Session page</a><a href="{s['id']}-handout.html">Handout</a></p>
</header>

<section><h2>Before you teach</h2><ul class="checks">{prep}</ul></section>

<aside class="caution" aria-labelledby="caution-{s['id']}"><h2 id="caution-{s['id']}">Caution</h2><p>{refs(d['guard'])}</p></aside>

<section><h2>Timed plan</h2>
<p class="plan-total">{minutes} minutes in all.</p>
<table class="plan"><thead><tr><th scope="col">Minutes</th><th scope="col">Segment</th><th scope="col">What to do</th></tr></thead><tbody>{plan}</tbody></table>
{extra}
</section>

<section class="notes"><h2>Teaching notes</h2>
<h3>Big idea</h3><p>{esc(d['big'])}</p>
<h3>Scripture</h3><dl class="ref-list">{ref_list}</dl>
<h3>Opening question</h3><p>{esc(d['opener'])}</p>
<h3>Teaching points</h3><ol class="teach-list">{teach}</ol>
{basics}
<h3>Practical step: {esc(d['skill'][0])}</h3><p>{esc(d['skill'][1])}</p>
<h3>Discussion questions</h3><ol>{qs}</ol>
<h3>{action_h}</h3><ul>{acts}</ul>
</section>

<section><h2>Likely objections</h2><dl class="qa">{objs}</dl></section>
</article>"""
    return page(f"Leader guide: {d['title']}", body, current="leader.html", kind="print-page",
                desc=f"Leader prep guide for {d['title']}.")


# ---------------------------------------------------------------- step card

def build_step_card():
    ev = C.EVERY_STEP
    rows = "".join(
        f'<li><span class="mark" aria-hidden="true"></span><span class="n">{i}</span>'
        f'<span class="what">{esc(s[1])}</span><span class="ref">{ref_a(first_ref(s[2]))}</span></li>'
        for i, s in enumerate(C.STEPS, 1))
    card = f"""<header><h1>{esc(C.STEPS_NAME)}</h1><p>From Dave Ramsey &middot; {esc(COURSE)}</p></header>
<p class="card-every"><b>{esc(ev[0])}:</b> {esc(ev[1])} <span class="ref">{refs(ev[2])}</span></p>
<ol class="card-steps">{rows}</ol>
<p class="card-notes"><b>Steps 4 and 5 are worked together.</b> Course notes: take any employer match at every step. If you keep a credit card, pay it in full every month.</p>
<p class="card-foot">{SITE_URL}</p>"""
    body = f"""{toolbar("Prints two cards on one sheet. Cut along the dashed line.")}
<div class="card-sheet">
<article class="step-card">{card}</article>
<div class="cut print-only" aria-hidden="true"></div>
<article class="step-card print-only" aria-hidden="true">{card}</article>
</div>"""
    return page("Step card", body, current="handouts.html", kind="print-page card-page",
                desc="Printable half-page card with Dave Ramsey's Baby Steps and their scripture.")


# ---------------------------------------------------------------- scripture list

def build_scripture():
    groups = []
    steps_rows = []
    for i, s in enumerate(C.STEPS, 1):
        steps_rows.append(f"<dt>{refs(s[2])}</dt><dd>Baby Step {i}, {esc(s[0][0].lower() + s[0][1:])}</dd>")
    steps_rows.append(f"<dt>{refs(C.EVERY_STEP[2])}</dt><dd>{esc(C.EVERY_STEP[0])}</dd>")
    groups.append(f"""<section class="sc-group" id="steps">
<h2>The Baby Steps</h2>
<dl class="ref-list">{''.join(steps_rows)}</dl>
</section>""")
    for key in TRACK_ORDER:
        t = C.TRACKS[key]
        blocks = []
        for s in track_sessions(key):
            d = s["d"]
            ref_list = "".join(f"<dt>{ref_a(r)}</dt><dd>{esc(p)}</dd>" for r, p in map(split_ref, d["scripture"]))
            extra = also_mentioned(d)
            extra_html = (f'<p class="also"><span>Also mentioned:</span> {"; ".join(ref_a(x) for x in extra)}</p>'
                          if extra else "")
            label = "" if s["count"] == 1 else f"Session {s['num']}: "
            blocks.append(f"""<div class="sc-session">
<h3>{label}<a href="{s['id']}.html">{esc(d['title'])}</a></h3>
<dl class="ref-list">{ref_list}</dl>
{extra_html}
</div>""")
        groups.append(f"""<section class="sc-group" id="{key}">
<h2><a href="{t['page']}">{esc(t['name'])}</a></h2>
{''.join(blocks)}
</section>""")
    body = f"""<header class="page-head wrap">
<h1>Scripture in the course</h1>
<p class="lede">Every passage the course reads, grouped by session, with a short paraphrase. Each reference opens the passage in the NIV on Bible Gateway in a new tab.</p>
<p class="head-links"><a href="#steps">Baby Steps</a><a href="#night">One Night</a><a href="#campus">4 Weeks</a><a href="#church">8 Weeks</a><a href="scripture-handout.html">Printable scripture handout</a></p>
</header>
<div class="wrap scripture-list">
{''.join(groups)}
</div>"""
    return page("Scripture in the course", body, current="handouts.html", kind="scripture-page",
                desc="Every scripture reference in Entrusted, grouped by session, each linked to the NIV.")


# ---------------------------------------------------------------- scripture handout

def _ref_key(ref):
    m = REF_RE.match(ref)
    book = m.group(1)
    num, _, name = book.partition(" ") if book[0].isdigit() else ("0", "", book)
    return (BOOKS.index(name), int(num), int(m.group(2)), int(m.group(3) or 0))


def all_scripture():
    """Every listed reference once, in Bible order: (ref, paraphrase, [where it is used])."""
    paras, where_used, order = {}, {}, []

    def add(ref, para, place):
        if ref not in where_used:
            where_used[ref] = []
            order.append(ref)
        if place not in where_used[ref]:
            where_used[ref].append(place)
        if para and len(para) > len(paras.get(ref, "")):
            paras[ref] = para
    for i, s in enumerate(C.STEPS, 1):
        for r in s[2].split(";"):
            add(r.strip(), "", f"Baby Step {i}")
    for r in C.EVERY_STEP[2].split(";"):
        add(r.strip(), "", "Every step")
    for s in SESSIONS:
        place = "One Night" if s["count"] == 1 else f"{s['track']['name']}: {s['num']}"
        for entry in s["d"]["scripture"]:
            r, p = split_ref(entry)
            add(r, p, place)
    rows = []
    for r in sorted(order, key=_ref_key):
        para = paras.get(r) or C.STEP_PARAS.get(r, "")
        rows.append((r, para, where_used[r]))
    mentioned = []
    for s in SESSIONS:
        for x in also_mentioned(s["d"]):
            if x not in where_used and x not in mentioned:
                mentioned.append(x)
    return rows, sorted(mentioned, key=_ref_key)


def build_scripture_handout():
    rows, mentioned = all_scripture()
    items = "".join(
        f'<li><span class="mark" aria-hidden="true"></span><div><p class="sh-ref">{ref_a(r)}</p>'
        f'<p class="sh-para">{esc(p)}</p><p class="sh-where">{esc(" · ".join(w))}</p></div></li>'
        for r, p, w in rows)
    also = "; ".join(ref_a(x) for x in mentioned)
    body = f"""{toolbar("Prints on one sheet, front and back. On screen, each reference opens in the NIV.")}
<article class="paper scripture-handout">
<header class="ho-head">
<p class="ho-where"><span>{esc(COURSE)}</span><span>Scripture handout</span></p>
<h1>Every passage in the course</h1>
<p class="ho-big">In Bible order, with a short summary and where each one comes up. Check the box when you have read it.</p>
<p class="ho-hint">Read them in your own Bible, or open each one in the NIV at {SITE_URL}/scripture-handout.html</p>
</header>
<ol class="sh-list">{items}</ol>
<section class="sh-also"><h2>Also referenced in the teaching</h2><p>{also}</p></section>
</article>"""
    return page("Scripture handout", body, current="handouts.html", kind="print-page",
                desc="Every passage in Entrusted on one printable sheet, in Bible order, each linked to the NIV.")


# ---------------------------------------------------------------- money basics

def build_basics():
    order = ["compound", "rule72", "debt", "apr", "taxes", "match", "stocks"]
    toc = "".join(f'<a href="#{k}">{esc(C.BASICS[k]["short"])}</a>' for k in order)
    secs = []
    for k in order:
        b = C.BASICS[k]
        more = "".join(f"<p>{refs(x)}</p>" for x in b["more"])
        links = "".join(f"<li>{out_a(x)}</li>" for x in b["links"])
        note = f'<p class="footnote">{RETURN_NOTE}</p>' if needs_return_note(b["text"]) else ""
        secs.append(f"""<section class="basic" id="{k}">
<h2>{esc(b['title'])}</h2>
<p class="basic-lead">{refs(b['text'])}</p>
{fig(b['graphic'], 'p-' + k)}
{note}
{more}
<div class="read-more"><p>Read more</p><ul>{links}</ul></div>
</section>""")
    sources = "".join(f"<li>{out_a(k)}</li>" for k in C.LINKS)
    body = f"""<header class="page-head wrap">
<h1>Money basics</h1>
<p class="lede">The practical side of the course: how compound interest works for you and against you, APR and APY, how income tax brackets work, the 401(k) and its match, and what the stock market is. These are the headlines from the One Night session, with a little more on each.</p>
<p class="head-links">{toc}</p>
</header>
<div class="wrap basics">
{''.join(secs)}
<section class="basic" id="cheat-sheets">
<h2>Cheat sheets</h2>
<div class="sheets-2">{prep_worksheet(C.APR)}{prep_worksheet(C.ACCOUNTS)}</div>
</section>
<section class="basic" id="read-more">
<h2>Articles and tools</h2>
<ul class="source-list">{sources}<li><a href="compound.html">Compound interest calculator</a> <span class="src">on this site</span></li><li><a href="tools.html">Debt payoff calculator</a> <span class="src">on this site</span></li></ul>
<p class="note">Teaching, not financial advice. This course recommends no specific investments. Examples assume a 7% return; returns are not guaranteed. Contribution limits and tax rules change, so check current figures before you plan.</p>
</section>
</div>"""
    return page("Money basics", body, current="basics.html", kind="basics-page",
                desc="Compound interest, the rule of 72, APR and APY, the 401(k) match and the stock market, with charts and articles.")


# ---------------------------------------------------------------- index pages

def build_handouts():
    groups = []
    for key in TRACK_ORDER:
        t = C.TRACKS[key]
        items = "".join(
            f'<li><a href="{s["id"]}-handout.html">'
            f'{"" if s["count"] == 1 else "Session " + str(s["num"]) + ": "}{esc(s["d"]["title"])}</a></li>'
            for s in track_sessions(key))
        groups.append(f'<section class="idx-group"><h2><a href="{t["page"]}">{esc(t["name"])}</a></h2>'
                      f'<p class="idx-len">{esc(t["length"])}</p><ul class="idx-list">{items}</ul></section>')
    body = f"""<header class="page-head wrap">
<h1>Handouts</h1>
<p class="lede">One handout per session, each on a single sheet printed front and back: notes on the front, the worksheet on the back. Print one per person.</p>
</header>
<div class="wrap">
<section class="idx-group idx-everyone">
<h2>For every format</h2>
<ul class="idx-list">
<li><a href="step-card.html">The Baby Steps card</a><span>Half-page card, two to a sheet</span></li>
<li><a href="scripture-handout.html">Scripture handout</a><span>Every passage on one sheet, in Bible order, each linked to the NIV on screen</span></li>
<li><a href="scripture.html">Scripture by session</a><span>Every passage, grouped by session, with links to the NIV</span></li>
<li><a href="basics.html">Money basics</a><span>Compound interest, APR and APY, tax brackets, the 401(k) match and the stock market, with cheat sheets</span></li>
</ul>
</section>
<div class="idx-grid">{''.join(groups)}</div>
</div>"""
    return page("Handouts", body, current="handouts.html", kind="index-page",
                desc="Printable handouts for every Entrusted session, the Baby Steps card and the scripture handout.")


def build_leader_index():
    groups = []
    for key in TRACK_ORDER:
        t = C.TRACKS[key]
        items = "".join(
            f'<li><a href="{s["id"]}-leader.html">'
            f'{"" if s["count"] == 1 else "Session " + str(s["num"]) + ": "}{esc(s["d"]["title"])}</a></li>'
            for s in track_sessions(key))
        groups.append(f'<section class="idx-group"><h2><a href="{t["page"]}">{esc(t["name"])}</a></h2>'
                      f'<p class="idx-len">{esc(t["length"])}</p><ul class="idx-list">{items}</ul></section>')
    body = f"""<header class="page-head wrap">
<h1>Leader prep</h1>
<p class="lede">Every session has a leader guide. Each one follows the same order: what to do before you teach, a caution to keep in mind, the timed plan, the full teaching notes, and the questions people are likely to ask.</p>
</header>
<div class="wrap">
<section class="prep-note">
<h2>How to prepare</h2>
<ol>
<li>Read the guide's passages in your own Bible, ideally twice, a few days before you teach.</li>
<li>Work through the handout's worksheet yourself so you can show a real example.</li>
<li>Read the caution and the likely objections, so you are ready for the conversation the session tends to start.</li>
<li>Print a handout for each person, plus the <a href="step-card.html">Baby Steps card</a> when the guide calls for it, and the <a href="scripture-handout.html">scripture handout</a> for anyone who wants to read ahead.</li>
<li>Skim the <a href="basics.html">Money Basics page</a> so you can answer practical questions about compound interest, APR and APY, tax brackets, the 401(k) and the stock market.</li>
<li>Open the session page on the screen you will teach from, and the <a href="tools.html">calculators</a> if the session uses them.</li>
</ol>
</section>
<div class="idx-grid">{''.join(groups)}</div>
</div>"""
    return page("Leader prep", body, current="leader.html", kind="index-page",
                desc="Leader prep guides for every Entrusted session.")


# ---------------------------------------------------------------- tools

CALC_CORE = """<script id="calc-core">
function growth(monthly, startAge, endAge, ratePct) {
  var n = Math.round((endAge - startAge) * 12);
  if (n <= 0) return { months: 0, contributed: 0, value: 0 };
  var i = ratePct / 100 / 12;
  var value = i === 0 ? monthly * n : monthly * (Math.pow(1 + i, n) - 1) / i;
  return { months: n, contributed: monthly * n, value: value };
}
function payoff(balance, aprPct, payment) {
  var i = aprPct / 100 / 12;
  var first = balance * i;
  if (payment <= first + 1e-9) return { never: true, firstInterest: first };
  var b = balance, months = 0, interest = 0;
  while (b > 0.005 && months < 1200) {
    var charge = b * i;
    interest += charge;
    b = b + charge - payment;
    months++;
  }
  return { never: false, months: months, interest: interest, capped: b > 0.005 };
}
</script>"""

CALC_UI = """<script>
(function () {
  var money = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
  var cents = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 2, maximumFractionDigits: 2 });
  function val(id) { var v = document.getElementById(id).value.trim(); return v === '' ? NaN : Number(v); }
  function plural(n, w) { return n + ' ' + w + (n === 1 ? '' : 's'); }
  function duration(m) {
    var y = Math.floor(m / 12), r = m % 12;
    if (!y) return plural(r, 'month');
    if (!r) return plural(y, 'year');
    return plural(y, 'year') + ', ' + plural(r, 'month');
  }

  var gForm = document.getElementById('growth-form'), gOut = document.getElementById('g-out');
  function runGrowth() {
    var p = val('g-amt'), a = val('g-start'), b = val('g-end'), r = val('g-rate');
    if (!(p >= 0) || !(a >= 0) || !(b > 0) || !(r >= 0)) {
      gOut.innerHTML = '<p class="msg">Enter a number of zero or more in each box.</p>'; return;
    }
    if (b <= a) { gOut.innerHTML = '<p class="msg">The end age has to be later than the start age.</p>'; return; }
    var now = growth(p, a, b, r), later = a + 10, rows, tail;
    rows = '<tr><th scope="row">Start at ' + a + '</th><td>' + money.format(now.contributed) + '</td><td>' + money.format(now.value) + '</td></tr>';
    if (later < b) {
      var w = growth(p, later, b, r);
      rows += '<tr><th scope="row">Start at ' + later + '</th><td>' + money.format(w.contributed) + '</td><td>' + money.format(w.value) + '</td></tr>';
      tail = '<p class="diff">Waiting ten years saves ' + money.format(now.contributed - w.contributed) +
             ' in contributions and costs <strong>' + money.format(now.value - w.value) + '</strong> by age ' + b + '.</p>';
    } else {
      tail = '<p class="msg">Starting ten years later, at ' + later + ', leaves no time before age ' + b + '.</p>';
    }
    gOut.innerHTML = '<table class="out"><thead><tr><th scope="col">Plan</th><th scope="col">You put in</th><th scope="col">Value at ' + b +
                     '</th></tr></thead><tbody>' + rows + '</tbody></table>' + tail;
  }

  var dForm = document.getElementById('debt-form'), dOut = document.getElementById('d-out');
  function runDebt() {
    var bal = val('d-bal'), apr = val('d-apr'), pay = val('d-pay');
    if (!(bal > 0)) { dOut.innerHTML = '<p class="msg">Enter a balance greater than zero.</p>'; return; }
    if (!(apr >= 0)) { dOut.innerHTML = '<p class="msg">Enter an APR of zero or more.</p>'; return; }
    if (!(pay > 0)) { dOut.innerHTML = '<p class="msg">Enter a monthly payment greater than zero.</p>'; return; }
    var res = payoff(bal, apr, pay);
    if (res.never) {
      dOut.innerHTML = '<p class="warn">At ' + cents.format(pay) + ' a month, this balance will never be paid off. The first month\\'s interest alone is ' +
                       cents.format(res.firstInterest) + ', so the payment has to be more than that before the balance starts to shrink.</p>';
      return;
    }
    if (res.capped) { dOut.innerHTML = '<p class="warn">At this payment the balance would take more than 100 years to pay off.</p>'; return; }
    dOut.innerHTML = '<dl class="out-dl"><div><dt>Months to pay off</dt><dd>' + res.months + ' <span>(' + duration(res.months) + ')</span></dd></div>' +
                     '<div><dt>Total interest</dt><dd>' + money.format(res.interest) + '</dd></div>' +
                     '<div><dt>Total paid</dt><dd>' + money.format(bal + res.interest) + '</dd></div></dl>';
  }

  [[gForm, runGrowth], [dForm, runDebt]].forEach(function (pair) {
    pair[0].addEventListener('input', pair[1]);
    pair[0].addEventListener('submit', function (e) { e.preventDefault(); pair[1](); });
    pair[1]();
  });
})();
</script>"""


def build_tools():
    body = """<header class="page-head wrap">
<h1>Tools</h1>
<p class="lede">Two calculators used in the sessions. They run entirely in your browser: nothing you type is stored or sent anywhere.</p>
<p class="tools-more">For a growth chart, a year-by-year spreadsheet you can edit, and an opportunity cost calculator, open the <a href="compound.html">compound interest page</a>. For plain explanations with charts, see <a href="basics.html">Money basics</a>.</p>
</header>
<div class="wrap tools">
<section class="tool" id="growth" aria-labelledby="growth-h">
<h2 id="growth-h">Compound growth</h2>
<p>What a steady monthly amount could grow to by a given age, and what starting ten years later costs.</p>
<form id="growth-form" class="calc" novalidate>
<label for="g-amt">Monthly amount ($)<input id="g-amt" type="number" inputmode="decimal" min="0" step="any" value="200"></label>
<label for="g-start">Start age<input id="g-start" type="number" inputmode="numeric" min="0" max="110" step="1" value="22"></label>
<label for="g-end">End age<input id="g-end" type="number" inputmode="numeric" min="1" max="120" step="1" value="65"></label>
<label for="g-rate">Annual return (%)<input id="g-rate" type="number" inputmode="decimal" min="0" max="30" step="0.1" value="7"></label>
<button type="submit" class="calc-btn">Calculate</button>
</form>
<div class="results" id="g-out" aria-live="polite"></div>
<p class="note">The return is an assumption, compounded monthly. Real markets rise and fall, and returns are not guaranteed. This is a teaching tool, not investment advice.</p>
<details><summary>How this is calculated</summary>
<p>Ending value = P &times; ((1 + r/12)<sup>n</sup> &minus; 1) &divide; (r/12), where P is the monthly amount, r is the annual return as a decimal, and n is the number of months between the two ages. Each deposit is made at the end of the month.</p>
</details>
</section>

<section class="tool" id="debt" aria-labelledby="debt-h">
<h2 id="debt-h">Debt payoff</h2>
<p>How long a balance takes to pay off at a fixed monthly payment, and what it costs in interest.</p>
<form id="debt-form" class="calc" novalidate>
<label for="d-bal">Balance ($)<input id="d-bal" type="number" inputmode="decimal" min="0" step="any" value="5000"></label>
<label for="d-apr">APR (%)<input id="d-apr" type="number" inputmode="decimal" min="0" max="100" step="0.1" value="24"></label>
<label for="d-pay">Monthly payment ($)<input id="d-pay" type="number" inputmode="decimal" min="0" step="any" value="200"></label>
<button type="submit" class="calc-btn">Calculate</button>
</form>
<div class="results" id="d-out" aria-live="polite"></div>
<p class="note">Assumes the APR stays the same and nothing new is charged. Interest is figured monthly at the APR divided by 12.</p>
</section>
</div>"""
    return page("Tools", body, current="tools.html", kind="tools-page",
                desc="Compound growth and debt payoff calculators. Nothing is stored or sent.",
                script=CALC_CORE + "\n" + CALC_UI)


# ---------------------------------------------------------------- compound interest page

CI_CORE = r"""<script id="ci-core">
function planRows(base, overrides) {
  var rows = [], rate = base.rate, monthly = base.monthly;
  for (var age = base.start; age < base.end; age++) {
    var o = overrides[age] || {};
    if (o.rate !== undefined) rate = o.rate;
    if (o.monthly !== undefined) monthly = o.monthly;
    rows.push({ age: age, rate: rate, monthly: monthly, lump: o.lump || 0,
                rateSet: o.rate !== undefined, monthlySet: o.monthly !== undefined });
  }
  return rows;
}
function simulate(rows, fromAge, startBalance) {
  var bal = 0, total = 0, years = [], points = [];
  for (var k = 0; k < rows.length; k++) {
    var r = rows[k];
    if (r.age < fromAge) continue;
    if (r.age === fromAge) {
      bal += startBalance; total += startBalance;
      points.push({ age: r.age, value: bal, put: total });
    }
    var begin = bal, put = 0, dep = r.lump, lump;
    if (bal + dep < 0) dep = -bal;
    bal += dep; put += dep; lump = dep;
    var i = r.rate / 1200;
    for (var m = 0; m < 12; m++) {
      bal = bal * (1 + i);
      dep = r.monthly;
      if (bal + dep < 0) dep = -bal;
      bal += dep; put += dep;
    }
    total += put;
    years.push({ age: r.age, rate: r.rate, monthly: r.monthly, lump: lump, put: put,
                 growth: bal - begin - put, total: total, balance: bal });
    points.push({ age: r.age + 1, value: bal, put: total });
  }
  return { years: years, points: points };
}
var PER_YEAR = { once: 0, day: 365, week: 52, month: 12, year: 1 };
function oppCost(price, freq, years, ratePct) {
  var n = Math.round(years * 12), i = ratePct / 1200, bal = 0, spent = 0;
  for (var m = 0; m < n; m++) {
    var dep;
    if (freq === 'once') dep = m === 0 ? price : 0;
    else if (freq === 'year') dep = m % 12 === 0 ? price : 0;
    else dep = price * PER_YEAR[freq] / 12;
    bal = (bal + dep) * (1 + i);
    spent += dep;
  }
  return { spent: spent, value: bal };
}
</script>"""

CI_UI = r"""<script>
(function () {
  'use strict';
  var C_VALUE = '#157a4b', C_PUT = '#b8862b', C_CMP = '#7d837e', C_GRID = '#e6dfd0', C_AXIS = '#bdb4a2',
      C_SURF = '#fffdf8', C_INK2 = '#4e5651', SVGNS = 'http://www.w3.org/2000/svg';
  var money = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
  var money2 = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 2, maximumFractionDigits: 2 });
  function $(id) { return document.getElementById(id); }
  function val(id) { var v = String($(id).value).trim(); return v === '' ? NaN : Number(v); }
  function fmt(v) { v = Math.round(v); if (v === 0) v = 0; return money.format(v); }
  function amt(v) { return v % 1 ? money2.format(v) : money.format(v); }
  function plain(v) { return String(Math.round(v * 100) / 100); }
  function addStat(dl, label, value) {
    var d = document.createElement('div'), dt = document.createElement('dt'), dd = document.createElement('dd');
    dt.textContent = label; dd.textContent = value; d.appendChild(dt); d.appendChild(dd); dl.appendChild(d);
  }
  function say(box, text) { var p = document.createElement('p'); p.className = 'msg'; p.textContent = text; box.appendChild(p); }

  /* ---------- tabs */
  var tabs = [].slice.call(document.querySelectorAll('[role="tab"]'));
  function select(tab, focus, writeHash) {
    tabs.forEach(function (t) {
      var on = t === tab;
      t.setAttribute('aria-selected', on ? 'true' : 'false');
      t.tabIndex = on ? 0 : -1;
      $(t.getAttribute('aria-controls')).hidden = !on;
    });
    $('plan').hidden = tab.id === 'opportunity-cost';
    if (focus) tab.focus();
    if (writeHash) { try { history.replaceState(null, '', '#' + tab.id); } catch (e) {} }
    if (tab.id === 'chart') drawChart();
  }
  tabs.forEach(function (t, i) {
    t.addEventListener('click', function () { select(t, false, true); });
    t.addEventListener('keydown', function (e) {
      var j = null;
      if (e.key === 'ArrowRight') j = (i + 1) % tabs.length;
      else if (e.key === 'ArrowLeft') j = (i - 1 + tabs.length) % tabs.length;
      else if (e.key === 'Home') j = 0;
      else if (e.key === 'End') j = tabs.length - 1;
      if (j !== null) { e.preventDefault(); select(tabs[j], true, true); }
    });
  });

  /* ---------- the shared plan */
  var overrides = {}, plan = null, rows = [], sim = null, builtFor = '';
  function readPlan() {
    var p = { bal: val('p-bal'), monthly: val('p-monthly'), rate: val('p-rate'), start: val('p-start'), end: val('p-end') }, err = '';
    if (!(p.bal >= 0)) err = 'Enter a starting balance of zero or more.';
    else if (!isFinite(p.monthly)) err = 'Enter a monthly amount. Use 0 for none.';
    else if (!(p.rate > -100 && p.rate <= 100)) err = 'Enter an annual return between -99 and 100 percent.';
    else if (!(p.start >= 0 && p.start <= 110 && p.start % 1 === 0)) err = 'Enter the start age as a whole number.';
    else if (!(p.end % 1 === 0 && p.end > p.start)) err = 'The end age has to be a whole number later than the start age.';
    else if (p.end - p.start > 80) err = 'Keep the plan to 80 years or fewer.';
    p.error = err;
    return p;
  }
  function changedYears() {
    var n = 0;
    for (var k in overrides) {
      var a = +k, o = overrides[k];
      if (a >= plan.start && a < plan.end && (o.rate !== undefined || o.monthly !== undefined || o.lump)) n++;
    }
    return n;
  }
  function refresh() {
    var p = readPlan(), msg = $('plan-msg');
    if (p.error) {
      msg.textContent = p.error; msg.hidden = false;
      document.body.classList.add('ci-stale');
      return;
    }
    msg.hidden = true;
    document.body.classList.remove('ci-stale');
    plan = p;
    rows = planRows(plan, overrides);
    sim = simulate(rows, plan.start, plan.bal);
    var n = changedYears();
    $('plan-note').hidden = !n;
    $('plan-note-text').textContent = n === 1
      ? '1 year has its own numbers in the Year by year tab, and the chart includes them.'
      : n + ' years have their own numbers in the Year by year tab, and the chart includes them.';
    updateStats();
    drawChart();
    renderSheet();
  }
  function resetOverrides() { overrides = {}; builtFor = ''; refresh(); }
  $('plan-form').addEventListener('input', refresh);
  $('plan-form').addEventListener('submit', function (e) { e.preventDefault(); });
  $('note-reset').addEventListener('click', resetOverrides);

  /* ---------- chart tab */
  function compareSim() {
    var on = $('c-cmp').checked, d = val('c-delay'), cmsg = $('cmp-msg');
    $('lg-cmp').hidden = true; cmsg.hidden = true;
    if (!on) return null;
    if (!(d >= 1 && d % 1 === 0)) { cmsg.textContent = 'Enter a whole number of years to compare.'; cmsg.hidden = false; return null; }
    var from = plan.start + d;
    if (from >= plan.end) {
      cmsg.textContent = 'Starting ' + d + ' years later, at ' + from + ', leaves no time before age ' + plan.end + '.';
      cmsg.hidden = false; return null;
    }
    $('lg-cmp').hidden = false;
    $('lg-cmp-text').textContent = 'Total value if you start at ' + from;
    return simulate(rows, from, plan.bal);
  }
  function updateStats() {
    var dl = $('c-stats'), last = sim.points[sim.points.length - 1], cmp = compareSim();
    dl.textContent = '';
    addStat(dl, 'Value at ' + plan.end, fmt(last.value));
    addStat(dl, 'You put in', fmt(last.put));
    addStat(dl, 'Growth', fmt(last.value - last.put));
    if (cmp) {
      var cl = cmp.points[cmp.points.length - 1];
      addStat(dl, 'If you start at ' + cmp.points[0].age, fmt(cl.value));
      addStat(dl, 'Cost of waiting', fmt(last.value - cl.value));
    }
  }
  ['c-cmp', 'c-delay'].forEach(function (id) {
    $(id).addEventListener('input', function () { if (plan && !plan.error) { updateStats(); drawChart(); } });
  });

  var box = $('chart-box'), tip = $('chart-tip'), live = $('chart-live'), geo = null, hoverIdx = null, focused = false;
  function el(tag, attrs, parent) {
    var e = document.createElementNS(SVGNS, tag);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }
  function niceStep(raw) {
    var p = Math.pow(10, Math.floor(Math.log(raw) / Math.LN10)), f = raw / p;
    return (f <= 1 ? 1 : f <= 2 ? 2 : f <= 2.5 ? 2.5 : f <= 5 ? 5 : 10) * p;
  }
  function tickLabel(v, top) {
    if (top < 10000) return money.format(v);
    if (v === 0) return '$0';
    if (v >= 1e6) return '$' + (+(v / 1e6).toFixed(2)) + 'M';
    return '$' + (+(v / 1e3).toFixed(1)) + 'K';
  }
  function drawChart() {
    if (!sim || $('panel-chart').hidden) return;
    var W = box.clientWidth;
    if (!W) return;
    var narrow = W < 560, H = narrow ? 280 : 390;
    var m = { l: narrow ? 52 : 66, r: narrow ? 14 : 22, t: 30, b: 42 };
    var pts = sim.points, cmp = compareSim(), cpts = cmp ? cmp.points : [];
    var a0 = plan.start, a1 = plan.end, pw = W - m.l - m.r, ph = H - m.t - m.b, max = 0;
    pts.forEach(function (p) { max = Math.max(max, p.value, p.put); });
    cpts.forEach(function (p) { max = Math.max(max, p.value); });
    if (max <= 0) max = 1;
    var step = niceStep(max / 4), nTicks = Math.ceil(max / step - 1e-9), top = nTicks * step;
    function x(a) { return m.l + (a - a0) / (a1 - a0) * pw; }
    function y(v) { return m.t + ph - Math.max(0, v) / top * ph; }

    var old = box.querySelector('svg');
    if (old) box.removeChild(old);
    var svg = el('svg', { width: W, height: H, viewBox: '0 0 ' + W + ' ' + H, 'aria-hidden': 'true', focusable: 'false' });

    for (var k = 0; k <= nTicks; k++) {
      var v = k * step, yy = Math.round(y(v)) + 0.5;
      el('line', { x1: m.l, x2: W - m.r, y1: yy, y2: yy, stroke: k === 0 ? C_AXIS : C_GRID, 'stroke-width': 1 }, svg);
      el('text', { x: m.l - 8, y: yy + 4, 'text-anchor': 'end', 'class': 'ax' }, svg).textContent = tickLabel(v, top);
    }
    var span = a1 - a0, choices = [1, 2, 5, 10, 20], most = narrow ? 5 : 9, xs = 20;
    for (var q = 0; q < choices.length; q++) { if (span / choices[q] <= most) { xs = choices[q]; break; } }
    for (var a = Math.ceil(a0 / xs) * xs; a <= a1; a += xs) {
      var xx = Math.round(x(a)) + 0.5;
      el('line', { x1: xx, x2: xx, y1: m.t + ph, y2: m.t + ph + 5, stroke: C_AXIS }, svg);
      el('text', { x: xx, y: m.t + ph + 20, 'text-anchor': 'middle', 'class': 'ax' }, svg).textContent = a;
    }
    el('text', { x: W - m.r, y: H - 3, 'text-anchor': 'end', 'class': 'ax' }, svg).textContent = 'Age';

    function path(list, get) {
      return list.map(function (p, i) { return (i ? 'L' : 'M') + x(p.age).toFixed(1) + ' ' + y(get(p)).toFixed(1); }).join('');
    }
    function base(p) { return Math.max(0, Math.min(p.put, p.value)); }
    var back = pts.slice().reverse();
    el('path', { d: path(pts, function (p) { return p.value; }) + back.map(function (p) {
      return 'L' + x(p.age).toFixed(1) + ' ' + y(base(p)).toFixed(1); }).join('') + 'Z', fill: C_VALUE, 'fill-opacity': 0.12 }, svg);
    el('path', { d: path(pts, base) + 'L' + x(pts[pts.length - 1].age).toFixed(1) + ' ' + y(0).toFixed(1) +
      'L' + x(pts[0].age).toFixed(1) + ' ' + y(0).toFixed(1) + 'Z', fill: C_PUT, 'fill-opacity': 0.16 }, svg);
    var line = { fill: 'none', 'stroke-width': 2, 'stroke-linejoin': 'round', 'stroke-linecap': 'round' };
    function stroke(d, color, extra) {
      var at = { d: d, stroke: color };
      for (var k in line) at[k] = line[k];
      for (var j in extra || {}) at[j] = extra[j];
      return el('path', at, svg);
    }
    if (cpts.length > 1) stroke(path(cpts, function (p) { return p.value; }), C_CMP, { 'stroke-dasharray': '6 5' });
    stroke(path(pts, function (p) { return p.put; }), C_PUT);
    stroke(path(pts, function (p) { return p.value; }), C_VALUE);

    var last = pts[pts.length - 1], ex = x(last.age), ey = y(last.value);
    el('circle', { cx: ex, cy: ey, r: 4, fill: C_VALUE, stroke: C_SURF, 'stroke-width': 2 }, svg);
    el('text', { x: ex - 9, y: Math.max(14, ey - 12), 'text-anchor': 'end', 'class': 'end-label' }, svg).textContent = fmt(last.value);

    var cross = el('line', { y1: m.t, y2: m.t + ph, stroke: C_INK2, 'stroke-width': 1, visibility: 'hidden' }, svg);
    var dots = [C_VALUE, C_PUT, C_CMP].map(function (c) {
      return el('circle', { r: 4, fill: c, stroke: C_SURF, 'stroke-width': 2, visibility: 'hidden' }, svg);
    });
    var hit = el('rect', { x: m.l - 6, y: 0, width: pw + 12, height: m.t + ph + 8, fill: 'transparent' }, svg);
    box.insertBefore(svg, tip);
    geo = { x: x, y: y, pts: pts, cpts: cpts, cross: cross, dots: dots, m: m, W: W };
    function track(e) {
      var r = svg.getBoundingClientRect();
      show(Math.round((e.clientX - r.left - m.l) / pw * (a1 - a0)), false);
    }
    hit.addEventListener('pointermove', track);
    hit.addEventListener('pointerdown', track);
    hit.addEventListener('pointerleave', function () { if (!focused) hide(); });
    if (hoverIdx !== null && focused) show(hoverIdx, false);
  }
  function place(dot, cx, cy) { dot.setAttribute('cx', cx); dot.setAttribute('cy', cy); dot.setAttribute('visibility', 'visible'); }
  function tipRow(value, label, keyClass) {
    var row = document.createElement('p'), key = document.createElement('span'), b = document.createElement('strong'), s = document.createElement('span');
    row.className = 'tip-row'; key.className = 'key ' + keyClass; b.textContent = value; s.textContent = label;
    row.appendChild(key); row.appendChild(b); row.appendChild(s); tip.appendChild(row);
  }
  function show(idx, announce) {
    if (!geo) return;
    var pts = geo.pts;
    idx = Math.max(0, Math.min(pts.length - 1, idx));
    hoverIdx = idx;
    var p = pts[idx], xx = geo.x(p.age), c = null;
    geo.cpts.forEach(function (q) { if (q.age === p.age) c = q; });
    geo.cross.setAttribute('x1', xx); geo.cross.setAttribute('x2', xx); geo.cross.setAttribute('visibility', 'visible');
    place(geo.dots[0], xx, geo.y(p.value));
    place(geo.dots[1], xx, geo.y(p.put));
    if (c) place(geo.dots[2], xx, geo.y(c.value)); else geo.dots[2].setAttribute('visibility', 'hidden');
    tip.textContent = '';
    var h = document.createElement('p'); h.className = 'tip-h'; h.textContent = 'Age ' + p.age; tip.appendChild(h);
    tipRow(fmt(p.value), 'Total value', 'k-value');
    tipRow(fmt(p.put), 'You put in', 'k-put');
    tipRow(fmt(p.value - p.put), 'Growth', 'k-none');
    if (c) tipRow(fmt(c.value), 'If you start at ' + geo.cpts[0].age, 'k-cmp');
    tip.hidden = false;
    var tw = tip.offsetWidth, left = xx + 14;
    if (left + tw > geo.W - 4) left = xx - tw - 14;
    if (left < 4) left = 4;
    tip.style.left = left + 'px';
    tip.style.top = (geo.m.t + 4) + 'px';
    if (announce) live.textContent = 'Age ' + p.age + ': total value ' + fmt(p.value) + ', you put in ' + fmt(p.put) +
      (c ? ', if you start at ' + geo.cpts[0].age + ' ' + fmt(c.value) : '') + '.';
  }
  function hide() {
    hoverIdx = null; tip.hidden = true;
    if (!geo) return;
    geo.cross.setAttribute('visibility', 'hidden');
    geo.dots.forEach(function (d) { d.setAttribute('visibility', 'hidden'); });
  }
  box.addEventListener('focus', function () { focused = true; if (geo) show(hoverIdx === null ? geo.pts.length - 1 : hoverIdx, true); });
  box.addEventListener('blur', function () { focused = false; hide(); });
  box.addEventListener('keydown', function (e) {
    if (!geo) return;
    var i = hoverIdx === null ? geo.pts.length - 1 : hoverIdx, n = null;
    if (e.key === 'ArrowRight') n = i + 1;
    else if (e.key === 'ArrowLeft') n = i - 1;
    else if (e.key === 'Home') n = 0;
    else if (e.key === 'End') n = geo.pts.length - 1;
    else if (e.key === 'Escape') { hide(); return; }
    if (n !== null) { e.preventDefault(); show(n, true); }
  });
  var pending = false;
  function schedule() {
    if (pending) return;
    pending = true;
    (window.requestAnimationFrame || setTimeout)(function () { pending = false; drawChart(); });
  }
  if (window.ResizeObserver) new ResizeObserver(schedule).observe(box);
  else window.addEventListener('resize', schedule);

  /* ---------- year by year tab */
  var tbody = $('sheet-body'), tfoot = $('sheet-foot');
  var KINDS = [['rate', 'Annual return, percent'], ['monthly', 'Monthly amount, dollars'], ['lump', 'One-time amount, dollars']];
  function cell(tr, cls, text) { var td = document.createElement('td'); if (cls) td.className = cls; if (text !== undefined) td.textContent = text; tr.appendChild(td); return td; }
  function buildRows() {
    builtFor = plan.start + '-' + plan.end;
    tbody.textContent = '';
    rows.forEach(function (r, i) {
      var tr = document.createElement('tr'), th = document.createElement('th');
      th.scope = 'row'; th.textContent = r.age; tr.appendChild(th);
      cell(tr, 'yr', i + 1);
      KINDS.forEach(function (kind) {
        var td = cell(tr, 'edit'), inp = document.createElement('input'), o = overrides[r.age] || {};
        inp.type = 'text'; inp.inputMode = 'decimal'; inp.autocomplete = 'off';
        inp.setAttribute('data-kind', kind[0]); inp.setAttribute('data-age', r.age);
        inp.setAttribute('aria-label', kind[1] + ', age ' + r.age);
        if (o[kind[0]] !== undefined && !(kind[0] === 'lump' && !o.lump)) inp.value = plain(o[kind[0]]);
        td.appendChild(inp);
      });
      for (var j = 0; j < 4; j++) cell(tr, 'out-c');
      tbody.appendChild(tr);
    });
  }
  function renderSheet() {
    if (!sim) return;
    if (builtFor !== plan.start + '-' + plan.end) buildRows();
    var trs = tbody.rows, putSum = 0, growSum = 0;
    sim.years.forEach(function (yv, i) {
      var r = rows[i], tr = trs[i];
      if (!tr) return;
      var ins = tr.querySelectorAll('input'), outs = tr.querySelectorAll('td.out-c');
      ins[0].placeholder = plain(r.rate); ins[0].classList.toggle('set', r.rateSet);
      ins[1].placeholder = plain(r.monthly); ins[1].classList.toggle('set', r.monthlySet);
      ins[2].classList.toggle('set', !!r.lump);
      outs[0].textContent = fmt(yv.put); outs[1].textContent = fmt(yv.growth);
      outs[2].textContent = fmt(yv.total); outs[3].textContent = fmt(yv.balance);
      outs[1].classList.toggle('neg', yv.growth < -0.5);
      putSum += yv.put; growSum += yv.growth;
    });
    var last = sim.years[sim.years.length - 1];
    tfoot.textContent = '';
    var tr = document.createElement('tr'), th = document.createElement('th');
    th.scope = 'row'; th.colSpan = 5; th.textContent = plan.bal ? 'Totals (starting balance ' + fmt(plan.bal) + ')' : 'Totals';
    tr.appendChild(th);
    cell(tr, '', fmt(putSum)); cell(tr, '', fmt(growSum)); cell(tr, '', fmt(last.total)); cell(tr, '', fmt(last.balance));
    tfoot.appendChild(tr);
  }
  tbody.addEventListener('input', function (e) {
    var inp = e.target;
    if (inp.tagName !== 'INPUT') return;
    var age = +inp.getAttribute('data-age'), kind = inp.getAttribute('data-kind');
    var raw = inp.value.replace(/[$,%\s]/g, ''), o = overrides[age] || (overrides[age] = {});
    if (raw === '-' || raw === '.' || raw === '-.') return;
    var n = Number(raw);
    if (raw === '') { delete o[kind]; inp.removeAttribute('aria-invalid'); }
    else if (isFinite(n) && !(kind === 'rate' && (n <= -100 || n > 100))) { o[kind] = n; inp.removeAttribute('aria-invalid'); }
    else { delete o[kind]; inp.setAttribute('aria-invalid', 'true'); }
    refresh();
  });
  tbody.addEventListener('keydown', function (e) {
    var inp = e.target;
    if (inp.tagName !== 'INPUT') return;
    var d = e.key === 'ArrowDown' || (e.key === 'Enter' && !e.shiftKey) ? 1 : e.key === 'ArrowUp' || (e.key === 'Enter' && e.shiftKey) ? -1 : 0;
    if (!d) return;
    var tr = inp.parentNode.parentNode, col = [].indexOf.call(tr.querySelectorAll('input'), inp);
    var next = d > 0 ? tr.nextElementSibling : tr.previousElementSibling;
    e.preventDefault();
    if (next) { var t = next.querySelectorAll('input')[col]; t.focus(); t.select(); }
  });
  $('s-reset').addEventListener('click', resetOverrides);
  $('s-print').addEventListener('click', function () { window.print(); });
  $('s-csv').addEventListener('click', function () {
    if (!sim) return;
    var lines = ['Age,Year,Annual return (%),Monthly amount,One-time amount,Put in this year,Growth this year,Total put in,Balance at year end'];
    if (plan.bal) lines.push('Start,,,,,,,' + plan.bal.toFixed(2) + ',' + plan.bal.toFixed(2));
    sim.years.forEach(function (y, i) {
      lines.push([y.age, i + 1, y.rate, y.monthly.toFixed(2), y.lump.toFixed(2), y.put.toFixed(2),
                  y.growth.toFixed(2), y.total.toFixed(2), y.balance.toFixed(2)].join(','));
    });
    var url = URL.createObjectURL(new Blob([lines.join('\r\n') + '\r\n'], { type: 'text/csv' }));
    var a = document.createElement('a');
    a.href = url; a.download = 'entrusted-year-by-year.csv';
    document.body.appendChild(a); a.click();
    setTimeout(function () { URL.revokeObjectURL(url); document.body.removeChild(a); }, 0);
  });

  /* ---------- opportunity cost tab */
  var WORDS = { once: 'once', day: 'every day', week: 'every week', month: 'every month', year: 'every year' };
  function runCost() {
    var out = $('cost-out'), price = val('o-price'), freq = $('o-freq').value, years = val('o-years'), rate = val('o-rate');
    out.textContent = '';
    if (!(price > 0)) return say(out, 'Enter a purchase amount greater than zero.');
    if (!(years >= 1 && years <= 60 && years % 1 === 0)) return say(out, 'Enter a whole number of years from 1 to 60.');
    if (!(rate > -100 && rate <= 100)) return say(out, 'Enter an annual return between -99 and 100 percent.');
    var r = oppCost(price, freq, years, rate), dl = document.createElement('dl');
    dl.className = 'stats';
    addStat(dl, freq === 'once' ? 'Spent' : 'Spent over ' + years + ' years', fmt(r.spent));
    addStat(dl, 'Could grow to in ' + years + ' years', fmt(r.value));
    addStat(dl, 'Growth given up', fmt(r.value - r.spent));
    out.appendChild(dl);
    var p = document.createElement('p');
    p.className = 'cost-line';
    p.textContent = freq === 'once'
      ? 'Spending ' + amt(price) + ' once gives up about ' + fmt(r.value) + ' in ' + years + (years === 1 ? ' year' : ' years') +
        ', if that money were invested at ' + rate + '% a year instead.'
      : 'Spending ' + amt(price) + ' ' + WORDS[freq] + ' for ' + years + (years === 1 ? ' year' : ' years') + ' adds up to ' + fmt(r.spent) +
        '. Invested instead at ' + rate + '% a year, it could grow to about ' + fmt(r.value) + '.';
    out.appendChild(p);
    var hs = [5, 10, 20, 30, 40];
    if (hs.indexOf(years) < 0) hs.push(years);
    hs.sort(function (a, b) { return a - b; });
    var t = document.createElement('table'), cap = document.createElement('caption'), thead = document.createElement('thead'), tb = document.createElement('tbody');
    t.className = 'out horizons'; cap.textContent = 'Over other time frames';
    var hr = document.createElement('tr');
    ['Years', 'Spent', 'Could grow to'].forEach(function (h) { var th = document.createElement('th'); th.scope = 'col'; th.textContent = h; hr.appendChild(th); });
    thead.appendChild(hr);
    hs.forEach(function (n) {
      var res = oppCost(price, freq, n, rate), tr = document.createElement('tr'), th = document.createElement('th');
      th.scope = 'row'; th.textContent = n; tr.appendChild(th);
      cell(tr, '', fmt(res.spent)); cell(tr, '', fmt(res.value));
      if (n === years) tr.className = 'chosen';
      tb.appendChild(tr);
    });
    t.appendChild(cap); t.appendChild(thead); t.appendChild(tb); out.appendChild(t);
  }
  $('cost-form').addEventListener('input', runCost);
  $('cost-form').addEventListener('change', runCost);
  $('cost-form').addEventListener('submit', function (e) { e.preventDefault(); });

  /* ---------- start */
  refresh();
  runCost();
  var first = tabs.filter(function (t) { return '#' + t.id === location.hash; })[0] || tabs[0];
  select(first, false, false);
})();
</script>"""


def build_compound():
    body = """<header class="page-head wrap">
<h1>Compound interest</h1>
<p class="lede">See how steady saving grows, change the numbers year by year, and work out what a purchase could have grown to. Everything runs in your browser; nothing you type is stored or sent anywhere.</p>
</header>
<div class="wrap ci">
<div class="tabs" role="tablist" aria-label="Calculator">
<button type="button" role="tab" id="chart" aria-controls="panel-chart" aria-selected="true">Growth chart</button>
<button type="button" role="tab" id="year-by-year" aria-controls="panel-sheet" aria-selected="false" tabindex="-1">Year by year</button>
<button type="button" role="tab" id="opportunity-cost" aria-controls="panel-cost" aria-selected="false" tabindex="-1">Opportunity cost</button>
</div>

<section class="plan-box" id="plan" aria-labelledby="plan-h">
<h2 class="plan-h" id="plan-h">Your plan</h2>
<form id="plan-form" class="calc calc-5" novalidate>
<label for="p-bal">Starting balance ($)<input id="p-bal" type="number" inputmode="decimal" min="0" step="any" value="0"></label>
<label for="p-monthly">Monthly amount ($)<input id="p-monthly" type="number" inputmode="decimal" step="any" value="200"></label>
<label for="p-rate">Annual return (%)<input id="p-rate" type="number" inputmode="decimal" step="0.1" value="7"></label>
<label for="p-start">Start age<input id="p-start" type="number" inputmode="numeric" min="0" max="110" step="1" value="22"></label>
<label for="p-end">End age<input id="p-end" type="number" inputmode="numeric" min="1" max="120" step="1" value="65"></label>
</form>
<p class="msg plan-msg" id="plan-msg" role="alert" hidden></p>
<p class="plan-note" id="plan-note" hidden><span id="plan-note-text"></span> <button type="button" class="link-btn" id="note-reset">Reset to the plan</button></p>
</section>

<section class="panel" role="tabpanel" id="panel-chart" aria-labelledby="chart">
<dl class="stats" id="c-stats"></dl>
<div class="chart-head">
<ul class="legend">
<li><span class="sw sw-value"></span>Growth</li>
<li><span class="sw sw-put"></span>You put in</li>
<li id="lg-cmp"><span class="sw-line"></span><span id="lg-cmp-text">Total value if you start later</span></li>
</ul>
<p class="cmp"><label><input type="checkbox" id="c-cmp" checked> Compare with starting</label> <input type="number" id="c-delay" inputmode="numeric" value="10" min="1" max="60" step="1" aria-label="Years later"> <span>years later</span></p>
</div>
<p class="msg" id="cmp-msg" hidden></p>
<div class="chart" id="chart-box" tabindex="0" role="group" aria-label="Growth chart. Use the left and right arrow keys to read each year. The Year by year tab has every value as a table.">
<div class="tip" id="chart-tip" hidden></div>
</div>
<p class="vh" id="chart-live" aria-live="polite"></p>
<p class="note">The return is compounded monthly. Real returns rise and fall from year to year and are not guaranteed; try uneven years in the Year by year tab. This is a teaching tool, not investment advice.</p>
</section>

<section class="panel" role="tabpanel" id="panel-sheet" aria-labelledby="year-by-year" hidden>
<div class="sheet-tools">
<p class="hint">Type a new return or monthly amount in any year. It carries into every year after, until you change it again; clear the cell to go back to the plan. A one-time amount applies to that year only; use a minus sign for a withdrawal. Total put in includes the starting balance.</p>
<div class="sheet-btns"><button type="button" class="btn-quiet" id="s-reset">Reset changes</button><button type="button" class="btn-quiet" id="s-csv">Download CSV</button><button type="button" class="btn-quiet" id="s-print">Print</button></div>
</div>
<div class="sheet-wrap">
<table class="sheet">
<thead><tr><th scope="col">Age</th><th scope="col">Year</th><th scope="col" class="edit-h">Return (%)</th><th scope="col" class="edit-h">Monthly ($)</th><th scope="col" class="edit-h">One-time ($)</th><th scope="col">Put in this year</th><th scope="col">Growth this year</th><th scope="col">Total put in</th><th scope="col">Balance at year end</th></tr></thead>
<tbody id="sheet-body"></tbody>
<tfoot id="sheet-foot"></tfoot>
</table>
</div>
<p class="note">Money is added at the end of each month and grows at that year's return divided by 12. One-time amounts go in at the start of the year. Returns are not guaranteed.</p>
</section>

<section class="panel" role="tabpanel" id="panel-cost" aria-labelledby="opportunity-cost" hidden>
<p class="panel-intro">What a purchase could have grown to if the same money had been invested instead.</p>
<form id="cost-form" class="calc calc-4" novalidate>
<label for="o-price">Purchase amount ($)<input id="o-price" type="number" inputmode="decimal" min="0" step="any" value="1000"></label>
<label for="o-freq">How often<select id="o-freq"><option value="once" selected>One time</option><option value="day">Every day</option><option value="week">Every week</option><option value="month">Every month</option><option value="year">Every year</option></select></label>
<label for="o-years">Years<input id="o-years" type="number" inputmode="numeric" min="1" max="60" step="1" value="20"></label>
<label for="o-rate">Annual return (%)<input id="o-rate" type="number" inputmode="decimal" step="0.1" value="7"></label>
</form>
<div id="cost-out" aria-live="polite"></div>
<p class="note">This does not mean a purchase is wrong. It shows the full cost, so the choice is made on purpose. Returns are not guaranteed.</p>
<details><summary>How this is calculated</summary>
<p>Each amount is treated as invested on the day it would have been spent, and it grows at the annual return divided by 12 each month. Daily and weekly amounts are added up by month.</p>
</details>
</section>
</div>"""
    return page("Compound interest", body, current="tools.html", kind="ci-page",
                desc="Compound interest chart, a year-by-year spreadsheet, and an opportunity cost calculator.",
                script=CI_CORE + "\n" + CI_UI)


# ---------------------------------------------------------------- about

def build_about():
    body = f"""<header class="page-head wrap">
<h1>About this course</h1>
<p class="lede">{esc(VISION)}</p>
</header>
<div class="wrap prose">
<h2>What Entrusted is</h2>
<p>{esc(COURSE)} is a Bible-based course on handling money as a manager of what belongs to God. It is written for church classes, small groups and campus ministry groups, and it comes in three formats: <a href="one-night.html">One Night</a>, a single 90-minute session; <a href="campus.html">4 Weeks</a>, for students near graduation and people in their first years of work; and <a href="church.html">8 Weeks</a>, for a church class or small group of any age.</p>
<p>The course follows <a href="steps.html">Dave Ramsey's Baby Steps</a>, with scripture for each step and giving and a written budget at every one. It leaves out his college-fund step and adds two notes of its own: take any employer retirement match at every step, and if you keep a credit card, pay it in full every month. Entrusted is not affiliated with or endorsed by Dave Ramsey or Ramsey Solutions; the Baby Steps are their plan, and you can read their own explanation at <a href="https://www.ramseysolutions.com/dave-ramsey-7-baby-steps" target="_blank" rel="noopener">Ramsey Solutions</a>.</p>

<h2>Teaching, not financial advice</h2>
<p>This is teaching for churches and small groups. It is not professional financial, investment, tax or legal advice, and it does not recommend specific investments, funds, banks, apps or advisors. Contribution limits, interest rates and tax rules change, so look up the current figures before you plan, and talk with a qualified professional about your own situation.</p>
<p>Investment examples assume a 7% annual return to show how time and steady saving work. Returns are not guaranteed.</p>

<h2>Scripture</h2>
<p>Passages are given as references with a short paraphrase, not quoted in full. Every reference on the site is a link that opens the passage in the New International Version (NIV) on Bible Gateway, or bring your own Bible and read it there. The <a href="scripture-handout.html">scripture handout</a> collects every reference in the course on one sheet.</p>

<h2>Privacy</h2>
<p>This site has no sign-ups, no tracking and no outside scripts. The <a href="tools.html">calculators</a> run in your browser and nothing you type is stored or sent anywhere. Links to Bible Gateway, Investor.gov, the Consumer Financial Protection Bureau and Ramsey Solutions open those sites in a new tab.</p>
</div>"""
    return page("About", body, current="about.html", kind="about-page",
                desc="What Entrusted is, and what it is not.")


# ---------------------------------------------------------------- stylesheet

CSS = r"""/* Entrusted: one shared stylesheet. Generated by build.py. */
:root {
  --paper: #f7f4ec;
  --sand: #ece5d5;
  --sheet: #fffdf8;
  --ink: #1c221f;
  --ink-2: #4e5651;
  --rule: #d6cebd;
  --rule-2: #bdb4a2;
  --green: #1d5640;
  --green-2: #164433;
  --green-tint: #e2ebe4;
  --serif: "Iowan Old Style", "Palatino Linotype", Palatino, "Book Antiqua", "URW Palladio L", P052, Georgia, serif;
  --sans: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

*, *::before, *::after { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body {
  margin: 0; background: var(--paper); color: var(--ink);
  font-family: var(--sans); font-size: 1.0625rem; line-height: 1.6;
}
h1, h2, h3, h4 { font-family: var(--serif); color: var(--ink); line-height: 1.2; margin: 0 0 .5em; font-weight: 600; }
h1 { font-size: clamp(2rem, 1.45rem + 2.4vw, 3rem); font-weight: 400; letter-spacing: -.005em; }
h2 { font-size: clamp(1.4rem, 1.2rem + .8vw, 1.75rem); }
h3 { font-size: 1.2rem; }
p { margin: 0 0 1em; }
a { color: var(--green); text-decoration-thickness: 1px; text-underline-offset: .18em; }
a:hover { color: var(--green-2); text-decoration-thickness: 2px; }
:focus-visible { outline: 3px solid var(--green); outline-offset: 2px; border-radius: 2px; }
.vh { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
.wrap { max-width: 68rem; margin: 0 auto; padding: 0 1.25rem; }
.skip { position: absolute; left: -9999px; top: .75rem; background: var(--sheet); padding: .5rem 1rem; z-index: 10; }
.skip:focus { left: 1rem; }
.print-only { display: none; }

/* header and footer */
.site-head { border-bottom: 1px solid var(--rule); }
.head-inner { display: flex; align-items: center; justify-content: space-between; gap: .75rem 2rem; flex-wrap: wrap; padding-top: .9rem; padding-bottom: .9rem; }
.brand { display: flex; flex-direction: column; text-decoration: none; color: var(--ink); line-height: 1.1; }
.brand:hover { color: var(--ink); }
.brand-name { font-family: var(--serif); font-size: 1.6rem; letter-spacing: .01em; }
.brand-sub { font-size: .8rem; color: var(--ink-2); margin-top: .15rem; }
.site-nav ul { list-style: none; margin: 0; padding: 0; display: flex; flex-wrap: wrap; gap: .15rem 1.15rem; }
.site-nav a { display: inline-block; color: var(--ink); text-decoration: none; font-size: .95rem; padding: .3rem 0; border-bottom: 2px solid transparent; }
.site-nav a:hover { border-bottom-color: var(--rule-2); color: var(--ink); }
.site-nav a[aria-current="page"] { color: var(--green); border-bottom-color: var(--green); }
.site-foot { border-top: 1px solid var(--rule); margin-top: 4rem; padding: 1.75rem 0 2.5rem; font-size: .875rem; color: var(--ink-2); }
.site-foot p { max-width: 44rem; margin: 0 0 .4rem; }
.foot-name { font-family: var(--serif); font-size: 1rem; color: var(--ink); }

/* page heads */
.page-head { padding-top: 3rem; padding-bottom: 1.25rem; }
.page-head h1 { margin-bottom: .35em; }
.lede { font-family: var(--serif); font-size: clamp(1.15rem, 1.05rem + .45vw, 1.4rem); line-height: 1.5; max-width: 40rem; color: var(--ink); }
.head-links { display: flex; flex-wrap: wrap; gap: .5rem 1.25rem; }

/* home */
.hero { padding: clamp(3rem, 2rem + 5vw, 6.5rem) 0 clamp(2.5rem, 2rem + 3vw, 4.5rem); }
.hero-course { font-size: 1rem; color: var(--ink-2); margin-bottom: 1.25rem; }
.hero-vision { font-size: clamp(2.3rem, 1.2rem + 4.4vw, 4.6rem); line-height: 1.06; max-width: 15em; margin-bottom: .4em; letter-spacing: -.012em; }
.hero-refs { font-family: var(--serif); font-style: italic; color: var(--green); font-size: 1.1rem; margin-bottom: 2rem; }
.hero .lede { max-width: 38rem; }
.band { padding: 2.5rem 0; border-top: 1px solid var(--rule); }
.formats { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0; margin-top: 1.25rem; border-top: 2px solid var(--ink); }
.format { padding: 1.25rem 1.5rem 1rem 0; }
.format + .format { padding-left: 1.5rem; border-left: 1px solid var(--rule); }
.format h3 { font-size: 1.6rem; font-weight: 400; margin-bottom: .2rem; }
.format h3 a { color: var(--ink); text-decoration: none; }
.format h3 a:hover { color: var(--green); }
.format-length { font-family: var(--serif); font-style: italic; color: var(--green); margin-bottom: .75rem; }
.format-who { font-weight: 600; font-size: .98rem; }
.format p { font-size: .98rem; }
.format-link { margin: 0; }
.split { display: grid; grid-template-columns: minmax(0, 18rem) minmax(0, 1fr); gap: 2rem 4rem; align-items: start; }
.every-line { font-size: 1.05rem; }
.leader-links { list-style: none; margin: 1rem 0 0; padding: 0; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1.5rem; }
.leader-links a { font-family: var(--serif); font-size: 1.3rem; display: block; margin-bottom: .25rem; }
.leader-links span { color: var(--ink-2); font-size: .95rem; }

/* the ladder: numbered steps with a rule joining them */
.ladder { list-style: none; margin: 0; padding: 0; }
.ladder > li { display: grid; grid-template-columns: 3.5rem minmax(0, 1fr); gap: 0 1.25rem; position: relative; padding-bottom: 1.6rem; }
.ladder > li::before { content: ""; position: absolute; left: 1.75rem; top: 3.1rem; bottom: .5rem; width: 1px; background: var(--green); opacity: .4; }
.ladder > li:last-child::before { display: none; }
.ladder .num { font-family: var(--serif); font-size: 2.9rem; line-height: 1; text-align: center; color: var(--green); font-variant-numeric: oldstyle-nums; }
.ladder-compact h3 { font-size: 1.3rem; margin: .35rem 0 .15rem; font-weight: 400; }
.ladder-compact p { margin: 0; color: var(--ink-2); }
.ladder-full > li { padding-bottom: 2.75rem; }
.ladder-full .num { font-size: 4rem; }
.ladder-full > li::before { left: 2.25rem; top: 4.4rem; }
.ladder-full > li { grid-template-columns: 4.5rem minmax(0, 1fr); }
.step-body h2 { font-size: clamp(1.6rem, 1.3rem + 1vw, 2.1rem); font-weight: 400; margin: .45rem 0 .2rem; }
.step-what { font-family: var(--serif); font-size: 1.25rem; line-height: 1.4; margin-bottom: .6rem; }
.step-ref { font-family: var(--serif); font-style: italic; color: var(--green); margin-bottom: .6rem; }
.step-why { max-width: 38rem; }
.done { max-width: 38rem; border-left: 3px solid var(--green); padding: .1rem 0 .1rem 1rem; }
.done h3 { font-family: var(--sans); font-size: .9rem; font-weight: 600; color: var(--green); margin: 0 0 .2rem; }
.done p { margin: 0; }
.every { background: var(--sand); padding: 1.5rem 1.75rem; margin: 1rem 0 3rem; max-width: 46rem; border-radius: 3px; }
.every h2 { font-weight: 400; margin-bottom: .2rem; }
.every .step-why { margin: 0; }
@media (min-width: 960px) {
  .step-body { display: grid; grid-template-columns: minmax(0, 38rem) 13rem; gap: 0 3rem; }
  .step-body > * { grid-column: 1; }
  .step-body > .step-ref { grid-column: 2; grid-row: 1 / span 2; align-self: start; margin-top: .9rem; padding-left: 1rem; border-left: 1px solid var(--rule); }
}

/* track pages */
.facts { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1rem 2.5rem; max-width: 46rem; margin: 1.5rem 0 1rem; padding-top: 1rem; border-top: 1px solid var(--rule); }
.facts dt { font-size: .85rem; font-weight: 600; color: var(--green); }
.facts dd { margin: .15rem 0 0; }
.track-extra { max-width: 46rem; background: var(--sand); padding: .9rem 1.2rem; border-radius: 3px; }
.session-list { list-style: none; margin: 1.25rem 0 3rem; padding: 0; border-top: 2px solid var(--ink); }
.session-list > li { display: grid; grid-template-columns: 3.25rem minmax(0, 1fr); gap: 0 1.25rem; padding: 1.4rem 0; border-bottom: 1px solid var(--rule); }
.session-list .num { font-family: var(--serif); font-size: 2.4rem; line-height: 1; color: var(--green); text-align: center; font-variant-numeric: oldstyle-nums; }
.sess-label { font-size: .85rem; color: var(--ink-2); margin: 0 0 .1rem; }
.session-list h3 { font-size: 1.55rem; font-weight: 400; margin-bottom: .3rem; }
.session-list h3 a { color: var(--ink); text-decoration: none; }
.session-list h3 a:hover { color: var(--green); text-decoration: underline; }
.session-list p { max-width: 42rem; }
.sess-links { display: flex; flex-wrap: wrap; gap: .5rem; margin: 0; }
.sess-links a, .end-links a, .doc-links a, .head-links a {
  display: inline-block; padding: .3rem .8rem; border: 1px solid var(--rule-2); border-radius: 3px;
  text-decoration: none; font-size: .92rem; background: var(--sheet);
}
.sess-links a:hover, .end-links a:hover, .doc-links a:hover, .head-links a:hover { border-color: var(--green); }
.sess-links a:first-child { background: var(--green); color: var(--sheet); border-color: var(--green); }
.sess-links a:first-child:hover { background: var(--green-2); }
.head-links a { padding: .25rem .7rem; }
.track-aside { max-width: 46rem; }
.track-aside h2 { font-size: 1.3rem; }

/* session pages: sized for a TV or projector */
body.session { font-size: clamp(1.125rem, .5rem + 1.15vw, 2.15rem); }
.slide { border-bottom: 1px solid var(--rule); padding: 2.5em 0; }
.slide-inner { max-width: 46em; margin: 0 auto; padding: 0 1.25rem; }
.margin { font-family: var(--serif); font-style: italic; color: var(--green); font-size: .8em; line-height: 1.35; margin: 0 0 .6em; }
.margin:empty { display: none; }
.slide h1 { font-size: 2.5em; line-height: 1.08; margin-bottom: .35em; }
.slide h2 { font-size: 1.65em; font-weight: 400; margin-bottom: .55em; }
.slide p, .slide li { line-height: 1.5; }
.slide-body > p, .slide-body > ul, .slide-body > ol { max-width: 32em; }
.where { font-size: .8em; margin-bottom: 1.2em; }
.where a { text-decoration: none; }
.where a:hover { text-decoration: underline; }
.big-idea { font-family: var(--serif); font-size: 1.35em; line-height: 1.4; max-width: 26em !important; }
.slide-body > .present-hint { font-size: .65em; color: var(--ink-2); margin-top: 2.5em; max-width: none; }
.refs { list-style: none; padding: 0; margin: 0; }
.refs li { margin: 0 0 .85em; }
.refs .ref { display: block; font-family: var(--serif); font-weight: 600; color: var(--green); }
.opener { font-family: var(--serif); font-size: 1.45em; line-height: 1.35; }
.footnote { font-size: .7em; color: var(--ink-2); border-top: 1px solid var(--rule); padding-top: .5em; margin-top: 1.5em; max-width: 34em; }
.discuss { padding-left: 1.4em; }
.discuss li { margin-bottom: .6em; padding-left: .2em; }
.discuss li::marker { font-family: var(--serif); color: var(--green); }
.slide-links { font-size: .8em; display: flex; flex-wrap: wrap; gap: .4em 1.4em; }
.session-end { padding-top: 2rem; padding-bottom: 1rem; font-size: 1rem; }
.end-links, .end-seq { display: flex; flex-wrap: wrap; gap: .5rem 1rem; }
.end-seq { justify-content: space-between; margin-top: 1rem; }
.end-seq .next { margin-left: auto; }
@media (min-width: 900px) and (min-height: 560px) {
  .slide { min-height: 100vh; min-height: 100svh; display: flex; align-items: center; padding: 2em 0; }
  .slide-inner { width: 100%; display: grid; grid-template-columns: 8.5em minmax(0, 1fr); gap: 0 2em; }
  .margin, .margin:empty { display: block; text-align: right; padding-top: .55em; margin: 0; }
  .slide-title .slide-inner { grid-template-columns: 8.5em minmax(0, 1fr); }
}

/* checkboxes drawn with borders so they print */
.checks { list-style: none; padding: 0; margin: 0 0 1em; }
.checks li { position: relative; padding-left: 1.75em; margin: 0 0 .45em; }
.checks li::before { content: ""; position: absolute; left: 0; top: .22em; width: 1em; height: 1em; border: 1.5px solid currentColor; border-radius: 2px; }
.big-checks li { margin-bottom: .8em; }

/* printable pages on screen */
.toolbar { display: flex; align-items: center; flex-wrap: wrap; gap: .5rem 1rem; max-width: 8.5in; margin: 1.75rem auto 1rem; padding: 0 1rem; }
.page-head .toolbar { margin: 1rem 0 0; padding: 0; }
.toolbar p { margin: 0; color: var(--ink-2); font-size: .95rem; }
.print-btn, .calc-btn {
  font: inherit; font-weight: 600; font-size: 1rem; background: var(--green); color: var(--sheet);
  border: 0; border-radius: 3px; padding: .55rem 1.4rem; cursor: pointer;
}
.print-btn:hover, .calc-btn:hover { background: var(--green-2); }
.paper, .doc { background: var(--sheet); max-width: 8.5in; margin: 0 auto 2rem; padding: .6in .65in; border: 1px solid var(--rule); }
.doc { max-width: 52rem; padding: 2.5rem clamp(1.25rem, 4vw, 3.25rem); }

/* handout */
.handout { font-size: .95rem; line-height: 1.45; }
.ho-where { display: flex; justify-content: space-between; flex-wrap: wrap; gap: 0 1rem; font-size: .82rem; color: var(--ink-2); margin: 0 0 .6rem; padding-bottom: .4rem; border-bottom: 1px solid var(--rule); }
.handout h1 { font-size: 2rem; margin: 0 0 .2em; }
.ho-big { font-family: var(--serif); font-size: 1.12rem; line-height: 1.4; margin-bottom: .4rem; }
.ho-block h2, .ho-back-title { font-size: 1.1rem; margin: 1.1rem 0 .45rem; padding-bottom: .15rem; border-bottom: 1.5px solid var(--ink); }
.ho-hint { font-size: .85rem; color: var(--ink-2); margin: 0 0 .2rem; }
.ho-refs { list-style: none; margin: 0; padding: 0; }
.ho-refs li { display: flex; align-items: flex-end; gap: .75rem; height: 1.95rem; }
.ho-refs .ref { font-family: var(--serif); font-weight: 600; white-space: nowrap; min-width: 9.5rem; }
.ho-refs .line { flex: 1; border-bottom: 1px solid #8f897d; height: 100%; }
.ho-points .pt { margin-bottom: .2rem; }
.ho-points h3 { font-size: 1rem; margin: .55rem 0 0; }
.write { border-bottom: 1px solid #8f897d; height: 1.75rem; }
.ho-discuss { margin: 0; padding-left: 1.3rem; }
.ho-discuss li { margin-bottom: .2rem; }
.ho-back { margin-top: 2rem; padding-top: 1rem; border-top: 2px dashed var(--rule); }
.ho-skill { font-size: .92rem; }

/* worksheets (HTML comes ready-made from content.py) */
.worksheet { margin: 0 0 1.2rem; }
.worksheet h3 { font-size: 1.15rem; margin: .4rem 0 .25rem; }
.wsnote { font-size: .86rem; color: var(--ink-2); margin: 0 0 .45rem; }
.worksheet table { width: 100%; border-collapse: collapse; table-layout: fixed; font-size: .9rem; }
.worksheet th, .worksheet td { border: 1px solid var(--rule-2); padding: .28rem .45rem; text-align: left; vertical-align: top; }
.worksheet thead th { background: var(--green-tint); font-family: var(--serif); font-weight: 600; }
.worksheet td:empty { height: 2.15rem; }
.worksheet table.cols-2 th:first-child { width: 55%; }
.worksheet table.cols-3 th:first-child { width: 46%; }
.worksheet table.cols-4 th:first-child { width: 40%; }
.worksheet table.cols-6 th:first-child { width: 22%; }
.worksheet table.filled th:first-child { width: 26%; }
.worksheet table.filled td:first-child { font-weight: 600; }
.worksheet .checks { columns: 2; column-gap: 2rem; }
.worksheet .checks li { break-inside: avoid; }

/* leader guide */
.doc-head .where { font-size: .9rem; margin-bottom: .6rem; }
.doc h1 { font-size: clamp(1.8rem, 1.4rem + 1.6vw, 2.5rem); }
.doc h2 { font-size: 1.45rem; margin-top: 2rem; padding-bottom: .2rem; border-bottom: 1px solid var(--rule); }
.doc h3 { font-size: 1.1rem; margin-top: 1.4rem; }
.doc h4 { font-size: 1.05rem; margin: 0 0 .2rem; }
.doc-links { display: flex; flex-wrap: wrap; gap: .5rem; }
.caution { background: var(--sand); border-left: 5px solid var(--green); padding: 1rem 1.25rem .4rem; margin: 2rem 0 1rem; border-radius: 0 3px 3px 0; }
.caution h2 { margin: 0 0 .3rem; border: 0; padding: 0; font-size: 1.2rem; color: var(--green); }
.plan-total { color: var(--ink-2); font-size: .95rem; }
.plan { width: 100%; border-collapse: collapse; font-size: .97rem; }
.plan th, .plan td { text-align: left; vertical-align: top; padding: .55rem .6rem .55rem 0; border-bottom: 1px solid var(--rule); }
.plan thead th { font-size: .85rem; color: var(--ink-2); font-weight: 600; border-bottom: 1.5px solid var(--ink); }
.plan td:first-child { white-space: nowrap; font-variant-numeric: tabular-nums; width: 5.5rem; }
.plan tbody th { font-family: var(--serif); font-weight: 600; width: 10rem; }
.plan-extra { margin-top: 1rem; background: var(--sand); padding: .75rem 1rem; border-radius: 3px; font-size: .95rem; }
.ref-list dt { font-family: var(--serif); font-weight: 600; color: var(--green); margin-top: .5rem; }
.ref-list dd { margin: .05rem 0 0; }
.teach-list { padding-left: 1.4rem; }
.teach-list li { margin-bottom: 1rem; }
.teach-list li::marker { font-family: var(--serif); color: var(--green); }
.notes .footnote { font-size: .85rem; margin-top: .4rem; padding-top: .3rem; }
.qa dt { font-family: var(--serif); font-weight: 600; font-size: 1.08rem; margin-top: 1.1rem; }
.qa dd { margin: .2rem 0 0; }

/* step card */
.card-sheet { max-width: 7in; margin: 0 auto 2rem; padding: 0 1rem; }
.step-card { background: var(--sheet); border: 1px solid var(--rule); padding: .4in .45in .3in; font-size: .95rem; }
.step-card header { display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap; gap: 0 1rem; border-bottom: 1.5px solid var(--ink); padding-bottom: .3rem; margin-bottom: .6rem; }
.step-card h1 { font-size: 1.6rem; margin: 0; }
.step-card header p { margin: 0; font-size: .82rem; color: var(--ink-2); }
.card-every { background: var(--green-tint); padding: .45rem .7rem; margin: 0 0 .5rem; border-radius: 2px; }
.step-card .ref { font-family: var(--serif); font-style: italic; color: var(--green); white-space: nowrap; }
.card-every .ref { margin-left: .3rem; }
.card-steps { list-style: none; margin: 0; padding: 0; }
.card-steps li { display: grid; grid-template-columns: .95rem 1.4rem minmax(0, 1fr) auto; gap: 0 .55rem; align-items: baseline; padding: .38rem 0; border-bottom: 1px solid var(--rule); }
.card-steps li:last-child { border-bottom: 0; }
.card-steps .mark { width: .95rem; height: .95rem; border: 1.5px solid var(--ink); border-radius: 2px; align-self: center; }
.card-steps .n { font-family: var(--serif); font-size: 1.35rem; line-height: 1; color: var(--green); text-align: center; font-variant-numeric: oldstyle-nums; }
.card-foot { margin: .45rem 0 0; font-size: .8rem; color: var(--ink-2); text-align: right; }

/* scripture list and indexes */
.scripture-list { max-width: 50rem; }
.sc-group { padding-top: 1.5rem; }
.sc-group > h2 { border-bottom: 2px solid var(--ink); padding-bottom: .25rem; margin-top: 1rem; }
.sc-group > h2 a { color: var(--ink); text-decoration: none; }
.sc-session { margin: 1.25rem 0 1.75rem; }
.sc-session h3 { font-weight: 400; font-size: 1.3rem; margin-bottom: .2rem; }
.also { font-size: .93rem; color: var(--ink-2); margin-top: .6rem; }
.also span { font-weight: 600; }
.idx-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 2rem; margin-top: 1rem; }
.idx-group h2 { font-size: 1.45rem; border-bottom: 2px solid var(--ink); padding-bottom: .2rem; margin-bottom: .2rem; }
.idx-group h2 a { color: var(--ink); text-decoration: none; }
.idx-group h2 a:hover { color: var(--green); }
.idx-len { font-family: var(--serif); font-style: italic; color: var(--green); font-size: .95rem; margin-bottom: .6rem; }
.idx-list { list-style: none; margin: 0; padding: 0; }
.idx-list li { padding: .45rem 0; border-bottom: 1px solid var(--rule); }
.idx-list span { display: block; color: var(--ink-2); font-size: .9rem; }
.idx-everyone { max-width: 40rem; margin-bottom: 2rem; }
.idx-everyone .idx-list a { font-family: var(--serif); font-size: 1.15rem; }
.prep-note { max-width: 44rem; margin-bottom: 2.5rem; }
.prep-note ol { padding-left: 1.3rem; }
.prep-note li { margin-bottom: .4rem; }
.prep-note li::marker { font-family: var(--serif); color: var(--green); }

/* tools */
.tools { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 2.5rem; align-items: start; }
.tool { background: var(--sheet); border: 1px solid var(--rule); border-top: 3px solid var(--green); padding: 1.5rem 1.6rem 1.2rem; border-radius: 0 0 3px 3px; }
.calc { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .9rem 1rem; margin: 1rem 0; }
.calc label { display: flex; flex-direction: column; gap: .25rem; font-size: .9rem; font-weight: 600; }
.calc input { font: inherit; font-size: 1.1rem; font-weight: 400; padding: .45rem .6rem; border: 1px solid var(--rule-2); border-radius: 3px; background: #fff; color: var(--ink); width: 100%; }
.calc input:focus-visible { outline: 3px solid var(--green); outline-offset: 0; border-color: var(--green); }
.calc-btn { justify-self: start; grid-column: 1 / -1; }
.results { min-height: 5rem; }
.out { width: 100%; border-collapse: collapse; font-variant-numeric: tabular-nums; margin-bottom: .75rem; }
.out th, .out td { text-align: right; padding: .45rem .3rem; border-bottom: 1px solid var(--rule); }
.out th:first-child { text-align: left; }
.out thead th { font-size: .82rem; color: var(--ink-2); font-weight: 600; border-bottom: 1.5px solid var(--ink); }
.out tbody td:last-child { font-family: var(--serif); font-size: 1.25rem; }
.diff { font-size: 1rem; }
.diff strong { font-family: var(--serif); font-size: 1.2rem; color: var(--green); }
.out-dl { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1rem; margin: 0 0 .75rem; }
.out-dl dt { font-size: .82rem; color: var(--ink-2); font-weight: 600; }
.out-dl dd { margin: .1rem 0 0; font-family: var(--serif); font-size: 1.5rem; font-variant-numeric: tabular-nums; }
.out-dl dd span { display: block; font-family: var(--sans); font-size: .85rem; color: var(--ink-2); }
.msg { color: var(--ink-2); }
.warn { background: var(--sand); border-left: 4px solid var(--green); padding: .7rem 1rem; }
.note { font-size: .88rem; color: var(--ink-2); }
details { font-size: .9rem; }
summary { cursor: pointer; color: var(--green); }

/* about */
.prose { max-width: 42rem; }
.prose h2 { margin-top: 2rem; }

/* small screens */
@media (max-width: 860px) {
  .formats, .leader-links, .idx-grid, .tools { grid-template-columns: 1fr; }
  .format, .format + .format { padding: 1.1rem 0; border-left: 0; }
  .format + .format { border-top: 1px solid var(--rule); }
  .split { grid-template-columns: 1fr; }
}
@media (max-width: 560px) {
  body { font-size: 1rem; }
  .head-inner { padding-top: .7rem; padding-bottom: .5rem; }
  .site-nav ul { gap: 0 .9rem; }
  .site-nav a { font-size: .9rem; }
  .facts, .calc, .out-dl { grid-template-columns: 1fr; }
  .paper { padding: 1.25rem 1rem; }
  .ho-refs .ref { min-width: 0; }
  .slide-body > .present-hint { display: none; }
  .worksheet table { font-size: .8rem; }
  .worksheet .checks { columns: 1; }
  .ladder-full .num { font-size: 3rem; }
  .ladder-full > li { grid-template-columns: 3rem minmax(0, 1fr); gap: 0 .9rem; }
  .ladder-full > li::before { left: 1.5rem; top: 3.4rem; }
  .step-card { padding: 1rem; }
  .card-steps li { grid-template-columns: .95rem 1.2rem minmax(0, 1fr); }
  .card-steps .ref { grid-column: 3; }
}
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }

/* print: black on white, no navigation */
@media print {
  @page { margin: .5in; }
  *, *::before, *::after { color: #000 !important; background: transparent !important; box-shadow: none !important; }
  body, body.session { font-size: 10pt; line-height: 1.38; }
  .site-head, .site-foot, .toolbar, .skip, .session-end, .present-hint, .slide-links, .doc-links, .head-links, .sess-links { display: none !important; }
  a { text-decoration: none; }
  .print-only { display: block; }
  .paper, .doc { border: 0; padding: 0; margin: 0; max-width: none; }
  h2, h3, h4 { break-after: avoid; }
  tr, li, dd { break-inside: avoid; }
  .slide { min-height: 0 !important; display: block !important; padding: .6em 0; border: 0; }
  .slide-inner { display: block !important; }
  .margin { text-align: left !important; }

  .handout { font-size: 9.6pt; line-height: 1.3; }
  .handout h1 { font-size: 19pt; }
  .ho-where { font-size: 8.5pt; border-color: #000; }
  .ho-big { font-size: 11pt; }
  .ho-block h2, .ho-back-title { font-size: 11pt; margin: .14in 0 .05in; border-color: #000; }
  .ho-hint { font-size: 8.5pt; }
  .ho-refs li { height: .3in; }
  .ho-refs .line, .write { border-color: #000; }
  .write { height: .3in; }
  .ho-points h3 { font-size: 10pt; margin-top: .07in; }
  .dense .ho-refs li { height: .27in; }
  .dense .write { height: .27in; }
  .ho-back { break-before: page; margin: 0; padding: 0; border: 0; }
  .ho-back-title { margin-top: 0; }
  .ho-skill { font-size: 9.5pt; }
  .worksheet { break-inside: avoid; margin-bottom: .14in; }
  .worksheet h3 { font-size: 12pt; }
  .wsnote { font-size: 8.8pt; }
  .worksheet table { font-size: 9pt; }
  .worksheet th, .worksheet td { border-color: #000; padding: 2pt 4pt; }
  .worksheet thead th { border-bottom: 1.5pt solid #000; }
  .worksheet td:empty { height: .3in; }
  .checks li::before { border-color: #000; }

  .doc h2 { border-color: #000; margin-top: .25in; }
  .caution { border: 2pt solid #000; border-radius: 0; break-inside: avoid; }
  .plan th, .plan td { border-color: #000; }

  .card-page main { margin: 0; }
  .card-sheet { max-width: none; margin: 0; padding: 0; }
  .step-card { border: 0; height: 4.98in; padding: .12in .35in 0; overflow: hidden; font-size: 10.2pt; }
  .step-card h1 { font-size: 17pt; }
  .card-every { border: 1pt solid #000; }
  .card-steps li { border-color: #999; padding: .065in 0; }
  .card-steps .mark { border-color: #000; }
  .cut { border-top: 1px dashed #000; height: 0; }

  .tools { display: block; }
  .tool { border: 1px solid #000; margin-bottom: .2in; break-inside: avoid; }
}
"""


# ---------------------------------------------------------------- build

CI_CSS = r"""
/* compound interest page */
.ci .tabs { display: flex; flex-wrap: wrap; gap: 0 .25rem; border-bottom: 2px solid var(--ink); margin: .25rem 0 1.5rem; }
.tabs [role="tab"] {
  font: inherit; font-family: var(--serif); font-size: 1.2rem; color: var(--ink-2); background: none; cursor: pointer;
  border: 0; border-bottom: 3px solid transparent; margin-bottom: -2px; padding: .55rem 1rem .5rem;
}
.tabs [role="tab"]:first-child { padding-left: 0; }
.tabs [role="tab"]:hover { color: var(--ink); }
.tabs [role="tab"][aria-selected="true"] { color: var(--ink); border-bottom-color: var(--green); }
.plan-box { background: var(--sheet); border: 1px solid var(--rule); padding: 1rem 1.25rem .4rem; margin-bottom: 1.5rem; border-radius: 3px; }
.plan-h { font-size: 1.1rem; margin: 0; }
.calc-5 { grid-template-columns: repeat(5, minmax(0, 1fr)); margin: .6rem 0 .8rem; }
.calc-4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }
.calc select { font: inherit; font-size: 1.1rem; font-weight: 400; padding: .5rem .5rem; border: 1px solid var(--rule-2); border-radius: 3px; background: #fff; color: var(--ink); width: 100%; }
.plan-msg { margin: 0 0 .8rem; }
.plan-note { background: var(--green-tint); padding: .5rem .8rem; border-radius: 3px; font-size: .95rem; margin: 0 0 .8rem; }
.link-btn { font: inherit; background: none; border: 0; padding: 0; color: var(--green); text-decoration: underline; text-underline-offset: .18em; cursor: pointer; }
.ci-stale .panel .stats, .ci-stale .chart, .ci-stale .sheet-wrap { opacity: .45; }
.panel-intro { font-family: var(--serif); font-size: 1.15rem; max-width: 40rem; }
.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(9.5rem, 1fr)); gap: .9rem 1.5rem; margin: 0 0 1.25rem; }
.stats dt { font-size: .85rem; color: var(--ink-2); font-weight: 600; }
.stats dd { margin: .1rem 0 0; font-size: clamp(1.35rem, 1.1rem + 1vw, 1.8rem); font-weight: 600; letter-spacing: -.01em; }
.chart-head { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: .5rem 1.5rem; margin-bottom: .6rem; }
.legend { list-style: none; margin: 0; padding: 0; display: flex; flex-wrap: wrap; gap: .3rem 1.25rem; font-size: .92rem; }
.legend li { display: flex; align-items: center; gap: .45rem; }
.sw { width: .85rem; height: .85rem; border-radius: 2px; display: inline-block; }
.sw-value { background: #157a4b; }
.sw-put { background: #b8862b; }
.sw-line { width: 1.4rem; border-top: 2px dashed #7d837e; display: inline-block; }
.cmp { margin: 0; font-size: .92rem; display: flex; align-items: center; flex-wrap: wrap; gap: .35rem; }
.cmp label { display: flex; align-items: center; gap: .4rem; cursor: pointer; }
.cmp input[type="checkbox"] { width: 1.05rem; height: 1.05rem; accent-color: var(--green); }
.cmp input[type="number"] { width: 3.6rem; font: inherit; padding: .2rem .35rem; border: 1px solid var(--rule-2); border-radius: 3px; background: #fff; }
.chart { position: relative; background: var(--sheet); border: 1px solid var(--rule); border-radius: 3px; min-height: 280px; }
.chart:focus-visible { outline: 3px solid var(--green); outline-offset: 2px; }
.chart svg { display: block; touch-action: pan-y; }
.chart .ax { font-family: var(--sans); font-size: 12px; fill: var(--ink-2); font-variant-numeric: tabular-nums; }
.chart .end-label { font-family: var(--sans); font-size: 14px; font-weight: 600; fill: var(--ink); paint-order: stroke; stroke: #fffdf8; stroke-width: 4px; stroke-linejoin: round; }
.tip { position: absolute; pointer-events: none; background: var(--sheet); border: 1px solid var(--rule-2); border-radius: 3px; padding: .45rem .7rem .35rem; font-size: .88rem; box-shadow: 0 2px 10px rgba(28, 34, 31, .12); min-width: 11.5rem; z-index: 3; }
.tip p { margin: 0 0 .2rem; }
.tip-h { font-weight: 600; color: var(--ink-2); font-size: .82rem; }
.tip-row { display: flex; align-items: center; gap: .5rem; }
.tip-row strong { font-variant-numeric: tabular-nums; }
.tip-row span:last-child { color: var(--ink-2); }
.key { width: .9rem; flex: none; border-top: 2px solid transparent; }
.k-value { border-top-color: #157a4b; }
.k-put { border-top-color: #b8862b; }
.k-cmp { border-top: 2px dashed #7d837e; }
.sheet-tools { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: flex-start; gap: .75rem 2rem; margin-bottom: .9rem; }
.hint { max-width: 44rem; margin: 0; font-size: .95rem; color: var(--ink-2); }
.sheet-btns { display: flex; flex-wrap: wrap; gap: .5rem; }
.btn-quiet { font: inherit; font-size: .92rem; background: var(--sheet); color: var(--green); border: 1px solid var(--rule-2); border-radius: 3px; padding: .35rem .8rem; cursor: pointer; }
.btn-quiet:hover { border-color: var(--green); }
.sheet-wrap { overflow: auto; max-height: 72vh; border: 1px solid var(--rule); border-radius: 3px; background: var(--sheet); }
.sheet { border-collapse: separate; border-spacing: 0; width: 100%; font-size: .92rem; font-variant-numeric: tabular-nums; }
.sheet th, .sheet td { padding: .28rem .6rem; text-align: right; white-space: nowrap; border-bottom: 1px solid #ebe4d6; border-right: 1px solid #f0eadf; }
.sheet thead th { position: sticky; top: 0; z-index: 2; background: var(--sand); font-size: .8rem; font-weight: 600; white-space: normal; vertical-align: bottom; line-height: 1.25; min-width: 5.5rem; border-bottom: 1.5px solid var(--ink); }
.sheet thead th.edit-h { color: var(--green); }
.sheet thead th:first-child { left: 0; z-index: 3; min-width: 3.5rem; }
.sheet tbody th { position: sticky; left: 0; z-index: 1; background: var(--sheet); font-weight: 600; }
.sheet td.yr { color: var(--ink-2); }
.sheet td.edit { background: #fff; padding: .12rem .2rem; }
.sheet input { width: 6.2rem; font: inherit; text-align: right; padding: .22rem .4rem; border: 1px solid transparent; border-radius: 2px; background: transparent; color: var(--ink); }
.sheet input::placeholder { color: var(--ink-2); opacity: 1; }
.sheet input:hover { border-color: var(--rule-2); }
.sheet input:focus { outline: 2px solid var(--green); outline-offset: -1px; background: #fff; }
.sheet input.set { background: var(--green-tint); font-weight: 600; }
.sheet input[aria-invalid="true"] { border-color: #9b2c2c; background: #fbeaea; }
.sheet td.neg { color: #8a2d2d; }
.sheet tfoot th, .sheet tfoot td { position: sticky; bottom: 0; z-index: 2; background: var(--sand); font-weight: 600; border-top: 1.5px solid var(--ink); }
.sheet tfoot th { text-align: left; left: 0; z-index: 3; }
.cost-line { font-family: var(--serif); font-size: 1.2rem; line-height: 1.45; max-width: 40rem; }
.horizons { max-width: 30rem; margin-top: .5rem; }
.horizons caption { text-align: left; font-weight: 600; padding-bottom: .35rem; }
.horizons tbody th { text-align: left; }
.horizons tbody td:last-child { font-family: var(--sans); font-size: inherit; }
.horizons tr.chosen th, .horizons tr.chosen td { background: var(--green-tint); font-weight: 700; }
.tools-more { max-width: 40rem; background: var(--sheet); border: 1px solid var(--rule); border-left: 4px solid var(--green); padding: .8rem 1rem; border-radius: 0 3px 3px 0; }
.tools-more a { font-weight: 600; }
@media (max-width: 860px) {
  .calc-5, .calc-4 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 560px) {
  .calc-5, .calc-4 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .tabs [role="tab"] { font-size: 1.05rem; padding: .5rem .6rem; }
  .sheet { font-size: .85rem; }
  .sheet input { width: 5rem; }
}
@media print {
  .tabs, .sheet-btns, .plan-note, .chart-head .cmp, .ci details, .hint { display: none !important; }
  .plan-box { border: 1px solid #000; }
  .sheet-wrap { max-height: none; overflow: visible; border: 0; }
  .sheet { font-size: 8.5pt; }
  .sheet thead th, .sheet tbody th, .sheet tfoot th, .sheet tfoot td { position: static; }
  .sheet th, .sheet td { border-color: #999; padding: 1.5pt 4pt; }
  .sheet input { border: 0; padding: 0; width: 100%; }
  .sheet input::placeholder { color: #000; }
  .chart { border: 1px solid #000; }
  .tip { display: none !important; }
  .ci-page .page-head .lede { display: none; }
}
"""


NEW_CSS = r"""
/* figures: inline SVG from graphics.py */
.fig { margin: 1.25rem 0 0; max-width: 46rem; }
.fig svg { display: block; width: 100%; height: auto; background: var(--sheet); border: 1px solid var(--rule); border-radius: 4px; }
.fig text { font-family: var(--sans); }
.fig .lab { font-size: 13px; fill: var(--ink-2); }
.fig .lab-strong { font-size: 14px; font-weight: 600; fill: var(--ink); }
.fig .val { font-size: 14px; font-weight: 600; fill: var(--ink); font-variant-numeric: tabular-nums; }
.fig .ax { font-size: 12px; fill: var(--ink-2); font-variant-numeric: tabular-nums; }
.fig .num-in { font-family: var(--serif); font-size: 26px; fill: var(--sheet); }
.fig .in { font-size: 13px; font-weight: 600; fill: #fff; }
.fig .big { font-family: var(--serif); font-size: 24px; fill: var(--ink); }
.fig-wide { max-width: none; }
.slide .fig { max-width: 30em; margin: .9em 0 0; }
.slide .fig-wide { max-width: 34em; }
/* on a wide screen, slides with a picture put the text beside it */
@media (min-width: 1100px) and (min-height: 560px) and (orientation: landscape) {
  .slide.has-fig .slide-inner { max-width: 62em; }
  .has-fig .slide-body { display: grid; grid-template-columns: minmax(0, 17em) minmax(0, 1fr); column-gap: 1.75em; align-items: start; }
  .has-fig .slide-body > h2 { grid-column: 1 / -1; }
  .has-fig .slide-body > p, .has-fig .slide-body > .read-more { grid-column: 1; }
  .has-fig .slide-body > .fig { grid-column: 2; grid-row: 2 / span 4; margin: .2em 0 0; max-width: none; }
  .has-fig .slide-body > p:not(.footnote) { font-size: .92em; }
  .has-fig .footnote { margin-top: 1em; }
}

/* scripture links: open the NIV on Bible Gateway */
a.bible { text-decoration-style: dotted; }
.refs .bible::after, .ref-list .bible::after, .ho-refs .bible::after, .sh-ref .bible::after {
  content: "NIV"; font-family: var(--sans); font-size: .55em; font-weight: 600; letter-spacing: .05em;
  margin-left: .4em; vertical-align: .3em; color: var(--ink-2);
}

/* read more and next steps */
.read-more { margin-top: 1.2rem; font-size: .95rem; }
.slide .read-more { font-size: .66em; margin-top: 1.2em; max-width: 46em; }
.read-more > p { font-weight: 600; margin: 0 0 .15em; color: var(--ink-2); }
.read-more ul { list-style: none; margin: 0; padding: 0; display: flex; flex-wrap: wrap; gap: .25em 1.6em; }
.src { color: var(--ink-2); font-size: .88em; }
.next-list { list-style: none; margin: 1em 0 0; padding: 0; max-width: 32em; }
.next-list li { margin-bottom: .7em; }
.next-list a { font-family: var(--serif); font-size: 1.1em; }
.next-list span { display: block; font-size: .72em; color: var(--ink-2); }

/* home and steps page */
.band-lede { max-width: 44rem; color: var(--ink-2); }
.band-steps .fig { margin: 1rem 0 2.25rem; max-width: 54rem; }
.band-basics .fig { margin: 0; }
.credit { max-width: 42rem; color: var(--ink-2); font-size: .98rem; }
.steps .fig { margin: .5rem 0 0; max-width: 54rem; }
.steps-asides { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1.5rem; margin: 2rem 0 3rem; max-width: 60rem; align-items: start; }
.steps-asides .every { margin: 0; max-width: none; }
.course-notes h3 { font-family: var(--sans); font-size: .95rem; color: var(--green); margin: .8rem 0 .15rem; }
.course-notes p { margin: 0 0 .4rem; }

/* handout: money basics at a glance */
.glance { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .1rem 1.4rem; margin: 0 0 .3rem; }
.glance dt { font-weight: 600; font-size: .86rem; }
.glance dd { margin: 0 0 .25rem; font-size: .86rem; line-height: 1.3; }
.card-notes { font-size: .82rem; margin: .45rem 0 0; color: var(--ink-2); }

/* scripture handout */
.scripture-handout h1 { font-size: 1.9rem; margin-bottom: .15em; }
.sh-list { list-style: none; margin: .8rem 0 0; padding: 0; columns: 2; column-gap: 1.6rem; }
.sh-list li { display: grid; grid-template-columns: .9rem minmax(0, 1fr); gap: 0 .55rem; break-inside: avoid; padding: .32rem 0; border-bottom: 1px solid var(--rule); }
.sh-list .mark { width: .85rem; height: .85rem; border: 1.5px solid var(--ink); border-radius: 2px; margin-top: .3rem; }
.sh-list p { margin: 0; }
.sh-ref { font-family: var(--serif); font-weight: 600; }
.sh-para { font-size: .9rem; line-height: 1.35; }
.sh-where { font-size: .76rem; color: var(--ink-2); }
.sh-also h2 { font-size: 1.05rem; margin: 1.1rem 0 .3rem; padding-bottom: .15rem; border-bottom: 1.5px solid var(--ink); }
.sh-also p { font-size: .88rem; }

/* money basics page */
.basic { padding: 2rem 0 1rem; border-top: 1px solid var(--rule); max-width: 50rem; }
.basic h2 { font-weight: 400; }
.basic-lead { font-family: var(--serif); font-size: 1.15rem; line-height: 1.5; }
.basic .fig { margin: 1rem 0 1.25rem; }
.sheets-2 { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1.5rem; }
.source-list { padding-left: 1.2rem; }
.source-list li { margin-bottom: .45rem; }

@media (max-width: 860px) {
  .steps-asides, .sheets-2 { grid-template-columns: 1fr; }
}
@media (max-width: 560px) {
  .glance { grid-template-columns: 1fr; }
  .sh-list { columns: 1; }
}
@media print {
  a.bible::after { content: none !important; }
  .fig svg { border-color: #999; }
  .read-more, .next-list span { display: none; }
  .glance { grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0 .9rem; margin-bottom: .1rem; }
  .glance dt, .glance dd { font-size: 8.2pt; line-height: 1.22; }
  .glance dd { margin-bottom: .05in; }
  .with-basics .ho-block h2 { margin-top: .1in; }
  .card-notes { font-size: 8.4pt; margin-top: .04in; }
  .scripture-handout { font-size: 9pt; }
  .scripture-handout h1 { font-size: 17pt; }
  .scripture-handout .ho-big { font-size: 10pt; }
  .sh-list { column-gap: .25in; margin-top: .08in; }
  .sh-list li { padding: 2.2pt 0; border-color: #999; }
  .sh-list .mark { border-color: #000; width: 8pt; height: 8pt; margin-top: 2pt; }
  .sh-ref { font-size: 9.4pt; }
  .sh-para { font-size: 8.5pt; line-height: 1.25; }
  .sh-where { font-size: 7.4pt; }
  .sh-also h2 { font-size: 10pt; border-color: #000; }
  .sh-also p { font-size: 8.5pt; }
}
"""


def write(name, text):
    (OUT / name).write_text(text, encoding="utf-8")


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    write("style.css", CSS + CI_CSS + NEW_CSS)
    write("index.html", build_index())
    write("steps.html", build_steps())
    for key in TRACK_ORDER:
        write(C.TRACKS[key]["page"], build_track(key))
    for s in SESSIONS:
        write(f"{s['id']}.html", build_session(s))
        write(f"{s['id']}-handout.html", build_handout(s))
        write(f"{s['id']}-leader.html", build_leader(s))
    write("step-card.html", build_step_card())
    write("scripture.html", build_scripture())
    write("scripture-handout.html", build_scripture_handout())
    write("basics.html", build_basics())
    write("handouts.html", build_handouts())
    write("leader.html", build_leader_index())
    write("tools.html", build_tools())
    write("compound.html", build_compound())
    write("about.html", build_about())


# ---------------------------------------------------------------- checks

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.ids = [], set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        for key in ("href", "src"):
            if a.get(key):
                self.links.append(a[key])


def check():
    problems = []
    files = sorted(p.name for p in OUT.iterdir())
    parsed = {}
    for name in files:
        if name.endswith(".html"):
            p = LinkParser()
            p.feed((OUT / name).read_text(encoding="utf-8"))
            parsed[name] = p
    link_count, ext_count = 0, 0
    for name, p in parsed.items():
        for href in p.links:
            if href.startswith(("data:", "mailto:")):
                continue
            m = re.match(r"^https://([^/]+)/", href)
            if m and m.group(1) in EXTERNAL_HOSTS:
                ext_count += 1
                continue
            if re.match(r"^[a-z]+://", href) or href.startswith("//") or href.startswith("/"):
                problems.append(f"{name}: non-relative link {href}")
                continue
            link_count += 1
            target, _, frag = href.partition("#")
            target = target or name
            if target not in files:
                problems.append(f"{name}: broken link {href}")
            elif frag and target in parsed and frag not in parsed[target].ids:
                problems.append(f"{name}: missing anchor {href}")

    for s in SESSIONS:
        for suffix in ("", "-handout", "-leader"):
            if f"{s['id']}{suffix}.html" not in files:
                problems.append(f"missing {s['id']}{suffix}.html")

    expected = ["index.html", "steps.html", "one-night.html", "campus.html", "church.html", "step-card.html",
                "scripture.html", "scripture-handout.html", "basics.html", "handouts.html", "leader.html", "tools.html",
                "compound.html", "about.html", "style.css"]
    for name in expected:
        if name not in files:
            problems.append(f"missing {name}")

    for name in files:
        text = (OUT / name).read_text(encoding="utf-8")
        # Wording from the old Stewardship Steps that should no longer appear anywhere.
        for phrase in ("Stewardship Step", "starter buffer", "full reserve", "consumer debt",
                       "before we meet next", "Avalanche order"):
            if phrase.lower() in text.lower():
                problems.append(f"{name}: contains old wording '{phrase}'")
        if re.search(r"<script[^>]+src=|<link[^>]+href=\"https?:|@import|url\(https?:", text):
            problems.append(f"{name}: external resource")
        for a in re.findall(r'<a [^>]*href="https://[^"]*"[^>]*>', text):
            if 'target="_blank"' not in a or 'rel="noopener"' not in a:
                problems.append(f"{name}: outside link without target and rel: {a}")
    if "Before we meet again" in (OUT / "night.html").read_text(encoding="utf-8"):
        problems.append("night.html: One Night says 'Before we meet again'")

    # Every scripture reference in a session's scripture list is a link to the NIV.
    for s in SESSIONS:
        text = (OUT / f"{s['id']}.html").read_text(encoding="utf-8")
        for entry in s["d"]["scripture"]:
            ref = split_ref(entry)[0]
            if f'href="{attr(bible_url(ref))}"' not in text:
                problems.append(f"{s['id']}.html: {ref} is not linked to the NIV")
    rows, _ = all_scripture()
    sh = (OUT / "scripture-handout.html").read_text(encoding="utf-8")
    for r, para, _ in rows:
        if not para:
            problems.append(f"scripture handout: {r} has no paraphrase")
        if f'href="{attr(bible_url(r))}"' not in sh:
            problems.append(f"scripture handout: {r} is not linked")

    # The money basics examples, worked independently of graphics.py.
    def fv_months(p, months, start=0.0, i=.07 / 12):
        b = start
        for _ in range(months):
            b = b * (1 + i) + p
        return b
    sam = fv_months(0, 396, fv_months(200, 120))
    jordan = fv_months(200, 396)
    double = [fv_months(0, 120 * k, 10000) for k in range(1, 5)]
    card, save = ((1 + .24 / 365) ** 365 - 1) * 100, ((1 + .04 / 365) ** 365 - 1) * 100
    expect = {
        "compound": ["$346,000", "$309,000", "$24,000", "$79,200"],
        "rule72": ["$20,000", "$40,000", "$81,000", "$163,000"],
        "debt": ["$100", "36 months", "$2,001"],
        "apr": ["27.1%", "4.08%"],
        "match": ["$3,000", "$1,500"],
        "taxes": ["$12,000", "$36,000", "$8,160", "13.6%"],
    }
    if (round(sam, -3), round(jordan, -3)) != (346000, 309000):
        problems.append(f"early/late saver example is off: {sam:,.0f} and {jordan:,.0f}")
    if [round(x, -3) for x in double] != [20000, 40000, 81000, 163000]:
        problems.append(f"rule of 72 example is off: {[round(x) for x in double]}")
    if (f"{card:.1f}", f"{save:.2f}") != ("27.1", "4.08"):
        problems.append(f"APR/APY example is off: {card:.2f} and {save:.3f}")
    layers = [(12000, .10), (36000, .12), (12000, .22)]
    tax = sum(a * r for a, r in layers)
    if (round(tax), f"{tax / 60000 * 100:.1f}") != (8160, "13.6"):
        problems.append(f"bracket example is off: {tax:,.0f}")
    for key, needles in expect.items():
        for n in needles:
            if n not in C.BASICS[key]["text"]:
                problems.append(f"money basics '{key}' text is missing {n}")
    calc_lines_extra = [f"Money basics: Sam ${sam:,.0f}, Jordan ${jordan:,.0f}; $10,000 doubles to "
                        + ", ".join(f"${x:,.0f}" for x in double) + f"; 24% APR = {card:.2f}%, 4% = {save:.3f}% APY"]

    def fv(p, start, end, rate):
        n, i = (end - start) * 12, rate / 12
        return p * ((1 + i) ** n - 1) / i
    a, b = fv(200, 22, 65, .07), fv(200, 32, 65, .07)
    if round(a) != 655226 or round(b) != 308813:
        problems.append(f"growth formula gives {a:,.0f} and {b:,.0f}")
    calc_lines = [f"Formula: $200/month 22 to 65 at 7% = ${a:,.0f}; from 32 = ${b:,.0f}"] + calc_lines_extra

    node = shutil.which("node")
    if node:
        core = re.search(r'<script id="calc-core">(.*?)</script>', (OUT / "tools.html").read_text(), re.S).group(1)
        js = core + """
var a = growth(200, 22, 65, 7), b = growth(200, 32, 65, 7);
var d1 = payoff(5000, 24, 200), d2 = payoff(5000, 24, 100), d3 = payoff(1200, 0, 100);
console.log(JSON.stringify({a: Math.round(a.value), b: Math.round(b.value), ca: a.contributed, cb: b.contributed,
  d1: d1, d2: d2, d3: d3}));"""
        out = subprocess.run([node, "-e", js], capture_output=True, text=True)
        if out.returncode:
            problems.append("calculator JavaScript failed: " + out.stderr.strip())
        else:
            r = json.loads(out.stdout)
            if r["a"] != 655226 or r["b"] != 308813:
                problems.append(f"calculator page gives {r['a']} and {r['b']}")
            if not r["d2"].get("never"):
                problems.append("debt calculator should report never paid off at $100 on $5,000 at 24%")
            if r["d3"]["months"] != 12:
                problems.append("debt calculator: $1,200 at 0% and $100 should take 12 months")
            calc_lines.append(f"Tools page JS: 22 to 65 = ${r['a']:,} (put in ${r['ca']:,}); 32 to 65 = ${r['b']:,} (put in ${r['cb']:,})")
            calc_lines.append(f"Debt $5,000 at 24%, $200/month: {r['d1']['months']} months, ${r['d1']['interest']:,.0f} interest; "
                              f"at $100/month: never paid off")
        ci = re.search(r'<script id="ci-core">(.*?)</script>', (OUT / "compound.html").read_text(), re.S).group(1)
        js2 = ci + """
var base = {start: 22, end: 65, rate: 7, monthly: 200}, rows = planRows(base, {});
var a = simulate(rows, 22, 0), b = simulate(rows, 32, 0);
var ov = {30: {monthly: 500}, 40: {rate: -10}, 41: {rate: 7}, 50: {lump: -1000}};
var c = simulate(planRows(base, ov), 22, 0);
var r30 = planRows(base, ov);
console.log(JSON.stringify({a: Math.round(a.points[a.points.length-1].value), b: Math.round(b.points[b.points.length-1].value),
  put: a.points[a.points.length-1].put, years: a.years.length,
  carry: [r30[7].monthly, r30[8].monthly, r30[42].monthly, r30[17].rate, r30[18].rate, r30[19].rate],
  c: Math.round(c.points[c.points.length-1].value),
  once: Math.round(oppCost(1000, 'once', 20, 7).value * 100) / 100,
  zero: oppCost(100, 'month', 10, 0), week: oppCost(10, 'week', 1, 0)}));"""
        out2 = subprocess.run([node, "-e", js2], capture_output=True, text=True)
        if out2.returncode:
            problems.append("compound page JavaScript failed: " + out2.stderr.strip())
        else:
            r2 = json.loads(out2.stdout)
            if r2["a"] != 655226 or r2["b"] != 308813 or r2["years"] != 43:
                problems.append(f"compound page gives {r2['a']} and {r2['b']} over {r2['years']} years")
            if r2["carry"] != [200, 500, 500, 7, -10, 7]:
                problems.append(f"year-by-year changes do not carry down correctly: {r2['carry']}")
            if r2["zero"]["value"] != 12000 or round(r2["week"]["spent"], 6) != 520:
                problems.append("opportunity cost totals are off")
            calc_lines.append(f"Compound page: 22 to 65 = ${r2['a']:,}; 32 to 65 = ${r2['b']:,}; with sample year changes = ${r2['c']:,}")
            calc_lines.append(f"Opportunity cost: $1,000 once, 20 years at 7% = ${r2['once']:,.2f}")
    else:
        calc_lines.append("node not found; skipped the in-page JavaScript check")

    html_count = sum(1 for f in files if f.endswith(".html"))
    print(f"Built {len(files)} files ({html_count} pages) in {OUT}")
    print(f"Checked {link_count} internal links and {ext_count} outside links "
          f"({', '.join(EXTERNAL_HOSTS)}); {len(SESSIONS)} sessions with 3 pages each")
    for line in calc_lines:
        print(line)
    if problems:
        print("\nPROBLEMS:")
        for p in problems:
            print("  " + p)
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    build()
    sys.exit(check())
