"""Inline SVG graphics for the Entrusted site. Standard library only.

Every function returns a self-contained <figure> with an <svg> that carries a
<title> and <desc> for screen readers and native hover titles on the main marks.
Numbers in the charts are computed here from the same formulas the calculators
use, so they always match the text (build.py checks the key ones).

Colors follow the site's data palette: green for growth or the good outcome,
ochre for money put in or owed, gray dashed for a comparison.
"""
import html

GREEN = "#157a4b"
DEEP = "#1d5640"
OCHRE = "#b8862b"
GRAY = "#7d837e"
INK = "#1c221f"
INK2 = "#4e5651"
RULE = "#d6cebd"
GRID = "#e6dfd0"
SAND = "#ece5d5"
SHEET = "#fffdf8"
TINT = "#e2ebe4"


def esc(s):
    return html.escape(str(s), quote=True)


def money(v):
    return f"${v:,.0f}"


def kmoney(v):
    if v >= 1000:
        k = v / 1000
        return f"${k:,.0f}K"
    return f"${v:,.0f}"


def monthly_fv(payment, months, rate=0.07, start=0.0):
    """End-of-month deposits, monthly compounding (same as the calculators)."""
    i = rate / 12
    bal = start
    out = [bal]
    for _ in range(months):
        bal = bal * (1 + i) + payment
        out.append(bal)
    return out


def figure(uid, w, h, title, desc, body, cls="", caption=""):
    cap = f'<figcaption>{caption}</figcaption>' if caption else ""
    return (f'<figure class="fig {cls}">'
            f'<svg viewBox="0 0 {w} {h}" role="img" aria-labelledby="{uid}-t {uid}-d" '
            f'xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid meet">'
            f'<title id="{uid}-t">{esc(title)}</title><desc id="{uid}-d">{esc(desc)}</desc>'
            f'{body}</svg>{cap}</figure>')


def text(x, y, s, cls="lab", anchor="start", extra=""):
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}"{extra}>{esc(s)}</text>'


def rbar(x, y, w, h, fill, r=4, round_end="right", tip=""):
    """A bar with a 4px rounded data end and a square baseline end."""
    t = f"<title>{esc(tip)}</title>" if tip else ""
    if w <= 0 or h <= 0:
        return ""
    r = min(r, w / 2, h / 2)
    if round_end == "right":
        d = (f"M{x:.1f},{y:.1f} h{w - r:.1f} a{r},{r} 0 0 1 {r},{r} v{h - 2 * r:.1f} "
             f"a{r},{r} 0 0 1 {-r},{r} h{-(w - r):.1f} z")
    elif round_end == "top":
        d = (f"M{x:.1f},{y + h:.1f} v{-(h - r):.1f} a{r},{r} 0 0 1 {r},{-r} h{w - 2 * r:.1f} "
             f"a{r},{r} 0 0 1 {r},{r} v{h - r:.1f} z")
    else:  # all corners
        return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r}" fill="{fill}">{t}</rect>'
    return f'<path d="{d}" fill="{fill}">{t}</path>'


def polyline(points, color, width=2, dash=False, tip=""):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    da = ' stroke-dasharray="6 5"' if dash else ""
    t = f"<title>{esc(tip)}</title>" if tip else ""
    return (f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{width}" '
            f'stroke-linejoin="round" stroke-linecap="round"{da}>{t}</polyline>')


def area(points, base_y, color, opacity=0.1):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    x0, x1 = points[0][0], points[-1][0]
    return (f'<polygon points="{x0:.1f},{base_y:.1f} {pts} {x1:.1f},{base_y:.1f}" '
            f'fill="{color}" fill-opacity="{opacity}"/>')


def dot(x, y, color, tip=""):
    t = f"<title>{esc(tip)}</title>" if tip else ""
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{color}" stroke="{SHEET}" stroke-width="2">{t}</circle>'


def hgrid(x0, x1, y, label):
    return (f'<line x1="{x0}" x2="{x1}" y1="{y:.1f}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>'
            + text(x0 - 8, y + 4, label, "ax", "end"))


