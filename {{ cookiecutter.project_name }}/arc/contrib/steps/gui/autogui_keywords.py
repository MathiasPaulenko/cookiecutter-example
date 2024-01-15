from behave import use_step_matcher, step

from arc.contrib.gui.autogui import AutoGUIWrapper
from arc.contrib.tools import files

import logging

logger = logging.getLogger(__name__)

use_step_matcher("re")

auto_gui_wrapper = AutoGUIWrapper()


@step("disable failsafe for autogui")
def disable_fail_safe(context):
    """
    This step disable the FAILSAFE for PyAutogui
    :param context:
    :return:
    """
    auto_gui_wrapper.set_fail_safe(False)
    msg = "AutoGUI disabled fail safe."
    context.func.evidences.add_text(msg)
    logger.info(msg)


@step("enable failsafe for autogui")
def enable_fail_safe(context):
    """
    This step enable the FAILSAFE for PyAutogui
    :param context:
    :return:
    """
    
    auto_gui_wrapper.set_fail_safe(True)
    msg = "AutoGUI enabled fail safe."
    context.func.evidences.add_text(msg)
    logger.info(msg)


@step(u"execute app with path '(?P<path>.+)'")
def execute_app_with_path(context, path):
    """
    This step execute the application given a path to the executable file.
    :param context:
    :param path:
    :return:
    """
    
    auto_gui_wrapper.execute_application(path)
    msg = f"Executed app in path '{path}'"
    context.func.evidences.add_text(msg)
    logger.info(msg)


@step(u"show message box of type '(?P<message_type>.+)' with text '(?P<text>.+)'")
def show_message_box_by_type(context, message_type, text):
    """
    This step allow to display a message given a type and a text.
    :param context:
    :param message_type:
    :param text:
    :return:
    """
    
    auto_gui_wrapper.message_box(text, message_type)
    msg = f"Showing message box of type '{message_type}' with text '{text}'"
    context.func.evidences.add_text(msg)
    logger.info(msg)


@step(u"show message box of type alert with text '(?P<text>.+)'")
def show_message_alert_box(context, text):
    """
    This step allow to display an alert box with a text.
    :param context:
    :param text:
    :return:
    """
    
    auto_gui_wrapper.message_box(text, 'alert')
    msg = f"Showing message box of type alert with text '{text}'"
    context.func.evidences.add_text(msg)
    logger.info(msg)


@step(u"show message box of type 'confirm' with text '(?P<text>.+)'")
def show_message_confirm_box(context, text):
    """
    This step allow to display a confirmation box with a text.
    :param context:
    :param text:
    :return:
    """
    
    auto_gui_wrapper.message_box(text, 'confirm')
    msg = f"Showing message box of type confirm with text '{text}'"
    context.func.evidences.add_text(msg)
    logger.info(msg)


@step(u"show message box of type 'prompt' with text '(?P<text>.+)'")
def show_message_prompt_box(context, text):
    """
    This step allow to display a prompt box with a text.
    :param context:
    :param text:
    :return:
    """
    
    auto_gui_wrapper.message_box(text, 'prompt')
    msg = f"Showing message box of type 'prompt' with text '{text}'"
    context.func.evidences.add_text(msg)
    logger.info(msg)


@step(u"locate unique image on screen with path '(?P<path>.+)' with similarity confidence of '(?P<similarity_confidence>.+)'")
def locate_unique_image_on_screen_with_path_and_similarity_confidence(context, path, similarity_confidence):
    """
    This step locate the coordinates of one image given a source path image and allow to change the similarity confidence.
    :param context:
    :param path:
    :param similarity_confidence:
    :return:
    """
    
    auto_gui_wrapper.locate_image_on_screen(path, similarity_confidence=int(similarity_confidence))
    msg = f"Locating unique image on screen with path '{path}' with similarity of {similarity_confidence}"
    context.func.evidences.add_text(msg)
    logger.info(msg)


@step(u"locate multiple image on screen with path '(?P<path>.+)' with similarity confidence of '(?P<similarity_confidence>.+)'")
def locate_multiple_image_on_screen_with_path_and_similarity_confidence(context, path, similarity_confidence):
    """
    This step locate the coordinates of multiple images given a source path image and allow to change the similarity confidence.
    :param context:
    :param path:
    :param similarity_confidence:
    :return:
    """
    
    auto_gui_wrapper.locate_image_on_screen(path, locate_multiple=True, similarity_confidence=int(similarity_confidence))
    msg = f"Locating multiple image on screen with path '{path}' with similarity of {similarity_confidence}"
    context.func.evidences.add_text(msg)
    logger.info(msg)


