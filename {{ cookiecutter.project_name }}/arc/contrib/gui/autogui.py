"""
Wrapper used to automate graphical user interfaces using pyautogui
"""

import logging
import os
from arc.core.test_method.exceptions import TalosNotThirdPartyAppInstalled, TalosRunError, TalosResourceNotFound

logger = logging.getLogger(__name__)

try:
    import pyautogui  # noqa
except ModuleNotFoundError:
    msg = "Please install the pyautogui module to use this functionality."
    logger.error(msg)
    raise TalosNotThirdPartyAppInstalled(msg)


class AutoGUIWrapper:

    """
    The following class contains all the elements needed to automate the use of a GUI using pyautogui
    """

    def __init__(self):

        self.system = os
        self.gui = pyautogui
        self.gui.FAILSAFE = True
        self.gui.PAUSE = 0
        self.keys = self.gui.KEY_NAMES
        self.key_press_direction = ['down', 'up']
        logger.info("AutoGUIWrapper object declared")

    def set_fail_safe(self, is_enabled):
        """
        enables or disables the FAILSAFE parameter of pyautogui
        :param is_enabled: true or false
        """
        self.gui.FAILSAFE = is_enabled
        logger.info(f"FAILSAFE set to {is_enabled}")

    def set_pause_time(self, pause_time):
        """
        sets the time of the PAUSE parameter of pyautogui
        :param pause_time: number of seconds
        """
        self.gui.PAUSE = pause_time
        logger.info(f"PAUSE time set to {pause_time}")

    def get_screen_size(self):
        """
        method used to get the size of the screen
        :return: size of the screen of the user
        """
        size = self.gui.size()
        logger.info(f"get screen size: {size}")
        return size

    def get_cursor_position(self):
        """
        method used to get the position of the mouse cursor
        :return: mouse cursor position coordinates
        """
        position = self.gui.position()
        logger.info(f"get cursor position: {position}")
        return position

    def check_cursor_is_in_position(self, cursor_pos_x, cursor_pos_y):
        """
        checks wether the mouse is in a position or not
        :param cursor_pos_x: x coordinate to check
        :param cursor_pos_y: y coordinate to check
        :return: true or false
        """
        check = (self.gui.position() == (cursor_pos_x, cursor_pos_y))
        logger.info(f"check if cursor is in {cursor_pos_x}, {cursor_pos_y} coordinates: {check}")
        return check

    def check_coordinates_are_on_screen(self, screen_coord_x, screen_coord_y):
        """
        checks wether the coordinates are on the screen or not
        :param screen_coord_x: x coordinate to check
        :param screen_coord_y: y coordinate to check
        :return: true or false
        """
        check = self.gui.onScreen(screen_coord_x, screen_coord_y)
        logger.info(f"check if coordinates {screen_coord_x}, {screen_coord_y} are on screen: {check}")
        return check

    def move_cursor_to(self, x_destination, y_destination, movement_duration=0):
        """
        moves the cursor to specified coordinates
        :param x_destination: x coordinate of destination
        :param y_destination: y coordinate of destination
        :param movement_duration: time taken to arrive to the destination from the origin
        """
        self.gui.moveTo(x_destination, y_destination, movement_duration)
        logger.info(f"cursor moved to {x_destination}, {y_destination}")

    def move_cursor_relative(self, x_movement=0, y_movement=0, movement_duration=0):
        """
        moves the cursor a number of pixels
        :param x_movement: number of pixels moved in the x-axis
        :param y_movement: number of pixels moved in the y-axis
        :param movement_duration: time taken to arrive to the destination from the origin
        """
        self.gui.move(x_movement, y_movement, movement_duration)
        logger.info(f"cursor moved {x_movement}, {y_movement} pixels")

    def drag_cursor_relative(self, x_movement=0, y_movement=0, movement_duration=0):
        """
        drags the cursor a number of pixels
        :param x_movement: number of pixels dragged in the x-axis
        :param y_movement: number of pixels dragged in the y-axis
        :param movement_duration: time taken to arrive to the destination from the origin
        """
        self.gui.drag(x_movement, y_movement, movement_duration)
        logger.info(f"cursor dragged {x_movement}, {y_movement} pixels")

    def drag_cursor_to(self, x_destination, y_destination, movement_duration=0):
        """
        drags the cursor to specified coordinates
        :param x_destination: x coordinate of destination
        :param y_destination: y coordinate of destination
        :param movement_duration: time taken to arrive to the destination from the origin
        """
        self.gui.dragTo(x_destination, y_destination, movement_duration)
        logger.info(f"cursor dragged to {x_destination}, {y_destination}")

    def click(self, move_to_x=None, move_to_y=None, clicks=1, interval=0.05, button='left'):
        """
        make a number of clicks with a mouse button on the specified coordinates
        :param move_to_x: x coordinate of destination
        :param move_to_y: y coordinate of destination
        :param clicks: number of clicks
        :param interval: time between each click
        :param button: mouse button used
        """
        try:
            self.gui.click(x=move_to_x, y=move_to_y, clicks=clicks, interval=interval, button=button)
            logger.info(f"{button} button clicked {clicks} times at {self.gui.position()} coordinates")
        except self.gui.PyAutoGUIException:
            msg = f"mouse button '{button}' not valid"
            logger.error(msg)
            raise TalosRunError(msg)

    def press_key(self, key_name, direction='down'):
        """
        presses a key from the keyboard
        :param key_name: key to press
        :param direction: direction of the interaction
        """
        if key_name in self.keys:
            if direction in self.key_press_direction:
                if direction == 'down':
                    self.gui.keyDown(key_name)
                    logger.info(f"key '{key_name}' pressed down")
                elif direction == 'up':
                    self.gui.keyUp(key_name)
                    logger.info(f"key '{key_name}' pressed up")
            else:
                raise TalosRunError('Key pressing direction not valid')
        else:
            raise TalosRunError('Key not valid')

    def hotkey(self, *args):
        """
        executes a shortcut
        Receives a list of string with the key name to press.
        """
        self.gui.hotkey(*args)

    def write_text(self, text, seconds_between_keys=0):
        """
        writes text simulating a keyboard
        :param text: text to write
        :param seconds_between_keys: seconds between each key input
        """
        self.gui.typewrite(text, seconds_between_keys)
        logger.info(f"text '{text}' written")

    def make_screenshot(self, path=None, screen_region=None):
        """
        makes a screenshot of the specified region of the screen
        :param path: path and name used to save the image
        :param screen_region: region of the screen to shot
        :return: image object
        """
        screenshot = self.gui.screenshot(path, screen_region)
        logger.info(f"screenshot {screenshot} was made")
        screenshot.save(path)
        return screenshot

    def locate_image_on_screen(self, img_path, locate_multiple=False, similarity_confidence=1):
        """
        locates the coordinates of an image found on the screen
        :param img_path: path of the image to look for in the screen
        :param locate_multiple: used when looking for multiple similar images on the screen
        :param similarity_confidence: used to locate images with subtle differences
        :return: coordinates of the image found
        """
        try:
            if locate_multiple:
                try:
                    image_list = list(self.gui.locateAllOnScreen(img_path, confidence=similarity_confidence))
                    logger.info(f"multiple images located at {image_list}")
                    if image_list is None:
                        msg = "Image not found on screen"
                        logger.error(msg)
                        raise TalosRunError(msg)
                    return image_list
                except ModuleNotFoundError:
                    msg = "Please install the opencv-python module to use this functionality."
                    logger.error(msg)
                    raise TalosNotThirdPartyAppInstalled(msg)
            elif not locate_multiple:
                try:
                    image_center = self.gui.locateCenterOnScreen(img_path, confidence=similarity_confidence)
                    logger.info(f"image located at {image_center}")
                    if image_center is None:
                        msg = f"Image {img_path} not found on screen"
                        logger.error(msg)
                        raise TalosRunError(msg)
                    return image_center
                except ModuleNotFoundError:
                    msg = "Please install the opencv-python module to use this functionality."
                    logger.error(msg)
                    raise TalosNotThirdPartyAppInstalled(msg)
            else:
                raise TalosRunError('Parameter value in locate_multiple not valid')
        except IOError:
            msg = f"Image path {img_path} could not be reached"
            logger.error(msg)
            raise TalosResourceNotFound(msg)

    def message_box(self, text, message_type='alert'):
        """
        shows a message box of the type alert, confirm or prompt
        :param text: text showed in the message
        :param message_type: type of the message
        """
        if message_type == 'alert':
            logger.info(f"message of the type {message_type} showed")
            return self.gui.alert(text)
        elif message_type == 'confirm':
            logger.info(f"message of the type {message_type} showed")
            return self.gui.confirm(text)
        elif message_type == 'prompt':
            logger.info(f"message of the type {message_type} showed")
            return self.gui.prompt(text)
        else:
            raise TalosRunError('Type of message not valid')

    def execute_application(self, app_exe_path):
        """
        runs a program using the executable
        :param app_exe_path: path of the application executable
        """
        try:
            self.system.startfile(app_exe_path)
            logger.info(f"application at {app_exe_path} executed")
        except FileNotFoundError:
            msg = f"Executable path {app_exe_path} not found"
            logger.error(msg)
            raise TalosResourceNotFound(msg)

    def sleep(self, seconds):
        """
        pauses the program for a number of seconds
        :param seconds: sleep time in seconds
        """
        self.gui.sleep(seconds)
        logger.info(f"program paused for {seconds} seconds")
