"""小小大富翁：雙人（玩家對電腦）桌面遊戲。"""

from __future__ import annotations

import random
import sys
from dataclasses import dataclass
from pathlib import Path

import pygame


WIDTH, HEIGHT = 1120, 760
BOARD_X, BOARD_Y, BOARD_SIZE = 35, 35, 650
CELL = BOARD_SIZE // 6
FPS = 60
START_MONEY = 1200

BG = (246, 240, 222)
INK = (54, 44, 36)
PANEL = (255, 252, 244)
BLUE = (48, 123, 196)
RED = (212, 81, 72)
GOLD = (234, 177, 57)
GREEN = (93, 158, 104)

# 先使用系統中確定含有 CJK（含繁體中文）字形的字型；其餘項目是不同
# Linux 發行版常見的安裝位置，讓程式移到其他電腦時也能優先顯示中文。
CJK_FONT_PATHS = (
    "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJKtc-Regular.otf",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
)


@dataclass
class Space:
    name: str
    kind: str
    price: int = 0
    rent: int = 0
    owner: int | None = None


@dataclass
class Player:
    name: str
    color: tuple[int, int, int]
    position: int = 0
    money: int = START_MONEY
    skip_turns: int = 0


SPACES = [
    Space("起點", "start"),
    Space("西門町", "property", 180, 35),
    Space("命運", "chance"),
    Space("淡水老街", "property", 220, 45),
    Space("所得稅", "tax", 0, 100),
    Space("台北101", "property", 300, 60),
    Space("監獄", "jail"),
    Space("九份", "property", 260, 55),
    Space("機會", "chance"),
    Space("日月潭", "property", 320, 65),
    Space("停車場", "rest"),
    Space("阿里山", "property", 360, 75),
    Space("命運", "chance"),
    Space("墾丁", "property", 400, 85),
    Space("旅遊稅", "tax", 0, 130),
    Space("太魯閣", "property", 450, 95),
    Space("回到監獄", "go_jail"),
    Space("澎湖", "property", 500, 110),
    Space("機會", "chance"),
    Space("玉山", "property", 560, 125),
]


def board_positions() -> list[tuple[int, int]]:
    """建立 20 個沿著正方形邊緣的格子座標。"""
    points: list[tuple[int, int]] = []
    for i in range(6):
        points.append((BOARD_X + BOARD_SIZE - CELL * (i + 0.5), BOARD_Y + BOARD_SIZE - CELL / 2))
    for i in range(1, 5):
        points.append((BOARD_X + CELL / 2, BOARD_Y + BOARD_SIZE - CELL * (i + 0.5)))
    for i in range(6):
        points.append((BOARD_X + CELL * (i + 0.5), BOARD_Y + CELL / 2))
    for i in range(1, 5):
        points.append((BOARD_X + BOARD_SIZE - CELL / 2, BOARD_Y + CELL * (i + 0.5)))
    return [(int(x), int(y)) for x, y in points]


