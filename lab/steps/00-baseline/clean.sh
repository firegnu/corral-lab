#!/bin/sh
. "$(dirname "$0")/../common.sh"
echo "00 只读检查，没有要清理的（基线 $LAB_TMP/confhash.json 留给最后核对；要重记：lab/bin/confhash save --force）"
