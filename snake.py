#!/usr/bin/env python

import termios
import sys
import select
import random
import fcntl
import tty
import os
from collections import deque
import time
from enum import IntEnum

T = 0.15

def clear_screen():
    print '\033[2J\033[H'

class Direction(IntEnum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

key_dir_map = {
    "h": Direction.LEFT,
    "j": Direction.DOWN,
    "k": Direction.UP,
    "l": Direction.RIGHT,
    "a": Direction.LEFT,
    "s": Direction.DOWN,
    "w": Direction.UP,
    "d": Direction.RIGHT,
}

class Game():
    def __init__(self):
        self.W = 20
        self.H = 20

        self.snake = deque()
        # row, col format
        self.snake.append( (self.H/2, self.W/2) )

        self.direction = Direction.RIGHT

        self.food = []
        self.food.append(self.next_food())

        self.over = False

    def __str__(self):
        s = []
        for row in range(self.H):
            for col in range(self.W):
                pos = (row, col)
                if pos in self.food:
                    s.append("*")
                elif pos in self.snake:
                    if pos == self.snake[-1]:
                        s.append("\033[1m@\033[0m")
                    else:
                        s.append("@")
                else:
                    s.append(" ")
            if row != self.H-1:
                s.append("\n")
        
        s = "".join(s)
        return s

    def bordered_str(self):
        s = str(self)
        H_border = "+" + "-"*self.W + "+"
        s = H_border + "\n|" + s.replace("\n", "|\n|") + "|\n" + H_border + "\n"
        return s

    def update(self, new_dir):
        opposite = {
            Direction.LEFT:  Direction.RIGHT,
            Direction.DOWN:  Direction.UP,
            Direction.UP:    Direction.DOWN,
            Direction.RIGHT: Direction.LEFT,
        }

        if new_dir and new_dir != opposite[self.direction]:
            self.direction = new_dir

        dir_rc_map = {
            Direction.LEFT:  (0, -1),
            Direction.DOWN:  (1, 0),
            Direction.UP:    (-1, 0),
            Direction.RIGHT: (0, 1),
        }

        head = self.snake.pop()
        adj = dir_rc_map[self.direction]
        new_head = (head[0] + adj[0], head[1] + adj[1])
        if not (0 <= new_head[0] < self.H and 0 <= new_head[1] < self.W) or \
            new_head in self.snake:
            self.over = True
        # need to reattach the head
        self.snake.append(head)
        self.snake.append(new_head)

        if new_head in self.food:
            self.food.remove(new_head)
            self.food.append(self.next_food())
        else:
            # remove snake's tail
            self.snake.popleft()

    def next_food(self):
        try_food = self.snake[-1]
        while (try_food in self.food or try_food in self.snake):
            try_food = ( random.randint(0, self.H-1), random.randint(0, self.W-1) )

        sys.stderr.write(str(try_food) + "\n")
        return try_food

def get_me_out():
    raise KeyboardInterrupt()

def raw_input_timed(timeout = 10):
    rlist, _, _ = select.select([sys.stdin], [], [], timeout)
    if rlist:
        s = sys.stdin.read()
        return s
    else:
        return None

'''
orig_fl = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
fcntl.fcntl(sys.stdin, fcntl.F_SETFL, orig_fl | os.O_NONBLOCK)
'''

old_settings = None

def save_tty_settings():
    global old_settings
    old_settings = termios.tcgetattr(sys.stdin)

def prepare_tty():
    global old_settings
    settings = old_settings[:]
    settings[3] = settings[3] & ~(termios.ECHO | termios.ICANON)
    termios.tcsetattr(sys.stdin, termios.TCSANOW, settings)

def restore_tty_settings():
    global old_settings
    termios.tcsetattr(sys.stdin, termios.TCSANOW, old_settings)

def main():
    game = Game()

    counter = 0
    while not game.over:
        clear_screen()
        print counter
        print game.bordered_str()

        termios.tcflush(sys.stdin, termios.TCIFLUSH)
        time.sleep(T)
        inp = None
        try:
            inp = sys.stdin.read(1)
        except IOError:
            pass
        termios.tcflush(sys.stdin, termios.TCIFLUSH)

        new_dir = game.direction
        if inp:
            inp = inp.lower()
            new_dir = key_dir_map[inp]

        game.update(new_dir)

        counter += 1

    print "GAME OVER!!"

try:
    save_tty_settings()
    prepare_tty()
    main()
finally:
    restore_tty_settings()