@step(u"locate unique image on screen with path '(?P<path>.+)'")
def locate_unique_image_on_screen_with_path(context, path):
    """
    This step locate the coordinates of one image given a source path image.
    :param context:
    :param path:
    :return:
    """
    
    auto_gui_wrapper.locate_image_on_screen(path)
    msg = f"Locating unique image on screen with path '{path}'"
    context.func.evidences.add_text(msg)
    logger.info(msg)


@step(u"locate multiple images on screen with path '(?P<path>.+)'")
def locate_multiple_image_on_screen_with_path(context, path):
    """
    This step locate the coordinates of multiple images given a source path image.
    :param context:
    :param path:
    :return:
    """
    
    auto_gui_wrapper.locate_image_on_screen(path, locate_multiple=True)
    msg = f"Locating unique image on screen with path '{path}'"
    context.func.evidences.add_text(msg)
    logger.info(msg)


@step(u"write text '(?P<text>.+)'")
def write_text(context, text):
    """
    This step write the given text.
    :param context:
    :param text:
    :return:
    """
    
    auto_gui_wrapper.write_text(text)
    msg = f"Written text: '{text}'"
    context.func.evidences.add_text(msg)
    logger.info(msg)


@step(u"send hotkeys '(?P<text>.+)'")
def send_hotkeys(context, text):
    """
    This step send a hotkeys.
    Example:
    send hotkeys 'ctrlleft, z'
    :param context:
    :param text:
    :return:
    """
    
    keys = text.replace(' ', '').split(',')
    auto_gui_wrapper.hotkey(*keys)
    msg = f"Executed hotkeys '{keys}'"
    context.func.evidences.add_text(msg)
    logger.info(msg)


@step(u"press key down '(?P<text>.+)'")
def press_key_down(context, text):
    """
    This step press a key down.
    :param context:
    :param text:
    :return:
    """
    
    auto_gui_wrapper.press_key(text)
    msg = f"pressing key down '{text}'"
    context.func.evidences.add_text(msg)
    logger.info(msg)


@step(u"press key up '(?P<text>.+)'")
def press_key_up(context, text):
    """
    This step press a key up.
    :param context:
    :param text:
    :return:
    """
    
    auto_gui_wrapper.press_key(text, direction="up")
    msg = f"pressing key up '{text}'"
    context.func.evidences.add_text(msg)
    logger.info(msg)


@step(u"make click in coordinates '(?P<text>.+)'")
def make_click_in_coordinates(context, text):
    """
        This step makes one left-click on the given coordinates
    :param context:
    :param text:
    :return:
    """
    coordinates = text.replace(' ', '').split(',')
    
    auto_gui_wrapper.click(move_to_x=int(coordinates[0]), move_to_y=(coordinates[1]))
    msg = f"Click on coordinates '{coordinates}'"
    context.func.evidences.add_text(msg)
    logger.info(msg)


@step(u"make '(?P<click_number>.+)' clicks in coordinates '(?P<text>.+)'")
def make_multiple_click_in_coordinates(context, click_number, text):
    """
    This step makes multiple left-click on the given coordinates
    :param context:
    :param click_number:
    :param text:
    :return:
    """
    coordinates = text.replace(' ', '').split(',')
    
    auto_gui_wrapper.click(move_to_x=int(coordinates[0]), move_to_y=int(coordinates[1]), clicks=int(click_number))
    msg = f"Click on coordinates '{coordinates}' {click_number} times"
    context.func.evidences.add_text(msg)
    logger.info(msg)


@step(u"make right click in coordinates '(?P<text>.+)'")
def make_right_click_in_coordinates(context, text):
    """
    This step makes one right-click on the given coordinates
    :param context:
    :param text:
    :return:
    """
    coordinates = text.replace(' ', '').split(',')
    
    auto_gui_wrapper.click(move_to_x=coordinates[0], move_to_y=coordinates[1], button="right")
    msg = f"Right click on coordinates '{coordinates}'"
    context.func.evidences.add_text(msg)
    logger.info(msg)


@step(u"make '(?P<click_number>.+)' right clicks in coordinates '(?P<text>.+)'")
def make_multiple_right_click_in_coordinates(context, click_number, text):
    """
    This step makes multiple right-click on the given coordinates
    :param context:
    :param click_number:
    :param text:
    :return:
    """
    coordinates = text.replace(' ', '').split(',')
    
    auto_gui_wrapper.click(move_to_x=int(coordinates[0]), move_to_y=int(coordinates[1]), clicks=int(click_number), button="right")
    msg = f"Right click on coordinates '{coordinates}' {click_number} times"
    context.func.evidences.add_text(msg)
    logger.info(msg)


