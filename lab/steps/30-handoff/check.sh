#!/bin/sh
. "$(dirname "$0")/../common.sh"
exec "$BIN/roundcheck" lab-a --expect delivered --contains LAB-A-TOKEN --wait 600
