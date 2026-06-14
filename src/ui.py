import pygame


def make_buttons(WIN_W):
    btn_w = 150
    btn_h = 55
    gap = 15

    total = btn_w * 3 + gap * 2
    x = (WIN_W - total) // 2
    y = 560

    menu = pygame.Rect(x, y, btn_w, btn_h)
    restart = pygame.Rect(x + btn_w + gap, y, btn_w, btn_h)
    next_b = pygame.Rect(x + (btn_w + gap) * 2, y, btn_w, btn_h)

    return menu, restart, next_b
