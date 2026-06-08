"""Keyless source-type tiers — classify_source + the 6 extractors (dossier 12 §A-F).

Each extractor emits the normalized vault note shape (dossier 12 §"normalized vault
note"). yt-dlp + git are EXTERNAL CLIs: detected at call time, degrade gracefully via
ExtractorUnavailable when absent. KNOWN = repo/dossier convention; DESIGNED = the port.
"""

from __future__ import annotations

import glob
import gzip
import io
import os
import re
import shutil
import subprocess
import tarfile
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlparse

import httpx

from bad_research.core.fetcher import assert_url_safe, safe_redirect_get


def _safe_get(url: str, *, timeout: float, headers: dict[str, str] | None = None) -> httpx.Response:
    """GET `url` with per-redirect SSRF re-validation (FIX 2).

    Every extractor used `httpx.get(url, follow_redirects=True)`, which httpx follows
    with NO further SSRF check — a public URL that 302s to `http://169.254.169.254/`
    (cloud metadata) or another internal host would be fetched silently. This wraps the
    kept `safe_redirect_get` (core/fetcher): an httpx.Client with redirects DISABLED,
    walking the chain manually and calling `assert_url_safe` on every hop. The entry
    `assert_url_safe(url)` checks at the call sites stay (defence-in-depth on the first
    hop); this closes the redirect bypass exactly as `_static_fetch` already does.
    """
    with httpx.Client(follow_redirects=False, timeout=timeout) as client:
        resp: httpx.Response = safe_redirect_get(client, url, headers=headers)
        return resp


class ExtractorUnavailable(RuntimeError):
    """A required external CLI (yt-dlp / git) is not installed.

    Carries an `install_hint`. The orchestrator catches this and skips the tier
    (graceful degradation) rather than crashing the run.
    """

    def __init__(self, tool: str, install_hint: str) -> None:
        self.tool = tool
        self.install_hint = install_hint
        super().__init__(f"{tool} not found on PATH — {install_hint}")


def _iso(raw: str | None) -> str | None:
    """Normalize a date string to an ISO date, or None. Uses dateparser (keyless).

    Handles yt-dlp's compact YYYYMMDD `upload_date` form (dateparser does not), then
    falls back to dateparser for ISO/RFC/free-text dates from feeds and Atom.
    """
    if not raw:
        return None
    raw = raw.strip()
    # yt-dlp upload_date is always 8 bare digits (YYYYMMDD); dateparser misses it.
    if re.fullmatch(r"\d{8}", raw):
        return f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}"
    import dateparser  # type: ignore[import-untyped]

    dt = dateparser.parse(raw)
    return dt.date().isoformat() if dt else None


def _html_to_md(html: str) -> str:
    """Minimal HTML->text for feed summaries (no full pipeline needed)."""
    from bs4 import BeautifulSoup

    return BeautifulSoup(html or "", "lxml").get_text("\n", strip=True)


def _now() -> str:
    return datetime.now(UTC).isoformat()


def classify_source(url: str) -> str:
    """URL-shape classifier, runs BEFORE the byte-fetch (dossier 12 §"Routing"). KNOWN.

    Returns one of: youtube | github | arxiv | feed | sitemap | llms_txt | html_or_pdf.
    For non-html_or_pdf types you must NOT scrape the URL's HTML — call the matching
    keyless extractor against the same identifier instead.
    """
    h = urlparse(url).hostname or ""
    if re.search(r"(youtube\.com/watch|youtu\.be/|youtube\.com/shorts)", url):
        return "youtube"
    if h == "github.com" and len(urlparse(url).path.strip("/").split("/")) >= 2:
        return "github"
    if re.search(r"arxiv\.org/(abs|pdf)/", url):
        return "arxiv"
    if url.rstrip("/").endswith(("/llms.txt", "/llms-full.txt")):
        return "llms_txt"
    if url.rstrip("/").endswith(("sitemap.xml", "/sitemap_index.xml")):
        return "sitemap"
    if re.search(r"(/feed/?$|/rss/?$|\.rss$|\.atom$|/atom\.xml$|/feed\.xml$)", url):
        return "feed"
    return "html_or_pdf"


