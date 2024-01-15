"""
Wrapper developed for handling, managing and obtaining information from PDF files within TalosBDD.
With this Wrapper you can obtain information from the pages of a PDF, such as the page number, text, images, to make
use of this information in test cases or perform tests of the document itself.
This module is a PyMuPDF wrapper, to which we have added extra functionalities for greater
optimization and obtaining information.
"""

import io
import logging

from PIL import Image

from arc.core.test_method.exceptions import TalosNotThirdPartyAppInstalled

logger = logging.getLogger(__name__)

try:
    import fitz  # noqa
    from fitz import Rect  # noqa
except ModuleNotFoundError:
    msg = "Please install the PyMuPDF module to use this functionality"
    logger.error(msg)
    raise TalosNotThirdPartyAppInstalled(msg)


class PDFWrapper:
    """
    Wrapper for managing and extracting information from PDF.
    """

    def __init__(self, file_path):
        """
        The PDFWrapper object must be instantiated by passing the relative path of the PDF file to which we
        want to have information.
        :param file_path:
        """
        self.file_path = file_path
        logger.info(f'Opening PDF file in: {self.file_path}')
        self.doc = fitz.open(self.file_path)

    # Working with the document
    def close(self):
        """
        Method to close the stream to the pdf file.
        """
        logger.info('Closing PDF file')
        self.doc.close()

    def get_all_markers(self) -> list:
        """
        Returns all marks in the pdf file.
        """
        markers = self.doc.get_toc()
        return markers

    def get_page_count(self) -> int:
        """
        Returns the total number of pages in the PDF file.
        """
        page_count = self.doc.page_count
        logger.info(f'Getting PDF page count: {page_count}')
        return page_count

    def get_chapter_count(self) -> int:
        """
        Returns the total number of chapters in the PDF file.
        """
        count = self.doc.chapter_count
        logger.info(f'Getting PDF chapter count: {count}')
        return count

    def get_last_location(self):
        """
        Returns the last location received.
        :rtype tuple:
        """
        last_location = self.doc.last_location
        logger.info(f'Getting PDF last location: {last_location}')
        return last_location

    def prev_location(self, page_index):
        """
        Returns the location of the previous page.
        :param page_index:
        :rtype tuple:
        """
        prev_location = self.doc.prev_location(page_id=page_index)
        logger.info(f'Getting PDF previous location: {prev_location}')
        return prev_location

    def next_location(self, page_index):
        """
        Returns the location of the next page.
        :param page_index:
        :rtype tuple:
        """
        next_location = self.doc.prev_location(page_id=page_index)
        logger.info(f'Getting PDF next location: {next_location}')
        return next_location

    def location_from_page_number(self, page_index):
        """
        Returns the location of a page.
        :param page_index:
        :rtype tuple:
        """
        location = self.doc.location_from_page_number(page_index)
        logger.info(f'Getting location from page number {page_index}: {location}')
        return location

    def page_number_from_location(self, page_location: tuple):
        """
        Returns the page number from the location.
        :param page_location:
        :rtype int:
        """
        page_number = self.doc.page_number_from_location(page_location)
        logger.info(f'Getting page number from location {page_location}: {page_number}')
        return page_number

    def get_catalog(self):
        """
        Returns the numbers of catalog.
        :rtype int:
        """
        logger.info('Getting catalog from PDF file')
        catalog = self.doc.pdf_catalog()
        return catalog

    def is_pdf(self):
        """
        Indicates with a Boolean if the file is a pdf.
        :rtype bool:
        """
        is_pdf = self.doc.is_pdf
        logger.info(f"Checking if file is a PDF file: {is_pdf}")
        return is_pdf

    def get_all_fonts(self, full=False):
        """
        Returns information from all sources used in the file.
        :param full:
        :rtype list:
        """
        logger.info('Getting all fonts from PDF file.')
        fonts = []
        for page_index in range(len(self.doc)):
            fonts.append(self.doc.get_page_fonts(page_index, full))

        return fonts

    def get_page_fonts(self, page_index, full=False):
        """
        Returns information from the fonts used on the indicated page.
        :param page_index:
        :param full:
        :return list:
        """
        logger.info(f'Getting fonts from page number {page_index}')
        return self.doc.get_page_fonts(page_index, full)

    # Working with pages
    def get_page_display_rect(self, page_index, annotations: int = 1):
        """
        Returns the location of the displays.
        :param page_index:
        :param annotations:
        :return list:
        """
        logger.info(f"Getting display rect from page number: {page_index}")
        page = self.doc[page_index]
        display_list = page.get_displaylist(annotations)

        return display_list.rect

    def get_page_rotation(self, page_index):
        """
        Returns the current rotation of the file, which can be 0, 90, 180, or 270.
        :param page_index:
        :return int:
        """
        page = self.doc[page_index]
        rotation = page.rotation
        logger.info(f"Getting page rotation from page number {page_index}: {rotation}")
        return rotation

    # Working with images
    def convert_all_pages_to_img(self, target_path, prefix='', ext='png'):
        """
        Convert all pdf pages into image files
        :param target_path:
        :param prefix:
        :param ext:
        """
        logger.info(f"Converting all pages to img {ext} in path {target_path}")
        for page in self.doc:
            pix = page.get_pixmap()
            pix.save(f"{target_path}{prefix}page-{str(page.number)}.{ext}")

    def convert_pages_to_img(self, page_index: int, target_path, prefix='', ext='png'):
        """
        Converts a specified page into a image file.
        :param page_index:
        :param target_path:
        :param prefix:
        :param ext:
        """
        logger.info(f"Converting page {page_index} to img {ext} in path {target_path}")
        page = self.doc[page_index]
        pix = page.get_pixmap()
        pix.save(f"{target_path}{prefix}page-{str(page.number)}.{ext}")

    def extract_all_img(self, target_path, prefix=''):
        """
        Extract all images from the PDF into image files.
        :param target_path:
        :param prefix:
        """
        logger.info(f"Extracting all img in path {target_path}")
        for page_index in range(len(self.doc)):
            page = self.doc[page_index]
            image_list = page.get_images()
            for image_index, img in enumerate(image_list, start=1):
                xref = img[0]
                base_image = self.doc.extract_image(xref)
                image_bytes = base_image["image"]
                image = Image.open(io.BytesIO(image_bytes))
                image_ext = base_image["ext"]
                image.save(open(f"{target_path}{prefix}image{page_index}_{image_index}.{image_ext}", "wb"))

    def extract_img_from_page(self, page_index: int, target_path, prefix=''):
        """
        Extracts all images from a PDF page into image files.
        :param page_index:
        :param target_path:
        :param prefix:
        """
        logger.info(f"Extracting all img in page {page_index} in path {target_path}")
        page = self.doc[page_index]
        image_list = page.get_images()
        for image_index, img in enumerate(image_list, start=1):
            xref = img[0]
            base_image = self.doc.extract_image(xref)
            image_bytes = base_image["image"]
            image = Image.open(io.BytesIO(image_bytes))
            image_ext = base_image["ext"]
            image.save(open(f"{target_path}{prefix}image{page_index + 1}_{image_index}.{image_ext}", "wb"))

    def insert_img_in_page(self, page_index, img_path, target_path, rect):
        """
        Inserts an indicated image on the indicated page of the PDF.
        :param page_index:
        :param img_path:
        :param target_path:
        :param rect:
        """
        page = self.doc[page_index]
        img = open(img_path, "rb").read()
        rect = Rect(rect)
        page.insert_image(rect, stream=img)
        self.doc.save(target_path)

    def get_images(self, full=False):
        """
        Returns the information for all images in the PDF.
        :param full:
        :return list:
        """
        logger.info('Getting the information for all images in PDF file')
        images = []
        for page in self.doc:
            images.append(page.get_images(full))
        return images

    def get_images_page(self, page_index, full=False):
        """
        Returns the information for all images on a page in the PDF.
        :param page_index:
        :param full:
        :return list:
        """
        logger.info(f"Getting information about img in page {page_index}")
        page = self.doc[page_index]
        images = page.get_images(full)
        return images

    # Working with texts
    def get_all_text(self):
        """
        Returns all text in the PDF.
        :return str:
        """
        logger.info('Getting all text in PDF file')
        text = ''
        for page in self.doc:
            text += page.get_text()

        return text

    def get_all_text_info(self):
        """
        Returns all the information in the text in the PDF.
        :return list:
        """
        logger.info("Getting all information about text in PDF")
        text = []
        for page in self.doc:
            text.append(page.get_text('words'))
        return text

    def get_page_text(self, page_index: int):
        """
        Returns the text of an indicated page in the PDF.
        :param page_index:
        :return str:
        """
        logger.info(f"Getting text from page {page_index}")
        page = self.doc[page_index]
        texts = page.get_text()
        return texts

    def get_page_text_info(self, page_index: int):
        """
        Returns all text information for an indicated page of the PDF.
        :param page_index:
        :return str:
        """
        logger.info(f"Getting information about text from page {page_index}")
        page = self.doc[page_index]
        texts = page.get_text('words')

        return texts

    def get_text_areas(self, text):
        """
        Returns information about the location of text passed by parameter.
        This method will search for all concurrency, and list its location within the PDF.
        :param text:
        :return list:
        """
        logger.info(f"Getting information about the location of the text: {text}")
        areas = []
        for page in self.doc:
            area = page.search_for(text)
            if area:
                areas.append(page.search_for(text))

        return areas

    def get_text_areas_in_page(self, page_index, text):
        """
        Returns information about the location of text passed by parameter.
        This method will search for all the concurrent and will list its location within the indicated page of the PDF.
        :param page_index:
        :param text:
        :return list:
        """
        logger.info(f"Get information about the location of te text in page {page_index}: {text}")
        areas = []
        page = self.doc[page_index]
        area = page.search_for(text)
        if area:
            areas.append(page.search_for(text))
        return areas

    # Working with drawings
    def get_all_drawings(self):
        """
        Returns information from the drawings in the PDF.
        :return list:
        """
        logger.info('Getting all drawing in PDF file')
        drawings = []
        for page in self.doc:
            drawings.append(page.get_drawings())

        return drawings

    def get_page_drawings(self, page_index: int):
        """
        Returns information from drawings on a page in the PDF.
        :param page_index:
        :return list:
        """
        logger.info(f"Getting all drawing from page {page_index}")
        page = self.doc[page_index]
        drawings = page.get_drawings()
        return drawings

    # Working with contents
    def get_all_contents(self):
        """
        Returns all contents of the PDF document.
        :return list:
        """
        logger.info(f"Getting all context of the PDF file")
        contents = []
        for page in self.doc:
            contents.append(page.get_contents())
        return contents

    def get_page_contents(self, page_index: int):
        """
        Returns all contents of the specified page of the PDF document.
        :param page_index:
        :return:
        """
        logger.info(f"Getting all contents from page: {page_index}")
        page = self.doc[page_index]
        contents = page.get_contents()
        return contents

    def get_all_contents_read(self):
        """
        Returns all contents read in binary fashion from of the PDF document.
        :return list:
        """
        logger.info('Getting all contests in binary fashion')
        contents = []
        for page in self.doc:
            contents.append(page.read_contents())
        return contents

    def get_page_contents_read(self, page_index: int):
        """
        Returns all contents read in binary fashion from the indicated page of the PDF document.
        :param page_index:
        :return list:
        """
        logger.info(f'Getting all contests in binary fashion in page {page_index}')
        page = self.doc[page_index]
        contents = page.read_contents()
        return contents

    def get_all_text_trace(self):
        """
        Returns the trace information of the text contained in the PDF file.
        :return list:
        """
        logger.info("Getting all traces in PDF file")
        traces = []
        for page in self.doc:
            traces.append(page.get_texttrace())
        return traces

    def get_page_text_trace(self, page_index):
        """
        Returns the trace information of the text contained in a page in the PDF file.
        :param page_index:
        :return list:
        """
        logger.info(f"Getting page text trace from page: {page_index}")
        page = self.doc[page_index]
        traces = page.get_texttrace()
        return traces

    # Working with metadata and markers, widgets and annotations
    def get_metadata(self):
        """
        Returns the metadata of the PDF file such as the date of creation, the author, date of modification,
        the format, among other information.
        :return:
        """
        metadata = self.doc.metadata
        logger.info(f"Getting all metadata of PDF file: {metadata}")
        return metadata

    def needs_pass(self):
        """
        Returns whether the pdf file requires a password.
        :return bool:
        """
        is_needs = self.doc.needs_pass
        logger.info(f"Checking if PDF file need password: {is_needs}")
        return is_needs

    def get_language(self):
        """
        Returns the language of the PDF file.
        :return str:
        """
        language = self.doc.language
        logger.info(f"Getting language of PDf file: {language}")
        return language

    def get_permissions(self):
        """
        Returns the identification number of the permissions that the PDF file has.
        : int:
        """
        permissions = self.doc.permissions
        logger.info(f"Getting permission of PDF file: {permissions}")
        return permissions

    # noinspection DuplicatedCode
    @staticmethod
    def _get_widget_object(widgets, store):
        """
        Fill in the list of dictionaries for informational data in the PDF file widget.
        :param widgets:
        :param store:
        :return list:
        """
        for wg in widgets:
            store.append({
                "this_own": wg.thisown,
                "border_color": wg.border_color,
                "border_style": wg.border_style,
                "border_width": wg.border_width,
                "border_dashes": wg.border_dashes,
                "choice_values": wg.choice_values,
                "field_name": wg.field_name,
                "field_label": wg.field_label,
                "field_value": wg.field_value,
                "field_flags": wg.field_flags,
                "field_display": wg.field_display,
                "field_type": wg.field_type,
                "field_type_string": wg.field_type_string,
                "fill_color": wg.fill_color,
                "button_caption": wg.button_caption,
                "is_signed": wg.is_signed,
                "text_color": wg.text_color,
                "text_font": wg.text_font,
                "text_fontsize": wg.text_fontsize,
                "text_max_len": wg.text_maxlen,
                "text_format": wg.text_format,
                "rect": wg.rect,
                "xref": wg.xref

            })

        return store

    def get_all_widget_info(self):
        """
        Returns information about the widgets in the PDF file.
        :return list:
        """
        logger.info("Getting all widget information in PDF file")
        widgets = []
        for page in self.doc:
            widget = page.widgets()
            widgets = self._get_widget_object(widget, widgets)
        return widgets

    def get_page_widget_info(self, page_index):
        """
        Returns information about the widgets in a page in the PDF file.
        :param page_index:
        :return:
        """
        logger.info(f"Getting all widget info in page {page_index}")
        page = self.doc[page_index]
        widgets = []
        widget = page.widgets()
        widgets = self._get_widget_object(widget, widgets)

        return widgets

    # noinspection DuplicatedCode
    @staticmethod
    def _get_annotation_object(annotations, store):
        """
        Fill in the list of dictionaries for informational data in the PDF file annotations.
        :param annotations:
        :param store:
        :return list:
        """
        for annotation in annotations:
            store.append({
                "this_own": annotation.thisown,
                "border_color": annotation.border_color,
                "border_style": annotation.border_style,
                "border_width": annotation.border_width,
                "border_dashes": annotation.border_dashes,
                "choice_values": annotation.choice_values,
                "field_name": annotation.field_name,
                "field_label": annotation.field_label,
                "field_value": annotation.field_value,
                "field_flags": annotation.field_flags,
                "field_display": annotation.field_display,
                "field_type": annotation.field_type,
                "field_type_string": annotation.field_type_string,
                "fill_color": annotation.fill_color,
                "button_caption": annotation.button_caption,
                "is_signed": annotation.is_signed,
                "text_color": annotation.text_color,
                "text_font": annotation.text_font,
                "text_fontsize": annotation.text_fontsize,
                "text_max_len": annotation.text_maxlen,
                "text_format": annotation.text_format,
                "rect": annotation.rect,
                "xref": annotation.xref

            })

        return store

    def get_all_annotations_info(self):
        """
        Returns information about the annotations in the PDF file.
        :return list:
        """
        logger.info('Getting all information about annotations in PDF file')
        annotations = []
        for page in self.doc:
            annotation_list = page.annots()
            annotations = self._get_annotation_object(annotation_list, annotations)

        return annotations

    def get_page_annotations_info(self, page_index):
        """
        Returns information about the annotations in a page in the PDF file.
        :param page_index:
        :return list:
        """
        logger.info(f"Getting all information about annotations in page {page_index}")
        page = self.doc[page_index]
        annotations = []
        annotation_list = page.annots()
        annotations = self._get_annotation_object(annotation_list, annotations)
        return annotations


