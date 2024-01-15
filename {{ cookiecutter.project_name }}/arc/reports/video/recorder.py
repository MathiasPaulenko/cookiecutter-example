"""
Module for generating video reports of the executed scenarios
"""
import logging
import os
import threading
from datetime import timedelta
from io import BytesIO
from timeit import default_timer

from PIL import Image

from arc.core.test_method.exceptions import TalosNotThirdPartyAppInstalled
from selenium.common.exceptions import InvalidSessionIdException
from urllib3.exceptions import NewConnectionError, MaxRetryError

from arc.settings.settings_manager import Settings

logger = logging.getLogger(__name__)

try:
    import cv2  # noqa
    import numpy as np  # noqa
except ModuleNotFoundError:
    if Settings.PYTALOS_REPORTS.get('generate_video') and Settings.PYTALOS_REPORTS.get('generate_video').get('enabled'):
        msg = "Please install the opencv module to use this functionality."
        logger.error(msg)
        raise TalosNotThirdPartyAppInstalled(msg)


class Recorder:

    def __init__(self, **kwargs):
        self.driver = kwargs.get("driver", None)
        self.file_name = kwargs.get("file_name", "unnamed_file")
        self.video_format = kwargs.get("video_format", "mp4")
        self.fps = int(kwargs.get("fps", 5))
        self.record = False
        self.frames = []
        self.recorder_thread = None

    def stop_recording(self):
        """
            Stops the recorder and creates the video
        """
        if self.record:
            self.record = False
            self.recorder_thread.join()
            output_file = f"{self.file_name}.{self.video_format}"
            if hasattr(self, "frames"):
                self.write_frame_list_to_video_file(self.frames, output_file=output_file)
                self.validate_video_creation(output_file)
                delattr(self, "frames")

    def record_screen(self):
        """
            Begins screen recording utilizing attributes set on initialisation.
        """
        if self.driver is not None:
            logger.debug("Starting recording process...")
            self.record = True
            self.recorder_thread = threading.Thread(
                target=self.__record_function,
                name="Screen Recorder",
                args=[self.frames]
            )
            self.recorder_thread.start()

        else:
            logger.warning("Driver needs to be used as parameter")

    def __record_function(self, frames):
        """
            Private method triggered within an individual thread to handle screen recording separately
        :param frames: List acting as a container for byte strings representing screenshots
        :return: List of generated frames
        """
        # ignore blank frames on startup before window is loaded
        while not self.driver.current_url or self.driver.current_url == "data:,":
            pass
        while self.record:
            img = None
            try:
                img = self.driver.get_screenshot_as_png()
            except (InvalidSessionIdException, NewConnectionError, MaxRetryError) as ex:
                logger.debug(ex)
                message = f'Driver session ended: {ex}'
                logger.debug(message)

            if img is not None:
                frames.append(img)

        logger.debug("Recording finished...")
        return frames

    def write_frame_list_to_video_file(self, frames, height=None, width=None, output_file=None, overwrite=True):
        """
            Writes a list of image data in Bytes to video file
        :param frames: Bytes representing Image data
        :param height: Int representing height of video
        :param width: Int representing width of video
        :param output_file: String representing filename of output - mp4/avi
        :param overwrite: Boolean determining whether an existing file of the same name should be overwritten
        :return: None
        """
        logger.debug("Compiling screen recording.")
        if height is None or width is None:
            try:
                width, height = Image.open(BytesIO(frames[0])).size
            except (Exception,) as ex:
                logger.debug(ex)
                logger.warning("Could not determine video resolution, exiting function...")
                return None

        video_format = self.video_format
        if video_format.lower() == "mp4":
            video_format += "v"
        elif video_format.lower() == "avi":
            video_format = "divx"

        if os.path.exists(output_file):
            if overwrite:
                logger.debug(f"File '{output_file}' already exists, and will be overwritten.")
            else:
                logger.debug(f"File '{output_file}' already exists, and will NOT be overwritten, exiting function.")
                return None

        start = default_timer()
        out = cv2.VideoWriter(output_file, cv2.VideoWriter_fourcc(*video_format.lower()), self.fps, # noqa
                              (width, height))
        for frame in frames:
            try:
                img_obj = cv2.cvtColor(np.array(Image.open(BytesIO(frame))), cv2.COLOR_RGB2BGR)  # noqa
                out.write(img_obj)
            except (Exception,) as ex:
                logger.error(f"Unable to create Image from bytes: {ex}")
        out.release()
        cv2.destroyAllWindows()  # noqa
        end = default_timer()
        logger.debug(f"Video compilation complete - Duration: {str(timedelta(seconds=end - start))}")

    @staticmethod
    def validate_video_creation(output_file):
        """
            Validates video was created and is populated
        :param output_file: Filepath containing rendered video
        :return:
        """
        if not os.path.exists(output_file):
            logger.debug(f"File '{output_file}' was NOT created.")
        elif os.stat(output_file).st_size == 0:
            logger.debug(f"File '{output_file}' was created but is EMPTY.")
        else:
            logger.debug(f"File '{output_file}' has been created")
