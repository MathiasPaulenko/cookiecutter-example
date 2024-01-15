# -*- coding: utf-8 -*-
"""
Page Elements init file.
"""
import logging

from arc.page_elements.button_page_element import Button
from arc.page_elements.checkbox_page_element import Checkbox
from arc.page_elements.group_page_element import Group
from arc.page_elements.input_radio_page_element import InputRadio
from arc.page_elements.input_text_page_element import InputText
from arc.page_elements.link_page_element import Link
from arc.page_elements.page_element import PageElement
from arc.page_elements.page_elements import PageElements, Groups
from arc.page_elements.page_elements import Texts, InputTexts, Selects, Buttons, Links, Checkboxes, InputRadios, Layers
from arc.page_elements.select_page_element import Select
from arc.page_elements.text_page_element import Text
from arc.page_elements.layer_page_element import Layer

logger = logging.getLogger(__name__)

logger.debug(f"Initialising Page Element Objects.")

__all__ = [
    'PageElement',
    'Text',
    'InputText',
    'Select',
    'Button',
    'Link',
    'Checkbox',
    'InputRadio',
    'Layer',
    'Group',
    'PageElements',
    'Texts',
    'InputTexts',
    'Selects',
    'Buttons',
    'Links',
    'Checkboxes',
    'InputRadios',
    'Groups',
    'Layers'
]
