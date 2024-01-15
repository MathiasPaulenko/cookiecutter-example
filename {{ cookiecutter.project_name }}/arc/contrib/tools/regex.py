# -*- coding: utf-8 -*-
"""
Module of useful functions and classes for the use and handling of RegEx statements.
"""
import logging
import re

logger = logging.getLogger(__name__)


def re_formatter(escaped_arg):
    """
    Return a regex parsed passed by a args escaped.
    :param escaped_arg:
    :return:
    """

    def regex_escaped(obj, *args):
        """
        Return a regex escaped.
        :param obj:
        :param args:
        :return:
        """
        esc = [isinstance(arg, RegExCompose) and arg.reg or re.escape(str(arg)) for arg in args]
        return escaped_arg(obj, *esc)

    return regex_escaped


class RegExCompose(object):
    """
    RegEx generator compose class.
    """

    def __init__(self):
        self.reg = []
        self.modifiers = {'A': 0, 'I': 0, 'L': 0, 'M': 0, 'S': 0, 'U': 0, 'X': 0}

    def __getattr__(self, attr):
        regex = self.regex()
        return getattr(regex, attr)

    def __str__(self):
        return "".join(self.reg)

    def add(self, value):
        """
        Add value to regex generated.
        :param value:
        :return:
        """
        if isinstance(value, list):
            self.reg.extend(value)
        else:
            self.reg.append(value)
        return self

    def regex(self):
        """
        Return regex compose.
        :return:
        """
        return re.compile(str(self), self.modifiers["I"] | self.modifiers["M"] | self.modifiers["A"])

    def custom_flag(self, flag=None):
        """
        Add a custom flag.
        :param flag:
        :return:
        """
        return re.compile(str(self), self.modifiers[flag.upper()]) if flag else None

    def expression(self):
        """
        Return regex expression as str.
        :return:
        """
        return str(self)

    def anything(self):
        """
        Add a anything regex value.
        :return:
        """
        return self.add("(.*)")

    @re_formatter
    def anything_except(self, value):
        """
        Add a anything value with a except value.
        :param value:
        :return:
        """
        return self.add("([^{value}]*)".format(value=value))

    def end_of_line(self):
        """
        Add a end of line.
        :return:
        """
        return self.add("$")

    @re_formatter
    def maybe(self, value):
        """
        Add a optional value.
        :param value:
        :return:
        """
        return self.add("({value})?".format(value=value))

    def start_of_line(self):
        """
        Add a start of line.
        :return:
        """
        return self.add("^")

    @re_formatter
    def find(self, value):
        """
        Add a finder of a value.
        :param value:
        :return:
        """
        return self.add("({value})".format(value=value))

    @re_formatter
    def format_occurrence(self, number):
        """
        Format occurrence statement by passed number.
        :param number:
        :return:
        """
        if isinstance(number, int):
            return "{number:d}".format(number=number)
        elif isinstance(number, tuple) or isinstance(number, list):
            return "{min:d},{max:d}".format(min=number[0], max=number[1])

    @re_formatter
    def occurrence(self, num):
        """
        Add a occurrence statement by passed number.
        :param num:
        :return:
        """
        return self.add("{" + self.format_occurrence(num) + "}")

    @re_formatter
    def any(self, value):
        """
        Add a any statement for a value.
        :param value:
        :return:
        """
        return self.add("([{value}])".format(value=value))

    def line_break(self):
        """
        Add a line break.
        :return:
        """
        return self.add(r"(\n|(\r\n))")

    @re_formatter
    def dictionary(self, *args):
        """
        Add a dictionary of value passed by args.
        :param args:
        :return:
        """
        rang = [args[i: i + 2] for i in range(0, len(args), 2)]
        return self.add("([{arg}])".format(arg="".join(["-".join(i) for i in rang])))

    def tabulator(self):
        """
        Add a tabulator statement.
        :return:
        """
        return self.add(r"\t")

    def alphanumeric(self):
        """
        Add a alphanumeric statement.
        :return:
        """
        return self.add(r"(\w+)")

    def no_alphanumeric(self):
        """
        Add a no alphanumeric statement.
        :return:
        """
        return self.add(r"(\W+)")

    def digit(self):
        """
        Add a digit statement.
        :return:
        """
        return self.add(r"(\d+)")

    def no_digit(self):
        """
        Add a no digit statement.
        :return:
        """
        return self.add(r"(\D+)")

    def white_spaces(self):
        """
        Add a white space statement.
        :return:
        """
        return self.add(r"(\s+)")

    def no_white_spaces(self):
        """
        Add a no white spaces statement.
        :return:
        """
        return self.add(r"(\S+)")

    def anyone(self, value=None):
        """
        Add a or logical statement for a value.
        :param value:
        :return:
        """
        self.add("|")
        return self.find(value) if value else self

    def find_all(self, expression, string):
        """
        Find all occurrence for a expression in a string.
        :param expression:
        :param string:
        :return:
        """
        return self.findall(expression, string)

    def splitter(self, delimiter, string):
        """
        Return a splitter of a string delimiter for a char.
        :param delimiter:
        :param string:
        :return:
        """
        return self.split(delimiter, string) if delimiter else None

    def search_first(self, expression, string):
        """
        Return first search occurrence for a expression in a string.
        :param expression:
        :param string:
        :return:
        """
        return self.search(expression, string)

    def replace(self, string, repl):
        """
        Replace a value in a string.
        :param string:
        :param repl:
        :return:
        """
        return self.sub(repl, string)

    def with_ascii(self, value=False):
        """
        Add a with ascii statement.
        :param value:
        :return:
        """
        self.modifiers["A"] = re.A if value else 0
        return self

    def with_any_case(self, value=False):
        """
        Add a any case statement.
        :param value:
        :return:
        """
        self.modifiers["I"] = re.I if value else 0
        return self

    def locale_dependent(self, value=False):
        """
        Add a locale dependent statement.
        :param value:
        :return:
        """
        self.modifiers["L"] = re.L if value else 0
        return self

    def multiline(self, value=False):
        """
        Add a multiline statement.
        :param value:
        :return:
        """
        self.modifiers["M"] = re.M if value else 0
        return self

    def all_match(self, value=False):
        """
        Add all math statement.
        :param value:
        :return:
        """
        self.modifiers["S"] = re.S if value else 0
        return self

    def with_unicode(self, value=False):
        """
        Add a with unicode statement.
        :param value:
        :return:
        """
        self.modifiers["U"] = re.U if value else 0
        return self

    def verbose(self, value=False):
        """
        Add a verbose statement.
        :param value:
        :return:
        """
        self.modifiers["X"] = re.X if value else 0
        return self
