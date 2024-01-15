"""
This is a 2D Platformer With Editor. The player controls a square that moves left and right and can jump.

Required features complete (or at least sufficiently presentable):
  - The player moves an avatar through a world using the keyboard.
  - Their avatar has gravity and falls until it hits an obstacle.
  - The avatar can move left and right.
  - The avatar can jump up.
  
Required features missing or incomplete:
  - The avatar must collect items and avoid obstacles.
  - The avatar wins when they reach the designated end of the level.
  - The player can create new obstacles by clicking with the mouse.
  
================================================================================
CHANGE LOG

BLOB 0.2.0
  - player can now make the square jump
(12.04.19)

BLOB 0.1.1
  - functionality for the "A" and "D" keys improved
(12.04.19)
  
BLOB 0.1.0
  - game named "BLOB"
  - player can now move a square in the left or right direction
(11.22.19)

Project Starter 0.0.2
  - added support for handle_release
(unknown date)

Project Starter 0.0.1
  - initial version
(unknown date)

================================================================================
"""

__VERSION__ = "0.2.0"

import arcade, math, random
from cisc108_game import Cisc108Game

################################################################################
## Game Constants

GAME_TITLE = "BLOB"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
BACKGROUND_COLOR = arcade.color.BLACK
CHARACTER_SIZE = 40
X_SPEED = 10.0
Y_SPEED = 20.0
JUMP_FRAMES = 30.0
FALL_FRAMES = 25.0
FLOATINESS = 1.0

################################################################################
## Record definitions

World = {
    # Character position and speed
    "current": {"x-pos": float, "y-pos": float, "x-speed": float, "y-speed": float},
    # Character state
    "state": {"on floor?": bool, "jumping?": bool},
    # Timers
    "jump tick": float,
    "fall tick": float,
    # Keyboard key states
    "key pressed?": {"a": bool, "d": bool, " ": bool},
}

INITIAL_WORLD = {
    "current": {
        "x-pos": WINDOW_WIDTH / 2,
        "y-pos": 600.0,
        "x-speed": 0.0,
        "y-speed": 0.0,
    },
    "state": {"on floor?": False, "jumping?": False},
    "jump tick": 0.0,
    "fall tick": 0.0,
    "key pressed?": {"a": False, "d": False, " ": False},
}

################################################################################
# Drawing functions


def draw_world(world: World):
    """
    Draws a square representing the player character.
    
    Args:
        world (World): The current world to draw
    """
    # Draws the player character
    arcade.draw_rectangle_filled(
        world["current"]["x-pos"],
        world["current"]["y-pos"],
        CHARACTER_SIZE,
        CHARACTER_SIZE,
        arcade.color.WHITE,
    )


################################################################################
# World manipulating functions


def update_world(world: World):
    """
    Updates the world based on certain conditions.
    
    Args:
        world (World): The current world to update.
    """
    # Checks for collision of the character with the game window boundaries
    check_window_collision(world)
    # Moves the character if the "A" or "D" keys are pressed
    update_x_speed(world)
    # Makes the character jump, controls falling acceleration
    update_y_speed(world)
    
    
def check_window_collision(world: World):
    """
    Checks for collision with the game window boundaries.
    
    Args:
        world (World): The current world to update.
    """
    ## Determines whether or not the player is crossing the left window boundary
    if world["current"]["x-pos"] <= CHARACTER_SIZE / 2:
        # Halt the player
        world["current"]["x-pos"] = CHARACTER_SIZE / 2
    ## Determines whether or not the player is crossing the right window boundary
    if world["current"]["x-pos"] >= WINDOW_WIDTH - CHARACTER_SIZE / 2:
        # Halt the player
        world["current"]["x-pos"] = WINDOW_WIDTH - CHARACTER_SIZE / 2

    ## Determines whether or not the player is crossing the upward window boundary
    if world["current"]["y-pos"] >= WINDOW_HEIGHT - CHARACTER_SIZE / 2:
        # Halt the player
        world["current"]["y-pos"] = WINDOW_HEIGHT - CHARACTER_SIZE / 2
        # Reset y-speed
        world["current"]["y-speed"] = 0.0
        # Player is now in free-fall until they hit the ground
        world["state"]["jumping?"] = False
        # Reset "jump tick"
        world["jump tick"] = 0.0
    ## Determines whether or not the player is crossing the downward window boundary
    if world["current"]["y-pos"] <= CHARACTER_SIZE / 2:
        # Halt the player
        world["current"]["y-pos"] = CHARACTER_SIZE / 2
        # Reset  y-speed
        world["current"]["y-speed"] = 0.0
        # Reset "jump tick"
        world["jump tick"] = 0.0
        # Reset "fall tick"
        world["fall tick"] = 5.0
        # Player is on floor
        world["state"]["on floor?"] = True
    else:
        # Otherwise the player is falling
        world["state"]["on floor?"] = False


def update_x_speed(world: World):
    """
    Updates the world's "x-speed" based on certain conditions.
    
    Args:
        world (World): The current world to update.
    """
    # If the "D" key is "pressed", moves the character to the right
    if world["key pressed?"]["d"] == True and world["key pressed?"]["a"] == False:
        world["current"]["x-speed"] = X_SPEED
    # If the "A" key is "pressed", moves the character to the left
    if world["key pressed?"]["a"] == True and world["key pressed?"]["d"] == False:
        world["current"]["x-speed"] = -X_SPEED
    # If both the "D" and "A" keys are "pressed", sets the horizontal speed to 0
    if world["key pressed?"]["d"] == True and world["key pressed?"]["a"] == True:
        world["current"]["x-speed"] = 0.0
    # If neither the keys "D" nor "A" keys are "pressed", sets the horizontal speed to 0
    if world["key pressed?"]["d"] == False and world["key pressed?"]["a"] == False:
        world["current"]["x-speed"] = 0.0
    # Updates horizontal speed
    world["current"]["x-pos"] += world["current"]["x-speed"]


