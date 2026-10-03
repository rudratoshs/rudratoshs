#!/usr/bin/env python3
"""Render data.json into output/pet.svg -- a commit Tamagotchi.

A virtual pet on a retro handheld whose health, mood and evolution track your
GitHub streak. Commit and it thrives; go dark and it gets hungry, then sad,
then sick. Pure stdlib; animations live in the SVG.
"""
import json
import os
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 640, 360

# device + LCD palette (retro handheld)
SHELL = "#131a24"
SHELL_EDGE = "#0b1016"
BTN = "#1c2735"
LCD = "#c7d49b"        # classic pea-green LCD
LCD_DK = "#2f3b1b"     # LCD "ink"
LCD_EDGE = "#7f8a5c"
NEON = "#00ff9c"
AMBER = "#ffb000"
RED = "#ff4d5e"
MONO = "ui-monospace,'SF Mono','DejaVu Sans Mono',Menlo,Consolas,monospace"


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def main():
    d = json.load(open(os.path.join(HERE, "data.json")))
    k = d["kpis"]
    cal = d["calendar"]

    # days since last contribution
    today = date.today()
    last = None
    for c in reversed(cal):
        if c["count"] > 0:
            last = date.fromisoformat(c["date"])
            break
    days_since = (today - last).days if last else 999
    streak = k["days_on_watch"]
    longest = k["longest_watch"]
    xp = d["year_contributions"]
    level = xp // 10 + 1
    species = (d["languages"][0]["name"] if d["languages"] else "CODE").upper()[:10]

    # evolution stage by longest streak
    stages = [(0, "EGG"), (1, "HATCHLING"), (3, "SPROUT"), (7, "JUNIOR"), (21, "ELDER")]
    stage = stages[0][1]
    for thr, nm in stages:
        if longest >= thr:
            stage = nm

    # mood by days since last feed
    if days_since <= 1:
        mood, status, mc = "happy", "THRIVING", NEON
    elif days_since <= 3:
        mood, status, mc = "ok", "CONTENT", NEON
    elif days_since <= 7:
        mood, status, mc = "hungry", "HUNGRY", AMBER
    elif days_since <= 14:
        mood, status, mc = "sad", "SAD", AMBER
    else:
        mood, status, mc = "sick", "NEGLECTED", RED
    hp = max(5, min(100, 100 - days_since * 12))

    # LCD ink helper
    def ink(x, y, s, size=13, anchor="start", cls=""):
        c = f' class="{cls}"' if cls else ""
        return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{LCD_DK}" '
                f'text-anchor="{anchor}"{c}>{esc(s)}</text>')

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" font-family="{MONO}">']

    # ---- defs + animation ----
    p.append(f"""
  <defs>
    <linearGradient id="shell" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#1b2635"/><stop offset="1" stop-color="{SHELL}"/>
    </linearGradient>
    <style>
      text {{ font-family:{MONO}; }}
      .bob {{ animation: bob 2.2s ease-in-out infinite; transform-origin:center; }}
      @keyframes bob {{ 0%,100%{{transform:translateY(0)}} 50%{{transform:translateY(-7px)}} }}
      .blink {{ animation: bk 3.4s steps(1) infinite; transform-origin:center; }}
      @keyframes bk {{ 0%,92%,100%{{transform:scaleY(1)}} 95%{{transform:scaleY(.1)}} }}
      .beat {{ animation: beat 1s ease-in-out infinite; transform-origin:center; }}
      @keyframes beat {{ 0%,100%{{transform:scale(1)}} 50%{{transform:scale(1.18)}} }}
      .float {{ animation: fl 2.6s ease-in infinite; opacity:0; }}
      @keyframes fl {{ 0%{{opacity:0;transform:translateY(0)}} 25%{{opacity:1}} 100%{{opacity:0;transform:translateY(-34px)}} }}
      .z {{ animation: zz 3s ease-in-out infinite; opacity:0; }}
      @keyframes zz {{ 0%{{opacity:0;transform:translate(0,0) scale(.6)}} 40%{{opacity:.9}} 100%{{opacity:0;transform:translate(16px,-26px) scale(1.1)}} }}
      .barfill {{ transform-origin:left center; animation: grow 1.2s cubic-bezier(.2,.8,.2,1) both; }}
      @keyframes grow {{ from{{transform:scaleX(0)}} to{{transform:scaleX(1)}} }}
      .scanl {{ animation: sc 5s linear infinite; }}
      @keyframes sc {{ 0%{{transform:translateY(0)}} 100%{{transform:translateY(190px)}} }}
    </style>
  </defs>
  <rect width="{W}" height="{H}" rx="14" fill="{SHELL_EDGE}"/>""")

    # ---- device shell ----
    p.append(f"""
  <rect x="8" y="8" width="{W-16}" height="{H-16}" rx="26" fill="url(#shell)" stroke="#263447"/>
  <text x="34" y="44" font-size="13" letter-spacing="2" fill="{NEON}">COMMIT-PET</text>
  <text x="{W-34}" y="44" text-anchor="end" font-size="11" fill="#5a6e82">v1 · auto-fed by commits</text>
  <circle cx="{W/2}" cy="{H-30}" r="16" fill="{BTN}" stroke="#2c3b4e"/>
  <circle cx="{W/2-70}" cy="{H-30}" r="12" fill="{BTN}" stroke="#2c3b4e"/>
  <circle cx="{W/2+70}" cy="{H-30}" r="12" fill="{BTN}" stroke="#2c3b4e"/>
  <text x="{W/2}" y="{H-26}" text-anchor="middle" font-size="10" fill="#6f829a">FEED</text>""")

    # ---- LCD screen ----
    lx, ly, lw, lh = 60, 60, W - 120, 210
    p.append(f"""
  <g>
    <rect x="{lx-6}" y="{ly-6}" width="{lw+12}" height="{lh+12}" rx="12" fill="#0d1208" stroke="{LCD_EDGE}"/>
    <rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="6" fill="{LCD}"/>
    <clipPath id="lcd"><rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="6"/></clipPath>
    <g clip-path="url(#lcd)">
      <rect class="scanl" x="{lx}" y="{ly-20}" width="{lw}" height="14" fill="#000" opacity="0.04"/>""")

    # LCD header line: species + stage + level
    p.append(ink(lx + 14, ly + 24, f"{species} · {stage}", 12))
    p.append(ink(lx + lw - 14, ly + 24, f"LVL {level}", 12, "end"))
    p.append(f'<line x1="{lx+14}" y1="{ly+32}" x2="{lx+lw-14}" y2="{ly+32}" stroke="{LCD_DK}" stroke-opacity="0.35"/>')

    # ---- the creature (centered in LCD) ----
    cx, cy = lx + lw / 2, ly + lh / 2 + 6
    # eyes squint when sick/sad
    eye_rx = 4
    mouth = {
        "happy": f'<path d="M{cx-16},{cy+16} q16,16 32,0" stroke="{LCD_DK}" stroke-width="3" fill="none" stroke-linecap="round"/>',
        "ok":    f'<path d="M{cx-14},{cy+18} q14,9 28,0" stroke="{LCD_DK}" stroke-width="3" fill="none" stroke-linecap="round"/>',
        "hungry":f'<line x1="{cx-12}" y1="{cy+18}" x2="{cx+12}" y2="{cy+18}" stroke="{LCD_DK}" stroke-width="3" stroke-linecap="round"/>',
        "sad":   f'<path d="M{cx-14},{cy+20} q14,-10 28,0" stroke="{LCD_DK}" stroke-width="3" fill="none" stroke-linecap="round"/>',
        "sick":  f'<path d="M{cx-14},{cy+20} q14,-10 28,0" stroke="{LCD_DK}" stroke-width="3" fill="none" stroke-linecap="round"/>',
    }[mood]

    if stage == "EGG":
        body = (f'<ellipse cx="{cx}" cy="{cy}" rx="46" ry="54" fill="{LCD_DK}"/>'
                f'<ellipse cx="{cx}" cy="{cy}" rx="38" ry="46" fill="{LCD}"/>'
                f'<path d="M{cx-38},{cy} l10,-10 10,10 10,-10 10,10 10,-10 10,10" '
                f'stroke="{LCD_DK}" stroke-width="3" fill="none"/>')
        creature = f'<g class="bob">{body}</g>'
    else:
        # blob body + antenna + feet, size by stage
        size = {"HATCHLING": 40, "SPROUT": 48, "JUNIOR": 54, "ELDER": 60}.get(stage, 48)
        eye_scale = "scaleY(.3)" if mood in ("sad", "sick") else "scaleY(1)"
        antenna = (f'<line x1="{cx}" y1="{cy-size}" x2="{cx}" y2="{cy-size-16}" stroke="{LCD_DK}" stroke-width="3"/>'
                   f'<circle cx="{cx}" cy="{cy-size-18}" r="4" fill="{LCD_DK}"/>') if stage in ("JUNIOR", "ELDER") else ""
        ears = (f'<path d="M{cx-size*0.7},{cy-size*0.5} l-14,-22 20,8 z" fill="{LCD_DK}"/>'
                f'<path d="M{cx+size*0.7},{cy-size*0.5} l14,-22 -20,8 z" fill="{LCD_DK}"/>') if stage == "ELDER" else ""
        body = (f'{antenna}{ears}'
                f'<ellipse cx="{cx}" cy="{cy}" rx="{size}" ry="{size*0.92}" fill="{LCD_DK}"/>'
                f'<ellipse cx="{cx}" cy="{cy}" rx="{size-6}" ry="{size*0.92-6}" fill="{LCD}"/>'
                f'<ellipse cx="{cx-size*0.45}" cy="{cy+size*0.9}" rx="10" ry="7" fill="{LCD_DK}"/>'
                f'<ellipse cx="{cx+size*0.45}" cy="{cy+size*0.9}" rx="10" ry="7" fill="{LCD_DK}"/>'
                # eyes
                f'<g class="blink" transform="translate(0,0)">'
                f'<ellipse cx="{cx-16}" cy="{cy-6}" rx="{eye_rx}" ry="6" fill="{LCD_DK}" transform="translate({cx-16} {cy-6}) {eye_scale} translate({-(cx-16)} {-(cy-6)})"/>'
                f'<ellipse cx="{cx+16}" cy="{cy-6}" rx="{eye_rx}" ry="6" fill="{LCD_DK}" transform="translate({cx+16} {cy-6}) {eye_scale} translate({-(cx+16)} {-(cy-6)})"/>'
                f'</g>'
                f'{mouth}')
        creature = f'<g class="bob">{body}</g>'
    p.append(creature)

    # mood decorations
    if mood in ("happy", "ok"):
        for i, (dx, dy, dl) in enumerate([(-54, -6, 0), (52, 2, 0.8), (-36, -20, 1.6)]):
            p.append(f'<g class="float" style="animation-delay:{dl}s" transform="translate({cx+dx},{cy+dy})">'
                     f'<path d="M0,2 a4,4 0 0 1 8,0 a4,4 0 0 1 8,0 q0,6 -8,12 q-8,-6 -8,-12 z" fill="{RED if mood=="happy" else LCD_DK}"/></g>')
    elif mood == "hungry":
        p.append(f'<text x="{cx+56}" y="{cy-10}" font-size="22" class="beat" fill="{LCD_DK}">!</text>')
    else:  # sad / sick -> zzz
        for i in range(3):
            p.append(f'<text x="{cx+40}" y="{cy-20}" class="z" style="animation-delay:{i*0.9}s" '
                     f'font-size="{12+i*4}" fill="{LCD_DK}">z</text>')

    # HP bar inside LCD (bottom)
    hbx, hby, hbw = lx + 14, ly + lh - 26, lw - 28
    p.append(ink(hbx, hby - 5, f"HP {hp}%", 11))
    p.append(f'<rect x="{hbx+62}" y="{hby-16}" width="{hbw-62}" height="12" rx="3" fill="none" stroke="{LCD_DK}"/>')
    p.append(f'<rect class="barfill" x="{hbx+64}" y="{hby-14}" width="{(hbw-66)*hp/100:.1f}" height="8" rx="2" fill="{LCD_DK}"/>')
    p.append("</g></g>")  # close clip + screen group

    # ---- side stat rail under screen label area (on shell, right of nothing) ----
    # status pill + stats row beneath LCD
    sy = ly + lh + 30
    p.append(f"""
  <g transform="translate({lx},{sy})">
    <rect x="0" y="-16" width="128" height="24" rx="6" fill="{BTN}" stroke="#2c3b4e"/>
    <text x="12" y="1" font-size="12" fill="{mc}">● {esc(status)}</text>
  </g>
  <text x="{lx+150}" y="{sy+1}" font-size="12" fill="#8aa0b6">🔥 streak {streak}d  ·  best {longest}d  ·  fed {('today' if days_since<=0 else str(days_since)+'d ago')}</text>""")

    p.append("</svg>")
    out = os.path.join(HERE, "output", "pet.svg")
    with open(out, "w") as f:
        f.write("\n".join(p))
    print(f"wrote {out} ({os.path.getsize(out)} bytes) | stage={stage} mood={mood} hp={hp} since={days_since}")


if __name__ == "__main__":
    main()
