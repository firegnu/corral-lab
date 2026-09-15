#!/bin/sh
# 停掉 skill 起的、没被 stop 的临时 agent（工作目录在 lab 目录里、名字不是 lab 前缀）
. "$(dirname "$0")/../common.sh"
"$BIN/strays" --stop
