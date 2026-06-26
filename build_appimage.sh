#!/usr/bin/env bash
#
# Build a single-file AppImage for the WireGuard GUI Client.
#
# Usage:
#   ./build_appimage.sh
#
# Requirements (must already be installed):
#   - Flutter SDK   (needed by `flet build linux`)
#   - flet          (pip install flet, in your virtualenv)
#   - wget, FUSE    (appimagetool is downloaded automatically; needs libfuse2)
#
# The resulting file is written to the repo root, e.g.:
#   WireGuard-GUI-Client-x86_64.AppImage
#
set -euo pipefail

# ---------------------------------------------------------------------------
# Config (override via environment variables if you like)
# ---------------------------------------------------------------------------
APP_NAME="${APP_NAME:-WireGuard GUI Client}"   # human-readable name (.desktop)
OUTPUT="${OUTPUT:-WireGuard-GUI-Client-x86_64.AppImage}"
ICON_SRC="${ICON_SRC:-src/assets/icon.png}"          # 256x256 PNG icon (optional)
ARCH="${ARCH:-x86_64}"

# Resolve repo root = directory of this script
ROOT="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
cd "$ROOT"

APPDIR="$ROOT/AppDir"
BUILD_DIR="$ROOT/build/linux"
APPIMAGETOOL="$ROOT/appimagetool"

log()  { printf '\033[1;34m==>\033[0m %s\n' "$*"; }
die()  { printf '\033[1;31mError:\033[0m %s\n' "$*" >&2; exit 1; }

# ---------------------------------------------------------------------------
# 0. Sanity checks
# ---------------------------------------------------------------------------
command -v flet >/dev/null 2>&1 || die "flet not found. Activate your venv and 'pip install flet'."

# ---------------------------------------------------------------------------
# 1. Build the Flet Linux bundle
# ---------------------------------------------------------------------------
log "Building Flet Linux bundle (flet build linux)..."
flet build linux

[ -d "$BUILD_DIR" ] || die "Expected $BUILD_DIR after build, but it's missing."

# ---------------------------------------------------------------------------
# 2. Detect the built executable name
# ---------------------------------------------------------------------------
# The main executable is the file directly inside build/linux/ that is
# executable and is not a directory.
APP_BIN="$(find "$BUILD_DIR" -maxdepth 1 -type f -executable -printf '%f\n' | head -n1 || true)"
[ -n "$APP_BIN" ] || die "Could not find an executable in $BUILD_DIR. Check 'ls $BUILD_DIR'."
log "Detected application executable: $APP_BIN"

# ---------------------------------------------------------------------------
# 3. Assemble the AppDir
# ---------------------------------------------------------------------------
log "Assembling AppDir..."
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin"
cp -r "$BUILD_DIR"/. "$APPDIR/usr/bin/"

# AppRun launcher
cat > "$APPDIR/AppRun" <<EOF
#!/bin/bash
HERE="\$(dirname "\$(readlink -f "\$0")")"
exec "\$HERE/usr/bin/$APP_BIN" "\$@"
EOF
chmod +x "$APPDIR/AppRun"

# .desktop entry
cat > "$APPDIR/$APP_BIN.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=$APP_NAME
Exec=$APP_BIN
Icon=$APP_BIN
Categories=Network;
Terminal=false
EOF

# Icon: use provided icon, otherwise generate a tiny placeholder so
# appimagetool doesn't fail on a missing icon.
if [ -f "$ICON_SRC" ]; then
    cp "$ICON_SRC" "$APPDIR/$APP_BIN.png"
    log "Using icon: $ICON_SRC"
else
    log "No icon at '$ICON_SRC' - writing a 1x1 placeholder PNG."
    # Minimal valid 1x1 transparent PNG (base64).
    base64 -d > "$APPDIR/$APP_BIN.png" <<'PNG'
iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==
PNG
fi

# ---------------------------------------------------------------------------
# 4. Get appimagetool
# ---------------------------------------------------------------------------
if [ ! -x "$APPIMAGETOOL" ]; then
    log "Downloading appimagetool..."
    wget -q -O "$APPIMAGETOOL" \
        "https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-${ARCH}.AppImage"
    chmod +x "$APPIMAGETOOL"
fi

# ---------------------------------------------------------------------------
# 5. Build the AppImage
# ---------------------------------------------------------------------------
log "Building AppImage -> $OUTPUT"
# --appimage-extract-and-run avoids needing FUSE for appimagetool itself.
ARCH="$ARCH" "$APPIMAGETOOL" --appimage-extract-and-run "$APPDIR" "$ROOT/$OUTPUT"

chmod +x "$ROOT/$OUTPUT"
log "Done: $ROOT/$OUTPUT"
log "Test it with:  ./$OUTPUT"
