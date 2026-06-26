#!/usr/bin/env bash

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"
LOG_FILE="$PROJECT_DIR/build.log"

echo "📦 Project: $PROJECT_DIR"
echo "🧹 Cleaning previous build..."

rm -rf "$PROJECT_DIR/build"

echo "🔍 Checking system dependencies..."

# clang++
if ! command -v clang++ &> /dev/null; then
    echo "❌ clang++ not found. Install: sudo dnf install clang"
    exit 1
else
    echo "✔ clang++ found: $(clang++ --version | head -n 1)"
fi

# ninja
if ! command -v ninja &> /dev/null; then
    echo "❌ ninja not found. Install: sudo dnf install ninja-build"
    exit 1
else
    echo "✔ ninja found: $(ninja --version)"
fi

echo "🐍 Activating venv..."
source "$VENV_DIR/bin/activate"

echo "📦 Checking Python dependencies..."

if [ -f "$PROJECT_DIR/requirements.txt" ]; then
    pip check || {
        echo "⚠ pip check found dependency conflicts"
        exit 1
    }

    echo "✔ requirements.txt dependencies OK"
else
    echo "⚠ requirements.txt not found, skipping check"
fi

echo "🚀 Starting Flet build..."
echo "📄 Logging to: $LOG_FILE"
echo "--------------------------------------"

# build with logging
flet build linux -v | tee "$LOG_FILE"

echo "--------------------------------------"
echo "✔ Build finished"

echo "🧹 Deactivating venv..."
deactivate

echo "🎉 Done."