def legend(items, x, y, gap=26):
    """items: (color, label, dashed). Laid out left to right with estimated widths."""
    out, cx = [], x
    for color, label, dashed in items:
        if dashed:
            out.append(f'<line x1="{cx}" x2="{cx + 18}" y1="{y - 4}" y2="{y - 4}" stroke="{color}" stroke-width="2" stroke-dasharray="5 4"/>')
        else:
            out.append(f'<rect x="{cx}" y="{y - 10}" width="12" height="12" rx="2" fill="{color}"/>')
        out.append(text(cx + (24 if dashed else 18), y, label, "lab"))
        cx += (24 if dashed else 18) + len(label) * 7.1 + gap
    return "".join(out)


# ---------------------------------------------------------------- the Baby Steps staircase

STAIR_LABELS = [("$1,000", "starter fund"), ("Debt", "snowball"), ("3–6 months", "saved"),
                ("Invest", "15%"), ("Pay off", "the home"), ("Build wealth", "and give")]


def staircase(uid="stairs"):
    w, h = 720, 330
    base = 232
    step_w, gap, x0 = 108, 8, 24
    body = []
    # panels behind the two phases
    px = x0 + 3 * (step_w + gap) - gap / 2
    body.append(f'<rect x="{px:.1f}" y="6" width="{2 * (step_w + gap):.1f}" height="{base - 6}" fill="{TINT}" rx="4"/>')
    body.append(text(px + 10, 26, "Worked at the same time", "lab"))
    body.append(text(x0, 26, "One at a time, in order", "lab"))
    for i in range(6):
        x = x0 + i * (step_w + gap)
        sh = 40 + i * 32
        y = base - sh
        color = DEEP if i < 3 else (GREEN if i < 5 else OCHRE)
        top, bottom = STAIR_LABELS[i]
        body.append(rbar(x, y, step_w, sh, color, r=4, round_end="top",
                         tip=f"Baby Step {i + 1}: {top} {bottom}"))
        body.append(text(x + step_w / 2, y + 30, str(i + 1), "num-in", "middle"))
        body.append(text(x + step_w / 2, base + 22, top, "lab-strong", "middle"))
        body.append(text(x + step_w / 2, base + 40, bottom, "lab", "middle"))
    body.append(f'<line x1="{x0 - 8}" x2="{x0 + 6 * (step_w + gap) - gap + 8}" y1="{base}" y2="{base}" stroke="{INK}" stroke-width="1.5"/>')
    # the every-step band
    by = base + 58
    body.append(f'<rect x="{x0 - 8}" y="{by}" width="{6 * (step_w + gap) - gap + 16}" height="30" rx="4" fill="{SAND}"/>')
    body.append(text(w / 2, by + 20, "At every step: give first and keep a written budget", "lab-strong", "middle"))
    return figure(uid, w, h, "The Baby Steps",
                  "Six rising steps. Steps 1 to 3 are done one at a time: $1,000 starter emergency fund, the debt snowball, "
                  "and 3 to 6 months of expenses saved. Steps 4 and 5 are worked at the same time: invest 15% and "
                  "pay off the home. Step 6 is build wealth and give. Underneath all of them: give first and keep a written budget.",
                  "".join(body), "fig-wide")


# ---------------------------------------------------------------- compound: start at 22 vs 32

def _age_chart_frame(x0, x1, y0, y1, a0, a1, vmax, yticks, xticks, fmt=kmoney):
    def sx(age):
        return x0 + (age - a0) / (a1 - a0) * (x1 - x0)

    def sy(v):
        return y1 - v / vmax * (y1 - y0)
    out = []
    for v in yticks:
        out.append(hgrid(x0, x1, sy(v), fmt(v)))
    for a in xticks:
        out.append(text(sx(a), y1 + 20, str(a), "ax", "middle"))
    out.append(f'<line x1="{x0}" x2="{x1}" y1="{y1}" y2="{y1}" stroke="{INK2}" stroke-width="1"/>')
    return sx, sy, out


