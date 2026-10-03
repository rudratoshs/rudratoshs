#!/usr/bin/env python3
"""Render data.json into output/soc.svg -- an animated Security Operations
Center console. Pure stdlib; the SVG carries its own CSS animations, so it
animates when embedded in a README via <img>.
"""
import json
import os
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 920, 560

# palette
BG0, BG1, BG2 = "#070b10", "#0b121b", "#0e1726"
LINE = "#16212e"
TEXT, DIM, FAINT = "#9fb3c8", "#5a6e82", "#33475b"
GREEN, NEON = "#2ea043", "#00ff9c"
AMBER, RED, CYAN = "#ffb000", "#ff4d5e", "#35d6ed"

MONO = "ui-monospace,'SF Mono','DejaVu Sans Mono',Menlo,Consolas,monospace"


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def tcell(x, y, w, h, label, value, accent, sub=""):
    """A KPI tile: small label, big value, small sub -- stacked, no overlap."""
    return f"""
  <g transform="translate({x},{y})">
    <rect width="{w}" height="{h}" rx="6" fill="{BG2}" stroke="{LINE}"/>
    <rect width="3" height="{h}" rx="1.5" fill="{accent}"/>
    <text x="14" y="22" font-size="10" letter-spacing="1.2" fill="{DIM}">{esc(label)}</text>
    <text x="14" y="60" font-size="32" font-weight="700" fill="{accent}">{esc(value)}</text>
    <text x="14" y="80" font-size="10" fill="{FAINT}">{esc(sub)}</text>
  </g>"""


def panel(x, y, w, h, title, accent=GREEN):
    return f"""
  <g transform="translate({x},{y})">
    <rect width="{w}" height="{h}" rx="7" fill="{BG1}" stroke="{LINE}"/>
    <rect width="{w}" height="26" rx="7" fill="{BG2}"/>
    <rect y="19" width="{w}" height="7" fill="{BG2}"/>
    <circle cx="16" cy="13" r="3.5" fill="{accent}"/>
    <text x="30" y="17" font-size="11" letter-spacing="1.5" fill="{TEXT}">{esc(title)}</text>
  </g>"""


def kind_color(kind):
    if "NEUTRALIZED" in kind or "DEPLOYED" in kind:
        return GREEN
    if "FLAGGED" in kind or "STAGED" in kind:
        return AMBER
    if "REJECTED" in kind:
        return RED
    return CYAN


