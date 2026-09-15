#!/bin/sh
# 评审方可能照请求不写文件（→ undelivered），也可能照交接的话写了（→ delivered）。
# 通过标准是「判定和文件实际情况一致」，不管它听了哪边的话。
. "$(dirname "$0")/../common.sh"
exec "$BIN/roundcheck" lab-a --wait 600
