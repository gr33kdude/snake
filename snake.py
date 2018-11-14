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

T = 1

def clear_screen():
    print '\033[2J\033[H'

def add_border(rect):
    R = rect.split("\n")
    W = max(map(len, R))
    H_border = "+" + "-"*W + "+"
    s = H_border + "\n|" + rect.replace("\n", "|\n|") + "|\n" + H_border + "\n"
    return s

class Direction(IntEnum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

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
                    s.append("@")
                else:
                    s.append(" ")
            if row != self.H-1:
                s.append("\n")
        
        s = "".join(s)
        return s

    def update(self, inp):
        key_dir_map = {
            "h": Direction.LEFT,
            "j": Direction.DOWN,
            "k": Direction.UP,
            "l": Direction.RIGHT,
        }
        opposite = {
            Direction.LEFT:  Direction.RIGHT,
            Direction.DOWN:  Direction.UP,
            Direction.UP:    Direction.DOWN,
            Direction.RIGHT: Direction.LEFT,
        }

        new_dir = key_dir_map.get(inp, None)
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
            try_food = ( random.randint(0, self.H), random.randint(0, self.W) )

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

orig_fl = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
fcntl.fcntl(sys.stdin, fcntl.F_SETFL, orig_fl | os.O_NONBLOCK)

game = Game()

counter = 0
while not game.over:
    clear_screen()
    print counter
    print add_border(str(game))

    time.sleep(T)
    inp = None
    try:
	inp = sys.stdin.read(1)
    except IOError:
        pass
    print inp
    time.sleep(1)

    if inp:
        inp = inp.lower()
    else:
        dm = {
                Direction.LEFT:  "h",
                Direction.DOWN:  "j",
                Direction.UP:    "k",
                Direction.RIGHT: "l",
        }
        inp = dm[game.direction]

    game.update(inp)

    counter += 1

print "GAME OVER!!"
