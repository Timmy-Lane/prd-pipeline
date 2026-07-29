#!/usr/bin/env node
// calibrate-caps — the sweep the design-audit caps were set from, kept so they can be re-set.
//
// A cap is only meaningful if the known-good pages and the deliberately-slopped fixture land on
// opposite sides of it. This runs design-audit across all three classes and prints the per-metric
// distribution, so moving a number is an argument about data rather than about taste.
//
// Serve the corpus first, then run it:
//   (cd examples && python3 -m http.server 8931 --bind 127.0.0.1) &
//   (cd examples/app-ui/dist && python3 -m http.server 8932 --bind 127.0.0.1) &
//   (cd scripts/fixtures && python3 -m http.server 8933 --bind 127.0.0.1) &
//   node scripts/calibrate-caps.mjs
//
// Reading it: a metric earns a cap when SLOP sits clearly above GOOD's max, and the cap goes in
// the gap. Four metrics do; four do not and are reported uncapped instead — see design-audit's
// REPORT block. WILD is not a target, it is a reality check on what shipped products score.
import { execFileSync } from 'node:child_process'

const AUDIT = new URL("design-audit.mjs", import.meta.url).pathname
const L = 'http://127.0.0.1:8931'

const CORPUS = [
  ['GOOD  cortex-landing', `${L}/cortex-landing/`],
  ['GOOD  fieldnote', `${L}/fieldnote-warm-paper/`],
  ['GOOD  meridian', `${L}/meridian-editorial/`],
  ['GOOD  pebble', `${L}/pebble-playful/`],
  ['GOOD  app-ui', 'http://127.0.0.1:8932/'],
  ['SLOP  geometry-fixture', 'http://127.0.0.1:8933/slopped-geometry.html'],
  ['WILD  linear.app', 'https://linear.app'],
  ['WILD  stripe.com', 'https://stripe.com'],
  ['WILD  vercel.com', 'https://vercel.com'],
  ['WILD  ui.shadcn.com', 'https://ui.shadcn.com'],
]

const METRICS = ['offGrid', 'off4', 'spacingSteps', 'nearMiss', 'fontSizes', 'shadows', 'radii']
const rows = []

for (const [name, url] of CORPUS) {
  for (const theme of ['light', 'dark']) {
    let out
    try {
      out = execFileSync('node', [AUDIT, '--url', url, '--theme', theme, '--json'],
        { encoding: 'utf8', timeout: 180_000, stdio: ['ignore', 'pipe', 'ignore'] })
    } catch (e) {
      out = e.stdout // non-zero exit is expected — the JSON is still on stdout
      if (!out) { console.error(`SKIP ${name} ${theme}: ${String(e.message).split('\n')[0]}`); continue }
    }
    let r
    try { r = JSON.parse(out) } catch { console.error(`SKIP ${name} ${theme}: unparseable`); continue }
    const m = r.themes?.[theme]?.measurements
    if (!m) { console.error(`SKIP ${name} ${theme}: no measurements`); continue }
    rows.push({ name, theme, ...Object.fromEntries(METRICS.map((k) => [k, m[k]])),
      layoutAnim: m.layoutAnim.length, noFocusRing: m.noFocusRing.length,
      offGridValues: m.offGridValues, radiusValues: m.radiusValues, nearMissPairs: m.nearMissPairs.length,
      layoutAnimWhat: m.layoutAnim.slice(0, 4) })
    process.stderr.write(`. ${name} ${theme}\n`)
  }
}

const pad = (s, n) => String(s).padEnd(n)
console.log('\n' + pad('page', 26) + pad('thm', 6) + METRICS.map((k) => pad(k, 14)).join('') + pad('layoutAnim', 12) + 'noFocus')
console.log('-'.repeat(150))
for (const r of rows)
  console.log(pad(r.name, 26) + pad(r.theme, 6) + METRICS.map((k) => pad(r[k], 14)).join('') + pad(r.layoutAnim, 12) + r.noFocusRing)

console.log('\n=== distribution by class ===')
for (const cls of ['GOOD', 'SLOP', 'WILD']) {
  const g = rows.filter((r) => r.name.startsWith(cls))
  if (!g.length) continue
  console.log(`\n${cls} (n=${g.length})`)
  for (const k of [...METRICS, 'layoutAnim']) {
    const v = g.map((r) => r[k]).sort((a, b) => a - b)
    console.log(`  ${pad(k, 14)} min ${pad(v[0], 5)} median ${pad(v[Math.floor(v.length / 2)], 5)} max ${v[v.length - 1]}`)
  }
}

console.log('\n=== detail ===')
for (const r of rows.filter((x) => x.theme === 'light')) {
  console.log(`${pad(r.name, 26)} offGrid=${JSON.stringify(r.offGridValues)} radii=${JSON.stringify(r.radiusValues)} anim=${JSON.stringify(r.layoutAnimWhat)}`)
}
console.log('\n' + JSON.stringify(rows, null, 1))
