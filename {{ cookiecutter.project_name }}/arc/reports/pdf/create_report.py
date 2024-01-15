import json
import os
import time
import logging

from copy import deepcopy

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Table, TableStyle
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph
from datetime import datetime
from arc.contrib.tools.formatters import replace_chars
from arc.contrib.utilities import load_translation
from arc.core.behave.template_var import replace_template_var
from arc.reports.html.utils import parse_url_params
from reportlab.lib.units import cm

from arc.settings.settings_manager import Settings

logger = logging.getLogger(__name__)

BASE_PATH = os.path.abspath(os.path.join(os.path.abspath(__file__), os.pardir)) + os.sep
PDF_PATH = os.path.join(Settings.REPORTS_PATH.get(force=True), 'pdf') + os.sep


class CreatePDF:
    document: Canvas
    total_width = 0
    total_height = 0
    current_height = 0
    reports = []
    driver_type = ""
    application_name = ""
    scenario_name = ""
    scenario_location = ""
    environment = ""
    logger.debug('Babel translation for documents reports loaded')
    gnu_translations = load_translation('docs_reports')
    _ = gnu_translations.gettext

    def generate_document_report(self, feature, global_data):
        """
        Generate document report depending on the global data.
        :param feature: feature information
        :param global_data: global data information
        :return reports: list with reports path created
        """
        logger.debug(f'Generating document pdf')
        self.driver_type = feature['driver']
        self.application_name = global_data['application']
        self.environment = global_data['environment']

        for scenario in feature['elements']:
            if scenario["type"] == 'scenario':
                logger.debug(f"Generating pdf evidence for scenario: {scenario['name']}")
                self.scenario_name = scenario['name']
                self.scenario_location = scenario['location']
                scenario_name = '%.100s' % self.scenario_name
                path = self.__get_pdf_path(replace_chars(scenario_name))
                if os.path.exists(path):
                    basename, ext = os.path.splitext(path)
                    index_location = str(self.scenario_location).rfind(':')
                    path = basename + f"_{self.scenario_location[index_location + 1:]}" + ext
                self.document = Canvas(path, pagesize=letter)
                self.document.setFontSize(10)
                width, height = letter
                self.total_width = width - 125
                self.total_height = height - 20
                self.current_height = self.total_height
                self.__print_header()
                self.__insert_space_len(20)
                testcase_name = self.scenario_name + ' - ' + str(self.driver_type).upper()
                self.__insert_text(f"{self._('Feature')}: {feature['name']}", 10, bold=True, italic=False)
                feature_description = ' '.join(feature.get('description', ''))
                self.__insert_space_len(20)
                self.__insert_text(f"{self._('Scenario')}: {testcase_name}", 10, bold=True, italic=False)
                scenario_description = ' '.join(scenario.get('description', ''))
                self.__insert_space_len(20)
                self.__generate_global_data_table(global_data)
                self.__insert_space_len(25)
                self.__generate_summary_table(scenario)
                self.__insert_space_len(25)
                self.__generate_description_table(f"{self._('Feature description')}:", feature_description)
                self.__generate_description_table(f"{self._('Scenario description')}:", scenario_description)
                self.__generate_total_step_table(scenario)
                self.__generate_pdf_body(scenario)
                self.document.save()
                self.reports.append(path)
                logger.debug(f'Document docx generated in path: {path}')
        return self.reports

    def __get_pdf_path(self, scenario_name):
        """
        Return pdf path
        :param scenario_name:
        :return path:
        :return:
        """
        path = str(PDF_PATH) + str(self.driver_type).upper() + "-" + replace_chars(scenario_name.__str__()) + ".pdf"
        return path

    def __print_header(self):
        """
        Set header in document
        :param:
        :return:
        """
        time = datetime.now().strftime("%d/%m/%Y")

        data = [['\n', Paragraph(self.application_name, ParagraphStyle(name='', alignment=TA_CENTER)), time]]
        new_table = Table(data, colWidths=[50, 350, 70])
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.grey),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ])
        new_table.setStyle(style)
        width, height = new_table.wrapOn(self.document, self.total_width, self.current_height)
        new_table.drawOn(self.document, 70, self.current_height - height)
        self.document.drawImage('arc/web/static/images/taloslogo.png', x=80, y=self.current_height - (height - 2), width=35,
                                height=25, mask='auto')
        page_num = self.document.getPageNumber()
        text = "Page %s" % page_num
        self.document.setFillColor(colors.grey)
        self.document.drawString(self.total_width / 2 + 20, 20, text)
        self.document.setFillColor(colors.black)
        self.current_height = self.current_height - height

    def __print_long_table(self, data, col_width, style):
        """
        print a table in document where a row is longer than a page
        :param data:
        :param col_width:
        :param style:
        :return:
        """
        first_iteration = True
        for row in data:
            if first_iteration:
                style.append(('BACKGROUND', (0, 0), (-1, -1), colors.white))
                first_iteration = False
            else:
                style.append(('BACKGROUND', (0, 0), (-1, 1), colors.whitesmoke))
            list_row = [row]
            table = Table(list_row, colWidths=col_width)
            table.setStyle(TableStyle(style))
            width, height = table.wrapOn(self.document, self.total_width, self.current_height)
            self.current_height = self.current_height - height
            if self.current_height < 60:
                self.document.showPage()
                self.current_height = self.total_height
                self.__print_header()
                self.__insert_space_len(20)
                self.current_height = self.current_height - height
                table.drawOn(self.document, 72, self.current_height)
            else:
                table.drawOn(self.document, 72, self.current_height)

    def __print_table(self, data, col_width, style):
        """
        print a table in document
        :param data:
        :param col_width:
        :param style:
        :return:
        """
        table = Table(data, colWidths=col_width)
        table.setStyle(TableStyle(style))
        data_len = len(data)
        height = 0
        for each in range(data_len):
            if each % 2 == 0:
                bg_color = colors.white
            else:
                bg_color = colors.whitesmoke
            table.setStyle(TableStyle([('BACKGROUND', (0, each), (-1, each), bg_color)]))

        if self.current_height < 70:
            self.document.showPage()
            self.current_height = self.total_height
            self.__print_header()
            self.__insert_space_len(20)
        table_split = table.splitOn(self.document, self.total_width, self.current_height - 60)
        if len(table_split) > 1:
            count = 0
            for current_table in table_split:
                width, height = current_table.wrapOn(self.document, self.total_width, self.current_height)
                current_table.drawOn(self.document, 72, self.current_height - height)
                if count < len(table_split) - 1:
                    self.document.showPage()
                    self.current_height = self.total_height
                    self.__print_header()
                    self.__insert_space_len(20)
                count += 1
            self.current_height = self.current_height - height
        else:
            width, height = table_split[0].wrapOn(self.document, self.total_width, self.current_height)
            table_split[0].drawOn(self.document, 72, self.current_height - height)
            self.current_height = self.current_height - height

    def __insert_text(self, text, size, bold=False, italic=False):
        """
        Insert in document a text and choosing normal, bold or italic
        :param text:
        :param size:
        :param bold:
        :param italic:
        :return:
        """
        if bold and italic:
            paragraph = Paragraph(
                f"<strong><i><font size={size}>{text}</font></i></strong>")
        elif bold:
            paragraph = Paragraph(
                f"<strong><font size={size}>{text}</font></strong>")
        elif italic:
            paragraph = Paragraph(
                f"<i><font size={size}>{text}</font></i>")
        else:
            paragraph = Paragraph(
                f"<font size={size}>{text}</font>")

        width, height = paragraph.wrapOn(self.document, self.total_width, self.current_height)
        paragraph.drawOn(self.document, 75, self.current_height - height)
        self.current_height = self.current_height - height

    def __insert_space_len(self, space_len):
        """
        Insert line breaks specifying the length of the space
        :param space_len:
        :return:
        """
        self.current_height = self.current_height - space_len
        if self.current_height < 30:
            self.current_height = self.total_height
            self.document.showPage()
            self.__print_header()

    def __split_long_text_rows(self, paragraph, data):
        """
        Read a long text, add break lines and store it
        in cells to split it in pages
        :param paragraph:
        :param data:
        :return:
        """
        lines = paragraph.text.split('<br/>')
        aux = deepcopy(self.current_height)
        current_line = 0
        index = 0
        count = 10
        text = ""
        while current_line < len(lines):
            text = '<br/>'.join(lines[index:index + count])
            word = Paragraph(text)
            width, height = word.wrapOn(self.document, self.total_width, self.total_height)
            aux = aux - height
            if aux < 168:
                index += count
                row = [Paragraph(text)]
                data.append(row)
                count = 30
                current_line += count
                aux = self.total_height
                text = None
            else:
                count += 1
                current_line += 1
                aux = aux + height
        if text is not None:
            row = [Paragraph(text)]
            data.append(row)
        return data

    def __generate_global_data_table(self, global_data):
        """
        Generate global data table in document.
        :param global_data:
        :return:
        """
        data = [
            [self._('Executed by user'),
             Paragraph(global_data['user_code'], ParagraphStyle(name='', alignment=TA_CENTER))],
            [self._('Business area'),
             Paragraph(global_data['business_area'], ParagraphStyle(name='', alignment=TA_CENTER))],
            [self._('Entity'), Paragraph(global_data['entity'], ParagraphStyle(name='', alignment=TA_CENTER))]]
        col_width = [235, 235]
        style = [("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                 ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                 ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]
        self.__print_table(data, col_width, style)

    def __generate_summary_table(self, scenario):
        """
        Generate summary table in document
        :param scenario:
        :return:
        """
        data = [[Paragraph(f"<a name='summary_table'/>{self._('Test Case Execution Summary')}",
                           ParagraphStyle(name='', alignment=TA_CENTER))],
                [self._('Result'), self._(str(scenario['status']).capitalize())],
                [self._('Number of steps'), scenario.get('total_steps', 0)],
                [self._('Correct steps'), scenario.get('steps_passed', 0)],
                [self._('Incorrect steps'), scenario.get('steps_failed', 0)],
                [self._('No Run steps'), scenario.get('steps_skipped', 0)],
                [self._('Start'), datetime.fromtimestamp(scenario.get('start_time', 0)).strftime("%d/%m/%Y %H:%M:%S")],
                [self._('End'), datetime.fromtimestamp(scenario.get('end_time', 0)).strftime("%d/%m/%Y %H:%M:%S")],
                [self._('Duration'), datetime.fromtimestamp(scenario.get('duration', 0)).strftime("%d/%m/%Y %H:%M:%S")],
                [self._('Execution Type'), str(self.driver_type).capitalize()],
                [self._('Environment'), str(self.environment).capitalize()]]
        col_width = [235, 235]
        style = [("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                 ('SPAN', (0, 0), (1, 0)),
                 ('TEXTCOLOR', (1, 1), (1, 1), self.__set_color_status(scenario['status'])),
                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                 ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                 ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)]
        self.__print_table(data, col_width, style)

    def __generate_description_table(self, title, description):
        """
        Generate a description in the table.
        :param title:
        :param description:
        :return:
        """
        data = [[title], [Paragraph(description)]]
        col_width = [470]
        style = [("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                 ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                 ('ALIGN', (0, 1), (1, -1), 'LEFT'),
                 ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)]
        self.__print_table(data, col_width, style)
        self.__insert_space_len(25)

    def __generate_total_step_table(self, scenario):
        """
        Generate total data information step table.
        :param scenario:
        :return:
        """
        steps = []
        for step in scenario['steps']:
            if not step.get('result'):
                step['result'] = {"status": 'skipped', 'duration': '-'}
            steps.append(step)
        data = [[self._('Steps'), self._('Description'), self._('Result'), self._('Duration')]]
        count_step = 1
        for current_step in steps:
            color = self.__set_color_status(current_step['result']['status'])
            if current_step['result']['status'] != 'skipped':
                link = f"<a href='#step_{count_step}'><font color='blue'>{self._('Step')} {count_step}</font></a>"
            else:
                link = f"<font color='blue'>{self._('Step')} {count_step}</font>"
            row = [Paragraph(link, ParagraphStyle(name='', alignment=TA_CENTER)),
                   Paragraph(current_step['name']),
                   Paragraph(
                       f"<font color='{color}'>{self._(str(current_step['result']['status']).capitalize())}</font>",
                       ParagraphStyle(name='', alignment=TA_CENTER))]
            if isinstance(current_step['result']['duration'], float):
                test_duration = time.strftime('%H:%M:%S', time.gmtime(current_step['result']['duration']))
            else:
                test_duration = current_step['result']['duration']
            row.append(test_duration)
            data.append(row)
            count_step += 1

        col_width = [50, 320, 50, 50]
        style = [("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                 ('ALIGN', (1, 1), (1, -1), 'LEFT'),
                 ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]
        self.__print_table(data, col_width, style)

    def __generate_pdf_body(self, scenario):
        """
        Generate document step information from scenario.
        :param scenario:
        :return:
        """
        count = 1
        for step in scenario['steps']:
            if step['result']['status'] != 'skipped':
                self.document.showPage()
                self.current_height = self.total_height
                self.__print_header()
                self.__insert_space_len(20)
                duration = datetime.fromtimestamp(step.get("start_time")).strftime("%d/%m/%Y %H:%M:%S")

                color = self.__set_color_status(step['result']['status'])
                data = [[Paragraph(f"<a name='step_{count}'/>{self._('Step')} {count}",
                                   ParagraphStyle(name='', alignment=TA_CENTER)),
                         Paragraph(f"<font color='{color}'>{self._(str(step['result']['status']).capitalize())}</font>",
                                   ParagraphStyle(name='', alignment=TA_CENTER)),
                         duration,
                         Paragraph(
                             f"<a href='#summary_table'><font color='blue'>{self._('Go to Summary Table')}</font></a>")]]
                col_width = [50, 50, 250, 120]
                style = [("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                         ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)]
                self.__print_table(data, col_width, style)
                self.__insert_space_len(25)
                self.__insert_text(f"{self._('Description')}:", 12, bold=True, italic=True)
                self.__insert_space_len(10)
                self.__insert_text(f'''{step['step_type']} {step['name']}''', 10, bold=False, italic=False)
                self.__insert_space_len(10)
                if step.get('text'):
                    self.__insert_text(step.get('text'), 10, bold=False, italic=True)
                    self.__insert_space_len(10)
                if step.get('table'):
                    data = []
                    headering = []
                    for header in step.get('table').get('headings'):
                        headering.append(Paragraph(replace_template_var(header)))
                    data.append(headering)
                    for row in step.get('table').get('rows'):
                        row_list = []
                        for current_row in row:
                            row_list.append(Paragraph(replace_template_var(current_row)))
                        data.append(row_list)
                    col_width = []
                    for _ in range(0, len(step.get('table').get('headings'))):
                        col_width.append(470 / len(step.get('table').get('headings')))
                    style = [("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                             ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                             ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                             ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]
                    self.__print_table(data, col_width, style)
                    self.__insert_space_len(10)
                self.__insert_space_len(25)
                self.__insert_text(f"{self._('Expected result')}:", 12, bold=True, italic=True)
                self.__insert_space_len(10)
                self.__insert_text(step.get('result').get('expected_result'), 10, bold=False, italic=False)
                self.__insert_space_len(25)
                self.__insert_text(f"{self._('Obtained result')}:", 12, bold=True, italic=True)
                self.__insert_space_len(10)
                self.__insert_text(step.get('result').get('obtained_result'), 10, bold=False, italic=False)
                self.__insert_space_len(25)
                if step.get('additional_text'):
                    self.__insert_text(f"{self._('Additional text')}:", 12, bold=True, italic=True)
                    self.__insert_space_len(10)
                    self.__insert_text('\n'.join(step.get('additional_text')), 10, bold=False, italic=False)
                self.__insert_space_len(20)
                self.__add_api_evidence_body(step)
                count += 1

                for screenshot in step['screenshots']:
                    if str(self.driver_type).lower() == "android" or str(self.driver_type).lower() == "ios":
                        width_screenshot = 10 * cm
                        height_screenshot = width_screenshot * 2
                    else:
                        width_screenshot = 18 * cm
                        height_screenshot = width_screenshot / 2

                    aux = self.current_height - height_screenshot
                    if aux < 60:
                        self.document.showPage()
                        self.current_height = self.total_height
                        self.__print_header()
                        self.__insert_space_len(20)
                    self.document.drawImage(screenshot, x=72, y=self.current_height - height_screenshot,
                                            width=width_screenshot, height=height_screenshot)
                    self.current_height = self.current_height - height_screenshot
                    self.__insert_space_len(10)

    def __add_api_evidence_body(self, step):
        """
        Add api evidences body to document from step.
        :param step:
        :return:
        """
        if step.get('jsons'):
            for inte in step.get("jsons"):
                if inte and str(inte) != "null":
                    api_evidence = inte
                    json_str = json.dumps(api_evidence['content'], indent=4)
                    json_str = json_str.replace('\n', '<br/>')
                    json_str = json_str.replace('    ', '&nbsp;&nbsp;&nbsp;&nbsp;')
                    data = [[Paragraph(f"<strong><font color='red'>{api_evidence['title']}</font></strong>")],
                            [Paragraph(json_str)]]
                    style = [("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                             ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)]
                    col_width = [470]
                    self.__print_table(data, col_width, style)
                    self.__insert_space_len(20)

        if step.get('api_info'):
            info_dict = step.get("api_info")
            url = info_dict.get("url")
            if params := info_dict.get('params'):
                url = parse_url_params(url, params)
            headers = json.dumps(info_dict.get("headers"), indent=4).replace('\\n', '$n')
            headers = headers.replace('\\', '')
            headers = headers.replace('"', '')
            headers = headers.replace('$n', '\n')
            headers = headers.replace('\n', '<br/>')
            headers = headers.replace('    ', '&nbsp;&nbsp;&nbsp;&nbsp;')

            body = json.dumps(info_dict.get("body"), indent=4).replace('\\n', '$n')
            body = body.replace('\\', '')
            body = body.replace('"', '')
            body = body.replace('$n', '\n')
            body = body.replace('\n', '<br/>')
            body = body.replace('    ', '&nbsp;&nbsp;&nbsp;&nbsp;')

            data = [[Paragraph(f"<strong><font color='red'>{self._('Request Info')}</font></strong>")],
                    ['URL', Paragraph(url)],
                    [self._("Method"), Paragraph(str(info_dict.get("method")).upper())],
                    [self._("Status Code"),
                     Paragraph(str(info_dict.get("status_code")) + " " + info_dict.get("reason"))],
                    [self._("Remote Address"), Paragraph(str(info_dict.get("remote Address")))],
                    [self._("Request headers"), Paragraph(headers)],
                    [self._("Request body"), Paragraph(body)]]
            style = [("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                     ('SPAN', (0, 0), (1, 0)),
                     ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)]
            col_width = [235, 235]
            self.__print_table(data, col_width, style)
            self.__insert_space_len(20)

        if step.get("response_headers"):
            self.__insert_space_len(20)
            response = json.dumps(step.get('response_headers'), indent=4).replace('\\n', '$n')
            response = response.replace('\\', '')
            response = response.replace('"', '')
            response = response.replace('$n', '\n')
            response = response.replace('\n', '<br/>')
            response = response.replace('    ', '&nbsp;&nbsp;&nbsp;&nbsp;')
            data = [[Paragraph(f"<strong><font color='red'>{self._('Response headers')}</font></strong>")],
                    [Paragraph(response)]]
            style = [("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                     ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)]
            col_width = [470]
            self.__print_table(data, col_width, style)
            self.__insert_space_len(20)

        if step.get("response_content"):
            response = json.dumps(step.get('response_content'), indent=4).replace('\\n', '$n')
            response = response.replace('\\', '')
            response = response.replace('"', '')
            response = response.replace('$n', '\n')
            response = response.replace('\n', '<br/>')
            response = response.replace('    ', '&nbsp;&nbsp;&nbsp;&nbsp;')
            data = [[Paragraph(f"<strong><font color='red'>{self._('Response content')}</font></strong>")]]
            data = self.__split_long_text_rows(Paragraph(response), data)
            style = [("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                     ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)]
            col_width = [470]
            self.__print_long_table(data, col_width, style)
            self.__insert_space_len(20)

        if step.get('unit_tables'):
            for dictionary in step.get("unit_tables"):
                self.__insert_space_len(20)
                dictionary = deepcopy(dictionary)
                data = [[Paragraph(f"<strong><font color='red'>{dictionary.get('title')}</font></strong>")]]
                for key in dictionary.keys():
                    if key == 'result':
                        color = self.__set_color_status(str(dictionary.get(key)))
                        text = f"<font color='{color}'>{self._(str(dictionary.get(key)))}</font>"
                    elif key != 'title':
                        text = f"<font>{str(dictionary.get(key))}</font>"
                    else:
                        text = None
                    if text is not None:
                        row = [Paragraph(key), Paragraph(text)]
                        data.append(row)
                style = [("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                         ('SPAN', (0, 0), (1, 0)),
                         ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)]
                col_width = [235, 235]
                self.__print_table(data, col_width, style)
                self.__insert_space_len(20)

    @staticmethod
    def __set_color_status(status):
        """
        Format with color status info.
        :param status:
        :return:
        """
        if str(status).lower() == 'passed':
            return colors.green
        elif str(status).lower() == 'failed':
            return colors.red
        else:
            return colors.blue