POSITIONS = board_positions()


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("小小大富翁")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = self.get_font(22)
        self.small_font = self.get_font(16)
        self.title_font = self.get_font(40)
        self.players = [Player("你", BLUE), Player("電腦", RED)]
        self.turn = 0
        self.dice = 0
        self.message = "歡迎來到小小大富翁！按「擲骰」開始遊戲。"
        self.waiting_buy = False
        self.game_over = False
        self.ai_at = 0
        self.roll_button = pygame.Rect(770, 460, 285, 62)
        self.buy_button = pygame.Rect(770, 540, 135, 55)
        self.skip_button = pygame.Rect(920, 540, 135, 55)

    @staticmethod
    def get_font(size: int) -> pygame.font.Font:
        for font_path in CJK_FONT_PATHS:
            if Path(font_path).is_file():
                return pygame.font.Font(font_path, size)
        for name in ("Noto Sans CJK TC", "Microsoft JhengHei", "WenQuanYi Zen Hei"):
            path = pygame.font.match_font(name)
            if path:
                return pygame.font.Font(path, size)
        return pygame.font.Font(None, size)

    def text(self, surface: pygame.Surface, value: str, pos: tuple[int, int], font: pygame.font.Font, color=INK, center=False) -> None:
        rendered = font.render(value, True, color)
        rect = rendered.get_rect(center=pos) if center else rendered.get_rect(topleft=pos)
        surface.blit(rendered, rect)

    def draw(self) -> None:
        self.screen.fill(BG)
        pygame.draw.rect(self.screen, (209, 232, 204), (BOARD_X + CELL, BOARD_Y + CELL, BOARD_SIZE - 2 * CELL, BOARD_SIZE - 2 * CELL), border_radius=18)
        self.text(self.screen, "小小大富翁", (BOARD_X + BOARD_SIZE // 2, BOARD_Y + BOARD_SIZE // 2 - 20), self.title_font, GREEN, True)
        self.text(self.screen, "先讓對手破產的人獲勝", (BOARD_X + BOARD_SIZE // 2, BOARD_Y + BOARD_SIZE // 2 + 30), self.font, INK, True)

        for i, space in enumerate(SPACES):
            x, y = POSITIONS[i]
            rect = pygame.Rect(x - CELL // 2, y - CELL // 2, CELL, CELL)
            fill = PANEL
            if space.kind == "start": fill = (255, 223, 128)
            elif space.kind == "chance": fill = (198, 226, 247)
            elif space.kind in ("tax", "go_jail"): fill = (249, 202, 195)
            elif space.kind == "jail": fill = (224, 207, 227)
            elif space.kind == "rest": fill = (211, 235, 202)
            pygame.draw.rect(self.screen, fill, rect)
            pygame.draw.rect(self.screen, INK, rect, 2)
            if space.owner is not None:
                pygame.draw.rect(self.screen, self.players[space.owner].color, (rect.x + 3, rect.y + 3, rect.width - 6, 9))
            self.text(self.screen, space.name, (rect.centerx, rect.y + 24), self.small_font, INK, True)
            if space.kind == "property":
                self.text(self.screen, f"${space.price} / 租{space.rent}", (rect.centerx, rect.y + 51), self.small_font, INK, True)
            elif space.kind == "tax":
                self.text(self.screen, f"付 ${space.rent}", (rect.centerx, rect.y + 51), self.small_font, INK, True)

        for idx, player in enumerate(self.players):
            x, y = POSITIONS[player.position]
            offset = -17 if idx == 0 else 17
            pygame.draw.circle(self.screen, player.color, (x + offset, y + 19), 14)
            pygame.draw.circle(self.screen, INK, (x + offset, y + 19), 14, 2)

        pygame.draw.rect(self.screen, PANEL, (735, 35, 350, 680), border_radius=16)
        pygame.draw.rect(self.screen, (215, 203, 180), (735, 35, 350, 680), 2, border_radius=16)
        self.text(self.screen, "遊戲資訊", (760, 63), self.title_font)
        for i, player in enumerate(self.players):
            y = 132 + i * 83
            pygame.draw.circle(self.screen, player.color, (780, y + 14), 13)
            self.text(self.screen, f"{player.name}：${player.money}", (805, y), self.font)
            assets = sum(1 for s in SPACES if s.owner == i)
            self.text(self.screen, f"地產：{assets} 塊　位置：{SPACES[player.position].name}", (805, y + 32), self.small_font)
        turn_name = self.players[self.turn].name
        self.text(self.screen, f"目前回合：{turn_name}", (760, 315), self.font, GREEN)
        self.text(self.screen, f"骰子：{self.dice if self.dice else '-'}", (760, 352), self.font)
        self.draw_wrapped(self.message, 760, 400, 295)
        if not self.game_over and not self.waiting_buy and self.turn == 0:
            self.button(self.roll_button, "擲骰", GOLD)
        if self.waiting_buy:
            self.button(self.buy_button, "買下", GREEN)
            self.button(self.skip_button, "略過", (150, 150, 150))
        if self.game_over:
            self.button(self.roll_button, "重新開始", GOLD)
        pygame.display.flip()

    def draw_wrapped(self, value: str, x: int, y: int, width: int) -> None:
        line, lines = "", []
        for char in value:
            candidate = line + char
            if self.small_font.size(candidate)[0] > width:
                lines.append(line)
                line = char
            else:
                line = candidate
        if line: lines.append(line)
        for i, text in enumerate(lines[:4]):
            self.text(self.screen, text, (x, y + i * 25), self.small_font)

    def button(self, rect: pygame.Rect, label: str, color: tuple[int, int, int]) -> None:
        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        pygame.draw.rect(self.screen, INK, rect, 2, border_radius=10)
        self.text(self.screen, label, rect.center, self.font, (255, 255, 255), True)

    def roll(self) -> None:
        player = self.players[self.turn]
        if player.skip_turns:
            player.skip_turns -= 1
            self.message = f"{player.name} 在監獄休息一回合。"
            self.end_turn()
            return
        self.dice = random.randint(1, 6)
        old = player.position
        player.position = (player.position + self.dice) % len(SPACES)
        if player.position < old:
            player.money += 200
            self.message = f"{player.name} 擲出 {self.dice}，通過起點獲得 $200。"
        else:
            self.message = f"{player.name} 擲出 {self.dice}。"
        self.resolve_space()

    def resolve_space(self) -> None:
        player = self.players[self.turn]
        space = SPACES[player.position]
        if space.kind == "property":
            if space.owner is None:
                if player.money >= space.price:
                    self.message += f" 停在 {space.name}，可用 ${space.price} 買下。"
                    self.waiting_buy = True
                    if self.turn == 1:
                        self.ai_at = pygame.time.get_ticks() + 700
                else:
                    self.message += f" 停在 {space.name}，但資金不足。"
                    self.end_turn()
            elif space.owner != self.turn:
                owner = self.players[space.owner]
                player.money -= space.rent
                owner.money += space.rent
                self.message += f" {space.name} 屬於{owner.name}，支付租金 ${space.rent}。"
                self.check_bankruptcy()
                if not self.game_over: self.end_turn()
            else:
                self.message += f" 這是{player.name}自己的地產。"
                self.end_turn()
        elif space.kind == "tax":
            player.money -= space.rent
            self.message += f" {space.name}：支付 ${space.rent}。"
            self.check_bankruptcy()
            if not self.game_over: self.end_turn()
        elif space.kind == "chance":
            amount = random.choice([-150, -100, 100, 150, 200])
            player.money += amount
            self.message += f" {space.name}：{'獲得' if amount > 0 else '支付'} ${abs(amount)}。"
            self.check_bankruptcy()
            if not self.game_over: self.end_turn()
        elif space.kind == "go_jail":
            player.position = 6
            player.skip_turns = 1
            self.message += f" 被送進監獄，下一回合暫停！"
            self.end_turn()
        else:
            self.message += f" 停在 {space.name}。"
            self.end_turn()

    def buy(self) -> None:
        player = self.players[self.turn]
        space = SPACES[player.position]
        player.money -= space.price
        space.owner = self.turn
        self.message = f"{player.name} 買下了 {space.name}！"
        self.waiting_buy = False
        self.end_turn()

    def check_bankruptcy(self) -> None:
        for player in self.players:
            if player.money < 0:
                winner = self.players[1 - self.players.index(player)]
                self.message = f"{player.name} 破產！{winner.name} 獲勝！按重新開始再玩一局。"
                self.game_over = True

    def end_turn(self) -> None:
        self.turn = 1 - self.turn
        if self.turn == 1 and not self.game_over:
            self.ai_at = pygame.time.get_ticks() + 800

    def reset(self) -> None:
        for space in SPACES: space.owner = None
        self.players = [Player("你", BLUE), Player("電腦", RED)]
        self.turn, self.dice, self.waiting_buy, self.game_over = 0, 0, False, False
        self.message = "新遊戲開始！按「擲骰」開始遊戲。"

    def handle_click(self, pos: tuple[int, int]) -> None:
        if self.game_over and self.roll_button.collidepoint(pos):
            self.reset()
        elif self.turn == 0 and not self.waiting_buy and self.roll_button.collidepoint(pos):
            self.roll()
        elif self.waiting_buy and self.turn == 0:
            if self.buy_button.collidepoint(pos): self.buy()
            elif self.skip_button.collidepoint(pos):
                self.message = "你決定略過這塊地。"
                self.waiting_buy = False
                self.end_turn()

    def update_ai(self) -> None:
        if self.game_over or self.turn != 1 or pygame.time.get_ticks() < self.ai_at:
            return
        if self.waiting_buy:
            space = SPACES[self.players[1].position]
            self.waiting_buy = False
            if self.players[1].money - space.price >= 250 or random.random() < 0.35:
                self.buy()
            else:
                self.message = f"電腦略過了 {space.name}。"
                self.end_turn()
        else:
            self.roll()

    def run(self) -> None:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.handle_click(event.pos)
            self.update_ai()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
