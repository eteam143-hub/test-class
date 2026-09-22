#!/usr/bin/env bash
# 從此檔案所在位置啟動，確保使用專案的 uv 虛擬環境。
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"
uv run python 0922-1/solitaire_game.py
