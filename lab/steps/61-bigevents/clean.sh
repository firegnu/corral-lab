#!/bin/sh
. "$(dirname "$0")/../common.sh"
corral stop lab/big --timeout 45 >/dev/null 2>&1 || true
"$BIN/need" --absent lab/big
