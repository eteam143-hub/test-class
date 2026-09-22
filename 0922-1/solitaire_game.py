"""經典 Klondike 接龍桌面遊戲。"""

from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path

import pygame


WIDTH, HEIGHT = 1180, 780
FPS = 60
CARD_W, CARD_H = 92, 128
TOP_Y = 72
TABLEAU_Y = 244
COLUMN_X = [42 + index * 160 for index in range(7)]
GREEN = (21, 104, 66)
DARK_GREEN = (13, 70, 44)
FELT_LINE = (86, 172, 126)
PANEL = (246, 247, 239)
INK = (29, 39, 34)
RED = (194, 47, 51)
GOLD = (246, 202, 74)
BLUE = (68, 129, 202)

CJK_FONT_PATHS = (
    "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJKtc-Regular.otf",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
)
CARD_FONT_PATHS = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf",
)

SUITS = (("♠", "黑桃", False), ("♥", "紅心", True), ("♣", "梅花", False), ("♦", "方塊", True))
RANKS = ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K")


@dataclass
class Card:
    suit: str
    suit_name: str
    rank: int
    is_red: bool
    face_up: bool = False

    @property
    def label(self) -> str:
        return f"{RANKS[self.rank - 1]}{self.suit}"


@dataclass
class Selection:
    source: str
    column: int | None
    index: int


