#!/usr/bin/env bash
# anti-slop-gate — the automatable half of the superdesign Phase-4 gate.
# Greps a target dir/file for the grep-detectable tells in the CANONICAL catalog
# (.claude/skills/superdesign/references/anti-slop.md § Automatable detectors + § APP-UI).
# Judge-only tells (mouse-only, missing states, decorative-color-over-hierarchy,
# one-fixed-density, animated ⌘K) can't be grepped — run `--lens` to print that checklist.
# Colour and spring physics are not greppable either: any stylesheet in the target that declares
# chart slots or spring easings is handed to scripts/validate-chart-palette.mjs and
# scripts/spring-tokens.mjs --check, whose exit codes fold into this one.
# Geometry needs a rendered page: that is scripts/design-audit.mjs, run separately.
#
# Usage:
#   scripts/anti-slop-gate.sh <dir-or-file>     # exit 0 = clean, non-zero = tells found
#   scripts/anti-slop-gate.sh --lens <dir>      # also print the judge-only lens checklist
#
# Exit code = number of distinct HARD tells found (0 = pass). `note` lines are reported
# but never counted — they are investigate-not-fail signals.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

LENS=0
if [[ "${1:-}" == "--lens" ]]; then LENS=1; shift; fi
TARGET="${1:-}"
if [[ -z "$TARGET" || ! -e "$TARGET" ]]; then
  echo "usage: $0 [--lens] <dir-or-file>" >&2; exit 2
fi

# Only scan source; never node_modules/dist/build. Strip comment lines to avoid
# flagging a descriptive mention (e.g. "deliberately NOT indigo").
FILES=$(grep -rIl --include='*.tsx' --include='*.ts' --include='*.jsx' --include='*.css' \
        --exclude-dir=node_modules --exclude-dir=dist --exclude-dir=build -e '' "$TARGET" 2>/dev/null)
[[ -z "$FILES" ]] && FILES="$TARGET"
# shellcheck disable=SC2086
scan() { grep -nHE "$1" $FILES 2>/dev/null | grep -vE '^\s*[^:]*:[0-9]+:\s*(//|/\*|\*)' ; }

hits=0
flag() { # <name> <matches>
  if [[ -n "$2" ]]; then
    hits=$((hits+1))
    echo "✗ SLOP: $1"
    echo "$2" | sed 's/^/    /' | head -6
  fi
}
note() { # <name> <matches> — investigate, never fail. Does NOT move the exit code.
  if [[ -n "$2" ]]; then
    echo "· NOTE: $1"
    echo "$2" | sed 's/^/    /' | head -6
  fi
}
nonblank() { grep -vE '^[[:space:]]*$' || true; }

# 1. Default indigo/violet/purple accent as a Tailwind utility or hex (not a comment).
flag "indigo/violet/purple default accent" \
  "$(scan '\b(bg|text|border|ring|from|via|to)-(indigo|violet|purple)-|#6366f1|#8b5cf6')"

# 1b. Tailwind's purple/indigo/violet arriving as a raw OKLCH triple through a token
#     (shadcn's default dark --chart-4 IS Tailwind purple-500). A hex/utility grep
#     can never see these.
#     Window: L 0.40-0.79, C >= 0.15, hue 270-319. Handles both `0.627` and `62.7%` notation.
#     The lower bound is 270, not 250, and the boundary is measured from Tailwind's own
#     palette: blue-700 sits at hue 264.376 and blue-800 at 265.638, while indigo-500 —
#     the first genuinely indigo step — is 277.117 (violet-500 292.717, purple-500 303.9).
#     A 250 floor flagged every blue brand as purple; e.g. `oklch(0.55 0.19 255)` is a
#     plain blue --info token. Blue shadcn DEFAULTS are still caught, by exact value, in 1c —
#     "is this a stock token" and "is this the reflexive purple" are two different questions
#     and one detector must not answer both.
#     Two exemptions, or the rule punishes every legitimately violet brand:
#       (a) a custom property NAMED in DESIGN.md is the project's declared brand hue;
#       (b) a --chart-N slot in a stylesheet whose palette already passes
#           scripts/validate-chart-palette.mjs — a computed check outranks a hue heuristic.
#           (Verified: shadcn's own defaults fail that validator, so this is not a hole.)
purple="$(scan 'oklch\(\s*(0?\.[4-7][0-9]*|[4-7][0-9](\.[0-9]+)?%)\s+0?\.(1[5-9]|[23][0-9])[0-9]*\s+(2[7-9][0-9]|3[01][0-9])(\.[0-9]+)?\s*\)')"
if [[ -n "$purple" ]]; then
  designmd=""
  for c in "$TARGET/DESIGN.md" "$(dirname "$TARGET")/DESIGN.md" "$HERE/../DESIGN.md"; do
    [[ -f "$c" ]] && { designmd="$c"; break; }
  done
  if [[ -n "$designmd" ]]; then
    declared="$(grep -oE -- '--[a-z0-9-]+' "$designmd" | sort -u | paste -sd'|' -)"
    [[ -n "$declared" ]] && purple="$(printf '%s\n' "$purple" | grep -vE -- "($declared)[[:space:]]*:" | nonblank)"
  fi
  for f in $(printf '%s\n' "$purple" | cut -d: -f1 | sort -u); do
    grep -qE -- '--chart-1[[:space:]]*:' "$f" 2>/dev/null || continue
    if command -v node >/dev/null && node "$HERE/validate-chart-palette.mjs" "$f" >/dev/null 2>&1; then
      purple="$(printf '%s\n' "$purple" | grep -vE -- "^$f:[0-9]+:.*--chart-[0-9]" | nonblank)"
    fi
  done
