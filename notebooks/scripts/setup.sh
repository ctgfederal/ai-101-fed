#!/bin/bash
# AI Roadshow Setup Script
# Terminal alternative to notebook 00_setup.ipynb
#
# Usage: ./scripts/setup.sh [--skip-smoke-test]
#
# This script:
# 1. Verifies Python >= 3.11
# 2. Vendors arc into vendor/arc/
# 3. Installs requirements.txt
# 4. Loads spaCy NER model
# 5. Creates .env from .env.example
# 6. Verifies imports
# 7. Runs smoke-test LLM call (optional, skipped with --skip-smoke-test)

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "=== AI Roadshow Setup ==="
echo "Project root: $PROJECT_ROOT"
echo ""

# 1. Python version check
echo "1. Checking Python version..."
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")
PYTHON_MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")
PYTHON_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
    echo "   ✗ Python 3.11+ required (found $PYTHON_VERSION)"
    echo "   Install with: brew install python@3.12"
    exit 1
fi
echo "   ✓ Python $PYTHON_VERSION"

# 2. Vendor arc
echo "2. Vendoring arc..."
ARC_DIR="$PROJECT_ROOT/vendor/arc"
ARC_URL="https://github.com/joshuamschultz/Arc.git"

if [ -d "$ARC_DIR" ]; then
    echo "   ✓ arc already vendored at vendor/arc/"
else
    echo "   Cloning arc from $ARC_URL..."
    mkdir -p "$(dirname "$ARC_DIR")"
    git clone --depth 1 "$ARC_URL" "$ARC_DIR"
    echo "   ✓ Cloned arc to vendor/arc/"
fi

# Verify required packages exist
REQUIRED_PACKAGES=("arctrust" "arcllm" "arcrun" "arcagent" "arcskill")
for pkg in "${REQUIRED_PACKAGES[@]}"; do
    if [ ! -d "$ARC_DIR/packages/$pkg" ]; then
        echo "   ✗ arc clone is missing package: $pkg"
        exit 1
    fi
done
echo "   ✓ All arc packages present"

# 3. Install dependencies
echo "3. Installing dependencies..."
pip install -r requirements.txt --quiet
echo "   ✓ Dependencies installed"

# 4. spaCy NER model
echo "4. Loading spaCy NER model..."
MODEL_PATH="$PROJECT_ROOT/data/models/en_core_web_sm-3.8.0"
if [ -d "$MODEL_PATH" ]; then
    python3 -c "import spacy; nlp = spacy.load('$MODEL_PATH'); print('   ✓ Loaded vendored model')"
elif python3 -c "import spacy; spacy.load('en_core_web_sm')" 2>/dev/null; then
    echo "   ✓ Loaded pip-installed en_core_web_sm"
else
    echo "   ⚠ No spaCy model found"
    echo "   Run: python3 -m spacy download en_core_web_sm"
fi

# 5. Environment file
echo "5. Setting up .env..."
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
    echo "   ✓ Created .env from .env.example"
    echo "   → Edit .env and add your API keys"
else
    echo "   ✓ .env already exists"
fi

# 6. Verify imports
echo "6. Verifying imports..."
python3 -c "
import importlib
modules = ['arctrust', 'arcllm', 'arcrun', 'arcagent', 'arcskill', 'spacy', 'dotenv', 'rich']
for name in modules:
    try:
        importlib.import_module(name)
        print(f'   ✓ {name}')
    except ImportError as e:
        print(f'   ✗ {name} — {e}')
        exit(1)
"

# 7. Smoke test (optional)
if [ "$1" != "--skip-smoke-test" ]; then
    echo "7. Running smoke-test LLM call..."
    python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()

provider = None
model_arg = {}

if os.getenv('ANTHROPIC_API_KEY'):
    provider, model_arg = 'anthropic', {}
elif os.getenv('OPENAI_API_KEY'):
    provider, model_arg = 'openai', {}
elif os.getenv('OLLAMA_BASE_URL'):
    provider, model_arg = 'ollama', {'model': 'llama3.1'}

if provider is None:
    print('   ⊘ Skipped — no provider in .env')
else:
    from arcllm import load_model, Message
    import asyncio
    async def test():
        model = load_model(provider, **model_arg)
        resp = await model.invoke([Message(role='user', content='In one sentence: what is a harness?')])
        print(f'   Provider: {provider}')
        print(f'   Reply: {resp.content}')
        print('   ✓ End-to-end LLM call works')
    asyncio.run(test())
"
else
    echo "7. Skipped smoke-test (use --skip-smoke-test flag)"
fi

echo ""
echo "=== Setup complete ==="
echo "Next: Open notebooks/01_chat_to_coworker.ipynb"