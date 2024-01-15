import json
import os

from arc.settings.settings_manager import Settings


class ErrorReport:
    """
        The following class contains all the elements needed to create json and html error reports
    """

    def __init__(self, talos_report, env, _):
        """
        This class manage the report generation
        :param talos_report
        :param env
        :param _
        """
        self.talos_report = talos_report
        self.env = env
        self._ = _
        self.list_error_report = []
        self.errors_path = os.path.join(Settings.OUTPUT_PATH.get(force=True), 'reports', 'errors')

    def generate_execution_errors_report(self):
        """
        Function that calls the html and json report generators
        """
        self._generate_json_report()
        self._generate_html_report()

    def _generate_json_report(self):
        """
        generate json report of errors in output/reports/errors
        """
        features = self.talos_report.get('features', None)
        steps_failed = []
        scenarios_failed = []
        for feature in features:
            if feature.get('status', '') == 'failed':
                scenarios = feature.get('elements', None)
                for scenario in scenarios:
                    if scenario.get('type', '') != 'background':
                        if scenario.get('status', '') == 'failed':
                            steps = scenario.get('steps', None)
                            for step in steps:
                                if step.get('result'):
                                    if step.get('result').get('status') == 'failed':
                                        steps_failed.append({'name': step.get('name'),
                                                             'error': step.get('result').get('error_message')
                                                             })
                            scenarios_failed.append({'name': scenario.get('name'),
                                                     'steps': steps_failed})
                            steps_failed = []

                self.list_error_report.append({
                    'feature_name': feature.get('name'),
                    'scenarios': scenarios_failed
                })
                scenarios_failed = []
        if os.path.exists(self.errors_path) is False:
            os.makedirs(self.errors_path)
        with open(os.path.join(self.errors_path, 'talos_errors.json'), 'w') as file:
            json.dump(self.list_error_report, file)

    def _generate_html_report(self):
        """
        generate html report of errors in output/reports/errors
        """
        global_template = self.env.get_template("global_template_errors.html")
        categorization_tags = {}

        if Settings.PYTALOS_REPORTS.get('generate_error_report').get('categorization').get('enabled', False):
            list_tags = Settings.PYTALOS_REPORTS.get('generate_error_report').get('categorization').get('tags')
            for feature in self.list_error_report:
                for scenario in feature.get('scenarios', []):
                    for step in scenario.get('steps', []):
                        if step.get('error').split(':')[0] in list_tags:
                            tag = step.get('error').split(':')[0]
                        else:
                            tag = 'NOT CLASSIFIED'

                        if tag not in categorization_tags:
                            categorization_tags[tag] = {}
                        if feature.get('feature_name') not in categorization_tags[tag]:
                            categorization_tags[tag][feature.get('feature_name')] = {}
                        if scenario.get('name') not in categorization_tags[tag][feature.get('feature_name')]:
                            categorization_tags[tag][feature.get('feature_name')][scenario.get('name')] = {'steps': []}

                        categorization_tags[tag][feature.get('feature_name')][scenario.get('name')]['steps'].append(
                            step)

        data = {
            "page_title": f"{self._('Global Report')}",
            "navbar_title": f"{self._('Global Report')}",
            "features": self.list_error_report,
            "categorization_tags": categorization_tags
        }

        global_template.stream(data).dump(os.path.join(self.errors_path, "global_errors.html"))
