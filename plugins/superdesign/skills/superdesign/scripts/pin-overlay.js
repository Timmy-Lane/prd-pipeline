// pin-overlay — point at a rendered element, get back the TOKEN that owns it.
//
// The problem this solves is not "let the user click things". It is that a design complaint
// arrives as a sentence about a screen ("this is too loud") and gets fixed as a className patch
// on one node — which SKILL.md:257 calls a defect, not a preference. The fix almost always
// belongs one or two layers up: in the token, or in the cva variant. Nothing in a screenshot
// tells you which. The CSSOM does.
//
//   getComputedStyle CANNOT name the token: the computed value is the specified value with
//   var() already substituted, so `oklch(0.53 0.17 240)` arrives with `--primary` erased
//   (drafts.csswg.org/css-variables-1). The DECLARED value survives in CSSOM and names it
//   exactly. So: walk the sheets, find the winning rule per property, pull the var() names out
//   of the declared text, read them off :root. Measured at 1.3ms over 14 matched rules.
//
// Zero dependencies, zero build step, no framework coupling — it never asks what rendered the
// page. That is deliberate: React 19 deleted the fiber source path (facebook/react#28265), so
// every click-to-source tool built on `_debugSource` broke and React shipped no replacement.
// This one never needed it.
//
//   Delivery A (nothing to install):  paste into devtools, or have the agent inject it.
//   Delivery B (survives reloads):    node scripts/pin-server.mjs, then add to the dev page
//                                     <script src="http://127.0.0.1:7332/pin-overlay.js"></script>
//
// Alt-click an element. Type one sentence. Enter. Pins land in window.__sdPins and, when the
// sink is up, in .superdesign/pins.jsonl. Read them with scripts/pin-report.mjs.
//
// Esc cancels · Alt+↑/↓ walks the occlusion stack (label → button → card) · Alt+Shift+P toggles.

