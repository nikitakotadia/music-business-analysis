"""Build docs/index.html from results.json and the SQL files.

Run from the project root:  python docs/build_site.py
results.json holds rates, shares, medians and indexes only. No counts, no revenue.
"""
import html
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = Path(__file__).resolve().parent
SQL = ROOT / "sql"
R = json.loads((SITE / "results.json").read_text())

GITHUB = "https://github.com/nikitakotadia/music-business-analysis"
LINKEDIN = "https://www.linkedin.com/in/nikitakotadia/"


def pct(x, dp=0):
    return f"{x:.{dp}f}%"


def sql_block(*names):
    parts = []
    for n in names:
        text = (SQL / n).read_text().strip()
        parts.append(f'<span class="sql-file">-- sql/{n}</span>\n{html.escape(text)}')
    joined = "\n\n".join(parts)
    return (
        '<details class="query"><summary><span class="q-icon" aria-hidden="true"></span>Show the SQL</summary>'
        f'<pre><code>{joined}</code></pre></details>'
    )


# ---------- values ----------

conv_pct = R["conversion_pct"]
one_in = R["one_in"]
median_days = R["median_days"]
rep = {r["list_status"]: r["repeat_pct"] for r in R["repeat"]}
on, off = rep["On the list"], rep["Not on the list"]
ratio = round(on / off)
ttc = R["time_to_convert"]
within_week = ttc[0]["pct"]
after_month = ttc[2]["pct"] + ttc[3]["pct"]
after_3m = ttc[3]["pct"]
period = {r["period"].split(". ", 1)[1]: r["joined_list_first_pct"] for r in R["list_share_by_period"]}
early, recent = period["2021 to 2023"], period["2024 to 2026"]
cat = R["catalogue"]
co_pct = R["co_produced_pct"]
bands = R["price_bands"]
mix = R["channel_mix"]
tests = {k: v.replace("<", "&lt;") for k, v in R["tests"].items()}
lift = 0.5 / conv_pct * 100


# ---------- visuals ----------

def dot_grid(total, filled, cls=""):
    cells = "".join(f'<i class="{"on" if i < filled else ""}"></i>' for i in range(total))
    return f'<div class="dotgrid {cls}" role="img" aria-label="{filled} of every {total}">{cells}</div>'


def hundred(filled_pct, label):
    n = round(filled_pct)
    cells = "".join(f'<i class="{"on" if i < n else ""}"></i>' for i in range(100))
    return f'<div class="hundred" role="img" aria-label="{label}">{cells}</div>'


# Time to convert, drawn as clips on a timeline with a log time axis (1 hour to 1 year).
LO, HI = math.log10(1 / 24), math.log10(365)
pos = lambda d: (math.log10(d) - LO) / (HI - LO) * 100
edges = [1 / 24, 7, 30, 90, 365]
names = ["Within a week", "1 to 4 weeks", "1 to 3 months", "3 to 12 months"]
clips = []
for i, r in enumerate(ttc):
    left, right = pos(edges[i]), pos(edges[i + 1])
    h = r["pct"] / 40 * 100
    clips.append(
        f'<div class="clip{" late" if i >= 2 else ""}" style="left:{left:.2f}%;width:{right - left:.2f}%;--h:{h:.1f}%">'
        f'<span class="clip-val">{pct(r["pct"])}</span><span class="clip-name">{names[i]}</span></div>'
    )
ticks = "".join(
    f'<span class="tick" style="left:{pos(d):.2f}%">{t}</span>'
    for d, t in [(1 / 24, "1 hr"), (1, "1 day"), (7, "1 wk"), (30, "1 mo"), (90, "3 mo"), (365, "1 yr")]
)
timeline = (
    '<div class="timeline" role="img" aria-label="Share of conversions by time from free download to first purchase">'
    f'<div class="lane">{"".join(clips)}'
    f'<div class="median" style="left:{pos(median_days):.2f}%"><span>median · {median_days} days</span></div></div>'
    f'<div class="ruler">{ticks}</div></div>'
)

price_rows = "".join(
    f'<div class="bar-row"><span class="bar-label">{lab}</span>'
    f'<span class="bar"><span class="fill{" accent" if i == 0 else ""}" style="--v:{r["pct_of_items"] / 60 * 100:.1f}%"></span></span>'
    f'<span class="bar-val">{pct(r["pct_of_items"])}</span></div>'
    for i, (r, lab) in enumerate(zip(bands, ["Under $35", "$35 to $59", "$60 to $99", "$100+"]))
)

mix_rows = "".join(
    f'<div class="bar-row"><span class="bar-label">{r["period"].replace("2024 to 2026", "2024+")}</span>'
    f'<span class="bar stack"><span class="fill accent" style="--v:{r["own_storefront_pct"]:.0f}%"></span></span>'
    f'<span class="bar-val">{r["own_storefront_pct"]:.0f}%</span></div>'
    for r in mix
)

waves_svg = "".join(
    f'<path d="M0 {60 + i * 7} C 160 {20 + i * 7}, 300 {120 + i * 7}, 460 {64 + i * 7} S 760 {10 + i * 7}, 1000 {56 + i * 7}"/>'
    for i in range(6)
)


