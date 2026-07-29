#!/usr/bin/env node
// extract-reference — measure a live page's design system so a reference becomes six numbers
// instead of an adjective. Phase 0 of the loop (SKILL.md → "Reference mining"), never Phase 2.
//
//   node scripts/extract-reference.mjs --url https://example.com
//   node scripts/extract-reference.mjs --url <url> --viewport 1440x900 --theme dark --json
//   node scripts/extract-reference.mjs --url <url> --out ref/example    # writes .md + .json
//   node scripts/extract-reference.mjs --diff ref/example.json ref/ours.json   # the clone gate
//
// Emits the SIX MECHANICS that `brand-to-system.md` § "Capturing a named product reference"
// demands — type pairing and weights, palette with roles, radius, elevation recipe,
// grid/measure, motion — plus the five design dials, measured rather than guessed.
//
// Needs Playwright, which this repo does not vendor. It is borrowed — in order — from this
// script's directory, the cwd, then `silver`'s own install. silver IS a local headless Playwright,
// so on a machine that can run silver there is nothing to install. Otherwise, in any project:
//   npm i -g agent-silver          # preferred; also gives you the driving/QA loop
//   npm i -D playwright && npx playwright install chromium     # or just the engine
//
// This measures PUBLIC RENDERED OUTPUT — the same computed styles any visitor's devtools show.
// It does not defeat auth, and it does not copy: the output is an input to a *differentiation*
// step (→ references/reference-mining.md § "The differentiation rule"), never a theme to ship.
// Exit 0 = measured. 2 = bad usage. 3 = page never loaded. 4 = playwright missing.

import { createRequire } from 'node:module'
import { existsSync, mkdirSync, readFileSync, realpathSync, writeFileSync } from 'node:fs'
import { delimiter, dirname, join } from 'node:path'
import { pathToFileURL } from 'node:url'

const argv = process.argv.slice(2)
const arg = (n, d) => { const i = argv.indexOf(`--${n}`); return i === -1 ? d : argv[i + 1] }
const url = arg('url')
const out = arg('out')
const theme = arg('theme', 'light')
const asJson = argv.includes('--json')
const [vw, vh] = String(arg('viewport', '1440x900')).split('x').map(Number)
const diffPair = argv.indexOf('--diff')

const USAGE = `usage:
  node scripts/extract-reference.mjs --url <url> [--viewport 1440x900] [--theme light|dark] [--out path] [--json]
  node scripts/extract-reference.mjs --diff <reference.json> <ours.json>`

if (diffPair !== -1) { await differentiationGate(argv[diffPair + 1], argv[diffPair + 2]); process.exit(0) }
if (!url) { console.error(USAGE); process.exit(2) }

/**
 * Find Playwright without asking anyone to install it. Three places, in order:
 *   1. next to this script — a checkout that vendored it;
 *   2. the cwd — the project under audit (ESM resolves a BARE import against the script's own
 *      directory, not the cwd, so this needs an explicit createRequire and is not the default it
 *      looks like);
 *   3. `silver`'s own install — silver IS a local headless Playwright, so if the machine can run
 *      silver it can already run this, and the "npm i -D playwright" step is noise.
 */
function silverRoot() {
  const exts = process.platform === 'win32' ? ['.cmd', '.exe', ''] : ['']
  for (const dir of (process.env.PATH || '').split(delimiter)) {
    for (const ext of exts) {
      const bin = join(dir, `silver${ext}`)
      if (!existsSync(bin)) continue
      let p = dirname(realpathSync(bin)) // dist/cli.js → dist → the package root
      for (let up = 0; up < 4; up++, p = dirname(p)) if (existsSync(join(p, 'node_modules'))) return p
    }
  }
  return null
}

async function need(name) {
  try { return await import(name) } catch { /* not next to the script */ }
  for (const base of [process.cwd(), silverRoot()].filter(Boolean)) {
    try {
      const req = createRequire(pathToFileURL(join(base, 'package.json')))
      return await import(pathToFileURL(req.resolve(name)).href)
    } catch { /* not there either */ }
  }
  throw new Error(`${name} is not resolvable from this script, from ${process.cwd()}, or from silver`)
}

/**
 * The differentiation gate. Mining a reference is legitimate; shipping it is not, and "we changed
 * it enough" is exactly the claim a model will make about a clone. So make it a count: of the six
 * mechanics, at least THREE must differ, and the accent hue may never land within 10° of the
 * reference's — a matching accent is the single tell a viewer reads as "this is that product".
 * Exit code = the number of failures. This is the measurable half of § The differentiation rule.
 */