@step(u"drag cursor to position '(?P<coordinates>.+)' with duration '(?P<duration>.+)'")
def drag_cursor_to_position_with_duration(context, coordinates, duration):
    """
    This step drag the cursor to a position given the coordinates and add a duration to the action
    :param context:
    :param coordinates:
    :param duration:
    :return:
    """
    coordinates = coordinates.replace(' ', '').split(',')
    
    auto_gui_wrapper.drag_cursor_to(
        x_destination=int(coordinates[0]),
        y_destination=int(coordinates[1]),
        movement_duration=float(duration)
    )
    msg = f"Dragging cursor to coordinates '{coordinates}' with duration '{duration}'"
    context.func.evidences.add_text(msg)
    logger.info(msg)


@step(u"drag cursor to relative position '(?P<coordinates>.+)' with duration '(?P<duration>.+)'")
def drag_cursor_to_relative_position_with_duration(context, coordinates, duration):
    """
    This step drag the cursor to a relative position given the coordinates and add a duration to the action
    :param context:
    :param coordinates:
    :param duration:
    :return:
    """
    coordinates = coordinates.replace(' ', '').split(',')
    
    auto_gui_wrapper.drag_cursor_relative(
        x_movement=int(coordinates[0]),
        y_movement=int(coordinates[1]),
        movement_duration=float(duration)
    )
    msg = f"Dragging cursor to relative coordinates '{coordinates}' with duration '{duration}'"
    context.func.evidences.add_text(msg)
    logger.info(msg)


@step(u"drag cursor to position '(?P<coordinates>.+)'")
def drag_cursor_to_position(context, coordinates):
    """
    This step drag the cursor to a position given the coordinates
    :param context:
    :param coordinates:
    :return:
    """
    coordinates = coordinates.replace(' ', '').split(',')
    
    auto_gui_wrapper.drag_cursor_to(x_destination=int(coordinates[0]), y_destination=int(coordinates[1]))
    msg = f"Dragging cursor to coordinates '{coordinates}'"
    context.func.evidences.add_text(msg)
    logger.info(msg)


@step(u"drag cursor to relative position '(?P<coordinates>.+)'")
def drag_cursor_to_relative_position(context, coordinates):
    """
    This step drag the cursor to a relative position given the coordinates
    :param context:
    :param coordinates:
    :return:
    """
    coordinates = coordinates.replace(' ', '').split(',')
    
    auto_gui_wrapper.drag_cursor_relative(x_movement=int(coordinates[0]), y_movement=int(coordinates[1]))
    msg = f"Dragging cursor to relative coordinates '{coordinates}'"
    context.func.evidences.add_text(msg)
    logger.info(msg)


@step(u"move cursor to position '(?P<coordinates>.+)' with duration '(?P<duration>.+)'")
def move_cursor_to_position_with_duration(context, coordinates, duration):
    """
    This step move the cursor to a position given the coordinates and add a duration to the action
    :param context:
    :param coordinates:
    :param duration:
    :return:
    """
    coordinates = coordinates.replace(' ', '').split(',')
    
    auto_gui_wrapper.move_cursor_to(
        x_destination=int(coordinates[0]),
        y_destination=int(coordinates[1]),
        movement_duration=float(duration)
    )
    msg = f"Move cursor to position '{coordinates}'"
    context.func.evidences.add_text(msg)
    logger.info(msg)


@step(u"move cursor to relative position '(?P<coordinates>.+)' with duration '(?P<duration>.+)'")
def move_cursor_to_relative_position_with_duration(context, coordinates, duration):
    """
    This step move the cursor to a relative position given the coordinates and add a duration to the action
    :param context:
    :param coordinates:
    :param duration:
    :return:
    """
    coordinates = coordinates.replace(' ', '').split(',')
    
    auto_gui_wrapper.move_cursor_relative(
        x_movement=int(coordinates[0]),
        y_movement=int(coordinates[1]),
        movement_duration=float(duration)
    )
    msg = f"Move cursor to relative position '{coordinates}' with duration '{duration}' seconds"
    context.func.evidences.add_text(msg)
    logger.info(msg)


@step(u"move cursor to position '(?P<coordinates>.+)'")
def move_cursor_to_position(context, coordinates):
    """
    This step move the cursor to a position given the coordinates
    :param context:
    :param coordinates:
    :return:
    """
    coordinates = coordinates.replace(' ', '').split(',')
    
    auto_gui_wrapper.move_cursor_to(x_destination=int(coordinates[0]), y_destination=int(coordinates[1]))
    msg = f"Moved cursor relative position '{coordinates}'"
    context.func.evidences.add_text(msg)
    logger.info(msg)


