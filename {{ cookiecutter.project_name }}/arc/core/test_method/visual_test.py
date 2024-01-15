# -*- coding: utf-8 -*-
"""
Visual Testing engine configuration file.
"""

import itertools
import logging
import os
import json
import re
import shutil
from io import BytesIO
from os import path
from selenium.common.exceptions import NoSuchElementException

from PIL import Image, ImageChops

from arc.core import constants
from arc.core.driver.driver_manager import DriverManager
from arc.core.test_method.exceptions import TalosVisualTestingError
from arc.settings.settings_manager import Settings

logger = logging.getLogger(__name__)


def activate_visualtesting(context):
    if Settings.VISUAL_TESTING.get('enabled'):
        from arc.core.behave.context_utils import PyTalosContext
        from arc.core.config_manager import ConfigFiles
        context.pytalos = PyTalosContext(context)
        context.pytalos.config_files = ConfigFiles()
        context.pytalos.config_files.set_visual_baseline_directory(
            Settings.VISUAL_TESTING.get('baseline_dir'))

        if Settings.VISUAL_TESTING.get('clean_baseline_dir'):
            shutil.rmtree(Settings.VISUAL_TESTING.get('baseline_dir'))

        if Settings.VISUAL_TESTING.get('save_img'):
            Settings.VISUAL_TESTING.set("generate_report", value=False)
            Settings.VISUAL_TESTING.set("generate_reports.json", value=False)
            Settings.VISUAL_TESTING.set("generate_reports.html", value=False)


