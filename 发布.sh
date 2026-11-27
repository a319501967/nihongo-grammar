#!/bin/bash
# 一条命令：重建索引 → 提交 → 推送
# 用法：bash ~/Documents/日语语法/发布.sh
#
# 依赖：本机 Clash Verge（7897）开着会更稳；没开则自动退化为直连。
set -uo pipefail
cd "$(dirname "$0")"

TOKEN_FILE="$HOME/.config/nihongo-grammar/token"
ASKPASS="$HOME/.config/nihongo-grammar/askpass.sh"

# ---------- 1. 重建索引 ----------
python3 更新索引.py || { echo "✗ 索引生成失败"; exit 1; }

# ---------- 2. 提交 ----------
git add -A
if git diff --cached --quiet; then
  echo "· 没有新内容，跳过提交"
else
  # 用最新那份页面的日期做提交信息，避免隔天补推时日期错位
  LATEST="$(ls -1 [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].html 2>/dev/null | sort | tail -1)"
  STAMP="${LATEST%.html}"
  [ -z "$STAMP" ] && STAMP="$(date +%Y-%m-%d)"
  git commit -q -m "更新 ${STAMP} 语法复习"
  echo "· 已提交 $(git rev-parse --short HEAD)"
fi

# ---------- 3. 准备凭据 ----------
if [ -f "$TOKEN_FILE" ] && [ -x "$ASKPASS" ]; then
  export GIT_ASKPASS="$ASKPASS"
  export NIHONGO_TOKEN="$(cat "$TOKEN_FILE")"
  export GIT_TERMINAL_PROMPT=0
fi

# ---------- 4. 选一个能用的通道 ----------
PROXY=""
for p in 7897 7890 1087; do
  if nc -z -G 1 127.0.0.1 "$p" 2>/dev/null; then
    PROXY="http://127.0.0.1:$p"
    break
  fi
done
GITNET=(-c http.version=HTTP/1.1)
[ -n "$PROXY" ] && GITNET+=(-c "http.proxy=$PROXY")

# ---------- 5. 推送，失败重试一次 ----------
for try in 1 2; do
  if git "${GITNET[@]}" push -q origin HEAD 2>/tmp/发布_error.log; then
    echo "· 已推送 $(git rev-parse --short HEAD)${PROXY:+  经 $PROXY}"
    echo "· 线上地址 https://a319501967.github.io/nihongo-grammar/"
    exit 0
  fi
  echo "· 第 $try 次推送失败：$(tail -1 /tmp/发布_error.log)"
  [ "$try" = 1 ] && sleep 2
done

echo "✗ 推送失败。检查：Clash Verge 是否开启、网络是否正常。"
echo "  日志：/tmp/发布_error.log"
echo "  手动重试：cd ~/Documents/日语语法 && bash 发布.sh"
exit 1