async function differentiationGate(refPath, oursPath) {
  if (!refPath || !oursPath) { console.error(USAGE); process.exit(2) }
  let R, O
  try { R = JSON.parse(readFileSync(refPath, 'utf8')); O = JSON.parse(readFileSync(oursPath, 'utf8')) } catch (e) {
    console.error(`✗ ${e.message.split('\n')[0]}`)
    console.error('  Both arguments are the .json written by --out. Capture your own build first:')
    console.error('    node scripts/extract-reference.mjs --url <your dev-server url> --out ref/ours')
    process.exit(2)
  }
  const hue = (s) => { const m = /oklch\(([\d.]+) ([\d.]+) ([\d.]+)/.exec(s || ''); return m ? { L: +m[1], C: +m[2], H: +m[3] } : null }
  const fam = (r) => (r.type.stacks?.[0]?.[0] || '').split(',')[0].replace(/["']/g, '').trim().toLowerCase()
  const rh = hue(R.palette.accent); const oh = hue(O.palette.accent)
  const dH = rh && oh ? Math.min(Math.abs(rh.H - oh.H), 360 - Math.abs(rh.H - oh.H)) : 180
  const shadowMode = (r) => (r.shadow.length <= 1 ? 'border-first' : r.shadow.length <= 3 ? 'restrained' : 'layered')

  const axes = [
    ['type family', fam(R) !== fam(O), `${fam(R) || '—'} → ${fam(O) || '—'}`],
    ['accent hue', dH >= 30, `${rh ? rh.H.toFixed(0) : '—'}° → ${oh ? oh.H.toFixed(0) : '—'}° (Δ${dH.toFixed(0)}°)`],
    ['radius base', R.radius.base !== O.radius.base, `${R.radius.base}px → ${O.radius.base}px`],
    ['elevation', shadowMode(R) !== shadowMode(O), `${shadowMode(R)} → ${shadowMode(O)}`],
    ['grid / measure', R.spacing.unit !== O.spacing.unit || Math.abs((R.type.measureCh || 0) - (O.type.measureCh || 0)) >= 8,
      `${R.spacing.unit}px·${R.type.measureCh ?? '—'}ch → ${O.spacing.unit}px·${O.type.measureCh ?? '—'}ch`],
    ['motion', Math.abs((R.motion.medianUiMs || 0) - (O.motion.medianUiMs || 0)) >= 40 ||
      (R.motion.easings?.[0]?.[0] || '') !== (O.motion.easings?.[0]?.[0] || ''),
      `${R.motion.medianUiMs ?? '—'}ms → ${O.motion.medianUiMs ?? '—'}ms`],
  ]
  const moved = axes.filter(([, d]) => d).length
  console.log(`differentiation — ${R.title || refPath}  vs  ${O.title || oursPath}\n`)
  for (const [name, differs, detail] of axes) console.log(`  [${differs ? 'MOVED' : 'SAME '}] ${name.padEnd(15)} ${detail}`)

  let failures = 0
  if (moved < 3) { failures += 3 - moved; console.log(`\n✗ only ${moved} of 6 mechanics moved — 3 is the floor`) }
  if (dH < 10) { failures++; console.log(`✗ accent hue is within ${dH.toFixed(0)}° of the reference — that is the clone tell, move it`) }
  console.log(failures === 0 ? `\n✓ differentiated: ${moved}/6 mechanics moved, accent Δ${dH.toFixed(0)}°` : '')
  process.exit(failures)
}

let chromium
try {
  const pw = await need('playwright')
  chromium = pw.chromium ?? pw.default?.chromium // a cwd-resolved CJS build lands under `default`
  if (!chromium) throw new Error('playwright resolved but exports no `chromium`')
} catch (e) {
  console.error('✗ extract-reference needs playwright, which this repo does not vendor.')
  console.error('  npm i -g agent-silver          # preferred — silver ships one, and drives pages too')
  console.error('  npm i -D playwright && npx playwright install chromium   # or just the engine')
  console.error(`  (tried this script's dir, ${process.cwd()}, and silver: ${e.message.split('\n')[0]})`)
  process.exit(4)
}

/* ── colour: whatever the browser serialised → OKLCH ─────────────────────────────────────── */

const lin = (v) => (v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4)

/** linear sRGB → OKLCH [L, C, H]. Björn Ottosson's matrices, same pair as validate-chart-palette. */
function linearToOklch(r, g, b) {
  const l = Math.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b)
  const m = Math.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b)
  const s = Math.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b)
  const L = 0.2104542553 * l + 0.793617785 * m - 0.0040720468 * s
  const A = 1.9779984951 * l - 2.428592205 * m + 0.4505937099 * s
  const B = 0.0259040371 * l + 0.7827717662 * m - 0.808675766 * s
  const C = Math.hypot(A, B)
  let H = (Math.atan2(B, A) * 180) / Math.PI
  if (H < 0) H += 360
  return [L, C, C < 0.0015 ? 0 : H] // hue is meaningless at neutral chroma; report 0, not noise
}

