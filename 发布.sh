#!/bin/bash
# 一条命令：重建索引 → 提交 → 推送
# 用法：bash ~/Documents/日语语法/发布.sh
set -euo pipefail
cd "$(dirname "$0")"

TOKEN_FILE="$HOME/.config/nihongo-grammar/token"
ASKPASS="$HOME/.config/nihongo-grammar/askpass.sh"

python3 更新索引.py

git add -A
if git diff --cached --quiet; then
  echo "· 没有新内容，跳过提交"
  exit 0
fi

STAMP="$(date +%Y-%m-%d)"
git commit -q -m "更新 ${STAMP} 语法复习"

if [ -f "$TOKEN_FILE" ] && [ -x "$ASKPASS" ]; then
  export GIT_ASKPASS="$ASKPASS"
  export NIHONGO_TOKEN="$(cat "$TOKEN_FILE")"
  export GIT_TERMINAL_PROMPT=0
fi

git push -q origin HEAD
echo "· 已推送 $(git rev-parse --short HEAD) → $(git remote get-url origin)"
