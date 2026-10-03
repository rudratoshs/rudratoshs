// Renders every profile panel as a standalone animated SVG (no JS — GitHub-safe).
export function render(D, A = {}) {
  const W = 840;
  const C = { ink: '#e6ecf7', dim: '#8b97b0', faint: '#56637f', cyan: '#5bd6ff', viol: '#a988ff', gold: '#ffce73', mint: '#54f0b2', coral: '#ff7f6e' };
  const MONO = `'JBM',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace`;
  const DISP = `'UNB','Segoe UI',Helvetica,Arial,sans-serif`;
  const used = { disp: new Set(), mono: new Set() };
  const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  const rec = (set, s) => { for (const ch of String(s)) set.add(ch); };
  const t = (x, y, s, a = '') => { rec(used.mono, s); return `<text x="${x}" y="${y}" ${a}>${esc(s)}</text>`; };
  const dt = (x, y, s, a = '', tail = '') => { rec(used.disp, s); return `<text class="d" x="${x}" y="${y}" ${a}>${esc(s)}${tail}</text>`; };
  const f = n => +n.toFixed(2);
  const wrap = (s, n) => { const out = []; let l = ''; for (const w of s.split(' ')) { if ((l + ' ' + w).trim().length > n) { out.push(l.trim()); l = w; } else l += ' ' + w; } if (l.trim()) out.push(l.trim()); return out; };
  const fade = (d, inner) => `<g class="fade" style="animation-delay:${d}s">${inner}</g>`;

  const corners = h => [[10, 10, 1, 1], [W - 10, 10, -1, 1], [10, h - 10, 1, -1], [W - 10, h - 10, -1, -1]]
    .map(([x, y, sx, sy]) => `<path d="M${x} ${y + 22 * sy} V${y} H${x + 22 * sx}" fill="none" stroke="${C.cyan}" stroke-opacity=".55" stroke-width="2" stroke-linecap="round"/>`).join('');

  function frame(h, num, title, body, css = '', defs = '') {
    const head = num ? `<rect class="pulse" x="28" y="27" width="7" height="7" rx="1.5" fill="${C.cyan}"/>
${t(44, 34, `// ${num} · ${title}`, `font-size="11" letter-spacing="3" fill="${C.cyan}"`)}
${t(W - 28, 34, `${D.world} · DEEP FIELD SURVEY`, `font-size="10" letter-spacing="2.5" fill="${C.faint}" text-anchor="end"`)}
<rect x="28" y="48" width="${W - 56}" height="1" fill="url(#hr)"/>` : '';
    return `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="${W}" height="${h}" viewBox="0 0 ${W} ${h}" role="img" aria-label="${esc(title)}">
<defs>
<linearGradient id="bg" x1="0" y1="0" x2=".35" y2="1"><stop offset="0" stop-color="#0c1532"/><stop offset=".6" stop-color="#070b1c"/><stop offset="1" stop-color="#04060d"/></linearGradient>
<linearGradient id="hr" x1="0" x2="1"><stop offset="0" stop-color="${C.cyan}" stop-opacity=".5"/><stop offset="1" stop-color="${C.cyan}" stop-opacity="0"/></linearGradient>
<linearGradient id="scan" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${C.cyan}" stop-opacity="0"/><stop offset="1" stop-color="${C.cyan}" stop-opacity=".06"/></linearGradient>
<linearGradient id="grad" x1="0" x2="1"><stop offset="0" stop-color="${C.cyan}"/><stop offset=".55" stop-color="${C.viol}"/><stop offset="1" stop-color="${C.gold}"/></linearGradient>
<pattern id="lines" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".2"/></pattern>
<clipPath id="fc"><rect width="${W}" height="${h}" rx="16"/></clipPath>
${defs}
</defs>
<style>${A.fontCSS || ''}
text{font-family:${MONO}}
.d{font-family:${DISP};font-weight:800}
.pulse{animation:pulse 1.8s ease-in-out infinite}
@keyframes pulse{50%{opacity:.2}}
.scan{animation:scan 8s linear infinite}
@keyframes scan{from{transform:translateY(-90px)}to{transform:translateY(${h}px)}}
.fade{animation:fade 1s cubic-bezier(.2,.8,.2,1) backwards}
@keyframes fade{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.blink{animation:blink 1.05s steps(1) infinite}
@keyframes blink{50%{opacity:0}}
@keyframes rot{to{transform:rotate(360deg)}}
${css}
@media (prefers-reduced-motion:reduce){*{animation-duration:0s!important;animation-delay:0s!important}}
</style>
<g clip-path="url(#fc)">
<rect width="${W}" height="${h}" fill="url(#bg)"/>
${body}
<rect class="scan" width="${W}" height="90" fill="url(#scan)"/>
<rect width="${W}" height="${h}" fill="url(#lines)"/>
</g>
<rect x=".5" y=".5" width="${W - 1}" height="${h - 1}" rx="16" fill="none" stroke="#7aa0e6" stroke-opacity=".22"/>
${corners(h)}
${head}
</svg>`;
  }

  // ---------- 01 HERO ----------
  function hero() {
    const h = 440, cx = 222, cy = 250;
    const LV = [[C.cyan, .14], [C.cyan, .45], [C.cyan, .85], [C.mint, 1], [C.gold, 1]];
    const dash = (ring, L) => {
      const m = [];
      for (let w = 0; w < 53; w++) {
        const parts = (D.weeks[w] && D.weeks[w][ring]) === L ? [[1, .7], [0, .3]] : [[0, 1]];
        for (const [k, v] of parts) { if (m.length && m[m.length - 1][0] === k) m[m.length - 1][1] += v; else m.push([k, v]); }
      }
      if (!m.some(p => p[0] === 1)) return null;
      if (m[0][0] === 0) m.unshift([1, 0]);
      if (m.length % 2) m.push([0, 0]);
      return m.map(p => f(p[1])).join(' ');
    };
    const rings = half => {
      let s = '';
      for (let r = 0; r < 7; r++) {
        const rx = 166 + r * 7, ry = f(rx * .27);
        for (let L = 0; L < 5; L++) { const d = dash(r, L); if (d) s += `<ellipse class="ring" rx="${rx}" ry="${ry}" pathLength="53" fill="none" stroke="${LV[L][0]}" stroke-opacity="${LV[L][1]}" stroke-width="3" stroke-dasharray="${d}"/>`; }
      }
      return `<g transform="translate(${cx} ${cy}) rotate(-16)"><g clip-path="url(#${half})">${s}</g></g>`;
    };
    const probe = half => `<g transform="translate(${cx} ${cy}) rotate(-16)"><g clip-path="url(#${half})"><ellipse rx="226" ry="66" fill="none" stroke="${C.viol}" stroke-opacity="${half === 'bk' ? .2 : .4}" stroke-dasharray="2 6"/><g class="px"><g class="py"><circle r="10" fill="url(#sat)"/><circle r="2.6" fill="#fff"/></g></g></g></g>`;
    const x0 = 486, y0 = 282;
    const stats = D.stats.map((s, i) => fade(.9 + i * .12, `<rect x="${x0 + i * 82}" y="${y0}" width="76" height="66" rx="10" fill="#0b1430" fill-opacity=".75" stroke="#7aa0e6" stroke-opacity=".18"/>
${dt(x0 + i * 82 + 12, y0 + 34, s.v, `font-size="22" fill="${s.c}"`)}
${t(x0 + i * 82 + 12, y0 + 52, s.l, `font-size="8.5" letter-spacing="1.4" fill="${C.dim}"`)}`)).join('');
    const legend = LV.map((l, i) => `<rect x="${292 + i * 13}" y="410" width="9" height="9" rx="2" fill="${l[0]}" fill-opacity="${l[1]}"/>`).join('');
    const body = `
<circle class="glow" cx="${cx}" cy="${cy}" r="200" fill="url(#halo)"/>
${rings('bk')}${probe('bk')}
<image href="${A.planet}" xlink:href="${A.planet}" x="${cx - 165}" y="${cy - 165}" width="330" height="330"/>
${rings('fr')}${probe('fr')}
${fade(1.6, `${t(28, 418, '53 WEEKS × 7 DAYS', `font-size="9.5" letter-spacing="1.5" fill="${C.faint}"`)}${t(262, 418, 'LESS', `font-size="9" fill="${C.faint}"`)}${legend}${t(364, 418, 'MORE', `font-size="9" fill="${C.faint}"`)}`)}
${fade(.1, t(x0, 100, `OPERATOR · CALLSIGN ${D.callsign}`, `font-size="10" letter-spacing="2.5" fill="${C.dim}"`))}
<g clip-path="url(#ty1)">${dt(x0, 152, D.name[0], `font-size="42" letter-spacing="-1" fill="${C.ink}"`)}</g>
<g clip-path="url(#ty2)">${dt(x0, 202, D.name[1], `font-size="42" letter-spacing="-1" fill="url(#grad)"`, `<tspan class="blink" fill="${C.cyan}">_</tspan>`)}</g>
${(rec(used.disp, '_'), '')}
${fade(.7, `${t(x0, 238, D.role, `font-size="12.5" fill="${C.ink}"`)}${t(x0, 257, D.role2, `font-size="11" fill="${C.dim}"`)}`)}
${stats}
${fade(1.4, `<circle class="pulse" cx="${x0 + 4}" cy="${378}" r="3.5" fill="${C.mint}"/>
${t(x0 + 14, 382, 'SURVEY ACTIVE', `font-size="10" letter-spacing="2" fill="${C.mint}"`)}
${t(x0 + 130, 382, `STARDATE ${D.stardate}`, `font-size="10" letter-spacing="1.5" fill="${C.dim}"`)}
${t(x0, 402, `SECTOR ${D.sector} · SYNCED ${D.synced}`, `font-size="10" letter-spacing="1.5" fill="${C.faint}"`)}`)}`;
    const defs = `<radialGradient id="halo"><stop offset=".55" stop-color="#3d8bff" stop-opacity=".38"/><stop offset="1" stop-color="#3d8bff" stop-opacity="0"/></radialGradient>
<radialGradient id="sat"><stop offset="0" stop-color="#fff"/><stop offset=".35" stop-color="${C.viol}"/><stop offset="1" stop-color="${C.viol}" stop-opacity="0"/></radialGradient>
<clipPath id="bk"><rect x="-400" y="-300" width="800" height="300"/></clipPath>
<clipPath id="fr"><rect x="-400" y="0" width="800" height="300"/></clipPath>
<clipPath id="ty1"><rect class="ty1" x="${x0 - 4}" y="108" width="344" height="58"/></clipPath>
<clipPath id="ty2"><rect class="ty2" x="${x0 - 4}" y="160" width="344" height="58"/></clipPath>`;
    const css = `.ring{animation:ring 90s linear infinite}
@keyframes ring{to{stroke-dashoffset:-53}}
.glow{animation:glow 7s ease-in-out infinite}
@keyframes glow{50%{opacity:.6}}
.px{animation:px 7s ease-in-out infinite alternate}
.py{animation:py 7s ease-in-out infinite alternate;animation-delay:-3.5s}
@keyframes px{from{transform:translate(-226px,0)}to{transform:translate(226px,0)}}
@keyframes py{from{transform:translate(0,66px)}to{transform:translate(0,-66px)}}
.ty1{transform-origin:${x0 - 4}px 0;animation:ty 1s steps(9) .3s backwards}
.ty2{transform-origin:${x0 - 4}px 0;animation:ty .8s steps(8) 1.25s backwards}
@keyframes ty{from{transform:scaleX(0)}to{transform:scaleX(1)}}`;
    return frame(h, '01', 'OPERATOR', body, css, defs);
  }

  // ---------- 02 MISSIONS ----------
  function missions() {
    const h = 340, cw = 252, ch = 240, y = 72;
    let css = '';
    const cards = D.projects.map((p, i) => {
      const x = 28 + i * (cw + 14), gx = x + cw - 34, gy = y + 32;
      css += `.g${i}{transform-origin:${gx}px ${gy}px;animation:rot ${9 + i * 3}s linear infinite}\n`;
      const lines = wrap(p.br, 31).slice(0, 5).map((l, k) => t(x + 20, y + 102 + k * 17, l, `font-size="11" fill="${C.dim}"`)).join('');
      let tx = x + 20;
      const tags = p.tech.map(tg => { const w = tg.length * 6 + 16; const s = `<rect x="${tx}" y="${y + ch - 40}" width="${w}" height="20" rx="6" fill="none" stroke="#7aa0e6" stroke-opacity=".25"/>${t(tx + 8, y + ch - 26, tg, `font-size="10" fill="${C.dim}"`)}`; tx += w + 6; return s; }).join('');
      return fade(.15 + i * .18, `<rect x="${x}" y="${y}" width="${cw}" height="${ch}" rx="14" fill="#0b1228" fill-opacity=".8" stroke="${p.c}" stroke-opacity=".28"/>
<rect x="${x + 20}" y="${y}" width="44" height="2" fill="${p.c}"/>
${t(x + 20, y + 36, p.cls, `font-size="9.5" letter-spacing="2" fill="${p.c}"`)}
<circle cx="${gx}" cy="${gy}" r="7" fill="${p.c}" fill-opacity=".9"/>
<g class="g${i}"><ellipse cx="${gx}" cy="${gy}" rx="18" ry="6" fill="none" stroke="${p.c}" stroke-opacity=".55" transform="rotate(-20 ${gx} ${gy})"/><circle cx="${gx + 16}" cy="${gy - 6}" r="2.2" fill="#fff"/></g>
${dt(x + 20, y + 72, p.n, `font-size="15" fill="${C.ink}"`)}
${lines}${tags}
${t(x + cw - 20, y + ch - 26, `★ ${p.s}`, `font-size="12" fill="${C.gold}" text-anchor="end"`)}`);
    }).join('');
    return frame(h, '02', 'FLAGSHIP MISSIONS', cards, css);
  }

  // ---------- 03 OPS (radar) ----------
  function ops() {
    const h = 310, cx = 150, cy = 182, R = 105;
    const pt = (a, r) => [f(cx + r * Math.cos(a * Math.PI / 180)), f(cy + r * Math.sin(a * Math.PI / 180))];
    let wedge = '';
    for (let k = 0; k < 7; k++) { const [x1, y1] = pt(-(k + 1) * 9, R), [x2, y2] = pt(-k * 9, R); wedge += `<path d="M${cx} ${cy} L${x1} ${y1} A${R} ${R} 0 0 1 ${x2} ${y2} Z" fill="${C.cyan}" fill-opacity="${f(.26 * (1 - k / 7))}"/>`; }
    const ang = [35, 125, 215, 300], rad = [62, 88, 46, 80];
    const blips = D.ops.map((o, i) => { const [x, y] = pt(ang[i], rad[i]); const d = f(-(4 - ang[i] / 90)); return `<circle class="ping" cx="${x}" cy="${y}" r="5" fill="none" stroke="${C.mint}" style="animation-delay:${d}s"/><circle class="blip" cx="${x}" cy="${y}" r="3.2" fill="${C.mint}" style="animation-delay:${d}s"/>${t(x + 8, y - 6, o.r, `font-size="9" fill="${C.ink}" fill-opacity=".75"`)}`; }).join('');
    const ticks = Array.from({ length: 36 }, (_, i) => { const [a, b] = pt(i * 10, R + 4), [c, d] = pt(i * 10, R + (i % 3 ? 8 : 12)); return `<line x1="${a}" y1="${b}" x2="${c}" y2="${d}" stroke="${C.cyan}" stroke-opacity=".35"/>`; }).join('');
    const max = Math.max(...D.ops.map(o => o.add + o.del));
    const x0 = 300;
    const rows = D.ops.map((o, i) => { const y = 112 + i * 46, aw = f(110 * o.add / max), dw = f(Math.max(1.5, 110 * o.del / max)); return fade(.2 + i * .15, `<circle class="pulse" cx="${x0 + 4}" cy="${y - 5}" r="4" fill="${C.cyan}" style="animation-delay:${i * .3}s"/>
${dt(x0 + 18, y, o.r, `font-size="14" fill="${C.ink}"`)}
${t(x0 + 18, y + 17, o.nt, `font-size="10.5" fill="${C.dim}"`)}
${t(588, y + 2, o.pr, `font-size="11.5" fill="${C.cyan}"`)}
${t(690, y - 2, `+${o.add}`, `font-size="11" fill="${C.mint}"`)}${t(812, y - 2, `−${o.del}`, `font-size="11" fill="${C.coral}" text-anchor="end"`)}
<rect x="690" y="${y + 6}" width="${aw}" height="4" rx="2" fill="${C.mint}"/><rect x="${f(692 + aw)}" y="${y + 6}" width="${dw}" height="4" rx="2" fill="${C.coral}"/>
<rect x="${x0}" y="${y + 26}" width="${812 - x0}" height="1" fill="#7aa0e6" fill-opacity=".1"/>`); }).join('');
    const body = `${[R / 3, 2 * R / 3, R].map(r => `<circle cx="${cx}" cy="${cy}" r="${f(r)}" fill="none" stroke="${C.cyan}" stroke-opacity=".18"/>`).join('')}
<line x1="${cx - R}" y1="${cy}" x2="${cx + R}" y2="${cy}" stroke="${C.cyan}" stroke-opacity=".12"/><line x1="${cx}" y1="${cy - R}" x2="${cx}" y2="${cy + R}" stroke="${C.cyan}" stroke-opacity=".12"/>
${ticks}
<g class="sweep">${wedge}<line x1="${cx}" y1="${cy}" x2="${cx + R}" y2="${cy}" stroke="${C.cyan}" stroke-width="1.5"/></g>
<circle cx="${cx}" cy="${cy}" r="3" fill="${C.cyan}"/>
${blips}
${t(x0, 80, 'SYSTEM', `font-size="9" letter-spacing="2" fill="${C.faint}"`)}${t(588, 80, 'PULL REQ', `font-size="9" letter-spacing="2" fill="${C.faint}"`)}${t(690, 80, 'DELTA', `font-size="9" letter-spacing="2" fill="${C.faint}"`)}
${rows}`;
    const css = `.sweep{transform-origin:${cx}px ${cy}px;animation:rot 4s linear infinite}
.ping{transform-box:fill-box;transform-origin:center;animation:ping 4s ease-out infinite}
@keyframes ping{0%{transform:scale(.6);opacity:.9}35%,100%{transform:scale(3);opacity:0}}
.blip{animation:blip 4s linear infinite}
@keyframes blip{0%{opacity:1}70%,100%{opacity:.3}}`;
    return frame(h, '03', 'EXTERNAL SYSTEMS REACHED', body, css);
  }

  // ---------- 04 SPECTRUM ----------
  function spectrum() {
    let seed = 11; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
    const sx = 28, sw = 784, sy = 76, sh = 76;
    const total = D.langs.reduce((a, l) => a + l.p, 0);
    const bands = [...D.langs, { n: 'Other', p: Math.max(0, 100 - total), c: C.faint }];
    let x = sx, lines = '';
    for (const b of bands) {
      const w = sw * b.p / 100;
      lines += `<rect x="${f(x)}" y="${sy}" width="${f(w)}" height="${sh}" fill="${b.c}" fill-opacity=".09"/>`;
      const n = Math.max(2, Math.round(w / 4));
      for (let k = 0; k < n; k++) { const lx = x + rnd() * w, lw = .6 + rnd() * 2.2, op = .25 + rnd() * .75; lines += `<rect${rnd() < .18 ? ` class="flk" style="animation-delay:-${f(rnd() * 3)}s"` : ''} x="${f(lx)}" y="${sy}" width="${f(lw)}" height="${sh}" fill="${b.c}" fill-opacity="${f(op)}"/>`; }
      x += w;
    }
    let lx = sx; const legend = bands.map(b => { const s = `<circle cx="${lx + 4}" cy="183" r="4" fill="${b.c}"/>${t(lx + 14, 187, b.n, `font-size="11" fill="${C.ink}"`)}${t(lx + 18 + b.n.length * 6.6, 187, `${b.p}%`, `font-size="11" fill="${C.dim}"`)}`; lx += 30 + (b.n.length + String(b.p).length + 1) * 6.6; return s; }).join('');
    let px = sx, py = 230; const pills = D.instr.map(n => { const w = n.length * 6.6 + 22; if (px + w > 812) { px = sx; py += 34; } const s = `<rect x="${f(px)}" y="${py}" width="${f(w)}" height="24" rx="8" fill="#0b1228" stroke="${C.viol}" stroke-opacity=".3"/>${t(f(px + 11), py + 16, n, `font-size="11" fill="${C.ink}"`)}`; px += w + 8; return s; }).join('');
    const h = py + 46;
    const body = `<clipPath id="sc"><rect x="${sx}" y="${sy}" width="${sw}" height="${sh}" rx="8"/></clipPath>
<rect x="${sx}" y="${sy}" width="${sw}" height="${sh}" rx="8" fill="#02040a"/>
<g clip-path="url(#sc)" class="fade">${lines}<rect class="cursor" x="${sx}" y="${sy}" width="2" height="${sh}" fill="#fff" fill-opacity=".8"/></g>
<rect x="${sx}" y="${sy}" width="${sw}" height="${sh}" rx="8" fill="none" stroke="#7aa0e6" stroke-opacity=".22"/>
${t(sx, 66, 'SPECTRAL ANALYSIS · LANGUAGE EMISSION LINES', `font-size="9" letter-spacing="2" fill="${C.faint}"`)}
${t(812, 66, '% OF SURVEYED SPACE', `font-size="9" letter-spacing="2" fill="${C.faint}" text-anchor="end"`)}
${fade(.3, legend)}
${t(sx, 218, 'ONBOARD INSTRUMENTS', `font-size="9" letter-spacing="2" fill="${C.faint}"`)}
${fade(.5, pills)}`;
    const css = `.flk{animation:flk 2.6s ease-in-out infinite}
@keyframes flk{50%{opacity:.15}}
.cursor{animation:cur 7s ease-in-out infinite alternate}
@keyframes cur{to{transform:translateX(${sw - 2}px)}}`;
    return frame(h, '04', 'INSTRUMENTS & LOADOUT', body, css);
  }

  // ---------- 05 TRANSMISSIONS (reactions-per-post signal) ----------
  function transmissions() {
    const S = (D.signal && D.signal.length) ? D.signal : [1, 1, 1, 1];
    const n = S.length, mx = Math.max(1, ...S), pk = S.indexOf(mx);
    const X0 = 28, CW = 784, Y0 = 70, CH = 74, base = Y0 + CH;
    const px = i => f(X0 + CW * (n > 1 ? i / (n - 1) : 0)), py = v => f(base - CH * (v / mx));
    const pts = S.map((v, i) => [px(i), py(v)]);
    const line = pts.map((p, i) => `${i ? 'L' : 'M'}${p[0]} ${p[1]}`).join(' ');
    const area = `M${X0} ${base} ${pts.map(p => `L${p[0]} ${p[1]}`).join(' ')} L${X0 + CW} ${base} Z`;
    const dots = pts.map((p, i) => i === pk
      ? `<circle cx="${p[0]}" cy="${p[1]}" r="9" fill="${C.mint}" fill-opacity=".25"/><circle cx="${p[0]}" cy="${p[1]}" r="4" fill="${C.mint}"/>`
      : `<circle cx="${p[0]}" cy="${p[1]}" r="2.4" fill="#cdd9ec"/>`).join('');
    const peak = pts[pk] ? t(pts[pk][0], pts[pk][1] - 10, String(mx), `font-size="11" fill="${C.mint}" text-anchor="middle"`) : '';
    const tot = D.txTotals || { r: 0, c: 0, p: D.tx.length };
    const rows = D.tx.map((r, i) => {
      const y = base + 50 + i * 38;
      const ti = r.ti.length > 58 ? r.ti.slice(0, 57) + '…' : r.ti;
      return fade(.25 + i * .1, `${t(28, y, r.d, `font-size="11" fill="${C.faint}"`)}${t(86, y, r.ch, `font-size="10" letter-spacing="1.5" fill="${C.viol}"`)}${t(188, y, ti, `font-size="12.5" fill="${C.ink}"`)}${t(650, y, `${r.r ?? 0} reactions`, `font-size="11" fill="${C.mint}"`)}${t(812, y, `${r.c ?? 0} comments`, `font-size="11" fill="${C.cyan}" text-anchor="end"`)}<rect x="28" y="${y + 14}" width="784" height="1" fill="#7aa0e6" fill-opacity=".1"/>`);
    }).join('');
    const h = base + 50 + D.tx.length * 38 + 6;
    const body = `<clipPath id="wc"><rect x="${X0}" y="${Y0 - 8}" width="${CW}" height="${CH + 14}" rx="8"/></clipPath>
${t(28, 56, 'SIGNAL · REACTIONS PER POST', `font-size="9" letter-spacing="2" fill="${C.faint}"`)}${t(812, 56, `${tot.r} reactions · ${tot.c} comments · ${tot.p} posts`, `font-size="9" letter-spacing="2" fill="${C.faint}" text-anchor="end"`)}
<g clip-path="url(#wc)"><path d="${area}" fill="url(#sig)"/><path d="${line}" fill="none" stroke="${C.viol}" stroke-width="2" stroke-opacity=".95"/>${dots}<rect class="sweep2" x="${X0}" y="${Y0 - 8}" width="2" height="${CH + 14}" fill="${C.cyan}" fill-opacity=".55"/></g>${peak}
${rows}`;
    const defs = `<linearGradient id="sig" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${C.viol}" stop-opacity=".32"/><stop offset="1" stop-color="${C.viol}" stop-opacity="0"/></linearGradient>`;
    const css = `.sweep2{animation:sw2 9s linear infinite}@keyframes sw2{from{transform:translateX(0)}to{transform:translateX(${CW - 2}px)}}`;
    return frame(h, '05', 'INTERCEPTED TRANSMISSIONS', body, css, defs);
  }

  // ---------- FOOTER ----------
  function footer() {
    const h = 150;
    rec(used.disp, '_');
    const body = `${t(420, 56, '// END OF TRANSMISSION', `font-size="11" letter-spacing="6" fill="${C.dim}" text-anchor="middle"`)}
${dt(420, 100, 'SURVEY CONTINUES', `font-size="30" letter-spacing="1" fill="url(#grad)" text-anchor="middle"`, `<tspan class="blink" fill="${C.cyan}">_</tspan>`)}
${t(420, 128, D.footer, `font-size="10" letter-spacing="1" fill="${C.faint}" text-anchor="middle"`)}`;
    return frame(h, null, 'Survey continues', body);
  }

  // ---------- LINK PILLS ----------
  function pill(l) {
    const w = Math.round(32 + (l.k.length + l.v.length) * 6.8 + 12), h = 40;
    return `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" role="img" aria-label="${esc(l.k)}">
<defs><linearGradient id="b" x1="0" x2="1"><stop offset="0" stop-color="#0c1532"/><stop offset="1" stop-color="#070b1c"/></linearGradient></defs>
<style>${A.fontCSS || ''}text{font-family:${MONO}}.p{animation:p 1.8s ease-in-out infinite}@keyframes p{50%{opacity:.25}}</style>
<rect x=".5" y=".5" width="${w - 1}" height="${h - 1}" rx="10" fill="url(#b)" stroke="${C.cyan}" stroke-opacity=".35"/>
<rect class="p" x="14" y="17" width="6" height="6" rx="1.5" fill="${C.cyan}"/>
${t(28, 25, l.k, `font-size="11" font-weight="600" letter-spacing="2" fill="${C.cyan}"`)}
${t(36 + l.k.length * 8.2, 25, l.v, `font-size="11" fill="${C.ink}"`)}
</svg>`;
  }

  const files = { 'hero.svg': hero(), 'missions.svg': missions(), 'ops.svg': ops(), 'spectrum.svg': spectrum(), 'transmissions.svg': transmissions(), 'footer.svg': footer() };
  for (const l of D.links) files[`link-${l.id}.svg`] = pill(l);
  return { files, disp: [...used.disp].join(''), mono: [...used.mono].join('') };
}

// Subsets Google Fonts to only the glyphs used and returns embeddable @font-face CSS.
export async function fontCSS(disp, mono, fetchImpl = fetch, b64) {
  const UA = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36' };
  async function one(family, weights, text, alias) {
    const url = `https://fonts.googleapis.com/css2?family=${family}:wght@${weights}&text=${encodeURIComponent(text)}`;
    const css = await (await fetchImpl(url, { headers: UA })).text();
    let out = '';
    for (const block of css.match(/@font-face\s*{[^}]+}/g) || []) {
      const w = (block.match(/font-weight:\s*(\d+)/) || [])[1] || '400';
      const src = (block.match(/url\(([^)]+)\)/) || [])[1];
      if (!src) continue;
      const buf = await (await fetchImpl(src)).arrayBuffer();
      out += `@font-face{font-family:'${alias}';font-weight:${w};src:url(data:font/woff2;base64,${b64(buf)}) format('woff2')}`;
    }
    return out;
  }
  return (await one('Unbounded', '800', disp, 'UNB')) + (await one('JetBrains+Mono', '400;600', mono, 'JBM'));
}
