#!/bin/bash
# Docker entry point for AI Roadshow
# Supports multiple modes: jupyter (default), dump-work, exec

set -e

# Default mode is jupyter
MODE="${1:-jupyter}"

case "$MODE" in
    jupyter)
        echo "Starting Jupyter Lab on http://0.0.0.0:8888"
        exec jupyter lab \
            --ip=0.0.0.0 \
            --port=8888 \
            --no-browser \
            --allow-root \
            --NotebookApp.token='' \
            --NotebookApp.password='' \
            --NotebookApp.open_browser=False
        ;;
    
    dump-work)
        echo "Dumping work to /app/output..."
        
        # Create output structure
        mkdir -p /app/output/notebooks /app/output/data /app/output/identities
        
        # Copy notebooks (only .ipynb files, skip checkpoints)
        if [ -d "/app/notebooks" ]; then
            find /app/notebooks -name "*.ipynb" -exec cp --parents {} /app/output/ \; 2>/dev/null || true
            echo "  ✓ Notebooks copied"
        fi
        
        # Copy data outputs (audit, traces, scratch)
        for dir in audit traces scratch; do
            if [ -d "/app/data/$dir" ]; then
                cp -r "/app/data/$dir" /app/output/data/ 2>/dev/null || true
                echo "  ✓ data/$dir copied"
            fi
        done
        
        # Copy identities
        if [ -d "/app/identities" ]; then
            cp -r /app/identities/* /app/output/identities/ 2>/dev/null || true
            echo "  ✓ Identities copied"
        fi
        
        # Create a summary file
        cat > /app/output/WORK_SUMMARY.md << 'EOF'
# AI Roadshow Work Output

This directory contains your work from the AI Roadshow session.

## Contents

- `notebooks/` — Your modified Jupyter notebooks
- `data/` — Generated outputs (audit logs, traces, scratch files)
- `identities/` — Identity files created during notebook 06

## Next Steps

1. Review the notebooks for any sensitive information
2. Commit to your repository or share with your team
3. Delete any API keys or secrets from `.env` if copied
EOF
        
        echo ""
        echo "Work dumped to /app/output/"
        echo "To extract: docker cp <container>:/app/output/. ."
        ;;
    
    exec)
        # Pass through to shell for debugging
        shift
        exec "$@"
        ;;
    
    shell)
        # Interactive shell
        exec /bin/bash
        ;;
    
    *)
        echo "Usage: $0 {jupyter|dump-work|exec <cmd>|shell}"
        echo ""
        echo "Modes:"
        echo "  jupyter    - Start Jupyter Lab (default)"
        echo "  dump-work  - Dump all work to /app/output"
        echo "  exec <cmd> - Execute a command in the container"
        echo "  shell      - Open a bash shell"
        exit 1
        ;;
esac