def compound(uid="compound"):
    w, h = 660, 300
    x0, x1, y0, y1 = 64, 500, 24, 250
    sx, sy, body = _age_chart_frame(x0, x1, y0, y1, 22, 65, 700000, [0, 200000, 400000, 600000],
                                    [22, 32, 42, 52, 65])
    early = monthly_fv(200, 43 * 12)
    late = [0.0] * 120 + monthly_fv(200, 33 * 12)
    put = [200 * m for m in range(43 * 12 + 1)]
    yearly = range(0, 43 * 12 + 1, 12)
    pe = [(sx(22 + m / 12), sy(early[m])) for m in yearly]
    pl = [(sx(22 + m / 12), sy(late[m])) for m in yearly if m >= 120]
    pp = [(sx(22 + m / 12), sy(put[m])) for m in yearly]
    body.append(area(pe, y1, GREEN))
    body.append(area(pp, y1, OCHRE, 0.12))
    body.append(polyline(pp, OCHRE, tip=f"Put in from 22: {money(put[-1])}"))
    body.append(polyline(pl, GRAY, dash=True, tip=f"Starting at 32: {money(late[-1])} at 65"))
    body.append(polyline(pe, GREEN, tip=f"Starting at 22: {money(early[-1])} at 65"))
    ex = sx(65)
    body.append(dot(ex, sy(early[-1]), GREEN, f"Start at 22: {money(early[-1])}"))
    body.append(dot(ex, sy(late[-1]), GRAY, f"Start at 32: {money(late[-1])}"))
    body.append(dot(ex, sy(put[-1]), OCHRE, f"Put in: {money(put[-1])}"))
    lx = ex + 12
    body.append(text(lx, sy(early[-1]) + 1, money(early[-1]), "val"))
    body.append(text(lx, sy(early[-1]) + 18, "start at 22", "lab"))
    body.append(text(lx, sy(late[-1]) + 1, money(late[-1]), "val"))
    body.append(text(lx, sy(late[-1]) + 18, "start at 32", "lab"))
    body.append(text(lx, sy(put[-1]) - 6, money(put[-1]), "val"))
    body.append(text(lx, sy(put[-1]) + 11, "put in from 22", "lab"))
    body.append(text(x0, h - 6, "Age", "ax"))
    body.append(legend([(GREEN, "Start at 22", False), (GRAY, "Start at 32", True), (OCHRE, "Money put in", False)],
                       x0 + 40, h - 6))
    return figure(uid, w, h, "$200 a month at an assumed 7%: starting at 22 versus 32",
                  f"Starting at 22, $200 a month grows to {money(early[-1])} by 65 from {money(put[-1])} put in. "
                  f"Starting at 32, it grows to {money(late[-1])}. Returns are assumed, not guaranteed.",
                  "".join(body))


# ---------------------------------------------------------------- early saver vs late saver

def early_late(uid="earlylate"):
    w, h = 660, 330
    x0, x1, y0, y1 = 64, 520, 40, 240
    sx, sy, body = _age_chart_frame(x0, x1, y0, y1, 22, 65, 400000, [0, 100000, 200000, 300000, 400000],
                                    [22, 32, 42, 52, 65])
    sam = monthly_fv(200, 120)
    i = 0.07 / 12
    for _ in range(33 * 12):
        sam.append(sam[-1] * (1 + i))
    jordan = [0.0] * 120 + monthly_fv(200, 33 * 12)
    yearly = range(0, 43 * 12 + 1, 12)
    ps = [(sx(22 + m / 12), sy(sam[m])) for m in yearly]
    pj = [(sx(22 + m / 12), sy(jordan[m])) for m in yearly if m >= 120]
    body.append(area(ps, y1, GREEN))
    body.append(polyline(pj, OCHRE, tip=f"Jordan at 65: {money(jordan[-1])}"))
    body.append(polyline(ps, GREEN, tip=f"Sam at 65: {money(sam[-1])}"))
    ex = sx(65)
    body.append(dot(ex, sy(sam[-1]), GREEN, f"Sam: {money(sam[-1])}"))
    body.append(dot(ex, sy(jordan[-1]), OCHRE, f"Jordan: {money(jordan[-1])}"))
    body.append(text(ex + 12, sy(sam[-1]) - 2, f"Sam {money(sam[-1])}", "val"))
    body.append(text(ex + 12, sy(jordan[-1]) + 14, f"Jordan {money(jordan[-1])}", "val"))
    # years each one pays in
    py = y1 + 40
    body.append(text(x0 - 8, py + 7, "Paying in", "ax", "end"))
    body.append(rbar(sx(22), py, sx(32) - sx(22), 8, GREEN, r=4, round_end="all", tip="Sam pays in from 22 to 32: $24,000"))
    body.append(text(sx(32) + 8, py + 8, "Sam: $24,000", "lab"))
    body.append(rbar(sx(32), py + 18, sx(65) - sx(32), 8, OCHRE, r=4, round_end="all", tip="Jordan pays in from 32 to 65: $79,200"))
    body.append(text(sx(65) + 8, py + 26, "Jordan: $79,200", "lab"))
    body.append(legend([(GREEN, "Sam: $200 a month from 22 to 32, then stops", False),
                        (OCHRE, "Jordan: $200 a month from 32 to 65", False)], x0, 20, 18))
    return figure(uid, w, h, "Early saver versus late saver at an assumed 7%",
                  f"Sam invests $200 a month from 22 to 32, $24,000 in all, then stops. Jordan invests $200 a month from 32 to 65, "
                  f"$79,200 in all. At 65 Sam has {money(sam[-1])} and Jordan has {money(jordan[-1])}. Returns are not guaranteed.",
                  "".join(body))


