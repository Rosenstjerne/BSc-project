
# The philosophy for this teaching-oriented compiler is to catch the first
# error, report an appropriate error message, and terminate.


import sys


def error_message(phase, description, lineno):

    print(f"\nError in phase {phase}, line {lineno}:\n    {description}",
          file=sys.stderr)
    sys.exit(1)