fi
flag "Tailwind purple/violet/indigo laundered through an OKLCH token" "$purple"

# 1c. Byte-identical shadcn default chromatic tokens (chart + destructive + sidebar).
flag "unedited shadcn default chart/destructive palette (= Tailwind palette in OKLCH)" \
  "$(scan '0\.646 0\.222 41|0\.6 0\.118 184|0\.398 0\.07 227|0\.828 0\.189 84|0\.769 0\.188 70|0\.488 0\.243 264|0\.696 0\.17 162|0\.627 0\.265 30[34]|0\.645 0\.246 16|0\.577 0\.245 27|0\.704 0\.191 22')"

# 2. Colored left-border strip (card/nav tell).
flag "colored left-border strip" \
  "$(scan '\bborder-l-(2|4|8)\b.*\b(border-)?(red|blue|green|amber|teal|primary|indigo|violet|purple)-|border-left:\s*[0-9]')"

# 3. Brand hue as the active/selected row FILL (should be a neutral accent).
flag "brand hue as active/selected fill" \
  "$(scan 'data-\[(state=selected|active=true)\][^\"'\'' ]*:?bg-primary|aria-current[^>]*bg-primary')"

# 4. Banned display fonts (Inter/Roboto/Open Sans/Lato as the face) — CSS or JSX inline style.
flag "banned default display font" \
  "$(scan 'font-?[Ff]amily:\s*[\"'\'']?(Inter|Roboto|Open Sans|Lato)\b|--font-(sans|display):[^;]*(Inter|Roboto)\b')"

# 5. Off-scale arbitrary spacing: p-/m-/gap-[Npx] outside the declared ramp.
#    Enumerated, not `n % 4`: the modulo rule passes 20/28/36/40/44 — every value the ramp
#    deliberately omits — and would false-flag the two Fluent "Nudge" half-steps (6, 10).
SCALE=" 0 1 2 4 6 8 10 12 16 24 32 48 64 96 "
offscale=""
while IFS= read -r line; do
  n=$(sed -E 's/.*[pmg][xytrbl]?-\[([0-9]+)px\].*/\1/' <<<"$line")
  [[ "$n" =~ ^[0-9]+$ ]] && [[ "$SCALE" != *" $n "* ]] && offscale+="$line"$'\n'
done < <(scan '\b[pmg][xytrbl]?-\[[0-9]+px\]')
flag "off-scale spacing (outside the declared ramp)" "$offscale"

# 6. One flat black shadow reused (rgba(0,0,0,0.1)) rather than a role-based scale.
flatshadow="$(scan 'rgba\(0,\s*0,\s*0,\s*0?\.1\)' | head -20)"
[[ $(printf '%s\n' "$flatshadow" | grep -c .) -ge 4 ]] && flag "flat uniform 0.1 black shadow reused" "$flatshadow"

# 7. Leading emoji in a heading. BSD grep lacks \x{} PCRE ranges — use perl (supports \x{},
# resets $. per file via `close ARGV if eof`).
# shellcheck disable=SC2086
emoji="$(perl -CSD -ne 'print "$ARGV:$.: $_" if /<h[1-6][^>]*>\s*[\x{1F000}-\x{1FAFF}\x{2600}-\x{27BF}\x{2190}-\x{21FF}]/; close ARGV if eof;' $FILES 2>/dev/null)"
flag "leading emoji in heading" "$emoji"