/** Any computed colour string → {L,C,H,a} or null. Chrome serialises modern spaces verbatim. */
function parseColor(str) {
  if (!str || str === 'transparent' || str === 'none') return null
  let m = str.match(/^rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)(?:[,/\s]+([\d.%]+))?/i)
  if (m) {
    const a = m[4] === undefined ? 1 : m[4].endsWith('%') ? parseFloat(m[4]) / 100 : parseFloat(m[4])
    if (a === 0) return null
    const [L, C, H] = linearToOklch(lin(+m[1] / 255), lin(+m[2] / 255), lin(+m[3] / 255))
    return { L, C, H, a }
  }
  m = str.match(/^oklch\(\s*([\d.]+%?)\s+([\d.]+%?)\s+([\d.]+)(?:deg)?(?:\s*\/\s*([\d.%]+))?/i)
  if (m) {
    const pc = (v, s) => (v.endsWith('%') ? (parseFloat(v) / 100) * s : parseFloat(v))
    const a = m[4] === undefined ? 1 : m[4].endsWith('%') ? parseFloat(m[4]) / 100 : parseFloat(m[4])
    if (a === 0) return null
    return { L: pc(m[1], 1), C: pc(m[2], 0.4), H: parseFloat(m[3]), a }
  }
  m = str.match(/^color\(\s*srgb\s+([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)(?:\s*\/\s*([\d.%]+))?/i)
  if (m) {
    const a = m[4] === undefined ? 1 : m[4].endsWith('%') ? parseFloat(m[4]) / 100 : parseFloat(m[4])
    if (a === 0) return null
    const [L, C, H] = linearToOklch(lin(+m[1]), lin(+m[2]), lin(+m[3]))
    return { L, C, H, a }
  }
  // Tailwind v4 is this skill's own target stack, and Chrome serialises its `color-mix()` results
  // and non-sRGB authored colours as `oklab()` / `lab()` — not as rgb(). Without these two, every
  // border and every mixed surface on a v4 site parses to null and the card reports "borderless".
  m = str.match(/^oklab\(\s*([\d.]+%?)\s+([\d.eE+-]+)\s+([\d.eE+-]+)(?:\s*\/\s*([\d.%]+))?/i)
  if (m) {
    const a = m[4] === undefined ? 1 : m[4].endsWith('%') ? parseFloat(m[4]) / 100 : parseFloat(m[4])
    if (a === 0) return null
    const L = m[1].endsWith('%') ? parseFloat(m[1]) / 100 : parseFloat(m[1])
    const A = +m[2]; const B = +m[3]
    const C = Math.hypot(A, B); let H = (Math.atan2(B, A) * 180) / Math.PI
    if (H < 0) H += 360
    return { L, C, H: C < 0.0015 ? 0 : H, a }
  }
  m = str.match(/^lab\(\s*([\d.]+%?)\s+([\d.eE+-]+)\s+([\d.eE+-]+)(?:\s*\/\s*([\d.%]+))?/i)
  if (m) {
    const a = m[4] === undefined ? 1 : m[4].endsWith('%') ? parseFloat(m[4]) / 100 : parseFloat(m[4])
    if (a === 0) return null
    // CIE Lab is D50-referred per CSS Color 4; sRGB is D65. Skipping the Bradford adaptation puts
    // neutrals off by a visible amount of yellow, which would then read as brand chroma.
    const L = m[1].endsWith('%') ? parseFloat(m[1]) : parseFloat(m[1])
    const fy = (L + 16) / 116; const fx = fy + +m[2] / 500; const fz = fy - +m[3] / 200
    const f = (t) => (t ** 3 > 216 / 24389 ? t ** 3 : (116 * t - 16) / 903.3)
    const D50 = [0.3457 / 0.3585, 1, (1 - 0.3457 - 0.3585) / 0.3585]
    const [X, Y, Z] = [f(fx) * D50[0], (L > 8 ? fy ** 3 : L / 903.3) * D50[1], f(fz) * D50[2]]
    const BRAD = [[0.9554734527042182, -0.023098536874261423, 0.0632593086610217],
      [-0.028369706963208136, 1.0099954580058226, 0.021041398966943008],
      [0.012314001688319899, -0.020507696433477912, 1.3303659366080753]] // D50 → D65
    const [x, y, z] = BRAD.map((r) => r[0] * X + r[1] * Y + r[2] * Z)
    const XYZ2RGB = [[3.2409699419045226, -1.537383177570094, -0.4986107602930034],
      [-0.9692436362808796, 1.8759675015077202, 0.04155505740717559],
      [0.05563007969699366, -0.20397695888897652, 1.0569715142428786]]
    const [r, g, b] = XYZ2RGB.map((row) => row[0] * x + row[1] * y + row[2] * z)
    const [Lo, Co, Ho] = linearToOklch(r, g, b)
    return { L: Lo, C: Co, H: Ho, a }
  }
  return null
}

const fmt = (c) => `oklch(${c.L.toFixed(3)} ${c.C.toFixed(3)} ${c.H.toFixed(1)})${c.a < 1 ? ` / ${c.a.toFixed(2)}` : ''}`
const key = (c) => `${c.L.toFixed(2)}|${c.C.toFixed(2)}|${(c.C < 0.02 ? 0 : Math.round(c.H / 4) * 4)}|${c.a.toFixed(2)}`

/* ── the in-page pass. Geometry and computed style only — nothing here is an opinion. ─────── */

function measure() {
  const px = (v) => Math.round(parseFloat(v) || 0)
  const bump = (map, k, n = 1) => k && map.set(k, (map.get(k) || 0) + n)
  const top = (map, n) => [...map.entries()].sort((a, b) => b[1] - a[1]).slice(0, n)

  const nodes = [...document.querySelectorAll('body *')]
    .filter((e) => e.getClientRects().length && getComputedStyle(e).visibility !== 'hidden')
    .map((e) => ({ e, r: e.getBoundingClientRect(), s: getComputedStyle(e) }))

  // COLOUR — two independent signals, because neither alone finds the brand.
  //   AREA answers "what is the surface": the page background is 60% of the paint.
  //   BRAND INTENT answers "what is the accent": a colour on an element whose class/id/data
  //   attributes say logo/brand/cta/button carries intent that frequency cannot see. Ranking by
  //   frequency finds a border; ranking by area finds a section fill; only the CTA background
  //   finds the actual brand colour. Weights and the ancestor-lift rule follow dembrandt's
  //   `color-heuristics.ts`, whose ANCESTOR_LIFT_MAX exists so a wrapper called `hero` cannot
  //   promote every colour inside it.
  const CONTEXT = { logo: 5, brand: 5, primary: 4, cta: 4, hero: 3, button: 3, card: 2, section: 2, feature: 2, panel: 2, input: 2, badge: 2, chip: 2, footer: 2, link: 2, header: 2, nav: 1 }
  const LIFT_MAX = 2
  const bg = new Map(); const fg = new Map(); const bd = new Map()
  const intent = new Map(); const ctaBg = new Map()
  for (const { e, r, s } of nodes) {
    const area = Math.max(0, r.width) * Math.max(0, r.height)
    if (area > 0) bump(bg, s.backgroundColor, area)
    const chars = [...e.childNodes].filter((n) => n.nodeType === 3).reduce((n, t) => n + t.textContent.trim().length, 0)
    if (chars > 0) bump(fg, s.color, chars)
    for (const [w, side] of [[s.borderTopWidth, s.borderTopColor], [s.borderRightWidth, s.borderRightColor],
      [s.borderBottomWidth, s.borderBottomColor], [s.borderLeftWidth, s.borderLeftColor]])
      if (px(w) > 0) bump(bd, side, Math.max(r.width, r.height))

    // `className` is an SVGAnimatedString on SVG elements and stringifies to "[object …]".
    const cls = (el) => el.getAttribute?.('class') || ''
    const ctx = `${cls(e)} ${e.id || ''} ${e.getAttribute('data-component') || ''} ${e.getAttribute('data-cta') || ''} ${e.tagName}`.toLowerCase()
    let score = 1
    for (const [k, w] of Object.entries(CONTEXT)) if (ctx.includes(k)) score = Math.max(score, w)
    if (e.tagName === 'A') score = Math.max(score, CONTEXT.link)
    if (e.tagName === 'BUTTON' || e.getAttribute('role') === 'button') score = Math.max(score, CONTEXT.button)
    if (score <= LIFT_MAX) { // only weak keywords may be inherited, and only 4 hops up
      let lift = 0, node = e.parentElement
      for (let hop = 0; hop < 4 && node && lift < LIFT_MAX; hop++) {
        const a = `${cls(node)} ${node.id || ''}`.toLowerCase()
        for (const [k, w] of Object.entries(CONTEXT)) if (w <= LIFT_MAX && a.includes(k)) lift = Math.max(lift, w)
        node = node.parentElement
      }
      score = Math.max(score, lift)
    }
    // A solid, non-monochrome fill on something that calls itself a button IS the primary. Two
    // sightings required — one "Sign up" pill is a page, a repeated pill is a system. The α≥0.7
    // floor is what makes it work on a site that ghost-buttons everything: a 5%-white hover fill
    // is chrome, not a CTA, and without the floor it wins by sheer repetition.
    const alpha = (s.backgroundColor.match(/rgba?\([^)]*[,/]\s*([\d.]+)\s*\)/) || [, '1'])[1]
    const solidFill = s.backgroundColor && +alpha >= 0.7 &&
      !['rgb(255, 255, 255)', 'rgb(0, 0, 0)', 'transparent'].includes(s.backgroundColor)
    if (/button|btn|cta/.test(ctx) && solidFill) { score = Math.max(score, 25); bump(ctaBg, s.backgroundColor) }
    if (score > 1) {
      if (solidFill) bump(intent, s.backgroundColor, score)
      if (chars > 0) bump(intent, s.color, score)
    }
  }

  // TYPE — the ramp as authored, not as guessed. Sample text proves which role each row is.
  const ramp = new Map(); const families = new Map()
  for (const { e, s } of nodes) {
    const text = [...e.childNodes].filter((n) => n.nodeType === 3).map((t) => t.textContent.trim()).join(' ').trim()
    if (!text) continue
    bump(families, s.fontFamily, text.length)
    const k = [px(s.fontSize), s.fontWeight, s.lineHeight === 'normal' ? 'normal' : px(s.lineHeight),
      s.letterSpacing === 'normal' ? '0' : parseFloat(s.letterSpacing).toFixed(2), s.textTransform].join('/')
    const cur = ramp.get(k) || { n: 0, chars: 0, sample: '' }
    cur.n++; cur.chars += text.length
    if (text.length > cur.sample.length) cur.sample = text.slice(0, 60)
    ramp.set(k, cur)
  }

  // MEASURE — line length of the longest real paragraph, in approximate characters.
  const paras = nodes.filter(({ e, r }) => /^(P|LI|BLOCKQUOTE)$/.test(e.tagName) && e.textContent.trim().length > 120 && r.width > 200)
  const measures = paras.map(({ r, s }) => Math.round(r.width / (parseFloat(s.fontSize) * 0.5)))

  // SPACING · RADIUS · ELEVATION
  const space = new Map(); const radius = new Map(); const shadow = new Map()
  for (const { r, s } of nodes) {
    for (const v of [s.paddingTop, s.paddingRight, s.paddingBottom, s.paddingLeft, s.gap, s.rowGap, s.columnGap]) {
      const n = px(v); if (n > 0 && n <= 200) bump(space, n)
    }
    for (const v of [s.borderTopLeftRadius, s.borderTopRightRadius, s.borderBottomLeftRadius, s.borderBottomRightRadius]) {
      if (v.includes('%')) { bump(radius, 'pill/circle'); continue }
      const n = px(v); if (n > 0) bump(radius, Math.min(n, Math.round(Math.min(r.width, r.height) / 2)) >= Math.round(Math.min(r.width, r.height) / 2) ? 'pill/circle' : n)
    }
    // Tailwind's shadow utilities compile to a six-layer stack of mostly zero-alpha no-ops, so a
    // naive census reports `rgba(0,0,0,0) 0px 0px 0px 0px, …` as the site's top elevation recipe.
    // Split on top-level commas and keep only layers that actually paint.
    if (s.boxShadow && s.boxShadow !== 'none') {
      const live = s.boxShadow.split(/,(?![^(]*\))/).map((l) => l.trim())
        .filter((l) => !/rgba?\([^)]*[,/]\s*0(\.0+)?\s*\)/.test(l)).join(', ')
      if (live) bump(shadow, live.replace(/\s+/g, ' ').slice(0, 120))
    }
  }

  // TEXTURE — the material layer, split by kind so TEXTURE_LEVEL is read, not guessed.
  const tex = { gradient: 0, image: 0, svgNoise: 0, backdropBlur: 0, blend: 0, filter: 0 }
  for (const { s } of nodes) {
    const bi = s.backgroundImage
    if (bi && bi !== 'none') {
      if (/gradient\(/.test(bi)) tex.gradient++
      if (/url\(/.test(bi)) (/data:image\/svg|noise|grain|texture/i.test(bi) ? tex.svgNoise++ : tex.image++)
    }
    if (s.backdropFilter && s.backdropFilter !== 'none') tex.backdropBlur++
    if (s.mixBlendMode && s.mixBlendMode !== 'normal') tex.blend++
    if (s.filter && s.filter !== 'none') tex.filter++
  }

  // GRID — the container widths the layout actually snaps to, and how symmetric it is.
  const widths = new Map()
  for (const { r } of nodes) if (r.width >= 480 && r.height > 40) bump(widths, Math.round(r.width / 8) * 8)
  const centred = nodes.filter(({ s }) => s.textAlign === 'center').length

  return {
    bg: top(bg, 14), fg: top(fg, 10), bd: top(bd, 8), intent: top(intent, 12), ctaBg: top(ctaBg, 6),
    ramp: [...ramp.entries()].sort((a, b) => b[1].chars - a[1].chars).slice(0, 14).map(([k, v]) => ({ k, ...v })),
    families: top(families, 6),
    // `status` matters: an `unloaded` face is declared but never actually used on this page, so it
    // belongs in the reference card as noise, not as part of the type pairing.
    fontFaces: [...document.fonts].map((f) => `${f.family} ${f.weight} ${f.style}${f.status === 'loaded' ? '' : ` (${f.status})`}`)
      .filter((v, i, a) => a.indexOf(v) === i).slice(0, 24),
    measures, space: top(space, 14), radius: top(radius, 8), shadow: top(shadow, 8),
    tex, widths: top(widths, 6), centred, nodeCount: nodes.length,
    viewportBg: getComputedStyle(document.documentElement).backgroundColor,
    title: document.title,
  }
}

/** Motion, read BEFORE the animation freeze — the freeze overwrites every property below. */
function readMotion() {
  const bump = (map, k, n = 1) => k && map.set(k, (map.get(k) || 0) + n)
  const top = (map, n) => [...map.entries()].sort((a, b) => b[1] - a[1]).slice(0, n)
  const dur = new Map(); const ease = new Map(); const prop = new Map(); let animated = 0
  for (const e of document.querySelectorAll('body *')) {
    if (!e.getClientRects().length) continue
    const s = getComputedStyle(e)
    const ds = s.transitionDuration.split(',').map((d) => Math.round(parseFloat(d) * 1000))
    const es = s.transitionTimingFunction.split(/,(?![^(]*\))/).map((x) => x.trim())
    const ps = s.transitionProperty.split(',').map((x) => x.trim())
    ds.forEach((d, i) => { if (d > 0) { bump(dur, d); bump(ease, es[i % es.length]); bump(prop, ps[i % ps.length]) } })
    if (s.animationName !== 'none') { animated++; for (const d of s.animationDuration.split(',')) { const n = Math.round(parseFloat(d) * 1000); if (n > 0) bump(dur, n) } }
  }
  return { dur: top(dur, 10), ease: top(ease, 6), prop: top(prop, 8), animated }
}

/** Click through a cookie/consent wall in any frame, piercing open shadow roots. */
async function dismissConsent(page) {
  const SELECTORS = ['#onetrust-accept-btn-handler', '#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll',
    '#CybotCookiebotDialogBodyButtonAccept', '#truste-consent-button', '#sp-cc-accept', '#uc-btn-accept-banner',
    '.optanon-allow-all', '.osano-cm-accept-all', '.cky-btn-accept', '.cc-btn.cc-allow', '.sp_choice_type_11',
    '[data-testid="uc-accept-all-button"]', 'button[id*="accept" i]', 'button[class*="accept" i]',
    'button[id*="agree" i]', 'button[class*="agree" i]', '[aria-label*="Accept" i]']
  const AFFIRM = /^(accept|allow|agree|i agree|got it|ok|okay|understood)\b/i
  const REJECT = /\b(reject|decline|deny|manage|settings|preferences|customi[sz]e|necessary only)\b/i
  for (const frame of page.frames()) {
    try {
      const hit = await frame.evaluate(({ SELECTORS, AFFIRM, REJECT }) => {
        // Only act on a surface that says it is about consent — otherwise a plain "OK" or
        // "Continue" button somewhere on the page gets clicked and the page navigates away.
        if (!/cookie|consent|gdpr|privacy|tracking/i.test((document.body?.innerText || '').slice(0, 4000))) return null
        const roots = [document]; let budget = 4000
        for (let i = 0; i < roots.length && budget > 0; i++) {
          let all = []; try { all = [...roots[i].querySelectorAll('*')] } catch { continue }
          for (const el of all) { if (budget-- <= 0) break; if (el.shadowRoot) roots.push(el.shadowRoot) }
        }
        for (const root of roots) for (const sel of SELECTORS) {
          let el; try { el = root.querySelector(sel) } catch { continue }
          if (el && el.getClientRects().length) { el.click(); return sel }
        }
        const aff = new RegExp(AFFIRM.source, AFFIRM.flags); const rej = new RegExp(REJECT.source, REJECT.flags)
        for (const root of roots) for (const el of root.querySelectorAll('button,a[role="button"]')) {
          const t = (el.textContent || '').trim()
          if (t && aff.test(t) && !rej.test(t) && el.getClientRects().length) { el.click(); return `text:${t.slice(0, 24)}` }
        }
        return null
      }, { SELECTORS, AFFIRM: { source: AFFIRM.source, flags: AFFIRM.flags }, REJECT: { source: REJECT.source, flags: REJECT.flags } })
      if (hit) return hit
    } catch { /* detached frame, cross-origin without access, or navigation mid-evaluate */ }
  }
  return null
}

/* ── drive the page ───────────────────────────────────────────────────────────────────────── */

const browser = await chromium.launch()
// `reducedMotion` MUST be explicit. Left to the host, a machine that prefers reduced motion makes
// every duration collapse — dembrandt reports `0.001s ×950` for a page whose real transitions are
// 150ms, and the number looks perfectly plausible.
const page = await browser.newPage({ viewport: { width: vw, height: vh }, colorScheme: theme, reducedMotion: 'no-preference', deviceScaleFactor: 1 })

// The authored token layer, straight out of the stylesheets. A site with a real design system
// leaks it here — this is the highest-yield single signal on the page, and it needs no DOM walk.
const cssText = []
page.on('response', async (res) => {
  const ct = res.headers()['content-type'] || ''
  if (!ct.includes('text/css')) return
  try { cssText.push(await res.text()) } catch { /* redirect or aborted body */ }
})

// networkidle is the right target and the wrong guarantee: analytics beacons, polling and video
// keep a real marketing site permanently busy. Degrade to `load` + a settle window rather than
// reporting nothing, and say which one produced the numbers.
let waited = 'networkidle'
try {
  await page.goto(url, { waitUntil: 'networkidle', timeout: 30_000 })
} catch {
  waited = 'load + 3s settle'
  try {
    await page.goto(url, { waitUntil: 'load', timeout: 30_000 })
    await page.waitForTimeout(3000)
  } catch (e) {
    console.error(`✗ ${url} never loaded: ${e.message.split('\n')[0]}`)
    await browser.close(); process.exit(3)
  }
}
// A cookie wall is a full-viewport surface with its own palette and its own type. Leave it up and
// the report describes the consent vendor's design, not the site's. Sweep every frame — CMPs are
// routinely iframed (Sourcepoint, TrustArc, Quantcast) — and only click affirmative labels.
const consent = await dismissConsent(page)
if (consent) await page.waitForTimeout(800)

// A stepped scroll to the bottom and back, not one jump: without it the census sees only the hero
// and the type ramp collapses to three sizes, because everything below the fold is lazy-mounted or
// still hidden behind a scroll-reveal.
for (const f of [0.25, 0.5, 0.75, 1, 0]) {
  await page.evaluate((frac) => window.scrollTo(0, document.body.scrollHeight * frac), f)
  await page.waitForTimeout(400)
}
await page.waitForTimeout(800)
try { await page.evaluate(() => document.fonts.ready) } catch { /* no font loading API */ }
// `unloaded` is the resting state of a declared-but-unused face, not a problem. Only `loading`
// and `error` mean the type table might be reporting a fallback instead of the brand face.
const fontsReady = await page.evaluate(() => !document.fonts ? true
  : ![...document.fonts].some((f) => f.status === 'loading' || f.status === 'error'))

const inline = await page.evaluate(() => [...document.querySelectorAll('style')].map((s) => s.textContent).join('\n'))

// PASS 1 — motion, read live. It must happen before the freeze below, which rewrites exactly the
// properties this pass reads.
const motion = await page.evaluate(readMotion)

// PASS 2 — everything else, read frozen. A hero that cross-fades or a swatch that cycles reports a
// different computed colour on every run; driving animations to their final frame and holding it
// makes the palette reproducible. (The technique is dembrandt's; the reason to split the passes is
// that it destroys the motion numbers.)
await page.addStyleTag({ content: `*, *::before, *::after { animation-duration: 1ms !important; animation-delay: 0ms !important; animation-iteration-count: 1 !important; animation-fill-mode: forwards !important; transition-duration: 1ms !important; transition-delay: 0ms !important; }` })
await page.waitForTimeout(300)
const m = { ...(await page.evaluate(measure)), ...motion }
await browser.close()

/* ── the authored layer: custom properties + @font-face, mined out of the CSS text ────────── */

const allCss = cssText.join('\n') + '\n' + inline
const customProps = new Map()
for (const [, name, value] of allCss.matchAll(/(--[\w-]+)\s*:\s*([^;{}]{1,120});/g))
  if (!customProps.has(name)) customProps.set(name, value.trim())
// `var(--space-3, 12px)` declares a value that may appear in no rule anywhere: the fallback at the
// call site is often the only place a build leaves its geometry scale in plain text. Framer's
// dimension scale is recoverable this way and by no other CSS route.
for (const [, name, fallback] of allCss.matchAll(/var\(\s*(--[\w-]+)\s*,\s*([^),;]{1,60})\)/g))
  if (!customProps.has(name)) customProps.set(name, `${fallback.trim()}   /* from a var() fallback */`)
// A site that ships Tailwind's or Panda's whole default palette as custom properties leaks 250
// tokens that say nothing about its brand. Brand-named tokens (`--accent-*`, `--brand-*`) do not
// match this and survive. Regex from dembrandt's custom-property filter.
const FRAMEWORK_DUMP = /^--(?:tw-)?colors?-(?:slate|gray|grey|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)-(?:50|\d00|950)$|^--(?:tw-)?colors?-(?:transparent|current|black|white|inherit)$/
const designProps = [...customProps.entries()].filter(([n]) => !FRAMEWORK_DUMP.test(n) &&
  /color|bg|background|surface|fg|foreground|text|border|accent|brand|primary|secondary|muted|radius|shadow|space|spacing|gap|font|size|weight|leading|tracking|ease|duration|transition/i.test(n))
const dumped = [...customProps.keys()].filter((n) => FRAMEWORK_DUMP.test(n)).length
const faceSrc = [...allCss.matchAll(/@font-face\s*{[^}]*?font-family\s*:\s*['"]?([^;'"]+)['"]?[^}]*?}/gi)]
  .map((x) => x[1].trim()).filter((v, i, a) => a.indexOf(v) === i)

/* ── derive: the six mechanics + the five dials ───────────────────────────────────────────── */

const colours = (rows) => rows.map(([str, w]) => ({ raw: str, w, c: parseColor(str) })).filter((x) => x.c)
const dedupe = (rows) => {
  const seen = new Map()
  for (const r of rows) { const k = key(r.c); const cur = seen.get(k); if (cur) cur.w += r.w; else seen.set(k, { ...r }) }
  return [...seen.values()].sort((a, b) => b.w - a.w)
}
const bgc = dedupe(colours(m.bg)); const fgc = dedupe(colours(m.fg)); const bdc = dedupe(colours(m.bd))

const surface = bgc[0]
const isDark = surface && surface.c.L < 0.5
// An accent is the MOST SATURATED colour, not the most painted one — 60-30-10 makes scarcity its
// defining property. Ranking chromatic backgrounds by area finds a brand *surface* (Stripe's navy
// section) and misses the actual accent (Stripe's blurple, 0.2% of the page).
// Alpha under 0.5 is a status tint or a wash over the surface, never the accent itself — and it
// carries the *tinted* hue at full chroma, so it outranks the real accent unless excluded.
const solid = (rows) => rows.filter((x) => x.c.a >= 0.5)
// The accent, in three falling tiers of evidence: a repeated CTA fill (the site said so), then
// the highest-intent chromatic colour (the markup said so), then the most saturated one (a guess).
const ctaAccent = dedupe(colours(m.ctaBg.filter(([, n]) => n >= 2))).map((x) => bgc.find((b) => key(b.c) === key(x.c)) || x)
  .filter((x) => x.c.C >= 0.05 && x.c.a >= 0.5)[0]
const intentAccent = dedupe(colours(m.intent)).filter((x) => x.c.C >= 0.06 && x.c.a >= 0.5)
  .sort((a, b) => b.w - a.w)[0]
const byChroma = (rows) => solid(rows).filter((x) => x.c.C >= 0.06).sort((a, b) => b.c.C - a.c.C || b.w - a.w)
const accentBasis = ctaAccent ? 'repeated CTA fill' : intentAccent ? 'brand-intent markup' : 'highest chroma (weakest evidence)'
const accentRaw = ctaAccent || intentAccent || byChroma(bgc)[0] || byChroma(fgc)[0] || null
const accent = accentRaw && (bgc.find((x) => key(x.c) === key(accentRaw.c)) || accentRaw)
const brandSurface = solid(bgc).find((x) => x.c.C >= 0.03 && (!accent || key(x.c) !== key(accent.c))) || null
const tints = bgc.filter((x) => x.c.a < 0.5 && x.c.C >= 0.04).slice(0, 4)
const neutrals = bgc.filter((x) => x.c.C < 0.04).slice(0, 5)

// Weight every histogram by USE COUNT, never by distinct value: a design system is what the page
// paints a thousand times, and a long tail of one-off values would otherwise outvote it.
const spaceTotal = m.space.reduce((n, [, c]) => n + c, 0)
const onGrid = (u) => m.space.filter(([v]) => v % u === 0).reduce((n, [, c]) => n + c, 0) / Math.max(1, spaceTotal)
const unit = [8, 6, 5, 4, 3, 2].find((u) => onGrid(u) >= 0.8) || 1
const gridShare = onGrid(unit)
const radiusNumeric = m.radius.filter(([r]) => r !== 'pill/circle')
const radiusMode = radiusNumeric[0]?.[0] ?? 0
const pillCount = m.radius.find(([r]) => r === 'pill/circle')?.[1] ?? 0
const weighted = (rows) => rows.flatMap(([v, n]) => Array(Math.min(n, 500)).fill(v)).sort((a, b) => a - b)
const durAll = weighted(m.dur)
const durMedian = durAll.length ? durAll[Math.floor(durAll.length / 2)] : null
// UI feedback and ambient/decorative loops are different budgets; the skill caps only the first.
const durUi = weighted(m.dur.filter(([d]) => d <= 1000))
const durUiMedian = durUi.length ? durUi[Math.floor(durUi.length / 2)] : null
const measureMed = m.measures.length ? m.measures.sort((a, b) => a - b)[Math.floor(m.measures.length / 2)] : null
const bodyRow = m.ramp.find((r) => +r.k.split('/')[0] >= 13 && +r.k.split('/')[0] <= 20) || m.ramp[0]
const bodySize = bodyRow ? +bodyRow.k.split('/')[0] : null

const texScore = m.tex.svgNoise + m.tex.image ? 2 : m.tex.gradient + m.tex.backdropBlur + m.tex.blend + m.tex.filter > 6 ? 1 : 0
const dials = {
  TEXTURE_LEVEL: texScore,
  VISUAL_DENSITY: bodySize === null ? '?' : bodySize <= 14 ? 'compact' : bodySize >= 17 ? 'spacious' : 'comfortable',
  GRID_DISCIPLINE: m.centred / Math.max(1, m.nodeCount) > 0.12 ? 'centred / symmetric' : 'asymmetric or left-anchored',
  MOTION_INTENSITY: durUiMedian === null ? 'none measured' : durUiMedian <= 150 ? 'snappy' : durUiMedian <= 300 ? 'moderate' : 'slow',
  DESIGN_VARIANCE: `${m.radius.length}+ radius steps · ${m.shadow.length}+ shadow recipes · ${m.ramp.length}+ type rows (each list is truncated — read the tables)`,
}

/* ── report ───────────────────────────────────────────────────────────────────────────────── */

const table = (rows) => rows.map((r) => `| ${r.join(' | ')} |`).join('\n')
const pct = (w, tot) => `${((w / Math.max(1, tot)) * 100).toFixed(1)}%`
const bgTotal = bgc.reduce((n, x) => n + x.w, 0)

const md = `# Reference card — ${m.title || url}

\`${url}\` · ${vw}×${vh} · \`prefers-color-scheme: ${theme}\` · ${m.nodeCount} visible elements
Waited for ${waited}${consent ? ` · dismissed a consent wall (\`${consent}\`)` : ''}${fontsReady ? '' : ' · **fonts were still loading — the type table may name fallbacks**'}
Measured, not judged. **This is an input to differentiation, not a theme to ship**
(→ \`references/reference-mining.md\` § The differentiation rule).

## 1. Palette with roles

Rendered as **${isDark ? 'DARK' : 'LIGHT'}**; surface L = ${surface ? surface.c.L.toFixed(3) : '?'}.

| role | OKLCH | share of painted area | as served |
|---|---|---|---|
${table([...new Set([surface, accent, brandSurface, ...bgc.slice(0, 8)])].filter(Boolean).slice(0, 9)
  .map((x, i) => [x === surface ? '**surface**' : x === accent ? '**accent**' : x === brandSurface ? '**brand surface**' : `bg ${i}`, fmt(x.c), pct(x.w, bgTotal), '`' + x.raw + '`']))}

Text: ${fgc.slice(0, 4).map((x) => fmt(x.c)).join(' · ') || '—'}
Border: ${bdc.slice(0, 3).map((x) => fmt(x.c)).join(' · ') || '— (borderless)'}
Accent hue: ${accent ? `**${accent.c.H.toFixed(0)}°** at C ${accent.c.C.toFixed(3)}, on ${pct(accent.w, bgTotal)} of painted area — identified by ${accentBasis}` : 'none above C 0.06 — this palette is achromatic'}
Brand surface (the 30% band): ${brandSurface ? `${fmt(brandSurface.c)} at ${pct(brandSurface.w, bgTotal)}` : '— none; neutral surfaces only'}
Chromatic backgrounds: ${bgc.filter((x) => x.c.C >= 0.06).length} of ${bgc.length} distinct · neutral steps: ${neutrals.length}
Tints (α<0.5 washes — status/hover layers, not palette entries): ${tints.length ? tints.map((x) => fmt(x.c)).join(' · ') : '— none'}

## 2. Type pairing and weights

Loaded faces: ${m.fontFaces.length ? m.fontFaces.map((f) => '`' + f + '`').join(' · ') : '— none (system stack)'}
\`@font-face\` families in CSS: ${faceSrc.length ? faceSrc.slice(0, 12).map((f) => '`' + f + '`').join(' · ') + (faceSrc.length > 12 ? ` … +${faceSrc.length - 12} more (a font *gallery*, not a type system — read the "stacks in use" line instead)` : '') : '—'}
Stacks in use: ${m.families.map(([f, n]) => `\`${f.split(',')[0].replace(/["']/g, '')}\` (${n} chars)`).join(' · ')}