def _clean_vtt(vtt: str) -> str:
    """Deterministic VTT clean (dossier 12 §A). DESIGNED (the repo's strip-VTT convention).

    Drops WEBVTT/Kind/Language headers + timestamp lines; strips inline <..> timing/<c>
    tags; takes each cue block's fullest line; dedups rolling captions (a cue that is a
    prefix of the next is dropped) + adjacent exact repeats.
    """
    lines: list[str] = []
    prev = ""
    for blk in vtt.split("\n\n"):
        txt = [
            ln for ln in blk.splitlines()
            if ln and "-->" not in ln
            and not ln.startswith(("WEBVTT", "Kind:", "Language:"))
        ]
        if not txt:
            continue
        cue = re.sub(r"<[^>]+>", "", txt[-1]).strip()
        if cue and cue != prev and not prev.endswith(cue):
            lines.append(cue)
            prev = cue
    # final adjacent-dedup
    out: list[str] = []
    for ln in lines:
        if not out or out[-1] != ln:
            out.append(ln)
    return "\n".join(out)


def _require_cli(tool: str, hint: str) -> None:
    if shutil.which(tool) is None:
        raise ExtractorUnavailable(tool, hint)


def _ytdlp_subs_dir(url: str) -> str:  # pragma: no cover - patched in tests
    import tempfile

    return tempfile.mkdtemp(prefix="bad_yt_")


def _ytdlp_json(url: str) -> dict[str, Any]:  # pragma: no cover - patched in tests
    out = subprocess.run(
        ["yt-dlp", "--skip-download", "--dump-json", url],
        capture_output=True, text=True, check=True,
    )
    import json as _json

    return _json.loads(out.stdout or "{}")  # type: ignore[no-any-return]


def youtube_transcript(url: str) -> dict[str, Any]:
    """yt-dlp caption track -> densify-ready transcript note (dossier 12 §A). KNOWN command.

    --skip-download => no video bytes, no Data-API call, keyless. Degrades via
    ExtractorUnavailable when yt-dlp is not installed. The host-model densification
    (the §6 pattern) is applied by the orchestrator, not here.
    """
    _require_cli("yt-dlp", "install with: pipx install yt-dlp (or brew install yt-dlp)")
    out_dir = _ytdlp_subs_dir(url)
    subprocess.run(
        ["yt-dlp", "--write-sub", "--write-auto-sub", "--sub-lang", "en",
         "--skip-download", "--sub-format", "vtt",
         "-o", os.path.join(out_dir, "%(id)s.%(ext)s"), url],
        capture_output=True, text=True, check=True,
    )
    vtt_files = sorted(glob.glob(os.path.join(out_dir, "*.vtt")))
    body = ""
    if vtt_files:
        with open(vtt_files[0], encoding="utf-8") as fh:
            body = _clean_vtt(fh.read())
    meta = _ytdlp_json(url)
    return {
        "title": meta.get("title"),
        "source": url,
        "source_type": "youtube",
        "fetched_at": _now(),
        "published": _iso(meta.get("upload_date")),
        "provenance": "yt-dlp --write-sub --write-auto-sub --sub-lang en "
                      "--skip-download --sub-format vtt",
        "markdown": body,
    }


_KEY_SOURCE_GLOBS = ("**/*.py", "**/*.ts", "**/*.rs", "**/*.go",
                     "pyproject.toml", "Dockerfile", "**/*.md")


def github_clone_notes(repo_url: str) -> list[dict[str, Any]]:
    """git clone --depth=1 -> per-file notes (dossier 12 §B). KNOWN.

    Shallow clone over smart-HTTP (no REST 60/hr cap). Degrades via ExtractorUnavailable
    when git is absent. Reads README + key source files into normalized notes.
    """
    _require_cli("git", "install git (https://git-scm.com/downloads)")
    slug = "/".join(urlparse(repo_url).path.strip("/").split("/")[:2])
    import tempfile

    dst = tempfile.mkdtemp(prefix="bad_gh_")
    subprocess.run(
        ["git", "clone", "--depth=1", f"https://github.com/{slug}.git", dst],
        capture_output=True, text=True, check=True,
    )
    if not os.path.isdir(os.path.join(dst, ".git")):
        raise RuntimeError(f"clone did not land for {slug}")
    notes: list[dict[str, Any]] = []
    seen: set[str] = set()
    for pat in _KEY_SOURCE_GLOBS:
        for fp in glob.glob(os.path.join(dst, pat), recursive=True):
            if fp in seen or not os.path.isfile(fp):
                continue
            seen.add(fp)
            rel = os.path.relpath(fp, dst)
            try:
                with open(fp, encoding="utf-8", errors="replace") as fh:
                    text = fh.read()
            except Exception:
                continue
            notes.append({
                "title": f"{slug}:{rel}",
                "source": f"https://github.com/{slug}/blob/HEAD/{rel}",
                "source_type": "github",
                "fetched_at": _now(),
                "published": None,
                "provenance": f"git clone --depth=1 https://github.com/{slug}.git",
                "markdown": f"```\n{text}\n```" if not rel.endswith(".md") else text,
            })
    return notes


