#!/usr/bin/env node
// pin-report — turn pins into a fix brief that names the LAYER, not the node.
//
// The pin already carries the token. What it cannot know from inside the page is where that
// token is declared on disk, which other tokens share its value in the theme the user is NOT
// currently looking at, and which source file emits the class list. This does those three, then
// applies the layer decision — which is mechanical, not a judgement call:
//
//   the rule reaches >1 distinct data-slot   → TOKEN     edit the theme, everything moves together
//   exactly one data-slot                    → VARIANT   edit that component's cva table
//   exactly one node, classes differ from
//   its same-slot siblings                   → OVERRIDE  already a SKILL.md:257 defect — delete it
//
//   node scripts/pin-report.mjs --dir ~/Documents/GitHub/socialAI
//   node scripts/pin-report.mjs --dir ~/Documents/GitHub/foji --json
//
// Exit code = number of pins that resolved to no token at all. Those are the ones where the
// design has no system behind it, which is a Phase-1 finding, not a styling request.

import { readFileSync, existsSync, readdirSync, statSync } from 'node:fs'
import { join, resolve, relative, extname } from 'node:path'
import { execFileSync } from 'node:child_process'

const arg = (name, fallback) => {
  const i = process.argv.indexOf(`--${name}`)
  return i > -1 && process.argv[i + 1] && !process.argv[i + 1].startsWith('--') ? process.argv[i + 1] : fallback
}
const has = (name) => process.argv.includes(`--${name}`)

const dir = resolve(arg('dir', process.cwd()).replace(/^~/, process.env.HOME ?? '~'))
const pinFile = arg('pins', join(dir, '.superdesign', 'pins.jsonl'))

if (!existsSync(pinFile)) {
  console.error(`pin-report: no pins at ${pinFile}`)
  console.error(`  run: node scripts/pin-server.mjs --dir ${dir}`)
  process.exit(1)
}

const pins = readFileSync(pinFile, 'utf8')
  .split('\n')
  .filter(Boolean)
  .map((l) => {
    try {
      return JSON.parse(l)
    } catch {
      return null
    }
  })
  .filter(Boolean)

// ── the theme on disk ────────────────────────────────────────────────────────────────────
// The page can only see the tokens that are live right now. The file sees both modes, which is
// where the sibling trap lives: four tokens can share a value in :root and diverge under .dark,
// so the sibling set is mode-dependent and only the file knows it.

const CSS_CANDIDATES = [
  'src/app/globals.css',
  'app/globals.css',
  'src/styles/tokens.css',
  'src/index.css',
  'src/App.css',
  'styles/globals.css',
  'ds-bundle/tokens/tokens.css',
]

const themeFiles = (arg('theme', '') ? [arg('theme')] : CSS_CANDIDATES)
  .map((p) => (p.startsWith('/') ? p : join(dir, p)))
  .filter(existsSync)

// --name: value, remembering which block it was declared in.
function readTokens(file) {
  const src = readFileSync(file, 'utf8')
  const out = []
  // Track the nearest enclosing selector by brace depth. Crude, and correct for the shape every
  // Tailwind v4 theme actually has (:root { … } / .dark { … } / @theme inline { … }).
  const lines = src.split('\n')
  const stack = []
  lines.forEach((line, i) => {
    const open = line.match(/^\s*([^{}]+?)\s*\{/)
    if (open) stack.push(open[1].trim())
    const decl = line.match(/^\s*(--[\w-]+)\s*:\s*([^;]+);/)
    if (decl) {
      out.push({
        token: decl[1],
        value: decl[2].trim(),
        block: stack[stack.length - 1] ?? '?',
        file: relative(dir, file),
        line: i + 1,
      })
    }
    const closes = (line.match(/\}/g) ?? []).length
    for (let c = 0; c < closes; c++) stack.pop()
  })
  return out
}

const theme = themeFiles.flatMap(readTokens)
const byName = new Map()
for (const t of theme) {
  if (!byName.has(t.token)) byName.set(t.token, [])
  byName.get(t.token).push(t)
}

