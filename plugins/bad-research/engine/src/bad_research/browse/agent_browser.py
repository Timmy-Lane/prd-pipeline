"""AgentBrowserProvider — keyless agentic browse on the local `agent-browser` CLI.

agent-browser (vercel-labs/agent-browser) is a native Rust CLI that drives a LOCAL
headless Chrome-for-Testing (or `--engine lightpanda`) over CDP. It is keyless: the
only keyed surfaces are `-p <cloud-provider>` and the built-in `chat` command, both of
which we never use (dossier 14 §1, §9). Claude Code (the host model) IS the agent brain
— it reasons over the @eN accessibility-snapshot text and supplies the next action; no
paid LLM call is ever made (dossier 14 §4).

This module:
  * _AgentBrowserCLI  — builds argv vectors + runs them via an injectable runner.
  * Snapshot          — parses `snapshot -i --json` stdout into {text, refs} (Task 3).
  * AgentBrowserProvider — the snapshot/ReAct browse loop returning WebResult (Task 4).
  * Stagehand act/extract/observe prompt constants (verbatim, dossier 14 §5).

agent-browser/lightpanda are EXTERNAL CLIs (NOT pip deps). `is_available()` gates
construction so the ladder degrades to crawl4ai/httpx when they are absent.
"""

from __future__ import annotations

import inspect
import json
import os
import re
import shutil
import subprocess
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Literal

from bad_research.web.base import WebResult

# ---- frozen constants (INTERFACES_KEYLESS §8 + dossier 14) ----
DEFAULT_MAX_STEPS = 12             # INTERFACES_KEYLESS §4.3 Protocol default
WAIT_TIMEOUT_MS = 25_000           # dossier 14 §3.5 (below the 30s IPC read timeout)
CLI_TIMEOUT_S = 60                 # dossier 14 §4.1 (chat.rs:226 tool timeout)
AXTREE_MAX_CHARS = 280_000         # dossier 14 §5.4 chunking heuristic
MIN_REFS_FOR_NONEMPTY = 2          # dossier 14 §12.5 lightpanda→chrome fallback floor
DEFAULT_ENGINE: Literal["lightpanda", "chrome"] = "lightpanda"
AB_PROGRAM = "agent-browser"

# A subprocess runner: (argv, *, timeout, env, stdin) -> (returncode, stdout, stderr).
Runner = Callable[..., tuple[int, str, str]]


def _default_runner(argv: list[str], *, timeout: float | None = None,
                    env: dict[str, str] | None = None,
                    stdin: str | None = None) -> tuple[int, str, str]:
    """The production runner: subprocess.run. Captures stdout/stderr text. Never raises on
    non-zero exit (the caller inspects returncode)."""
    proc = subprocess.run(
        argv, capture_output=True, text=True, timeout=timeout,
        env=env, input=stdin,
    )
    return (proc.returncode, proc.stdout or "", proc.stderr or "")


def is_available(program: str = AB_PROGRAM) -> bool:
    """True iff the agent-browser CLI is on PATH (detect-and-degrade contract)."""
    return shutil.which(program) is not None


def _runner_accepts_stdin(runner: Runner) -> bool:
    """Best-effort: does the runner accept a `stdin=` kwarg? Default runner & FakeRunner do."""
    try:
        sig = inspect.signature(runner)
    except (TypeError, ValueError):
        return False
    return "stdin" in sig.parameters or any(
        p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()
    )


