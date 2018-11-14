#!/usr/bin/env python

import threading
import thread
import random
from collections import deque
import time
from enum import Enum

class Direction(IntEnum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

W = 20
H = 20

snake = deque()
direction = Direction.RIGHT
N = 1
# row, col format
snake.append( (H/2, W/2) )

food = []

def raw_input_timed(timeout = 10):
    timer = threading.Timer(timeout, thread.interrupt_main)
    astring = None
    try:
        timer.start()
        astring = raw_input()
    except KeyboardInterrupt:
        pass
    timer.cancel()
    return astring

def clear_screen():
    print '\033[2J\033[H'

def render_game():
    s = []
    for row in range(H):
        for col in range(W):
            pos = (row, col)
            if pos in food:
                s.append("*")
            elif pos in snake:
                s.append("@")
            else:
                s.append(" ")
        s.append("\n")
    
    s = "".join(s)
    return s

def next_food():
    try_food = snake[0]
    while (try_food in food or try_food in snake):
        try_food = ( random.randint(0, H), random.randint(0, W) )

    return try_food

def game_loop():
    clear_screen()
    render_game()

    #inp = raw_input_timed(1)
    inp = raw_input("").lower()

    dir_map = {
        "h": Direction.LEFT,
        "j": Direction.DOWN,
        "k": Direction.UP,
        "l": Direction.RIGHT,
    }

    if dir_map.get(inp, None):
       # 
        pass

    

    print inp

gg = False

counter = 0
while not gg:
    game_loop()
    print counter

    counter += 1
