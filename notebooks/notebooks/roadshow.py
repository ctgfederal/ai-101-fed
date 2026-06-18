"""Shared setup for the AI Roadshow notebooks.

One import gives every notebook the same wiring, so the cells stay about the
lesson — not the plumbing:

    from roadshow import setup
    model, ask, ntok, DATA = setup()

`setup()` loads your `.env`, connects the model, and hands back four things:

    model   the connected LLM (Anthropic by default)
    ask     async one-shot helper:  await ask("question", system="...")
    ntok    token counter (tiktoken if available, else a ~4-chars/token estimate)
    DATA    Path to the repo's data/ directory

A couple of extras, imported only by the notebooks that need them:

    from roadshow import Message        # build multi-turn message lists
    from roadshow import invoke_sync     # call the async model from sync code
    from roadshow import parse_json_loose  # tolerant JSON extraction from model text
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import threading
from pathlib import Path

from dotenv import load_dotenv
from arcllm import load_model, Message  # re-exported for notebooks that build messages
from arcllm import registry as _registry
from arcllm.config import load_provider_config

__all__ = ["setup", "connect", "Message", "invoke_sync", "run_sync",
           "parse_json_loose", "project_root", "ntok",
           "chunk_markdown", "show_diff", "panel", "md", "rule"]


def project_root() -> Path:
    """Repo root, whether a notebook runs from notebooks/ or the repo root."""
    cwd = Path.cwd()
    return cwd.parent if cwd.name == "notebooks" else cwd


# --- token counting ---------------------------------------------------------
# Prefer tiktoken's real BPE count; fall back to a dependency-free estimate so
# token charts still render if tiktoken isn't installed.
try:
    import tiktoken
    _ENC = tiktoken.get_encoding("cl100k_base")

    def ntok(text: str) -> int:
        """Number of tokens in *text* (tiktoken cl100k_base)."""
        return len(_ENC.encode(text or ""))
except Exception:  # pragma: no cover - exercised only without tiktoken
    def ntok(text: str) -> int:
        """Approximate token count (~4 characters per token)."""
        return max(1, len(text or "") // 4)


def parse_json_loose(text: str) -> dict:
    """Pull a JSON object out of model text, tolerating stray prose / trailing commas."""
    if not text:
        return {}
    match = re.search(r"\{.*\}", text, re.DOTALL)
    blob = match.group(0) if match else text
    try:
        return json.loads(blob)
    except Exception:
        try:
            return json.loads(re.sub(r",\s*([}\]])", r"\1", blob))  # drop trailing commas
        except Exception:
            return {}


# --- async bridge -----------------------------------------------------------
# A notebook kernel already runs an event loop, and arcllm's HTTP client binds
# its connection pool to the first loop it runs on. So sync code (e.g. an
# optimizer) can't call asyncio.run() per request. We keep ONE background loop
# in a daemon thread and marshal calls onto it.
_bg_loop: asyncio.AbstractEventLoop | None = None
_bg_lock = threading.Lock()


def _background_loop() -> asyncio.AbstractEventLoop:
    global _bg_loop
    if _bg_loop is None:
        with _bg_lock:
            if _bg_loop is None:
                loop = asyncio.new_event_loop()
                threading.Thread(target=loop.run_forever, daemon=True).start()
                _bg_loop = loop
    return _bg_loop


def run_sync(coro):
    """Run any awaitable to completion on the shared background loop, from sync code.

    Use this for agent loops (e.g. arcrun.run(...)) so they run on the SAME loop the
    model client was first bound to — mixing loops triggers "bound to a different event
    loop" errors.
    """
    return asyncio.run_coroutine_threadsafe(coro, _background_loop()).result()


def invoke_sync(model, messages):
    """Run `await model.invoke(messages)` to completion from synchronous code.

    *messages* is a list of Message objects. Returns the model's response.
    """
    return run_sync(model.invoke(messages))


# --- provider resolution (the one switch) -----------------------------------
# Every machine runs the *same* notebooks. The only thing that changes is the
# provider, set once per machine in .env:
#
#   Mac / EC2 (Anthropic cloud):   ARC_PROVIDER=anthropic   + ANTHROPIC_API_KEY
#   GB10 (local LiteLLM proxy):    ARC_PROVIDER=litellm      + ARC_BASE_URL + ARC_MODEL
#
# "litellm" isn't a native arc provider — LiteLLM's proxy speaks the OpenAI
# wire protocol, so we route it through arc's `openai` adapter pointed at the
# proxy's base_url. ARC_MODEL/ARC_BASE_URL override the defaults for any provider.
_DEFAULT_LITELLM_URL = "http://localhost:4000"


def _resolve(provider: str | None, model: str | None):
    """Turn (provider, model) + .env into a concrete (provider, model, base_url)."""
    provider = (provider or os.getenv("ARC_PROVIDER") or "anthropic").lower()
    model = model or os.getenv("ARC_MODEL") or None
    base_url = os.getenv("ARC_BASE_URL") or None
    if provider == "litellm":                  # LiteLLM proxy → OpenAI-compatible
        provider = "openai"
        base_url = base_url or _DEFAULT_LITELLM_URL
    return provider, model, base_url


def connect(provider: str | None = None, model: str | None = None, **kwargs):
    """Return a configured arc model, honoring .env. Pass `load_model` kwargs
    (e.g. ``security={...}``, ``audit=True``) straight through.

    Notebooks call this with no arguments — the active machine's .env decides
    the provider. Explicit args override .env when you need a one-cell switch.
    """
    load_dotenv(project_root() / ".env")
    provider, model, base_url = _resolve(provider, model)
    if base_url:
        # Local proxies (LiteLLM/Ollama) need a custom endpoint and usually no
        # real key. Inject both via arc's module-level provider-config cache so
        # the change lives here, not in the vendored arc package.
        cfg = load_provider_config(provider)
        cfg.provider.base_url = base_url
        cfg.provider.api_key_required = False
        _registry._provider_config_cache[provider] = cfg
    llm = load_model(provider, model, **kwargs) if model else load_model(provider, **kwargs)
    return _with_transient_retry(llm)


def _with_transient_retry(llm, *, attempts: int = 4, base: float = 0.8):
    """Wrap a model so `invoke()` retries on transient network errors with
    exponential backoff. arc's built-in retry covers ConnectError/timeouts/5xx but
    NOT httpx.ReadError — exactly what a room full of guests hammering one endpoint
    hits. We catch the whole httpx.TransportError family so a dropped read doesn't
    kill a cell mid-sweep. Both ask() and arcrun.run() go through invoke()."""
    import httpx

    original = llm.invoke

    async def invoke(*args, **kwargs):
        for i in range(attempts):
            try:
                return await original(*args, **kwargs)
            except httpx.TransportError:
                if i == attempts - 1:
                    raise
                await asyncio.sleep(base * (2 ** i))

    llm.invoke = invoke
    return llm


# --- the one-liner ----------------------------------------------------------
def setup(provider: str | None = None, model: str | None = None):
    """Load `.env`, connect the model, and return (model, ask, ntok, DATA).

    provider/model default to the .env switch (ARC_PROVIDER / ARC_MODEL); pass
    them explicitly only to override for a single notebook.
    """
    root = project_root()
    llm = connect(provider, model)
    data = (root / "data").resolve()

    # Show which provider is live, so every notebook visibly confirms it's using
    # the machine's .env switch (anthropic on mac/ec2, litellm on gb10) — not a
    # silent per-notebook default.
    active = provider or os.getenv("ARC_PROVIDER") or "anthropic"
    active_model = model or os.getenv("ARC_MODEL") or "provider default"
    print(f"✓ provider: {active}  ·  model: {active_model}")

    async def ask(user: str, *, system: str | None = None) -> str:
        """One-shot: send a prompt, return the reply text."""
        messages = []
        if system:
            messages.append(Message(role="system", content=system))
        messages.append(Message(role="user", content=user))
        resp = await llm.invoke(messages)
        return resp.content or ""

    return llm, ask, ntok, data



# --- corpus chunking (NB01) -------------------------------------------------
def chunk_markdown(text: str, source: str) -> list:
    """Split a markdown doc into section-sized chunks (one per heading), each
    tagged with its `source` filename. Splitting on headings keeps a symptom and
    the cause that explains it in the SAME chunk — which is what makes retrieval
    actually useful. Returns a list of {"source", "text"} dicts."""
    parts = [p.strip() for p in re.split(r"\n(?=#{1,6}\s)", text) if p.strip()]
    return [{"source": source, "text": p} for p in parts]


# --- rich display helpers (used across notebooks) ---------------------------
def show_diff(before: str, after: str, *, title: str = "diff", context: int = 2) -> None:
    """Render a readable, colored diff in the notebook: additions green, removals
    red, hunks cyan. Clearer than a raw `difflib` dump for non-coders."""
    import difflib
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text

    body = Text()
    for ln in difflib.unified_diff(before.splitlines(), after.splitlines(),
                                   lineterm="", n=context):
        if ln.startswith(("+++", "---")):
            continue
        if ln.startswith("@@"):
            body.append(ln + "\n", style="bold cyan")
        elif ln.startswith("+"):
            body.append(ln + "\n", style="green")
        elif ln.startswith("-"):
            body.append(ln + "\n", style="red")
        else:
            body.append(ln + "\n", style="dim")
    if not body:
        body = Text("(no changes)", style="dim")
    Console().print(Panel(body, title=title, border_style="cyan"))


def panel(text, title: str = "", style: str = "cyan") -> None:
    """Print text inside a titled rich panel."""
    from rich.console import Console
    from rich.panel import Panel
    Console().print(Panel(str(text), title=title, border_style=style))


def md(markdown: str) -> None:
    """Render a markdown string as rich formatted text in the notebook."""
    from rich.console import Console
    from rich.markdown import Markdown
    Console().print(Markdown(markdown))


def rule(title: str = "") -> None:
    """Print a titled horizontal rule (section divider)."""
    from rich.console import Console
    Console().rule(title)
