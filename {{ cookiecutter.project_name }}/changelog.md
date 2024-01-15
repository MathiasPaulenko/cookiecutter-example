### v2.4.0

  - New Features:
    - IA Self-healing (Beta): It can be configured in settings.py. Only work for Page Elements.
    - Visual Testing (Beta). It can be configured in settings.py.
    - User steps are loaded automatically. The default steps must be indicated in the settings.py file in the PYTALOS_STEPS variable. The import_steps.py file is deleted.
    - The management of user configurations was improved with respect to that of the core. If there is no configuration in the user settings, a default value is taken.
  - Portal: (Collaboration with TCoE Mexico)
    - Section was added for editing features and data files.
    - Added folder navigation module.
    - Added saving and creating files.
    - Added autocompletion and search for Gherkin steps when editing features files.
    - Abort test button implemented.
    - Alerts were refactored.
    - Formatted console errors for better visualization.
    - Error notifications implemented.
    - Sending errors from TalosBDD to the portal.
    - Configuration was added to choose the default steps that you want to use.
    - The way of execution by scenario name has been improved.
    - The execution form by features and by scenario was changed to a selection form by toggles.
    - Message and notification management was improved.
    - The responsive was improved.
    - Filters were added to the tables.
  - Defaults steps:
    - Android keywords added. (Collaboration with SDET - CoE Testing Automation)
    - Appian keywords added. (Collaboration with SDET - CoE Testing Automation)
    - Added PyAutoGui default steps.
  - General improvements:
    - Added version command to tools.py file.
    - Changed driver updater to before_all instead of before_scenario. Running only once.
    - Message when trying to execute tags that do not execute any scenario.
    - Added the ability to run by scenario name (regex) in talos_run
    - Force close_driver to True when running in headless mode.
    - Added @no-screenshot tag to avoid adding screenshots to the evidence even if the option is active in the settings file.
    - Added the ability to change the scenario outline name schema to the settings.
    - Info message of the version that is being updated added to the update_core function in tools.py
    - Improved evidence when more than one execute_step is executed in the same step. Added ability to execute execute_steps more than once in steps.
    - Save repositories only if the repositories setting is True.
    - Added function order_by_rows() in excel wrapper.
    - The --update-driver command was added to activate the automatic driver updater via the command line.
  - Improvements in reporting and integrations: 
    - A new HTML report was added that shows all the errors caused in the execution as a summary and in a list.
    - Added error categorization system for HTML error reporting.
    - The version of Talos Connect was updated allowing the upgrade to Octane.
    - Added Octane upload to tools.py.
    - Added new functions to set the default values for reporting.
    - The steps in ALM have been correctly ordered when using substeps.
    - Removed deprecated add_extra_info functions. We have been warning for just over a year.
    - The list of errors in the scenario report and in the global report has been added to the HTML reports.
    - The display of errors in the HTML report has been improved.
    - Added response headers without body in HTML report.
    - Improved Host screenshots. (Collaboration with TCoE Mexico)
    - The integration message with Jira was improved.
    - New information was added to the talos_report.json such as attachments, the raw name of the scenarios or the matches.
  - Refactorings:
    - Versions of requirements.txt were updated to resolve vulnerabilities and bugs in the libraries. 
    - The name of the xml and simple html reports was shortened.
    - The generation of necessary directories was refactored and optimized.
    - The Axe engine has been updated to the latest version.
  - Bugs Fixed:
    - Update driver does not work due to API update.
    - Check portal is running function when portal is offline.
    - Video recorder imports.
    - Snowflake wrapper and default steps typo.
    - Settings used when running cases with the portal running.
    - Browser console memory leak with portal running.
    - After execution hooks with context.
    - Error with api "204 No Content".
    - Accessibility tests are run on no_driver, host and api.
    - Inconsistency of results data in the summary report.
    - Recording video enabled in api, host o services executions.
    - Snowflake wrapper is not in context.

### v2.3.0