def github_file(owner: str, repo: str, path: str,
                branch: str | None = None) -> dict[str, Any]:
    """Single file via raw.githubusercontent.com (CDN, uncapped) (dossier 12 §B). KNOWN."""
    if branch is None:
        meta_url = f"https://api.github.com/repos/{owner}/{repo}"
        assert_url_safe(meta_url)
        branch = _safe_get(meta_url, timeout=15).json().get(
            "default_branch", "main"
        )
    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"
    assert_url_safe(raw_url)
    text = _safe_get(raw_url, timeout=15).text
    return {
        "title": f"{owner}/{repo}:{path}",
        "source": f"https://github.com/{owner}/{repo}/blob/{branch}/{path}",
        "source_type": "github",
        "fetched_at": _now(),
        "published": None,
        "provenance": f"GET {raw_url}",
        "markdown": text,
    }


def _arxiv_atom_meta(aid: str) -> dict[str, Any]:  # pragma: no cover - patched in tests
    import feedparser  # type: ignore[import-untyped]

    f = feedparser.parse(f"https://export.arxiv.org/api/query?id_list={aid}")
    if not f.entries:
        return {"title": aid, "published": None}
    e = f.entries[0]
    return {"title": e.get("title"), "published": _iso(e.get("published"))}


def _detex(tex: str) -> str:
    """Cheap LaTeX -> markdown (dossier 12 §C). DESIGNED. pandoc if present, else regex."""
    body = tex.split(r"\begin{document}", 1)[-1]
    body = re.sub(r"(?m)%.*$", "", body)                       # drop comments
    if shutil.which("pandoc"):
        try:
            out = subprocess.run(
                ["pandoc", "-f", "latex", "-t", "gfm"],
                input=body, capture_output=True, text=True, timeout=30,
            )
            if out.returncode == 0 and out.stdout.strip():
                return out.stdout
        except Exception:
            pass
    body = re.sub(r"\\section\*?\{([^}]*)\}", r"## \1", body)
    body = re.sub(r"\\subsection\*?\{([^}]*)\}", r"### \1", body)
    body = re.sub(r"\\textbf\{([^}]*)\}", r"**\1**", body)
    body = re.sub(r"\\item\s*", "- ", body)
    body = re.sub(r"\\end\{document\}", "", body)
    body = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?", "", body)    # strip remaining commands
    body = body.replace("{", "").replace("}", "")
    return re.sub(r"\n{3,}", "\n\n", body).strip()


def _extract_tex(raw: bytes) -> str:
    """Untar/gunzip the arXiv source tarball, concat all .tex (dossier 12 §C). KNOWN."""
    try:
        with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as tar:
            texts = []
            for m in tar.getmembers():
                if m.name.endswith(".tex") and m.isfile():
                    f = tar.extractfile(m)
                    if f:
                        texts.append(f.read().decode("utf-8", errors="replace"))
            return "\n".join(texts)
    except (tarfile.TarError, OSError):
        try:
            return gzip.decompress(raw).decode("utf-8", errors="replace")
        except OSError:
            return raw.decode("utf-8", errors="replace")


def arxiv_source_notes(url: str) -> dict[str, Any]:
    """arXiv LaTeX source tarball -> note (dossier 12 §C). KNOWN. Prefer over the PDF.

    export.arxiv.org/e-print/<id> is keyless (no token). De-TeX the source; metadata
    from the keyless Atom export API.
    """
    m = re.search(r"arxiv\.org/(?:abs|pdf)/([\d.]+(?:v\d+)?)", url)
    aid = m.group(1) if m else url.rstrip("/").split("/")[-1]
    src_url = f"https://export.arxiv.org/e-print/{aid}"
    assert_url_safe(src_url)
    raw = _safe_get(src_url, timeout=30).content
    body = _detex(_extract_tex(raw))
    meta = _arxiv_atom_meta(aid)
    return {
        "title": meta.get("title"),
        "source": f"https://arxiv.org/abs/{aid}",
        "source_type": "arxiv_src",
        "fetched_at": _now(),
        "published": meta.get("published"),
        "provenance": f"GET export.arxiv.org/e-print/{aid}",
        "markdown": body,
    }