// Other tokens that resolve to the same literal value, per block. Editing one and not these is a
// half-applied change: fixed on this screen, broken two routes away.
function siblingsOf(token) {
  const decls = byName.get(token) ?? []
  const out = []
  for (const d of decls) {
    for (const other of theme) {
      if (other.token === token) continue
      if (other.block !== d.block) continue
      if (other.value !== d.value) continue
      out.push({ token: other.token, block: other.block, value: other.value, line: other.line, file: other.file })
    }
  }
  return out
}

// ── where the class list came from ───────────────────────────────────────────────────────

const SRC_EXT = new Set(['.tsx', '.jsx', '.ts', '.js', '.html', '.svelte', '.vue'])
const SKIP = new Set(['node_modules', '.git', 'dist', 'build', '.next', 'out', 'src-tauri', 'target', '.superdesign'])

function sourceFiles(root, acc = [], depth = 0) {
  if (depth > 8) return acc
  let entries
  try {
    entries = readdirSync(root, { withFileTypes: true })
  } catch {
    return acc
  }
  for (const e of entries) {
    if (SKIP.has(e.name) || e.name.startsWith('.')) continue
    const p = join(root, e.name)
    if (e.isDirectory()) sourceFiles(p, acc, depth + 1)
    else if (SRC_EXT.has(extname(e.name))) acc.push(p)
  }
  return acc
}

let FILES = null
// Find the source by its rarest class. A common utility (`flex`, `p-4`) matches everywhere; the
// rarest one in the list is the fingerprint. Ties broken by fewest hits.
function locate(classes) {
  if (!classes) return []
  FILES ??= sourceFiles(dir)
  const tokens = classes
    .split(/\s+/)
    .filter((c) => c && !c.startsWith('data-') && c.length > 3)
    .sort((a, b) => b.length - a.length)
    .slice(0, 6)
  const scored = []
  for (const c of tokens) {
    const hits = []
    for (const f of FILES) {
      let src
      try {
        src = readFileSync(f, 'utf8')
      } catch {
        continue
      }
      const idx = src.indexOf(c)
      if (idx > -1) hits.push({ file: relative(dir, f), line: src.slice(0, idx).split('\n').length })
      if (hits.length > 12) break
    }
    if (hits.length) scored.push({ class: c, hits })
  }
  scored.sort((a, b) => a.hits.length - b.hits.length)
  return scored.slice(0, 2)
}

// ── the layer decision ───────────────────────────────────────────────────────────────────

function decide(prop, r, pin) {
  const blast = r.blast ?? {}
  if (blast.scope === 'inline') {
    return { layer: 'OVERRIDE', why: 'an inline style attribute — never a design decision, always a leak' }
  }
  if ((blast.slots?.length ?? 0) > 1) {
    return {
      layer: 'TOKEN',
      why: `the rule reaches ${blast.nodes} nodes across ${blast.slots.length} components (${blast.slots.join(', ')}) — moving the token moves them together`,
    }
  }
  if ((blast.slots?.length ?? 0) === 1) {
    return {
      layer: 'VARIANT',
      why: `only ${blast.slots[0]} uses this — add or edit a cva variant row rather than the shared token`,
    }
  }
  if (blast.nodes === 1) {
    return {
      layer: 'OVERRIDE',
      why: 'exactly one node and no component owns it — this is the call-site override SKILL.md:257 forbids. Delete it, add a variant.',
    }
  }
  return { layer: 'NODE', why: `${blast.nodes} nodes, no data-slot on any of them — no component boundary to hang a variant on` }
}

// ── report ───────────────────────────────────────────────────────────────────────────────

const report = []
let untokened = 0

