'''
Tests for my CISC108 final project.

Change log:
  - 0.0.2: Fixed typo with assert_equal
  - 0.0.1: Initial version
'''

__VERSION__ = '0.0.2'

from cisc108 import assert_equal
from cisc108_game import assert_type

################################################################################
# Game import
# Rename this to the name of your project file.
from project_starter import *
world = INITIAL_WORLD

################################################################################

# Testing handle_key function
handle_key(INITIAL_WORLD, 97)
assert_equal(INITIAL_WORLD["key pressed?"]["a"], True)
handle_key(INITIAL_WORLD, 100)
assert_equal(INITIAL_WORLD["key pressed?"]["d"], True)
handle_key(INITIAL_WORLD, 32)
assert_equal(INITIAL_WORLD["key pressed?"][" "], True)

# Testing handle_release function
handle_release(INITIAL_WORLD, 97)
assert_equal(INITIAL_WORLD["key pressed?"]["a"], False)
handle_release(INITIAL_WORLD, 100)
assert_equal(INITIAL_WORLD["key pressed?"]["d"], False)
handle_release(INITIAL_WORLD, 32)
assert_equal(INITIAL_WORLD["key pressed?"][" "], False)

# Testing basic movement
world["current"]["y-pos"] = 40
world["current"]["x-speed"] = X_SPEED
world["current"]["x-pos"] += world["current"]["x-speed"]
assert_equal(world["current"]["x-pos"], 650.0)
world["current"]["x-speed"] = -X_SPEED
world["current"]["x-pos"] += world["current"]["x-speed"]
world["current"]["x-pos"] += world["current"]["x-speed"]
assert_equal(world["current"]["x-pos"], 630.0)
