// node scripts/generate.mjs   (Node 18+). Optional env GH_TOKEN for live contribution rings.
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { render, fontCSS } from './render.mjs';

const root = new URL('..', import.meta.url);
const D = JSON.parse(await readFile(new URL('data.json', root), 'utf8'));
const b64 = buf => Buffer.from(buf).toString('base64');

// Contribution calendar → 53 weeks × 7 day levels (0–4)
const LEVEL = { NONE: 0, FIRST_QUARTILE: 1, SECOND_QUARTILE: 2, THIRD_QUARTILE: 3, FOURTH_QUARTILE: 4 };
D.weeks = Array.from({ length: 53 }, () => Array(7).fill(0));
if (process.env.GH_TOKEN) {
  const q = `query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{weekday contributionLevel}}}}}}`;
  const res = await fetch('https://api.github.com/graphql', { method: 'POST', headers: { Authorization: `bearer ${process.env.GH_TOKEN}`, 'Content-Type': 'application/json' }, body: JSON.stringify({ query: q, variables: { u: D.user } }) });
  const cal = (await res.json())?.data?.user?.contributionsCollection?.contributionCalendar;
  if (cal) {
    cal.weeks.slice(-53).forEach((w, i) => w.contributionDays.forEach(d => { D.weeks[i][d.weekday] = LEVEL[d.contributionLevel] ?? 0; }));
    D.stats[0].v = String(cal.totalContributions);
  }
}

// dev.to → signal (reactions per post) + enrich the transmission rows
try {
  const arts = await (await fetch(`https://dev.to/api/articles?username=${D.devto || 'rudratosh'}&per_page=30`)).json();
  if (Array.isArray(arts) && arts.length) {
    D.txTotals = {
      r: arts.reduce((a, x) => a + x.public_reactions_count, 0),
      c: arts.reduce((a, x) => a + x.comments_count, 0),
      p: arts.length,
    };
    D.signal = arts.slice(0, 16).map(x => x.public_reactions_count).reverse();   // oldest→newest
    const norm = s => s.toLowerCase().replace(/[^a-z0-9]/g, '');
    for (const row of D.tx) {
      const key = norm(row.ti).slice(0, 16);
      const hit = arts.find(x => norm(x.title).includes(key));
      row.r = hit ? hit.public_reactions_count : 0;
      row.c = hit ? hit.comments_count : 0;
    }
  }
} catch (e) { console.warn('dev.to skipped:', e.message); }

const now = new Date();
const doy = (now - new Date(now.getFullYear(), 0, 0)) / 864e5;
D.stardate = (now.getFullYear() + doy / 365).toFixed(4);
D.synced = now.toISOString().slice(0, 10);

const planet = 'data:image/webp;base64,' + b64(await readFile(new URL('assets/planet.webp', root)));
const probe = render(D, { planet });
let css = '';
try { css = await fontCSS(probe.disp, probe.mono, fetch, b64); } catch (e) { console.warn('fonts skipped:', e.message); }
const { files } = render(D, { planet, fontCSS: css });

await mkdir(new URL('svg/', root), { recursive: true });
for (const [name, svg] of Object.entries(files)) await writeFile(new URL(`svg/${name}`, root), svg);
console.log('wrote', Object.keys(files).length, 'SVGs');