class VisualTest(object):
    """Visual testing class

    :type driver_wrapper: toolium.driver_wrapper.DriverWrapper
    """
    driver_wrapper = None  #: driver wrapper instance
    results = {
        'scenario_results': {},
        'total_results': {'equal': 0, 'diff': 0},
        'include_passed_tests': Settings.VISUAL_TESTING.get('include_passed_tests')
    }  #: dict to save visual assert results
    force = False  #: if True, screenshot is compared even if visual testing is disabled by configuration

    def __init__(self, driver_wrapper=None, force=False):
        from arc.contrib.utilities import makedirs_safe
        self.driver_wrapper = driver_wrapper if driver_wrapper else DriverManager.get_default_wrapper()
        self.force = force
        if not Settings.VISUAL_TESTING.get('enabled') and not self.force:
            return

        self.utils = self.driver_wrapper.utils
        self.output_directory = DriverManager.visual_output_directory

        # Update baseline with real platformVersion value
        if self.driver_wrapper.baseline_name is not None and '{platformVersion}' in self.driver_wrapper.baseline_name:
            platform_version = self.driver_wrapper.driver.capabilities['platformVersion']
            baseline_name = self.driver_wrapper.baseline_name.replace('{platformVersion}', platform_version)
            self.driver_wrapper.baseline_name = baseline_name
            self.driver_wrapper.visual_baseline_directory = os.path.join(
                DriverManager.visual_baseline_directory,
                self.get_valid_filename(baseline_name)
            )

        self.baseline_directory = Settings.VISUAL_TESTING.get('baseline_dir')
        self.save_img = Settings.VISUAL_TESTING.get('save_img')

        # Create folders
        makedirs_safe(self.baseline_directory)
        makedirs_safe(self.output_directory)

    def assert_screenshot(self, element, filename, file_suffix=None, threshold=0, exclude_elements=None):
        """Assert that a screenshot of an element is the same as a screenshot on disk, within a given threshold

        :param element: either a WebElement, PageElement or element locator as a tuple (locator_type, locator_value).
                        If None, a full screenshot is taken.
        :param filename: the filename for the screenshot, which will be appended with ``.png``
        :param file_suffix: a string to be appended to the output filename with extra info about the test.
        :param threshold: percentage threshold for triggering a test failure (value between 0 and 1)
        :param exclude_elements: list of WebElements, PageElements or element locators as a tuple (locator_type,
                                 locator_value) that must be excluded from the assertion
        """
        if exclude_elements is None:
            exclude_elements = []
        if not Settings.VISUAL_TESTING.get('enabled') and not self.force:
            return
        if not (isinstance(threshold, int) or isinstance(threshold, float)) or threshold < 0 or threshold > 1:
            raise TypeError('Threshold must be a number between 0 and 1: {}'.format(threshold))

        # Search elements
        web_element = self.utils.get_web_element(element)
        exclude_web_elements = []
        for exclude_element in exclude_elements:
            try:
                exclude_web_elements.append(self.utils.get_web_element(exclude_element))
            except NoSuchElementException as e:
                logger.warning("Element to be excluded not found: %s", str(e))

        baseline_path = os.path.join(self.baseline_directory, '{}.png'.format(filename))
        filename_with_suffix = '{0}__{1}'.format(filename, file_suffix) if file_suffix else filename
        unique_name = '{0:0=2d}_{1}'.format(DriverManager.visual_number, filename_with_suffix)
        unique_name = '{}.png'.format(self.get_valid_filename(unique_name))
        output_path = os.path.join(self.output_directory, unique_name)

        # Get screenshot and modify it
        img = Image.open(BytesIO(self.driver_wrapper.driver.get_screenshot_as_png()))
        img = self.remove_scrolls(img)
        img = self.mobile_resize(img)
        img = self.desktop_resize(img)
        img = self.exclude_elements(img, exclude_web_elements)
        img = self.crop_element(img, web_element)
        img.save(output_path)
        DriverManager.visual_number += 1

        self.results['scenario_results'].setdefault(file_suffix, {
            'scenario_name': file_suffix,
            'equal': 0,
            'diff': 0,
            'screenshots': {}
        })

        self.results['scenario_results'][file_suffix]['screenshots'].setdefault(filename, {
            "current": 0,
            "diff": 0,
            "result": "failed"
        })

        # Determine whether we should save the baseline image
        if self.save_img:
            # Copy screenshot to baseline
            shutil.copyfile(output_path, baseline_path)

            if Settings.VISUAL_TESTING.get('generate_report'):
                self._add_result_to_report('baseline', baseline_path, file_suffix, filename)
            logger.debug("Visual screenshot '%s' saved in visualtests/baseline folder", filename)

        elif not os.path.exists(baseline_path):
            # Baseline should exist if save mode is not enabled
            error_message = f'Baseline file not found: {baseline_path}'
            logger.warning(error_message)
            self._add_result_to_report('diff', baseline_path, file_suffix, filename)
            if Settings.VISUAL_TESTING.get('fail') or self.force:
                raise AssertionError(error_message)
        elif Settings.VISUAL_TESTING.get('generate_report'):
            # Compare the screenshots
            self.compare_files(output_path, baseline_path, threshold, file_suffix, filename)

    def get_scrolls_size(self):
        """Return Chrome and Explorer scrolls sizes if they are visible
        Firefox screenshots don't contain scrolls

        :returns: dict with horizontal and vertical scrolls sizes
        """
        scroll_x = 0
        scroll_y = 0
        if self.driver_wrapper.config.get('Driver', 'type').split('-')[0] in ['chrome', 'iexplore'] and not self.driver_wrapper.is_mobile_test():
            scroll_height = self.driver_wrapper.driver.execute_script("return document.body.scrollHeight")
            scroll_width = self.driver_wrapper.driver.execute_script("return document.body.scrollWidth")
            window_height = self.driver_wrapper.driver.execute_script("return window.innerHeight")
            window_width = self.driver_wrapper.driver.execute_script("return window.innerWidth")
            scroll_size = 21 if self.driver_wrapper.config.get('Driver', 'type').split('-')[0] == 'iexplore' else 17
            scroll_x = scroll_size if scroll_width > window_width else 0
            scroll_y = scroll_size if scroll_height > window_height else 0
        return {'x': scroll_x, 'y': scroll_y}

    def remove_scrolls(self, img):
        """Remove browser scrolls from image if they are visible

        :param img: image object
        :returns: modified image object
        """
        scrolls_size = self.get_scrolls_size()
        if scrolls_size['x'] > 0 or scrolls_size['y'] > 0:
            new_image_width = img.size[0] - scrolls_size['y']
            new_image_height = img.size[1] - scrolls_size['x']
            img = img.crop((0, 0, new_image_width, new_image_height))
        return img

    def mobile_resize(self, img):
        """Resize image in iOS (native and web) and Android (web) to fit window size

        :param img: image object
        :returns: modified image object
        """
        if self.driver_wrapper.is_ios_test() or self.driver_wrapper.is_android_web_test():
            img = self.base_resize(img=img)
        return img

    def desktop_resize(self, img):
        """Resize image in Mac with Retina to fit window size

        :param img: image object
        :returns: modified image object
        """
        if self.driver_wrapper.is_mac_test():
            img = self.base_resize(img=img)
        return img

    def base_resize(self, img):
        """Base method for resize image

        :param img: image object
        :returns: modified image object
        """
        scale = img.size[0] / self.utils.get_window_size()['width']
        if scale != 1:
            new_image_size = (int(img.size[0] / scale), int(img.size[1] / scale))
            img = img.resize(new_image_size, Image.LANCZOS)
        return img

    def get_element_box(self, web_element):
        """Get element coordinates

        :param web_element: WebElement object
        :returns: tuple with element coordinates
        """
        if not self.driver_wrapper.is_mobile_test():
            scroll_x = self.driver_wrapper.driver.execute_script("return window.pageXOffset")
            scroll_x = scroll_x if scroll_x else 0
            scroll_y = self.driver_wrapper.driver.execute_script("return window.pageYOffset")
            scroll_y = scroll_y if scroll_y else 0
            offset_x = -scroll_x
            offset_y = -scroll_y
        else:
            offset_x = 0
            offset_y = self.utils.get_safari_navigation_bar_height()

        location = web_element.location
        size = web_element.size
        return (int(location['x']) + offset_x, int(location['y'] + offset_y),
                int(location['x'] + offset_x + size['width']), int(location['y'] + offset_y + size['height']))

    def crop_element(self, img, web_element):
        """Crop image to fit element

        :param img: image object
        :param web_element: WebElement object
        :returns: modified image object
        """
        if web_element:
            element_box = self.get_element_box(web_element)
            # Reduce element box if it is greater than image size
            element_max_x = img.size[0] if element_box[2] > img.size[0] else element_box[2]
            element_max_y = img.size[1] if element_box[3] > img.size[1] else element_box[3]
            element_box = (element_box[0], element_box[1], element_max_x, element_max_y)
            img = img.crop(element_box)
        return img

    def exclude_elements(self, img, web_elements):
        """Modify image hiding elements with a black rectangle

        :param img: image object
        :param web_elements: WebElement objects to be excluded
        """
        if web_elements and len(web_elements) > 0:
            img = img.convert("RGBA")
            pixel_data = img.load()

            for web_element in web_elements:
                element_box = self.get_element_box(web_element)
                for x, y in itertools.product(range(element_box[0], element_box[2]),
                                              range(element_box[1], element_box[3])):
                    try:
                        pixel_data[x, y] = (0, 0, 0, 255)
                    except IndexError:
                        pass

        return img

    def compare_files(self, image_path, baseline_path, threshold, file_suffix, filename):
        """Compare two image files, generate a new image file with highlighted differences,
           calculate the percentage of pixels that are different between both images and add result to the html report
        :param image_path: image file path
        :param baseline_path: baseline image file path
        :param threshold: percentage threshold
        :returns: result message
        """
        # Make two new images with same size
        with Image.open(image_path) as image:
            image_size = image.size
            with Image.open(baseline_path) as baseline:
                baseline_size = baseline.size
                max_size = (max(image.width, baseline.width), max(image.height, baseline.height))
                image_max = Image.new('RGB', max_size)
                image_max.paste(image.convert('RGB'))
                baseline_max = Image.new('RGB', max_size)
                baseline_max.paste(baseline.convert('RGB'))

        # Generate and save diff image
        diff_path = image_path.replace('.png', '.diff.png')
        diff_pixels_percentage = self.save_differences_image(image_max, baseline_max, diff_path)

        # Check differences and add to report
        if image_size != baseline_size:
            # Different size
            diff_message = f"Image dimensions {image_size} do not match baseline size {baseline_size}"
            exception_message = f"\nThe new screenshot '{image_path}' size '{image_size}' did not match the" \
                                f" baseline '{baseline_path}' size '{baseline_size}'"
            result = 'diff'
        elif diff_pixels_percentage == 0:
            # Equal images
            diff_path = diff_message = None
            result = 'equal'
        elif 0 < diff_pixels_percentage <= threshold:
            # Similar images
            diff_message = f'Distance is {diff_pixels_percentage:.8f}, less than {threshold} threshold'
            result = 'equal'
        else:
            # Different images
            diff_message = f'\nDistance is {diff_pixels_percentage:.8f}, more than {threshold} threshold'
            exception_message = f"\nThe new screenshot '{image_path}' did not match the baseline '{baseline_path}'" \
                                f" (by a distance of {diff_pixels_percentage:.8f}, more than {threshold} threshold)"
            result = 'diff'

        if result in ['equal', 'diff']:
            self._add_result_to_report(result, baseline_path, file_suffix, filename)
            # Add message to result to be used in unittests
            result = f'{result}-{diff_message}' if diff_message is not None else result

        # Prepare current image and diff path.
        current_image_path = path.relpath(image_path, self.output_directory).replace('\\', '/')
        if diff_path is not None:
            diff_path = path.relpath(diff_path, self.output_directory).replace('\\', '/')

        if Settings.VISUAL_TESTING.get('include_passed_tests') is False and not result.startswith('diff'):
            del self.results['scenario_results'][file_suffix]['screenshots'][filename]
        else:
            self.results['scenario_results'][file_suffix]['screenshots'][filename]['current'] = current_image_path
            self.results['scenario_results'][file_suffix]['screenshots'][filename]['diff'] = diff_path

        if result.startswith('diff'):
            logger.warning(f"Visual error in '{os.path.splitext(os.path.basename(baseline_path))[0]}':"
                           f" {diff_message}")
            if Settings.VISUAL_TESTING.get('fail') or self.force:
                raise TalosVisualTestingError(exception_message)

        return result

    @staticmethod
    def save_differences_image(image, baseline, diff_path):
        """Create and save an image showing differences between both images

        :param image: image object
        :param baseline: reference baseline image object
        :param diff_path: file path where difference image will be saved
        :returns: percentage of pixels that are different between both images
        """
        # Create a mask with differences
        mask = ImageChops.difference(image, baseline).convert('L').point(lambda x: 255 if x else 0)
        # Create a White base
        white_image = Image.new('RGB', baseline.size, (255, 255, 255))
        # Add baseline with 50% opacity
        baseline.putalpha(127)
        white_image.paste(baseline, (0, 0), baseline)
        # Add red points in different pixels
        red_image = Image.new('RGB', baseline.size, (255, 0, 0))
        white_image.paste(red_image, (0, 0), mask)
        # Save file
        white_image.save(diff_path)

        # Count different pixels (black pixels in mask image are equal pixels)
        equal_pixels = sum([1 for pixel in mask.getdata() if pixel == 0])
        diff_pixels_percentage = 1 - equal_pixels / (baseline.width * baseline.height)
        return diff_pixels_percentage

    def _add_result_to_report(self, result, baseline_path, file_suffix, filename):
        """Add the result of a visual test to the html report

        :param result: comparison result (equal, diff, baseline)
        :param baseline_path: baseline image file path
        """
        if Settings.VISUAL_TESTING.get('include_passed_tests'):
            self.results['total_results'][result] += 1
            self.results['scenario_results'][file_suffix][result] += 1
        else:
            if result == 'diff':
                self.results['total_results'][result] += 1
                self.results['scenario_results'][file_suffix][result] += 1

        if baseline_path is not None:
            output_baseline_path = os.path.join(self.output_directory, os.path.basename(baseline_path))
            shutil.copyfile(baseline_path, output_baseline_path)
            output_baseline_path = path.relpath(output_baseline_path, self.output_directory).replace('\\', '/')
            if result != 'diff':
                self.results['scenario_results'][file_suffix]['screenshots'][filename]['result'] = 'passed'
            # Save the baseline image
            self.results['scenario_results'][file_suffix]['screenshots'][filename]['baseline'] = output_baseline_path

    def generate_json_report(self):
        """
        Generate the json report for visual testing.
        :return:
        """
        with open(
                f"{Settings.BASE_PATH.get(force=True)}/output/visualtests/visual_tests.json", "w", encoding="utf-8"
        ) as f:
            f.write(json.dumps(self.results, indent=4))

    def generate_html_report(self):
        """
        Generate the html report for visual testing
        :return:
        """
        from arc.core.behave.env_utils import load_env_html
        env, _ = load_env_html()
        visual_template = env.get_template("visual_testing_template.html")
        self.results.update(
            {
                'navbar_title': "Visual Tests Report",
                'page_title': "Visual Tests Report"
            }
        )
        visual_template.stream(self.results).dump(
            f"{Settings.BASE_PATH.get(force=True)}/output/visualtests/visual_tests.html", encoding="utf-8"
        )

    @staticmethod
    def get_valid_filename(s, max_length=constants.FILENAME_MAX_LENGTH):
        """
        Get valid file name string from a current file name (s) with a file name max length.
        :param s:
        :param max_length:
        :return:
        """
        s = str(s).strip().replace(' -- @', '_')
        s = re.sub(r'(?u)[^-\w]', '_', s).strip('_')
        return s[:max_length]
