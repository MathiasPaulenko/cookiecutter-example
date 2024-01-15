# -*- coding: utf-8 -*-
"""
Utility files for running accessibility tests with Axe Core.
"""
import json
import logging
import os
from datetime import datetime

from arc.contrib.utilities import get_valid_filename
from arc.settings.settings_manager import Settings

logger = logging.getLogger(__name__)


def write_results(data, name="results.json"):
    """
    This function generates a json with the analysis data passed by parameter.
    :param data:
    :param name:
    """
    accessibility_folder = os.path.join(Settings.REPORTS_PATH.get(force=True), 'accessibility')

    if os.path.isdir(accessibility_folder) is False:
        os.mkdir(accessibility_folder)
    name = get_valid_filename(name)
    name = f"{name}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.json"
    filepath = os.path.join(accessibility_folder, name)
    with open(filepath, "w", encoding="utf8") as f:
        f.write(json.dumps(data, indent=4))
        logger.info(f'Accessibility test json result created in path: {filepath}')

    return filepath, name


def get_nodes(string, violation, count):
    """
    Returns reporting information for accessibility error nodes.
    :param string:
    :param violation:
    :param count:
    """
    for node in violation["nodes"]:
        for target in node["target"]:
            string += "\n\t" + str(count) + ") Target: " + target
            count += 1
        for item in node["all"]:
            string += "\n\t\t" + item["message"]
        for item in node["any"]:
            string += "\n\t\t" + item["message"]
        for item in node["none"]:
            string += "\n\t\t" + item["message"]
    return string


def report(violations):
    """
    This function returns the accessibility analysis information in dictionary format.
    :param violations:
    """
    string = ""
    string += "Found " + str(len(violations)) + " accessibility violations:"
    for violation in violations:
        string += (
                "\n\n\nRule Violated:\n"
                + violation["id"]
                + " - "
                + violation["description"]
                + "\n\tURL: "
                + violation["helpUrl"]
                + "\n\tImpact Level: "
                + violation["impact"]
                + "\n\tTags:"
        )
        for tag in violation["tags"]:
            string += " " + tag
        string += "\n\tElements Affected:"
        i = 1
        string = get_nodes(string, violation, i)
        string += "\n\n\n"
        logger.debug(f'Reporting accessibility violation: {string}')

    return string


def evidence_accessibility_violations(context, violations):
    """
    Create evidence tables for each violation of accessibility rules.
    """
    for violation in violations:
        nodes = violation['nodes']
        logger.debug(f'Reporting accessibility violation: {violation}')
        for node in nodes:
            target = ''
            target += ', '.join(node['target'])
            summary = node['failureSummary']

            context.func.evidences.add_custom_table(
                title=f"Rule {violation['id']} in {target}",
                id=violation['id'],
                target=target,
                impact=violation['impact'],
                description=violation['description'],
                help=violation['help'],
                url=violation['helpUrl'],
                summary=summary,
            )