- TalosBDD local web (Collaboration with TCoE Mexico):
  - Database creation.
  - Requirements added.
  - Added settings to settings.py.
  - Added dashboard page.
  - Added the option to save runs to a database.
  - Added executions page.
  - Added execution page:
    - Executions by Tags
    - Executions by Scenario
    - Executions by Features
    - Custom executions.
  - Light mode and dark mode added.
  - Logs were added.
  - Added documentation page.
  - Added configuration and settings page.
  - pop-ups and notifications created.
  - Added the portal service execution to the tools.py tool.
  - Added 404 page.
  - Added new blue-print for utilities.
  - Added console log real time execution page.
- The AXE wrapper for accessibility testing was improved.
- Default Steps:
  - Api Keywords:
    - print request information
    - prepare for the application the certificates 'cert'
  - Web Keywords: (Collaboration with SDET - CoE Testing Automation)
    - deselect the option with index 'index' from the select element by 'by' and locator 'loc' fixed
    - wait until the title is 'title' fixed
    - wait until the title contain 'title' fixed
    - wait until alert is present fixed
  - Snowflake default steps added.
  - SSH default steps added. (Collaboration with TCoE Mexico)
  - Appian Keywords:
    - click the icon with preceding text 'text' (Collaboration with SDET - CoE Testing Automation)
    - click the icon with following text 'text' (Collaboration with SDET - CoE Testing Automation)
    - fill the textarea with role textbox with the text 'text' (Collaboration with SDET - CoE Testing Automation)
    - verify that any paragraph contains the text 'text' and is presented (Collaboration with SDET - CoE Testing Automation)
  - Android Keywords:
    - write 'text' to the android element with id 'id_text' (Collaboration with SDET - CoE Testing Automation)
    - write 'text' to the android element with resource id 'resources id' (Collaboration with SDET - CoE Testing Automation)
- General improvements:
  - The driver scenario name was prefixed to properties to avoid duplication when running in parallel on the same browser or operating system.
  - Added the list of errors that occurred during execution by printing it to the console.
  - Report generation cascade errors have been caught if the framework execution fails.
  - Added the parameters of the curl call that appears in the reports.
  - Added the certification parameter in the wrapper api.
- Improvements in reporting and integrations:
  - Talos Connect has been updated to the latest version.
  - Added skipped steps in ALM.
  - Added the possibility to add all runs in the Test Set indicated in the configuration CSV.
  - Added setting not to copy the folder structure of features in ALM for TL and TP. Configuration in PYTALOS_ALM.replicate_folder_structure.
  - Added the option to set the ALM test run name as the scenario name or not.
  - Renamed the file alm.properties to alm3.properties. Also changed its location to the settings/integration folder.
  - Moved the location of the ALM configuration CSV file to the settings/integrations folder.
  - Added functions to be able to add extra information to ALM evidence through functions in the steps or hooks.
  - Added the function to add user files to the ALM upload.
  - Added the list of installed third-party libraries to the log.
  - Added HTML accessibility report.
    - Screenshots of the analysed elements were added.
    - Tabs were added for typologies of results.
    - Added results of the analysis rules.
    - Added settings to make screenshots and highlights optional.
  - The way HTML reports are generated has been changed to templates and Jinja.
  - The graphics in the HTML report were improved.
  - Jira connector adapted for compatibility with Big Jira and Cloud Jira.
  - Added options for which evidence file is uploaded to the Jira.
  - Updated the Boostrap version to version 5.
  - Added option to run the Octane upload connector.
  - The presentation of json data in reports has been improved.
  - Video capture evidence and its settings were added.
- Other small but powerful changes:
  - Added add_html function for HTML reports.
    - add_html_custom
    - add_html_link
    - add_html_attach
    - add_html_custom
    - add_html_table
  - Sub-steps:
    - Added the option to include the sub steps in the HTML accounting of the results.
    - Modified context_utils.py to prevent from stack overflow error when trying to run a sub-step that contains a superior step.
    - Added sub-steps as drop-downs in HTML reports.
  - New PyAutoGui Wrapper.
  - Added the possibility to sort the priority of scenario executions by tags.
  - tools.py
    - The core update function has been optimised.
    - The file CONTRIBUTING.md was added to the list of files to be updated.
  - Snowflake Wrapper added.
  - New SSH Wrapper. (Collaboration with TCoE Mexico)
