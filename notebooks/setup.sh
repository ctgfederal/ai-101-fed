#!/usr/bin/env bash
# AI Roadshow — one-shot environment bootstrap.
#
#   ./setup.sh
#
# Idempotent: safe to re-run. Creates an isolated .venv, installs every
# package the notebooks need, registers the "Arc venv" Jupyter kernel the
# notebooks are pinned to, and seeds .env. After it finishes, open any
# notebook and pick the "Arc venv" kernel — everything will import.
#
# Works with or without `uv` (falls back to python3 -m venv + pip).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
VENV="$ROOT/.venv"
ARC_DIR="$ROOT/vendor/arc"
ARC_URL="https://github.com/joshuamschultz/Arc.git"
PY_BIN="$VENV/bin/python"

echo "▶ AI Roadshow setup  ($ROOT)"

# 1 — Vendor arc (the five editable packages requirements.txt installs from) ---
if [ -d "$ARC_DIR/packages/arcllm" ]; then
  echo "  ✓ arc already vendored at vendor/arc"
else
  echo "  • cloning arc → vendor/arc"
  mkdir -p "$ROOT/vendor"
  git clone --depth 1 "$ARC_URL" "$ARC_DIR"
fi
for p in arctrust arcllm arcrun arcagent arcskill; do
  [ -d "$ARC_DIR/packages/$p" ] || { echo "  ✗ arc checkout missing package: $p"; exit 1; }
done

# 2 — Find a usable Python and create the virtualenv --------------------------
need_python_help() {
  cat >&2 <<'HELP'
  ✗ No suitable Python found (need 3.11+).

  Install one, then re-run ./setup.sh:

    Amazon Linux 2023 / RHEL / Fedora:
        sudo dnf install -y python3.12 python3.12-pip
    Ubuntu / Debian:
        sudo apt-get update && sudo apt-get install -y python3 python3-venv python3-pip
    Or install uv (no root, bundles its own Python):
        curl -LsSf https://astral.sh/uv/install.sh | sh && exec "$SHELL" -l
HELP
  exit 1
}

if [ -x "$PY_BIN" ]; then
  echo "  ✓ .venv already exists"
elif command -v uv >/dev/null 2>&1; then
  echo "  • creating .venv with uv (python 3.12)"
  uv venv "$VENV" --python 3.12 --seed   # --seed adds pip so notebooks can self-install
else
  # Pick the newest interpreter that is >= 3.11 (AL2023's python3 is 3.9 — too old).
  HOST_PY=""
  for cand in python3.13 python3.12 python3.11 python3; do
    command -v "$cand" >/dev/null 2>&1 || continue
    if "$cand" -c 'import sys; raise SystemExit(0 if sys.version_info[:2] >= (3,11) else 1)' 2>/dev/null; then
      HOST_PY="$cand"; break
    fi
  done
  [ -n "$HOST_PY" ] || need_python_help
  echo "  • creating .venv with $HOST_PY ($("$HOST_PY" --version 2>&1))"
  if ! "$HOST_PY" -m venv "$VENV" 2>/tmp/arc_venv_err; then
    cat /tmp/arc_venv_err >&2
    echo "  ✗ venv creation failed — on Debian/Ubuntu run: sudo apt-get install -y python3-venv" >&2
    exit 1
  fi
fi
[ -x "$PY_BIN" ] || { echo "  ✗ .venv created but has no python at $PY_BIN" >&2; exit 1; }

# 3 — Install all dependencies into the venv ----------------------------------
echo "  • installing requirements.txt (this can take a minute)"
if command -v uv >/dev/null 2>&1; then
  uv pip install --python "$VENV" -r "$ROOT/requirements.txt"
else
  # --upgrade pip first so editable installs resolve cleanly
  "$PY_BIN" -m pip install --quiet --upgrade pip
  "$PY_BIN" -m pip install -r "$ROOT/requirements.txt"
fi

# 4 — spaCy NER model (NB08/28 PII redaction) ---------------------------------
# Vendored at data/models/en_core_web_sm-3.8.0/ for air-gapped labs; only
# download if neither the vendored copy nor a pip-registered model is present.
if [ -d "$ROOT/data/models/en_core_web_sm-3.8.0" ]; then
  echo "  ✓ spaCy model vendored at data/models/"
elif "$PY_BIN" -c "import spacy; spacy.load('en_core_web_sm')" >/dev/null 2>&1; then
  echo "  ✓ spaCy model already installed"
else
  echo "  • downloading spaCy en_core_web_sm (~13 MB)"
  "$PY_BIN" -m spacy download en_core_web_sm || \
    echo "  ⚠ spaCy model download failed — NB08/28 will be limited (non-fatal)"
fi

# 5 — Register the Jupyter kernel the notebooks are pinned to ------------------
echo "  • registering Jupyter kernel 'arcvenv' (display: Arc venv)"
"$PY_BIN" -m ipykernel install --user --name arcvenv --display-name "Arc venv" >/dev/null

# 6 — Seed .env ---------------------------------------------------------------
if [ -f "$ROOT/.env" ]; then
  echo "  ✓ .env already present"
else
  cp "$ROOT/.env.example" "$ROOT/.env"
  echo "  • created .env from .env.example — add your ANTHROPIC_API_KEY"
fi

# 7 — Verify the import surface -----------------------------------------------
echo "  • verifying imports"
"$PY_BIN" - <<'PY'
import importlib
mods = ["arctrust","arcllm","arcrun","arcagent","arcskill",
        "spacy","dotenv","rich","ipywidgets","pydantic","httpx",
        "matplotlib","numpy"]
bad = []
for m in mods:
    try:
        importlib.import_module(m)
    except Exception as e:
        bad.append(f"{m}: {e}")
if bad:
    print("  ✗ failed imports:\n   - " + "\n   - ".join(bad)); raise SystemExit(1)
print(f"  ✓ all {len(mods)} packages import")
PY

cat <<EOF

✅ Setup complete. Everything is installed into ./.venv

⚠ IMPORTANT — your shell's default 'python' / 'pip' / 'jupyter' may point at
  conda or the system Python, which do NOT have these packages. Use the venv:

      source .venv/bin/activate     # then python / jupyter resolve to .venv
  or call its binaries directly:    .venv/bin/python   .venv/bin/jupyter

Next:
  1. Put your key in .env:   ANTHROPIC_API_KEY=sk-ant-...
  2. Launch Jupyter:         .venv/bin/jupyter lab
  3. Open a notebook and select the "Arc venv" kernel (top-right).
  4. Start with 00_setup.ipynb (verifies everything), then 01_context_engineering.ipynb.

The curriculum is notebooks 01–10 (01_context_engineering → 10_your_workflow).
EOF