# ---------------------------------------------------------------- rule of 72

def doubling(uid="double"):
    w, h = 640, 270
    x0, x1, y0, y1 = 64, 600, 30, 220
    vals = monthly_fv(0, 40 * 12, start=10000)
    ages = [22, 32, 42, 52, 62]
    pts = [vals[(a - 22) * 12] for a in ages]
    vmax = 180000
    body = []
    for v in (0, 50000, 100000, 150000):
        y = y1 - v / vmax * (y1 - y0)
        body.append(hgrid(x0, x1, y, kmoney(v)))
    slot = (x1 - x0) / len(ages)
    bw = 28
    for k, (a, v) in enumerate(zip(ages, pts)):
        cx = x0 + slot * (k + .5)
        bh = v / vmax * (y1 - y0)
        body.append(rbar(cx - bw / 2, y1 - bh, bw, bh, GREEN, round_end="top", tip=f"Age {a}: {money(v)}"))
        body.append(text(cx, y1 - bh - 8, kmoney(round(v, -3)), "val", "middle"))
        body.append(text(cx, y1 + 20, f"Age {a}", "ax", "middle"))
    body.append(f'<line x1="{x0}" x2="{x1}" y1="{y1}" y2="{y1}" stroke="{INK2}" stroke-width="1"/>')
    body.append(text(x0, h - 8, "$10,000 invested once at 22, nothing added, assumed 7% a year", "lab"))
    return figure(uid, w, h, "The rule of 72: money doubles about every 10 years at 7%",
                  "A one-time $10,000 at age 22 grows to about $20,000 at 32, $40,000 at 42, $81,000 at 52 and $163,000 at 62 "
                  "at an assumed 7% a year. Returns are not guaranteed.", "".join(body))


# ---------------------------------------------------------------- debt at 24%

def debt_balances(balance, apr, payment, months):
    i = apr / 12
    out, b, paid_months, interest = [balance], balance, None, 0.0
    for m in range(1, months + 1):
        if b > 0.005:
            c = b * i
            interest += c
            b = max(0.0, b + c - payment)
            if b <= 0.005 and paid_months is None:
                paid_months = m
        out.append(b)
    return out, paid_months, interest


