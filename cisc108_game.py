"""
This file contains a basic Arcade Window class. It is necessary
to run your game.

You do not need to open or read this file. It must
be in the same folder as your other files.

Change Log:
  - 0.0.6: Added try/except around all functions to handle stupid Pyglet bug.
  - 0.0.5: Added rule to type checker about primitive values in World.
  - 0.0.4: Added on_key_release
  - 0.0.3: Allow int in World checks for float type
  - 0.0.2: Added assert_type, World checks, mock game runner
  - 0.0.1: Initial version
"""

__version__ = '0.0.6'

import arcade

# Better tools for detecting issues in students' code
from cisc108.assertions import (get_line_code, QUIET,
                                MESSAGE_LINE_CODE, MESSAGE_GENERIC_SUCCESS)

GAME_SPEED = 1/60

def fix_attribute_error(e):
    return Exception("AttributeError: "+str(e.args[0])).with_traceback(e.__traceback__)

class Cisc108GameUntyped(arcade.Window):
    """
    An Arcade Window subclass that allows you to specify its
    functions and is built around a World data model.
    
    Args:
        window_width (int): The width of the game window.
        window_height (int): The height of the game window.
        window_caption (str): The title of the game window.
        an_initial_world (World): The initial state of the world.
        draw_world (World->None): A function that draws a world.
        update_world (World->None): A function that updates the world.
        handle_key (World,int->None): A function that handles keyboard input.
        handle_mouse (World,int,int,str->None): A function that handles mouse clicks.
        handle_motion (World,int,int->None): A function that handles mouse movement.
    
    Attributes:
        world (World): The current state of the world.
    """
    def __init__(self, window_width, window_height, window_caption,
                 an_initial_world, draw_world, update_world,
                 handle_key=None, handle_mouse=None, handle_motion=None,
                 handle_release=None):
        super().__init__(window_width, window_height, window_caption, update_rate=GAME_SPEED)
        self.world = an_initial_world
        self.draw_world = draw_world
        self.update_world = update_world
        self.handle_key = handle_key
        self.handle_release = handle_release
        self.handle_mouse = handle_mouse
        self.handle_motion = handle_motion
    
    def on_draw(self):
        """ Called when it is time to draw the world """
        try:
            arcade.start_render()
            self.draw_world(self.world)
        except AttributeError as e:
            raise fix_attribute_error(e)
    
    def on_update(self, delta_time: float):
        """ Called every frame """
        try:
            self.update_world(self.world)
        except AttributeError as e:
            raise fix_attribute_error(e)
    
    def on_key_press(self, key: int, modifiers: int):
        """ Called when the keyboard is pressed """
        if self.handle_key is not None:
            try:
                self.handle_key(self.world, key)
            except AttributeError as e:
                raise fix_attribute_error(e)
    
    def on_key_release(self, key: int, modifiers: int):
        """ Called when a keyboard is released """
        if self.handle_release is not None:
            try:
                self.handle_release(self.world, key)
            except AttributeError as e:
                raise fix_attribute_error(e)
    
    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        """ Called when the mouse is pressed """
        if self.handle_mouse is not None:
            button_str = ('left' if button == arcade.MOUSE_BUTTON_LEFT
                          else 'right' if button == arcade.MOUSE_BUTTON_RIGHT
                          else 'middle' if button == arcade.MOUSE_BUTTON_MIDDLE
                          else 'unknown')
            try:
                self.handle_mouse(self.world, x, y, button_str)
            except AttributeError as e:
                raise fix_attribute_error(e)
    
    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        """ Called when the mouse is moved """
        if self.handle_motion is not None:
            try:
                self.handle_motion(self.world, x, y)
            except AttributeError as e:
                raise fix_attribute_error(e)

BETTER_TYPE_NAMES = {
    str: 'string',
    int: 'integer',
    float: 'float',
    bool: 'boolean',
    dict: 'dictionary',
    list: 'list'
    }

def get_name(value):
    try:
        return BETTER_TYPE_NAMES.get(value, value.__name__)
    except Exception:
        return str(value)[8:-2]
    
def make_key_list(values):
    if not values:
        return "and there were no keys at all"
    elif len(values) == 1:
        return "but there was the key {!r}".format(values[0])
    else:
        return "but there were the keys "+ (", ".join(map(repr, values[:-1]))) + " and {!r}".format(values[-1])

WRONG_TYPE_MESSAGE = " was the wrong type. Expected type was {y_type!r}, but actual value was {x} ({x_type!r})."
WRONG_KEY_TYPE_MESSAGE = " had a wrong type for a key. Expected type of all keys was {y_type!r}, but there was the key {x} ({x_type!r})."
MISSING_KEY_MESSAGE = " was missing the key {!r}, {}."
EXTRA_KEYS_MESSAGE = " had all the correct keys ({}), but also had these unexpected keys: {}"
NOT_A_TYPE_MESSAGE = " was the value {x!r} ({x_type!r}). However, that's not important because your World definition's expected type ({y}) doesn't make sense! Your World definition should not have literal values like {y} in it, only types (like {y_type}). The literal values go into instances of the world (like INITIAL_WORLD)."

