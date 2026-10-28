#!/bin/sh
# Run from any working directory; override PYTHON to select Python >= 3.10.
set -eu

cd "$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
PYTHON=${PYTHON:-python3}

"$PYTHON" -c 'import sys; sys.exit("Cal Python 3.10 o superior; prova PYTHON=python3.12 sh scripts/check-foundation.sh") if sys.version_info < (3, 10) else None'
"$PYTHON" -m unittest discover -s tests -v
"$PYTHON" scripts/foundation.py validate
"$PYTHON" scripts/routing.py validate
"$PYTHON" scripts/continuity.py validate
"$PYTHON" scripts/continuity.py --root evals/pilot/corporate validate
"$PYTHON" scripts/evaluate.py report --input evals/pilot/records.json > /dev/null
