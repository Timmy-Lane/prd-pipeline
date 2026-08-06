#!/usr/bin/env node
// pin-server — serves pin-overlay.js and catches the pins it posts.
//
// Optional. The overlay works with nothing running: pins accumulate in window.__sdPins and an
// agent reads them back out of the tab. This exists for the case the overlay cannot cover — a
// pin has to survive a reload, and pins taken while nobody is watching have to queue somewhere.
//
//   node scripts/pin-server.mjs --dir ~/Documents/GitHub/socialAI
//   node scripts/pin-server.mjs --dir ~/Documents/GitHub/foji --port 7332
//
// Then, in the dev page only:
//   <script src="http://127.0.0.1:7332/pin-overlay.js"></script>
//
// Pins append to <dir>/.superdesign/pins.jsonl, one JSON object per line. Read them with
// scripts/pin-report.mjs. Binds 127.0.0.1 only — it is a dev sink, never a service.
//
// That file is an append-only LOG, not a list: an edit and a delete arrive as new records carrying
// the same `id`, so the current set of pins is a fold over it. GET /__sd_pins serves that fold, so
// nothing but this file and pin-report.mjs ever has to know the difference.
//
// It accepts JSON from any localhost origin, which is the whole point (the page is on :3000 or
// :1420, the sink is on :7332). It therefore treats every field as untrusted: the body is size-
// capped, the parse is guarded, and the destination path is fixed at startup — nothing in a
// request can influence where a byte lands.

