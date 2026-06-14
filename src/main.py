import pygame
import sys
from levels import levels, LEVEL_ORDER
from colors import *
from ui import make_buttons
pygame.init()

# ---------------- НАСТРОЙКИ ----------------
WIN_W = 700
WIN_H = 700
CELL = 75
MARK_SIZE = 50

screen = pygame.display.set_mode((WIN_W, WIN_H))
pygame.display.set_caption("Witless")

font = pygame.font.Font(None, 45)
small_font = pygame.font.Font(None, 35)

LINE_WIDTH = 13
clock = pygame.time.Clock()

# ---------------- СЕТКА ----------------

def get_grid_offset(size):
    return (WIN_W - size * CELL) // 2, 140

# ---------------- ЛОКАЦИИ ----------------
scene = "menu"   # menu / level1 / level2 / end

# ---------------- ИГРОВАЯ ЛОГИКА ----------------
starts = {}
ends = {}
cross_cells = {}
dots = {}
active_start = None
paths = {}
finished_paths = {}
active_color = None 
drawing = False
win = False

invalid_line = False
finished = set()

first_move = False
level_name = "Level 1"
end_timer = 0
current_level = "level1"



menu_btn2, restart_btn, next_btn = make_buttons(WIN_W)
menu_btn = pygame.Rect(WIN_W // 2 - 120, WIN_H // 2 - 40, 240, 80)
exit_btn = pygame.Rect(WIN_W // 2 - 120, WIN_H // 2 + 60, 240, 80)


# ---------------- ФУНКЦИИ ----------------
def draw_button(rect, text):
    pygame.draw.rect(screen, COLORS["button"], rect)
    pygame.draw.rect(screen, COLORS["grid_line"], rect, 2)

    txt = small_font.render(text, True, COLORS["text"])
    screen.blit(
        txt,
        (
            rect.centerx - txt.get_width() // 2,
            rect.centery - txt.get_height() // 2
        )
    )

def load_level(name):
    global grid_x, grid_y, start_cell, end_cell
    global cross_cells, paths, starts, ends, dots, drawing, win, active_color

    size, matrix = levels[name]

    grid_x, grid_y = get_grid_offset(size)

    win = False
    drawing = False
    active_color = None

    reset_level_state()
    global invalid_line
    invalid_line = False
    clear_press()

    # имя уровня
    global level_name

    num = int(name.replace("level", ""))
    level_name = f"Уровень {num}"

    # разбираем поле
    for r in range(size):
        for c in range(size):
            cell = matrix[r][c]

            t = cell[0]
            color = cell[1]

            # старт
            if t == 1:
                if color == 1:
                    starts.setdefault(COL_WHITE, []).append((r, c))
                elif color == 2:
                    starts.setdefault(COL_RED, []).append((r, c))
                elif color == 3:
                    starts.setdefault(COL_GREEN, []).append((r, c))
                elif color == 4:
                    starts.setdefault(COL_BLUE, []).append((r, c))

            # конец
            elif t == 2:
                if color == 1:
                    ends.setdefault(COL_WHITE, []).append((r, c))
                elif color == 2:
                    ends.setdefault(COL_RED, []).append((r, c))
                elif color == 3:
                    ends.setdefault(COL_GREEN, []).append((r, c))
                elif color == 4:
                    ends.setdefault(COL_BLUE, []).append((r, c))

            # крестик
            elif t == 3:
                if color == 1:
                    cross_cells[(r, c)] = COL_WHITE
                elif color == 2:
                    cross_cells[(r, c)] = COL_RED
                elif color == 3:
                    cross_cells[(r, c)] = COL_GREEN
                elif color == 4:
                    cross_cells[(r, c)] = COL_BLUE
            
            # точка
            elif t == 4:
                if color == 1:
                    dots.setdefault(COL_WHITE, []).append((r, c))
                elif color == 2:
                    dots.setdefault(COL_RED, []).append((r, c))
                elif color == 3:
                    dots.setdefault(COL_GREEN, []).append((r, c))
                elif color == 4:
                    dots.setdefault(COL_BLUE, []).append((r, c))

    # создаём пустые пути и сбор точек
    paths = {}
    

    all_colors = set(starts.keys()) | set(dots.keys())

    for col in all_colors:
        paths[col] = []
        
def get_mouse_cell(pos):
    mx, my = pos

    if mx < grid_x or my < grid_y:
        return None

    size, _ = levels.get(scene, (8, []))

    c = (mx - grid_x) // CELL
    r = (my - grid_y) // CELL

    if 0 <= r < size and 0 <= c < size:
        return (r, c)

    return None

def near(a, b):
    if not isinstance(a, tuple) or not isinstance(b, tuple):
        return False
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1

def is_cross(color, cell):
    if cell not in cross_cells:
        return False

    cross_color = cross_cells[cell]

    # белый крестик блокирует всех
    if cross_color == COL_WHITE:
        return True

    # цветной блокирует только свой цвет
    return cross_color == color

def draw_menu():
    screen.fill(COLORS["bg"])

    txt = font.render("Witless", True, COLORS["text"])
    screen.blit(txt, (WIN_W // 2 - txt.get_width() // 2, 220))

    draw_button(menu_btn, "Начать игру")
    draw_button(exit_btn, "Выход")

def draw_cell(r, c):
        rect = pygame.Rect(
            grid_x + c * CELL,
            grid_y + r * CELL,
            CELL,
            CELL
        )
    
        inner = rect.inflate(-6, -6)
    
        pygame.draw.rect(screen, COLORS["cell"], inner, border_radius=8)

def center(cell):
    r, c = cell
    return (
        grid_x + c * CELL + CELL // 2,
        grid_y + r * CELL + CELL // 2
    )

def draw_level():
    screen.fill(COLORS["bg"])

    size, matrix = levels[scene]

    title = font.render(level_name, True, COLORS["text"])
    screen.blit(title, (WIN_W // 2 - title.get_width() // 2, 20))

    msg = "Отлично!" if win else "Проведите линию"
    msg_color = (0, 220, 0) if win else COLORS["text"]

    msg_txt = small_font.render(msg, True, msg_color)
    screen.blit(
        msg_txt,
        (WIN_W // 2 - msg_txt.get_width() // 2, 70)
    )

    # ---------------- СЕТКА ----------------
    for r in range(size):
        for c in range(size):
            draw_cell(r, c)

    # ---------------- СТАРТЫ ----------------
    for color, start_list in starts.items():
        for start in start_list:
            sx, sy = center(start)

            rect = pygame.Rect(
                sx - MARK_SIZE // 2,
                sy - MARK_SIZE // 2,
                MARK_SIZE,
                MARK_SIZE
            )

            pygame.draw.rect(
                screen,
                COLORS_LINE.get(color, COLORS_LINE[COL_WHITE]),
                rect,
                border_radius=11
            )

    # ---------------- КОНЦЫ ----------------
    for color, end_list in ends.items():
        for end in end_list:
            ex, ey = center(end)

            rect = pygame.Rect(
                ex - MARK_SIZE // 2,
                ey - MARK_SIZE // 2,
                MARK_SIZE,
                MARK_SIZE
            )

            pygame.draw.rect(
                screen,
                COLORS_LINE.get(color, COLORS_LINE[COL_WHITE]),
                rect,
                5,
                border_radius=11
            )

    # ---------------- КРЕСТИКИ ----------------
    for (r, c), cross_color in cross_cells.items():
        rect = pygame.Rect(
            grid_x + c * CELL,
            grid_y + r * CELL,
            CELL,
            CELL
        )

        inner = rect.inflate(-55, -55)

        pygame.draw.rect(
            screen,
            COLORS["cell"],
            inner,
            border_radius=1
        )

        pygame.draw.line(
            screen,
            COLORS_LINE.get(cross_color, COLORS["white"]),
            (inner.left, inner.top),
            (inner.right, inner.bottom),
            7
        )

        pygame.draw.line(
            screen,
            COLORS_LINE.get(cross_color, COLORS["white"]),
            (inner.right, inner.top),
            (inner.left, inner.bottom),
            7
        )
        
    # ---------------- ТОЧКИ ----------------
    for color, cells in dots.items():
        for r, c in cells:
            cx = grid_x + c * CELL + CELL // 2
            cy = grid_y + r * CELL + CELL // 2

            pygame.draw.circle(
                screen,
                COLORS_LINE.get(color, COLORS["white"]),
                (cx, cy),
                10
            )

    # ---------------- ЛИНИИ ----------------
    half = LINE_WIDTH // 2

    for start_cell, path in paths.items():
        if len(path) < 2:
            continue

        line_color = COL_WHITE

        for color, start_list in starts.items():
            if start_cell in start_list:
                line_color = color
                break
        
        line_color = COLORS_LINE[line_color]

        for i in range(len(path) - 1):
            r1, c1 = path[i]
            r2, c2 = path[i + 1]

            x1 = grid_x + c1 * CELL + CELL // 2
            y1 = grid_y + r1 * CELL + CELL // 2
            x2 = grid_x + c2 * CELL + CELL // 2
            y2 = grid_y + r2 * CELL + CELL // 2

            if y1 == y2:
                if x1 < x2:
                    x2 += half
                    if i > 0:
                        x1 -= half
                else:
                    x2 -= half
                    if i > 0:
                        x1 += half

            if x1 == x2:
                if y1 < y2:
                    y2 += half
                    if i > 0:
                        y1 -= half
                else:
                    y2 -= half
                    if i > 0:
                        y1 += half

            pygame.draw.line(
                screen,
                line_color,
                (x1, y1),
                (x2, y2),
                LINE_WIDTH
            )

    # ---------------- КНОПКИ ----------------
    draw_button(menu_btn2, "Меню")
    draw_button(restart_btn, "Заново")

    current_num = int(scene.replace("level", ""))
    next_level = f"level{current_num + 1}"

    if next_level in levels:
        draw_button(next_btn, "Далее")
    else:
        draw_button(next_btn, "Выйти")
    
def draw_end():
    screen.fill(COLORS["bg"])

    txt = small_font.render(
        "Окно закроется через три секунды...",
        True,
        COLORS["text"]
    )

    screen.blit(
        txt,
        (WIN_W // 2 - txt.get_width() // 2, WIN_H // 2)
    )

def occupied_by_other(active_start, cell):

    for start_cell, path in paths.items():

        # свою линию игнорируем
        if start_cell == active_start:
            continue

        if cell in path:
            return True

    return False

pressed_kind = None   # None / "start" / "end"
pressed_cell = None
pressed_color = None

def clear_press():
    global pressed_kind, pressed_cell, pressed_color
    pressed_kind = None
    pressed_cell = None
    pressed_color = None

def acceptable_end_for(color, cell):
    if cell is None:
        return False

    white_end = ends.get(COL_WHITE)
    color_end = ends.get(color)

    # белая линия всегда только в белый конец
    if color == COL_WHITE:
        return cell == white_end

    # цветная линия может:
    # 1) закончить в своём конце
    # 2) ИЛИ в белом (НО только если выполнены условия в
    return cell == color_end or cell == white_end

def is_other_start(active, cell):
    for color, start in starts.items():
        if color != active and cell == start:
            return True
    return False

def validate_move(active_start, cell, path):
    """Проверка во время движения (MOUSEMOTION)"""

    # крестики
    line_color = active_color

    if is_cross(line_color, cell):
        return False

    # чужие старты
    if is_other_start(line_color, cell):
        return False

    # чужие пути
    if occupied_by_other(active_start, cell):
        return False

    # движение только по соседним клеткам
    if not near(path[-1], cell):
        return False

    return True

def validate_finish(start_cell, path):

    line_color = None

    # определяем цвет линии по старту
    for color, start_list in starts.items():
        if start_cell in start_list:
            line_color = color
            break

    if line_color is None:
        return False

    last = path[-1]

    color_end_list = ends.get(line_color, [])
    white_end_list = ends.get(COL_WHITE, [])

    # -------------------------------------------------
    # ПРОВЕРКА КОНЕЧНОЙ КЛЕТКИ
    # -------------------------------------------------

    # белая линия -> только белый конец
    if line_color == COL_WHITE:

        if last not in white_end_list:
            return False

    # цветная линия
    else:

        # либо свой конец
        # либо белый
        if last not in color_end_list and last not in white_end_list:
            return False

    # -------------------------------------------------
    # ПРОВЕРКА ПРОХОЖДЕНИЯ ЧЕРЕЗ ЧУЖИЕ ОБЪЕКТЫ
    # -------------------------------------------------

    for cell in path[:-1]:

        # ---------- ЧУЖИЕ СТАРТЫ ----------
        for color, start_list in starts.items():

            for s in start_list:

                # свой старт можно
                if s == start_cell:
                    continue

                # белые объекты универсальны
                if color == COL_WHITE:
                    continue

                # чужой старт
                if color != line_color and cell == s:
                    return False

        # ---------- ЧУЖИЕ КОНЦЫ ----------
        for color, end_list in ends.items():

            for e in end_list:

                # белые универсальны
                if color == COL_WHITE:
                    continue

                # свои концы можно
                if color == line_color:
                    continue

                # чужой конец
                if cell == e:
                    return False

        # ---------- ЧУЖИЕ ТОЧКИ ----------
        for color, dot_list in dots.items():

            for d in dot_list:

                # белые универсальны
                if color == COL_WHITE:
                    continue

                # свои точки можно
                if color == line_color:
                    continue

                # чужая точка
                if cell == d:
                    return False

    # -------------------------------------------------
    # СВОИ ТОЧКИ ОБЯЗАТЕЛЬНЫ
    # -------------------------------------------------

    if not all_color_dots_collected(line_color):
        return False

    # -------------------------------------------------

    if invalid_line:
        return False

    return True

def validate_level():

    # -------------------------------------------------
    # ВСЕ СТАРТЫ ДОЛЖНЫ БЫТЬ ЗАВЕРШЕНЫ
    # -------------------------------------------------

    for start_list in starts.values():

        for start_cell in start_list:

            if start_cell not in finished:
                return False

    # -------------------------------------------------
    # ВСЕ ЛИНИИ ДОЛЖНЫ СУЩЕСТВОВАТЬ
    # -------------------------------------------------

    for start_list in starts.values():

        for start_cell in start_list:

            if start_cell not in paths:
                return False

            if len(paths[start_cell]) < 2:
                return False

    # -------------------------------------------------
    # ВСЕ ЦВЕТНЫЕ ТОЧКИ СОБРАНЫ
    # -------------------------------------------------

    for color, dot_list in dots.items():

        if color == COL_WHITE:
            continue

        for dot in dot_list:

            collected = False

            for path in paths.values():

                if dot in path:
                    collected = True
                    break

            if not collected:
                return False

    # -------------------------------------------------
    # ВСЕ БЕЛЫЕ ТОЧКИ СОБРАНЫ
    # -------------------------------------------------

    for dot in dots.get(COL_WHITE, []):

        collected = False

        for path in paths.values():

            if dot in path:
                collected = True
                break

        if not collected:
            return False

    # -------------------------------------------------

    return True

def reset_level_state():
    global starts, ends, cross_cells, dots, paths
    global drawing, active_color, win, invalid_line, finished

    cross_cells = {}
    starts = {}
    ends = {}
    dots = {}
    paths = {}

    finished = set()

    drawing = False
    active_color = None
    win = False
    invalid_line = False

def reset_active_line():
    global drawing, active_start, active_color, invalid_line

    if active_start is not None:
        paths[active_start] = []

    drawing = False
    active_start = None
    active_color = None
    invalid_line = False
    clear_press()

def erase_line(start_cell):

    # удалить путь
    if start_cell in paths:
        paths[start_cell] = []

    # убрать из завершённых
    if start_cell in finished:
        finished.remove(start_cell)

    # убрать сохранённую копию
    if start_cell in finished_paths:
        del finished_paths[start_cell]

def point_covered(cell):
    for path in paths.values():
        if cell in path:
            return True
    return False

def all_dots_collected():
    for cells in dots.values():
        for cell in cells:
            if not point_covered(cell):
                return False
    return True

def all_color_dots_collected(color):
    if color not in dots:
        return True

    for dot in dots[color]:
        if not point_covered(dot):
            return False
    return True



# ---------------- ЦИКЛ ----------------
while True:
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # ---------- MENU ----------
        if scene == "menu":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                if menu_btn.collidepoint(event.pos):
                    scene = "level1"
                    current_level = "level1"
                    load_level("level1")

                elif exit_btn.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        # ---------- LEVELS ----------
        elif scene in LEVEL_ORDER:

            # ---------- MOUSE DOWN ----------
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                # -------- UI КНОПКИ --------
                if restart_btn.collidepoint(event.pos):
                    load_level(current_level)
                    continue

                if menu_btn2.collidepoint(event.pos):
                    scene = "menu"
                    continue

                if next_btn.collidepoint(event.pos):

                    if not win:
                        continue

                    idx = LEVEL_ORDER.index(current_level)
                    next_idx = idx + 1

                    if next_idx < len(LEVEL_ORDER):
                        next_level = LEVEL_ORDER[next_idx]
                        current_level = next_level
                        scene = next_level
                        load_level(next_level)
                    else:
                        scene = "menu"
                        reset_level_state()

                    continue

                # -------- КЛИК ПО СЕТКЕ --------
                cell = get_mouse_cell(event.pos)

                if cell is None:
                    continue

                # ищем старт
                clicked_start = None
                clicked_color = None

                for color, start_list in starts.items():

                    if cell in start_list:
                        clicked_start = cell
                        clicked_color = color
                        break

                if clicked_start is None:
                    continue

                # если уже рисуем другую линию —
                # сбрасываем активную
                if drawing and active_start != clicked_start:
                    reset_active_line()

                # если линия уже существует —
                # удаляем её для перерисовки
                erase_line(clicked_start)

                clear_press()

                pressed_kind = "start"
                pressed_cell = clicked_start
                pressed_color = clicked_color

            # ---------- MOUSE UP ----------
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:

                cell = get_mouse_cell(event.pos)

                # подтверждение старта линии
                if pressed_kind == "start":
                    if cell == pressed_cell:

                        active_start = pressed_cell
                        active_color = pressed_color
                        drawing = True
                        invalid_line = False

                        # ВАЖНО: берём именно клетку старта, а не список
                        paths[pressed_cell] = [pressed_cell]
                        active_start = pressed_cell

                    clear_press()
                    continue

                clear_press()

                # если не рисуем — ничего
                if not drawing or active_color is None:
                    continue

                path = paths.get(active_start, [])

                if not path:
                    reset_active_line()
                    continue

                # финальная проверка линии
                if not validate_finish(active_start, path):
                    reset_active_line()
                    continue

                # линия завершена
                finished_paths[active_start] = paths[active_start][:]
                finished.add(active_start)

                drawing = False
                active_color = None
                clear_press()

                # победа уровня
                if validate_level():
                    win = True

            # ---------- MOUSE MOVE ----------
            elif event.type == pygame.MOUSEMOTION and drawing and not win:

                if active_color is None:
                    continue

                cell = get_mouse_cell(event.pos)

                if cell is None:
                    continue

                path = paths.get(active_start, [])

                if not path:
                    continue

                # шаг назад
                if len(path) >= 2 and cell == path[-2]:
                    path.pop()
                    continue

                # повтор клетки нельзя
                if cell in path:
                    continue

                # единая проверка движения
                if not validate_move(active_start, cell, path):
                    continue

                # добавить клетку
                path.append(cell)

                # точки
                for color, cells in dots.items():
                    if cell in cells:

                        # белые всем можно
                        if color == COL_WHITE:
                            continue

                        # чужая цветная точка = ошибка линии
                        if color != active_color:
                            invalid_line = True

        # ---------- END ----------
        elif scene == "end":
            pass

    # ---------- DRAW ----------
    if scene == "end":
        if pygame.time.get_ticks() - end_timer >= 3000:
            pygame.quit()
            sys.exit()

    if scene == "menu":
        draw_menu()

    elif scene in LEVEL_ORDER:
        draw_level()

    elif scene == "end":
        draw_end()

    pygame.display.flip()
    clock.tick(60)