def debt_trap(uid="debt"):
    w, h = 660, 280
    x0, x1, y0, y1 = 64, 470, 30, 220
    months = 60
    low, _, _ = debt_balances(5000, .24, 100, months)
    high, done, interest = debt_balances(5000, .24, 200, months)

    def sx(m):
        return x0 + m / months * (x1 - x0)

    def sy(v):
        return y1 - v / 6000 * (y1 - y0)
    body = []
    for v in (0, 2500, 5000):
        body.append(hgrid(x0, x1, sy(v), money(v)))
    for m, lab in ((0, "Start"), (12, "1 year"), (24, "2 years"), (36, "3 years"), (48, "4 years"), (60, "5 years")):
        body.append(text(sx(m), y1 + 20, lab, "ax", "middle"))
    body.append(f'<line x1="{x0}" x2="{x1}" y1="{y1}" y2="{y1}" stroke="{INK2}" stroke-width="1"/>')
    pl = [(sx(m), sy(low[m])) for m in range(months + 1)]
    ph = [(sx(m), sy(high[m])) for m in range(done + 1)]
    body.append(polyline(pl, OCHRE, tip="$100 a month: still $5,000 after five years"))
    body.append(polyline(ph, GREEN, tip=f"$200 a month: paid off in {done} months"))
    body.append(dot(sx(months), sy(low[-1]), OCHRE))
    body.append(dot(sx(done), sy(0), GREEN))
    body.append(text(sx(months) + 12, sy(5000) - 2, "$100 a month:", "val"))
    body.append(text(sx(months) + 12, sy(5000) + 16, "still $5,000 after 5 years", "lab"))
    body.append(text(sx(done) + 14, sy(0) - 56, "$200 a month:", "val"))
    body.append(text(sx(done) + 14, sy(0) - 38, f"paid off in {done} months,", "lab"))
    body.append(text(sx(done) + 14, sy(0) - 20, f"{money(interest)} in interest", "lab"))
    body.append(text(x0, h - 8, "A $5,000 card balance at 24% APR, nothing new charged", "lab"))
    return figure(uid, w, h, "A $5,000 card balance at 24% APR",
                  f"Paying $100 a month only covers the interest, so the balance stays at $5,000. "
                  f"Paying $200 a month clears it in {done} months with {money(interest)} of interest.", "".join(body))


# ---------------------------------------------------------------- APR vs APY

def apr_apy(uid="aprapy"):
    w, h = 660, 210
    card = ((1 + .24 / 365) ** 365 - 1) * 100
    save = ((1 + .04 / 365) ** 365 - 1) * 100
    body = []
    tiles = [(16, OCHRE, "When you borrow", "24% APR", f"{card:.1f}%", "what a year really costs,",
              "compounded daily"),
             (340, GREEN, "When you save", "4% rate", f"{save:.2f}% APY", "what you really earn in a year,",
              "compounded daily")]
    for x, color, head, left, right, c1, c2 in tiles:
        body.append(f'<rect x="{x}" y="10" width="304" height="186" rx="4" fill="{SHEET}" stroke="{RULE}"/>')
        body.append(f'<rect x="{x}" y="10" width="304" height="6" rx="2" fill="{color}"/>')
        body.append(text(x + 18, 46, head, "lab-strong"))
        body.append(text(x + 18, 104, left, "big"))
        body.append(f'<path d="M{x + 134},{95} h24 m-8,-7 l8,7 l-8,7" fill="none" stroke="{INK2}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')
        body.append(text(x + 168, 104, right, "big"))
        body.append(text(x + 18, 150, c1, "lab"))
        body.append(text(x + 18, 170, c2, "lab"))
    return figure(uid, w, h, "APR versus APY",
                  f"A card at 24% APR compounding daily costs about {card:.1f}% a year. "
                  f"Savings at a 4% rate compounding daily earn an APY of {save:.2f}%.", "".join(body))


# ---------------------------------------------------------------- 401(k) match

def _segbar(x, y, total_w, parts, scale_total, h=28):
    """Tall segmented bar: parts are (value, color, inside label). 2px surface gaps."""
    out, cx = [], x
    for k, (v, color, label) in enumerate(parts):
        wv = v / scale_total * total_w - (2 if k < len(parts) - 1 else 0)
        out.append(f'<rect x="{cx:.1f}" y="{y}" width="{wv:.1f}" height="{h}" rx="4" fill="{color}"><title>{esc(label)}</title></rect>')
        if label and wv > len(label) * 7.6 + 16:
            out.append(text(cx + 10, y + h / 2 + 5, label, "in"))
        cx += wv + 2
    return out


