import curses
import functools
import random

begin_x = 20
begin_y = 7


KEY_Q = 113
KEY_UP = 65
KEY_DOWN = 66
KEY_RIGHT = 67
KEY_LEFT = 68
SNAKE = '.'
SNAKE_X, SNAKE_Y = 0, 0
SCORE = 0


# Todo: Command pattern is suitable here, let's use that after game just works
# Todo: add score board
# Todo: snake direction alignment
# Todo: screen edge detection
# Todo: auto move snake
# Todo: increase length of snake as per score
def quit_game(screen):
    curses.nocbreak()
    screen.keypad(False)
    curses.echo()
    curses.endwin()


def prepare_food(screen, x, y, refresh=True):
    screen.addstr(y, x, '0', curses.color_pair(2))
    if refresh:
        screen.refresh()


def up(screen, **kwargs):
    cursor_y = kwargs.pop('cursor_y') - 1
    cursor_x = kwargs.pop('cursor_x')
    return add_snake(screen, cursor_y=cursor_y, cursor_x=cursor_x, direction='up')


def down(screen, **kwargs):
    cursor_y = kwargs.pop('cursor_y') + 1
    cursor_x = kwargs.pop('cursor_x')
    return add_snake(screen, cursor_y=cursor_y, cursor_x=cursor_x, direction='down')


def left(screen, **kwargs):
    cursor_y = kwargs.pop('cursor_y')
    cursor_x = kwargs.pop('cursor_x') - 1
    return add_snake(screen, cursor_y=cursor_y, cursor_x=cursor_x, direction='left')


def right(screen, **kwargs):
    cursor_y = kwargs.pop('cursor_y')
    cursor_x = kwargs.pop('cursor_x') + 1
    return add_snake(screen, cursor_y=cursor_y, cursor_x=cursor_x, direction='right')


def do_nothing(screen, **kwargs):
    return kwargs.pop('cursor_x'), kwargs.pop('cursor_y')


def ate_food(f):
    @functools.wraps(f)
    def detector(*args, **kwargs):
        global SNAKE_Y, SNAKE_X, SNAKE, SCORE
        if kwargs.get('cursor_x') == SNAKE_X and kwargs.get('cursor_y') == SNAKE_Y:
            screen = args[0]
            height, width = screen.getmaxyx()
            SNAKE_X = random.randint(0, width)
            SNAKE_Y = random.randint(0, height)
            SCORE = SCORE + 1
            #SNAKE = '.' * (SCORE + 1)
            prepare_food(screen, SNAKE_X, SNAKE_Y)
        return f(*args, **kwargs)

    return detector


@ate_food
def add_snake(screen, **kwargs):
    curses.erasechar()
    screen.refresh()
    global SNAKE
    cursor_x = kwargs.pop('cursor_x')
    cursor_y = kwargs.pop('cursor_y')
    direction = kwargs.pop('direction')
    """if direction in {'left', 'right'} or len(SNAKE) == 1:
        screen.addstr(cursor_y, cursor_x, SNAKE, curses.color_pair(1))
    else:
        pos = (len(SNAKE)) if direction == 'down' else len(SNAKE)
        pos -= 1
        for i in range(len(SNAKE)):

            screen.addstr(cursor_y+pos, cursor_x, SNAKE[0], curses.color_pair(1))
            pos += 1
            #cursor_y = cursor_y - 2 if direction == 'down' else cursor_y - 1"""
    screen.addstr(cursor_y, cursor_x, SNAKE, curses.color_pair(1))
    screen.move(cursor_y, cursor_x)
    return cursor_x, cursor_y


def render_status_bar(screen, height, width):
    global SCORE
    statusbarstr = "RETRO SNAKE GAME. Press q to quit. SCORE: {}".format(SCORE)
    screen.attron(curses.color_pair(3))
    screen.addstr(height - 1, 0, statusbarstr)
    screen.addstr(height - 1, len(statusbarstr), " " * (width - len(statusbarstr) - 1))
    screen.attroff(curses.color_pair(3))


def main(win):
    global SNAKE_X, SNAKE_Y, SCORE
    move_snake = dict()
    move_snake[KEY_UP] = up
    move_snake[KEY_DOWN] = down
    move_snake[KEY_LEFT] = left
    move_snake[KEY_RIGHT] = right

    screen = curses.initscr()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
    height, width = screen.getmaxyx()
    curses.noecho()
    curses.cbreak()
    screen.keypad(True)
    win = curses.newwin(height//2, width//2, height//2, width//2)
    cursor_x = width // 2
    cursor_y = height // 2
    screen.addstr("RETRO SNAKE GAME\n")
    screen.addstr("Press Q to quit. Press arrow keys to play.\n\n")
    SNAKE_X = random.randint(0, width)
    SNAKE_Y = random.randint(0, height)
    prepare_food(screen, x=SNAKE_X, y=SNAKE_Y, refresh=False)
    cursor_x, cursor_y = add_snake(screen, cursor_x=cursor_x+1, cursor_y=cursor_y, direction='right')
    screen.refresh()
    while True:
        try:
            key = win.getch()
            if key == ord('q'):
                quit_game(screen)
                break
            else:
                screen.erase()
                render_status_bar(screen, height, width)
                prepare_food(screen, SNAKE_X, SNAKE_Y, refresh=False)
                cursor_x, cursor_y = move_snake.get(key, do_nothing)(screen, cursor_x=cursor_x, cursor_y=cursor_y)
            screen.refresh()
        except Exception as e:
            print(e.__repr__())


curses.wrapper(main)