@step(u"move cursor to relative position '(?P<coordinates>.+)'")
def move_cursor_to_relative_position(context, coordinates):
    """
    This step move the cursor to a relative position given the coordinates
    :param context:
    :param coordinates:
    :return:
    """
    coordinates = coordinates.replace(' ', '').split(',')
    
    auto_gui_wrapper.move_cursor_relative(x_movement=int(coordinates[0]), y_movement=int(coordinates[1]))
    msg = f"Moved cursor to relative position '{coordinates}'"
    context.func.evidences.add_text(msg)
    logger.info(msg)


@step(u"check coordinates '(?P<coordinates>.+)' are on screen")
def check_coordinates_are_on_screen(context, coordinates):
    """
    This step check if the coordinates are available in the screen.
    :param context:
    :param coordinates:
    :return:
    """
    logger.info(f"Checking coordinates '{coordinates}' are on screen")
    coordinates = coordinates.replace(' ', '').split(',')
    
    result = auto_gui_wrapper.check_coordinates_are_on_screen(
        screen_coord_x=int(coordinates[0]), screen_coord_y=int(coordinates[1])
    )
    current_position = auto_gui_wrapper.get_cursor_position()
    error_msg = f"Cursor not in {coordinates} position. Cursor is at {current_position}"
    context.func.evidences.add_unit_table(
        'Check coordinates are on screen',
        "Coordinates",
        current_position,
        coordinates,
        result,
        error_msg=error_msg
    )
    logger.info(f"Coordinates in screen: {result}")
    assert result, error_msg


@step(u"get cursor position and save in the profile file '(?P<file_name>.+)' with key '(?P<key>.+)'")
def get_cursor_position_and_save_in_path(context, file_name, key):
    """
    This step get the cursor position and save in the selected profile file with the selected file.
    :param context:
    :param file_name:
    :param key:
    :return:
    """
    
    current_position = auto_gui_wrapper.get_cursor_position()
    msg = f"Current cursor position in '{current_position}'. Saving in file '{file_name}' with key '{key}'"
    context.func.evidences.add_text(msg)
    files.update_data_value(context, 'profiles', file_name, key, current_position)
    logger.info(msg)


@step(u"get screen size and save in the profile file '(?P<file_name>.+)' with key '(?P<key>.+)'")
def get_screen_size_and_save_in_path(context, file_name, key):
    """
    This step get the screen size and save it in the selected profile file with the selected key
    :param context:
    :param file_name:
    :param key:
    :return:
    """
    
    size = auto_gui_wrapper.get_screen_size()
    msg = f"The screen size is {size}. Saving in file name {file_name} with key {key}"
    context.func.evidences.add_text(msg)
    files.update_data_value(context, 'profiles', file_name, key, size)
    logger.info(msg)


@step(u"do a sleep of '(?P<seconds>.+)' seconds")
def do_a_sleep_of_n_seconds(context, seconds):
    """
    This steps do a sleep for pyautogui
    :param context:
    :param seconds:
    :return:
    """
    
    auto_gui_wrapper.sleep(int(seconds))
    msg = f"Do a sleep of '{seconds}' seconds"
    context.func.evidences.add_text(msg)
    logger.info(msg)


@step(u"make a screenshot with pyautogui on the region '(?P<region>.+)'")
def make_screenshot_with_pyautogui_and_region(context, region):
    """
    This step allows to make a screenshot while using pyautogui
    :param context:
    :param region:
    :return:
    """
    region = region.replace(' ', '').split(',')
    
    screenshot_path = context.utils.get_path_capture_screenshot_autogui(
        f"{str(context.runtime.step.keyword)}_{str(context.runtime.step.name)}"
    )
    auto_gui_wrapper.make_screenshot(
        path=screenshot_path,
        screen_region=region
    )
    context.runtime.step.screenshots.append(screenshot_path)
    logger.info(f"Making screenshot of the region '{region}' and saving it in path '{screenshot_path}'")


@step(u"make a screenshot with pyautogui")
def make_screenshot_with_pyautogui(context):
    """
    This step allows to make a screenshot while using pyautogui
    :param context:
    :return:
    """
    
    screenshot_path = context.utils.get_path_capture_screenshot_autogui(
        f"{str(context.runtime.step.keyword)}_{str(context.runtime.step.name)}"
    )
    auto_gui_wrapper.make_screenshot(
        path=screenshot_path
    )
    context.runtime.step.screenshots.append(screenshot_path)
    logger.info(f"Making a screenshot and saving it in path '{screenshot_path}'")