def get_paper_size(paper_type):
    """
    Returns the size parameters of the type of sheet that has been passed to the parameter.
    :param paper_type:
    :return tuple:
    """
    logger.info(f"Getting paper size for paper type: {paper_type}")
    return fitz.paper_size(paper_type)


def get_paper_sizes():
    """
    Returns information about the page size of the PDF file.
    :return dict:
    """
    logger.info("Get information about paper size of the PDF file.")
    return fitz.paper_sizes()


def get_paper_rect(paper_type):
    """
    Returns the rectangle measurements of the sheet type passed by parameter.
    :param paper_type:
    :return Rect:
    """
    logger.info(f"Get information bout paper rect from paper type: {paper_type}")
    return fitz.paper_rect(paper_type)


def get_table_made(rect, col, rows):
    """
    Returns the table made earlier. It returns its location to us.
    :param rect:
    :param col:
    :param rows:
    :return:
    """
    logger.info(f"Getting table made location from col {col} and row {rows}")
    rect = Rect(rect)
    return fitz.make_table(rect, cols=col, rows=rows)


def get_font_descriptors():
    """
    It returns the description of the fonts used in PDF files.
    :return dict:
    """
    logger.info("Getting fonts information descriptors")
    return fitz.fitz_fontdescriptors


def get_pdf_color():
    """
    Returns the colors used in PDF files.
    :return dict:
    """
    logger.info("Getting PDF file color information")
    return fitz.pdfcolor


def get_pdf_timestamp():
    """
    Returns in Date format the timestamp of the PDF files.
    :return str:
    """
    logger.info("Getting PDF file timestamp information")
    return fitz.get_pdf_now()


def get_image_profile(image_path):
    """
    It returns the profile information of an image passed by parameter.
    :param image_path:
    :return dict:
    """
    logger.info(f"Getting image profile information for image: {image_path}")
    return fitz.image_profile(open(image_path, "rb").read())


def get_pdf_convert_str(text):
    """
    Returns the conversion of a string to string type PDF file.
    :param text:
    :return str:
    """
    logger.info(f"Getting PDF convert str: {text}")
    return fitz.get_pdf_str(text)