def update_y_speed(world: World):
    """
    Updates the world's "y-speed" based on certain conditions.
    
    Args:
        world (World): The current world to update.
    """
    # Determine if the player has just input a jump
    if (
        # Check if the "SPACE" key is pressed
        world["key pressed?"][" "] == True
        # Check if the player is not already jumping
        and world["state"]["jumping?"] == False
        # Check if the player is in free-fall
        and world["state"]["on floor?"] == True
    ):
        # If the conditions are met, the player WILL jump
        world["state"]["jumping?"] = True

    # Controls actions during a jump from the start up until the peak
    # JUMP_FRAMES is a constant float
    if world["state"]["jumping?"] == True and world["jump tick"] < JUMP_FRAMES:
        # The world's jump tick starts at 0 and ends at JUMP_FRAMES, or 30.0
        # The world's jump tick increments by FLOATINESS, or 1.0
        # The smaller FLOATINESS is, the longer it takes to reach the peak (opposite for when it's larger)
        world["jump tick"] += FLOATINESS
        # To make the y-speed change at a rate that makes the jump trajectory mimic the graph of sine, I use its derivative, cosine
        # The value is related to the size of the jump tick
        # The decimal was determined via trial and error
        # Makes the character jump
        world["current"]["y-speed"] = math.cos(world["jump tick"] * 0.104719) * Y_SPEED

    # Determines if the player has reached the peak of a jump and change state
    if world["jump tick"] >= JUMP_FRAMES and world["state"]["jumping?"] == True:
        # The player is no longer "jumping," rather they are "falling"
        world["state"]["jumping?"] = False
        # World's jump tick is reset for use next jump
        world["jump tick"] = 0.0

    ## Determine if the player is "falling" and initiate free-fall actions
    if (
        # Checks to see if the player is touching a floor regardless of whether they just jumped
        world["state"]["on floor?"] == False
        # Makes sure the player isn't in a jump while off the floor
        and world["state"]["jumping?"] == False
        # Makes sure the player is still in early "falling frames"
        # Fall tick replaces jump tick in this situation
        and world["fall tick"] < FALL_FRAMES
    ):
        # Changes y-speed to make the player accelerate downward
        # Like jumping, but the speed is less than 0
        world["fall tick"] += FLOATINESS
        world["current"]["y-speed"] = (
            math.cos(world["fall tick"] * 0.104719) * Y_SPEED - Y_SPEED
        )
    if (
        # Determines whether the player is falling and has already accelerated downward a bit
        world["state"]["on floor?"] == False
        and world["state"]["jumping?"] == False
        and world["fall tick"] >= FALL_FRAMES
    ):
        # Caps the y-speed after a certain number of frames
        world["current"]["y-speed"] = (
            math.cos(JUMP_FRAMES * 0.104719) * Y_SPEED - Y_SPEED
        )
    if world["current"]["y-speed"] < 0:
        # The player is never "jumping" if the player's y-speed is less than 0
        world["state"]["jumping?"] = False
    # Updates vertical speed
    world["current"]["y-pos"] += world["current"]["y-speed"]


def handle_key(world: World, key: int):
    """
    Sets a keyboard key's "pressed" state of the current world to True if it is pressed.
    
    Args:
        world (World): Current state of the world.
        key (int): The ASCII value of the pressed keyboard key (use ord and chr).
    """
    # If the "A" key is pressed, set it to "pressed"
    if key == ord("a"):
        world["key pressed?"]["a"] = True
    # If the "D" key is pressed, set it to "pressed"
    if key == ord("d"):
        world["key pressed?"]["d"] = True
    # If the "SPACE" key is pressed, set it to "pressed"
    if key == ord(" "):
        world["key pressed?"][" "] = True


def handle_mouse(world: World, x: int, y: int, button: str):
    """
    Updates the game based on mouse clicks.
    
    Args:
        world (World): Current state of the world.
        x (int): The x-coordinate of the mouse when the button was clicked.
        y (int): The y-coordinate of the mouse when the button was clicked.
        button (str): The button that was clicked ("left", "right", "middle")
    """
    # This function serves no purpose in my game.


def handle_motion(world: World, x: int, y: int):
    """
    Updates the game based on mouse movement.
    
    Args:
        world (World): Current state of the world.
        x (int): The x-coordinate of where the mouse was moved to.
        y (int): The x-coordinate of where the mouse was moved to.
    """
    # This function serves no purpose in my game.


def handle_release(world: World, key: int):
    """
    Sets a keyboard key's "pressed" state of the current world to False if it is left unpressed.
    
    Args:
        world (World): Current state of the world.
        key (int): The ASCII value of the released keyboard key (use ord and chr).
    """
    # If the "A" key is unpressed, set it to "unpressed"
    if key == ord("a"):
        world["key pressed?"]["a"] = False
    # If the "D" key is unpressed, set it to "unpressed"
    if key == ord("d"):
        world["key pressed?"]["d"] = False
    # If the "SPACE" key is unpressed, set it to "unpressed"
    if key == ord(" "):
        world["key pressed?"][" "] = False


############################################################################
# Set up the game
# Don't need to change any of this

if __name__ == "__main__":
    Cisc108Game(
        World,
        WINDOW_WIDTH,
        WINDOW_HEIGHT,
        GAME_TITLE,
        INITIAL_WORLD,
        draw_world,
        update_world,
        handle_key,
        handle_mouse,
        handle_motion,
        handle_release,
    )
    arcade.set_background_color(BACKGROUND_COLOR)
    arcade.run()
