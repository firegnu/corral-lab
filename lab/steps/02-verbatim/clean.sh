#!/bin/sh
. "$(dirname "$0")/../common.sh"
for n in lab/verb-claude lab/verb-codex; do corral stop "$n" --timeout 40 >/dev/null 2>&1 || true; done
"$BIN/need" --absent lab/verb-claude lab/verb-codex
