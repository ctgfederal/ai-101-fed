---
topic: Kimi (Moonshot AI) Provider Support for arcllm
date: 2026-04-27
status: complete
related_prd: .claude/specs/kimi-provider/PRD.md
---

# Kimi (Moonshot AI) Provider Support

## Inspiration

`arcllm` already speaks to a dozen LLM providers through a single
`load_model("provider")` switch. Users keep asking for Moonshot AI's Kimi
models — competitive quality, a 256K context window, native tool calling,
and attractive pricing. Because Moonshot exposes an OpenAI-compatible API,
adding it should be a thin alias over the existing adapter rather than a new
integration from scratch. The goal: one more provider, near-zero new surface
area, no regressions.

## Projects

- **Moonshot adapter** — a thin subclass/alias of the existing
  OpenAI-compatible adapter, routing to Moonshot's endpoint.
- **Provider metadata** — a TOML entry describing the `kimi-k2` and
  `kimi-k2.5` models (context window, pricing, capabilities).
- **Registration** — a lazy import wired into `arcllm`'s provider registry so
  `load_model("moonshot")` resolves with no eager dependency cost.

## Audience

- **Arc agent developers** who want to point an existing agent at a Kimi model
  by changing a single string — `load_model("moonshot", "kimi-k2.5")` — with
  no code changes elsewhere.
- **Evaluators** comparing model quality/cost across providers from one
  consistent interface.

## Use Cases

- **Swap the brain.** An agent built against `arcllm` runs unchanged against
  Kimi by selecting the provider — same loop, same tools, same audit trail.
- **Tool-calling agents on Kimi.** Native function calling works through the
  inherited OpenAI-compatible request/response format.
- **Cost/quality comparison.** Run the same prompt set across providers and
  compare tokens, latency, and answer quality.

## Desired Outcomes

- `load_model("moonshot")` returns a working adapter; `load_model("moonshot",
  "kimi-k2.5")` selects the right model.
- Adapter stays tiny (a thin alias) — no new dependencies.
- All existing parametrized provider tests pass with `moonshot` included.
- `mypy --strict` and `ruff check` stay clean.

## Guiding Principles

- **Reuse over reinvention.** Inherit everything possible from the existing
  OpenAI-compatible adapter; only override what differs (endpoint, auth env
  var, model list).
- **Smallest correct change.** A provider addition should not touch unrelated
  code. Thin alias, one TOML block, one lazy import.
- **No regressions.** The existing twelve providers must behave identically
  after the change.

## Constraints

- **OpenAI-compatible only for v1** — rely on the inherited adapter; don't
  hand-roll a bespoke client.
- **Auth via `MOONSHOT_API_KEY`** (Bearer token) read from the environment.
- **Zero new dependencies** — use the HTTP client already in `arcllm`.
- **Adapter must validate** against the existing `ProviderConfig` schema.

## Scope

**In:**
- Moonshot adapter (thin alias of the OpenAI-compatible adapter)
- Provider TOML for `kimi-k2` and `kimi-k2.5`
- Lazy import registration in `__init__.py`
- Tool calling via inherited OpenAI-compatible format
- Parametrized provider tests extended to cover `moonshot`

**Out (deferred):**
- Streaming support
- Thinking-mode / `reasoning_content` parsing
- China-region endpoint (`api.moonshot.cn`)
- Bespoke vision message formatting (already handled by the inherited adapter)

## Open Questions for /build

- **Alias vs subclass:** Is a pure alias enough, or does Moonshot need a
  one-line override for the endpoint/auth differences?
- **Model list source:** Hard-code `kimi-k2`/`kimi-k2.5` in TOML now, or fetch
  the model list dynamically? (Static TOML is simpler and matches existing
  providers.)
- **Default model:** Which Kimi model should `load_model("moonshot")` select
  when none is specified?

## Related Solutions

- None specific to Moonshot in `.claude/solutions/`. The existing
  OpenAI-compatible adapter is the reference implementation to mirror; every
  prior provider addition followed the same thin-alias pattern.