- Bug Fixes:
  - Template var in example tables and in parallel execution.
  - Keep the HTML report zipper when uploading to ALM.
  - Added image captures to html reports when uploading to ALM.
  - Fixed status display in SauceLabs runs.
  - Changed selenium version from 4.* to 4.9.1.
  - Added error message when AXE could not be injected.
  - Fixed arguments and options for Edge executions.
  - Fixed tc-path and ts-path concatenation.
  - Excel and CSV data collection is fixed when they start at 0.
  - Parallel runs are fixed when tags are in the example table.
  - Fixed the Server section from mandatory to optional in properties.cfg files.
- Functions deprecated:
    - context.func.get_profile_value_key_path
    - context.func.get_unique_profile_re_var
    - context.func.is_contains_profile_re_var
    - context.func.get_formatter_multiple_re_var
    - context.func.get_template_var_value
    - context.func.add_extra_info


### v2.2.0

- Complete optimisation of the core to solve performance problems due to overuse of template var and file reading. 
- Fixed dependency for compatibility with python 3.11. Compatibility with python 3.10 is maintained.
- Added CONTRIBUTING.md file indicating steps to take into account if you want to contribute to the TalosBDD core.
- Added log system.
  - The log can be configured in the settings.py file in the PYTALOS_GENERAL section in the logger key.
  - You can make use of the Talos log by putting at the beginning of the file: logger = logging.getLogger(__name__)
  - A log file is generated in the output/logs folder and the log can be activated by console.
- Translations were added to the evidence documents.
    - English and Spanish are the added languages, for now.
    - The language change is done through the report_language setting in the PYTALOS_REPORTS section of the settings.py
      file.
- Changes related to evidence files:
    - HTML images have been added when uploading to ALM.
    - When uploading HTML files as evidence to ALM, a zip file with the HTML files and images will be uploaded.
    - Improved the description of the scenarios and feature in HTML.
    - The PDF generation engine was changed to increase the generation speed and to be compatible with linux systems.
    - The names of the json files have been shortened.
    - Added the executed environment and Talos version in the html.
    - The names of the evidence files have been shortened with respect to the scenario names to avoid compatibility problems with Windows.
    - The generation of evidence was optimised.
    - Changed the HTML generation engine to Jinja2.
    - Added the no_evidence tag to avoid generating feature reports with this tag.
    - Added Curl command to report when running send_request steps.
    - Added functionality to truncate the report name if it exceeds 100 characters, in order to avoid Windows file length compatibility issues.
    - Changed dimensions of pictures in docs.
    - Added requests headers and params to api response.
- Other small but powerful changes:
    - Improved context.execute_step function to add nested evidence between steps.
      - Added capacity for parameterised steps.
      - Added var template and var repository capability in sub steps.
      - Configuration to add evidence or not of sub steps to report.
    - The colour library has been changed from termcolor to colorama.
    - New hooks have been added:
      - before_tag - return scenario tags before the execution.
      - after_tag - return scenario tags after the execution.
      - before_report - return talos json report information before report generation.
    - Added talos version in the title and as an attribute of the arc module: arc.__VERSION__().
    - Added folder nesting capabilities for repository data, making it similar to profile data.
    - The deprecated flag was created to indicate if a function is deprecated.
    - ALL core methods and functions have been discussed.
    - Added .env_template file.
    - The Faker library and functions have been changed to optional.
    - Added customised exceptions for Talos.
    - Added new optional argument named run_settings (-rs) in order to receive a string with the name of the settings file.
    - Added sys.exit with the return code of the execution.
    - Added multi-browser multi-scenario parallel execution.
