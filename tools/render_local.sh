#!/bin/bash
# render_local.sh <video...> : renders using every CPU core and joins. Output in out/
set -e; cd "$(dirname "$0")/.."
for v in "$@"; do python3 videos/$v.py all parts/$v; done
./tools/join.sh parts out "$@"
