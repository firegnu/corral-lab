#!/bin/sh
# 只在单独重跑 10 时用：后面的步骤都要用 lab-a/dev
. "$(dirname "$0")/../common.sh"
corral stop lab-a/dev --timeout 45 || true