- Bug Fixed:
    - Driver session and driver process reuse functionality.
    - Failed to connect to Elasticsearch if the environment proxy is enabled.
    - Put spaces in the template var.
    - Error in coding evidence creation with tools.py. Added utf8.
    - Wrong alm connector version in tools.py file.
    - Removed local configuration from talos_run.py
    - Capitalize was removed from the evidence
    - Template var value is empty.
    - Template var returns a convention instead of the data if the data is long or is a dictionary or a list.
    - Conflict in the generation of evidence when features are called the same.
    - Api response without content not showing in evidences.
    - duplicated context in oracle steps.
    - Removed comtype library.
- Functions deprecated:
    - context.func.get_profile_value_key_path
    - context.func.get_unique_profile_re_var
    - context.func.is_contains_profile_re_var
    - context.func.get_formatter_multiple_re_var
    - context.func.get_template_var_value
    - context.func.add_extra_info


### v2.1.3

- Added Accessibility Tests.
    - It can be done automatically every time the web changes url by configuring it in the settings.py in the
      PYTALOS_ACCESSIBILITY section.
    - Default steps have been created to be used in the scenarios that the user sees fit.
    - The default steps show the results in the evidence files.
    - A json is generated to report the results of the accessibility test.
- Talos Virtual was integrated into Talos BDD.
    - The settings are located in settings TALOS_VIRTUAL.
    - It can be used automatically to lift service virtualization before running tests.
    - Added default steps for use within scenarios in arc.contrib.steps.mock.mountebank_keywords.py.
- The tools.py file has been added as a command line to execute functions independent of automation such as:
    - Create evidences from talos_report.json
    - Run ALM encoder Jar.
    - Run ALM Connector Jar.
    - Encode and decode literals.
    - Update drivers.
    - Updates core.
- Parallel executions by environment of the profiles files.
- Repetition of scenarios that have failed.
    - It is done automatically by using the autoretry option of the settings file or by the @autoretry tag.
    - You can select the number of attempts and the wait between attempts.
- Other small changes:
    - The TalosBDD logo was changed.
    - Option to take capture if the step fails automatically in the settings options.
    - Requirements.txt updated.
    - Information from the html evidence would be changed to a collapsed table.
    - Button to go to the beginning in the HTML evidence.
    - Fixed an issue with var templates with repository.
    - The generation of PDF evidence has been changed to another engine and optimized.
    - The description of the features and scenarios has been added in the evidence files.
    - The execution of the framework is stopped in the event that the selected environment does not exist.
    - Added information for integration with Octane to talos_report.json.
    - Added a summary of global execution information to the TalosBDD json report.
    - Added an error message when a var template is malformed or some of the values do not exist.
    - Added edge, edgeie and iexplore to extension-paths in driver setup
    - The version of the ALM connector was uploaded.
- Bug Fixed:
    - Description of the scenarios in the evidence files.
    - Delete duplicated descriptions in docx.
    - Fixed multi-locator when there is no shadow-roots.
    - Fixed scroll in mobile native test in scroll_element_into_view function.
    - Fixed an issue with hooks that did not pass the instance of steps, scenario or features.
    - Special characters were solved by decoding in HTML evidences.
    - Fixed default web and appian steps.
- Internal restructuring and optimization.
- Functions deprecated:
    - context.func.get_profile_value_key_path
    - context.func.get_unique_profile_re_var
    - context.func.is_contains_profile_re_var
    - context.func.get_formatter_multiple_re_var
    - context.func.get_template_var_value
    - context.func.add_extra_info

### v2.1.2

- Added functionality to encrypt and decrypt sensitive data:
    - Added decode() and encode() functionalities in arc.contrib.tools.crypto.crypto
    - If you work locally, you must add the .env file to the root of the project and put the PASSPHRASE key with the
      value you want to use as an encryption password.
    - If you work from an orchestrator like Laika or Jenkins, you must create a system variable with the PASSPHRASE key
      and the key with which you encrypted the data.
    - More information in the README in the section: Handle sensible data