def _validate_dictionary_type(value, expected_type, path):
    if not isinstance(value, dict):
        return path + WRONG_TYPE_MESSAGE.format(x=repr(value), x_type=get_name(type(value)), y_type="dictionary")
    for expected_key, expected_value in expected_type.items():
        if isinstance(expected_key, str):
            if expected_key not in value:
                return path + MISSING_KEY_MESSAGE.format(expected_key, make_key_list(list(value.keys())))
            reason = _validate_type(value[expected_key], expected_value,
                                    path+"[{!r}]".format(expected_key))
            if reason:
                return reason
        elif isinstance(expected_key, type):
            for k, v in value.items():
                new_path = path+"[{!r}]".format(k)
                if not isinstance(k, expected_key):
                    return path + WRONG_KEY_TYPE_MESSAGE.format(x=repr(k), x_type=get_name(type(k)), y_type=get_name(expected_key))
                reason = _validate_type(v, expected_value, new_path)
                if reason:
                    return reason
            break # only support one key/value type in Lookup style
    else:
        if len(expected_type) != len(value):
            unexpected_keys = set(value.keys()) - set(expected_type.keys())
            unexpected_keys = ", ".join(map(repr, unexpected_keys))
            expected_keys = ", ".join(map(repr, expected_type))
            return path + EXTRA_KEYS_MESSAGE.format(expected_keys, unexpected_keys)
        
SIMPLE_TYPES = (int, float, bool, str)

def _validate_type(value, expected_type, path="world"):
    if isinstance(expected_type, dict):
        return _validate_dictionary_type(value, expected_type, path)
    elif isinstance(expected_type, list):
        if not isinstance(value, list):
            return path + WRONG_TYPE_MESSAGE.format(x=repr(value), x_type=get_name(type(value)), y_type="list")
        if not expected_type and value:
            return path + WRONG_TYPE_MESSAGE.format(x=repr(value), x_type=get_name(type(value)), y_type="empty list")
        for index, element in enumerate(value):
            reason = _validate_type(element, expected_type[0], path+"[{}]".format(index))
            if reason:
                return reason
    elif isinstance(expected_type, SIMPLE_TYPES):
        return path + NOT_A_TYPE_MESSAGE.format(x=repr(value), x_type=get_name(type(value)), y=repr(expected_type), y_type=type(expected_type).__name__)
    elif expected_type == float:
        if not isinstance(value, (int, float)) and value is not None:
            return path + WRONG_TYPE_MESSAGE.format(x=repr(value), x_type=get_name(type(value)), y_type=get_name(expected_type))
    elif not isinstance(value, expected_type) and value is not None:
        return path + WRONG_TYPE_MESSAGE.format(x=repr(value), x_type=get_name(type(value)), y_type=get_name(expected_type))


class Cisc108Game(Cisc108GameUntyped):
    '''
    A version of the Cisc108Game class that requires stricter typing with the
    World.
    '''
    def __init__(self, World, window_width, window_height, window_caption,
                 an_initial_world, draw_world, update_world,
                 handle_key=None, handle_mouse=None, handle_motion=None,
                 handle_release=None):
        super().__init__(window_width, window_height, window_caption,
                         an_initial_world, draw_world, update_world,
                         handle_key, handle_mouse, handle_motion, handle_release)
        self.World = World
        self.validate_worlds_type("In the initial world")
    
    def validate_worlds_type(self, when: str):
        that_world_is_valid = or_give_reason = _validate_type(self.world, self.World, when+", world")
        that_world_is_valid = not that_world_is_valid
        if not that_world_is_valid:
            try:
                arcade.close_window()
            except:
                pass
        assert that_world_is_valid, or_give_reason
        #if reason:
        #    raise AssertionError(reason)

    def on_draw(self):
        self.validate_worlds_type("Before on_draw")
        super().on_draw()
        self.validate_worlds_type("After on_draw")
    
    def on_update(self, delta_time: float):
        self.validate_worlds_type("Before on_update")
        super().on_update(delta_time)
        self.validate_worlds_type("After on_update")
    
    def on_key_press(self, key: int, modifiers: int):
        self.validate_worlds_type("Before on_key_press")
        super().on_key_press(key, modifiers)
        self.validate_worlds_type("After on_key_press")
    
    def on_key_release(self, key: int, modifiers: int):
        self.validate_worlds_type("Before on_key_release")
        super().on_key_release(key, modifiers)
        self.validate_worlds_type("After on_key_release")
    
    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        self.validate_worlds_type("Before on_mouse_press")
        super().on_mouse_press(x, y, button, modifiers)
        self.validate_worlds_type("After on_mouse_press")
    
    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        self.validate_worlds_type("Before on_mouse_motion")
        super().on_mouse_motion(x, y, dx, dy)
        self.validate_worlds_type("After on_mouse_motion")

def assert_type(value, expected_type) -> bool:
    """
    Checks that the given value is of the expected_type.
    
    Args:
        value (Any): Any kind of python value. Should have been computed by
            the students' code (their actual answer).
        expected_type (type): Any kind of type value. Should be in the format
            used within CISC108. This includes support for literal composite
            types (e.g., [int] and {str: int}) and record types.
    Returns:
        bool: Whether or not the assertion passed.
    """
    # Can we add in the line number and code?
    line, code = get_line_code()
    if None in (line, code):
        context = ""
    else:
        context = MESSAGE_LINE_CODE.format(line=line, code=code)
        #student_tests.lines.append(line)
    
    reason = _validate_type(value, expected_type, "value")
    # TODO
    #student_tests.tests += 1
    if reason is not None:
        #student_tests.failures += 1
        if isinstance(expected_type, dict):
            if isinstance(value, dict):
                reason = "the "+reason
            else:
                reason = "the "+reason
        print("FAILURE{context},".format(context=context), reason)
        return False
    elif not QUIET:
        print(MESSAGE_GENERIC_SUCCESS.format(context=context))
    #student_tests.successes += 1
    return True

