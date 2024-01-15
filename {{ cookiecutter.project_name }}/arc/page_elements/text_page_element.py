# -*- coding: utf-8 -*-
"""
Text Page Element class file
"""
import logging

from arc.core.test_method.exceptions import TalosTestError
from arc.page_elements.page_element import PageElement

logger = logging.getLogger(__name__)


class Text(PageElement):
    """
    Text Page Element class, a subclass of PageElement.
    """

    @property
    def text(self):
        """
        Return web element text.
        :return:
        """
        try:
            return self.web_element.text
        except Exception as ex:
            logger.error(str(ex))
            raise TalosTestError(str(ex))