import { createServer } from 'node:http'
import { appendFileSync, mkdirSync, readFileSync, existsSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const HERE = dirname(fileURLToPath(import.meta.url))
const MAX_BODY = 512 * 1024 // a pin is ~2-6 KB; 512 KB is 100x headroom and still bounded

const arg = (name, fallback) => {
  const i = process.argv.indexOf(`--${name}`)
  return i > -1 && process.argv[i + 1] ? process.argv[i + 1] : fallback
}

const port = Number(arg('port', 7332))
const targetDir = resolve(arg('dir', process.cwd()).replace(/^~/, process.env.HOME ?? '~'))
const outDir = join(targetDir, '.superdesign')
const outFile = join(outDir, 'pins.jsonl')
const overlayPath = join(HERE, 'pin-overlay.js')

if (!existsSync(overlayPath)) {
  console.error(`pin-server: cannot find ${overlayPath}`)
  process.exit(1)
}
mkdirSync(outDir, { recursive: true })

// Replay the log. A record with no `id` predates the log format and folds through unchanged, so
// every pins.jsonl written before today still reads. The same fold lives in pin-report.mjs — two
// consumers, ~14 lines each; a third is when it becomes a module.
const fold = (lines) => {
  const order = []
  const byId = new Map()
  let legacy = 0
  for (const raw of lines) {
    let r
    try {
      r = JSON.parse(raw)
    } catch {
      continue
    }
    if (!r.id) {
      // A key no UUID can collide with, so a legacy pin keeps its slot in document order.
      const k = ` legacy${legacy++}`
      order.push(k)
      byId.set(k, r)
      continue
    }
    const op = r.op ?? 'pin'
    if (op === 'pin') {
      if (!byId.has(r.id)) order.push(r.id)
      byId.set(r.id, r)
    } else if (op === 'edit') {
      const p = byId.get(r.id)
      if (p) {
        p.said = r.said
        p.editedAt = r.at
      }
    } else if (op === 'delete') {
      byId.delete(r.id)
    }
  }
  return order.map((k) => byId.get(k)).filter(Boolean)
}

// Any localhost port is a legitimate dev origin; anything else is not.
const allowOrigin = (origin) => {
  if (!origin) return '*'
  try {
    const u = new URL(origin)
    return ['localhost', '127.0.0.1', '[::1]', 'tauri.localhost'].includes(u.hostname) ? origin : null
  } catch {
    return null
  }
}

const cors = (res, origin) => {
  const allowed = allowOrigin(origin)
  if (!allowed) return false
  res.setHeader('access-control-allow-origin', allowed)
  res.setHeader('access-control-allow-headers', 'content-type')
  res.setHeader('access-control-allow-methods', 'GET,POST,OPTIONS')
  return true
}

let n = 0

const server = createServer((req, res) => {
  const origin = req.headers.origin
  if (!cors(res, origin)) {
    res.writeHead(403).end('bad origin')
    return
  }
  if (req.method === 'OPTIONS') {
    res.writeHead(204).end()
    return
  }

  if (req.method === 'GET' && req.url.startsWith('/pin-overlay.js')) {
    res.writeHead(200, { 'content-type': 'text/javascript; charset=utf-8', 'cache-control': 'no-store' })
    // Tell the overlay where to post. Without this it falls back to the 7332 literal, and any run
    // started with --port silently drops every pin into a closed socket.
    res.end(`window.__sdPinSink='http://127.0.0.1:${port}';\n${readFileSync(overlayPath)}`)
    return
  }

  if (req.method === 'GET' && req.url === '/') {
    res.writeHead(200, { 'content-type': 'text/plain' })
    res.end(`pin-server\npins → ${outFile}\ncaught: ${n}\n`)
    return
  }

  // The inventory the overlay hydrates from on every page load. `resolved` is stripped: the list
  // shows a sentence and an element, never a resolution, and it is ~4 KB of the ~4.5 KB a pin
  // weighs — 200 unstripped pins would be most of a megabyte on every reload. No path, query or
  // body field reaches the filesystem here; outFile is still the one fixed at startup.
  if (req.method === 'GET' && req.url === '/__sd_pins') {
    let lines = []
    try {
      lines = readFileSync(outFile, 'utf8').split('\n').filter(Boolean)
    } catch {
      /* nothing pinned yet — an empty inventory, not an error */
    }
    res.writeHead(200, { 'content-type': 'application/json', 'cache-control': 'no-store' })
    res.end(JSON.stringify(fold(lines).map(({ resolved, ...rest }) => rest)))
    return
  }

  if (req.method === 'POST' && req.url.startsWith('/__sd_pin')) {
    let body = ''
    let over = false
    req.on('data', (c) => {
      body += c
      if (body.length > MAX_BODY) {
        over = true
        req.destroy()
      }
    })
    req.on('end', () => {
      if (over) return
      let pin
      try {
        pin = JSON.parse(body)
      } catch {
        res.writeHead(400).end('bad json')
        return
      }
      appendFileSync(outFile, `${JSON.stringify(pin)}\n`)
      n++
      // An edit and a delete carry no identity and no resolution, so the pin line would print them
      // as `[?] "" · no token resolved` — three fields of nothing that read like a broken pin.
      const op = pin?.op ?? 'pin'
      if (op === 'pin') {
        const t = pin?.identity?.slot ?? pin?.identity?.tag ?? '?'
        const first = Object.entries(pin?.resolved ?? {}).find(([, r]) => r.tokens?.length)
        const tok = first ? `${first[0]} → ${first[1].tokens[0].token}` : 'no token resolved'
        console.log(`  ${String(n).padStart(3)}  [${t}] ${JSON.stringify(pin?.said ?? '')}  ·  ${tok}`)
      } else {
        const said = op === 'edit' ? `  →  ${JSON.stringify(pin?.said ?? '')}` : ''
        console.log(`  ${String(n).padStart(3)}  ${op} ${String(pin?.id ?? '?').slice(0, 6)}${said}`)
      }
      res.writeHead(204).end()
    })
    return
  }

  res.writeHead(404).end('nope')
})

server.listen(port, '127.0.0.1', () => {
  console.log(`pin-server  http://127.0.0.1:${port}`)
  console.log(`  overlay   http://127.0.0.1:${port}/pin-overlay.js`)
  console.log(`  pins      ${outFile}`)
  console.log(`\n  <script src="http://127.0.0.1:${port}/pin-overlay.js"></script>\n`)
})
