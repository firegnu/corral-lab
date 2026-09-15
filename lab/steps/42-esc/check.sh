#!/bin/sh
# check.sh a：Claude Code 评审方 → interrupted，不叫醒 dev
# check.sh b：Codex 评审方 → undelivered（最后事件 Interrupt），叫醒 dev
. "$(dirname "$0")/../common.sh"
case "${1:-}" in
  a) exec "$BIN/roundcheck" lab-a --expect interrupted --wait 120 ;;
  b) "$BIN/roundcheck" lab-a --expect undelivered --wait 300 || true
     grep '"undelivered"' "$RUN/lab-a/watch.log" | tail -1 ;;
  *) echo "用法：check.sh a|b"; exit 1 ;;
esac
