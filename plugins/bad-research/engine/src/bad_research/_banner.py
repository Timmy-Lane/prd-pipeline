"""The Bad Research wordmark — a chunky block ``BAD`` sign in hyperresearch's
pixel style. Embedded as a constant so it renders from an installed wheel; the
repo also keeps ``assets/banner.txt`` for the README."""

from __future__ import annotations

BANNER = (
    "██████    █████   ██████\n"
    "██   ██  ██   ██  ██   ██\n"
    "██████   ███████  ██   ██\n"
    "██   ██  ██   ██  ██   ██\n"
    "██████   ██   ██  ██████"
)

TAGLINE = "michael jackson bad"

# Warm gradient evoking the hyperresearch wordmark (yellow → pink → purple).
_ROW_COLORS = ("#f5d76e", "#f0a868", "#e87a8a", "#c86fa8", "#9b6fc8")


def render_rich() -> str:
    """The banner as a rich-markup string — one gradient colour per row."""
    rows = [f"[{c}]{line}[/]" for c, line in zip(_ROW_COLORS, BANNER.splitlines(), strict=True)]
    rows.append(f"[dim]         {TAGLINE}[/]")
    return "\n".join(rows)


def render_plain() -> str:
    """The banner as plain text (README / no-colour terminals)."""
    return f"{BANNER}\n         {TAGLINE}"


__all__ = ["BANNER", "TAGLINE", "render_plain", "render_rich"]
