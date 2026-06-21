#!/bin/bash
# AI-101-Fed Docker Runner
# Convenient wrapper for running ai-101-fed container with persistence
#
# Usage:
#   ./scripts/run-docker.sh              # Start Jupyter Lab
#   ./scripts/run-docker.sh dump         # Dump work to ./work-output/
#   ./scripts/run-docker.sh clean        # Remove container and output

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="$PROJECT_ROOT/work-output"

# Check if image exists, build if not
if ! docker image inspect ai-101-fed >/dev/null 2>&1; then
    echo "Building ai-101-fed image..."
    docker build -t ai-101-fed "$PROJECT_ROOT"
fi

case "${1:-run}" in
    run|jupyter)
        echo "Starting AI-101-Fed Jupyter Lab..."
        echo "Open http://localhost:8888 in your browser"
        echo ""
        docker run -it --rm \
            -p 8888:8888 \
            -v "$PROJECT_ROOT/notebooks:/app/notebooks" \
            -v "$PROJECT_ROOT/data:/app/data" \
            -v "$PROJECT_ROOT/identities:/app/identities" \
            -v "$PROJECT_ROOT/.env:/app/.env" \
            -v "$PROJECT_ROOT/vendor:/app/vendor" \
            --name ai-101-fed-session \
            ai-101-fed
        ;;
    
    dump)
        echo "Dumping work from container..."
        
        # Run dump-work in a temporary container
        docker run --rm \
            -v "$PROJECT_ROOT/notebooks:/app/notebooks" \
            -v "$PROJECT_ROOT/data:/app/data" \
            -v "$PROJECT_ROOT/identities:/app/identities" \
            -v "$OUTPUT_DIR:/app/output" \
            ai-101-fed dump-work
        
        echo ""
        echo "Work dumped to: $OUTPUT_DIR"
        ls -la "$OUTPUT_DIR"
        ;;
    
    clean)
        echo "Cleaning up..."
        docker rm -f ai-101-fed-session 2>/dev/null || true
        rm -rf "$OUTPUT_DIR"
        echo "Done."
        ;;
    
    build)
        echo "Rebuilding ai-101-fed image..."
        docker build -t ai-101-fed "$PROJECT_ROOT"
        ;;
    
    *)
        echo "Usage: $0 {run|dump|clean|build}"
        echo ""
        echo "Commands:"
        echo "  run    - Start Jupyter Lab (default)"
        echo "  dump   - Dump work to ./work-output/"
        echo "  clean  - Remove container and output"
        echo "  build  - Rebuild the Docker image"
        exit 1
        ;;
esac