- Added the option to save old reports:
    - In the file settings.py in section PYTALOS_REPORTS is the configuration save_old_reports where you can enable this
      action, indicate the absolute path of where the reports are going to be saved and the type of tablet you want to
      generate.
    - If enabled, this option will generate a compressed file with the name output and timestamp.
- Added access by template var to the values of the repository of literals or elements:
    - You can access the data in the settings/repositories folder using the var template &{{file_name:key1}}
    - Unlike the var templates of profile files, the differentiating character is & instead of $.
- Added functionality to interact with ShadowRoots elements recursively.
- Steps and keywords by default:
    - New default cases for Appian Web.
        - You can import the steps from:  arc.contrib.steps.web.appian_keywords.py
        - Documentation was added to the steps.
    - Refactored and added documentation to the default host and data steps.
    - Web Default Steps:
        - New one-actions and verification default steps added.
        - The property tables of the web default steps have been removed and added to the settings as default values.
            - Web steps no longer use gherkin tables to pass data.
            - The highlight and wait options for waits are located in the settings.py in the
              PYTALOS_RUN.default_steps_options section.
        - Steps were refactored and comments were added for the steps catalog.
- Other small changes:
    - Encoding of the yaml/json files of the data repository system.
    - Added custom error when evidence cannot be created in Docx due to open file
    - Variables with the path to the helpers and test folders were added to the settings.py for use in the tests.
    - Added examples of properties configurations of all execution possibilities.
    - Moved the option to delete old reports to the PYTALOS_REPORTS section.
    - Added automatic support for .env files.
    - Data, functional, appian and mail steps were added to the steps excel catalog.
    - The following features were added to context.utilities:
        - double_click()
        - javascript_click()
        - change_style_attribute()
    - Libraries:
        - The following libraries in the requirements.txt were commented as optional:
            - PyMuPDF - management and extraction of information from PDF files.
            - PyJWT - encryption and decryption of JWT tokens.
        - PyCryptoDome added in the requirements.txt file.
- Bug Fixed:
    - Dynamic waits for PageElements failed.
    - Error in context in order in arguments in PageObjects
    - Encoding of the yaml/json files of the data repository system.
    - Fixed issue with mobile device executions in remote device farms.
- Internal restructuring and optimization.
- Functions deprecated:
    - context.func.get_profile_value_key_path
    - context.func.get_unique_profile_re_var
    - context.func.is_contains_profile_re_var
    - context.func.get_formatter_multiple_re_var
    - context.func.get_template_var_value
    - context.func.add_extra_info

### v2.1.1

- New literal management system and optional elements added:
    - You can use the files literals.yaml/json and elements.yaml/json in the path settings/repositories/
    - The elements.yaml/json file can be used to save locators.
    - The literals.yaml/json file can be used to save text in different languages.
    - The context variable will contain the language selected in the settings and a dictionary with the data in the
      elements.yaml/json and literals.yaml/json files.
    - You can tell literals and elements values that can be replaced with the self.format_text function and using the {}
      character.
    - You can put other json files of information not changing by environment.
    - Documentation: https://confluence.alm.europe.cloudcenter.corp/display/QUASER/Elements+and+Literals+in+TALOS+BDD
- You can pass the context to the instances of the PageObject, so that you can use it natively within them with
  self.context.
- New functionalities for the management and extraction of information from PDF files.
- New default step for API testing:
    - verify response not contains value {}
- Optimization in the process of generating and reducing the weight of HTML evidence.
    - Images for HTML evidence file are converted to webp format for size reduction and will be generated within
      output/reports/html/assets.
- The following default settings have been changed:
    - generate_pdf: False
    - update_step_catalog: False
    - alm3_properties: False
