# -*- coding: utf-8 -*-
"""
TalosBDD execution file.
You can run this file via the IDE option or via command line.
"""
import sys

from arc.core.behave import runner
from arc.core.behave.runner import make_behave_argv


def main():
    """TalosBDD main function."""
    if sys.argv[1:]:
        runner.main(' '.join(sys.argv[1:]))

    else:
        runner.main(make_behave_argv(
            conf_properties='chrome',
            tags=['san_web']
        ))


if __name__ == '__main__':
    main()
