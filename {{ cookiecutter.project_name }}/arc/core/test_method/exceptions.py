# -*- coding: utf-8 -*-
"""
File containing the Talos-specific exception functions.
"""


class VerificationException(Exception):
    """
    Exception for value checks.
    Automatically generates a unit evidence table in Talos reports.
    """

    def __init__(
            self, context, current_value, expected_value,
            result=False, title="", key=None, error_msg="Verification Error Exception."
    ):
        self.context = context
        self.current_value = current_value
        self.expected_value = expected_value
        self.result = result
        self.title = title
        self.key = key
        self.error_msg = error_msg

        super().__init__(self.error_msg)

        self.context.func.evidences.add_unit_table(
            title=self.title,
            key=self.key,
            current_value=self.current_value,
            expected_value=self.expected_value,
            result=self.result,
            error_msg=self.error_msg
        )

    def __str__(self):
        return self.error_msg


class TalosReportException(Exception):
    """
    Exception class for Talos reporting errors.
    """

    def __init__(self, error_msg='Document generation error.'):
        self.error_msg = error_msg

    def __str__(self):
        return self.error_msg


class TalosNotThirdPartyAppInstalled(Exception):
    """
    Exception class for Talos Third Party App installation errors.
    """

    def __init__(self, error_msg='The application is not installed on the system.'):
        self.error_msg = error_msg

    def __str__(self):
        return self.error_msg


class TalosErrorReadFile(Exception):
    """
    Exception class for Talos Read File errors.
    """

    def __init__(self, error_msg='Error in reading the file.'):
        self.error_msg = error_msg

    def __str__(self):
        return self.error_msg


class TalosGenerationReportError(Exception):
    """
    Exception class for Talos Generation Report errors.
    """

    def __init__(self, error_msg='Error in report generation.'):
        self.error_msg = error_msg

    def __str__(self):
        return self.error_msg


class TalosResourceNotFound(Exception):
    """
    Exception class for Talos Resources not found errors.
    """

    def __init__(self, error_msg='The resource has not been found.'):
        self.error_msg = error_msg

    def __str__(self):
        return self.error_msg


class TalosConfigurationError(Exception):
    """
    Exception class for Talos Configuration Error errors.
    """

    def __init__(self, error_msg='Talos configuration failed.'):
        self.error_msg = error_msg

    def __str__(self):
        return self.error_msg


class TalosDriverError(Exception):
    """
    Exception class for Talos Driver configuration or execution errors.
    """

    def __init__(self, error_msg='Driver configuration or execution failed.'):
        self.error_msg = error_msg

    def __str__(self):
        return str(self.error_msg)


class TalosRunError(Exception):
    """
    Exception class for Talos general run errors.
    """

    def __init__(self, error_msg='The operation could not succeed.'):
        self.error_msg = error_msg

    def __str__(self):
        return self.error_msg


class TalosHookError(Exception):
    """
    Exception class for Talos general run errors.
    """

    def __init__(self, error_msg='The operation could not succeed.'):
        self.error_msg = error_msg

    def __str__(self):
        return self.error_msg


class TalosTestError(Exception):
    """
    Exception class for Talos general test errors.
    """

    def __init__(self, error_msg='The operation could not succeed.'):
        self.error_msg = error_msg

    def __str__(self):
        return self.error_msg


class TalosDatabaseError(Exception):
    """
        Exception class for Talos database errors.
    """

    def __init__(self, error_msg='Database not exists'):
        self.error_msg = error_msg

    def __str__(self):
        return self.error_msg


class TalosVisualTestingError(Exception):
    """
        Exception class for Talos Visual Testing errors.
    """

    def __init__(self, error_msg='Visual testing error'):
        self.error_msg = error_msg

    def __str__(self):
        return self.error_msg
