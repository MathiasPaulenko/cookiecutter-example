# -*- coding: utf-8 -*-
"""
Module with parsing functionalities and formatters useful for testing.
"""
import logging
import re

logger = logging.getLogger(__name__)


def replace_chars(text, new_char=""):
    """
    Replace chars from text passed by parameter.
    :param text:
    :param new_char:
    :return:
    """
    logger.debug(f"Replace chars: {new_char} in text: {text}")
    text = re.sub(r"[^À-úa-zA-Z0-9-_ ]+", new_char, text)
    return text.strip()
