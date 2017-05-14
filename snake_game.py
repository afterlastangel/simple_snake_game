#!/usr/bin/python
import os
import sys
import thread
import tty
import termios
import collections
import random
from time import sleep

breakNow = False
key_pressed = ''
control_keys = ['h', 'j', 'k', 'l', '+', '-']
direction_keys = ['h', 'j', 'k', 'l']


class GoodGameException(Exception):
    pass


class Snake(object):

    def __init__(self, x, y, direction):
        self.snake = collections.deque()
        self.snake.append((x, y))
        self.direction = direction

    def is_in_snake(self, x, y):
        return (x, y) in self.snake

    def change_direction(self, new_direction):
        possible_direction = {
            'h': ['j', 'k'],
            'l': ['j', 'k'],
            'j': ['h', 'l'],
            'k': ['h', 'l'],
        }
        if new_direction in possible_direction[self.direction]:
            self.direction = new_direction

    def move(self, foods):
        head = self.snake[-1]
        if self.direction == 'h':
            new_head = (head[0] - 1, head[1])
        elif self.direction == 'j':
            new_head = (head[0], head[1] + 1)
        elif self.direction == 'k':
            new_head = (head[0], head[1] - 1)
        elif self.direction == 'l':
            new_head = (head[0] + 1, head[1])
        if new_head not in foods:
            self.snake.popleft()
        if self.is_in_snake(new_head[0], new_head[1]):
            raise GoodGameException
        self.snake.append(new_head)
        return new_head


class SnakeBoard(object):

    def __init__(self, snake, board_size):
        self.snake = snake
        self.board_size = board_size
        self.foods = []
        self.move_count = 0

    def is_in_snake(self, x, y):
        return self.snake.is_in_snake(x, y)

    def change_direction(self, direction):
        self.snake.change_direction(direction)

    def tick(self):
        self.move_count = self.move_count + 1
        if self.move_count % 3 == 0 and len(self.foods) < 2:
            while True:
                new_food = (
                    random.randint(1, self.board_size - 2),
                    random.randint(1, self.board_size - 2)
                )
                if not self.is_in_snake(new_food[0], new_food[1]):
                    break
                # TODO: Break when full
            self.foods.append(new_food)

        new_head = self.snake.move(self.foods)
        if new_head in self.foods:
            self.foods.remove(new_head)
        if self.is_border(new_head[0], new_head[1]):
            raise GoodGameException

    def is_border(self, x, y):
        if (
                x == 0 or y == 0 or
                x == self.board_size - 1 or y == self.board_size - 1):
            return True

    def is_in_food(self, x, y):
        return (x, y) in self.foods

    def board(self, x, y):
        if x == 0 or x == self.board_size - 1:
            return '|'
        if y == 0 or y == self.board_size - 1:
            return '-'
        if self.is_in_snake(x, y):
            return 'x'
        if self.is_in_food(x, y):
            return 'o'
        return ' '

    def draw(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        for y in range(self.board_size):
            for x in range(self.board_size):
                sys.stdout.write(self.board(x, y))
            sys.stdout.write("\r\n")


def getch():

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def waitForKeyPress():
    global breakNow
    global key_pressed

    while True:
        ch = getch()
        if ch == "q":
            breakNow = True
            break
        if ch in control_keys:
            key_pressed = ch


thread.start_new_thread(waitForKeyPress, ())
os.system('cls' if os.name == 'nt' else 'clear')

BOARD_SIZE = 20
SPEED = 0.5
snake = Snake(BOARD_SIZE/2, BOARD_SIZE/2, 'l')
snake_board = SnakeBoard(snake, BOARD_SIZE)

count = 0
try:
    while breakNow is False:
        if key_pressed in control_keys:
            if key_pressed in direction_keys:
                snake_board.change_direction(key_pressed)
            if key_pressed == '+' and SPEED > 0.05:
                SPEED = SPEED - 0.05
            if key_pressed == '-' and SPEED < 1:
                SPEED = SPEED + 0.05
            key_pressed = ''
        snake_board.tick()
        snake_board.draw()
        sleep(SPEED)
    os.system('cls' if os.name == 'nt' else 'clear')
except GoodGameException:
    print "Good Game"


####
# Reference
# http://stackoverflow.com/a/2084628
# http://stackoverflow.com/a/39376068