# 8. Tailwind v3 syntax in a v4 project = stale-weights leak, not a style choice.
#    Source: tailwindcss.com/docs/upgrade-guide. Bare `ring` is v3's 3px default ring; it must be a
#    whole utility inside a class attribute, or the rule eats the word "ring" in prose AND the `ring`
#    half of v4's own `ring-ring` colour utility.
if grep -rq '@import "tailwindcss"' "$TARGET" 2>/dev/null; then
  flag "Tailwind v3 syntax in a v4 project (stale-weights leak)" \
    "$(scan '@tailwind (base|components|utilities)|bg-gradient-to-|focus:outline-none|\bflex-(shrink|grow)-|\b(bg|text|border)-opacity-[0-9]|overflow-ellipsis|decoration-slice|class(Name)?="([^"]*[[:space:]:])?ring([[:space:]]|")')"
fi

# 9./10. Comment-borne tells. Raw grep, NOT scan() — scan() strips comment lines, which is
# exactly what these two detectors read. (Routing 10 through scan() returns zero hits.)
# shellcheck disable=SC2086
flag "banned output marker (lazy stub / self-narration)" \
  "$(grep -nHE '//[[:space:]]*(\.\.\.|rest of( the)? code|implement here|TODO|similar to above|continue pattern|add more as needed)|/\*[[:space:]]*\.\.\.[[:space:]]*\*/|for brevity|the rest follows the same pattern|similarly for the remaining|and so on|I.ll leave that as an exercise' $FILES 2>/dev/null)"
# shellcheck disable=SC2086
flag "self-narrating comment in shipped code" \
  "$(grep -nHE '//[[:space:]]*(Now |Next,|Here we|We (also )?(need|want|will)|Let.s |This (is|will) )' $FILES 2>/dev/null)"

# 11. Tailwind v4: outline-none also kills the forced-colors outline — the reset is outline-hidden.
#     Only a defect when nothing restores a visible indicator. shadcn's own primitives pair
#     `outline-none` with `focus-visible:ring-[3px]` on the same class string, which is correct;
#     flagging the bare token made every vetted primitive a tell and taught the reader to
#     ignore the detector. Fire only on the lines that strip the outline and put nothing back.
flag "outline-none with no focus-visible replacement" \
  "$(scan '\boutline-none\b' | grep -v 'focus-visible' | nonblank)"

# 12. Round target below the SC 2.5.8 inscribed-square size (needs d >= 34px => size-9).
#     NOTE, not a hard tell: grep sees geometry, never interactivity. A `size-4 rounded-full`
#     may be a switch thumb (`pointer-events-none`, not a target at all) or a decorative dot,
#     and `h-5 w-9 rounded-full` is a pill track whose inscribed square is not its height.
#     Those two shapes are excluded outright; what survives still needs a human to confirm the
#     element is a target before it is a violation.
round="$(scan 'rounded-full[^"'\'']*\b(size|h)-(4|5|6|7|8)\b|\b(size|h)-(4|5|6|7|8)\b[^"'\'']*rounded-full' \
  | grep -vE 'pointer-events-none|aria-hidden' \
  | grep -vE '\bh-[0-9]+\b[^"'\'']*\bw-[0-9]+\b|\bw-[0-9]+\b[^"'\'']*\bh-[0-9]+\b' | nonblank)"
note "round element < 34px — a violation only if it is a target (SC 2.5.8 inscribed square)" "$round"

# 12b. The placeholder font shipped as-is. tokens.md/theme.css plant this marker precisely
#      so the gate can catch a theme that was generated and never art-directed.
flag "placeholder font never replaced" "$(scan 'REPLACE-ME-FONT')"

# 13. Positive tabIndex breaks focus order (SC 2.4.3).
flag "positive tabIndex" "$(scan 'tabIndex=\{[1-9]')"

# 14. Legacy ARIA 1.0/1.1 combobox shape.
flag "legacy combobox (aria-owns / role=combobox on a non-input)" \
  "$(scan 'aria-owns=|<(div|span)[^>]*role="combobox"')"

# 15. Render-blocking Google Fonts @import (LCP) — link+preconnect or self-host instead.
flag "render-blocking @import of Google Fonts" \
  "$(scan '@import\s+url\(.{0,2}https://fonts\.googleapis\.com')"

# 16. transition-all repaints properties you never meant to animate (motion + INP tell).
flag "transition-all" "$(scan '\btransition-all\b')"

# 17. <img> with no intrinsic size => CLS. Perl, same idiom as the emoji rule.
# shellcheck disable=SC2086
imgnodim="$(perl -ne 'print "$ARGV:$.: $_" if /<img\b/ && !/\bwidth=/ && !/\bfill\b/; close ARGV if eof;' $FILES 2>/dev/null)"
flag "img without width/height (CLS)" "$imgnodim"

# 18. No reduced-motion reset anywhere in the target (SC 2.3.3).
# shellcheck disable=SC2086
grep -rq 'prefers-reduced-motion' $FILES 2>/dev/null || flag "no prefers-reduced-motion reset" "(none found under $TARGET)"

# 19. Generator deployment artifact left in the build. Palette-based generator attribution is
#     not supportable; a deploy string is (class D, seconds to check).
flag "generator deployment artifact left in the build" \
  "$(scan 'lovable\.dev|Built with v0|Built on Lovable|\.replit\.dev|Crafted with love|Built with care')"

# 20. State-coverage ratio over data-rendering components.
# shellcheck disable=SC2086
data_files=$(grep -rlE 'useQuery|useSWR|await fetch|\.map\(' $FILES 2>/dev/null)
missing=""; total=0
for f in $data_files; do
  total=$((total+1))
  grep -qE 'isLoading|isPending|Skeleton' "$f" && grep -qE 'isError|error' "$f" \
    && grep -qE '\.length === 0|<Empty' "$f" || missing+="$f"$'\n'
done
(( total > 0 )) && flag "data components missing loading/error/empty ($(printf '%s' "$missing" | grep -c .)/$total)" "$missing"

# 21. Theme-level checks are computed, not grepped: hand off any stylesheet that declares chart
#     slots or spring easings to the two generators/validators that own those numbers.
if command -v node >/dev/null; then
  # shellcheck disable=SC2086
  for t in $(grep -rlE -- '--chart-1[[:space:]]*:|--ease-spring-' $FILES 2>/dev/null); do
    grep -qE -- '--chart-1[[:space:]]*:' "$t" && {
      out="$(node "$HERE/validate-chart-palette.mjs" "$t" 2>&1)" \
        || flag "chart palette fails its computed checks ($t)" "$out"
    }
    grep -qE -- '--ease-spring-' "$t" && {
      out="$(node "$HERE/spring-tokens.mjs" --check "$t" 2>&1)" \
        || flag "spring tokens drifted from the generator ($t)" "$out"
    }
  done
else
  note "node not found — chart-palette and spring-token validators were SKIPPED" "(install node; greps alone cannot check colour or physics)"
fi

# Investigate-not-fail: curly quotes are a ChatGPT/DeepSeek default, but Chicago style, Word and
# macOS substitution produce them too. Reported, never counted.
# shellcheck disable=SC2086
curly="$(perl -CSD -ne 'print "$ARGV:$.: $_" if /[\x{2018}\x{2019}\x{201C}\x{201D}]/; close ARGV if eof;' $FILES 2>/dev/null | head -10)"
note "curly quotes/apostrophes in source strings (ChatGPT/DeepSeek tell)" "$curly"

echo ""
if (( hits == 0 )); then echo "✓ anti-slop gate: CLEAN ($TARGET)"; else echo "✗ anti-slop gate: $hits tell(s) found in $TARGET"; fi

if (( LENS == 1 )); then
  cat <<'LENS'

── product-taste judge-lens (judge-only tells greps CANNOT see — review manually / with a blind judge) ──
  [ ] Keyboard-first? global ⌘K, single-letter/ G-letter actions, keyboard row nav — NOT mouse-only.
  [ ] Full state machine present? default/hover/focus-visible/active/disabled/loading/empty/error.
  [ ] Hierarchy from spacing + weight, NOT decorative color? (no colored chips carrying meaning color alone).
  [ ] Density is a choice? at least compact/comfortable tiers, not one fixed airy height.
  [ ] ⌘K / high-frequency surfaces open at 0ms? (an animated command palette is a motion fingerprint).
  [ ] Focus ring: 3:1 vs BOTH adjacent colors, in every state, on light AND dark surfaces?
      Inset rings (outline-offset negative / inset box-shadow / border) must be >= 3px, not 2px.
  [ ] Dialog: initial focus on a static element or the LEAST destructive button — never autofocus destroy?
      Focus restored to the invoker on close?
  [ ] Every drag has a single-POINTER (tap/click) alternative — keyboard support does not satisfy 2.5.7?
  [ ] Auth: paste allowed, password managers not blocked, OTP is one input with autocomplete="one-time-code"?
  A screen that passes every grep above and still reads generic has FAILED this lens.
LENS
fi

exit "$hits"