def match(uid="match"):
    w, h = 660, 170
    body = [text(16, 24, "Example: $50,000 salary, employer matches half of the first 6% you put in", "lab")]
    body += _segbar(16, 44, 560, [(3000, OCHRE, "You put in $3,000"), (1500, GREEN, "Employer $1,500")], 4500)
    body.append(text(586, 64, "$4,500", "val"))
    body.append(text(586, 82, "a year", "lab"))
    body.append(legend([(OCHRE, "You: 6% of pay", False), (GREEN, "Employer match: an instant 50% return", False)], 16, 112, 22))
    body.append(text(16, 150, "Matches vary. Ask HR for yours, and how long until it is fully yours to keep.", "lab"))
    return figure(uid, w, h, "How a 401(k) match adds to what you put in",
                  "On a $50,000 salary you put in 6%, or $3,000 a year. An employer that matches half of the first 6% adds $1,500, "
                  "so $4,500 a year goes into your account.", "".join(body))


# ---------------------------------------------------------------- tax brackets

def brackets(uid="brackets"):
    w, h = 660, 232
    layers = [(12000, .10, DEEP), (36000, .12, GREEN), (12000, .22, OCHRE)]
    total = sum(a for a, _, _ in layers)
    tax = sum(a * r for a, r, _ in layers)
    body = [text(16, 24, "Example: $60,000 of taxable income, single filer, round-number brackets", "lab")]
    x, bw, y = 16, 560, 44
    cx = x
    for k, (amt, rate, color) in enumerate(layers):
        wv = amt / total * bw - (2 if k < len(layers) - 1 else 0)
        t = f"{rate * 100:.0f}% on {money(amt)} = {money(amt * rate)}"
        body.append(f'<rect x="{cx:.1f}" y="{y}" width="{wv:.1f}" height="34" rx="4" fill="{color}"><title>{esc(t)}</title></rect>')
        body.append(text(cx + wv / 2, y + 22, f"{rate * 100:.0f}%", "in", "middle"))
        body.append(text(cx + wv / 2, y + 58, money(amt * rate), "val", "middle"))
        body.append(text(cx + wv / 2, y + 76, f"on {money(amt)}", "lab", "middle"))
        cx += wv + 2
    body.append(text(586, y + 22, money(total), "val"))
    body.append(text(x, 150, f"Total tax {money(tax)}: {tax / total * 100:.1f}% of the {money(total)}. That is your effective rate.", "lab-strong"))
    body.append(text(x, 174, "Your top bracket is 22%, but only the last $12,000 is taxed at it.", "lab"))
    body.append(text(x, 196, "A $1,000 raise is taxed at 22%: you still keep $780 of it.", "lab"))
    body.append(text(x, 218, "Round numbers for teaching. Real brackets change most years.", "lab"))
    return figure(uid, w, h, "How tax brackets work",
                  "A single filer with $60,000 of taxable income pays 10% on the first $12,000 ($1,200), 12% on the next $36,000 ($4,320) "
                  "and 22% on the last $12,000 ($2,640). Total tax is $8,160, or 13.6% of $60,000.", "".join(body))


# ---------------------------------------------------------------- shares and index funds

