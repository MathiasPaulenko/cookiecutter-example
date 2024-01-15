# -*- coding: utf-8 -*-
"""
TalosBDD executions handler configuration file.
In this file there are classes and functions for handling and configuring the execution of Talos.
In addition to the wrapper for certain Behave classes for the increase of functionalities and optimization.
"""
import os
import sys
import logging
from multiprocessing import Pool
import re

from behave.__main__ import run_behave
from behave._types import ExceptionUtil  # noqa
from behave.capture import CaptureController
from behave.formatter._registry import make_formatters  # noqa

from behave.runner import Runner
from arc.core.behave.context_utils import Context
from behave.runner_util import parse_features
from behave.step_registry import registry as the_step_registry  # noqa

from arc.core.behave.configuration import BehaveConfiguration
from arc.core.behave.env_utils import check_features_order
from arc.core.behave.parallel import (
    run_browsers_parallel, parse_parallel_schema_args,
    parse_parallel_browsers_args, run_scenarios_parallel, parse_parallel_scenarios_args, run_features_parallel,
    parse_parallel_features_args, parse_parallel_environments_args, run_environments_parallel,
    parse_parallel_scenarios_browser_args, run_scenarios_browsers_parallel, ENVIRONMENTS, BROWSERS, SCENARIOS, FEATURES,
    MULTI_BROWSERS_SCENARIOS
)
from arc.core.paths.directories import get_steps_dir, import_default_steps_dir
from arc.environment import after_execution, before_execution
from arc.reports.custom_formatters import get_json_report_args
from arc.settings.settings_manager import Settings
from arc.web.app.utils import send_alert_portal, print_portal_console
from behave.model import ScenarioOutline

try:
    from settings import settings
except (Exception,):
    from arc.settings import settings

logger = logging.getLogger(__name__)

ERROR_HOOK_MSG = []
SCENARIOS_RUN = []