- Bug Fixed:
    - Error with templates var when using the gherkin parameters inside.
    - Error of the var templates with special characters.
    - Tables and texts are unbalanced and text with dictionaries in PDF evidence.
    - Use of template var within the examples table of gherkin.
    - Special character error in name of scenarios when there is template var.
    - Desynchronization error between file name and HTML evidence binding when there are special characters.
    - PDF evidence error with multiline cells with unit table evidences.
    - API test evidence error that checks response schemas.
    - Multiple screenshot generation failed in tests for Host.
    - Evidence error when the response of an api is not in json format (for example: an array).

### v2.1.0

- ¡Added parallel executions!
    - Documentation: https://confluence.alm.europe.cloudcenter.corp/display/QUASER/Run+TALOS+BDD
- A mandatory section of project information has been added in the settings of the framework.
    - Project information will be seen in the evidence documents.
    - Documentation: https://confluence.alm.europe.cloudcenter.corp/display/QUASER/Project+info+fields
- Evidence:
    - New way to introduce extra evidence such as json, text, screenshots, data tables.
        - These methods can be accessed using context.func.evidences
        - Documentation: https://confluence.alm.europe.cloudcenter.corp/display/QUASER/Add+Information+to+Reports
    - Now you can generate a PDF document of evidence by scenarios.
    - Improved HTML evidence design.
- Improvements in integrations:
    - Improved execution for Laika. Proxy settings.
    - You can choose which file can be uploaded to Jira and ALM. Allowed files: HTML, PDF or Docx.
    - Arguments were added for Jira.
    - Improved integration with SauceLab and Perfecto.
    - The summary by scenario was removed from Jira's comments. And the attachments and summary comment were improved.
- Other new implementations:
    - Now it is allowed to put folders inside the profiles folders and be able to access this data through the
      dictionary of context.config.userdata
    - Added capabilities, arguments and extra options for integrations with Sauce Lab and Perfecto in addition to others
      of Selenium 4.
    - Added Oracle-based connectivity functionality.
        - Documentation: https://confluence.alm.europe.cloudcenter.corp/display/QUASER/Oracle+DataBase+Wrapper
    - New steps by default.
    - The title of the framework was updated when running it.
    - Added ESC key press functionality for HOST.
    - Added the new PageElement Layer for Divs or other layers.
- Bug Fixed:
    - New step added to ignore blank params
    - Step snippet not implemented fixed.
    - Error Step object has no attribute 'result_expected' fixed
    - Docx template error removed, evidence is generated from talos_report.json.
    - Session de api wrapper now closes.
    - Incompatibility between Gherkin's RE and fixed var templates.
    - Highlight Element fixed.
    - Fixed the error of generation of evidence in case of special characters in name of scenarios.
    - Error in updating drivers fixed.
- Internal restructuring and optimization.
- Functions deprecated:
    - add_extra_info
    - get_template_var_value
    - get_formatter_multiple_re_var
    - is_contains_profile_re_var
    - get_unique_profile_re_var
    - get_profile_value_key_path

### v2.0.6

- Fixes and improvements in integration with Jira.
    - Added connection via proxy by execution arguments and in the settings.
    - The visualization of evidence attachments in the tasks has been improved.
    - Jira SaaS Compatibility.
- Changes in remote executions in properties driver configuration:
    - If the port parameter is empty, it is not added to the connection url to the remote server.
    - Now you have to enter the protocol of the connection url. Before it was forced to use https connection, now the
      user chooses.
- Refactoring integration with ALM.
    - Updated alm.properties for compatibility.
    - Fixed problem with paths to integration resources.
    - The match_alm_execution option now concatenates the day, month, year, hour, minute, and second of execution.
      Before, it only concatenated the day, month and year.
    - The reference about test folder was removed from the path of the test cases in the TestPlan and TestLab.
- The character of the template var was changed due to compatibility problems. Now it's ${{---}}.
- Bug Fixed:
    - Error in the generation of the evidence json with scenarios outlines.
    - Fixed the crash that occurred when the response of an api request was empty or without headers. Yes, AGAIN...
    - Fixed problem with routes that did not generate the user's steps in the catalog excel.
    - Documentation fixes in the Readme.

