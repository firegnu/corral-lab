#!/bin/sh
. "$(dirname "$0")/../common.sh"
for n in lab/life-cx lab/life-cc; do corral stop "$n" --timeout 45 >/dev/null 2>&1 || true; done
"$BIN/need" --absent lab/life-cx lab/life-cc