for (const [i, pin] of pins.entries()) {
  const entry = {
    n: i + 1,
    said: pin.said,
    route: pin.route,
    theme: pin.theme,
    viewport: pin.viewport,
    identity: pin.identity,
    classes: pin.classes,
    warnings: [],
    properties: [],
    source: locate(pin.classes),
  }
  if (pin.blockedSheets) {
    entry.warnings.push(
      `${pin.blockedSheets} stylesheet(s) were unreadable in-page (cross-origin or file://) — resolution is incomplete`,
    )
  }
  const withTokens = Object.entries(pin.resolved ?? {}).filter(([, r]) => r.tokens?.length)
  if (!withTokens.length) {
    untokened++
    entry.warnings.push('no property on this element resolved to a token — the value is hard-coded, which is a Phase-1 defect, not a styling request')
  }
  for (const [prop, r] of Object.entries(pin.resolved ?? {})) {
    const d = decide(prop, r, pin)
    entry.properties.push({
      prop,
      selector: r.sel,
      context: r.ctx,
      declared: r.declared,
      computed: r.computed,
      layer: d.layer,
      why: d.why,
      blast: r.blast,
      tokens: (r.tokens ?? []).map((t) => ({
        ...t,
        onDisk: (byName.get(t.token) ?? []).map((x) => `${x.file}:${x.line} in ${x.block} = ${x.value}`),
        siblingsOnDisk: siblingsOf(t.token),
      })),
    })
  }
  report.push(entry)
}

if (has('json')) {
  console.log(JSON.stringify({ dir, themeFiles: themeFiles.map((f) => relative(dir, f)), pins: report }, null, 2))
  process.exit(untokened)
}

const B = (s) => `\x1b[1m${s}\x1b[0m`
const D = (s) => `\x1b[2m${s}\x1b[0m`
const R = (s) => `\x1b[31m${s}\x1b[0m`
const Y = (s) => `\x1b[33m${s}\x1b[0m`
const G = (s) => `\x1b[32m${s}\x1b[0m`
const layerColor = { TOKEN: G, VARIANT: Y, OVERRIDE: R, NODE: D }

console.log(`\n${B('pin-report')}  ${relative(process.cwd(), dir) || dir}`)
console.log(D(`  theme: ${themeFiles.map((f) => relative(dir, f)).join(', ') || 'none found'} (${theme.length} tokens)`))
console.log(D(`  pins:  ${pins.length}\n`))

for (const e of report) {
  const id = e.identity ?? {}
  console.log(`${B(`── ${e.n}. "${e.said}"`)}`)
  console.log(
    D(`   ${id.slot ? `[${id.slot}]` : id.tag}${id.variant ? ` variant=${id.variant}` : ''}${id.text ? `  "${id.text}"` : ''}`),
  )
  console.log(D(`   ${e.route} · ${e.theme} · ${e.viewport?.w}×${e.viewport?.h}`))
  for (const w of e.warnings) console.log(`   ${Y('!')} ${w}`)

  const interesting = e.properties.filter((p) => p.tokens.length || p.layer === 'OVERRIDE')
  for (const p of interesting) {
    const c = layerColor[p.layer] ?? D
    console.log(`   ${c(p.layer.padEnd(8))} ${B(p.prop)}  ${D(p.selector)}${p.context?.length > 1 ? D(` @ ${p.context.slice(1).join(' ')}`) : ''}`)
    console.log(D(`            ${p.why}`))
    for (const t of p.tokens) {
      console.log(`            ${G(t.token)} = ${t.value}`)
      for (const d of t.onDisk) console.log(D(`              ${d}`))
      if (t.siblingsOnDisk.length) {
        console.log(
          `              ${Y('↳ same value, will NOT move with it:')} ${t.siblingsOnDisk.map((s) => `${s.token} (${s.file}:${s.line}, ${s.block})`).join(', ')}`,
        )
      }
    }
  }
  if (e.source.length) {
    console.log(D(`   source (by rarest class "${e.source[0].class}"):`))
    for (const h of e.source[0].hits.slice(0, 4)) console.log(D(`     ${h.file}:${h.line}`))
  }
  console.log()
}

if (untokened) console.log(R(`${untokened} pin(s) resolved to no token at all.\n`))
process.exit(untokened)
