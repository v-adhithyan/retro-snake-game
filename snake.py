import curses
from collections import defaultdict

begin_x = 20
begin_y = 7

# screen_height = curses.LINES
# screen_width = curses.COLS
height = 500
width = 500
KEY_Q = 113
KEY_UP = 65
KEY_DOWN = 66
KEY_RIGHT = 67
KEY_LEFT = 68
SNAKE = '-\n'


# Command pattern is suitable here, let's use that after game just works
def quit_game(screen):
    curses.nocbreak()
    screen.keypad(False)
    curses.echo()
    curses.endwin()


def prepare_food(screen, refresh=True, **kwargs):
    if not kwargs:
        screen.addstr("O", curses.A_BLINK)
    else:
        pass
    if refresh:
        screen.refresh()


def up(screen):
    #screen.clear()
    screen.addstr(SNAKE)


def down(screen):
    #screen.clear()
    screen.addstr(SNAKE)


def left(screen):
    #screen.clear()
    screen.addstr(SNAKE)


def right(screen):
    #screen.clear()
    screen.addstr(SNAKE)


def do_nothing(screen):
    pass


def main(win):
    move_snake = dict()
    move_snake[KEY_UP] = up
    move_snake[KEY_DOWN] = down
    move_snake[KEY_LEFT] = left
    move_snake[KEY_RIGHT] = right

    screen = curses.initscr()
    curses.noecho()
    curses.cbreak()
    screen.keypad(True)
    win = curses.newwin(height, width, begin_y, begin_x)
    screen.addstr("RETRO SNAKE GAME\n")
    screen.addstr("Press Q to quit. Press arrow keys to play.\n\n")
    prepare_food(screen, refresh=False)
    screen.refresh()
    while True:
        try:
            key = win.getch()
            if key == KEY_Q:
                quit_game(screen)
                break
            else:
                move_snake.get(key, do_nothing)(screen)
            screen.refresh()
        except Exception as e:
            print(e.__repr__())


# win = curses.newwin(height, width, begin_y, begin_x)
curses.wrapper(main)
