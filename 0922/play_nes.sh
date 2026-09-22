#!/usr/bin/env bash
# NES 復古遊戲啟動器
# 用法: ./play_nes.sh  (或直接 ./play_nes.py)
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 優先使用專案的 uv 虛擬環境
for py in "$DIR/../.venv/bin/python" "$DIR/../../.venv/bin/python"; do
    if [ -x "$py" ]; then
        exec "$py" "$DIR/play_nes.py" "$@"
    fi
done

PY="$(command -v python3)"
if [ -z "$PY" ]; then
    echo "找不到 python3,請先安裝 Python"
    exit 1
fi
exec "$PY" "$DIR/play_nes.py" "$@"