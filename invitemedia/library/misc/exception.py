# $Id: exception.py 7458 2008-04-29 00:20:17Z brian $

"""
Provides some base exception classes for Invite Media.
"""

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Exports
# ---------------------------------------------------------------------------

__all__ = ['ExceptionWithMessage', 'CommandLineError']

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

class ExceptionWithMessage(Exception):
    """
    Useful base class for Invite Media exceptions that have a single
    exception message argument. Among other things, this method provides a
    reasonable default C{__str__()} method.

    Usage::

        from invitemedia.library.misc import BaseException
        class MyException(BaseException.ExceptionWithMessage):
            def __init__(self, msg):
                BaseException.ExceptionWithMessage.__init__(self, msg)
    """
    def __init__(self, errorMessage):
        self._msg = errorMessage

    @property
    def message(self):
        """
        The message stored with this object.
        """
        return self._msg

    def __str__(self):
        return '%s: %s' % (self.__class__.__name__, self._msg)

class CommandLineUtilityError(ExceptionWithMessage):
    """Thrown to indicate an error in a command line utility."""
    pass