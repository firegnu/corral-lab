#!/bin/sh
. "$(dirname "$0")/../common.sh"
"$BIN/strays" --stop
for n in $(corral ls | "$PY" -c 'import json,sys; print(" ".join(a["name"] for a in json.load(sys.stdin)["agents"] if a["name"].startswith("lab/fan")))'); do
  corral stop "$n" --timeout 45 || true
done
