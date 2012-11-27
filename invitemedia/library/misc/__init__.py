# $Id: __init__.py 10896 2008-09-08 15:45:19Z brian $

"""
This package contains miscellaneous functions, classes, and modules.
"""

__docformat__ = 'restructuredtext'

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

import sys

# ---------------------------------------------------------------------------
# Exports
# ---------------------------------------------------------------------------

__all__ = ['die']

# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------

def die(msg, exit_code=1):
    """
    Print a message to standard error and exit. It's deliberately reminiscent
    of the *perl* ``die()`` built-in.

    :Parameters:
        msg : str
            The message to print
        exit_code : int
            The desired process exit code
    """
    print >> sys.stderr, msg
    sys.exit(exit_code)
