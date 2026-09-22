#!/usr/bin/env bash
# 瑪利歐兄弟 NES 啟動檔
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 優先使用此專案的 uv 虛擬環境。
if [ -x "$DIR/../.venv/bin/python" ]; then
    exec "$DIR/../.venv/bin/python" "$DIR/play_mario.py" "$@"
fi

exec python3 "$DIR/play_mario.py" "$@"