class _AgentBrowserCLI:
    """Builds + runs agent-browser command argv. The runner is injectable so tests assert
    the constructed argv and feed canned stdout (NO real subprocess in tests)."""

    def __init__(
        self,
        *,
        engine: Literal["lightpanda", "chrome"] = DEFAULT_ENGINE,
        runner: Runner | None = None,
        session: str | None = None,
        state: str | None = None,
        headers: str | None = None,
        program: str = AB_PROGRAM,
        timeout_s: float = CLI_TIMEOUT_S,
    ) -> None:
        self.engine = engine
        self._runner = runner or _default_runner
        self.session = session
        self.state = state
        self.headers = headers
        self.program = program
        self.timeout_s = timeout_s

    # ---- argv prefix: program + global flags (order is stable, asserted by tests) ----
    def _prefix(self) -> list[str]:
        argv = [self.program, "--engine", self.engine]
        if self.session:
            argv += ["--session", self.session]
        if self.state:
            argv += ["--state", self.state]
        if self.headers:
            argv += ["--headers", self.headers]
        return argv

    def _env(self) -> dict[str, str] | None:
        if self.engine == "lightpanda":
            env = dict(os.environ)
            env["LIGHTPANDA_DISABLE_TELEMETRY"] = "true"  # dossier 14 §12.1
            return env
        return None

    def _run(self, *args: str, stdin: str | None = None) -> str:
        argv = self._prefix() + list(args)
        env = self._env()
        # Pass stdin only when the runner accepts it; otherwise fall back to argv-only.
        if _runner_accepts_stdin(self._runner):
            _rc, out, _err = self._runner(argv, timeout=self.timeout_s, env=env, stdin=stdin)
        else:
            _rc, out, _err = self._runner(argv, timeout=self.timeout_s, env=env)
        return out

    # ---- lifecycle / nav (dossier 14 §3.1) ----
    def open(self, url: str) -> str:
        return self._run("open", url)

    def close(self, *, all_sessions: bool = False) -> str:
        return self._run("close", "--all") if all_sessions else self._run("close")

    # ---- perception (dossier 14 §3.2) ----
    def snapshot(self, *, interactive: bool = True, compact: bool = False,
                 links: bool = False, scope: str | None = None) -> str:
        args = ["snapshot"]
        if interactive:
            args.append("-i")
        if compact:
            args.append("-c")
        if links:
            args.append("-u")
        if scope:
            args += ["-s", scope]
        args.append("--json")
        return self._run(*args)

    def get_text(self, ref: str) -> str:
        return self._run("get", "text", ref)

    def get_attr(self, ref: str, attr: str) -> str:
        return self._run("get", "attr", ref, attr)

    def eval_js(self, js: str) -> str:
        """Run arbitrary JS in the page via `eval --stdin` (the deterministic extraction
        escape hatch, dossier 14 §5.2 Mode B). JS goes on stdin, NOT argv."""
        return self._run("eval", "--stdin", stdin=js)

    # ---- interaction (dossier 14 §3.3) ----
    def click(self, ref: str) -> str:
        return self._run("click", ref)

    def fill(self, ref: str, value: str) -> str:
        return self._run("fill", ref, value)

    def type_text(self, ref: str, value: str) -> str:
        return self._run("type", ref, value)

    def press(self, key: str) -> str:
        return self._run("press", key)

    def select(self, ref: str, *values: str) -> str:
        return self._run("select", ref, *values)

    # ---- wait (dossier 14 §3.5) ----
    def wait_load(self, state: str = "networkidle") -> str:
        return self._run("wait", "--load", state)

    def wait_text(self, text: str) -> str:
        return self._run("wait", "--text", text)

    def wait_url(self, pattern: str) -> str:
        return self._run("wait", "--url", pattern)

    def wait_selector(self, sel: str) -> str:
        return self._run("wait", sel)

    # ---- network (XHR-JSON shortcut, dossier 14 §7) ----
    def network_requests(self, *, types: str = "xhr,fetch") -> str:
        return self._run("network", "requests", "--type", types, "--json")

    # ---- auth (dossier 14 §8/§13) ----
    def state_save(self, path: str) -> str:
        return self._run("state", "save", path)

    def cookies_set_curl(self, curl_file: str) -> str:
        return self._run("cookies", "set", "--curl", curl_file)


# ============================================================ Snapshot (@eN tree)
def normalize_ref(ref: str) -> str:
    """Accept `@e1`, `ref=e1`, or bare `e1` → canonical `e1` (dossier 14 §2.3 parse_ref)."""
    r = ref.strip()
    if r.startswith("@"):
        r = r[1:]
    if r.startswith("ref="):
        r = r[len("ref="):]
    return r


@dataclass
class Snapshot:
    """A parsed agent-browser accessibility snapshot. `refs` is the grounding source:
    a ref is valid iff its normalized id is a key here (dossier 14 §6.3 / §10B)."""

    text: str = ""
    refs: dict[str, dict[str, Any]] = field(default_factory=dict)
    title: str = ""
    url: str = ""

    @property
    def is_empty(self) -> bool:
        """Implausibly empty → triggers the lightpanda→chrome fallback (dossier 14 §12.5)."""
        return len(self.refs) < MIN_REFS_FOR_NONEMPTY

    def has_ref(self, ref: str) -> bool:
        return normalize_ref(ref) in self.refs

    def find_refs_by_role(self, role: str) -> list[str]:
        return [f"@{rid}" for rid, meta in self.refs.items() if meta.get("role") == role]


_TITLE_RE = re.compile(r"^Page:\s*(.+)$", re.MULTILINE)
_URL_RE = re.compile(r"^URL:\s*(\S+)$", re.MULTILINE)