page = f"""<title>Free Downloads to Customers</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="Nikita Kotadia, data analyst: do free music downloads turn into paying customers? A SQL case study on her own music business.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* Layout: a DAW-style case study. Fixed transport bar with a scroll playhead; light pages bracket one dark "studio" band for the findings. */
:root {{
  --bg: #EEF0F3;
  --surface: #E3E6EB;
  --fg: #121418;
  --fg2: #50565F;
  --line: #C6CBD2;
  --accent: #2B45D4;
  --studio: #0F1115;
  --studio-2: #181B21;
  --studio-fg: #ECEEF2;
  --studio-fg2: #9AA1AC;
  --studio-line: #2A2F38;
  --studio-accent: #8FA3FF;
  --display: "Oswald", "Arial Narrow", "Helvetica Neue", sans-serif;
  --body: "IBM Plex Sans", "Helvetica Neue", Arial, sans-serif;
  --mono: "IBM Plex Mono", ui-monospace, "SF Mono", Menlo, monospace;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --bg: #14161A; --surface: #1C1F25; --fg: #ECEEF2; --fg2: #A0A7B2; --line: #2E333C; --accent: #8FA3FF;
    --studio: #0B0C0F; --studio-2: #15171C; --studio-line: #262A32; color-scheme: dark;
  }}
}}
:root[data-theme="dark"] {{
  --bg: #14161A; --surface: #1C1F25; --fg: #ECEEF2; --fg2: #A0A7B2; --line: #2E333C; --accent: #8FA3FF;
  --studio: #0B0C0F; --studio-2: #15171C; --studio-line: #262A32; color-scheme: dark;
}}

* {{ box-sizing: border-box; }}
html {{ -webkit-text-size-adjust: 100%; scroll-behavior: smooth; }}
@media (prefers-reduced-motion: reduce) {{ html {{ scroll-behavior: auto; }} }}
body {{ margin: 0; background: var(--bg); color: var(--fg); font-family: var(--body); font-size: 17px; line-height: 1.6; }}
body::before {{ content: ""; position: fixed; inset: 0 0 auto; height: env(safe-area-inset-top, 0px); z-index: 30; background: var(--bg); }}
a {{ color: inherit; text-decoration-color: currentColor; text-underline-offset: 4px; text-decoration-thickness: 1px; }}
a:focus-visible, summary:focus-visible, button:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 3px; }}

.wrap {{ max-width: 1180px; margin: 0 auto; padding-left: max(20px, env(safe-area-inset-left, 0px)); padding-right: max(20px, env(safe-area-inset-right, 0px)); }}
.read {{ max-width: 640px; }}

/* transport bar */
.transport {{
  position: sticky; top: env(safe-area-inset-top, 0px); z-index: 20;
  background: color-mix(in srgb, var(--bg) 88%, transparent); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--line);
}}
.transport .wrap {{ display: flex; align-items: center; gap: 18px; height: 52px; }}
.brand {{ font-family: var(--display); font-weight: 600; font-size: 15px; letter-spacing: 0.2em; white-space: nowrap; }}
.track {{ position: relative; flex: 1; height: 2px; background: var(--line); min-width: 0; }}
.track .played {{ position: absolute; inset: 0 auto 0 0; width: 0; background: var(--accent); }}
.track .head {{ position: absolute; top: 50%; left: 0; width: 10px; height: 10px; margin: -5px 0 0 -5px; border-radius: 50%; background: var(--accent); }}
.track .marker {{ position: absolute; top: -4px; width: 1px; height: 10px; background: var(--fg2); opacity: 0.5; }}
.now {{ font-family: var(--mono); font-size: 12px; color: var(--fg2); white-space: nowrap; min-width: 9.5em; text-align: right; text-transform: uppercase; letter-spacing: 0.08em; }}

/* hero */
.hero {{ position: relative; overflow: hidden; }}
.hero canvas {{ position: absolute; inset: 0; width: 100%; height: 100%; display: block; }}
.hero .wrap {{ position: relative; padding-block: clamp(56px, 9vw, 120px) clamp(48px, 6vw, 80px); display: grid; gap: 30px; }}
.eyebrow {{ font-family: var(--mono); font-size: 12px; letter-spacing: 0.16em; text-transform: uppercase; color: var(--fg2); margin: 0; display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }}
.eyebrow b {{ font-weight: 500; color: var(--accent); }}
h1 {{
  font-family: var(--display); font-weight: 600; text-transform: uppercase; margin: 0;
  font-size: clamp(52px, 10.5vw, 148px); line-height: 0.9; letter-spacing: -0.005em; text-wrap: balance; max-width: 11ch;
}}
h1 em {{ font-style: normal; color: var(--accent); }}
.lede {{ font-size: clamp(18px, 2vw, 21px); color: var(--fg2); margin: 0; max-width: 34em; }}
.hero-figs {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); border-top: 1px solid var(--fg); margin-top: 12px; }}
.hero-fig {{ padding: 18px 20px 0 0; display: grid; gap: 4px; align-content: start; }}
.hero-fig + .hero-fig {{ padding-left: 20px; border-left: 1px solid var(--line); }}
.hero-fig b {{ font-family: var(--display); font-weight: 600; font-size: clamp(40px, 5.4vw, 72px); line-height: 1; font-variant-numeric: tabular-nums; }}
.hero-fig span {{ font-size: 14px; color: var(--fg2); line-height: 1.45; }}
.byline {{ display: flex; flex-wrap: wrap; gap: 8px 22px; font-family: var(--mono); font-size: 13px; color: var(--fg2); margin: 0; }}

/* sections */
.sec {{ border-top: 1px solid var(--line); }}
.sec > .wrap {{ padding-block: clamp(64px, 8vw, 112px); display: grid; gap: 26px; }}
.label {{ font-family: var(--mono); font-size: 12px; letter-spacing: 0.16em; text-transform: uppercase; color: var(--fg2); margin: 0; display: flex; gap: 14px; align-items: center; }}
.label .tc {{ color: var(--accent); }}
h2 {{ font-family: var(--display); font-weight: 600; text-transform: uppercase; font-size: clamp(36px, 6vw, 76px); line-height: 0.95; margin: 0; text-wrap: balance; max-width: 16ch; }}
h3 {{ font-size: clamp(20px, 2.2vw, 24px); line-height: 1.3; font-weight: 600; margin: 0; text-wrap: balance; }}
p {{ margin: 0; }}
.muted {{ color: var(--fg2); }}
.small {{ font-size: 15px; }}

.split {{ display: grid; grid-template-columns: minmax(0, 5fr) minmax(0, 7fr); gap: 40px 64px; align-items: start; }}
.facts {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0; border-top: 1px solid var(--line); }}
.fact {{ padding: 20px 0; border-bottom: 1px solid var(--line); display: grid; gap: 4px; }}
.fact:nth-child(odd) {{ padding-right: 20px; }}
.fact:nth-child(even) {{ padding-left: 20px; border-left: 1px solid var(--line); }}
.fact b {{ font-family: var(--display); font-weight: 600; font-size: 40px; line-height: 1; }}
.fact span {{ font-size: 14px; color: var(--fg2); }}

.proud-grid {{ display: grid; grid-template-columns: minmax(0, 5fr) minmax(0, 7fr); gap: 40px 72px; align-items: center; }}
.record-wrap {{ display: grid; place-items: center; }}
.record {{
  width: 100%; max-width: 400px; aspect-ratio: 1; border-radius: 50%; position: relative; display: grid; place-items: center;
  box-shadow: 0 30px 60px -30px rgba(40,30,0,.55), inset 0 0 0 1px rgba(90,65,10,.35);
}}
.record .spin {{
  position: absolute; inset: 0; border-radius: 50%;
  background:
    repeating-radial-gradient(circle, rgba(0,0,0,.10) 0 1px, transparent 1px 4px),
    conic-gradient(from 20deg, #F3DC93, #B8882F, #F7E7AE, #9C7224, #EED38A, #B8882F, #F3DC93);
}}
.record::before {{ content: ""; position: absolute; inset: 0; border-radius: 50%; z-index: 1;
  background: radial-gradient(circle at 32% 26%, rgba(255,250,225,.5), transparent 40%); }}
.record-label {{
  width: 36%; aspect-ratio: 1; border-radius: 50%; background: #2B45D4; color: #fff; position: relative; z-index: 2;
  display: grid; place-content: center; text-align: center; gap: 4px;
}}
.record-label span {{ font-family: var(--mono); font-size: clamp(9px, 1vw, 11px); letter-spacing: .2em; text-transform: uppercase; opacity: .85; }}
.record-label b {{ font-family: var(--display); font-weight: 600; font-size: clamp(20px, 2.4vw, 32px); line-height: 1; }}
@media (prefers-reduced-motion: no-preference) {{ .record .spin {{ animation: spin 18s linear infinite; }} }}
@keyframes spin {{ to {{ transform: rotate(360deg); }} }}
.proud-copy {{ display: grid; gap: 24px; min-width: 0; }}
.honours {{ list-style: none; margin: 0; padding: 0; display: grid; border-top: 1px solid var(--fg); }}
.honours li {{ display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr); gap: 16px; align-items: baseline; padding: 16px 0; border-bottom: 1px solid var(--line); }}
.honours b {{ font-family: var(--display); font-weight: 600; text-transform: uppercase; font-size: clamp(30px, 3.6vw, 50px); line-height: 1; white-space: nowrap; }}
.honours span {{ font-size: 15px; color: var(--fg2); line-height: 1.4; }}
.gold-text {{ background: linear-gradient(100deg, #9C7224, #D9AE4F 40%, #B8882F 70%, #8A6420); -webkit-background-clip: text; background-clip: text; color: transparent; }}
@media (max-width: 860px) {{
  .proud-grid {{ grid-template-columns: minmax(0, 1fr); }}
  .record {{ max-width: 260px; }}
}}
@media (max-width: 480px) {{
  .honours li {{ grid-template-columns: minmax(0, 1fr); gap: 4px; }}
}}
.glance {{ background: var(--surface); border-top: 1px solid var(--line); }}
.glance .wrap {{ padding-block: 40px; display: grid; gap: 18px; }}
.glance-grid {{ margin: 0; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 22px 32px; }}
.glance-grid div {{ display: grid; gap: 6px; align-content: start; padding-top: 14px; border-top: 1px solid var(--line); min-width: 0; }}
.glance-grid dt {{ font-family: var(--mono); font-size: 11px; letter-spacing: .16em; text-transform: uppercase; color: var(--accent); }}
.glance-grid dd {{ margin: 0; font-size: 15px; line-height: 1.5; }}
.model {{ padding: clamp(24px, 4vw, 36px); background: var(--surface); }}
.schema {{ display: grid; grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr) auto minmax(0, 1fr); align-items: center; gap: 0; min-width: 0; }}
.tbl {{ background: var(--bg); border: 1px solid var(--line); display: grid; font-family: var(--mono); font-size: 12px; min-width: 0; }}
.tbl b {{ font-weight: 500; padding: 8px 10px; border-bottom: 1px solid var(--line); background: var(--fg); color: var(--bg); }}
.tbl span {{ padding: 5px 10px; color: var(--fg2); overflow-wrap: anywhere; }}
.tbl span.key {{ color: var(--accent); }}
.tbl-stack {{ display: grid; gap: 12px; min-width: 0; }}
.join {{ position: relative; width: 100px; height: 1px; background: var(--accent); }}
.join span {{ position: absolute; left: 50%; bottom: 6px; transform: translateX(-50%); font-family: var(--mono); font-size: 10px; color: var(--accent); white-space: nowrap; }}
.decisions {{ list-style: none; margin: 0; padding: 0; display: grid; border-top: 1px solid var(--line); }}
.decisions li {{ padding: 14px 0; border-bottom: 1px solid var(--line); font-size: 15px; color: var(--fg2); }}
.decisions b {{ color: var(--fg); font-weight: 600; }}
code {{ font-family: var(--mono); font-size: .9em; }}
.sig {{ justify-self: start; font-family: var(--mono); font-size: 12px; color: var(--accent); border: 1px solid var(--accent); padding: 4px 10px; }}
@media (max-width: 960px) {{
  .schema {{ grid-template-columns: minmax(0, 1fr); justify-items: stretch; }}
  .join {{ width: 1px; height: 36px; justify-self: center; }}
  .join span {{ left: 10px; bottom: 50%; transform: translateY(50%); }}
}}
@media (max-width: 860px) {{ .glance-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
@media (max-width: 560px) {{ .glance-grid {{ grid-template-columns: minmax(0, 1fr); }} }}
.questions {{ list-style: none; margin: 0; padding: 0; display: grid; gap: 0; counter-reset: q; }}
.questions li {{ counter-increment: q; display: grid; grid-template-columns: 56px minmax(0, 1fr); padding: 18px 0; border-top: 1px solid var(--line); font-size: clamp(19px, 2vw, 23px); line-height: 1.35; }}
.questions li:last-child {{ border-bottom: 1px solid var(--line); }}
.questions li::before {{ content: "Q" counter(q); font-family: var(--mono); font-size: 13px; color: var(--accent); padding-top: 6px; }}

.steps {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0; border-top: 1px solid var(--line); }}
.step {{ padding: 22px 0; border-bottom: 1px solid var(--line); display: grid; gap: 8px; align-content: start; }}
.step:nth-child(odd) {{ padding-right: 28px; }}
.step:nth-child(even) {{ padding-left: 28px; border-left: 1px solid var(--line); }}
.step .k {{ font-family: var(--mono); font-size: 12px; letter-spacing: 0.12em; text-transform: uppercase; color: var(--fg2); }}
.step p + p {{ color: var(--fg2); font-size: 15px; }}

.callout {{ position: relative; padding: clamp(24px, 4vw, 40px); background: var(--fg); color: var(--bg); display: grid; gap: 14px; }}
.callout .k {{ font-family: var(--mono); font-size: 12px; letter-spacing: 0.16em; text-transform: uppercase; color: var(--bg); opacity: 0.7; }}
.callout h3 {{ font-family: var(--display); font-weight: 600; text-transform: uppercase; font-size: clamp(28px, 4vw, 44px); line-height: 1; }}
.callout .clock {{ display: flex; gap: 10px; flex-wrap: wrap; font-family: var(--mono); font-size: 14px; }}
.callout .clock span {{ border: 1px solid color-mix(in srgb, var(--bg) 40%, transparent); padding: 4px 10px; }}

/* studio band: the findings */
.studio {{ background: var(--studio); color: var(--studio-fg); --fg2: var(--studio-fg2); --line: var(--studio-line); --accent: var(--studio-accent); --surface: var(--studio-2); }}
.studio .sec-head {{ display: grid; gap: 20px; padding-block: clamp(72px, 9vw, 120px) 8px; }}
.finding {{ display: grid; grid-template-columns: minmax(0, 5fr) minmax(0, 7fr); gap: 32px 64px; padding-block: clamp(48px, 6vw, 80px); border-top: 1px solid var(--line); align-items: start; }}
.finding:last-child {{ padding-bottom: clamp(72px, 9vw, 120px); }}
.finding .left {{ display: grid; gap: 16px; position: sticky; top: 84px; }}
.finding .num {{ font-family: var(--display); font-weight: 600; font-size: clamp(64px, 9vw, 128px); line-height: 0.88; color: var(--accent); font-variant-numeric: tabular-nums; }}
.finding .right {{ display: grid; gap: 18px; min-width: 0; }}
.cap {{ font-size: 15px; color: var(--fg2); max-width: 36em; }}

.dotgrid {{ display: grid; grid-template-columns: repeat(31, minmax(0, 1fr)); gap: 5px; max-width: 560px; }}
.dotgrid i {{ aspect-ratio: 1; background: var(--surface); border-radius: 2px; }}
.dotgrid i.on {{ background: var(--accent); box-shadow: 0 0 0 4px color-mix(in srgb, var(--accent) 25%, transparent); }}
@media (prefers-reduced-motion: no-preference) {{ .dotgrid i.on {{ animation: pulse 1.8s ease-in-out infinite; }} }}
@keyframes pulse {{ 50% {{ box-shadow: 0 0 0 9px color-mix(in srgb, var(--accent) 0%, transparent); }} }}

.timeline {{ display: grid; gap: 10px; padding-top: 30px; }}
.lane {{ position: relative; height: 240px; border-bottom: 1px solid var(--line);
  background-image: linear-gradient(to right, var(--line) 1px, transparent 1px); background-size: 12.5% 100%; }}
.clip {{ position: absolute; z-index: 1; bottom: 0; height: var(--h); padding: 2px; transition: height .9s cubic-bezier(.2,.8,.2,1); }}
.clip::before {{ content: ""; position: absolute; inset: 0 2px 0 2px; background: color-mix(in srgb, var(--studio-fg) 16%, transparent); border-top: 2px solid var(--studio-fg); }}
.clip.late::before {{ background: color-mix(in srgb, var(--accent) 30%, transparent); border-top-color: var(--accent); }}
.clip-val {{ position: absolute; top: -30px; left: 6px; font-family: var(--mono); font-size: 14px; font-weight: 500; }}
.clip-name {{ position: absolute; bottom: 6px; left: 8px; right: 4px; font-family: var(--mono); font-size: 11px; color: var(--fg2); line-height: 1.2; }}
.median {{ position: absolute; top: 0; bottom: -6px; width: 0; border-left: 1px dashed var(--studio-fg); }}
.median span {{ position: absolute; top: 4px; right: 8px; font-family: var(--mono); font-size: 12px; white-space: nowrap; color: var(--studio-fg); }}
.ruler {{ position: relative; height: 18px; font-family: var(--mono); font-size: 11px; color: var(--fg2); }}
.tick {{ position: absolute; transform: translateX(-50%); white-space: nowrap; }}
.tick:first-child {{ transform: none; }}
.tick:last-child {{ transform: translateX(-100%); }}

.pair {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 28px; max-width: 560px; }}
.pair figure {{ margin: 0; display: grid; gap: 12px; }}
.pair figcaption {{ display: flex; justify-content: space-between; gap: 8px; font-family: var(--mono); font-size: 13px; }}
.pair figcaption b {{ font-weight: 500; }}
.hundred {{ display: grid; grid-template-columns: repeat(10, minmax(0, 1fr)); gap: 4px; }}
.hundred i {{ aspect-ratio: 1; background: var(--surface); border-radius: 1px; }}
.hundred i.on {{ background: var(--accent); }}
.pair .dim .hundred i.on {{ background: var(--studio-fg); }}

.ratio-rows {{ display: grid; gap: 22px; max-width: 600px; }}
.ratio-row {{ display: grid; gap: 10px; }}
.ratio-row header {{ display: flex; justify-content: space-between; font-family: var(--mono); font-size: 13px; color: var(--fg2); }}
.ratio-row header b {{ color: var(--studio-fg); font-weight: 500; }}
.ratio-row .dotgrid.r20 {{ grid-template-columns: repeat(20, minmax(0, 1fr)); max-width: none; }}
.ratio-row .dotgrid.r5 {{ grid-template-columns: repeat(20, minmax(0, 1fr)); max-width: none; }}
.r5 i:nth-child(n+6) {{ display: none; }}

/* bars */
.bars {{ display: grid; gap: 10px; }}
.bar-row {{ display: grid; grid-template-columns: 6.5em minmax(0, 1fr) 3em; gap: 12px; align-items: center; font-family: var(--mono); font-size: 13px; }}
.bar-label {{ color: var(--fg2); }}
.bar-val {{ text-align: right; font-weight: 500; }}
.bar {{ height: 14px; background: var(--surface); position: relative; overflow: hidden; }}
.bar .fill {{ position: absolute; inset: 0 auto 0 0; width: var(--v); background: var(--fg); transition: width .9s cubic-bezier(.2,.8,.2,1); }}
.bar .fill.accent {{ background: var(--accent); }}
.bar.stack {{ background: color-mix(in srgb, var(--fg) 14%, transparent); }}

/* motion: everything is drawn at rest; JS only replays the growth when a chart scrolls into view */
.js-anim [data-grow]:not(.in) .clip {{ height: 0; }}
.js-anim [data-grow]:not(.in) .fill {{ width: 0; }}

/* recommendations */
.recs {{ list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0; border-top: 1px solid var(--fg); counter-reset: r; }}
.recs li {{ counter-increment: r; padding: 24px 24px 0 0; display: grid; gap: 10px; align-content: start; }}
.recs li + li {{ padding-left: 24px; border-left: 1px solid var(--line); }}
.recs li::before {{ content: "0" counter(r); font-family: var(--display); font-weight: 600; font-size: 44px; line-height: 1; color: var(--accent); }}
.recs p {{ color: var(--fg2); font-size: 16px; }}

.more {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0; border-top: 1px solid var(--line); }}
.more > div {{ padding: 28px 0; border-bottom: 1px solid var(--line); display: grid; gap: 14px; align-content: start; min-width: 0; }}
.more > div:nth-child(odd) {{ padding-right: 32px; }}
.more > div:nth-child(even) {{ padding-left: 32px; border-left: 1px solid var(--line); }}
.big {{ font-family: var(--display); font-weight: 600; font-size: 64px; line-height: 0.9; color: var(--accent); }}

.limits {{ margin: 0; padding: 0; list-style: none; display: grid; gap: 0; }}
.limits li {{ padding: 16px 0; border-top: 1px solid var(--line); display: grid; gap: 4px; }}
.limits li b {{ font-weight: 600; }}

/* sql */
details.query {{ max-width: 100%; }}
details.query summary {{ cursor: pointer; list-style: none; display: inline-flex; align-items: center; gap: 10px; font-family: var(--mono); font-size: 13px; color: var(--fg2); padding: 4px 0; }}
details.query summary::-webkit-details-marker {{ display: none; }}
.q-icon {{ width: 18px; height: 18px; border: 1px solid currentColor; position: relative; }}
.q-icon::before, .q-icon::after {{ content: ""; position: absolute; left: 4px; right: 4px; top: 50%; height: 1px; background: currentColor; }}
.q-icon::after {{ transform: rotate(90deg); transition: transform .2s; }}
details[open] .q-icon::after {{ transform: rotate(0deg); }}
details.query summary:hover {{ color: var(--accent); }}
pre {{ margin: 12px 0 0; padding: 20px; background: var(--studio-2); color: var(--studio-fg); overflow-x: auto; font-family: var(--mono); font-size: 12.5px; line-height: 1.65; border-left: 2px solid var(--accent); }}
.sec pre {{ background: var(--studio); }}
.sql-file {{ color: var(--studio-accent); }}

footer {{ background: var(--studio); color: var(--studio-fg); --fg2: var(--studio-fg2); --line: var(--studio-line); }}
footer .wrap {{ padding-block: 72px max(72px, env(safe-area-inset-bottom, 0px)); display: grid; gap: 22px; }}
footer .sign {{ font-family: var(--display); font-weight: 600; font-size: clamp(40px, 7vw, 96px); line-height: 0.9; text-transform: uppercase; }}
footer .links {{ display: flex; flex-wrap: wrap; gap: 12px 28px; font-family: var(--mono); font-size: 14px; }}

@media (max-width: 860px) {{
  .split, .finding {{ grid-template-columns: minmax(0, 1fr); }}
  .finding .left {{ position: static; }}
  .recs {{ grid-template-columns: minmax(0, 1fr); }}
  .recs li, .recs li + li {{ padding: 22px 0; border-left: 0; border-bottom: 1px solid var(--line); }}
}}
@media (max-width: 640px) {{
  body {{ font-size: 16px; }}
  .hero-figs {{ grid-template-columns: minmax(0, 1fr); }}
  .hero-fig, .hero-fig + .hero-fig {{ padding: 16px 0; border-left: 0; }}
  .hero-fig + .hero-fig {{ border-top: 1px solid var(--line); }}
  .steps, .more {{ grid-template-columns: minmax(0, 1fr); }}
  .step:nth-child(n), .more > div:nth-child(n) {{ padding-left: 0; padding-right: 0; border-left: 0; }}
  .now {{ display: none; }}
  .brand {{ font-size: 13px; }}
  .lane {{ height: 200px; }}
  .clip-name {{ display: none; }}
  .dotgrid {{ gap: 3px; }}
  .pair {{ gap: 18px; }}
}}
</style>

<nav class="transport" aria-label="Progress">
  <div class="wrap">
    <span class="brand">NIKITA KOTADIA</span>
    <div class="track" id="track" aria-hidden="true"><span class="played" id="played"></span><span class="head" id="head"></span></div>
    <span class="now" id="now">Intro</span>
  </div>
</nav>

<header class="hero" id="intro" data-name="Intro">
  <canvas id="wave" aria-hidden="true"></canvas>
  <div class="wrap">
    <p class="eyebrow"><b>Case study</b><span>SQL · Python · my own business data</span></p>
    <h1>Do free downloads turn into <em>customers?</em></h1>
    <p class="lede">I've run a music production business since 2018, licensing my instrumentals to artists online. Like most producers, I give some away as free downloads to build an email list. I joined my sales and email data to find out whether that actually works.</p>
    <div class="hero-figs">
      <div class="hero-fig"><b>1 in {one_in}</b><span>free downloaders became a paying customer</span></div>
      <div class="hero-fig"><b>{median_days} days</b><span>median wait between download and first purchase</span></div>
      <div class="hero-fig"><b>{ratio}×</b><span>as likely to buy again when on the email list</span></div>
    </div>
    <p class="byline"><span>Nikita Kotadia · Data Analyst · MSc Data Science</span><a href="{LINKEDIN}">LinkedIn</a><a href="{GITHUB}">Code on GitHub</a></p>
  </div>
</header>

<section class="glance" id="summary" data-name="Summary" aria-label="At a glance">
  <div class="wrap">
    <p class="label">At a glance</p>
    <dl class="glance-grid">
      <div><dt>Question</dt><dd>Do free downloads turn into paying customers, and how long does it take?</dd></div>
      <div><dt>Data</dt><dd>My own sales and email list exports, January 2020 to September 2026</dd></div>
      <div><dt>Method</dt><dd>Cleaned and pseudonymised in Python, analysed in SQL, comparisons tested with Fisher's exact test</dd></div>
      <div><dt>Answer</dt><dd>1 in {one_in} free downloaders buy, after a median of {median_days} days. Buyers on the list are {ratio}× as likely to buy again ({tests["repeat"]}).</dd></div>
      <div><dt>Recommendation</dt><dd>Follow up for a year, send new releases to past buyers first, and prove it with a holdout test</dd></div>
      <div><dt>Tools</dt><dd>Python · pandas · SQLite · SQL (CTEs, window functions, views) · SciPy</dd></div>
    </dl>
  </div>
</section>

<main>
<section class="sec proud" id="business" data-name="The business">
  <div class="wrap" style="gap:48px">
    <p class="label"><span class="tc">01</span>The business</p>
    <div class="proud-grid">
      <div class="record-wrap" aria-hidden="true">
        <div class="record"><div class="spin"></div><div class="record-label"><span>Since</span><b>2018</b></div></div>
      </div>
      <div class="proud-copy">
        <h2>Eight years of producing and licensing music</h2>
        <p class="read">I've produced music since 2018 and license my instrumentals online, through a public marketplace and my own storefront. I run the whole business myself: production, pricing, licence terms, delivery and promotion.</p>
        <ul class="honours">
          <li><b class="gold-text">Gold-certified</b><span>production credits</span></li>
          <li><b>UK-charting</b><span>records I've produced on</span></li>
          <li><b>UK + US</b><span>credits with internationally known artists</span></li>
          <li><b>Independent</b><span>built and run entirely by me</span></li>
        </ul>
      </div>
    </div>
    <p class="read small muted">Sales peaked in 2022 and have slowed since, which turns out to be useful here: it shows whether the email list keeps producing buyers when sales are quiet. To keep the business private, this page shows rates, shares and medians only. No customer, order or subscriber numbers, and no revenue.</p>
  </div>
</section>

<section class="sec" id="question" data-name="The question">
  <div class="wrap split">
    <div style="display:grid;gap:22px">
      <p class="label"><span class="tc">02</span>The question</p>
      <h2>Is a free download worth giving away?</h2>
    </div>
    <div style="display:grid;gap:26px">
      <p class="read">Every free download is a track someone didn't pay for. In return, the downloader is added to my email list automatically. The trade only makes sense if some of them come back and buy.</p>
      <ol class="questions">
        <li>What share of free downloaders become paying customers?</li>
        <li>How long do they take to buy?</li>
        <li>Are buyers who stay on the list worth more than buyers who don't?</li>
      </ol>
    </div>
  </div>
</section>

<section class="sec" id="data" data-name="The data">
  <div class="wrap" style="gap:40px">
    <div class="split">
      <div style="display:grid;gap:22px">
        <p class="label"><span class="tc">03</span>The data</p>
        <h2>Two messy exports</h2>
      </div>
      <p class="read">An export of every order from January 2020 to September 2026, and an export of my current email list. I cleaned both in Python with pandas, loaded them into SQLite, and answered every question in SQL.</p>
    </div>
    <div class="steps">
      <div class="step"><span class="k">Block layout</span><p>Each order came out as a block of rows: the order, then a row per extra track and per collaborator's share.</p><p>Parsed line by line into orders, items and payment splits.</p></div>
      <div class="step"><span class="k">Broken columns</span><p>Track titles containing commas had spilled into the next column.</p><p>Detected by field count and rejoined.</p></div>
      <div class="step"><span class="k">Revenue splits</span><p>Most sales are split with collaborators, so the sale price isn't what I earned.</p><p>Kept every party's share separately and anonymised every collaborator.</p></div>
      <div class="step"><span class="k">Free checkouts</span><p>Some items went through checkout at a price of zero.</p><p>Flagged so they never count as purchases.</p></div>
    </div>
    <div class="callout">
      <span class="k">The detail that changed the answer</span>
      <h3>Two systems, two clocks</h3>
      <div class="clock" aria-hidden="true"><span>+4:00 EDT</span><span>+5:00 EST</span></div>
      <p class="read">When I first joined the files, most buyers seemed to subscribe exactly four or five hours before buying. That's the gap between US Eastern time and UTC: the email platform appears to record Eastern time without labelling it. With the clocks aligned, those buyers had joined the list at checkout, seconds before paying. Without the fix they'd have counted as free downloaders who converted, and the headline result would have been several times too high.</p>
    </div>
    <div class="model">
      <div class="split">
        <div style="display:grid;gap:14px">
          <h3>The data model</h3>
          <p class="small muted">Four tables. Emails become a hashed <code>customer_id</code>, which is the only link between sales and the email list.</p>
        </div>
        <div class="schema" role="img" aria-label="subscribers joins orders on customer_id; orders joins order_items and payment_splits on order_id">
          <div class="tbl"><b>subscribers</b><span class="key">customer_id</span><span>optin_time_utc</span><span>source</span><span>tag_free_download</span></div>
          <div class="join"><span>customer_id</span></div>
          <div class="tbl"><b>orders</b><span class="key">order_id</span><span class="key">customer_id</span><span>order_time_utc</span><span>channel, status</span></div>
          <div class="join"><span>order_id</span></div>
          <div class="tbl-stack">
            <div class="tbl"><b>order_items</b><span class="key">order_id</span><span>track_title</span><span>list_price, sale_price</span></div>
            <div class="tbl"><b>payment_splits</b><span class="key">order_id</span><span>party</span><span>split_amount</span></div>
          </div>
        </div>
      </div>
    </div>
    <div class="split">
      <h3>Decisions behind the numbers</h3>
      <ul class="decisions">
        <li><b>The one-hour rule.</b> Buyers are added to the list at checkout, so a conversion only counts when the first purchase comes more than an hour after joining.</li>
        <li><b>Medians over averages.</b> A few buyers took most of a year, which would drag an average. The median shows the typical wait.</li>
        <li><b>Imported contacts left out of timing.</b> Their join date is the day I uploaded them, so it says nothing about when they found me.</li>
        <li><b>Fisher's exact test for comparisons.</b> The groups are small and repeat purchases are rare, which is where this test is reliable.</li>
        <li><b>Privacy by design.</b> Every query returns a rate, share, median or index. Small groups are grouped or rounded so no total can be worked out.</li>
      </ul>
    </div>
    <p class="read small muted">Privacy: customer emails are replaced with salted one-way hashes, so the files can be joined without anyone being identifiable. The data stays on my computer, and shares based on small groups are rounded so the numbers behind them can't be worked out.</p>
  </div>
</section>

<section class="studio" id="findings" data-name="Findings">
  <div class="wrap">
    <div class="sec-head">
      <p class="label"><span class="tc">04</span>What the data shows</p>
      <h2>Four findings</h2>
    </div>

    <article class="finding">
      <div class="left">
        <span class="num">1 in {one_in}</span>
        <h3>About {pct(conv_pct, 1)} of people who downloaded a free track later bought one.</h3>
        <p class="cap">A conversion counts only when the first paid purchase came more than an hour after joining the list. Inside the hour, the person joined by buying.</p>
      </div>
      <div class="right">
        {dot_grid(one_in, 1)}
        <p class="cap">Each square is one free downloader. One in every {one_in} came back and paid.</p>
        {sql_block("00_views.sql", "01_free_download_conversion.sql")}
      </div>
    </article>

    <article class="finding">
      <div class="left">
        <span class="num">{median_days} days</span>
        <h3>Most people who converted took more than a month to buy.</h3>
        <p class="cap">About {pct(within_week)} bought within a week. {pct(after_month)} took more than a month, and {pct(after_3m)} took between three months and a year.</p>
      </div>
      <div class="right">
        <p class="label">Time from free download to first purchase · rounded to 5%</p>
        <div data-grow>{timeline}</div>
        {sql_block("02_time_to_convert.sql", "02b_median_days.sql")}
      </div>
    </article>

    <article class="finding">
      <div class="left">
        <span class="num">{ratio}×</span>
        <h3>Buyers on the list are five times as likely to buy again.</h3>
        <span class="sig">Fisher's exact test · {tests["repeat"]}</span>
        <p class="cap">The gap is very unlikely to be chance, but it's still a correlation: buyers who unsubscribed drop out of the list, and they were probably less likely to return anyway.</p>
      </div>
      <div class="right">
        <p class="label">Out of every 100 buyers, how many bought again · since May 2021</p>
        <div class="pair">
          <figure>{hundred(on, f"{on}% of buyers on the list bought again")}<figcaption><span>On the list</span><b>{pct(on, 1)}</b></figcaption></figure>
          <figure class="dim">{hundred(off, f"{off}% of buyers not on the list bought again")}<figcaption><span>Not on the list</span><b>{pct(off, 1)}</b></figcaption></figure>
        </div>
        {sql_block("03_repeat_rate_by_path.sql")}
      </div>
    </article>

    <article class="finding">
      <div class="left">
        <span class="num">1 in 20<br>→ 1 in 5</span>
        <h3>As sales slowed, more new buyers came through the list.</h3>
        <p class="cap">The share of new buyers who joined the list before buying went from about {pct(early)} in the peak years to about {pct(recent)} since 2024. Because of the 2025 sync gap (see Limits), the recent figure is, if anything, low.</p>
        <span class="sig">Fisher's exact test · {tests["list_share"]}</span>
      </div>
      <div class="right">
        <p class="label">New buyers who joined the list first</p>
        <div class="ratio-rows">
          <div class="ratio-row"><header><span>2021 to 2023</span><b>1 in 20</b></header>{dot_grid(20, 1, "r20")}</div>
          <div class="ratio-row"><header><span>2024 to 2026</span><b>1 in 5</b></header>{dot_grid(20, 1, "r5")}</div>
        </div>
        {sql_block("04_list_share_by_period.sql")}
      </div>
    </article>
  </div>
</section>

<section class="sec" id="change" data-name="What I'd change">
  <div class="wrap" style="gap:40px">
    <div class="split">
      <div style="display:grid;gap:22px">
        <p class="label"><span class="tc">05</span>What I'd change</p>
        <h2>Follow up for months</h2>
      </div>
      <p class="read">The list works, but slowly. Most of the value arrives long after a welcome email would have been forgotten.</p>
    </div>
    <ol class="recs">
      <li><h3>Email free downloaders for a year</h3><p>About {pct(100 - within_week)} of conversions came after the first week. Emails at one week, one month, three months and six months match when people actually buy. If they turned one more downloader in every 200 into a customer, the list would bring in about {lift:.0f}% more new customers.</p></li>
      <li><h3>Send new releases to past buyers first</h3><p>Buyers on the list are five times as likely to buy again, and buyers are added to it at checkout. They're the warmest audience I have.</p></li>
      <li><h3>Fix the sync, then test it</h3><p>Check the connection between the store and the email list so no sign-ups are lost again. Then send the follow-ups to a random half of new downloaders and compare. At a {pct(conv_pct, 1)} baseline, track opens and clicks early and judge purchases after six months.</p></li>
    </ol>
  </div>
</section>

<section class="sec" id="more" data-name="Other findings">
  <div class="wrap" style="gap:36px">
    <div style="display:grid;gap:22px">
      <p class="label"><span class="tc">06</span>Other findings</p>
      <h2>Pricing, channels, catalogue</h2>
    </div>
    <div class="more">
      <div>
        <h3>Most sales are entry-level leases</h3>
        <div class="bars" data-grow>{price_rows}</div>
        <p class="small muted">{pct(bands[0]["pct_of_items"])} of of licences sold were listed under $35. Licences at $100 and over make up {pct(bands[3]["pct_of_items"])}.</p>
        {sql_block("07_price_tiers.sql")}
      </div>
      <div>
        <h3>The marketplace took over from my own storefront</h3>
        <div class="bars" data-grow>{mix_rows}</div>
        <p class="small muted">My own storefront's share of paid orders peaked at {[r for r in mix if r["period"] == "2021"][0]["own_storefront_pct"]:.0f}% in 2021. Since 2024, most orders have come through the public marketplace.</p>
        {sql_block("06_channel_mix_by_year.sql")}
      </div>
      <div>
        <h3>A few tracks carry the catalogue</h3>
        <p class="big">{cat["top_10_pct"]:.0f}%</p>
        <p class="small muted">of paid sales came from my top 10 tracks. The best seller alone accounts for {cat["top_track_pct"]:.0f}%, and {cat["sold_once_pct"]:.0f}% of the tracks that sold were bought only once.</p>
        {sql_block("08_catalogue_concentration.sql")}
      </div>
      <div>
        <h3>Most of the catalogue is collaborative</h3>
        <p class="big">{co_pct:.0f}%</p>
        <p class="small muted">of tracks sold were co-produced with other producers. Every split is recorded in the payment data.</p>
        {sql_block("09_collaboration.sql")}
      </div>
    </div>
  </div>
</section>

<section class="sec" id="limits" data-name="Limits">
  <div class="wrap split">
    <div style="display:grid;gap:22px">
      <p class="label"><span class="tc">07</span>Limits</p>
      <h2>What the data can't tell me</h2>
    </div>
    <ul class="limits">
      <li><b>A gap in 2025.</b><span class="muted">Almost nobody joined the list during 2025, against steady sign-ups every other year, and sign-ups pick up again in 2026. The most likely cause is that the automatic sync between my store and the email list stopped for most of that year, so people from that period are missing from the list.</span></li>
      <li><b>Current subscribers only.</b><span class="muted">Anyone who bought and then unsubscribed counts as never having been on the list.</span></li>
      <li><b>One download per person.</b><span class="muted">A free download is visible only through its tag and the date the person first joined. Later downloads aren't recorded.</span></li>
      <li><b>Imported contacts.</b><span class="muted">Contacts imported from a spreadsheet in 2021 have their upload date as their join date, so they're left out of the timing and repeat questions.</span></li>
      <li><b>Correlation, not cause.</b><span class="muted">Recent years are small. The test in recommendation 3 is how I'd find out what causes what.</span></li>
    </ul>
  </div>
</section>
</main>

<footer>
  <div class="wrap">
    <p class="label">Method</p>
    <p class="sign">Nikita Kotadia</p>
    <p class="read muted">Data analyst. Python and pandas for cleaning, SQLite for analysis. Every query on this page is in the repository, with the notebooks that run them.</p>
    <p class="links"><a href="{GITHUB}">GitHub repository</a><a href="{LINKEDIN}">LinkedIn</a></p>
  </div>
</footer>

<script>
(() => {{
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Playhead: scroll progress with a marker per section
  const track = document.getElementById("track"), played = document.getElementById("played"),
        head = document.getElementById("head"), now = document.getElementById("now");
  const sections = [...document.querySelectorAll("[data-name]")];
  const docH = () => document.documentElement.scrollHeight - innerHeight;
  function markers() {{
    track.querySelectorAll(".marker").forEach(m => m.remove());
    sections.forEach(s => {{
      const m = document.createElement("span");
      m.className = "marker";
      m.style.left = Math.min(100, s.offsetTop / Math.max(1, docH()) * 100) + "%";
      track.appendChild(m);
    }});
  }}
  function tick() {{
    const p = Math.min(1, Math.max(0, scrollY / Math.max(1, docH())));
    played.style.width = p * 100 + "%";
    head.style.left = p * 100 + "%";
    let cur = sections[0];
    for (const s of sections) if (s.getBoundingClientRect().top < innerHeight * 0.35) cur = s;
    now.textContent = cur.dataset.name;
  }}
  addEventListener("scroll", tick, {{ passive: true }});
  addEventListener("resize", () => {{ markers(); tick(); }});
  addEventListener("load", () => {{ markers(); tick(); }});
  markers(); tick();

  // Hero waveform
  const cv = document.getElementById("wave"), ctx = cv.getContext("2d");
  let w = 0, h = 0, t = 0;
  function size() {{
    const r = cv.getBoundingClientRect(), d = devicePixelRatio || 1;
    w = r.width; h = r.height; cv.width = w * d; cv.height = h * d; ctx.setTransform(d, 0, 0, d, 0, 0);
  }}
  function draw() {{
    const css = getComputedStyle(document.documentElement);
    ctx.clearRect(0, 0, w, h);
    const lines = 9, base = h * 0.8;
    for (let i = 0; i < lines; i++) {{
      ctx.beginPath();
      ctx.strokeStyle = i === 4 ? css.getPropertyValue("--accent") : css.getPropertyValue("--line");
      ctx.globalAlpha = i === 4 ? 0.5 : 0.6;
      ctx.lineWidth = 1;
      for (let x = 0; x <= w; x += 6) {{
        const k = x / w;
        const env = Math.sin(Math.PI * k) * 0.9 + 0.1;
        const y = base + i * 9 + Math.sin(k * 7 + t + i * 0.35) * 26 * env + Math.sin(k * 17 - t * 1.3) * 7 * env;
        x ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
      }}
      ctx.stroke();
    }}
    ctx.globalAlpha = 1;
  }}
  size(); draw();
  addEventListener("resize", () => {{ size(); draw(); }});
  if (!reduce) {{
    let on = true;
    new IntersectionObserver(e => {{ on = e[0].isIntersecting; }}).observe(cv);
    (function loop() {{ if (on) {{ t += 0.012; draw(); }} requestAnimationFrame(loop); }})();
  }}

  // Charts grow when they scroll into view (they are fully drawn without JS)
  if (!reduce && "IntersectionObserver" in window) {{
    const els = [...document.querySelectorAll("[data-grow]")];
    const below = els.filter(el => el.getBoundingClientRect().top > innerHeight);
    below.forEach(el => el.classList.remove("in"));
    document.documentElement.classList.add("js-anim");
    els.filter(el => !below.includes(el)).forEach(el => el.classList.add("in"));
    const io = new IntersectionObserver(es => es.forEach(e => {{
      if (e.isIntersecting) {{ e.target.classList.add("in"); io.unobserve(e.target); }}
    }}), {{ threshold: 0.3 }});
    below.forEach(el => io.observe(el));
    setTimeout(() => els.forEach(el => el.classList.add("in")), 8000);
  }}
}})();
</script>
"""

head, body = page.split('<nav class="transport"', 1)
full = (
    '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n' + head
    + '</head>\n<body>\n<nav class="transport"' + body + '</body>\n</html>\n'
)
(SITE / "index.html").write_text(full)
print("Wrote", SITE / "index.html")
