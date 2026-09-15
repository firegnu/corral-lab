#!/bin/sh
. "$(dirname "$0")/../common.sh"
"$BIN/snapshot" save after-quit
exec "$BIN/snapshot" compare before-quit after-quit
