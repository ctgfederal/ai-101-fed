# AI-101-Fed — From Chat to Coworker

A teaching curriculum for national lab audiences. Eleven Jupyter notebooks that
build an agent harness piece by piece, using the [Arc](https://github.com/joshuamschultz/Arc)
foundations: `arcllm` (LLM calls), `arcrun` (the agentic loop), `arcagent`
(identity, audit, skills), and `arcskill` (skill packaging).

This is the runnable course (the repo's project root). The top-level
`../README.md` covers the slide decks and the course as a whole.

## The premise

1. **Harnesses bring a model from chat to coworker.** A chat window is a
   single prompt at a time. A harness is the loop, the tools, the memory,
   the policy, and the audit trail that turns that one-shot model into
   something you can hand a multi-step job to.
2. **Working through the agent builds intelligence that transfers.** Once
   you understand prompt → loop → skill → policy → audit, you can apply
   that thinking to *any* tool, model, or framework. Arc is one harness;
   the mental model is portable.
3. **The basics are enough to start.** Prompts, skills, workflows, audit.
   Nothing exotic. Each notebook builds on the previous one.

## The arc

| Notebook | Topic | What it teaches |
|---|---|---|
| `00_setup.ipynb` | Environment | Verifier / fallback for `./setup.sh`. Confirms Python, arc, packages, spaCy, `.env`, and a live LLM call. |
| `01_context_engineering.ipynb` | Context engineering | Same model, same question, four context layouts → four answers. STORE · RETRIEVE · CONDENSE · INSERT · ISOLATE, with token-budget and cost-vs-quality visuals. |
| `02_agentic_loop.ipynb` | The agentic loop | LLM + tools + memory as a loop (`arcrun.run()`). Healthy vs runaway runs, the plan · do · check pattern, token curves. |
| `03_harness.ipynb` | The harness | What turns a model into a coworker: tools, capabilities, cold/warm memory, tamper-evident audit chain, PII redaction. |
| `04_skills.ipynb` | Skills | A real `SKILL.md` folder (FOLDER · CONTRACT · SCRIPT · TEST). The agent loads only what it needs; push-down to scripts; validator gate. |
| `05_identity.ipynb` | Identity-based reasoning | Conservative vs Aggressive identity, same data, different decisions. Tribal knowledge → identity edit → diff under git. |
| `06_workflows.ipynb` | Workflows & sub-agents | Ad-hoc vs structured workflows, isolation/fan-out, the fractal plan/do/check, harvesting a trace into a reusable workflow. |
| `07_adaptation.ipynb` | Adaptation | Prompt/skill optimization with a held-out gate (overfitting made visible), tool graduation, and audit-trace → fine-tune data. |
| `08_security_at_runtime.ipynb` | Security at runtime | The full security posture on one call: PII redaction, request signing, sandboxing, budgets, and the tamper-evident audit chain. |
| `09_coding_workflow.ipynb` | The coding workflow | The principled-coder identity governing a spec-driven chain (/brainstorm → /build → /deepen → /specify), walked through real shipped artifacts. |
| `10_your_workflow.ipynb` | Your workflow | Assemble your own coworker from the pieces: harness + skill + identity + the `run` loop, end to end. |

## Setup

```bash
git clone git@github.com:ctgfederal/ai-101-fed.git
cd ai-101-fed/notebooks
./setup.sh                       # creates .venv, installs everything, registers the kernel
# then edit .env and add: ANTHROPIC_API_KEY=sk-ant-...
.venv/bin/jupyter lab            # open a notebook, pick the "Arc venv" kernel
```

`./setup.sh` is idempotent and safe to re-run. Arc is **vendored** at
`vendor/arc/`, so the course runs offline with no extra clone (setup.sh will
clone it only as a fallback if the directory is missing). It creates an
isolated `.venv`, installs everything in `requirements.txt` (jupyter, spaCy,
matplotlib, tiktoken, and the five arc packages from `vendor/arc/`), loads the
vendored spaCy NER model, registers the **Arc venv** Jupyter kernel, and seeds
`.env`.

No terminal? Open **`00_setup.ipynb`** with the **Arc venv** kernel and run it
top-to-bottom — it does the same steps and smoke-tests a live LLM call.

The spaCy NER model used in NB08 is **vendored** at
`data/models/en_core_web_sm-3.8.0/` (~15 MB), so air-gapped labs
get a working notebook with zero network calls. To upgrade or
re-fetch, run `python -m spacy download en_core_web_sm` and copy
the package's model directory into `data/models/`.

**Prefer `uv`?** `uv sync` works out of the box — the
`[tool.uv.sources]` paths in `pyproject.toml` point at the vendored `vendor/arc/`.

## Air-gapped labs

For environments without external API access:
- **Arc is already vendored** at `vendor/arc/` — no clone needed.
- The spaCy NER model is **vendored** at `data/models/en_core_web_sm-3.8.0/`,
  so the PII-redaction notebook runs with zero network calls.
- Run [Ollama](https://ollama.com/) locally on the demo machine.
- Set `OLLAMA_BASE_URL` in `.env`.
- In each notebook, change `load_model("anthropic")` to `load_model("ollama", "llama3.1")`.

The harness is identical. Only the brain changes.

## Layout

```
notebooks/           # the runnable course (repo project root)
├── notebooks/       # Setup (00) + curriculum (01-10)
├── setup.sh         # One-shot env bootstrap (.venv + packages + kernel + .env)
├── .claude/         # Full spec-driven dev workflow (drop into your own project)
│   ├── agents/      # 29 specialist agents (principled-coder + implementers + reviewers)
│   ├── commands/    # 7 workflow commands (/brainstorm, /build, /specify, ...)
│   ├── skills/      # 39 skills with templates, scripts, references (see INDEX.md)
│   ├── examples/    # Real shipped artifacts from arc (steering, brainstorm, spec, ADR)
│   └── README.md    # How to adopt this workflow in your own repo
├── skills/          # Example SKILL.md folders created at runtime by notebooks 04 and 05
├── identities/      # Identity files used by notebook 05
├── data/            # Data directory structure:
│   ├── models/      # Vendored spaCy NER model (en_core_web_sm-3.8.0)
│   ├── scratch/     # Temporary working files (gitignored)
│   ├── audit/       # Audit logs from notebook 07 (gitignored)
│   └── traces/      # Trace store from notebook 07 (gitignored)
├── scripts/         # Utility scripts (graduated tools, etc.)
├── vendor/arc/      # Vendored static snapshot of Arc (Apache 2.0)
├── Dockerfile       # For air-gapped lab deployments
├── docker-compose.yml  # Docker Compose for local development
├── Makefile         # Common development tasks
└── pyproject.toml
```

## Docker (Run and Dump Workflow)

The Docker setup is designed for a "run and dump" workflow — perfect for labs where you want to discard the environment after use.

### Quick Start

```bash
# Start Jupyter Lab (persists notebooks and data to host)
./scripts/run-docker.sh

# When done, dump all work to ./work-output/
./scripts/run-docker.sh dump

# Clean up container and output
./scripts/run-docker.sh clean
```

### What Gets Dumped

The `dump-work` command copies:
- Modified notebooks from `notebooks/`
- Generated outputs from `data/audit/`, `data/traces/`, `data/scratch/`
- Identity files from `identities/`
- A `WORK_SUMMARY.md` with next steps

### Manual Docker Commands

```bash
# Build the image
docker build -t ai-101-fed .

# Run with persistence
docker run -it --rm \
  -p 8888:8888 \
  -v $(pwd)/notebooks:/app/notebooks \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/identities:/app/identities \
  -v $(pwd)/.env:/app/.env \
  -v $(pwd)/vendor:/app/vendor \
  ai-101-fed

# Dump work from a stopped container
docker run --rm \
  -v $(pwd)/notebooks:/app/notebooks \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/identities:/app/identities \
  -v $(pwd)/work-output:/app/output \
  ai-101-fed dump-work
```

## Adopting the dev workflow

`.claude/` is a **complete, self-contained workflow** that you can copy
into any project to get spec-driven development with the principled-coder
identity. Notebook 09 walks through it pedagogically; the README inside
`.claude/` explains how to drop it into your own repo.

```bash
# read about it
jupyter lab notebooks/09_coding_workflow.ipynb

# adopt it in your own project
cp -R .claude /path/to/your-project/
```
