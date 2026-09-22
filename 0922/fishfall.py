#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""可直接遊玩的魚兒墜落；從 play_nes.py 的選單啟動。"""
import random
import sys

import pygame

from play_nes import load_font


SKY = (29, 91, 155)
SEA = (20, 65, 118)
WAVE = (93, 185, 235)
BOAT = (150, 86, 42)
FISH = (255, 196, 72)
TEXT = (245, 250, 255)
HINT = (205, 235, 255)
DANGER = (255, 100, 95)


def make_fish(width):
    return {"x": random.randint(25, width - 25), "y": -30, "speed": random.uniform(155, 290)}


def reset_game(width):
    return width // 2, [make_fish(width)], 0, 3, False


def draw_center(screen, font, text, y, color=TEXT):
    surface = font.render(text, True, color)
    screen.blit(surface, surface.get_rect(centerx=screen.get_width() // 2, y=y))


def draw_fish(screen, x, y):
    pygame.draw.ellipse(screen, FISH, (x - 16, y - 10, 32, 20))
    pygame.draw.polygon(screen, FISH, [(x - 14, y), (x - 29, y - 12), (x - 29, y + 12)])
    pygame.draw.circle(screen, (30, 45, 65), (x + 8, y - 3), 2)


def main():
    pygame.init()
    info = pygame.display.Info()
    screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
    pygame.display.set_caption("魚兒墜落")
    clock = pygame.time.Clock()

    title_font = load_font(42)
    text_font = load_font(25)
    small_font = load_font(20)
    width, height = screen.get_size()
    boat_y = height - 115
    boat_x, fishes, score, lives, paused = reset_game(width)
    game_over = False
    spawn_elapsed = 0
    running = True

    while running:
        delta = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    if game_over:
                        boat_x, fishes, score, lives, paused = reset_game(width)
                        game_over = False
                    else:
                        paused = not paused
                elif event.key == pygame.K_r:
                    boat_x, fishes, score, lives, paused = reset_game(width)
                    game_over = False

        keys = pygame.key.get_pressed()
        if not paused and not game_over:
            moving_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
            moving_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
            if moving_left:
                boat_x -= 410 * delta
            if moving_right:
                boat_x += 410 * delta
            boat_x = max(45, min(width - 45, boat_x))

            spawn_elapsed += delta
            spawn_delay = max(0.32, 1.05 - score * 0.025)
            if spawn_elapsed >= spawn_delay:
                fishes.append(make_fish(width))
                spawn_elapsed = 0

            for fish in fishes[:]:
                fish["y"] += fish["speed"] * delta
                caught = abs(fish["x"] - boat_x) < 54 and boat_y - 24 <= fish["y"] <= boat_y + 18
                if caught:
                    fishes.remove(fish)
                    score += 1
                elif fish["y"] > height + 25:
                    fishes.remove(fish)
                    lives -= 1
                    if lives <= 0:
                        game_over = True

        screen.fill(SKY)
        pygame.draw.rect(screen, SEA, (0, boat_y + 45, width, height - boat_y - 45))
        for x in range(0, width, 70):
            pygame.draw.arc(screen, WAVE, (x, boat_y + 42, 55, 20), 0, 3.14, 2)

        draw_center(screen, title_font, "魚兒墜落", 22)
        draw_center(screen, text_font, f"分數：{score}　生命：{'♥' * lives}", 76, HINT)
        for fish in fishes:
            draw_fish(screen, int(fish["x"]), int(fish["y"]))

        boat_rect = pygame.Rect(int(boat_x) - 48, boat_y, 96, 30)
        pygame.draw.polygon(screen, BOAT, [(boat_rect.left, boat_rect.top), (boat_rect.right, boat_rect.top), (boat_rect.right - 17, boat_rect.bottom), (boat_rect.left + 17, boat_rect.bottom)])
        pygame.draw.rect(screen, (242, 232, 185), (int(boat_x) - 3, boat_y - 36, 6, 36))
        pygame.draw.polygon(screen, (248, 245, 215), [(int(boat_x) + 3, boat_y - 34), (int(boat_x) + 3, boat_y - 4), (int(boat_x) + 32, boat_y - 4)])

        if game_over:
            draw_center(screen, title_font, "遊戲結束", height - 95, DANGER)
            draw_center(screen, small_font, "按 Enter、Space 或 R 重新開始", height - 48)
        elif paused:
            draw_center(screen, title_font, "暫停", height - 95, (255, 230, 115))
            draw_center(screen, small_font, "按 Enter 或 Space 繼續", height - 48)
        else:
            draw_center(screen, small_font, "方向鍵或 A/D 移動小船接魚　Enter/Space 暫停　ESC 返回選單", height - 48, HINT)
        pygame.display.flip()

    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