class CustomModelRunner(Runner):
    """
    The definition class of the execution model.
    Subclass of Behave Runner class.
    """

    def __init__(self, config, features=None, step_registry=None):
        super(CustomModelRunner, self).__init__(config)
        self.config = config
        self.features = features or []
        self.hooks = {}
        self.formatters = []
        self.undefined_steps = []
        self.step_registry = step_registry
        self.capture_controller = CaptureController(config)

        self.context = None
        self.feature = None
        self.hook_failures = 0

    def run_hook(self, name, context, *args):
        """
        Execution of the hooks of behave.
        :param name:
        :param context:
        :param args:
        :return:
        """
        logger.debug(f"Running Behave hook: {name} withs args: {args}")
        if not self.config.dry_run and (name in self.hooks):
            try:
                with context.use_with_user_mode():
                    self.hooks[name](context, *args)
            except KeyboardInterrupt as ex:
                logger.error(ex)
                self.aborted = True
                if name not in ("before_all", "after_all"):
                    raise
            except Exception as e:
                global ERROR_HOOK_MSG

                use_traceback = True
                ExceptionUtil.set_traceback(e)
                extra = u""
                if "tag" in name:
                    extra = "(tag=%s)" % args[0]

                error_text = ExceptionUtil.describe(e, use_traceback).rstrip()
                error_message = u"\nHOOK-ERROR in %s%s: %s" % (name, extra, error_text)
                logger.error(u"HOOK-ERROR in %s%s: %s" % (name, extra, e))
                print(error_message)
                ERROR_HOOK_MSG.append(e)
                self.hook_failures += 1
                if "tag" in name:
                    statement = getattr(context, "scenario", context.feature)
                elif "all" in name:
                    self.aborted = True
                    statement = None
                else:
                    statement = args[0]

                if statement:
                    statement.hook_failed = True
                    if statement.error_message:
                        statement.error_message += u"\n" + error_message
                    else:
                        statement.store_exception_context(e)  # noqa
                        statement.error_message = error_message

    def run_model(self, features=None):
        """
        Run custom Behave model
        :param features:
        :return:
        """
        # pylint: disable=too-many-branches
        logger.debug("Running Behave model")
        if not self.context:
            self.context = Context(self)
        if self.step_registry is None:
            self.step_registry = the_step_registry
        if features is None:
            features = self.features

        # -- ENSURE: context.execute_steps() works in weird cases (hooks, ...)
        context = self.context
        self.hook_failures = 0
        self.setup_capture()
        self.run_hook("before_all", context)

        run_feature = not self.aborted
        failed_count = 0
        undefined_steps_initial_size = len(self.undefined_steps)
        features = check_features_order(features)
        features_run = []
        for feature in features:
            if run_feature:
                try:
                    self.feature = feature
                    for formatter in self.formatters:
                        formatter.uri(feature.filename)
                    try:

                        failed = feature.run(self)
                        if feature.status.value != 1:
                            features_run.append(feature)
                        if failed:
                            failed_count += 1
                            if self.config.stop or self.aborted:
                                # -- FAIL-EARLY: After first failure.
                                run_feature = False
                    except (KeyError, IndexError) as ex:
                        logger.warning(ex)

                except KeyboardInterrupt as ex:
                    self.aborted = True
                    failed_count += 1
                    run_feature = False
                    logger.warning(ex)

            # -- ALWAYS: Report run/not-run feature to reporters.
            # REQUIRED-FOR: Summary to keep track of untested features.
            for reporter in self.config.reporters:
                reporter.feature(feature)

        if len(features_run) == 0 and run_feature is not False:
            msg = 'There is no scenario with that expression. No scenario has been run.'
            print(msg)
            logger.warning(msg)

        # -- AFTER-ALL:
        # pylint: disable=protected-access, broad-except
        cleanups_failed = False
        self.run_hook("after_all", self.context)
        try:
            self.context._do_cleanups()  # noqa
        except Exception as ex:
            logger.warning(ex)
            cleanups_failed = True

        if self.aborted:
            logger.error("ABORTED: By user.")
        for formatter in self.formatters:
            formatter.close()
        for reporter in self.config.reporters:
            reporter.end()

        failed = ((failed_count > 0) or self.aborted or (self.hook_failures > 0)
                  or (len(self.undefined_steps) > undefined_steps_initial_size)
                  or cleanups_failed)
        # XXX-MAYBE: or context.failed)
        return failed

    def run_with_paths(self):
        """
        Run Behave model with feature paths.
        :return:
        """
        self.context = Context(self)
        self.load_hooks()

        try:
            self.load_step_definitions(get_steps_dir(self.config.steps_dir))
        except (Exception,):
            if os.environ.get('EXECUTION_TYPE') == 'Portal':
                send_alert_portal('ERROR: Step has already been defined.')
                print_portal_console('ERROR: Step has already been defined.')
        import_default_steps_dir()

        # -- ENSURE: context.execute_steps() works in weird cases (hooks, ...)
        # self.setup_capture()
        # self.run_hook("before_all", self.context)

        # -- STEP: Parse all feature files (by using their file location).
        feature_locations = [filename for filename in self.feature_locations()
                             if not self.config.exclude(filename)]

        features = parse_features(feature_locations, language=self.config.lang)
        final_features = features

        if SCENARIOS_RUN:
            final_features = _get_final_features(features)

        self.features.extend(final_features)

        # -- STEP: Run all features.
        stream_openers = self.config.outputs
        self.formatters = make_formatters(self.config, stream_openers)
        if self.config.environment:
            Settings.PYTALOS_PROFILES.set('environment', value=self.config.environment[0])
        return self.run_model()


def _get_final_features(features):
    final_features = []
    for current_feature in features:
        found = False
        for scenario in current_feature.scenarios:
            if isinstance(scenario, ScenarioOutline):
                name_transformed = re.sub('<.*>', '.+', scenario.name)
                name_regex = re.compile(name_transformed)
                for scenario_run in SCENARIOS_RUN:
                    if name_regex.search(scenario_run):
                        final_features.append(current_feature)
                        found = True
                        break
                if found is True:
                    break
            else:
                if scenario.name in SCENARIOS_RUN:
                    final_features.append(current_feature)
                    break
    return final_features