| size/weight/line-height/tracking/transform | uses | sample |
|---|---|---|
${table(m.ramp.map((r) => ['`' + r.k + '`', r.n, r.sample.replace(/\|/g, '\\|') || '—']))}

Measure: ${measureMed ? `${measureMed}ch median across ${m.measures.length} paragraphs` : 'no paragraph over 120 chars found'}

## 3. Radius

${m.radius.map(([r, n]) => `\`${r === 'pill/circle' ? r : r + 'px'}\` ×${n}`).join(' · ') || 'all square'}
Base **${radiusMode ? radiusMode + 'px' : 'square'}** (most-used numeric step) · pill/circle on ${pillCount} corners

## 4. Elevation recipe

${m.shadow.length ? m.shadow.map(([s, n]) => `- ×${n} \`${s}\``).join('\n') : '- none — this design is border-first'}
Borders present on ${bdc.length} distinct colours.

## 5. Grid / spacing / measure

Inferred base unit: **${unit}px** (${(gridShare * 100).toFixed(0)}% of uses) · on a 4px grid: ${(onGrid(4) * 100).toFixed(0)}% · 8px: ${(onGrid(8) * 100).toFixed(0)}%${onGrid(4) < 0.8 ? '\nThis reference is off the 4px grid the skill mandates — read the histogram for which values escaped, and do not carry them over.' : ''}
${m.space.filter(([v]) => v % 4 !== 0).length ? `Off-4px values: ${m.space.filter(([v]) => v % 4 !== 0).map(([v, n]) => `${v}px×${n}`).join(' · ')}` : 'Every measured spacing value is on the 4px grid.'}
Spacing histogram: ${m.space.map(([v, n]) => `${v}px×${n}`).join(' · ')}
Container widths: ${m.widths.map(([w, n]) => `${w}px×${n}`).join(' · ')}
Centred text nodes: ${m.centred} / ${m.nodeCount}

