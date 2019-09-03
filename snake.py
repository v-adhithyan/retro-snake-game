import configparser
import curses
import functools
import os
import random

import time

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
DIRECTION = 'right'


# Todo: Command pattern is suitable here, let's use that after game just works
# Todo: snake direction alignment
# Todo: increase length of snake as per score

class Game:
    config_file = os.path.expanduser('~/.snake.ini')

    def __init__(self):
        self.config = configparser.ConfigParser()

    def get_best_score(self):
        if not os.path.exists(self.config_file):
            return 'NA'

        self.config.read(self.config_file)
        return self.config['DEFAULT']['BEST_SCORE']

    def set_best_score(self, current_score):
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
            current_best_score = self.config['DEFAULT']['BEST_SCORE']
            if int(current_best_score) > int(current_score):
                current_score = current_best_score

        self.config['DEFAULT']['BEST_SCORE'] = str(current_score)

        with open(self.config_file, 'w') as game_config:
            self.config.write(game_config)


def quit_game(screen):
    curses.nocbreak()
    screen.keypad(False)
    curses.echo()
    curses.endwin()


def detect_screen_edge(func):

    @functools.wraps(func)
    def detector(*args, **kwargs):
        screen = args[0]
        cursor_x = kwargs.get('cursor_x')
        cursor_y = kwargs.get('cursor_y')
        height, width = screen.getmaxyx()

        if cursor_y == 0:
            cursor_y = height - 2
        if cursor_y == height - 1:
            cursor_y = 1
        if cursor_x == 0:
            cursor_x = width - 2
        if cursor_x == width - 1:
            cursor_x = 1

        kwargs['cursor_x'] = cursor_x
        kwargs['cursor_y'] = cursor_y

        return func(*args, **kwargs)

    return detector


def prepare_food(screen, x, y, refresh=True):
    screen.addstr(y, x, '@', curses.color_pair(2))
    if refresh:
        screen.refresh()


@detect_screen_edge
def up(screen, **kwargs):
    cursor_y = kwargs.pop('cursor_y') - 1
    if kwargs.get('key_press'):
        cursor_y = cursor_y + 1
    cursor_x = kwargs.pop('cursor_x')
    return add_snake(screen, cursor_y=cursor_y, cursor_x=cursor_x, direction='up')


@detect_screen_edge
def down(screen, **kwargs):
    cursor_y = kwargs.pop('cursor_y') + 1
    if kwargs.get('key_press'):
        cursor_y = cursor_y - 1
    cursor_x = kwargs.pop('cursor_x')
    return add_snake(screen, cursor_y=cursor_y, cursor_x=cursor_x, direction='down')


@detect_screen_edge
def left(screen, **kwargs):
    cursor_y = kwargs.pop('cursor_y')
    cursor_x = kwargs.pop('cursor_x') - 1
    if kwargs.get('key_press'):
        cursor_x = cursor_x + 1
    return add_snake(screen, cursor_y=cursor_y, cursor_x=cursor_x, direction='left')


@detect_screen_edge
def right(screen, **kwargs):
    cursor_y = kwargs.pop('cursor_y')
    cursor_x = kwargs.pop('cursor_x') + 1
    if kwargs.get('key_press'):
        cursor_x = cursor_x - 1
    return add_snake(screen, cursor_y=cursor_y, cursor_x=cursor_x, direction='right')


def do_nothing(screen, **kwargs):
    return kwargs.pop('cursor_x'), kwargs.pop('cursor_y'), kwargs.pop('direction')


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
            Game().set_best_score(SCORE)
            SNAKE = '.' * (SCORE + 1)
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
    if direction in {'left', 'right'} or len(SNAKE) == 1:
        screen.addstr(cursor_y, cursor_x, SNAKE, curses.color_pair(1))
    else:
        pos = -len(SNAKE)
        for i in range(len(SNAKE)):
            screen.addstr(cursor_y+pos, cursor_x, SNAKE[0], curses.color_pair(1))
            pos += 1
    screen.move(cursor_y, cursor_x)
    return cursor_x, cursor_y, direction


def render_status_bar(screen, height, width, game, **kwargs):
    global SCORE
    cx = kwargs.get('x', False)
    cy = kwargs.get('y', False)
    statusbarstr = "RETRO SNAKE GAME. Press q to quit. SCORE: {}, BEST SCORE: {}, x: {}, y:{}".format(SCORE, game.get_best_score(), cx, cy)
    screen.attron(curses.color_pair(3))
    screen.addstr(height - 1, 0, statusbarstr)
    screen.addstr(height - 1, len(statusbarstr), " " *
                  (width - len(statusbarstr) - 1))
    screen.attroff(curses.color_pair(3))


# for debug purposes
def render_status_bar_1(screen, message, width, height):
    screen.attron(curses.color_pair(3))
    screen.addstr(height - 1, 0, message)
    screen.addstr(height - 1, len(message), " " *
                  (width - len(message) - 1))
    screen.attroff(curses.color_pair(3))


def automove(screen, direction, cursor_x, cursor_y):
    if direction == 'right':
        return right(screen, cursor_x=cursor_x, cursor_y=cursor_y, direction=direction)
    if direction == 'left':
        return left(screen, cursor_x=cursor_x, cursor_y=cursor_y, direction=direction)
    if direction == 'up':
        return up(screen, cursor_x=cursor_x, cursor_y=cursor_y, direction=direction)
    if direction == 'down':
        return down(screen, cursor_x=cursor_x, cursor_y=cursor_y, direction=direction)


def main(win):
    global SNAKE_X, SNAKE_Y, SCORE
    direction = 'right'
    move_snake = dict()
    move_snake[KEY_UP] = up
    move_snake[KEY_DOWN] = down
    move_snake[KEY_LEFT] = left
    move_snake[KEY_RIGHT] = right

    game = Game()
    screen = curses.initscr()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
    height, width = screen.getmaxyx()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    screen.keypad(True)
    win = curses.newwin(height // 2, width // 2, height // 2, width // 2)
    win.nodelay(True)
    cursor_x = width // 2
    cursor_y = height // 2
    SNAKE_X = random.randint(0, width)
    SNAKE_Y = random.randint(0, height - 1)
    prepare_food(screen, x=SNAKE_X, y=SNAKE_Y, refresh=False)
    cursor_x, cursor_y, direction = add_snake(
        screen, cursor_x=cursor_x + 1, cursor_y=cursor_y, direction='right')
    screen.refresh()
    while True:
        try:
            key = win.getch()
            if key == ord('q'):
                quit_game(screen)
                break
            elif key == -1:
                screen.erase()
                time.sleep(0.5)
                render_status_bar(screen, height, width, game, x=cursor_x, y=cursor_y)
                prepare_food(screen, SNAKE_X, SNAKE_Y, refresh=False)
                cursor_x, cursor_y, direction = automove(
                    screen, direction, cursor_x, cursor_y)
            else:
                screen.erase()
                render_status_bar(screen, height, width, game, x=cursor_x, y=cursor_y)
                prepare_food(screen, SNAKE_X, SNAKE_Y, refresh=False)
                cursor_x, cursor_y, direction = move_snake.get(key, do_nothing)(screen, cursor_x=cursor_x,
                                                                                cursor_y=cursor_y, direction=direction, key_press=True)
            screen.refresh()
        except Exception as e:
            print(e.__repr__())


curses.wrapper(main)