def make_behave_argv(verbose: bool = False, junit: bool = False, format_pretty: bool = False,
                     tags: [str, list] = None, scenario_names: str | list = None, conf_properties=None,
                     allure: bool = False, teamcity: bool = False,
                     parallel=False, processes: int = 5, includes: list = None, excludes: list = None,
                     environment=None, **kwargs):
    """
    This function converts parameters to behave arguments.
    :param verbose:
    :param junit:
    :param format_pretty:
    :param tags:
    :param scenario_names:
    :param conf_properties:
    :param allure:
    :param teamcity:
    :param parallel:
    :param processes:
    :param includes:
    :param excludes:
    :param environment:
    :param kwargs:
    :return:
    """
    params = ''

    if verbose:
        params = params + ' -v'
    if junit:
        params = params + ' --junit'
    if format_pretty:
        params = params + ' --format pretty'
    if tags:
        params = ''.join(' --tags=' + ','.join(tag if isinstance(tag, list) else [tag]) for tag in
                         (tags if isinstance(tags, list) else [tags])).replace(', ', ',')
    if scenario_names:
        if isinstance(scenario_names, list):
            for name in scenario_names:
                SCENARIOS_RUN.append(name)
                name = re.sub('<.*>', '.*', name)
                params = params + f" -n '{name}'"
        else:
            SCENARIOS_RUN.append(scenario_names)
            name = re.sub('<.*>', '.*', scenario_names)
            params = params + f" -n '{name}'"

    if conf_properties:
        properties_base_config = ' -D Config_environment='
        if type(conf_properties) is str:
            params = params + properties_base_config + conf_properties
        if type(conf_properties) is list and parallel is False:
            params = params + properties_base_config + conf_properties[0]
        if type(conf_properties) is list and parallel == ENVIRONMENTS:
            params = params + properties_base_config + conf_properties[0]
        elif type(conf_properties) is list and parallel:
            params = params + f" --browsers {','.join(conf_properties)}"

    if kwargs:
        for k, v in kwargs.items():
            params += f" -D {k}={v}"

    if allure:
        params = params + " -f allure_behave.formatter:AllureFormatter -o output/info/allure"

    if teamcity:
        params = params + " -f behave_teamcity:TeamcityFormatter -o output/info/teamcity"

    if parallel:
        params = params + f" --parallel {parallel}"
        params = params + f" --processes {str(processes)}"

        if environment:
            params = params + f" --environment {','.join(environment)}"

    if includes:
        params = params + f" --include '/({'|'.join(includes)}).feature'"
    if excludes:
        params = params + f" --exclude '/({'|'.join(excludes)}).feature'"

    logger.info(f"Talos run params configured: {params}")
    return params


def add_extra_args(args):
    """
    This feature adds mandatory default arguments to user arguments.
    :param args:
    :return:
    """
    args += get_json_report_args()
    return args


def run_parallel(args):
    """
    Run Talos in parallel mode.
    :param args:
    :return:
    """

    logger.info('Running Talos in parallel mode')
    parallel_args, run_args = parse_parallel_schema_args(args)
    parallel_schema = parallel_args.parallel
    processes = parallel_args.processes
    pool = Pool(processes)

    logger.info("Parallel options configured:")
    logger.info(f"Parallel schema: {parallel_schema}")
    logger.info(f"Parallel processes: {processes}")

    os.environ['PARALLEL_TYPE'] = parallel_schema
    results = []
    if parallel_schema == BROWSERS:
        parallel_args, browser_args = parse_parallel_browsers_args(run_args)
        results = run_browsers_parallel(parallel_args, browser_args, pool, run_behave)
    elif parallel_schema == SCENARIOS:
        parallel_args, scenarios_args = parse_parallel_scenarios_args(run_args)
        results = run_scenarios_parallel(parallel_args, scenarios_args, pool, run_behave)

    elif parallel_schema == FEATURES:
        parallel_args, features_args = parse_parallel_features_args(run_args)
        results = run_features_parallel(parallel_args, features_args, pool, run_behave)
    elif parallel_schema == ENVIRONMENTS:
        parallel_args, environment_args = parse_parallel_environments_args(run_args)
        results = run_environments_parallel(parallel_args, environment_args, pool, run_behave)
    elif parallel_schema == MULTI_BROWSERS_SCENARIOS:
        parallel_args, unknown_args = parse_parallel_scenarios_browser_args(run_args)
        results = run_scenarios_browsers_parallel(parallel_args, unknown_args, pool, run_behave)

    return 1 if 1 in results else 0


def run_sequential(args):
    """
    Run Talos in sequential mode.
    :param args:
    :return:
    """
    logger.info('Running Talos in sequential mode')

    args = add_extra_args(args)
    config = BehaveConfiguration(command_args=args, run_settings=settings)
    finish_code = run_behave(config, CustomModelRunner)

    return finish_code


def main(args=None, env=None):
    """
    Main function of Talos, here begins and ends the execution of the framework.
    :param env:
    :param args:
    :return:
    """
    args = args.replace(', ', ',')
    if env:
        os.environ = env
    logger.info('Starting TalosBDD main')
    os.environ['RUN_TYPE'] = 'parallel' if '--parallel' in args or ' -x ' in args else 'sequential'

    before_execution()
    if os.environ['RUN_TYPE'] == 'parallel':
        finish_code = run_parallel(args)
    else:
        finish_code = run_sequential(args)
    after_execution()
    logger.info(f"Finish code: {finish_code}")
    sys.exit(finish_code)
