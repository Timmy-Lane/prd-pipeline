// pin-overlay — point at a rendered element, get back the TOKEN that owns it.
//
// The problem this solves is not "let the user click things". It is that a design complaint
// arrives as a sentence about a screen ("this is too loud") and gets fixed as a className patch
// on one node — which SKILL.md:278-281 calls a defect, not a preference. The fix almost always
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
// Click the corner chip for everything pinned so far, grouped by the screen it was taken on: hover
// a row to light its element up again, edit the sentence, delete it. That list is hydrated from
// the sink on every load, so it survives a reload. With no sink the chip says `offline` and the
// list holds only what this tab has taken — same as it always did, but now it admits it.
//
// "The screen it was taken on" is observed, not asked for: most apps worth pinning route in React
// state and never move the URL, so a pin records a view key read off the DOM alongside the route.
// When the app changes screens — by any route it has, or by none — the highlight and the panel go
// with it rather than hanging over an element that has been unmounted.
//
// Alt+SHIFT+drag draws a box where an element is MISSING instead. That pin names no element —
// there is not one yet — it names the parent that would hold it, which index between which two
// siblings, and the box that was drawn. Nothing is written to the app: what comes back is a brief
// precise enough to build from, which is the one thing "instead create kanban here" alt-clicked
// onto the nearest button never was.
//
// Esc cancels · Alt+↑/↓ walks the occlusion stack (label → button → card) · Alt+Shift+P toggles.

