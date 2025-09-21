# Ana.py - RAU Snake (Connected snake renderer + working levels)
import curses
import random
import locale
locale.setlocale(locale.LC_ALL, '')

# Characters
FOOD_CHAR = "$"

# -----------------------------
# Level walls (fixed maps)
# -----------------------------
def get_level_walls(level, gh, gw):
    walls = set()
    mid_y = gh // 2
    mid_x = gw // 2

    def hor(y, x1, x2):
        for x in range(x1, x2+1):
            walls.add((y, x))

    def ver(x, y1, y2):
        for y in range(y1, y2+1):
            walls.add((y, x))

    if level == 1:
        pass
    elif level == 2:
        hor(mid_y - 2, gw//6, gw//6 + gw//3)
        hor(mid_y + 2, gw - gw//6 - gw//3, gw - gw//6)
    elif level == 3:
        ver(gw//4, gh//6, gh - gh//6)
        ver(gw - gw//4, gh//6, gh - gh//6)
    elif level == 4:
        for x in range(mid_x-10, mid_x+11):
            walls.add((mid_y-3, x)); walls.add((mid_y+3, x))
        for y in range(mid_y-3, mid_y+4):
            walls.add((y, mid_x-10)); walls.add((y, mid_x+10))
    elif level == 5:
        for i in range(0, 5):
            y = 3 + i*4
            hor(y, 4 + i*6, 10 + i*6)
            hor(gh - 4 - i*4, gw - (4 + i*6) - 6, gw - (4 + i*6))
    elif level == 6:
        for by in range(gh//5, gh-gh//5, gh//5):
            for bx in range(gw//5, gw-gw//5, gw//5):
                for x in range(bx-2, bx+3):
                    walls.add((by-2, x)); walls.add((by+2, x))
                for y in range(by-2, by+3):
                    walls.add((y, bx-2)); walls.add((y, bx+2))
    elif level == 7:
        for i in range(4, gw-4, 6):
            for y in range(3, gh-3):
                if (y // 3) % 2 == 0:
                    walls.add((y, i))
    elif level == 8:
        for i in range(4, gh-4, 5):
            for x in range(3, gw-3):
                if not (gw//3 - 2 < x < gw//3 + 2) and not (2*gw//3 - 2 < x < 2*gw//3 + 2):
                    walls.add((i, x))
    elif level == 9:
        for x in range(6, gw-6):
            walls.add((mid_y-6, x)); walls.add((mid_y+6, x))
        for y in range(6, gh-6):
            walls.add((y, mid_x-12)); walls.add((y, mid_x+12))
    else:  # level 10+
        r = 2
        cx, cy = mid_x, mid_y
        while r < min(mid_x, mid_y) - 3:
            for x in range(cx-r, cx+r+1):
                walls.add((cy-r, x))
            for y in range(cy-r+1, cy+r+1):
                walls.add((y, cx+r))
            for x in range(cx+r-1, cx-r-1, -1):
                walls.add((cy+r, x))
            for y in range(cy+r-1, cy-r, -1):
                walls.add((y, cx-r))
            r += 4

    # remove border touching walls
    clean = set()
    for (y, x) in walls:
        if 1 <= y <= gh-2 and 1 <= x <= gw-2:
            clean.add((y, x))
    return clean

# -----------------------------
# Menu drawing
# -----------------------------
def draw_menu(stdscr, selected_row_idx, menu):
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    title = [
"██████╗  █████╗ ██╗   ██╗    ███████╗███╗   ██╗ █████╗ ██╗  ██╗███████╗",
"██╔══██╗██╔══██╗██║   ██║    ██╔════╝████╗  ██║██╔══██╗██║ ██╔╝██╔════╝",
"██████╔╝███████║██║   ██║    ███████╗██╔██╗ ██║███████║█████╔╝ █████╗  ",
"██╔══██╗██╔══██║██║   ██║    ╚════██║██║╚██╗██║██╔══██║██╔═██╗ ██╔══╝  ",
"██║  ██║██║  ██║╚██████╔╝    ███████║██║ ╚████║██║  ██║██║  ██╗███████╗",
"╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝     ╚══════╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝",
"                                                                       "
]

    snake_art = [
        "        /^\\/^\\",
        "      _|__|  O|",
        "\\/     /~     \\_/ \\",
        " \\____|__________/  \\",
        "        \\_______      \\",
        "                `\\     \\                 \\",
        "                  |     |                  \\",
        "                 /      /                    \\",
        "                /     /                       \\",
        "               /      /                         \\",
        "              /     /                            \\",
        "             (      (                             \\",
        "              \\      \\                             \\",
        "               \\______\\                             \\"
    ]

    for i, line in enumerate(title):
        x = w//2 - len(line)//2
        try:
            stdscr.addstr(i+1, x, line, curses.color_pair(4) | curses.A_BOLD)
        except:
            stdscr.addstr(i+1, x, line)

    for i, line in enumerate(snake_art):
        x = w//2 - len(line)//2
        try:
            stdscr.addstr(len(title) + 2 + i, x, line, curses.color_pair(2))
        except:
            stdscr.addstr(len(title) + 2 + i, x, line)

    start_y = len(title) + len(snake_art) + 4
    for idx, row in enumerate(menu):
        x = w//2 - len(row)//2
        y = start_y + idx
        if idx == selected_row_idx:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x, row)
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(y, x, row)

    # Developer name only (no age in main menu)
    dev_text = "Developer: Rana Ahmad Umar"
    stdscr.addstr(h-2, w//2 - len(dev_text)//2, dev_text, curses.color_pair(3))

    stdscr.refresh()

# -----------------------------
# Show text (Controls / About)
# -----------------------------
def show_text_screen(stdscr, title_lines, body_lines):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    for i, line in enumerate(title_lines):
        x = w//2 - len(line)//2
        stdscr.addstr(2 + i, x, line, curses.color_pair(4) | curses.A_BOLD)
    for i, line in enumerate(body_lines):
        x = w//2 - len(line)//2
        stdscr.addstr(6 + len(title_lines) + i, x, line, curses.color_pair(3))
    footer = "Press ESC to return"
    stdscr.addstr(h-2, w//2 - len(footer)//2, footer, curses.color_pair(3))
    stdscr.refresh()
    while True:
        k = stdscr.getch()
        if k == 27:
            break

# -----------------------------
# Snake rendering helpers
# -----------------------------
def get_head_symbol(head, neck):
    hy, hx = head; ny, nx = neck
    if hy == ny:
        return '▶' if hx > nx else '◀'
    else:
        return '▼' if hy > ny else '▲'

def get_tail_symbol(prev, tail):
    py, px = prev; ty, tx = tail
    dy = py - ty; dx = px - tx
    if (dy, dx) == (0, -1): return '╺'  # prev is left => tail points left
    if (dy, dx) == (0, 1):  return '╸'  # prev is right => tail points right
    if (dy, dx) == (-1, 0): return '╻'  # prev is up => tail points up
    if (dy, dx) == (1, 0):  return '╹'  # prev is down => tail points down
    return '•'

def get_body_symbol(prev, curr, nxt):
    py, px = prev; cy, cx = curr; ny, nx = nxt
    # vectors from curr to neighbors
    d1 = (py - cy, px - cx)
    d2 = (ny - cy, nx - cx)

    # straight if directions are opposite
    if d1[0] == -d2[0] and d1[1] == -d2[1]:
        # horizontal or vertical
        if d1[0] == 0:
            return '═'  # horizontal
        else:
            return '║'  # vertical

    s = frozenset([d1, d2])
    # corner mapping: neighbors are (right/down), (left/down), (right/up), (left/up)
    corner_map = {
        frozenset({(0,1),(1,0)}): '╔',   # right + down
        frozenset({(0,-1),(1,0)}): '╗',  # left + down
        frozenset({(0,1),(-1,0)}): '╚',  # right + up
        frozenset({(0,-1),(-1,0)}): '╝', # left + up
    }
    return corner_map.get(s, '■')

def render_snake(win, snake):
    length = len(snake)
    for i, (y, x) in enumerate(snake):
        try:
            if i == 0:
                ch = get_head_symbol(snake[0], snake[1])
            elif i == length - 1:
                ch = get_tail_symbol(snake[-2], snake[-1])
            else:
                ch = get_body_symbol(snake[i-1], snake[i], snake[i+1])
            win.addstr(y, x, ch, curses.color_pair(2))
        except Exception:
            try:
                win.addch(y, x, ord('?'))
            except Exception:
                pass

# -----------------------------
# Play game
# -----------------------------
def play_game(stdscr, speed_ms=120, level=1):
    curses.curs_set(0)
    sh, sw = stdscr.getmaxyx()

    stdscr.clear()
    stdscr.border()
    try:
        stdscr.addstr(0, 2, " RAU SNAKE ", curses.color_pair(4) | curses.A_BOLD)
    except:
        stdscr.addstr(0, 2, " RAU SNAKE ")

    gh = sh - 6
    gw = sw - 4
    if gh < 12 or gw < 28:
        stdscr.addstr(2, 4, "Window too small. Resize and try again.", curses.color_pair(3))
        stdscr.refresh()
        stdscr.getch()
        return

    win = curses.newwin(gh, gw, 2, 2)
    win.keypad(1)
    win.timeout(speed_ms)
    win.border()

    level_walls = get_level_walls(level, gh, gw)

    # initial snake: head near quarter width, length 4 facing right
    snk_x = max(5, gw // 4)
    snk_y = gh // 2
    snake = [[snk_y, snk_x + i] for i in range(0, -4, -1)]  # head at index 0, facing right
    direction = curses.KEY_RIGHT

    def place_food():
        while True:
            fy = random.randint(1, gh-2)
            fx = random.randint(1, gw-2)
            if (fy, fx) not in level_walls and [fy, fx] not in snake:
                return [fy, fx]

    food = place_food()
    score = 0
    high_score = 0

    while True:
        # HUD on stdscr
        stdscr.addstr(sh-3, 4, f"Level {level}", curses.color_pair(3))
        stdscr.addstr(sh-3, sw//2 - 10, f"Score {score}", curses.color_pair(3))
        stdscr.addstr(sh-3, sw - 28, f"Speed {round(1000/speed_ms,1)}", curses.color_pair(3))
        stdscr.refresh()

        # draw frame
        win.erase()
        win.border()

        # draw walls
        for (wy, wx) in level_walls:
            try:
                win.addstr(wy, wx, '#', curses.color_pair(6))
            except:
                win.addch(wy, wx, ord('#'))

        # draw food
        try:
            win.addstr(food[0], food[1], FOOD_CHAR, curses.color_pair(5))
        except:
            win.addch(food[0], food[1], ord(FOOD_CHAR))

        # draw snake (connected)
        render_snake(win, snake)

        win.refresh()

        next_key = win.getch()
        if next_key != -1:
            if next_key in [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT]:
                # avoid reverse
                if (direction == curses.KEY_UP and next_key != curses.KEY_DOWN) or \
                   (direction == curses.KEY_DOWN and next_key != curses.KEY_UP) or \
                   (direction == curses.KEY_LEFT and next_key != curses.KEY_RIGHT) or \
                   (direction == curses.KEY_RIGHT and next_key != curses.KEY_LEFT):
                    direction = next_key
            elif next_key == 27:
                break

        # compute new head
        head = [snake[0][0], snake[0][1]]
        if direction == curses.KEY_UP:
            head[0] -= 1
        elif direction == curses.KEY_DOWN:
            head[0] += 1
        elif direction == curses.KEY_LEFT:
            head[1] -= 1
        elif direction == curses.KEY_RIGHT:
            head[1] += 1

        # collisions with border
        if head[0] in [0, gh-1] or head[1] in [0, gw-1]:
            break
        # with walls
        if (head[0], head[1]) in level_walls:
            break
        # with self
        if head in snake:
            break

        # move
        snake.insert(0, head)
        if head == food:
            score += 10
            if score > high_score:
                high_score = score
            food = place_food()
            # speed up slightly
            speed_ms = max(30, int(speed_ms * 0.98))
            win.timeout(speed_ms)
        else:
            snake.pop()

    # Game over
    stdscr.clear()
    msg1 = "GAME OVER"
    msg2 = f"Level {level} - Score: {score}"
    msg3 = "Press ENTER to return to menu or ESC to quit"
    h, w = stdscr.getmaxyx()
    stdscr.addstr(h//2 - 2, w//2 - len(msg1)//2, msg1, curses.color_pair(4) | curses.A_BOLD)
    stdscr.addstr(h//2, w//2 - len(msg2)//2, msg2, curses.color_pair(3))
    stdscr.addstr(h//2 + 2, w//2 - len(msg3)//2, msg3, curses.color_pair(3))
    stdscr.refresh()
    while True:
        k = stdscr.getch()
        if k in [10, 13]:
            break
        if k == 27:
            curses.endwin()
            exit(0)

# -----------------------------
# Level select menu
# -----------------------------
def level_select(stdscr):
    curses.curs_set(0)
    h, w = stdscr.getmaxyx()
    level = 1
    while True:
        stdscr.clear()
        title = "Level Select - Choose 1..10"
        stdscr.addstr(1, w//2 - len(title)//2, title, curses.color_pair(4) | curses.A_BOLD)
        for i in range(1, 11):
            txt = f"Level {i}"
            x = w//2 - 22 + ((i-1) % 5) * 11
            y = 4 + ((i-1) // 5) * 4
            if i == level:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, x, txt)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(y, x, txt)

        footer = "LEFT/RIGHT to choose, ENTER to play, ESC to return"
        stdscr.addstr(h-2, w//2 - len(footer)//2, footer, curses.color_pair(3))
        stdscr.refresh()

        k = stdscr.getch()
        if k == curses.KEY_RIGHT and level < 10:
            level += 1
        elif k == curses.KEY_LEFT and level > 1:
            level -= 1
        elif k in [10, 13]:
            base_speed = max(40, 170 - (level-1)*10)
            play_game(stdscr, speed_ms=base_speed, level=level)
        elif k == 27:
            break

# -----------------------------
# Main
# -----------------------------
def main(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)   # selection
    curses.init_pair(2, curses.COLOR_GREEN, -1)  # snake
    curses.init_pair(3, curses.COLOR_CYAN, -1)   # text
    curses.init_pair(4, curses.COLOR_RED, -1)    # title
    curses.init_pair(5, curses.COLOR_YELLOW, -1) # food
    curses.init_pair(6, curses.COLOR_MAGENTA, -1)# walls

    menu = ["Arcade Mode", "Level Select", "Game Settings", "GUI Options", "Controls", "About Developer", "Quit"]
    current_row = 0

    while True:
        draw_menu(stdscr, current_row, menu)
        key = stdscr.getch()
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu)-1:
            current_row += 1
        elif key in [10, 13]:
            if current_row == 0:  # Arcade
                diffs = [("Easy", 200), ("Medium", 140), ("Hard", 80)]
                d_idx = 0
                while True:
                    draw_menu(stdscr, d_idx, [d[0] for d in diffs])
                    k2 = stdscr.getch()
                    if k2 == curses.KEY_UP and d_idx > 0:
                        d_idx -= 1
                    elif k2 == curses.KEY_DOWN and d_idx < len(diffs)-1:
                        d_idx += 1
                    elif k2 in [10,13]:
                        play_game(stdscr, speed_ms=diffs[d_idx][1], level=1)
                        break
                    elif k2 == 27:
                        break

            elif current_row == 1:  # Level Select
                level_select(stdscr)

            elif current_row == 2:
                title = ["Game Settings"]
                body = ["No settings yet. Future: sound, colors, and more.", "", "Press ESC to return"]
                show_text_screen(stdscr, title, body)

            elif current_row == 3:
                title = ["GUI Options"]
                body = ["No GUI options yet. Could add font/size toggles.", "", "Press ESC to return"]
                show_text_screen(stdscr, title, body)

            elif current_row == 4:
                title = ["Controls"]
                body = [
                    "Arrow keys -> Move the snake",
                    "ESC        -> Exit to menu / Quit",
                    "Enter      -> Select menu item / Continue",
                    "",
                    "Press ESC to return"
                ]
                show_text_screen(stdscr, title, body)

            elif current_row == 5:
                title = ["About the Game"]
                body = [
                    "RAU Snake is a modern remake of the classic Snake game.",
                    "Features:",
                    "- 10 Levels with unique challenges",
                    "- Arcade mode with difficulty select",
                    "- Smooth connected snake with head, corners, and tail",
                    "- Obstacles and increasing speed for higher levels",
                    "",
                    "About the Developer:",
                    "Name: Rana Ahmad Umar",
                    "Age: 20 years old",
                    "Passionate self-taught programmer building fun projects.",
                    "",
                    "Press ESC to return"
                ]
                show_text_screen(stdscr, title, body)

            elif current_row == 6:
                break

        elif key == 27:
            break

if __name__ == "__main__":
    curses.wrapper(main)