def shares(uid="shares"):
    w, h = 660, 260
    body = []
    # one company, 10 x 10 pieces, one owned
    s, g = 14, 2
    ox, oy = 40, 36
    body.append(text(ox, 22, "One company", "lab-strong"))
    for r in range(10):
        for c in range(10):
            fill = GREEN if (r, c) == (0, 0) else SAND
            body.append(f'<rect x="{ox + c * (s + g)}" y="{oy + r * (s + g)}" width="{s}" height="{s}" rx="2" fill="{fill}"/>')
    body.append(text(ox, oy + 10 * (s + g) + 22, "One share: a small piece of it", "lab"))
    # index fund: many companies, one piece of each
    fx, fy = 300, 36
    body.append(text(fx, 22, "An index fund", "lab-strong"))
    body.append(f'<rect x="{fx}" y="{fy}" width="330" height="160" rx="6" fill="none" stroke="{INK2}" stroke-width="1.5"/>')
    ms, mg = 6, 1.5
    for k in range(18):
        cx = fx + 14 + (k % 6) * 52
        cy = fy + 14 + (k // 6) * 50
        for r in range(5):
            for c in range(5):
                fill = GREEN if (r, c) == (0, 0) else SAND
                body.append(f'<rect x="{cx + c * (ms + mg):.1f}" y="{cy + r * (ms + mg):.1f}" width="{ms}" height="{ms}" rx="1" fill="{fill}"/>')
    body.append(text(fx, oy + 10 * (s + g) + 22, "A small piece of hundreds of companies", "lab"))
    body.append(legend([(GREEN, "What you own", False)], 40, h - 10))
    return figure(uid, w, h, "A share of stock versus an index fund",
                  "A share of stock is one small piece of one company. An index fund owns a small piece of hundreds of companies at once.",
                  "".join(body))


# ---------------------------------------------------------------- a written budget

BUDGET_EXAMPLE = [("Giving", 300), ("Saving", 300), ("Housing", 900), ("Food", 450),
                  ("Transport", 350), ("Other needs", 450), ("Fun", 250)]


def budget(uid="budget"):
    income = sum(v for _, v in BUDGET_EXAMPLE)
    rows = len(BUDGET_EXAMPLE) + 2
    rh = 30
    w, h = 660, rows * rh + 46
    lx, bx0, bx1 = 150, 160, 540

    def sx(v):
        return bx0 + v / income * (bx1 - bx0)
    body = [text(16, 20, f"Example: {money(income)} a month after tax", "lab")]
    y = 36
    body.append(text(lx, y + 15, "Income", "lab-strong", "end"))
    body.append(rbar(bx0, y + 2, sx(income) - bx0, 18, GREEN, tip=f"Income: {money(income)}"))
    body.append(text(sx(income) + 8, y + 16, money(income), "val"))
    left = income
    for name, v in BUDGET_EXAMPLE:
        y += rh
        body.append(text(lx, y + 15, name, "lab", "end"))
        body.append(rbar(sx(left - v), y + 2, sx(left) - sx(left - v), 18, OCHRE, round_end="all", tip=f"{name}: {money(v)}"))
        body.append(text(sx(left) + 8, y + 16, money(v), "lab"))
        left -= v
    y += rh
    body.append(text(lx, y + 15, "Left over", "lab-strong", "end"))
    body.append(f'<line x1="{bx0}" x2="{bx0}" y1="{y}" y2="{y + 22}" stroke="{INK}" stroke-width="2"/>')
    body.append(text(bx0 + 10, y + 16, "$0: every dollar has a job", "val"))
    return figure(uid, w, h, "A zero-based budget",
                  f"An example {money(income)} monthly income. Giving and saving come off first, then housing, food, transport, "
                  "other needs and fun, until nothing is left without a job.", "".join(body))


# ---------------------------------------------------------------- emergency fund

def efund(uid="efund"):
    w, h = 660, 190
    x0, x1 = 30, 620
    top = 18000

    def sx(v):
        return x0 + v / top * (x1 - x0)
    body = [text(x0, 22, "Example: $3,000 of essential expenses a month", "lab")]
    y = 56
    body.append(f'<rect x="{sx(9000):.1f}" y="{y - 10}" width="{sx(18000) - sx(9000):.1f}" height="48" rx="4" fill="{TINT}"/>')
    body.append(rbar(x0, y, sx(1000) - x0, 28, GREEN, tip="Baby Step 1: $1,000"))
    body.append(f'<line x1="{x0}" x2="{x1}" y1="{y + 40}" y2="{y + 40}" stroke="{INK2}" stroke-width="1"/>')
    for v, lab, anc in ((0, "$0", "start"), (9000, "$9,000: 3 months", "middle"), (18000, "$18,000: 6 months", "end")):
        body.append(f'<line x1="{sx(v):.1f}" x2="{sx(v):.1f}" y1="{y + 40}" y2="{y + 46}" stroke="{INK2}"/>')
        body.append(text(sx(v), y + 62, lab, "ax", anc))
    body.append(text(sx(1000) + 10, y + 19, "Baby Step 1: $1,000, fast", "val"))
    body.append(text(sx(9000), y + 92, "Baby Step 3: 3 to 6 months of expenses", "val"))
    body.append(text(sx(9000), y + 110, "after all debt but the house is gone", "lab"))
    return figure(uid, w, h, "Starter emergency fund versus full emergency fund",
                  "Baby Step 1 is $1,000. Baby Step 3 is three to six months of expenses, which for $3,000 a month of essentials "
                  "is $9,000 to $18,000.", "".join(body))


# ---------------------------------------------------------------- the debt snowball

SNOWBALL = [("Medical bill", 500, 25), ("Credit card", 2000, 60), ("Car loan", 7000, 250), ("Student loan", 15000, 165)]
SNOWBALL_EXTRA = 300


def snowball(uid="snowball"):
    rh = 52
    w, h = 660, 40 + rh * len(SNOWBALL) + 30
    bx0, bx1 = 170, 360
    vmax = max(b for _, b, _ in SNOWBALL)
    pmax = SNOWBALL_EXTRA + sum(m for _, _, m in SNOWBALL)
    px0, px1 = 450, 600
    body = [text(16, 22, "Smallest first", "lab-strong"),
            text(bx0, 22, "Balance", "lab-strong"),
            text(px0, 22, "Payment on the target", "lab-strong")]
    pay = SNOWBALL_EXTRA
    y = 40
    for k, (name, bal, minimum) in enumerate(SNOWBALL):
        pay += minimum
        body.append(text(16, y + 20, f"{k + 1}. {name}", "lab"))
        bw = bal / vmax * (bx1 - bx0)
        body.append(rbar(bx0, y + 6, bw, 18, OCHRE, tip=f"{name}: {money(bal)}"))
        body.append(text(bx0 + bw + 8, y + 20, money(bal), "lab"))
        pw = pay / pmax * (px1 - px0)
        body.append(rbar(px0, y + 6, pw, 18, GREEN, tip=f"Paying {name}: {money(pay)} a month"))
        body.append(text(px0 + pw + 8, y + 20, money(pay), "val"))
        if k < len(SNOWBALL) - 1:
            body.append(f'<path d="M{px0 + 10},{y + 30} v14 m-5,-5 l5,5 l5,-5" fill="none" stroke="{INK2}" stroke-width="1.5" stroke-linecap="round"/>')
        y += rh
    body.append(text(16, h - 12, f"Example: ${SNOWBALL_EXTRA} a month extra, and each paid-off payment rolls into the next debt", "lab"))
    return figure(uid, w, h, "The debt snowball",
                  "Four debts listed from smallest balance to largest. Each time one is paid off, its payment rolls into the next, "
                  f"so the payment grows from {money(SNOWBALL_EXTRA + SNOWBALL[0][2])} to {money(pmax)} a month.", "".join(body))


# ---------------------------------------------------------------- live like a student

def gap(uid="gap"):
    w, h = 660, 190
    total = 4000
    x0, bw = 140, 440
    body = [text(16, 22, "Example: monthly spending in college, and take-home pay on a first salary", "lab")]
    body.append(text(x0 - 10, 62, "In college", "lab-strong", "end"))
    body += _segbar(x0, 44, bw, [(1500, OCHRE, "Spending $1,500")], total)
    body.append(text(x0 - 10, 112, "First salary", "lab-strong", "end"))
    body += _segbar(x0, 94, bw, [(1800, OCHRE, "Spending $1,800"), (2200, GREEN, "The gap $2,200")], total)
    body.append(text(x0 + bw + 8, 112, "$4,000", "val"))
    body.append(legend([(OCHRE, "Spending", False), (GREEN, "The gap: giving, saving, paying off debt", False)], x0, 160, 22))
    return figure(uid, w, h, "Keep living like a student",
                  "In college, spending is $1,500 a month. On a $4,000 take-home salary, spending rises only to $1,800, "
                  "leaving a $2,200 gap for giving, saving and paying off debt.", "".join(body))


GRAPHICS = {
    "staircase": staircase,
    "compound": compound,
    "early_late": early_late,
    "doubling": doubling,
    "debt_trap": debt_trap,
    "apr_apy": apr_apy,
    "match": match,
    "brackets": brackets,
    "shares": shares,
    "budget": budget,
    "efund": efund,
    "snowball": snowball,
    "gap": gap,
}


def render(key, uid=None):
    return GRAPHICS[key](uid or key)
