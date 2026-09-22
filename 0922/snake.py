#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""可直接遊玩的貪食蛇；從 play_nes.py 的「貪食蛇」選項啟動。"""
import random
import sys

import pygame

from play_nes import load_font


BACKGROUND = (18, 22, 35)
GRID = (42, 50, 70)
SNAKE = (105, 220, 130)
HEAD = (170, 255, 180)
FOOD = (245, 90, 105)
TEXT = (235, 240, 250)
HINT = (165, 205, 165)


def new_game(columns, rows):
    center = (columns // 2, rows // 2)
    snake = [(center[0], center[1]), (center[0] - 1, center[1]), (center[0] - 2, center[1])]
    return snake, (1, 0), (1, 0), None, 0, False


def new_food(snake, columns, rows):
    choices = [(x, y) for y in range(rows) for x in range(columns) if (x, y) not in snake]
    return random.choice(choices) if choices else None


def draw_center(screen, font, text, y, color=TEXT):
    surface = font.render(text, True, color)
    screen.blit(surface, surface.get_rect(centerx=screen.get_width() // 2, y=y))


def main():
    pygame.init()
    info = pygame.display.Info()
    screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
    pygame.display.set_caption("貪食蛇")
    clock = pygame.time.Clock()

    title_font = load_font(42)
    text_font = load_font(25)
    small_font = load_font(20)

    width, height = screen.get_size()
    cell = max(16, min(28, width // 36, (height - 180) // 24))
    columns = max(12, min(36, (width - 80) // cell))
    rows = max(10, min(22, (height - 190) // cell))
    board_w, board_h = columns * cell, rows * cell
    board_x = (width - board_w) // 2
    board_y = 115

    snake, direction, next_direction, food, score, paused = new_game(columns, rows)
    food = new_food(snake, columns, rows)
    game_over = False
    elapsed = 0
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    if game_over:
                        snake, direction, next_direction, food, score, paused = new_game(columns, rows)
                        food = new_food(snake, columns, rows)
                        game_over = False
                    else:
                        paused = not paused
                elif event.key == pygame.K_r:
                    snake, direction, next_direction, food, score, paused = new_game(columns, rows)
                    food = new_food(snake, columns, rows)
                    game_over = False
                elif event.key in (pygame.K_UP, pygame.K_w):
                    candidate = (0, -1)
                    if candidate != (-direction[0], -direction[1]):
                        next_direction = candidate
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    candidate = (0, 1)
                    if candidate != (-direction[0], -direction[1]):
                        next_direction = candidate
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    candidate = (-1, 0)
                    if candidate != (-direction[0], -direction[1]):
                        next_direction = candidate
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    candidate = (1, 0)
                    if candidate != (-direction[0], -direction[1]):
                        next_direction = candidate

        elapsed += clock.tick(60)
        step_ms = max(75, 150 - score * 3)
        if elapsed >= step_ms and not paused and not game_over:
            elapsed = 0
            direction = next_direction
            head_x, head_y = snake[0]
            new_head = (head_x + direction[0], head_y + direction[1])
            ate_food = new_head == food
            body = snake if ate_food else snake[:-1]
            if (
                new_head[0] < 0
                or new_head[0] >= columns
                or new_head[1] < 0
                or new_head[1] >= rows
                or new_head in body
            ):
                game_over = True
            else:
                snake.insert(0, new_head)
                if ate_food:
                    score += 1
                    food = new_food(snake, columns, rows)
                    if food is None:
                        game_over = True
                else:
                    snake.pop()

        screen.fill(BACKGROUND)
        draw_center(screen, title_font, "貪食蛇", 24)
        draw_center(screen, text_font, f"分數：{score}", 76, HINT)
        pygame.draw.rect(screen, GRID, (board_x - 3, board_y - 3, board_w + 6, board_h + 6), border_radius=5)
        pygame.draw.rect(screen, (25, 31, 47), (board_x, board_y, board_w, board_h))

        if food:
            food_rect = pygame.Rect(board_x + food[0] * cell + 3, board_y + food[1] * cell + 3, cell - 6, cell - 6)
            pygame.draw.rect(screen, FOOD, food_rect, border_radius=max(3, cell // 4))
        for number, (x, y) in enumerate(snake):
            rect = pygame.Rect(board_x + x * cell + 2, board_y + y * cell + 2, cell - 4, cell - 4)
            pygame.draw.rect(screen, HEAD if number == 0 else SNAKE, rect, border_radius=max(3, cell // 4))

        if game_over:
            draw_center(screen, title_font, "遊戲結束", height - 95, FOOD)
            draw_center(screen, small_font, "按 Enter、Space 或 R 重新開始", height - 48, TEXT)
        elif paused:
            draw_center(screen, title_font, "暫停", height - 95, (255, 220, 110))
            draw_center(screen, small_font, "按 Enter 或 Space 繼續", height - 48, TEXT)
        else:
            draw_center(screen, small_font, "方向鍵或 W/A/S/D 移動　Enter/Space 暫停　ESC 返回選單", height - 48, HINT)
        pygame.display.flip()

    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
