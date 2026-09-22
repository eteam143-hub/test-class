#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""瑪利歐兄弟 NES ROM 啟動器（僅使用使用者自行提供的合法 ROM）。"""
import os
import shutil
import subprocess
import sys


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROM_DIR = os.path.join(BASE_DIR, "roms")
CONFIG_FILE = os.path.join(BASE_DIR, "mednafen.cfg")
MEDNAFEN_HOME = os.path.join(BASE_DIR, ".mednafen")
NATIVE_GAME = os.path.join(BASE_DIR, "plumber_adventure.py")
ROM_EXTENSIONS = (".nes", ".fds", ".unf", ".unif")

# 常見的合法自備 ROM 檔名優先順序。
PREFERRED_ROM_NAMES = (
    "Super Mario Bros.nes",
    "Super Mario Bros. (World).nes",
    "Mario Bros.nes",
)


def find_mario_rom():
    """在 roms/ 尋找名稱含 mario 的 NES ROM，並優先選擇常見檔名。"""
    if not os.path.isdir(ROM_DIR):
        return None

    roms = [
        name
        for name in os.listdir(ROM_DIR)
        if name.lower().endswith(ROM_EXTENSIONS)
    ]
    by_casefold = {name.casefold(): name for name in roms}
    for preferred in PREFERRED_ROM_NAMES:
        if preferred.casefold() in by_casefold:
            return os.path.join(ROM_DIR, by_casefold[preferred.casefold()])

    matches = sorted(name for name in roms if "mario" in name.casefold())
    return os.path.join(ROM_DIR, matches[0]) if matches else None


def launch_native_game():
    """沒有自備 ROM 時，啟動專案內附的原創跳躍遊戲。"""
    if not os.path.exists(NATIVE_GAME):
        print(f"找不到內建遊戲程式：{NATIVE_GAME}")
        return 1
    print("未找到自備瑪利歐 ROM，改啟動內建的原創水管工跳躍冒險。")
    return subprocess.run([sys.executable, NATIVE_GAME]).returncode


def main():
    rom = find_mario_rom()
    if not rom:
        return launch_native_game()

    mednafen = shutil.which("mednafen")
    if not mednafen:
        print("找不到 Mednafen 模擬器。請先執行：")
        print("  sudo apt install mednafen")
        return 1
    if not os.path.exists(CONFIG_FILE):
        print(f"找不到設定檔：{CONFIG_FILE}")
        return 1

    os.makedirs(MEDNAFEN_HOME, exist_ok=True)
    env = os.environ.copy()
    env["MEDNAFEN_HOME"] = MEDNAFEN_HOME
    print(f"啟動遊戲：{os.path.basename(rom)}")
    print("操作：方向鍵移動、Z=B、X=A、Enter=開始、Tab=選擇、ESC=結束並回到桌面")

    result = subprocess.run([mednafen, "-ovconfig", CONFIG_FILE, rom], env=env)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
