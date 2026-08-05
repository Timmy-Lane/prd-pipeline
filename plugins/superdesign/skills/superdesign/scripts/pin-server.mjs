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
    res.end(readFileSync(overlayPath))
    return
  }

  if (req.method === 'GET' && req.url === '/') {
    res.writeHead(200, { 'content-type': 'text/plain' })
    res.end(`pin-server\npins → ${outFile}\ncaught: ${n}\n`)
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
      const t = pin?.identity?.slot ?? pin?.identity?.tag ?? '?'
      const first = Object.entries(pin?.resolved ?? {}).find(([, r]) => r.tokens?.length)
      const tok = first ? `${first[0]} → ${first[1].tokens[0].token}` : 'no token resolved'
      console.log(`  ${String(n).padStart(3)}  [${t}] ${JSON.stringify(pin?.said ?? '')}  ·  ${tok}`)
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