## 6. Motion

Durations: ${m.dur.map(([d, n]) => `${d}ms×${n}`).join(' · ') || '— none'}
Median: **${durUiMedian ?? '—'}ms** across UI transitions ≤1s${durMedian !== durUiMedian ? ` · ${durMedian}ms including ambient loops` : ''}
Curves: ${m.ease.map(([e, n]) => `\`${e}\`×${n}`).join(' · ') || '—'}
Animated properties: ${m.prop.map(([p, n]) => `${p}×${n}`).join(' · ') || '—'}
Keyframe animations running: ${m.animated}

## Dials, measured

${Object.entries(dials).map(([k, v]) => `- **${k}** — ${v}`).join('\n')}
Texture counts: ${Object.entries(m.tex).map(([k, v]) => `${k} ${v}`).join(' · ')}

## Authored token layer (${designProps.length} design-relevant custom properties of ${customProps.size} total${dumped ? `; ${dumped} framework-default palette entries dropped` : ''})

${designProps.length
  ? '```css\n' + designProps.slice(0, 60).map(([n, v]) => `${n}: ${v};`).join('\n') + '\n```'
  : '_No CSS custom properties reached — the site inlines values, ships no design system, or serves CSS this run did not see._'}
`

const report = { url, viewport: `${vw}x${vh}`, theme, title: m.title, isDark,
  captured: { waitedFor: waited, consentDismissed: consent, fontsReady },
  palette: { surface: surface && fmt(surface.c), accent: accent && fmt(accent.c), accentBasis, accentShare: accent && accent.w / Math.max(1, bgTotal), brandSurface: brandSurface && fmt(brandSurface.c), backgrounds: bgc.slice(0, 8).map((x) => ({ oklch: fmt(x.c), weight: x.w, raw: x.raw })), text: fgc.slice(0, 4).map((x) => fmt(x.c)), border: bdc.slice(0, 3).map((x) => fmt(x.c)) },
  type: { faces: m.fontFaces, fontFaceFamilies: faceSrc, stacks: m.families, ramp: m.ramp, measureCh: measureMed },
  radius: { histogram: m.radius, base: radiusMode, pillCorners: pillCount },
  shadow: m.shadow, spacing: { unit, gridShare, histogram: m.space, containers: m.widths, centred: m.centred },
  motion: { durations: m.dur, easings: m.ease, properties: m.prop, keyframes: m.animated, medianUiMs: durUiMedian, medianAllMs: durMedian },
  texture: m.tex, dials, customProperties: Object.fromEntries(designProps.slice(0, 200)), nodeCount: m.nodeCount }

if (out) {
  mkdirSync(dirname(`${out}.md`), { recursive: true })
  writeFileSync(`${out}.md`, md)
  writeFileSync(`${out}.json`, JSON.stringify(report, null, 2))
  console.log(`✓ wrote ${out}.md and ${out}.json`)
} else if (asJson) {
  console.log(JSON.stringify(report, null, 2))
} else {
  console.log(md)
}
