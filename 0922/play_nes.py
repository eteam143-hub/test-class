#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NES 復古遊戲選單與啟動器

掃描本資料夾中的 roms/,以 pygame 顯示遊戲清單,
選擇後呼叫 Mednafen 模擬器執行,退出後回到選單。
啟動失敗的詳細原因會顯示在畫面上,並寫入 launcher.log。
"""
import os
import shutil
import subprocess
import sys
import time

import pygame

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROM_DIR = os.path.join(BASE_DIR, "roms")
LOG_FILE = os.path.join(BASE_DIR, "launcher.log")
CFG_TEMPLATE = os.path.join(BASE_DIR, "mednafen.cfg")
SNAKE_SCRIPT = os.path.join(BASE_DIR, "snake.py")
MEDNAFEN_HOME = os.path.expanduser("~/.mednafen")
MEDNAFEN_CFG = os.path.join(MEDNAFEN_HOME, "mednafen.cfg")

ROM_EXTS = (".nes", ".fds", ".unf", ".unif", ".nsf")

APP_VERSION = "v4 (2026-09-22)"

# 內附遊戲的選單名稱；ROM 實體檔名不變，避免影響模擬器載入。
GAME_TITLES = {
    "Alter Ego.nes": "另一個自我",
    "Columns.nes": "寶石方塊",
    "D-Pad Hero.nes": "方向鍵英雄",
    "Fishfall.nes": "魚兒墜落",
    "Geminim.nes": "雙子星",
    "Hoppin Mad.nes": "瘋狂跳跳",
    "Nanaca-Crash!!.nes": "七香衝撞！！",
    "Snake.nes": "貪食蛇",
}

# 找不到中文字型時自動改用英文,確保絕不出現亂碼
T = {
    "title": "NES 任天堂復古遊戲機",
    "title_en": "NES Retro Machine",
    "gamepad": "手把:",
    "pad": "Gamepad:",
    "no_rom": "roms/ 資料夾裡還沒有遊戲 ROM",
    "no_rom_en": "No ROM in the roms/ folder",
    "no_rom2": "請將 .nes 遊戲檔放入 roms/ 資料夾後重新啟動",
    "no_rom2_en": "Drop .nes files into roms/ and restart",
    "exit_item": "離開遊戲、回到桌面",
    "exit_item_en": "Exit to desktop",
    "controls": [
        "↑↓ 或 W/S:選擇項目      Enter 或 Space:確認",
        "遊戲中按 ESC:結束遊戲、回到此選單",
        "選單中按 ESC 或 Q:離開、回到桌面",
        "遊戲按鍵:方向=↑↓←→  B=Z  A=X  START=Enter  SELECT=Tab",
    ],
    "controls_en": [
        "Up/Down or W/S: choose    Enter or Space: confirm",
        "In-game: ESC exits and returns to this menu",
        "In menu: ESC or Q exits to desktop",
        "Game keys: arrows=D-pad  Z=B  X=A  Enter=START  Tab=SELECT",
    ],
    "launching": "正在啟動: ",
    "launching_en": "Starting: ",
    "esc_back": "遊戲中按 ESC 可結束,回到此選單",
    "esc_back_en": "Press ESC in-game to return here",
    "play_keys": "遊戲按鍵:方向鍵移動　Z=B　X=A　Enter=開始　Tab=選擇",
    "play_keys_en": "Game keys: arrows move  Z=B  X=A  Enter=Start  Tab=Select",
    "fail_title": "遊戲啟動失敗!原因如下:",
    "fail_title_en": "Failed to launch! Reason:",
    "any_key": "按任意鍵回到選單",
    "any_key_en": "Press any key to return",
    "shot_saved": "已儲存畫面截圖到 0922/menu.png",
    "shot_saved_en": "Screenshot saved to 0922/menu.png",
}


def T2(k):
    """依中文字型是否可用挑中文或英文文案"""
    if find_cjk_font_path():
        return T[k]
    return T.get(k + "_en", T[k])


# 會畫出繁體中文的字型名稱(依優先順序)
CJK_FONT_NAMES = (
    "droidsansfallback",
    "notosanscjktc",
    "notosanscjk",
    "notosanscjk tc",
    "noto sans cjk tc",
    "wqyzenhei",
    "wqymicrohei",
    "arplumingtw",
    "pmingliu",
    "dfkai",
    "dflisong",
)

_font_path_cache = None


class MixedFont:
    """以繁中字型畫漢字、以一般字型補足英文與按鍵符號。"""

    def __init__(self, cjk_path, size):
        self.cjk = pygame.font.Font(cjk_path, size)
        latin_path = pygame.font.match_font("dejavusans")
        self.latin = pygame.font.Font(latin_path, size)
        self._height = max(self.cjk.get_height(), self.latin.get_height())
        missing = self.cjk.render("\U0010ffff", True, (255, 255, 255))
        self._missing_size = missing.get_size()
        self._missing_bytes = pygame.image.tostring(missing, "RGBA")
        self._cjk_chars = {}

    def get_height(self):
        return self._height

    def _has_cjk_glyph(self, char):
        if char not in self._cjk_chars:
            glyph = self.cjk.render(char, True, (255, 255, 255))
            self._cjk_chars[char] = not (
                glyph.get_size() == self._missing_size
                and pygame.image.tostring(glyph, "RGBA") == self._missing_bytes
            )
        return self._cjk_chars[char]

    def render(self, text, antialias, color, background=None):
        """維持 pygame.font.Font.render 的常用介面。"""
        parts = []
        for char in text:
            font = self.cjk if self._has_cjk_glyph(char) else self.latin
            parts.append(font.render(char, antialias, color, background))
        width = sum(part.get_width() for part in parts)
        surface = pygame.Surface((max(1, width), self._height), pygame.SRCALPHA)
        x = 0
        for part in parts:
            surface.blit(part, (x, (self._height - part.get_height()) // 2))
            x += part.get_width()
        return surface


def log(msg):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
    except OSError:
        pass
    print(msg)


def list_roms():
    if not os.path.isdir(ROM_DIR):
        return []
    roms = []
    for name in sorted(os.listdir(ROM_DIR)):
        if name.lower().endswith(ROM_EXTS):
            roms.append(os.path.join(ROM_DIR, name))
    return roms


def game_title(game):
    """回傳選單用名稱；未設定翻譯的自訂 ROM 維持原檔名。"""
    filename = os.path.basename(game)
    if find_cjk_font_path():
        return GAME_TITLES.get(filename, filename)
    return filename


def ensure_mednafen_config():
    """把專案的 mednafen.cfg 合併寫入 ~/.mednafen/mednafen.cfg"""
    if not os.path.exists(CFG_TEMPLATE):
        return
    os.makedirs(MEDNAFEN_HOME, exist_ok=True)
    overrides = {}
    with open(CFG_TEMPLATE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, val = line.split(None, 1)
            overrides[key] = val

    lines = []
    if os.path.exists(MEDNAFEN_CFG):
        with open(MEDNAFEN_CFG, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()

    changed = False
    kept, seen = [], set()
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and " " in stripped:
            key = stripped.split(None, 1)[0]
            if key in overrides:
                kept.append(f"{key} {overrides[key]}")
                seen.add(key)
                changed = changed or line != f"{key} {overrides[key]}"
                continue
        kept.append(line)
    if kept and kept[-1] != "":
        kept.append("")
    for key, val in overrides.items():
        if key not in seen:
            kept.append(f"{key} {val}")
            changed = True

    if changed:
        with open(MEDNAFEN_CFG, "w", encoding="utf-8") as f:
            f.write("\n".join(kept) + "\n")


def _font_files():
    """收集系統上所有字形檔路徑"""
    paths = []
    for base in (
        "/usr/share/fonts",
        "/usr/local/share/fonts",
        os.path.expanduser("~/.fonts"),
        os.path.expanduser("~/.local/share/fonts"),
        os.path.join(BASE_DIR, "fonts"),
    ):
        if not os.path.isdir(base):
            continue
        for root, _dirs, files in os.walk(base):
            for name in files:
                if name.lower().endswith((".ttf", ".ttc", ".otf")):
                    paths.append(os.path.join(root, name))
    return paths


def _can_render_cjk(font, sample="任天堂復古遊戲機繁體中文測試"):
    """確認字型有中文字形，而不是把所有缺字畫成同一個方塊。"""
    try:
        # pygame 對缺字仍會畫出「豆腐字」，所以只檢查有無像素並不可靠。
        # 用一個不可能存在的 Unicode 字元當作缺字樣本；所有中文字都和它
        # 長得一樣時，代表這個字型沒有真正的中文字形。
        missing = font.render("\U0010ffff", True, (255, 255, 255))
        missing_bytes = pygame.image.tostring(missing, "RGBA")
        for char in sample:
            glyph = font.render(char, True, (255, 255, 255))
            if (
                glyph.get_size() == missing.get_size()
                and pygame.image.tostring(glyph, "RGBA") == missing_bytes
            ):
                return False
        return True
    except pygame.error:
        return False


def find_cjk_font_path():
    """找到一個能渲染繁體中文的字型檔路徑,找不到回 None"""
    global _font_path_cache
    if _font_path_cache is not None:
        return _font_path_cache

    def try_path(path):
        try:
            if _can_render_cjk(pygame.font.Font(path, 24)):
                return path
        except pygame.error:
            return None
        return None

    for name in CJK_FONT_NAMES:
        p = pygame.font.match_font(name)
        if p and try_path(p):
            _font_path_cache = p
            return p

    for fam in pygame.font.get_fonts():
        if any(k in fam for k in ("droid", "cjk", "zh", "wqy", "noto", "kai", "sung", "ming", "hei")):
            p = pygame.font.match_font(fam)
            if p and try_path(p):
                _font_path_cache = p
                return p

    for path in _font_files():
        low = path.lower()
        if any(k in low for k in ("droid", "cjk", "wqy", "noto", "kai", "sung", "ming", "hei")):
            p = try_path(path)
            if p:
                _font_path_cache = p
                return p

    for path in _font_files():
        p = try_path(path)
        if p:
            _font_path_cache = p
            return p

    _font_path_cache = ""
    return None


def load_font(size):
    path = find_cjk_font_path()
    if path:
        return MixedFont(path, size)
    log("警告:沒找到可顯示中文的字型,選單可能出現亂碼")
    return pygame.font.Font(None, size)


def draw_menu(screen, roms, index, font_title, font_item, font_small, joystick_names, flash_msg=None):
    w, h = screen.get_size()
    bg = (20, 20, 40)
    screen.fill(bg)

    title = font_title.render(T2("title"), True, (255, 230, 120))
    screen.blit(title, title.get_rect(centerx=w // 2, y=30))

    ver = font_small.render(APP_VERSION, True, (90, 100, 130))
    screen.blit(ver, ver.get_rect(topright=(w - 16, 12)))

    if joystick_names:
        pad = font_small.render(T2("gamepad") + "、".join(joystick_names), True, (150, 200, 255))
        screen.blit(pad, pad.get_rect(centerx=w // 2, y=80))

    if not roms:
        msg = font_item.render(T2("no_rom"), True, (200, 200, 200))
        screen.blit(msg, msg.get_rect(center=(w // 2, 145)))
        msg2 = font_small.render(T2("no_rom2"), True, (160, 160, 160))
        screen.blit(msg2, msg2.get_rect(center=(w // 2, 185)))

    # 「離開遊戲」和 ROM 使用同一個可選清單，避免它只是一行看得到卻按不到的說明。
    items = [game_title(rom) for rom in roms] + [T2("exit_item")]
    area_h = h - 330
    row_h = font_item.get_height() + 10
    visible = max(area_h // max(1, row_h), 1)
    start = max(0, min(index - visible // 2, len(items) - visible))
    y = 220 if not roms else 140
    for i in range(start, min(start + visible, len(items))):
        is_exit = i == len(roms)
        name = items[i]
        if i == index:
            box = pygame.Rect(w // 2 - 380, y - 4, 760, font_item.get_height() + 8)
            color = (140, 65, 65) if is_exit else (70, 90, 160)
            pygame.draw.rect(screen, color, box, border_radius=6)
            surf = font_item.render("▶ " + name, True, (255, 255, 255))
        else:
            color = (255, 180, 180) if is_exit else (210, 210, 210)
            surf = font_item.render("  " + name, True, color)
        screen.blit(surf, (w // 2 - 360, y))
        y += row_h

    hint_y = h - 160
    for t in T2("controls"):
        surf = font_small.render(t, True, (150, 200, 120))
        screen.blit(surf, surf.get_rect(centery=hint_y, centerx=w // 2))
        hint_y += font_small.get_height() + 6

    if flash_msg:
        m = font_small.render(flash_msg, True, (255, 255, 255))
        box = pygame.Rect(0, h - 200, w, m.get_height() + 16)
        pygame.draw.rect(screen, (30, 50, 90), box)
        screen.blit(m, m.get_rect(centerx=w // 2, centery=box.centery))

    pygame.display.flip()


def wait_launch(screen, font_small, game):
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))
    msg = font_small.render(T2("launching") + game_title(game), True, (255, 255, 255))
    screen.blit(msg, msg.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 44)))
    keys = font_small.render(T2("play_keys"), True, (150, 220, 150))
    screen.blit(keys, keys.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2)))
    msg2 = font_small.render(T2("esc_back"), True, (220, 220, 220))
    screen.blit(msg2, msg2.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 44)))
    pygame.display.flip()
    pygame.event.pump()
    time.sleep(1.2)


def launch_local_snake(size):
    """啟動內建的 pygame 貪食蛇；結束後恢復選單視窗。"""
    if not os.path.exists(SNAKE_SCRIPT):
        return "找不到內建貪食蛇程式 snake.py"

    pygame.quit()
    try:
        proc = subprocess.run([sys.executable, SNAKE_SCRIPT])
    except OSError as exc:
        return f"無法啟動貪食蛇:\n{exc}"

    try:
        pygame.display.init()
        pygame.display.set_mode(size)
        pygame.display.set_caption("NES 任天堂復古遊戲機")
    except pygame.error as exc:
        log(f"重開 pygame 顯示失敗: {exc}")

    if proc.returncode:
        message = f"貪食蛇異常結束(returncode={proc.returncode})"
        log(message)
        return message
    return None


def launch_game(game, size):
    """啟動 mednafen 跑指定 ROM。成功回傳 None,失敗回傳錯誤說明。"""
    if os.path.basename(game) == "Snake.nes":
        return launch_local_snake(size)

    mednafen = shutil.which("mednafen")
    if not mednafen:
        log("找不到 mednafen")
        return "找不到 mednafen 模擬器,請先安裝:\n  sudo apt install mednafen"

    ensure_mednafen_config()

    forced_driver = (
        pygame.display.get_driver() if pygame.display.get_init() else None
    )
    if forced_driver:
        log(f"啟動 {os.path.basename(game)}  pygame 驅動={forced_driver}")
    pygame.quit()

    windowed = os.environ.get("NES_WINDOW") == "1"

    proc = None
    for attempt in range(2):
        env = os.environ.copy()
        if attempt == 0 and forced_driver:
            env["SDL_VIDEODRIVER"] = forced_driver
        args = [mednafen] + (["-fs", "0"] if windowed else []) + [game]
        try:
            proc = subprocess.run(args, capture_output=True, text=True, env=env)
        except Exception as exc:
            return f"無法執行 mednafen:\n{exc}"
        if proc.returncode == 0 or not (attempt == 0 and forced_driver):
            break
        log("強制驅動失敗,改用自動偵測重試一次…")

    try:
        pygame.display.init()
        pygame.display.set_mode(size)
        pygame.display.set_caption("NES 任天堂復古遊戲機")
    except pygame.error as exc:
        log(f"重開 pygame 顯示失敗: {exc}")

    if proc and proc.returncode != 0:
        out = (proc.stdout or "") + "\n" + (proc.stderr or "")
        out = "\n".join(
            l for l in out.splitlines() if "Error opening file" not in l
        )
        tail = out.strip()[-1200:]
        log(f"模擬器異常結束 returncode={proc.returncode}:\n{tail}")
        return (
            "模擬器異常結束(returncode="
            + str(proc.returncode)
            + ")\n\n詳細錯誤:\n"
            + tail
            + "\n\n(已寫入 launcher.log)"
        )
    return None


def show_error(screen, font_small, font_item, message):
    """顯示啟動失敗原因,等待按下任意鍵回到選單。"""
    w, h = screen.get_size()
    panel = pygame.Surface((w - 80, h - 120), pygame.SRCALPHA)
    panel.fill((90, 20, 25, 235))
    screen.blit(panel, (40, 60))

    title = font_item.render(T2("fail_title"), True, (255, 120, 120))
    screen.blit(title, title.get_rect(centerx=w // 2, y=90))

    line_h = font_small.get_height() + 4
    max_lines = (h - 220) // line_h
    lines = message.splitlines()
    y = 150
    for line in lines[:max_lines]:
        surf = font_small.render(line[:100], True, (255, 235, 235))
        screen.blit(surf, (70, y))
        y += line_h
    if len(lines) > max_lines:
        more = font_small.render("…尚有更多,請看 launcher.log", True, (200, 200, 200))
        screen.blit(more, (70, y))

    hint = font_small.render(T2("any_key"), True, (255, 230, 120))
    hrect = hint.get_rect()
    hrect.center = (w // 2, h - 140)
    screen.blit(hint, hrect)
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        time.sleep(0.05)


def main():
    global screen_size
    os.environ.setdefault("SDL_VIDEO_CENTERED", "1")
    pygame.init()
    info = pygame.display.Info()
    screen_size = (info.current_w, info.current_h)
    screen = pygame.display.set_mode(screen_size, pygame.FULLSCREEN)
    pygame.display.set_caption("NES 任天堂復古遊戲機")

    font_title = load_font(44)
    font_item = load_font(30)
    font_small = load_font(22)

    joystick_names = []
    try:
        pygame.joystick.init()
        joystick_names = [
            pygame.joystick.Joystick(i).get_name()
            for i in range(pygame.joystick.get_count())
        ]
    except pygame.error:
        pass

    roms = list_roms()
    index = 0
    clock = pygame.time.Clock()
    running = True
    flash_msg = None
    flash_until = 0.0

    while running:
        now = time.time()
        if flash_until and now > flash_until:
            flash_msg = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                elif event.key == pygame.K_F9:
                    try:
                        pygame.image.save(screen, os.path.join(BASE_DIR, "menu.png"))
                        flash_msg = T2("shot_saved")
                        flash_until = now + 3
                    except pygame.error as exc:
                        log(f"儲存截圖失敗: {exc}")
                elif event.key in (pygame.K_UP, pygame.K_w):
                    index = (index - 1) % (len(roms) + 1)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    index = (index + 1) % (len(roms) + 1)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE) and roms:
                    if index == len(roms):
                        running = False
                        continue
                    game = roms[index]
                    wait_launch(screen, font_small, game)
                    error = launch_game(game, screen_size)
                    screen = pygame.display.set_mode(screen_size, pygame.FULLSCREEN)
                    if error:
                        show_error(screen, font_small, font_item, error)
                    pygame.event.clear()
                    roms = list_roms()
                    if index > len(roms):
                        index = len(roms)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    running = False
            elif event.type == pygame.JOYHATMOTION:
                if event.value[1] > 0:
                    index = (index - 1) % (len(roms) + 1)
                elif event.value[1] < 0:
                    index = (index + 1) % (len(roms) + 1)
            elif event.type == pygame.JOYBUTTONDOWN and event.button == 0 and roms:
                if index == len(roms):
                    running = False
                    continue
                game = roms[index]
                wait_launch(screen, font_small, game)
                error = launch_game(game, screen_size)
                screen = pygame.display.set_mode(screen_size, pygame.FULLSCREEN)
                if error:
                    show_error(screen, font_small, font_item, error)
                pygame.event.clear()
                roms = list_roms()
                if index > len(roms):
                    index = len(roms)
            elif event.type == pygame.JOYBUTTONDOWN and event.button == 0:
                running = False

        draw_menu(screen, roms, index, font_title, font_item, font_small, joystick_names, flash_msg)
        clock.tick(30)

    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
