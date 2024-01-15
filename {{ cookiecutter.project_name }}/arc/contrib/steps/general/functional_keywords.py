"""
Funcional Default Keywords
Default steps for use in Gherkin features.
In each step there is the documentation of what it is for and how to use it, as well as an example.
In some steps, not only is the desired operation performed, but it also adds extra information to the Word evidence.

List of steps:
######################################################################################################################
time sleep by {seconds} seconds


"""
import time
from behave import use_step_matcher, step

use_step_matcher("re")


#######################################################################################################################
#                                                Python Steps                                                         #
#######################################################################################################################
@step(u"time sleep by '(?P<seconds>.+)' seconds")
def time_sleep_by_seconds(context, seconds):
    """
    Wait for N seconds passed by parameter
    :example

        When time sleep by '10' seconds

    :
    :tag Python Steps:
    :param context:
    :param seconds:
    :return:
    """
    time.sleep(float(seconds))
