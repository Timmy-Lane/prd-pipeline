#!/usr/bin/env node
// check-pointers — every path and every in-file anchor the skill mentions must resolve.
//
// A skill is a graph of pointers. One dead edge and the model either opens nothing or
// invents the contents; this repo has already shipped one dead `examples/` pointer and
// one comment claiming a grep that did not exist. Cheap to check, so check it.
//
//   node scripts/check-pointers.mjs            # skill + scripts + evals
//   node scripts/check-pointers.mjs <dir…>     # anything else
//
// Exit 0 = every pointer resolves. Non-zero = the number of dead pointers.

import { readFileSync, existsSync, statSync } from 'node:fs'
import { readdirSync } from 'node:fs'
import { join, dirname, resolve, extname } from 'node:path'

const ROOT = resolve(new URL('..', import.meta.url).pathname)
const ROOTS = process.argv.slice(2).length
  ? process.argv.slice(2)
  : ['.claude/skills/superdesign', 'scripts', 'evals']

function walk(dir, out = []) {
  for (const e of readdirSync(dir, { withFileTypes: true })) {
    if (e.name === 'node_modules' || e.name.startsWith('.git')) continue
    const p = join(dir, e.name)
    e.isDirectory() ? walk(p, out) : out.push(p)
  }
  return out
}

const files = ROOTS.flatMap((r) => {
  const abs = resolve(ROOT, r)
  if (!existsSync(abs)) return []
  return statSync(abs).isDirectory() ? walk(abs) : [abs]
}).filter((f) => ['.md', '.mjs', '.js', '.sh', '.css'].includes(extname(f)))

// Only count a path when it is written AS a pointer — inside backticks or as a
// markdown link target. Free prose and regex fragments produce path-shaped noise
// (`src/`, `s/`, `tokens.md/theme.css`) that would drown the real findings.
const BACKTICKED = /`([^`\n]+)`/g
const MDLINK = /\]\(([^)#\s]+)\)/g
const KNOWN_EXT = /\.(md|mjs|js|ts|tsx|css|sh|json)$/
const DOMAINISH = /^[\w-]+(\.[\w-]+)+\//   // vercel.com/design.md — a URL missing its scheme
// Paths that live in the CONSUMER's project, not in this repo. A cookbook recipe saying
// "put this in `app/globals.css`" is a correct instruction, not a dead pointer.
const CONSUMER = /^(app|src|components|lib|styles|public|pages|hooks)\//

function pointerCandidates(body, isCode) {
  // Strip fenced code blocks: they hold regexes, shell fragments and example paths
  // that are illustrations, not references.
  const prose = body.replace(/```[\s\S]*?```/g, '')
  const src = isCode
    ? prose.split('\n').filter((l) => !/^\s*(\/\/|#)/.test(l)).join('\n')
    : prose
  const out = new Set()
  for (const m of src.matchAll(BACKTICKED)) out.add(m[1])
  for (const m of src.matchAll(MDLINK)) out.add(m[1])
  return [...out]
}

// Slug a heading the way GitHub does. The one non-obvious rule: whitespace runs are
// NOT collapsed. Dropping a `—`, `&`, `/` or `+` from between two words leaves two
// spaces, which become two hyphens — `## 1. Color primitives — the ramps` is
// `#1-color-primitives--the-ramps`. Collapsing them marks every such anchor dead.
const slug = (h) =>
  h.toLowerCase().trim()
    .replace(/[`*_~]/g, '')
    .replace(/[^\w\s-]/g, '')
    .trim()
    .replace(/ /g, '-')

const anchorsOf = (body) =>
  new Set(body.split('\n').filter((l) => /^#{1,6}\s/.test(l)).map((l) => slug(l.replace(/^#+\s*/, ''))))

const dead = []
let checkedPaths = 0
let checkedAnchors = 0

for (const f of files) {
  const body = readFileSync(f, 'utf8')
  const here = dirname(f)
  const anchors = anchorsOf(body)

  // 1. In-file anchors: [text](#anchor). Same filter as paths — a `//` line in a
  //    script is documentation about the syntax, not a link that has to resolve.
  const isCodeFile = ['.mjs', '.js', '.sh', '.css'].includes(extname(f))
  const linkSrc = isCodeFile
    ? body.split('\n').filter((l) => !/^\s*(\/\/|#)/.test(l)).join('\n')
    : body
  for (const m of linkSrc.matchAll(/\]\(#([^)]+)\)/g)) {
    checkedAnchors++
    if (!anchors.has(m[1].toLowerCase())) {
      dead.push([f, `anchor #${m[1]} — no heading slugs to it`])
    }
  }

  // 2. Paths. Resolve against the file's dir, the skill root, and the repo root —
  //    a reference legitimately writes `references/tokens.md` from inside references/.
  const isCode = ['.mjs', '.js', '.sh', '.css'].includes(extname(f))
  for (const cand of pointerCandidates(body, isCode)) {
    const raw = cand.trim().replace(/[.,;:)\]]+$/, '')
    if (!raw.includes('/')) continue
    if (!KNOWN_EXT.test(raw)) continue          // only extension-bearing pointers
    if (/^(https?:|\/\/|\w+:)/.test(raw)) continue
    if (DOMAINISH.test(raw) || CONSUMER.test(raw)) continue
    if (/[ *?<>|$(){}]/.test(raw)) continue     // globs, shell expansions, prose
    if (raw.startsWith('node_modules/') || raw.startsWith('@')) continue
    const skillRoot = f.includes('/skills/superdesign/')
      ? f.slice(0, f.indexOf('/skills/superdesign/') + '/skills/superdesign'.length)
      : ROOT
    const candidates = [resolve(here, raw), resolve(skillRoot, raw), resolve(ROOT, raw)]
    checkedPaths++
    if (candidates.some(existsSync)) continue
    // An artifact the operator creates from a committed template is not a dead pointer:
    // evals/calibration.json ships as evals/calibration.template.json.
    if (candidates.some((c) => existsSync(c.replace(/\.([^.]+)$/, '.template.$1')))) continue
    dead.push([f, `path ${raw}`])
  }
}

for (const [f, what] of dead) console.log(`  [DEAD] ${f.replace(ROOT + '/', '')} → ${what}`)
console.log(
  dead.length === 0
    ? `\n✓ pointers: all resolve (${checkedPaths} paths, ${checkedAnchors} anchors, ${files.length} files)`
    : `\n✗ pointers: ${dead.length} dead of ${checkedPaths + checkedAnchors} checked`,
)
process.exit(dead.length)