class Solitaire:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("經典接龍")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = self.get_font(22)
        self.small_font = self.get_font(16)
        self.title_font = self.get_font(34)
        # 牌面數字採用確定含有拉丁字元的字型，與中文介面字型分開處理。
        self.rank_font = self.get_card_font(27)
        self.rank_small_font = self.get_card_font(18)
        self.new_button = pygame.Rect(975, 23, 155, 42)
        self.new_game()

    @staticmethod
    def get_font(size: int) -> pygame.font.Font:
        for font_path in CJK_FONT_PATHS:
            if Path(font_path).is_file():
                return pygame.font.Font(font_path, size)
        return pygame.font.Font(None, size)

    @staticmethod
    def get_card_font(size: int) -> pygame.font.Font:
        for font_path in CARD_FONT_PATHS:
            if Path(font_path).is_file():
                return pygame.font.Font(font_path, size)
        return pygame.font.Font(None, size)

    def new_game(self) -> None:
        deck = [Card(suit, name, rank, red) for suit, name, red in SUITS for rank in range(1, 14)]
        random.shuffle(deck)
        self.tableau: list[list[Card]] = [[] for _ in range(7)]
        for column in range(7):
            for row in range(column + 1):
                card = deck.pop()
                card.face_up = row == column
                self.tableau[column].append(card)
        self.stock = deck
        self.waste: list[Card] = []
        self.foundations: list[list[Card]] = [[] for _ in range(4)]
        self.selection: Selection | None = None
        self.dragging = False
        self.drag_position: tuple[int, int] | None = None
        self.drag_offset = (0, 0)
        self.message = "按住牌並拖曳到目的地；也可點選來源後再點選目的地。"
        self.won = False

    @staticmethod
    def card_rect(x: int, y: int) -> pygame.Rect:
        return pygame.Rect(x, y, CARD_W, CARD_H)

    def tableau_card_y(self, column: int, index: int) -> int:
        pile = self.tableau[column]
        y = TABLEAU_Y
        for card_index, card in enumerate(pile[:index]):
            y += 25 if not card.face_up else 31
        return y

    def foundation_index(self, card: Card) -> int:
        return next(index for index, (suit, _, _) in enumerate(SUITS) if suit == card.suit)

    def movable_sequence(self, pile: list[Card], index: int) -> bool:
        sequence = pile[index:]
        if not sequence or not sequence[0].face_up:
            return False
        return all(
            current.face_up
            and current.is_red != following.is_red
            and current.rank == following.rank + 1
            for current, following in zip(sequence, sequence[1:])
        )

    def can_place_tableau(self, card: Card, column: int) -> bool:
        pile = self.tableau[column]
        if not pile:
            return card.rank == 13
        target = pile[-1]
        return target.face_up and target.is_red != card.is_red and target.rank == card.rank + 1

    def can_place_foundation(self, card: Card) -> bool:
        pile = self.foundations[self.foundation_index(card)]
        return (not pile and card.rank == 1) or (bool(pile) and pile[-1].rank == card.rank - 1)

    def source_cards(self, selection: Selection) -> list[Card]:
        if selection.source == "tableau":
            return self.tableau[selection.column or 0][selection.index:]
        if selection.source == "waste":
            return self.waste[-1:]
        return self.foundations[selection.column or 0][-1:]

    def remove_source(self, selection: Selection) -> list[Card]:
        if selection.source == "tableau":
            pile = self.tableau[selection.column or 0]
            moved = pile[selection.index:]
            del pile[selection.index:]
            if pile and not pile[-1].face_up:
                pile[-1].face_up = True
                self.message = "翻開了一張新牌！"
            return moved
        if selection.source == "waste":
            return [self.waste.pop()]
        return [self.foundations[selection.column or 0].pop()]

    def try_move_to_tableau(self, column: int) -> bool:
        if not self.selection:
            return False
        cards = self.source_cards(self.selection)
        if cards and self.can_place_tableau(cards[0], column):
            self.tableau[column].extend(self.remove_source(self.selection))
            self.selection = None
            self.message = "移動成功。"
            return True
        return False

    def try_move_to_foundation(self, foundation: int) -> bool:
        if not self.selection:
            return False
        cards = self.source_cards(self.selection)
        card = cards[0] if len(cards) == 1 else None
        if card and self.foundation_index(card) == foundation and self.can_place_foundation(card):
            self.foundations[foundation].extend(self.remove_source(self.selection))
            self.selection = None
            self.message = "已放入基礎牌堆。"
            self.won = sum(map(len, self.foundations)) == 52
            return True
        return False

    def select(self, source: str, column: int | None, index: int) -> None:
        candidate = Selection(source, column, index)
        if source == "tableau" and not self.movable_sequence(self.tableau[column or 0], index):
            self.selection = None
            self.message = "只能移動正面朝上的、紅黑交錯遞減的牌。"
            return
        self.selection = candidate
        self.message = "已選取；請點選要放入的牌堆。"

    def stock_click(self) -> None:
        self.selection = None
        if self.stock:
            card = self.stock.pop()
            card.face_up = True
            self.waste.append(card)
            self.message = "抽了一張牌。"
        elif self.waste:
            self.stock = list(reversed(self.waste))
            for card in self.stock:
                card.face_up = False
            self.waste.clear()
            self.message = "已回收廢牌堆。"
        else:
            self.message = "沒有可抽的牌。"

    def select_tableau_card(self, position: tuple[int, int]) -> bool:
        for column, pile in enumerate(self.tableau):
            x = COLUMN_X[column]
            for index in range(len(pile) - 1, -1, -1):
                y = self.tableau_card_y(column, index)
                next_y = self.tableau_card_y(column, index + 1) if index + 1 < len(pile) else y + CARD_H
                if pygame.Rect(x, y, CARD_W, next_y - y).collidepoint(position):
                    self.select("tableau", column, index)
                    return True
        return False

    def selected_card_position(self) -> tuple[int, int]:
        """回傳被拖曳牌組第一張牌的原始座標。"""
        assert self.selection is not None
        if self.selection.source == "tableau":
            column = self.selection.column or 0
            return COLUMN_X[column], self.tableau_card_y(column, self.selection.index)
        if self.selection.source == "waste":
            return 162, TOP_Y
        return 542 + (self.selection.column or 0) * 120, TOP_Y

    def start_drag(self, position: tuple[int, int]) -> None:
        """記錄游標相對牌面的位置，供畫面即時顯示拖曳中的牌。"""
        if not self.selection:
            return
        card_x, card_y = self.selected_card_position()
        self.dragging = True
        self.drag_position = position
        self.drag_offset = (position[0] - card_x, position[1] - card_y)

    def drop_card(self, position: tuple[int, int]) -> bool:
        """將目前選取的牌放到滑鼠放開處的合法牌堆。"""
        if not self.selection:
            return False
        for index in range(4):
            if self.card_rect(542 + index * 120, TOP_Y).collidepoint(position):
                if self.try_move_to_foundation(index):
                    return True
                self.message = "此牌不能放入這個基礎牌堆。"
                return False
        for column, pile in enumerate(self.tableau):
            target_y = TABLEAU_Y if not pile else self.tableau_card_y(column, len(pile) - 1)
            if self.card_rect(COLUMN_X[column], target_y).collidepoint(position):
                if self.try_move_to_tableau(column):
                    return True
                self.message = "遊戲區牌堆必須紅黑交錯、數字遞減。"
                return False
        return False

    def begin_drag(self, position: tuple[int, int]) -> None:
        if self.new_button.collidepoint(position):
            self.new_game()
            return
        if self.won:
            return
        if self.card_rect(42, TOP_Y).collidepoint(position):
            self.stock_click()
            return
        # 已選取牌時，直接點選目的地同樣可以完成移動。
        if self.selection and self.drop_card(position):
            return
        if self.card_rect(162, TOP_Y).collidepoint(position) and self.waste:
            self.select("waste", None, len(self.waste) - 1)
            self.start_drag(position)
            return
        for index in range(4):
            if self.card_rect(542 + index * 120, TOP_Y).collidepoint(position):
                if self.foundations[index]:
                    self.select("foundation", index, len(self.foundations[index]) - 1)
                    self.start_drag(position)
                return
        if self.select_tableau_card(position):
            self.start_drag(position)
        elif self.selection:
            self.selection = None
            self.message = "已取消選取。"

    def auto_move_to_foundation(self, position: tuple[int, int]) -> None:
        """雙擊牌面時，嘗試將單張頂牌自動送入對應的基礎牌堆。"""
        if self.won:
            return
        self.dragging = False
        self.drag_position = None
        self.selection = None

        if self.card_rect(162, TOP_Y).collidepoint(position) and self.waste:
            self.select("waste", None, len(self.waste) - 1)
        elif self.select_tableau_card(position):
            pass
        else:
            self.message = "請雙擊廢牌或遊戲區最上方的正面牌。"
            return

        if not self.selection:
            return
        cards = self.source_cards(self.selection)
        if len(cards) != 1:
            self.selection = None
            self.message = "只能自動歸位遊戲區最上方的一張牌。"
            return
        foundation = self.foundation_index(cards[0])
        if self.try_move_to_foundation(foundation):
            self.message = "已自動歸位到右上方的基礎牌堆。"
        else:
            self.selection = None
            self.message = "尚不符合基礎牌堆的歸位順序。"

    def draw_suit(self, suit: str, center: tuple[int, int], color: tuple[int, int, int], size: int) -> None:
        """以圖形繪製花色，不依賴字型是否提供撲克牌符號。"""
        cx, cy = center
        if suit == "♦":
            pygame.draw.polygon(self.screen, color, [(cx, cy - size), (cx + size, cy), (cx, cy + size), (cx - size, cy)])
        elif suit == "♥":
            radius = max(2, size // 2)
            pygame.draw.circle(self.screen, color, (cx - radius, cy - radius // 2), radius)
            pygame.draw.circle(self.screen, color, (cx + radius, cy - radius // 2), radius)
            pygame.draw.polygon(self.screen, color, [(cx - size, cy), (cx + size, cy), (cx, cy + size)])
        elif suit == "♣":
            radius = max(2, size // 2)
            pygame.draw.circle(self.screen, color, (cx, cy - radius), radius)
            pygame.draw.circle(self.screen, color, (cx - radius, cy + radius // 3), radius)
            pygame.draw.circle(self.screen, color, (cx + radius, cy + radius // 3), radius)
            pygame.draw.rect(self.screen, color, (cx - max(2, size // 6), cy + radius, max(3, size // 3), size))
            pygame.draw.polygon(self.screen, color, [(cx - size // 2, cy + size * 2), (cx + size // 2, cy + size * 2), (cx, cy + size)])
        else:  # 黑桃
            radius = max(2, size // 2)
            pygame.draw.circle(self.screen, color, (cx - radius, cy + radius // 3), radius)
            pygame.draw.circle(self.screen, color, (cx + radius, cy + radius // 3), radius)
            pygame.draw.polygon(self.screen, color, [(cx - size, cy + radius), (cx + size, cy + radius), (cx, cy - size)])
            pygame.draw.rect(self.screen, color, (cx - max(2, size // 6), cy + radius, max(3, size // 3), size))
            pygame.draw.polygon(self.screen, color, [(cx - size // 2, cy + size * 2), (cx + size // 2, cy + size * 2), (cx, cy + size)])

    def draw_card(self, card: Card, x: int, y: int, selected: bool = False) -> None:
        rect = self.card_rect(x, y)
        if not card.face_up:
            pygame.draw.rect(self.screen, (36, 78, 152), rect, border_radius=7)
            pygame.draw.rect(self.screen, (208, 224, 255), rect.inflate(-10, -10), 2, border_radius=4)
            for offset in range(12, CARD_W, 16):
                pygame.draw.line(self.screen, (120, 166, 235), (x + offset, y + 12), (x + 4, y + CARD_H - 12), 2)
            return
        pygame.draw.rect(self.screen, PANEL, rect, border_radius=7)
        pygame.draw.rect(self.screen, GOLD if selected else (210, 218, 207), rect, 3 if selected else 1, border_radius=7)
        color = RED if card.is_red else INK
        rank = self.rank_font.render(RANKS[card.rank - 1], True, color)
        self.screen.blit(rank, (x + 8, y + 5))
        # 右下角再印一個數字／字母，讓牌面數值在牌堆中也容易辨識。
        bottom_rank = self.rank_small_font.render(RANKS[card.rank - 1], True, color)
        self.screen.blit(bottom_rank, (x + CARD_W - bottom_rank.get_width() - 8, y + CARD_H - 27))
        self.draw_suit(card.suit, (x + CARD_W // 2, y + CARD_H // 2 - 2), color, 17)
        self.draw_suit(card.suit, (x + 19, y + 42), color, 7)
        self.draw_suit(card.suit, (x + CARD_W - 19, y + CARD_H - 43), color, 7)
        corner = self.small_font.render(card.suit_name, True, color)
        self.screen.blit(corner, (x + 8, y + CARD_H - 24))

    def draw_slot(self, x: int, y: int, label: str) -> None:
        rect = self.card_rect(x, y)
        pygame.draw.rect(self.screen, FELT_LINE, rect, 2, border_radius=7)
        text = self.small_font.render(label, True, (188, 225, 199))
        self.screen.blit(text, text.get_rect(center=rect.center))

    def draw(self) -> None:
        self.screen.fill(GREEN)
        pygame.draw.rect(self.screen, DARK_GREEN, (0, 0, WIDTH, 54))
        title = self.title_font.render("經典接龍", True, (255, 255, 246))
        self.screen.blit(title, (42, 9))
        guide = self.small_font.render("操作：拖曳移牌；雙擊最上方牌可自動歸位", True, (219, 243, 224))
        self.screen.blit(guide, (190, 18))
        pygame.draw.rect(self.screen, (245, 247, 239), self.new_button, border_radius=8)
        new_text = self.font.render("重新開始", True, INK)
        self.screen.blit(new_text, new_text.get_rect(center=self.new_button.center))

        self.draw_slot(42, TOP_Y, "牌庫")
        if self.stock:
            back = Card("", "", 0, False, False)
            self.draw_card(back, 42, TOP_Y)
        self.draw_slot(162, TOP_Y, "廢牌")
        if self.waste:
            chosen = self.selection == Selection("waste", None, len(self.waste) - 1)
            if not (self.dragging and chosen):
                self.draw_card(self.waste[-1], 162, TOP_Y, chosen)
        for index, (suit, name, _) in enumerate(SUITS):
            x = 542 + index * 120
            self.draw_slot(x, TOP_Y, name)
            if self.foundations[index]:
                chosen = self.selection == Selection("foundation", index, len(self.foundations[index]) - 1)
                if not (self.dragging and chosen):
                    self.draw_card(self.foundations[index][-1], x, TOP_Y, chosen)

        for column, pile in enumerate(self.tableau):
            x = COLUMN_X[column]
            if not pile:
                self.draw_slot(x, TABLEAU_Y, "國王")
            for index, card in enumerate(pile):
                if (
                    self.dragging
                    and self.selection
                    and self.selection.source == "tableau"
                    and self.selection.column == column
                    and index >= self.selection.index
                ):
                    continue
                selected = bool(self.selection and self.selection.source == "tableau" and self.selection.column == column and index >= self.selection.index)
                self.draw_card(card, x, self.tableau_card_y(column, index), selected)

        # 拖曳時將整疊牌畫在游標下方，使用者能立即看見牌正在移動。
        if self.dragging and self.selection and self.drag_position:
            draw_x = self.drag_position[0] - self.drag_offset[0]
            draw_y = self.drag_position[1] - self.drag_offset[1]
            for index, card in enumerate(self.source_cards(self.selection)):
                self.draw_card(card, draw_x, draw_y + index * 31, True)

        status_rect = pygame.Rect(22, HEIGHT - 58, WIDTH - 44, 38)
        pygame.draw.rect(self.screen, (239, 247, 233), status_rect, border_radius=8)
        message = self.font.render(self.message, True, INK)
        self.screen.blit(message, (status_rect.x + 14, status_rect.y + 7))
        if self.won:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 130))
            self.screen.blit(overlay, (0, 0))
            win = self.title_font.render("恭喜完成接龍！", True, (255, 238, 112))
            self.screen.blit(win, win.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 12)))
            hint = self.font.render("按右上角「重新開始」再玩一局", True, (255, 255, 255))
            self.screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 32)))
        pygame.display.flip()

    def run(self) -> None:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.begin_drag(event.pos)
                elif event.type == pygame.MOUSEMOTION and self.dragging:
                    self.drag_position = event.pos
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if self.dragging and self.selection:
                        self.drop_card(event.pos)
                    self.dragging = False
                    self.drag_position = None
                elif event.type == pygame.MOUSEBUTTONDBLCLICK and event.button == 1:
                    self.auto_move_to_foundation(event.pos)
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()


if __name__ == "__main__":
    Solitaire().run()