;(() => {
  if (window.__sdPinOverlay) {
    window.__sdPinOverlay.toggle()
    return
  }

  // The sink is wherever the overlay was served from — pin-server stamps `__sdPinSink` on the
  // copy it hands out, so a non-default `--port` can never leave the page posting into a dead
  // one. The literal is only the fallback for Delivery A, where nobody served anything.
  const SINK = `${window.__sdPinSink ?? 'http://127.0.0.1:7332'}/__sd_pin`
  // The same sink, read side. It answers with the FOLD over pins.jsonl — deletes applied, edits
  // applied, resolutions stripped — so the overlay never has to know the file is a log.
  const SINK_LIST = `${window.__sdPinSink ?? 'http://127.0.0.1:7332'}/__sd_pins`
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

    const walk = (rules, ctx, parentSel) => {
      for (const r of rules) {
        // CSSStyleRule ALSO carries .cssRules now that CSS Nesting shipped. A naive
        // `if (r.cssRules) recurse` therefore short-circuits every style rule and matches
        // NOTHING. Test selectorText first, recurse into the nested block second.
        if (r.selectorText) {
          harvestTokens(r)
          // A nested rule's selectorText is relative: `&` means "the parent compound", and the
          // parent is only known here, on the way down. Substituting :is(parent) is the one form
          // that survives a comma-separated parent. With no parent to substitute there is nothing
          // to test this element against — and Chromium answers el.matches('&') with true, which
          // is how all 104 of foji's nested rules matched every element on the page.
          const abs = /&/.test(r.selectorText)
            ? parentSel
              ? r.selectorText.replace(/&/g, `:is(${parentSel})`)
              : null
            : r.selectorText
          let m = false
          if (abs) {
            try {
              m = el.matches(stripPseudoState(abs))
            } catch {
              m = false
            }
          }
          if (m) hits.push({ sel: abs, ctx, style: r.style, state: stateOf(r.selectorText) })
          if (r.cssRules?.length) walk(r.cssRules, m ? [...ctx, abs] : ctx, abs ?? parentSel)
          continue
        }
        // CSSNestedDeclarations — a bare declaration block inside a nested @media or @supports.
        // It has no selector and no children, so both branches around it skip it, and Tailwind v4
        // puts the payload of every `hover:` utility exactly there, behind @media (hover: hover).
        // The declarations belong to the enclosing selector, which is what parentSel holds.
        if (!r.cssRules && r.style?.length && parentSel) {
          let m = false
          try {
            m = el.matches(stripPseudoState(parentSel))
          } catch {
            m = false
          }
          if (m) hits.push({ sel: parentSel, ctx, style: r.style, state: stateOf(parentSel) })
          continue
        }
        if (r.cssRules) {
          walk(r.cssRules, [...ctx, r.conditionText ?? r.name ?? String(r.constructor.name)], parentSel)
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
        walk(sheet.cssRules, [], null)
      } catch {
        blockedSheets++
      }
    }
    // Inline style wins over everything the sheets said.
    if (el.getAttribute('style')) hits.push({ sel: '[style]', ctx: ['inline'], style: el.style, state: null })

    return { hits, tokens: [...tokens.values()] }
  }

  // The interaction pseudo-classes, as one list because two things need it and they must agree
  // about what counts. Order matters: `focus` ahead of `focus-visible` strips `:focus` out of
  // `:focus-visible` and leaves `-visible` behind as a class name that matches nothing.
  const STATES = 'hover|focus-visible|focus-within|focus|active|visited|target'
  const ANY_STATE = new RegExp(`:(?:${STATES})\\b`, 'g')
  const FIRST_STATE = new RegExp(`:(${STATES})\\b`)

  // querySelectorAll cannot take :hover/:focus-visible and el.matches() would be false for them
  // anyway. Strip the interaction pseudo-classes so a `hover:` utility still resolves to its rule.
  const stripPseudoState = (sel) => sel.replace(ANY_STATE, '')

  // ...and then name what was stripped, so the rule can be filed under its state rather than let
  // into the race for the resting value. The walk reads it off the RAW selector text of a nested
  // rule — `&:active` says `active` — and off the absolutised parent for a bare declaration block,
  // which has no selector of its own to read.
  const stateOf = (sel) => sel.match(FIRST_STATE)?.[1] ?? null

  // ── resolution ─────────────────────────────────────────────────────────────────────────

  function resolve(el) {
    if (!el || el.nodeType !== 1) return { resolved: {}, blockedSheets: 0, matchedRules: 0, tokenCount: 0 }
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
    //
    // A rule that only applies while the element is hovered, focused or held down is not a
    // candidate in that race — its value is not on screen. Being last in the document it used to
    // win every time, which is how `&:active` came to be the answer to "what owns this button's
    // background". It is kept, per property, under `states`: the user did point at this element,
    // and "the pressed state is the loud one" is a complaint the pin must still be able to carry.
    const winners = new Map()
    const states = new Map()
    for (const h of hits) {
      for (let i = 0; i < h.style.length; i++) {
        const p = h.style[i]
        if (!INTERESTING.has(p)) continue
        const declared = h.style.getPropertyValue(p)
        if (h.state) {
          if (!states.has(p)) states.set(p, [])
          states.get(p).push({ state: h.state, sel: h.sel, declared: declared.trim() })
          continue
        }
        winners.set(p, { prop: p, sel: h.sel, ctx: h.ctx, declared })
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
        tokens: toks.filter((t) => !isPlumbing(t)),
        plumbing: toks.filter(isPlumbing).map((t) => t.token),
        states: states.get(w.prop) ?? [],
        blast: blastRadius(w.sel),
      }
    }
    return { resolved, blockedSheets, matchedRules: hits.length, tokenCount: tokens.length }
  }

  // `--tw-*` are Tailwind's internal composition slots, not the project's design system. A ring or
  // shadow utility declares five of them at once, almost always empty or `0 0 #0000`, and left in
  // they crowd every real token off the panel — measured on foji, where a card's entire readout was
  // three `--tw-*-shadow = 0 0 #0000` rows and nothing else. They are kept, under `plumbing`, so a
  // pin never silently drops a property; they just stop competing for the eye.
  const NOOP = /^(0 0 #0+|none|normal|auto|initial)$/i
  const isPlumbing = (t) => t.token.startsWith('--tw-') || !t.value || NOOP.test(t.value)

  // How many nodes, and how many DISTINCT components, this rule reaches. This one number decides
  // which layer the fix belongs in — see references/critique.md § The pointed-at defect.
  function blastRadius(sel) {
    if (sel === '[style]') return { nodes: 1, slots: [], scope: 'inline' }
    // A `&` that reached this far is one the walk could not absolutise. querySelectorAll answers
    // it with [HTML] rather than throwing, so the catch below never fires and the rule looks like
    // it reaches exactly one node — which the reader then calls a call-site override. Refuse.
    if (/&/.test(sel)) return { nodes: -1, slots: [], scope: 'unqueryable' }
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
  // Identity, not just a handle for the e2e driver: elementsFromPoint and elementFromPoint both
  // have to exclude this subtree, and an id is the one way to say "that thing" from outside it.
  host.id = 'sd-pin-overlay'
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
      /* Above the list: the list is a place to look, the panel is a place to type, and the one
         you are typing into is never the one that gets covered. */
      .panel { position:fixed; z-index:1; pointer-events:auto; display:none; width:340px;
               background:#0b0b0c; color:#f4f4f5; border:1px solid #2a2a2e; border-radius:2px;
               font:13px/1.45 ui-sans-serif,system-ui,sans-serif; box-shadow:0 12px 40px rgba(0,0,0,.5) }
      .panel header { padding:8px 10px; border-bottom:1px solid #2a2a2e;
                      font:600 11px ui-monospace,monospace; color:#a1a1aa; letter-spacing:.02em }
      .panel .why { padding:8px 10px; border-bottom:1px solid #2a2a2e; max-height:150px;
                    overflow:auto; font:11px/1.5 ui-monospace,monospace; color:#d4d4d8 }
      .panel .why b { color:#fff; font-weight:600 }
      .panel .why .tok { color:${ACCENT} }
      .panel .why .anchor { color:#fff; margin-bottom:6px }
      .panel textarea { width:100%; box-sizing:border-box; border:0; background:transparent;
                        color:inherit; font:inherit; padding:10px; resize:none; outline:none }
      .panel footer { padding:6px 10px; border-top:1px solid #2a2a2e;
                      font:10px ui-monospace,monospace; color:#71717a; display:flex;
                      justify-content:space-between; align-items:center; gap:8px }
      .panel footer button { font:600 10px ui-monospace,monospace; color:#fff; background:${ACCENT};
                             border:0; padding:4px 10px; border-radius:2px; cursor:pointer }
      .chip { position:fixed; right:12px; bottom:12px; pointer-events:auto;
              background:${ACCENT}; color:#fff; font:600 11px ui-monospace,monospace;
              padding:5px 9px; border-radius:2px; cursor:pointer; user-select:none }
      .warn { color:#fbbf24 }

      /* The inventory. Same width as the panel and anchored to the same corner as the chip that
         opens it, because the panel already sits wherever the user is pointing and a second slab
         in the middle of the screen would cover the thing every row is about. */
      .list { position:fixed; right:12px; bottom:38px; width:340px; max-height:min(52vh,420px);
              overflow:auto; pointer-events:auto; display:none; margin:0; padding:0;
              list-style:none; background:#0b0b0c; color:#f4f4f5; border:1px solid #2a2a2e;
              border-radius:2px; box-shadow:0 12px 40px rgba(0,0,0,.5) }
      .list .grp { position:sticky; top:0; display:flex; gap:6px; align-items:baseline;
                   padding:6px 10px 4px; background:#0b0b0c; border-top:1px solid #2a2a2e;
                   font:600 10px ui-monospace,monospace; color:#71717a; letter-spacing:.02em }
      .list .grp:first-child { border-top:0 }
      .list .grp .vk { flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap }
      .list .grp.now .vk { color:${ACCENT} }
      .list .grp .go { border:0; background:transparent; padding:0; cursor:pointer;
                       font:600 10px ui-monospace,monospace; color:${ACCENT} }
      .list .row { display:flex; gap:8px; align-items:baseline; padding:4px 10px;
                   font:11px/1.5 ui-sans-serif,system-ui,sans-serif }
      .list .row:hover { background:#141416 }
      .list .row.cold { color:#71717a }
      .list .said { flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap }
      .list .where { max-width:42%; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;
                     font:10px ui-monospace,monospace; color:#52525b }
      .list .acts { display:flex; gap:6px; opacity:0 }
      .list .row:hover .acts { opacity:1 }
      .list .acts button { border:0; background:transparent; padding:0; cursor:pointer;
                           font:10px ui-monospace,monospace; color:#71717a }
      .list .acts button:hover { color:${ACCENT} }
      .list .empty { padding:10px; font:10px ui-monospace,monospace; color:#52525b }
    </style>
    <div class="box"></div><div class="tag"></div>
    <div class="panel">
      <header>pin</header><div class="why"></div>
      <textarea rows="2" placeholder="what is wrong with this?  ⏎ to pin, esc to cancel"></textarea>
      <footer><span class="count"></span><button class="commit">pin it ⏎</button></footer>
    </div>
    <ol class="list"></ol>
    <div class="chip"></div>`

  const $ = (s) => shadow.querySelector(s)
  const box = $('.box')
  const tag = $('.tag')
  const panel = $('.panel')
  const head = $('.panel header')
  const why = $('.why')
  const input = $('textarea')
  const commitBtn = $('.commit')
  const list = $('.list')
  const chip = $('.chip')

  let on = false
  let stack = []
  let depth = 0
  let target = null
  let frozen = false
  let editing = null // the id of the pin whose sentence the panel is currently rewriting, or null
  let listOpen = false
  let offline = false
  let lastView = '' // the view key as of the last settled screen change — see onNav
  let navT = 0
  let anchor = null // where an element the user drew is missing FROM, or null — see resolveAnchor
  let drawStart = null // the viewport point an alt+shift drag began at, while one is in flight
  const pins = (window.__sdPins = window.__sdPins || [])

  // A "view" is the coarsest thing that changes when the user changes screens. We do not know the
  // app's router — foji does not have one, its URL is `/` on every screen — so we ask the DOM
  // instead: what element under the centre of the viewport is big enough to BE the screen? Its tag
  // plus class list is the key. Measured on foji: five screens, five distinct keys, one URL.
  const viewKey = () => {
    const A = innerWidth * innerHeight
    let n = document.elementFromPoint(innerWidth >> 1, innerHeight >> 1)
    while (n && (n === host || host.contains(n))) n = n.parentElement // never key on our own host
    for (; n && n.nodeType === 1; n = n.parentElement) {
      const r = n.getBoundingClientRect()
      if (r.width * r.height >= A * 0.6) {
        const cls = (typeof n.className === 'string' ? n.className : '').trim().split(/\s+/).filter(Boolean)
        return n.tagName.toLowerCase() + (cls.length ? `.${cls.slice(0, 6).join('.')}` : '')
      }
    }
    return 'none'
  }

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
    editing = null
    anchor = null
    drawStart = null
    head.textContent = 'pin'
    commitBtn.textContent = 'pin it ⏎'
  }

  // Hovering a list row lights up the element that row names. Letting go has to put back whatever
  // was on screen before it, because a frozen panel is a sentence the user is halfway through and
  // moving its box out from under him is the tool getting in the way.
  const restore = () => {
    if (frozen && target) paint(target)
    else {
      box.style.display = 'none'
      tag.style.display = 'none'
    }
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
    const untokened = Object.entries(res.resolved)
      .filter(([, r]) => !r.tokens.length && !r.plumbing?.length)
      .map(([p]) => p)
    if (untokened.length) rows.push(`<div class="warn">no token: ${untokened.join(', ')}</div>`)
    const plumbed = Object.entries(res.resolved).filter(([, r]) => !r.tokens.length && r.plumbing?.length)
    if (plumbed.length) {
      rows.push(
        `<div style="color:#52525b">${plumbed.length} propert${plumbed.length === 1 ? 'y' : 'ies'} carry only Tailwind's internal --tw-* slots (${plumbed.map(([p]) => p).join(', ')}) — plumbing, not design</div>`,
      )
    }
    if (res.blockedSheets) {
      rows.unshift(
        `<div class="warn"><b>${res.blockedSheets} stylesheet(s) unreadable</b> — cross-origin or file://. Serve over http://localhost.</div>`,
      )
    }
    return rows.join('') || '<div class="warn">nothing resolved</div>'
  }

  // Put the panel beside a rectangle — the element being critiqued, or the parent an add pin is
  // going into. Show, THEN measure: the why-block is variable height, so any guessed constant
  // clips the textarea off the bottom of the viewport exactly when the thing pinned sits low.
  const openPanel = (r) => {
    panel.style.display = 'block'
    panel.style.left = `${Math.min(Math.max(8, r.left), Math.max(8, innerWidth - 348))}px`
    panel.style.top = '0px'
    const h = panel.getBoundingClientRect().height
    const below = r.bottom + 8
    const top = below + h <= innerHeight - 8 ? below : r.top - h - 8 >= 8 ? r.top - h - 8 : innerHeight - h - 8
    panel.style.top = `${Math.max(8, top)}px`
    input.focus()
  }

  const select = (el) => {
    target = el
    // Pointing at an element that exists retires an anchor for one that does not. Two answers to
    // "what is this pin about" cannot both be live, and the later gesture is the one meant.
    anchor = null
    paint(el)
    const res = resolve(el)
    why.innerHTML = summarize(res)
    target.__sdRes = res
    $('.count').textContent = `${res.matchedRules} rules · ${res.tokenCount} tokens`
    openPanel(el.getBoundingClientRect())
  }

  // ── add-element anchors ────────────────────────────────────────────────────────────────
  // The other half of a design complaint: not "this is wrong" but "something is missing here". A
  // pin saying that cannot name an element, because the element does not exist. So it names the
  // parent that would hold it and the gap it goes in — which is what a brief has to say before
  // anyone can write the JSX, and what alt-clicking the nearest button can never say.

  // Tags that can only hold inline content. Drawing on top of a button means "next to this button",
  // never "inside it", so the resolution climbs out of every one of these before it starts asking
  // about children. Onlook's INLINE_ONLY_CONTAINERS, verbatim (packages/constants/src/dom.ts:2-60).
  const INLINE_ONLY = new Set(
    (
      'a abbr area audio b bdi bdo br button canvas cite code data datalist del dfn em embed h1 h2 ' +
      'h3 h4 h5 h6 i iframe img input ins kbd label li map mark meter noscript object output p ' +
      'picture progress q ruby s samp script select slot small span strong sub sup svg template ' +
      'textarea time u var video wbr'
    ).split(' '),
  )

  // Explicitly null past either end of the child list rather than undefined: a record whose shape
  // changes depending on where in the list the gap fell is a record every reader has to guess at.
  const brief = (el) =>
    el
      ? {
          tag: el.tagName.toLowerCase(),
          slot: el.dataset.slot ?? null,
          text: (el.textContent ?? '').trim().slice(0, 40) || null,
          classes: typeof el.className === 'string' ? el.className : el.getAttribute('class'),
        }
      : null

  // A point becomes a parent and an index. Onlook stops there and throws the rectangle away at the
  // iframe boundary (insert-element.md:158-160); it can afford to, because it writes the JSX
  // itself. A brief cannot: `index: 1` is unactionable in a file whose JSX children include
  // whitespace nodes, so the two siblings either side of the gap are named by their text as well.
  const resolveAnchor = (x, y, drawn) => {
    let t = document.elementsFromPoint(x, y).find((n) => n !== host && !host.contains(n))
    while (t && INLINE_ONLY.has(t.tagName.toLowerCase())) t = t.parentElement
    if (!t || t.nodeType !== 1) return null
    const cs = getComputedStyle(t)
    const kids = [...t.children]
    const rects = kids.map((k) => k.getBoundingClientRect())
    // Onlook measures the distance to each child's VERTICAL midpoint and nothing else
    // (insert.ts:24-42), so in a flex row every child shares one midpoint, the strict `<` never
    // beats the first of them, and the index collapses to 0 or 1 — horizontal position is never
    // resolved at all. The axis is not a constant. A flex container names it outright; a grid has
    // no such property (grid-auto-flow describes fill order, not geometry) so its own children's
    // spread answers for it.
    const span = (f) => (rects.length ? Math.max(...rects.map(f)) - Math.min(...rects.map(f)) : 0)
    const axis = cs.display.includes('flex')
      ? cs.flexDirection.startsWith('row')
        ? 'x'
        : 'y'
      : span((r) => r.left) > span((r) => r.top)
        ? 'x'
        : 'y'
    const mid = (r) => (axis === 'x' ? r.left + r.width / 2 : r.top + r.height / 2)
    const at = axis === 'x' ? x : y
    let best = 0
    let min = Infinity
    rects.forEach((r, i) => {
      const d = Math.abs(at - mid(r))
      if (d < min) {
        min = d
        best = i
      }
    })
    // A container that stacks its children has a place BETWEEN two of them. Anything else — a block
    // whose children are laid out by the flow, an empty container — has only an end to append to,
    // and claiming an index into it would be inventing a precision the layout does not have.
    const stacked = /flex|grid/.test(cs.display) && rects.length > 0
    const index = stacked ? (at > mid(rects[best]) ? best + 1 : best) : null
    const path = domPath(t)
    let unique = false
    try {
      unique = document.querySelectorAll(path).length === 1
    } catch {
      unique = false
    }
    return {
      type: stacked ? 'index' : 'append',
      index,
      childCount: kids.length,
      axis,
      parent: {
        tag: t.tagName.toLowerCase(),
        slot: t.dataset.slot ?? null,
        classes: typeof t.className === 'string' ? t.className : t.getAttribute('class'),
        display: cs.display,
        flexDirection: cs.flexDirection,
        path,
        // The same refusal locateRow makes, for the same reason: when the path matches more than
        // one node, the brief describes a shape rather than a place. Pointing at the first
        // document-order match would be a guess, and a guess reads exactly like a fact.
        unique,
      },
      // The SIBLINGS either side of the gap, not instructions: the new element goes after `before`
      // and ahead of `after`. Named by their text because that is what names the pattern to copy.
      before: stacked ? brief(kids[index - 1]) : brief(kids[kids.length - 1]),
      after: stacked ? brief(kids[index]) : null,
      drawn,
      // `res` and `el` are the live half and never reach the record — commit() lifts the parent's
      // resolution to the pin's top level, where a critique pin keeps the resolution of its own
      // element, and drops the node. It is the parent's because that is the gap, padding and
      // colour system whatever gets built has to join.
      res: resolve(t),
      el: t,
    }
  }

  const onMove = (e) => {
    // A drag in flight owns the box, and it is the only thing on screen that follows the pointer
    // without asking what is under it — the whole point is that nothing is there yet.
    if (drawStart) {
      const l = Math.min(drawStart.x, e.clientX)
      const t = Math.min(drawStart.y, e.clientY)
      box.style.cssText += `;display:block;left:${l}px;top:${t}px;width:${Math.abs(e.clientX - drawStart.x)}px;height:${Math.abs(e.clientY - drawStart.y)}px`
      tag.style.display = 'none'
      return
    }
    if (!on || frozen) return
    // A mousemove inside the shadow root is retargeted to the host, so this one test covers the
    // list and the panel both. Without it, sweeping the mouse down the inventory repaints whatever
    // sits UNDER the list on each step and fights the row's own hover for the box.
    if (host.contains(e.target)) return
    stack = document.elementsFromPoint(e.clientX, e.clientY).filter((n) => n !== host && !host.contains(n))
    depth = 0
    if (stack[0]) paint(stack[0])
  }

  // The host app must never see the mousedown half of an alt-click. foji's title strip starts a
  // Tauri window drag from its own mousedown handler (lib/drag.ts:22), so alt-clicking it drags the
  // window out from under the pin in the desktop app and throws `undefined (reading 'metadata')` in
  // a plain browser, where __TAURI_INTERNALS__ does not exist. Capture phase, because React's root
  // listener and every other delegated handler live below it. The click still arrives at onClick:
  // preventDefault on mousedown suppresses focus and text selection, not the click event.
  const onDown = (e) => {
    if (!on || !e.altKey || host.contains(e.target)) return
    e.preventDefault()
    e.stopPropagation()
    // Alt+SHIFT is the add gesture, and everything from here draws the box the user means to fill.
    // It cannot collide with Alt+Shift+P: that branch tests e.key, and a mousedown carries no key.
    if (!e.shiftKey) return
    clear()
    frozen = true
    drawStart = { x: e.clientX, y: e.clientY }
  }

  const onUp = (e) => {
    if (!drawStart) return
    const s = drawStart
    drawStart = null
    const drawn = {
      x: Math.min(s.x, e.clientX),
      y: Math.min(s.y, e.clientY),
      width: Math.abs(e.clientX - s.x),
      height: Math.abs(e.clientY - s.y),
    }
    // The mouse-UP point, which is onlook's choice too (insert-element.md:72-81): a drag that
    // started on a button and ended in the gap below it means the gap, not the button. A modifier
    // click with no drag is the same gesture with a zero-size box, so pointing works as well as
    // drawing. onDown already preventDefaulted this sequence for the host's sake — nothing here
    // has to repeat that.
    anchor = resolveAnchor(e.clientX, e.clientY, drawn)
    if (!anchor) {
      clear()
      return
    }
    // The box moves onto the PARENT rather than staying on what was drawn. The drawn rectangle is
    // already in the record; the one thing the user cannot otherwise see is which container the
    // resolution decided to put the element in, and that is the half he can still correct.
    paint(anchor.el)
    tag.textContent = `+ into ${anchor.parent.tag}${anchor.index == null ? '' : `  ${anchor.index}/${anchor.childCount}`}`
    why.innerHTML = summarize(anchor.res)
    // mk, so the neighbours' text is set as text. It comes off the host page, and the why-block is
    // the one place in this file that assigns innerHTML.
    why.prepend(
      mk(
        'div',
        'anchor',
        `add into <${anchor.parent.tag}>` +
          (anchor.index == null
            ? ` — appended after ${anchor.childCount} children`
            : ` at ${anchor.index} of ${anchor.childCount}` +
              (anchor.before?.text ? ` · after "${anchor.before.text}"` : '') +
              (anchor.after?.text ? ` · before "${anchor.after.text}"` : '')),
      ),
    )
    $('.count').textContent = `${anchor.res.matchedRules} rules · ${anchor.res.tokenCount} tokens`
    head.textContent = 'add'
    commitBtn.textContent = 'add it ⏎'
    openPanel(anchor.el.getBoundingClientRect())
  }

  const onClick = (e) => {
    if (!on || !e.altKey) return
    e.preventDefault()
    e.stopPropagation()
    // onUp already answered this one. A modifier click with no drag is still the add gesture, and
    // letting the critique path run here would replace its anchor with a plain selection of
    // whatever happened to be under the pointer.
    if (e.shiftKey) return
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

  // Every write is one appended record and the same failure question: did it land? The old bare
  // `.catch(() => {})` answered "who knows" and the pin died on the next reload with nothing on
  // screen having said so. Now a rejected POST flags the record it came from and lights the chip.
  const post = (body, local) => {
    fetch(SINK, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(body),
      mode: 'cors',
      keepalive: true,
    })
      .then((r) => {
        if (!r.ok) throw new Error(String(r.status))
      })
      .catch(() => {
        offline = true
        if (local) local.unsynced = true
        render()
      })
  }

  // crypto.randomUUID is missing outside a secure context, and Delivery A is a devtools paste into
  // whatever page the user has open. An id that is merely unique within one pins.jsonl is enough.
  const newId = () =>
    crypto.randomUUID?.() ?? `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`

  function commit() {
    if (!target && !editing && !anchor) return
    const said = input.value.trim()
    if (!said) return
    if (editing) {
      const rec = pins.find((p) => p.id === editing)
      const at = new Date().toISOString()
      if (rec) {
        rec.said = said
        rec.editedAt = at
      }
      post({ op: 'edit', id: editing, said, at }, rec)
      input.value = ''
      clear()
      render()
      return
    }
    const r = target?.getBoundingClientRect()
    // `el` is a live node and `res` belongs at the pin's top level beside a critique pin's own
    // resolution, so neither is part of the anchor as recorded.
    const { el, res, ...where } = anchor ?? {}
    const pin = {
      // op and id are what make the file a log rather than a list: an edit or a delete is another
      // record naming this same id, never a rewrite of this line. kind defaults to critique for a
      // consumer that has never heard of it, and the two shapes differ exactly here: an add pin
      // has no element to identify — that absence IS what it says — so it carries an anchor and
      // the parent's resolution where a critique pin carries an identity and its own.
      op: 'pin',
      id: newId(),
      kind: anchor ? 'add' : 'critique',
      said,
      at: new Date().toISOString(),
      url: location.href,
      route: location.pathname,
      view: viewKey(),
      viewport: { w: innerWidth, h: innerHeight, dpr: devicePixelRatio },
      theme:
        document.documentElement.classList.contains('dark') ||
        document.documentElement.dataset.theme === 'dark'
          ? 'dark'
          : matchMedia('(prefers-color-scheme: dark)').matches
            ? 'dark(system)'
            : 'light',
      scrollY: scrollY,
      identity: target ? identify(target) : null,
      classes: target ? (typeof target.className === 'string' ? target.className : target.getAttribute('class')) : null,
      box: r ? { x: +r.x.toFixed(1), y: +r.y.toFixed(1), width: +r.width.toFixed(1), height: +r.height.toFixed(1) } : null,
      ...(anchor ? { anchor: where, ...res } : target.__sdRes),
    }
    pins.push(pin)
    post(pin, pin)
    input.value = ''
    clear()
    render()
  }

  // ── the inventory ──────────────────────────────────────────────────────────────────────

  // Jumping back to a pinned element, and refusing to. domPath caps at six segments and two of the
  // four pins in the real corpus carry no #id anchor, so a stale path resolves to a live WRONG
  // element as readily as the right one. One node or nothing — never highlight on a maybe.
  const locateRow = (pin, here = viewKey()) => {
    if (pin.view && pin.view !== here) return null
    let n = []
    try {
      n = [...document.querySelectorAll(pin.identity?.path ?? '')]
    } catch {
      return null
    }
    return n.length === 1 ? n[0] : null
  }

  // textContent, never innerHTML: a pin's sentence is whatever the user typed, and the panel next
  // to it is already showing markup this file built.
  const mk = (t, cls, text) => {
    const n = document.createElement(t)
    if (cls) n.className = cls
    if (text != null) n.textContent = text
    return n
  }

  // One group per screen a pin was taken on. The route is there for an app that has a router; the
  // view key is what tells two screens apart in the far more common case where the URL never moves.
  const groupKey = (p) => `${p.route ?? location.pathname} ${p.view ?? ''}`

  const whereLabel = (pin) => {
    if (pin.anchor) return `+ into ${pin.anchor.parent?.tag ?? '?'}`
    const id = pin.identity ?? {}
    return `${id.slot ? `[${id.slot}]` : (id.tag ?? '?')}${id.text ? ` "${id.text.slice(0, 24)}"` : ''}`
  }

  // Grouped by the screen the pin was taken on, because a sentence about a screen means nothing
  // beside a screen it is not about, and on a state-routed app half the rows always are.
  const renderList = () => {
    list.textContent = ''
    if (!pins.length) {
      list.append(mk('li', 'empty', 'no pins yet — alt-click an element'))
      return
    }
    const here = viewKey()
    const groups = new Map()
    for (const p of pins) {
      const key = groupKey(p)
      if (!groups.has(key)) groups.set(key, { route: p.route ?? location.pathname, view: p.view, rows: [] })
      groups.get(key).rows.push(p)
    }
    for (const g of groups.values()) {
      const now = g.route === location.pathname && g.view === here
      const h = mk('li', `grp${now ? ' now' : ''}`)
      h.title = `${g.route} · ${g.view ?? 'view not recorded'}`
      h.append(mk('span', 'rt', g.route), mk('span', 'vk', g.view ?? 'view not recorded'), mk('span', 'cnt', String(g.rows.length)))
      // The one screen change the overlay can actually make, and only ever to a route a pin was
      // already taken on — this is not a route list, it is the pins' own. A hard navigation rather
      // than pushState, deliberately: the overlay knows nothing about the app's router and a tool
      // with no framework knowledge has no business synthesising a history entry. When the route
      // already matches and only the view differs there is no handle at all, and the rows say so.
      if (g.route !== location.pathname) {
        const go = mk('button', 'go', 'go')
        go.dataset.route = g.route
        h.append(go)
      }
      list.append(h)
      for (const p of g.rows) {
        // An add pin has no element to find and never will — it is about a gap. Running the lookup
        // on it would report `could not locate`, which reads as the lookup failing rather than as
        // the point of the pin.
        const node = now && !p.anchor ? locateRow(p, here) : null
        const row = mk('li', `row${node ? '' : ' cold'}`)
        row.dataset.id = p.id ?? ''
        row.title = whereLabel(p)
        row.append(
          mk('span', 'said', p.said ?? ''),
          mk('span', 'where', node || p.anchor ? whereLabel(p) : now ? 'could not locate' : 'not on this screen'),
        )
        const acts = mk('span', 'acts')
        acts.append(mk('button', 'ed', 'edit'), mk('button', 'rm', 'del'))
        row.append(acts)
        if (node) {
          row.onmouseenter = () => paint(node)
          row.onmouseleave = restore
        }
        list.append(row)
      }
    }
  }

  const beginEdit = (id) => {
    const pin = pins.find((p) => p.id === id)
    if (!pin) return
    editing = id
    frozen = true
    head.textContent = `edit · ${id.slice(0, 6)}`
    commitBtn.textContent = 'save ⏎'
    const node = locateRow(pin)
    if (node) {
      // The full selection, resolution included: the panel is about to ask what is wrong with this
      // element, and the answer to that question is the same one it gives on a fresh pin.
      select(node)
    } else {
      // Nothing on this screen to point the panel at, so it goes beside the list rather than
      // hovering over an element that is not the one being talked about.
      why.innerHTML = '<div style="color:#71717a">not on this screen — editing the sentence only</div>'
      panel.style.display = 'block'
      panel.style.left = `${Math.max(8, innerWidth - 360)}px`
      panel.style.top = '80px'
      input.focus()
    }
    input.value = pin.said ?? ''
  }

  // A delete is an appended tombstone, so a mis-delete is a `grep -v` away in pins.jsonl. With the
  // sink down there is nowhere to append it: the row goes from this tab and comes back on reload,
  // which is what `offline` on the chip is there to warn about.
  const del = (id) => {
    const i = pins.findIndex((p) => p.id === id)
    if (i < 0) return
    if (editing === id) clear()
    pins.splice(i, 1)
    post({ op: 'delete', id, at: new Date().toISOString() })
    render()
  }

  // The sink is the record; window.__sdPins is this tab's copy of it. Anything the sink has not
  // heard of — a pin whose POST was rejected, or one taken while this GET was in flight — is kept.
  const hydrate = async () => {
    let served = null
    try {
      const r = await fetch(SINK_LIST, { mode: 'cors' })
      if (r.ok) served = await r.json()
    } catch {
      /* no sink running — the chip says so */
    }
    offline = !Array.isArray(served)
    if (!offline) {
      const known = new Set(served.map((p) => p.id))
      const mine = pins.filter((p) => p.id && !known.has(p.id))
      pins.length = 0
      pins.push(...served, ...mine)
    }
    render()
  }

  const render = () => {
    // The view count is §2.2 in one glance: more views than routes means the tool can tell two
    // screens apart that location.pathname insists are the same screen.
    const views = new Set(pins.map(groupKey)).size
    chip.textContent = on
      ? `pin · ${pins.length}` + (views ? ` · ${views} view${views === 1 ? '' : 's'}` : '') + (offline ? ' · offline' : '')
      : ''
    chip.style.display = on ? 'block' : 'none'
    if (!on) listOpen = false
    list.style.display = on && listOpen ? 'block' : 'none'
    if (on && listOpen) renderList()
  }

  // Every navigation signal converges here. A screen change is a burst, not an event — measured on
  // foji, three screen changes produced 6 MutationObserver batches over 28 records — and the view
  // key costs a forced layout at ~1ms, so they coalesce on a trailing timer instead of each paying
  // for it. Re-rendering only when the key actually moved is what keeps that affordable with the
  // list open, where a render is one querySelectorAll per row.
  const onNav = () => {
    clearTimeout(navT)
    navT = setTimeout(() => {
      // onlook's validateAndCleanSelections, minus the RPC. This is the whole of the liveness fix:
      // the one thing that must never survive a screen change is a highlight box, or a half-typed
      // sentence, still pointing at a node the app has already thrown away.
      if (target && !target.isConnected) clear()
      const v = viewKey()
      if (v === lastView) return
      lastView = v
      // An anchor holds no live node — it is already a path, a class list and two sibling texts —
      // so nothing detaches to catch it. What goes stale is the screen it describes, and a commit
      // after the app has moved on would file that brief under the view key of another screen.
      if (anchor) clear()
      render()
    }, 120)
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
    // The wire format gained op, id, kind and view, and superdesign-pin-contract.md:112 requires
    // the bump on any schema change.
    version: 2,
    view: () => viewKey(),
  }

  addEventListener('mousemove', onMove, true)
  addEventListener('mousedown', onDown, true)
  addEventListener('mouseup', onUp, true)
  addEventListener('click', onClick, true)
  addEventListener('keydown', onKey, true)
  // Also on the shadow root. A keystroke aimed at the textarea is retargeted at the boundary, and
  // whether it reaches a window-level capture listener depends on how it was dispatched — a real
  // keyboard does, some automation drivers do not. Committing is the one action that must never
  // depend on that, so it has two paths that do not share a failure mode: this, and the button.
  shadow.addEventListener('keydown', onKey, true)
  commitBtn.addEventListener('click', (e) => {
    e.preventDefault()
    e.stopPropagation()
    commit()
  })
  chip.title = 'the pins so far · alt-click an element to add one'
  chip.addEventListener('click', (e) => {
    e.preventDefault()
    e.stopPropagation()
    listOpen = !listOpen
    render()
  })
  // Delegated, so a re-render does not have to re-bind two buttons per row. Inside the shadow root
  // the event is not retargeted, so e.target really is the button that was pressed.
  list.addEventListener('click', (e) => {
    if (e.target.classList?.contains('go')) {
      location.href = e.target.dataset.route
      return
    }
    const row = e.target.closest?.('.row')
    if (!row) return
    e.preventDefault()
    e.stopPropagation()
    if (e.target.classList.contains('ed')) beginEdit(row.dataset.id)
    else if (e.target.classList.contains('rm')) del(row.dataset.id)
  })
  // Four free signals and one that costs. The free four cover every navigation that moves the URL;
  // the observer is the only one that fires at all on an app like foji, whose screens are React
  // state and whose URL is `/` on all five of them. history.pushState is deliberately NOT patched:
  // the Navigation API covers Chromium and the observer covers the rest, so the patch would buy a
  // mutated host global and nothing else — and a router that captured the original reference before
  // injection would silently defeat it anyway.
  addEventListener('popstate', onNav)
  addEventListener('hashchange', onNav)
  addEventListener('pageshow', onNav)
  if (typeof navigation === 'object') navigation?.addEventListener?.('navigate', onNav)
  new MutationObserver(onNav).observe(document.documentElement, { childList: true, subtree: true })

  document.documentElement.appendChild(host)
  // Seeded once the host has landed and still ahead of the observer's trailing timer, because that
  // append is itself a mutation and its batch would otherwise report a screen change that was us.
  lastView = viewKey()
  window.__sdPinOverlay = api
  api.toggle()
  // Kept on the api because hydration is the one thing about this overlay that is asynchronous:
  // without a handle, a driver that pins immediately after load races the fetch that is about to
  // replace the array it just pushed into.
  api.hydrated = hydrate()

  console.log(
    '%cpin-overlay%c ready — alt-click an element · alt+shift+P toggles · window.__sdPins',
    `background:${ACCENT};color:#fff;padding:2px 6px;border-radius:2px;font-weight:600`,
    '',
  )
})()
