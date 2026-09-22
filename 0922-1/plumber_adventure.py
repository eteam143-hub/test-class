#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""原創的水管工跳躍冒險，不使用任天堂的角色、圖像或 ROM。"""
import os
import sys

import pygame


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class MixedFont:
    """在常見 Linux 字型組合下同時顯示繁中與英數。"""

    def __init__(self, size):
        cjk_path = pygame.font.match_font("droidsansfallback")
        latin_path = pygame.font.match_font("dejavusans")
        self.cjk = pygame.font.Font(cjk_path or latin_path, size)
        self.latin = pygame.font.Font(latin_path, size)
        self.height = max(self.cjk.get_height(), self.latin.get_height())
        missing = self.cjk.render("\U0010ffff", True, "white")
        self.missing_size = missing.get_size()
        self.missing_bytes = pygame.image.tostring(missing, "RGBA")
        self.cache = {}

    def render(self, text, antialias, color):
        pieces = []
        for char in text:
            if char not in self.cache:
                image = self.cjk.render(char, True, "white")
                self.cache[char] = not (
                    image.get_size() == self.missing_size
                    and pygame.image.tostring(image, "RGBA") == self.missing_bytes
                )
            font = self.cjk if self.cache[char] else self.latin
            pieces.append(font.render(char, antialias, color))
        width = sum(piece.get_width() for piece in pieces)
        result = pygame.Surface((max(width, 1), self.height), pygame.SRCALPHA)
        x = 0
        for piece in pieces:
            result.blit(piece, (x, (self.height - piece.get_height()) // 2))
            x += piece.get_width()
        return result


def draw_text(screen, font, text, x, y, color):
    screen.blit(font.render(text, True, color), (x, y))


def reset_level(width, height):
    ground_y = height - 105
    platforms = [
        pygame.Rect(0, ground_y, width, 40),
        pygame.Rect(width * 18 // 100, ground_y - 105, 160, 22),
        pygame.Rect(width * 43 // 100, ground_y - 185, 145, 22),
        pygame.Rect(width * 66 // 100, ground_y - 115, 160, 22),
        pygame.Rect(width * 82 // 100, ground_y - 205, 115, 22),
    ]
    coins = [
        pygame.Rect(width * 23 // 100, ground_y - 140, 18, 18),
        pygame.Rect(width * 49 // 100, ground_y - 220, 18, 18),
        pygame.Rect(width * 71 // 100, ground_y - 150, 18, 18),
        pygame.Rect(width * 86 // 100, ground_y - 240, 18, 18),
    ]
    return platforms, coins, pygame.Rect(45, ground_y - 48, 36, 48), ground_y


def main():
    pygame.init()
    info = pygame.display.Info()
    screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
    pygame.display.set_caption("水管工跳躍冒險")
    clock = pygame.time.Clock()
    title_font, ui_font, hint_font = MixedFont(42), MixedFont(26), MixedFont(20)
    width, height = screen.get_size()
    platforms, coins, player, ground_y = reset_level(width, height)
    player_x, player_y = float(player.x), float(player.y)
    velocity_y = 0.0
    score, lives, won, game_over = 0, 3, False, False
    running = True

    while running:
        delta = min(clock.tick(60) / 1000, 0.05)
        jump = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                elif event.key in (pygame.K_SPACE, pygame.K_x, pygame.K_UP, pygame.K_w):
                    jump = True
                elif event.key in (pygame.K_RETURN, pygame.K_r) and (won or game_over):
                    platforms, coins, player, ground_y = reset_level(width, height)
                    player_x, player_y, velocity_y = float(player.x), float(player.y), 0.0
                    score, lives, won, game_over = 0, 3, False, False

        keys = pygame.key.get_pressed()
        if not won and not game_over:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                player_x -= 280 * delta
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                player_x += 280 * delta
            player_x = max(0, min(width - player.width, player_x))

            was_bottom = player_y + player.height
            velocity_y += 1100 * delta
            player_y += velocity_y * delta
            player.x, player.y = round(player_x), round(player_y)
            grounded = False
            for platform in platforms:
                if (
                    velocity_y >= 0
                    and player.right > platform.left
                    and player.left < platform.right
                    and was_bottom <= platform.top + 8
                    and player.bottom >= platform.top
                ):
                    player.bottom = platform.top
                    player_y = float(player.y)
                    velocity_y = 0
                    grounded = True
                    break
            if jump and grounded:
                velocity_y = -500

            for coin in coins[:]:
                if player.colliderect(coin):
                    coins.remove(coin)
                    score += 1
            if player.left > width - 100 and player.bottom >= ground_y:
                won = True
            if player.top > height:
                lives -= 1
                if lives <= 0:
                    game_over = True
                else:
                    player.x, player.y = 45, ground_y - 48
                    player_x, player_y, velocity_y = float(player.x), float(player.y), 0.0

        screen.fill((93, 181, 237))
        pygame.draw.circle(screen, (255, 238, 125), (width - 90, 85), 38)
        for platform in platforms:
            pygame.draw.rect(screen, (87, 150, 63), platform)
            pygame.draw.rect(screen, (50, 100, 44), platform, 3)
        for coin in coins:
            pygame.draw.circle(screen, (255, 214, 58), coin.center, 10)
            pygame.draw.circle(screen, (255, 244, 155), coin.center, 6)
        goal = pygame.Rect(width - 80, ground_y - 95, 8, 95)
        pygame.draw.rect(screen, (230, 230, 235), goal)
        pygame.draw.polygon(screen, (218, 65, 65), [(goal.right, goal.top), (goal.right + 42, goal.top + 15), (goal.right, goal.top + 30)])
        pygame.draw.rect(screen, (205, 72, 55), player, border_radius=8)
        pygame.draw.rect(screen, (38, 68, 156), (player.x + 5, player.y + 23, 26, 21), border_radius=4)
        pygame.draw.circle(screen, (255, 220, 174), (player.x + 18, player.y + 16), 12)

        draw_text(screen, title_font, "水管工跳躍冒險", 28, 24, (255, 255, 255))
        draw_text(screen, ui_font, f"金幣：{score}/4　生命：{lives}", 30, 78, (28, 61, 95))
        if won:
            draw_text(screen, title_font, "過關！", width // 2 - 70, height // 2 - 35, (255, 245, 120))
            draw_text(screen, hint_font, "按 Enter 或 R 再玩一次", width // 2 - 120, height // 2 + 25, (255, 255, 255))
        elif game_over:
            draw_text(screen, title_font, "遊戲結束", width // 2 - 95, height // 2 - 35, (235, 70, 65))
            draw_text(screen, hint_font, "按 Enter 或 R 重新開始", width // 2 - 120, height // 2 + 25, (255, 255, 255))
        else:
            draw_text(screen, hint_font, "←→ 或 A/D 移動　Space/X/↑ 跳躍　ESC 離開", 28, height - 42, (255, 255, 255))
        pygame.display.flip()

    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