def feed_notes(feed_url: str) -> list[dict[str, Any]]:
    """RSS/Atom -> per-entry normalized notes (dossier 12 §D). KNOWN (feedparser).

    Accepts a feed URL or a raw XML string (feedparser handles both). Each entry yields
    {title, source=link, published, markdown}; full-content feeds inline the body.
    """
    import feedparser

    f = feedparser.parse(feed_url)
    out: list[dict[str, Any]] = []
    for e in f.entries:
        body = ""
        if e.get("content"):
            body = e["content"][0].get("value", "")
        body = body or e.get("summary", "")
        out.append({
            "title": e.get("title"),
            "source": e.get("link"),
            "source_type": "feed",
            "fetched_at": _now(),
            "published": _iso(e.get("published") or e.get("updated")),
            "provenance": f"feedparser {feed_url}",
            "markdown": _html_to_md(body),
        })
    return out


def _discover_sitemap(host: str) -> str:
    """robots.txt Sitemap: directive, else /sitemap.xml (dossier 12 §E)."""
    robots_url = f"https://{host}/robots.txt"
    assert_url_safe(robots_url)
    try:
        r = _safe_get(robots_url, timeout=15)
        for line in r.text.splitlines():
            if line.lower().startswith("sitemap:"):
                return line.split(":", 1)[1].strip()
    except Exception:
        pass
    return f"https://{host}/sitemap.xml"


def _sitemap_urls_from(sitemap_url: str) -> list[dict[str, Any]]:
    assert_url_safe(sitemap_url)
    root = ET.fromstring(_safe_get(sitemap_url, timeout=15).content)
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    if root.tag.endswith("sitemapindex"):
        out: list[dict[str, Any]] = []
        for c in root.findall(".//s:loc", ns):
            if c.text:
                out.extend(_sitemap_urls_from(c.text))
        return out
    return [
        {
            "source": loc.findtext("s:loc", None, ns),
            "published": _iso(loc.findtext("s:lastmod", None, ns)),
            "source_type": "sitemap",
        }
        for loc in root.findall(".//s:url", ns)
    ]


def sitemap_urls(host: str) -> list[dict[str, Any]]:
    """sitemap.xml -> {url, lastmod} crawl-frontier seeds (dossier 12 §E). KNOWN.

    robots.txt Sitemap: directive (authoritative) > /sitemap.xml; recurse into a
    sitemapindex. lastmod is the recency signal. Emits seeds, not content.
    """
    return _sitemap_urls_from(_discover_sitemap(host))


def llms_txt_notes(host: str) -> dict[str, Any] | list[dict[str, Any]]:
    """/llms-full.txt (whole corpus, one note) else /llms.txt link-harvest (§F). KNOWN.

    llms-full.txt present -> one pre-cleaned note (skip §2-6). Only llms.txt -> a curated,
    summarized link index harvested as crawl seeds.
    """
    full_url = f"https://{host}/llms-full.txt"
    assert_url_safe(full_url)
    full = _safe_get(full_url, timeout=15)
    if full.status_code == 200 and full.text.strip():
        return {
            "title": f"{host} docs (llms-full)",
            "source": full_url,
            "source_type": "llms_txt",
            "fetched_at": _now(),
            "published": None,
            "provenance": f"GET {host}/llms-full.txt",
            "markdown": full.text,
        }
    idx_url = f"https://{host}/llms.txt"
    assert_url_safe(idx_url)
    idx = _safe_get(idx_url, timeout=15)
    links = re.findall(r"\[([^\]]+)\]\((https?://[^)]+)\)", idx.text)
    return [
        {
            "title": t,
            "source": u,
            "source_type": "llms_txt",
            "fetched_at": _now(),
            "published": None,
            "provenance": f"link in {host}/llms.txt",
            "markdown": "",
        }
        for t, u in links
    ]