def parse_snapshot(stdout: str) -> Snapshot:
    """Parse `snapshot -i --json` stdout into a Snapshot. Tolerant: malformed JSON or
    success:false → empty Snapshot (never raises) so the loop/ladder can degrade."""
    try:
        payload = json.loads(stdout)
    except (json.JSONDecodeError, TypeError):
        return Snapshot()
    if not isinstance(payload, dict) or not payload.get("success"):
        return Snapshot()
    data = payload.get("data")
    if not isinstance(data, dict):  # type-divergent CLI output → degrade, never raise
        return Snapshot()
    text = data.get("snapshot")
    if not isinstance(text, str):
        text = ""
    raw_refs = data.get("refs")
    if not isinstance(raw_refs, dict):
        raw_refs = {}
    refs = {normalize_ref(k): v for k, v in raw_refs.items() if isinstance(v, dict)}
    title_m = _TITLE_RE.search(text)
    url_m = _URL_RE.search(text)
    return Snapshot(
        text=text,
        refs=refs,
        title=title_m.group(1).strip() if title_m else "",
        url=url_m.group(1).strip() if url_m else "",
    )


# ============================================================ Verbatim prompts
# Stagehand act/extract/observe system prompts (dossier 14 §5, BROWSERBASE_PRODUCT_CODE.md
# :4279-4367). Shipped as constants for the Bad Research skill to embed when it reasons
# over the snapshot text — the LLM call is Claude Code itself, not a paid network call.

ACT_SYSTEM_PROMPT = (
    "You are helping the user automate the browser by finding elements based on what "
    "action the user wants to take on the page. You will be given: 1. a user defined "
    "instruction about what action to take on the page 2. a hierarchical accessibility "
    "tree showing the semantic structure of the page. The tree is a hybrid of the DOM and "
    "the accessibility tree. Return the element that matches the instruction if it exists. "
    "Otherwise, return an empty object."
)

EXTRACT_SYSTEM_PROMPT = (
    "You are extracting content on behalf of a user. If a user asks you to extract a "
    "'list' of information, or 'all' information, YOU MUST EXTRACT ALL OF THE INFORMATION "
    "THAT THE USER REQUESTS. You will be given: 1. An instruction 2. A list of DOM "
    "elements to extract from. Print the exact text from the DOM elements with all "
    "symbols, characters, and endlines as is. Print null or an empty string if no new "
    "information is found. ONLY print the content using the print_extracted_data tool "
    "provided. If a user is attempting to extract links or URLs, you MUST respond with "
    "ONLY the IDs of the link elements. Do not attempt to extract links directly from the "
    "text unless absolutely necessary."
)

OBSERVE_SYSTEM_PROMPT = (
    "You are helping the user automate the browser by finding elements based on what the "
    "user wants to observe in the page. You will be given: 1. a instruction of elements to "
    "observe 2. a hierarchical accessibility tree showing the semantic structure of the "
    "page. Return an array of elements that match the instruction if they exist, otherwise "
    "return an empty array. When returning elements, include the appropriate method from "
    "the supported actions list."
)

# The agent-loop system-prompt seed (dossier 14 §4.1, stream/chat.rs:124-153). The skill
# embeds these rules; we DROP the --json-ban and command-allowlist (those exist because
# Vercel doesn't trust its LLM; Claude Code is trusted and --json is useful — dossier 14 §10F).
AGENT_LOOP_SYSTEM_PROMPT = (
    "You control a browser through the agent-browser CLI. You have an active browser "
    "session.\n"
    "RULES:\n"
    "- You MUST run the agent-browser command for every browser action. NEVER claim you "
    "performed an action without running it.\n"
    "- If a request is outside your capabilities, say so honestly. Do not improvise.\n"
    "- One command, read the output, then decide the next.\n"
    "- Re-snapshot after ANY page change (navigate, submit, re-render, dialog) — refs go "
    "stale.\n"
    "- Pick a @eN ref only from the most recent snapshot's refs map; never invent one."
)


@dataclass
class BrowseStep:
    """One action in the ReAct loop. `kind` ∈ {click, fill, type, press, select, eval,
    wait_text, wait_url}. `target` is a @eN ref (or a key/text/url for press/wait). `value`
    is the fill/type text (variable VALUES never go through the cache key — see cache.py)."""

    kind: str
    target: str = ""
    value: str = ""


# kinds that change the page → re-snapshot afterward (dossier 14 §10A)
_PAGE_CHANGING = {"click", "press", "select"}


