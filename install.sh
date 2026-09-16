#!/usr/bin/env bash
# axgraph install script (pip install-style experience)
#
# Usage:   ./install.sh           # symlink into ~/.local/bin
#          ./install.sh /some/bin # symlink into <some/bin> instead
#
# Effect:  after this script runs, typing `ax` in a new shell works —
#          no need to know axgraph's install path or modify PATH manually.
#          Symlink points at <axgraph>/bin/ax, so updates to the source
#          (git pull) take effect automatically (just re-run install.sh).
#
# pip equivalent: console_scripts entry point, written to <venv>/bin
#                 (we use XDG user bin ~/.local/bin instead — no venv needed)

set -euo pipefail

# Resolve axgraph root (this script lives in <axgraph>/, one level up if invoked
# from elsewhere; this script is at axgraph/install.sh, so dirname gives axgraph/).
AXGRAPH_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

TARGET_DIR="${1:-$HOME/.local/bin}"
TARGET="$TARGET_DIR/ax"
SOURCE="$AXGRAPH_ROOT/bin/ax"

# Sanity checks
if [[ ! -f "$SOURCE" ]]; then
    echo "install.sh: cannot find $SOURCE — is this script inside the axgraph repo?" >&2
    exit 1
fi
if [[ ! -x "$SOURCE" ]]; then
    echo "install.sh: $SOURCE is not executable — chmod +x bin/ax first" >&2
    exit 1
fi

mkdir -p "$TARGET_DIR"

# Atomic symlink (mv into place) so a half-installed state never points at nothing.
tmp_link="$TARGET_DIR/.ax.tmp.$$"
ln -sf "$SOURCE" "$tmp_link"
mv -f "$tmp_link" "$TARGET"

# Detect whether TARGET_DIR is on PATH (warn but don't fail)
case ":$PATH:" in
    *":$TARGET_DIR:"*) echo "✓ install.sh: $TARGET_DIR is on PATH — 'ax' is ready" ;;
    *) echo "⚠ install.sh: $TARGET_DIR is NOT on PATH for this shell." >&2
       echo "  Add it now:   export PATH=\"\$HOME/.local/bin:\$PATH\"" >&2
       echo "  Or permanently: echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc" >&2
       echo "  Then:        new shell, type 'ax --version'" >&2
       ;;
esac

echo "✓ install.sh: symlinked $TARGET → $SOURCE"
echo "  Plugin root: $AXGRAPH_ROOT"
echo "  Test:        ax --version   (should print 0.1.0)"
echo "  Uninstall:   rm $TARGET"