### v2.0.5

- The template variables were added natively and improved.
- Default steps of an action for web automation have been added.
- Other functional and control default steps have been added.
- Other functionalities have been added in the context.utilities instance.
- Bug Fixed:
    - Scenario start_time html report error.
    - ALM Connect CSV encodec error.
    - Error with the paths of the json attachments to upload the HTML evidence to ALM.
- Refactoring and optimization.

### v2.0.4-BETA

- Improvements applied to evidence reports.
    - Added the possibility to change the obtained result and the expected result in the word and html document.
    - The description of the scenarios and steps was added to the html report.
    - The information displayed in the html report has been restructured.
    - Added screenshots for Host executions in html.
    - The styles of the html report have been updated.
- The option of being able to put more than one locator in the Page Element was added.
    - The element can be passed a list of tuples with a first By object and a string indicating the locator.
    - The rest of the parameters remain the same.
- Added new arguments for command line execution:
    - Argument to enable or disable the ALM connector.
    - Argument to introduce runtime or environment proxy.
    - Argument to activate headless mode.
    - Argument to change any value of the properties values:
        - The argument follows the structure: -D [Section]_[key]="new value", , where section is the section in which
          the value we want to change is in the properties file, and the key is the value we want to change.
- Added arguments and functionality to update the framework core and VERSION, Changelog and README files:
    - You can run the update with the command: python talos_run.py --token github_personal_acces_token --version v0.0.0
    - The token is a personal Github generated token.
    - Version is the displayed version of the release to which you want to upgrade.
- Integrations:
    - Integration with Sauce Lab was fixed and properties prepared for such executions were added.
    - Added properties file for executions in laika.
- Bug Fixed:
    - Fixed the option not to close the driver in web executions.
    - Fixed a problem with the generation of the report json when the execution of the framework failed.
    - Fixed the parameter of the master file in the default steps for api rest.

### v2.0.3-BETA

- Hotfix and bug resolutions.

### v2.0.2-BETA

- Added module to work with SFTP services.
    - SFTP Default Keywords added.
- Added functionality to update web drivers automatically.
    - You can tell it in the settings.py file if you want to update the drivers automatically or not.
    - Proxy update support.
- New reports added.
    - HTML execution report added.
        - Global report, by feature and by scenario.
    - JSON report with all the execution information.
    - Reports and logs of behave and others.
    - Automatic catalog of the steps in RST format.
    - The previous html unit reports are maintained.
- Added new types of drivers: services, backend, edgeie. API is no longer valid as driver type.
- Added new arguments for command execution:
    - Argument to proxy by putting --proxy http....
    - Argument to change environment of profiles files by putting --env cer
- Another little implementations:
    - The configuration of execution through proxy for api, services and web executions through the settings.py file has
      been improved.
- Bugs fixed.
    - Path to ALM connect resources jar fixed.
    - Path to VBS host middleware fixed.

### v2.0.1-BETA

- Added edge functionality for internet explore compatibility.
    - New valid driver types: edgeie in order to activate edge in ie explore compatibility.
    - IE and EDGE driver added
- Integration was added in the excel and csv profile files to make use of these formats to obtain data in the steps
- Bugs fixed

### v2.0.0-BETA

- The folder system has been restructured. The folders related to the test cases, such as features, steps, helpers, were
  unified in the Test folder.
- The core was optimized, increasing its speed and better managing the type of execution.
- The embedded virtual environment has been removed, now any version of python higher than 3.6 can be used. The library
  list is left free in the requirements.txt file.
- The versions of the most important libraries were increased, Selenium to version 4, Appium, requests, among others.
- Improved performance on Linux and Mac.
- New functionalities:

    - SQL Wrappers.
    - Writing and reading of Excel and CSV files.
    - Proxy settings for executions.
    - The default apis execution steps were improved.
    - More reports enabled.
    - Integration with Allure.

- Bugs fixed