class AgentBrowserProvider:
    """Keyless agentic browse on the local agent-browser CLI (dossier 14 §4.2 ReAct loop).
    Claude Code is the brain: it supplies `steps`; this driver executes + re-snapshots."""

    name = "agent-browser"

    def __init__(
        self,
        *,
        engine: Literal["lightpanda", "chrome"] = DEFAULT_ENGINE,
        runner: Runner | None = None,
        program: str = AB_PROGRAM,
    ) -> None:
        self.engine = engine
        self._runner = runner
        self.program = program

    def _cli(
        self,
        engine: Literal["lightpanda", "chrome"],
        *,
        session: str | None = None,
        state: str | None = None,
        headers: str | None = None,
    ) -> _AgentBrowserCLI:
        return _AgentBrowserCLI(
            engine=engine, runner=self._runner, program=self.program,
            session=session, state=state, headers=headers,
        )

    def snapshot(
        self,
        *,
        interactive: bool = True,
        engine: Literal["lightpanda", "chrome"] | None = None,
    ) -> Snapshot:
        cli = self._cli(engine or self.engine)
        return parse_snapshot(cli.snapshot(interactive=interactive))

    def browse(
        self,
        url: str,
        instruction: str,
        *,
        max_steps: int = DEFAULT_MAX_STEPS,
        variables: dict[str, Any] | None = None,
        replay_key: str | None = None,
        steps: list[BrowseStep] | None = None,
        state: str | None = None,
        headers: str | None = None,
    ) -> WebResult:
        """Run the keyless ReAct loop. `steps` (host-model-supplied) drives interaction;
        with no steps, returns the initial snapshot as content (the 'observe' case)."""
        if not is_available(self.program):
            return WebResult(url=url, title="", content="",
                             metadata={"unavailable": True, "provider": self.name})

        # ---- authed browse is chrome-only: lightpanda blocks --state/--profile (dossier 14 §12.4) ----
        engine = "chrome" if (state is not None or headers is not None) else self.engine

        # ---- rung-2.5 lightpanda first; fall back to chrome on an empty snapshot ----
        snap = self._open_and_snapshot(url, engine, state=state, headers=headers)
        if engine == "lightpanda" and snap.is_empty:
            engine = "chrome"  # dossier 14 §12.5: same command surface, swap engine
            snap = self._open_and_snapshot(url, engine, state=state, headers=headers)

        cli = self._cli(engine, state=state, headers=headers)
        executed = 0
        for step in (steps or []):
            if executed >= max_steps:
                break
            # ---- grounding: a @eN target must exist in the current snapshot refs ----
            if step.target.startswith("@") and not snap.has_ref(step.target):
                continue  # ungrounded ref → skip (dossier 14 §6.3 grounding)
            self._dispatch(cli, step)
            executed += 1
            if step.kind in _PAGE_CHANGING:
                cli.wait_load("networkidle")
                snap = parse_snapshot(cli.snapshot(interactive=True))  # re-snapshot

        content = snap.text
        metadata: dict[str, Any] = {
            "engine": engine,
            "provider": self.name,
            "refs": list(snap.refs.keys()),
            "steps_executed": executed,
            "replay_key": replay_key,
        }
        return WebResult(
            url=snap.url or url,
            title=snap.title,
            content=content,
            metadata=metadata,
        )

    def _open_and_snapshot(
        self,
        url: str,
        engine: Literal["lightpanda", "chrome"],
        *,
        state: str | None = None,
        headers: str | None = None,
    ) -> Snapshot:
        cli = self._cli(engine, state=state, headers=headers)
        cli.open(url)
        cli.wait_load("networkidle")
        return parse_snapshot(cli.snapshot(interactive=True))

    @staticmethod
    def _dispatch(cli: _AgentBrowserCLI, step: BrowseStep) -> None:
        k = step.kind
        if k == "click":
            cli.click(step.target)
        elif k == "fill":
            cli.fill(step.target, step.value)
        elif k == "type":
            cli.type_text(step.target, step.value)
        elif k == "press":
            cli.press(step.target)
        elif k == "select":
            cli.select(step.target, step.value)
        elif k == "eval":
            cli.eval_js(step.value)
        elif k == "wait_text":
            cli.wait_text(step.target)
        elif k == "wait_url":
            cli.wait_url(step.target)
        # unknown kind → no-op (graceful)

    def save_state(self, path: str, *, session: str | None = None) -> None:
        """Persist cookies + localStorage + sessionStorage to a Playwright-compatible
        StorageState JSON (dossier 14 §13.1). Chrome-only."""
        self._cli("chrome", session=session).state_save(path)

    def cookies_set_curl(self, curl_file: str, *, session: str | None = None) -> None:
        """Replay a Copy-as-cURL dump's cookies (the no-automation auth path, dossier 14
        §13.1). The model never sees the password — only the resulting cookies."""
        self._cli("chrome", session=session).cookies_set_curl(curl_file)