def main():
    d = json.load(open(os.path.join(HERE, "data.json")))
    k = d["kpis"]
    p = []
    p.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="{MONO}">')

    # defs: scanline gradient, glow, styles
    p.append(f"""
  <defs>
    <linearGradient id="scan" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{NEON}" stop-opacity="0"/>
      <stop offset="0.5" stop-color="{NEON}" stop-opacity="0.07"/>
      <stop offset="1" stop-color="{NEON}" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{CYAN}" stop-opacity="0"/>
      <stop offset="1" stop-color="{CYAN}" stop-opacity="0.55"/>
    </linearGradient>
    <radialGradient id="vig" cx="0.5" cy="0.1" r="1">
      <stop offset="0" stop-color="{BG1}"/>
      <stop offset="1" stop-color="{BG0}"/>
    </radialGradient>
    <style>
      text {{ font-family:{MONO}; }}
      .blink {{ animation: blink 1.05s steps(1) infinite; }}
      @keyframes blink {{ 50% {{ opacity:0; }} }}
      .pulse {{ animation: pulse 1.6s ease-in-out infinite; transform-origin:center; }}
      @keyframes pulse {{ 0%,100%{{opacity:1}} 50%{{opacity:.25}} }}
      .scan {{ animation: scan 6s linear infinite; }}
      @keyframes scan {{ 0%{{transform:translateY(-60px)}} 100%{{transform:translateY({H}px)}} }}
      .row {{ animation: fin .5s ease both; }}
      @keyframes fin {{ from{{opacity:.15;transform:translateX(-10px)}} to{{opacity:1;transform:translateX(0)}} }}
      .bar {{ transform-origin:left center; animation: grow 1.1s cubic-bezier(.2,.8,.2,1) both; }}
      @keyframes grow {{ from {{ transform:scaleX(0); }} to {{ transform:scaleX(1); }} }}
      .radar {{ animation: rsweep 4s linear infinite; }}
      @keyframes rsweep {{ 0%{{transform:translateX(0);opacity:.0}} 10%{{opacity:1}} 100%{{transform:translateX(330px);opacity:0}} }}
      .flick {{ animation: flick 4s steps(1) infinite; }}
      @keyframes flick {{ 0%,97%,100%{{opacity:1}} 98%{{opacity:.4}} 99%{{opacity:.85}} }}
    </style>
  </defs>
  <rect width="{W}" height="{H}" rx="10" fill="url(#vig)" stroke="{LINE}"/>
  <rect class="scan" width="{W}" height="60" fill="url(#scan)"/>""")

    # ---- header ----
    prompt = f'{esc(d["login"])}@soc:~# ./threat-monitor --live'
    p.append(f"""
  <g transform="translate(22,34)">
    <text font-size="15" fill="{NEON}" class="flick">{prompt}<tspan class="blink" fill="{NEON}">▊</tspan></text>
  </g>
  <g transform="translate({W-22},34)" text-anchor="end">
    <text font-size="12" fill="{TEXT}"><tspan fill="{GREEN}" class="pulse">●</tspan>  STATUS: MONITORING   ·   {esc(d["generated_at"])}</text>
  </g>
  <line x1="22" y1="48" x2="{W-22}" y2="48" stroke="{LINE}"/>""")

    # ---- KPI strip ----
    tiles = [
        ("THREATS NEUTRALIZED", k["threats_neutralized"], GREEN, f'{k["threats_active"]} active'),
        ("PATCHES DEPLOYED", k["patches_deployed"], CYAN, "merged"),
        ("SYSTEMS DEFENDED", k["systems_defended"], TEXT, f'{k["stars"]}★'),
        ("DAYS ON WATCH", k["days_on_watch"], AMBER, f'max {k["longest_watch"]}'),
        ("INTEL REPORTS", k["intel_reports"], NEON, f'{d["year_contributions"]}/yr'),
    ]
    tx, ty, gap = 22, 64, 12
    tw = (W - 44 - gap * (len(tiles) - 1)) / len(tiles)
    for i, (lab, val, acc, sub) in enumerate(tiles):
        p.append(tcell(tx + i * (tw + gap), ty, tw, 92, lab, val, acc, sub))

    # ---- live scan feed (left) ----
    fx, fy, fw, fh = 22, 172, 556, 300
    p.append(panel(fx, fy, fw, fh, "LIVE SCAN FEED", GREEN))
    ly = fy + 48
    for i, e in enumerate(d["feed"]):
        c = kind_color(e["kind"])
        ts = e["ts"][:10]
        line = f'{e["kind"]:<18} {e["ref"]:<11} {e["repo"]}'
        meta = f'  {e["meta"]}' if e["meta"] else ""
        p.append(f"""
  <g class="row" style="animation-delay:{0.12*i:.2f}s" transform="translate({fx+16},{ly+i*27})">
    <text font-size="12" fill="{FAINT}">{esc(ts)}</text>
    <text x="78" font-size="12" fill="{c}">▸ {esc(e["kind"])}</text>
    <text x="238" font-size="12" fill="{DIM}">{esc(e["ref"])}</text>
    <text x="330" font-size="12" fill="{TEXT}">{esc(e["repo"])}{esc(meta)}</text>
  </g>""")

    # ---- monitored systems (right top) ----
    sx, sy, sw, sh = 592, 172, W - 22 - 592, 182
    p.append(panel(sx, sy, sw, sh, "MONITORED SYSTEMS", CYAN))
    maxpct = max((l["pct"] for l in d["languages"]), default=1)
    barmax = sw - 110
    by = sy + 44
    for i, l in enumerate(d["languages"]):
        w = max(4, barmax * l["pct"] / maxpct)
        col = l.get("color") or GREEN
        p.append(f"""
  <g transform="translate({sx+16},{by+i*22})">
    <text font-size="11" fill="{TEXT}">{esc(l["name"][:9])}</text>
    <rect x="72" y="-9" width="{barmax}" height="9" rx="2" fill="{BG0}" stroke="{LINE}"/>
    <rect class="bar" style="animation-delay:{0.1*i:.2f}s" x="72" y="-9" width="{w:.1f}" height="9" rx="2" fill="{esc(col)}"/>
    <text x="{72+barmax+6}" y="0" font-size="10" fill="{DIM}">{l["pct"]:.0f}%</text>
  </g>""")

    # ---- defense readiness gauge (right bottom) ----
    gx, gy, gw, gh = 592, 364, W - 22 - 592, 108
    p.append(panel(gx, gy, gw, gh, "DEFENSE READINESS", AMBER))
    readiness = min(99, 42 + k["days_on_watch"] * 4 + len(d["feed"]) * 3)
    rbw = gw - 32
    rbfill = rbw * readiness / 100
    posture = "ELEVATED" if readiness >= 75 else "GUARDED" if readiness >= 55 else "BASELINE"
    pcol = GREEN if readiness >= 75 else AMBER if readiness >= 55 else CYAN
    p.append(f"""
  <g transform="translate({gx+16},{gy+46})">
    <text font-size="26" font-weight="700" fill="{pcol}">{readiness}%</text>
    <text x="{gw-32}" y="0" text-anchor="end" font-size="12" fill="{pcol}">{posture}</text>
    <rect y="14" width="{rbw}" height="10" rx="5" fill="{BG0}" stroke="{LINE}"/>
    <rect class="bar" y="14" width="{rbfill:.1f}" height="10" rx="5" fill="{pcol}"/>
    <text y="46" font-size="10.5" fill="{DIM}">uptime {d["uptime_days"]}d · {k["reviews"]} reviews · {k["forks"]} forks</text>
  </g>""")

    # ---- threat heatmap (contribution calendar) ----
    hx, hy, hw, hh = 22, 484, W - 44, 60
    p.append(f"""
  <rect x="{hx}" y="{hy}" width="{hw}" height="{hh}" rx="7" fill="{BG1}" stroke="{LINE}"/>
  <text x="{hx+16}" y="{hy+18}" font-size="11" letter-spacing="1.5" fill="{TEXT}">THREAT HEATMAP · 52W</text>""")
    cal = d["calendar"]
    maxc = max((c["count"] for c in cal), default=1)
    cell, gapc = 5, 1.4
    # group into weeks (7-day columns), align so last day is bottom-right
    wd_first = date.fromisoformat(cal[0]["date"]).weekday()  # Mon=0
    # github weeks are Sun-start; approximate columns by index
    gx0, gy0 = hx + 212, hy + 11
    for idx, c in enumerate(cal):
        col = idx // 7
        row = idx % 7
        v = c["count"]
        if v == 0:
            fill = "#10202a"
        else:
            t = (v / maxc) ** 0.5
            # green -> amber -> red as intensity climbs
            fill = GREEN if t < 0.45 else AMBER if t < 0.8 else RED
        p.append(f'<rect x="{gx0+col*(cell+gapc):.1f}" y="{gy0+row*(cell+gapc):.1f}" '
                 f'width="{cell}" height="{cell}" rx="1" fill="{fill}"/>')
    sweep_h = 7 * (cell + gapc)
    p.append(f'<rect class="radar" x="{gx0}" y="{gy0}" width="26" height="{sweep_h:.0f}" fill="url(#sweep)"/>')
    # legend + footer
    p.append(f"""
  <text x="{hx+16}" y="{hy+40}" font-size="10" fill="{DIM}">low</text>
  <rect x="{hx+40}" y="{hy+32}" width="7" height="7" rx="1" fill="{GREEN}"/>
  <rect x="{hx+49}" y="{hy+32}" width="7" height="7" rx="1" fill="{AMBER}"/>
  <rect x="{hx+58}" y="{hy+32}" width="7" height="7" rx="1" fill="{RED}"/>
  <text x="{hx+70}" y="{hy+40}" font-size="10" fill="{DIM}">high</text>
  <text x="{hx+hw-14}" y="{hy+40}" text-anchor="end" font-size="10" fill="{FAINT}">no human in the loop · auto-refreshed daily</text>""")

    p.append("</svg>")
    out = os.path.join(HERE, "output", "soc.svg")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        f.write("\n".join(p))
    print(f"wrote {out} ({os.path.getsize(out)} bytes)")


if __name__ == "__main__":
    main()
