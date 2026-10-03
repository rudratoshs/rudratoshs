#!/usr/bin/env python3
"""render_grid.py -> output/grid.svg

An isometric 3D "secure datacenter": one server rack per repository, shaded in
its primary language's colour, windows lit by its stars, with live packets
streaming across the grid and a radar sweep. Built to out-do a static skyline
on the two axes a city is weak on -- motion and theme.
"""
import base64
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1000, 560

BG = "#060a10"
RAIL = "#123042"
GRID = "#0e2230"
TEXT = "#9fb3c8"
DIM = "#4a6075"
CYAN = "#22e0ff"
NEON = "#00ff9c"
AMBER = "#ffb000"
RED = "#ff4d5e"
GREY = "#6e7681"

# isometric tiles
TW, TH = 62, 31          # tile width/height (2:1)
HW, HH = TW / 2, TH / 2
COLS, ROWS = 11, 6       # 66 cells
OX, OY = 424, 188        # projection origin
RH = 34                  # base rack height


def iso(c, r):
    return (OX + (c - r) * HW, OY + (c + r) * HH)


def hx(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def shade(color, f):
    """Darken (<0 lighten) a hex colour by factor f in [-1,1]."""
    r, g, b = hx(color)
    if f >= 0:
        r, g, b = (int(x * (1 - f)) for x in (r, g, b))
    else:
        r, g, b = (int(x + (255 - x) * -f) for x in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


def poly(pts, fill, extra=""):
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<polygon points="{p}" fill="{fill}"{(" " + extra) if extra else ""}/>'


def font_face():
    faces = []
    for weight, fn in ((400, "jbm-400.woff2"), (700, "jbm-700.woff2")):
        path = os.path.join(HERE, "fonts", fn)
        if not os.path.exists(path):
            return ""
        b64 = base64.b64encode(open(path, "rb").read()).decode()
        faces.append(f"@font-face{{font-family:'JBM';font-style:normal;font-weight:{weight};"
                     f"src:url(data:font/woff2;base64,{b64}) format('woff2');}}")
    return "".join(faces)


FONT = "'JBM',ui-monospace,Menlo,Consolas,monospace"


def main():
    d = json.load(open(os.path.join(HERE, "data.json")))
    repos = d["repos"][:COLS * ROWS]
    maxstars = max((r["stars"] for r in repos), default=1) or 1

    cells = []  # (c, r, repo)
    i = 0
    for r in range(ROWS):
        for c in range(COLS):
            if i < len(repos):
                cells.append((c, r, repos[i]))
                i += 1
    cells.sort(key=lambda t: (t[0] + t[1], t[1]))   # back-to-front

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" font-family="{FONT}">']
    p.append(f"""<defs>
  <style>{font_face()}
    text{{font-family:{FONT};}}
    .win{{animation:flk 4s steps(1) infinite;}}
    @keyframes flk{{0%,96%,100%{{opacity:1}}97%{{opacity:.35}}98%{{opacity:1}}99%{{opacity:.5}}}}
    .cur{{animation:bl 1.05s steps(1) infinite;}}
    @keyframes bl{{50%{{opacity:0}}}}
    .sweep{{animation:sw 7s linear infinite;transform-origin:{OX}px {OY+ROWS*HH}px;}}
    @keyframes sw{{to{{transform:rotate(360deg)}}}}
  </style>
  <radialGradient id="vig" cx="0.5" cy="0.35" r="0.9">
    <stop offset="0" stop-color="#0a131c"/><stop offset="1" stop-color="{BG}"/>
  </radialGradient>
  <filter id="glow" x="-60%" y="-60%" width="220%" height="220%">
    <feGaussianBlur stdDeviation="3" result="b"/><feMerge>
    <feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <radialGradient id="rad" cx="0" cy="0" r="1">
    <stop offset="0" stop-color="{CYAN}" stop-opacity="0.33"/>
    <stop offset="1" stop-color="{CYAN}" stop-opacity="0"/>
  </radialGradient>
</defs>
<rect width="{W}" height="{H}" rx="12" fill="url(#vig)"/>""")

    # starfield
    import random
    rnd = random.Random(7)
    stars = "".join(f'<circle cx="{rnd.randint(40, W-40)}" cy="{rnd.randint(40, 230)}" '
                    f'r="{rnd.choice([0.6,0.8,1.1])}" fill="#8fb6d9" opacity="{rnd.choice([0.3,0.5,0.7])}"/>'
                    for _ in range(46))
    p.append(f"<g>{stars}</g>")

    # side rails + header chrome
    p.append(f'<rect x="4" y="4" width="{W-8}" height="{H-8}" rx="12" fill="none" stroke="{RAIL}" stroke-width="1.5"/>')
    p.append(f'<line x1="14" y1="40" x2="14" y2="{H-40}" stroke="{CYAN}" stroke-opacity="0.35" stroke-width="2"/>')
    p.append(f'<line x1="{W-14}" y1="40" x2="{W-14}" y2="{H-40}" stroke="{CYAN}" stroke-opacity="0.35" stroke-width="2"/>')
    p.append(f'<text x="34" y="46" font-size="20" font-weight="700" fill="{TEXT}">~/<tspan fill="{CYAN}">threat-grid</tspan>'
             f'<tspan class="cur" fill="{CYAN}">_</tspan></text>')
    p.append(f'<text x="{W-34}" y="46" text-anchor="end" font-size="13" fill="{DIM}">// 01 · SECURE</text>')
    p.append(f'<line x1="34" y1="58" x2="{W-34}" y2="58" stroke="{RAIL}"/>')

    # iso floor grid
    floor = []
    for c in range(COLS + 1):
        a = iso(c, 0); b = iso(c, ROWS)
        floor.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{GRID}"/>')
    for r in range(ROWS + 1):
        a = iso(0, r); b = iso(COLS, r)
        floor.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{GRID}"/>')
    p.append(f'<g opacity="0.8">{"".join(floor)}</g>')

    # radar sweep wedge from the front edge
    cxr, cyr = iso(COLS / 2 - 0.5, ROWS)
    p.append(f'<g class="sweep"><path d="M0,0 L160,-70 L175,-20 Z" transform="translate({cxr},{cyr})" '
             f'fill="url(#rad)"/></g>')

    # racks (back to front)
    hot_color = NEON
    for c, r, repo in cells:
        sx, sy = iso(c, r)
        stars = repo["stars"]
        accent = repo.get("color") or GREY
        if not repo.get("lang"):
            accent = GREY
        hseed = int(hashlib.md5((repo["name"] + "h").encode()).hexdigest(), 16)
        h = 30 + min(64, stars * 5) + repo.get("forks", 0) * 2 + hseed % 16
        is_hot = stars == maxstars and maxstars > 1

        # corners
        Nt = (sx, sy - HH - h); Et = (sx + HW, sy - h)
        St = (sx, sy + HH - h); Wt = (sx - HW, sy - h)
        E = (sx + HW, sy); S = (sx, sy + HH); Wb = (sx - HW, sy)

        top = shade(accent, -0.15)
        right = shade(accent, 0.30)
        left = shade(accent, 0.52)
        p.append(poly([Nt, Et, St, Wt], top, 'stroke="#05080c" stroke-width="0.6"'))
        p.append(poly([Et, St, S, E], right, 'stroke="#05080c" stroke-width="0.6"'))
        p.append(poly([Wt, St, S, Wb], left, 'stroke="#05080c" stroke-width="0.6"'))

        # windows: lit by stars + a deterministic base so even 0-star racks glow a little
        seed = int(hashlib.md5(repo["name"].encode()).hexdigest(), 16)
        rr = random.Random(seed)
        nx = 3
        ny = max(3, int(h / 22))          # more window rows on taller racks
        lit_target = 2 + round((nx * ny - 2) * (stars / maxstars) ** 0.6) + rr.randint(0, 2)
        lit_bright = hot_color if is_hot else shade(accent, -0.55)

        def face_windows(origin, u, v):
            out = []
            n = 0
            vstep = 0.82 / ny
            for yy in range(ny):
                for xx in range(nx):
                    a0 = 0.12 + xx * 0.30
                    b0 = 0.10 + yy * vstep
                    da, db = 0.18, vstep * 0.62
                    corners = []
                    for aa, bb in ((a0, b0), (a0 + da, b0), (a0 + da, b0 + db), (a0, b0 + db)):
                        corners.append((origin[0] + aa * u[0] + bb * v[0],
                                        origin[1] + aa * u[1] + bb * v[1]))
                    lit = n < lit_target
                    col = lit_bright if lit else "#0a1119"
                    cls = ' class="win"' if lit and rr.random() < 0.5 else ""
                    op = "" if lit else ' opacity="0.9"'
                    out.append(f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in corners)}" '
                               f'fill="{col}"{cls}{op}/>')
                    n += 1
            return "".join(out)

        # right face frame: origin Et, u->St, v->E
        uR = (St[0] - Et[0], St[1] - Et[1]); vR = (E[0] - Et[0], E[1] - Et[1])
        # left face frame: origin Wt, u->St, v->Wb
        uL = (St[0] - Wt[0], St[1] - Wt[1]); vL = (Wb[0] - Wt[0], Wb[1] - Wt[1])
        grp = face_windows(Et, uR, vR) + face_windows(Wt, uL, vL)
        p.append(f'<g filter="url(#glow)">{grp}</g>' if is_hot else f"<g>{grp}</g>")

        # top-edge accent light
        p.append(f'<line x1="{Nt[0]:.1f}" y1="{Nt[1]:.1f}" x2="{Et[0]:.1f}" y2="{Et[1]:.1f}" '
                 f'stroke="{shade(accent,-0.4)}" stroke-width="1" opacity="0.7"/>')
        if is_hot:
            p.append(f'<text x="{Nt[0]:.1f}" y="{Nt[1]-8:.1f}" text-anchor="middle" font-size="10" '
                     f'fill="{NEON}" filter="url(#glow)">★{stars}</text>')

    # live packets streaming along two iso lanes toward the front gateway
    gate = iso(COLS / 2 - 0.5, ROWS)
    p.append(f'<circle cx="{gate[0]:.1f}" cy="{gate[1]+24:.1f}" r="7" fill="{NEON}" filter="url(#glow)"/>')
    p.append(f'<text x="{gate[0]:.1f}" y="{gate[1]+46:.1f}" text-anchor="middle" font-size="11" fill="{NEON}">FIREWALL · taintgate</text>')
    lanes = [
        (iso(0, 0), gate, NEON, "0s"),
        (iso(COLS, 0), gate, CYAN, "1.1s"),
        (iso(COLS, ROWS - 1), gate, NEON, "2.2s"),
        (iso(0, ROWS - 1), gate, RED, "0.6s"),   # one hostile packet
    ]
    for (x0, y0), (x1, y1), col, beg in lanes:
        pid = f"p{abs(hash((x0, y0, col))) % 9999}"
        p.append(f'<path id="{pid}" d="M{x0:.1f},{y0-6:.1f} L{x1:.1f},{y1+20:.1f}" fill="none" '
                 f'stroke="{col}" stroke-opacity="0.12" stroke-width="1.5"/>')
        p.append(f'<circle r="3.2" fill="{col}" filter="url(#glow)">'
                 f'<animateMotion dur="2.6s" begin="{beg}" repeatCount="indefinite">'
                 f'<mpath href="#{pid}"/></animateMotion></circle>')

    # legend + stat line
    ly = H - 30
    p.append(f'<text x="34" y="{ly}" font-size="12" fill="{DIM}">'
             f'cold <tspan fill="{shade(GREY,0.2)}">█</tspan><tspan fill="#1f6feb">█</tspan>'
             f'<tspan fill="{CYAN}">█</tspan><tspan fill="{NEON}">█</tspan> hot</text>')
    k = d["kpis"]
    p.append(f'<text x="{W-34}" y="{ly}" text-anchor="end" font-size="12" fill="{TEXT}">'
             f'{len(repos)} systems · {k["stars"]}★ · {k["patches_deployed"]} patches · '
             f'<tspan fill="{NEON}">0 breaches</tspan></text>')

    p.append("</svg>")
    out = os.path.join(HERE, "output", "grid.svg")
    with open(out, "w") as f:
        f.write("\n".join(p))
    print(f"wrote {out} ({os.path.getsize(out)} bytes) · {len(cells)} racks")


if __name__ == "__main__":
    main()