;(() => {
  if (window.__sdPinOverlay) {
    window.__sdPinOverlay.toggle()
    return
  }

  const SINK = 'http://127.0.0.1:7332/__sd_pin'
  const ACCENT = '#ff2d55'

  // Properties worth resolving. Everything a design complaint is ever actually about; anything
  // outside this set is noise that would triple the pin size for no decision value.
  const INTERESTING = new Set([
    'color', 'background-color', 'background-image', 'border-color', 'border-top-color',
    'border-bottom-color', 'border-left-color', 'border-right-color', 'border-width',
    'border-radius', 'border-top-left-radius', 'outline-color', 'outline-width',
    'box-shadow', 'opacity', 'font-family', 'font-size', 'font-weight', 'line-height',
    'letter-spacing', 'text-transform', 'padding', 'padding-top', 'padding-bottom',
    'padding-left', 'padding-right', 'margin', 'margin-top', 'margin-bottom', 'gap',
    'width', 'height', 'min-height', 'max-width', 'transition-duration',
    'transition-timing-function', 'animation-duration', 'backdrop-filter', 'filter',
  ])

  // ── CSSOM walk ─────────────────────────────────────────────────────────────────────────
  // One pass collects both halves: the rules matching THIS element, and every custom-property
  // declaration in the document. The second half is what makes the sibling-token scan possible
  // in-page — four tokens can carry a byte-identical value, and editing one silently leaves the
  // other three behind (assets/theme.css: --primary, --ring, --sidebar-primary, --sidebar-ring).

  let blockedSheets = 0

  function collect(el) {
    const hits = []
    const tokens = new Map() // "--name @ :root" -> {token, value, declaredAt}

    const walk = (rules, ctx) => {
      for (const r of rules) {
        // CSSStyleRule ALSO carries .cssRules now that CSS Nesting shipped. A naive
        // `if (r.cssRules) recurse` therefore short-circuits every style rule and matches
        // NOTHING. Test selectorText first, recurse into the nested block second.
        if (r.selectorText) {
          harvestTokens(r)
          let m = false
          try {
            m = el.matches(stripPseudoState(r.selectorText))
          } catch {
            m = false
          }
          if (m) hits.push({ sel: r.selectorText, ctx, style: r.style })
          if (r.cssRules?.length) walk(r.cssRules, m ? [...ctx, r.selectorText] : ctx)
          continue
        }
        if (r.cssRules) {
          walk(r.cssRules, [...ctx, r.conditionText ?? r.name ?? String(r.constructor.name)])
        }
      }
    }

    const harvestTokens = (r) => {
      const s = r.style
      for (let i = 0; i < s.length; i++) {
        const p = s[i]
        if (!p.startsWith('--')) continue
        tokens.set(`${p} @ ${r.selectorText}`, {
          token: p,
          value: s.getPropertyValue(p).trim(),
          declaredAt: r.selectorText,
        })
      }
    }

    blockedSheets = 0
    for (const sheet of document.styleSheets) {
      // Cross-origin and file:// sheets are not origin-clean; .cssRules throws SecurityError
      // (drafts.csswg.org/cssom). Silently returning nothing here would look identical to
      // "this element has no styles", so it is counted and surfaced instead.
      try {
        walk(sheet.cssRules, [])
      } catch {
        blockedSheets++
      }
    }
    // Inline style wins over everything the sheets said.
    if (el.getAttribute('style')) hits.push({ sel: '[style]', ctx: ['inline'], style: el.style })

    return { hits, tokens: [...tokens.values()] }
  }

  // querySelectorAll cannot take :hover/:focus-visible and el.matches() would be false for them
  // anyway. Strip the interaction pseudo-classes so a `hover:` utility still resolves to its rule.
  const stripPseudoState = (sel) =>
    sel.replace(/:(hover|focus|focus-visible|focus-within|active|visited|target)\b/g, '')

  // ── resolution ─────────────────────────────────────────────────────────────────────────

  function resolve(el) {
    const { hits, tokens } = collect(el)
    const root = getComputedStyle(document.documentElement)
    const comp = getComputedStyle(el)
    const byValue = new Map()
    for (const t of tokens) {
      if (!t.value) continue
      if (!byValue.has(t.value)) byValue.set(t.value, [])
      byValue.get(t.value).push(t)
    }

    // Winner per property = the LAST matching rule that declares it. Cascade order within one
    // element is document order for equal specificity, and Tailwind emits utilities in one layer,
    // so last-wins is right far more often than a hand-rolled specificity sort would be.
    const winners = new Map()
    for (const h of hits) {
      for (let i = 0; i < h.style.length; i++) {
        const p = h.style[i]
        if (!INTERESTING.has(p)) continue
        winners.set(p, { prop: p, sel: h.sel, ctx: h.ctx, declared: h.style.getPropertyValue(p) })
      }
    }

    const resolved = {}
    for (const w of winners.values()) {
      const names = [...w.declared.matchAll(/var\(\s*(--[\w-]+)/g)].map((m) => m[1])
      const toks = names.map((n) => {
        const value = root.getPropertyValue(n).trim()
        const decl = tokens.filter((t) => t.token === n).map((t) => t.declaredAt)
        // The sibling set: other tokens carrying a byte-identical value. Editing one and not
        // these is a half-applied change that looks fixed on this screen and is broken two
        // routes away.
        const siblings = (byValue.get(value) ?? [])
          .filter((t) => t.token !== n)
          .map((t) => t.token)
        return { token: n, value, declaredAt: [...new Set(decl)], siblings: [...new Set(siblings)] }
      })
      resolved[w.prop] = {
        sel: w.sel,
        ctx: w.ctx,
        declared: w.declared.trim(),
        computed: comp.getPropertyValue(w.prop).trim(),
        tokens: toks,
        blast: blastRadius(w.sel),
      }
    }
    return { resolved, blockedSheets, matchedRules: hits.length, tokenCount: tokens.length }
  }

  // How many nodes, and how many DISTINCT components, this rule reaches. This one number decides
  // which layer the fix belongs in — see references/critique.md § The pointed-at defect.
  function blastRadius(sel) {
    if (sel === '[style]') return { nodes: 1, slots: [], scope: 'inline' }
    let nodes = []
    try {
      nodes = [...document.querySelectorAll(stripPseudoState(sel))]
    } catch {
      return { nodes: -1, slots: [], scope: 'unqueryable' }
    }
    const slots = [...new Set(nodes.map((n) => n.closest('[data-slot]')?.dataset.slot).filter(Boolean))]
    return {
      nodes: nodes.length,
      slots,
      scope: slots.length > 1 ? 'token' : slots.length === 1 ? 'variant' : 'node',
    }
  }

  // ── identity ───────────────────────────────────────────────────────────────────────────
  // What the model needs to find the source. data-slot is shipped by every shadcn primitive;
  // where it is absent (foji has no shadcn) the class list plus the DOM path is enough for one
  // grep, and data-sd-loc fills in if a build plugin is ever added.

  function identify(el) {
    const owner = el.closest('[data-slot]')
    return {
      tag: el.tagName.toLowerCase(),
      slot: el.dataset.slot ?? null,
      ownerSlot: owner && owner !== el ? owner.dataset.slot : null,
      variant: el.dataset.variant ?? owner?.dataset.variant ?? null,
      size: el.dataset.size ?? owner?.dataset.size ?? null,
      loc: el.dataset.sdLoc ?? null,
      testid: el.dataset.testid ?? null,
      id: el.id || null,
      role: el.getAttribute('role'),
      ariaLabel: el.getAttribute('aria-label'),
      text: (el.textContent ?? '').trim().slice(0, 80) || null,
      path: domPath(el),
    }
  }

  function domPath(el) {
    const parts = []
    for (let n = el; n && n.nodeType === 1 && parts.length < 6; n = n.parentElement) {
      let s = n.tagName.toLowerCase()
      if (n.id) {
        parts.unshift(`${s}#${n.id}`)
        break
      }
      if (n.dataset.slot) s += `[data-slot=${n.dataset.slot}]`
      const sibs = n.parentElement ? [...n.parentElement.children].filter((c) => c.tagName === n.tagName) : []
      if (sibs.length > 1) s += `:nth-of-type(${sibs.indexOf(n) + 1})`
      parts.unshift(s)
    }
    return parts.join(' > ')
  }

  // ── UI ─────────────────────────────────────────────────────────────────────────────────

  const host = document.createElement('div')
  host.style.cssText = 'position:fixed;inset:0;z-index:2147483647;pointer-events:none'
  const shadow = host.attachShadow({ mode: 'open' })
  shadow.innerHTML = `
    <style>
      :host { all: initial }
      .box { position:fixed; border:2px solid ${ACCENT}; pointer-events:none; display:none;
             box-shadow:0 0 0 9999px rgba(0,0,0,.25); border-radius:1px }
      .tag { position:fixed; font:600 11px ui-monospace,SFMono-Regular,monospace; color:#fff;
             background:${ACCENT}; padding:2px 6px; white-space:nowrap; pointer-events:none;
             display:none; border-radius:1px }
      .panel { position:fixed; pointer-events:auto; display:none; width:340px;
               background:#0b0b0c; color:#f4f4f5; border:1px solid #2a2a2e; border-radius:2px;
               font:13px/1.45 ui-sans-serif,system-ui,sans-serif; box-shadow:0 12px 40px rgba(0,0,0,.5) }
      .panel header { padding:8px 10px; border-bottom:1px solid #2a2a2e;
                      font:600 11px ui-monospace,monospace; color:#a1a1aa; letter-spacing:.02em }
      .panel .why { padding:8px 10px; border-bottom:1px solid #2a2a2e; max-height:150px;
                    overflow:auto; font:11px/1.5 ui-monospace,monospace; color:#d4d4d8 }
      .panel .why b { color:#fff; font-weight:600 }
      .panel .why .tok { color:${ACCENT} }
      .panel textarea { width:100%; box-sizing:border-box; border:0; background:transparent;
                        color:inherit; font:inherit; padding:10px; resize:none; outline:none }
      .panel footer { padding:6px 10px; border-top:1px solid #2a2a2e;
                      font:10px ui-monospace,monospace; color:#71717a; display:flex;
                      justify-content:space-between; align-items:center; gap:8px }
      .panel footer button { font:600 10px ui-monospace,monospace; color:#fff; background:${ACCENT};
                             border:0; padding:4px 10px; border-radius:2px; cursor:pointer }
      .chip { position:fixed; right:12px; bottom:12px; pointer-events:auto;
              background:${ACCENT}; color:#fff; font:600 11px ui-monospace,monospace;
              padding:5px 9px; border-radius:2px; cursor:default; user-select:none }
      .warn { color:#fbbf24 }
    </style>
    <div class="box"></div><div class="tag"></div>
    <div class="panel">
      <header>pin</header><div class="why"></div>
      <textarea rows="2" placeholder="what is wrong with this?  ⏎ to pin, esc to cancel"></textarea>
      <footer><span class="count"></span><button class="commit">pin it ⏎</button></footer>
    </div>
    <div class="chip"></div>`

  const $ = (s) => shadow.querySelector(s)
  const box = $('.box')
  const tag = $('.tag')
  const panel = $('.panel')
  const why = $('.why')
  const input = $('textarea')
  const chip = $('.chip')

  let on = false
  let stack = []
  let depth = 0
  let target = null
  let frozen = false
  const pins = (window.__sdPins = window.__sdPins || [])

  const paint = (el) => {
    const r = el.getBoundingClientRect()
    box.style.cssText += `;display:block;left:${r.left}px;top:${r.top}px;width:${r.width}px;height:${r.height}px`
    tag.style.display = 'block'
    tag.style.left = `${r.left}px`
    tag.style.top = `${Math.max(0, r.top - 20)}px`
    const id = identify(el)
    tag.textContent = `${id.slot ? `[${id.slot}]` : id.tag}${id.variant ? ` ${id.variant}` : ''}  ${Math.round(r.width)}×${Math.round(r.height)}`
  }

  const clear = () => {
    box.style.display = 'none'
    tag.style.display = 'none'
    panel.style.display = 'none'
    frozen = false
    target = null
  }

  const summarize = (res) => {
    const rows = []
    for (const [prop, r] of Object.entries(res.resolved)) {
      if (!r.tokens.length) continue
      for (const t of r.tokens) {
        rows.push(
          `<div><b>${prop}</b> → <span class="tok">${t.token}</span> = ${t.value || '?'}` +
            `  <span style="color:#71717a">(${r.blast.scope}, ${r.blast.nodes} nodes)</span>` +
            (t.siblings.length ? `<br><span class="warn">  ↳ same value: ${t.siblings.join(', ')}</span>` : '') +
            `</div>`,
        )
      }
    }
    const untokened = Object.entries(res.resolved).filter(([, r]) => !r.tokens.length).map(([p]) => p)
    if (untokened.length) rows.push(`<div class="warn">no token: ${untokened.join(', ')}</div>`)
    if (res.blockedSheets) {
      rows.unshift(
        `<div class="warn"><b>${res.blockedSheets} stylesheet(s) unreadable</b> — cross-origin or file://. Serve over http://localhost.</div>`,
      )
    }
    return rows.join('') || '<div class="warn">nothing resolved</div>'
  }

  const select = (el) => {
    target = el
    paint(el)
    const res = resolve(el)
    why.innerHTML = summarize(res)
    target.__sdRes = res
    $('.count').textContent = `${res.matchedRules} rules · ${res.tokenCount} tokens`
    // Show, THEN measure. The why-block is variable height, so any guessed constant clips the
    // textarea off the bottom of the viewport exactly when the pinned element sits low on the page.
    const r = el.getBoundingClientRect()
    panel.style.display = 'block'
    panel.style.left = `${Math.min(Math.max(8, r.left), Math.max(8, innerWidth - 348))}px`
    panel.style.top = '0px'
    const h = panel.getBoundingClientRect().height
    const below = r.bottom + 8
    const top = below + h <= innerHeight - 8 ? below : r.top - h - 8 >= 8 ? r.top - h - 8 : innerHeight - h - 8
    panel.style.top = `${Math.max(8, top)}px`
    input.focus()
  }

  const onMove = (e) => {
    if (!on || frozen) return
    stack = document.elementsFromPoint(e.clientX, e.clientY).filter((n) => n !== host && !host.contains(n))
    depth = 0
    if (stack[0]) paint(stack[0])
  }

  const onClick = (e) => {
    if (!on || !e.altKey) return
    e.preventDefault()
    e.stopPropagation()
    stack = document.elementsFromPoint(e.clientX, e.clientY).filter((n) => n !== host && !host.contains(n))
    depth = 0
    frozen = true
    if (stack[0]) select(stack[0])
  }

  const onKey = (e) => {
    if (e.altKey && e.shiftKey && (e.key === 'P' || e.key === 'p')) {
      e.preventDefault()
      api.toggle()
      return
    }
    if (!on) return
    if (e.key === 'Escape') {
      clear()
      return
    }
    if (frozen && e.altKey && (e.key === 'ArrowUp' || e.key === 'ArrowDown')) {
      e.preventDefault()
      depth = Math.min(stack.length - 1, Math.max(0, depth + (e.key === 'ArrowDown' ? 1 : -1)))
      select(stack[depth])
      return
    }
    if (frozen && e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      commit()
    }
  }

  function commit() {
    if (!target) return
    const said = input.value.trim()
    if (!said) return
    const r = target.getBoundingClientRect()
    const pin = {
      said,
      at: new Date().toISOString(),
      url: location.href,
      route: location.pathname,
      viewport: { w: innerWidth, h: innerHeight, dpr: devicePixelRatio },
      theme:
        document.documentElement.classList.contains('dark') ||
        document.documentElement.dataset.theme === 'dark'
          ? 'dark'
          : matchMedia('(prefers-color-scheme: dark)').matches
            ? 'dark(system)'
            : 'light',
      scrollY: scrollY,
      identity: identify(target),
      classes: typeof target.className === 'string' ? target.className : target.getAttribute('class'),
      box: { x: +r.x.toFixed(1), y: +r.y.toFixed(1), width: +r.width.toFixed(1), height: +r.height.toFixed(1) },
      ...target.__sdRes,
    }
    pins.push(pin)
    fetch(SINK, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(pin),
      mode: 'cors',
      keepalive: true,
    }).catch(() => {
      /* no sink running — window.__sdPins is still the record */
    })
    input.value = ''
    clear()
    render()
  }

  const render = () => {
    chip.textContent = on ? `pin · ${pins.length} · alt-click` : ''
    chip.style.display = on ? 'block' : 'none'
  }

  const api = {
    toggle() {
      on = !on
      if (!on) clear()
      document.body.style.cursor = on ? 'crosshair' : ''
      render()
      return on
    },
    pins,
    resolve: (el) => resolve(el),
    version: 1,
  }

  addEventListener('mousemove', onMove, true)
  addEventListener('click', onClick, true)
  addEventListener('keydown', onKey, true)
  // Also on the shadow root. A keystroke aimed at the textarea is retargeted at the boundary, and
  // whether it reaches a window-level capture listener depends on how it was dispatched — a real
  // keyboard does, some automation drivers do not. Committing is the one action that must never
  // depend on that, so it has two paths that do not share a failure mode: this, and the button.
  shadow.addEventListener('keydown', onKey, true)
  $('.commit').addEventListener('click', (e) => {
    e.preventDefault()
    e.stopPropagation()
    commit()
  })
  document.documentElement.appendChild(host)
  window.__sdPinOverlay = api
  api.toggle()

  console.log(
    '%cpin-overlay%c ready — alt-click an element · alt+shift+P toggles · window.__sdPins',
    `background:${ACCENT};color:#fff;padding:2px 6px;border-radius:2px;font-weight:600`,
    '',
  )
})()
