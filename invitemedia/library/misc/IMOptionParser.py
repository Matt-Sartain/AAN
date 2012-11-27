#!/usr/bin/env python
#
# $Id: IMOptionParser.py 10726 2008-08-28 22:20:10Z brian $
# ---------------------------------------------------------------------------

# NOTE: Documentation is intended to be processed by epydoc and contains
# epydoc markup.

"""
Provides a front-end to the Python standard 'optparse' module. The
``IMOptionParser`` class makes two changes to the standard behavior.

- The output for the '-h' option is slightly different.
- A bad option causes the parser to generate the entire usage output,
  not just an error message.

It also provides a couple extra utility modules. In the future, it can
also be a place to put options that we want to be the same across all our
programs.
"""

__docformat__ = 'restructuredtext'

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

from optparse import OptionParser
import sys

from invitemedia.library.metaclass.singleton import MetaSingletonStrict
from invitemedia.library.misc.exception import ExceptionWithMessage

# ---------------------------------------------------------------------------
# Classes
# ---------------------------------------------------------------------------

class CommandLineUsageError(ExceptionWithMessage):
    """
    Thrown to indicate an error with the command line parameters.
    """
    pass

class IMOptionParser(OptionParser):
    """Custom version of command line option parser."""

    def __init__(self, *args, **kw_args):
        """ Create a new instance. """
        OptionParser.__init__(self, *args, **kw_args)

        # I like my help option message better than the default...
        self.remove_option('-h')
        self.add_option('-h', '--help', action='help',
                        help='Show this message and exit.')

    def addOption(self, *args, **kw):
        """
        Front-end to ``add_option()``. Exists solely for Camel-case
        consistency.
        """
        return self.add_option(*args, **kw)

    def addOptions(self, optionList):
        """
        Front-end to ``add_options()``. Exists solely for Camel-case
        consistency.
        """
        return self.add_options(optionList)

    def parseArgs(self, args=sys.argv):
        """
        Front-end to ``parse_args()``. Exists solely for Camel-case
        consistency.
        """
        return self.parse_args(args)

    def showUsage(self, msg=None):
        """
        Force the display of the usage message.

        :Parameters:
            msg : str
                If not set the ``None`` (the default), this message will
                be displayed before the usage message.
        """
        self.show_usage(msg)

    def show_usage(self, msg=None):
        """
        Force the display of the usage message.

        :Parameters:
            msg : str
                If not set the ``None`` (the default), this message will
                be displayed before the usage message.
        """
        if msg != None:
            print >> sys.stderr, msg
        self.print_help(sys.stderr)
        sys.exit(2)
        
    def error(self, msg):
        """
        Overrides parent C{OptionParser} class's C{error} message and
        forces the full usage message on error.
        """
        sys.stderr.write("%s: error: %s\n" % (self.get_prog_name(), msg))
        self.showUsage()

class IMOptionParserShared(IMOptionParser, object):
    """
    Shared option parsing class.

    Use of this class as an option parser allows separate packages in a 
    program to coordinate command line option parsing.  Each client of
    this class gets a shared, singleton instance on construction.  Clients
    may then add their options to the common pool of program options.  
    If two or more separate clients of the common option parsing class 
    use the same option, the L{C{OptionParser}<OptionParser>} I{resolve} 
    handler is used to resolve the conflicts, with front-end checks and 
    warnings issues in the case where suspected resolution will lead to 
    conflicts that should be resolved with code changes.

    Note that, in general, options that have the same type, destination, and
    action in separate parts of a program do not create conflict issues --
    typically, the intent is that these distinct parts of the overall program
    want the same behavior for the given option.  While it's best to segregate
    the options to a single place, that may not always be feasible and it may
    instead be desirable to have separate clients see the options as if they
    were theirs only.  This class facilitates that behavior.
    """

    #
    # Use the singleton metaclass.  Note that the base OptionParser class
    # is an old style class and metaclasses require new style classes.  The
    # inheritence from L{C{object}<object>} above enables that.
    #
    __metaclass__ = MetaSingletonStrict

    def __init__(self, **kwArgs):
        """
        Constructor.
        """

        # Construct via the parent class and set the default conflict handler.
        IMOptionParser.__init__(self, **kwArgs)
        if not kwArgs.has_key("conflict_handler"):
            self.set_conflict_handler("resolve")

    def add_option(self, *args, **kwArgs):
        """
        Add an option after first checking for problematic conflicts.
        """

        self._checkConflicting(*args, **kwArgs)
        IMOptionParser.add_option(self, *args, **kwArgs)

    def _checkConflicting(self, *args, **kwArgs):
        """
        Private method to check conflicts.
        """

        #
        # The easiest way to get consistent values to compare is to assign
        # the option to a parser of its own and get it in its standard, set
        # form.
        #
        parser = IMOptionParser()
        if not parser.has_option(args[0]):
            parser.add_option(*args, **kwArgs)
        new = parser.get_option(args[0])

        # Check each option string for conflicts.
        for opt in args:
            if self.has_option(opt):
                existing = self.get_option(opt)
                self._checkConflictingOpt(opt, existing, new)

    def _checkConflictingOpt(self, opt, existing, new):
        """
        Private method to check a single option conflict.
        """

        # Check the attributes where differences are problematic.
        for attr in ('action', 'type', 'dest'):
            if getattr(existing, attr) != getattr(new, attr):
                print >> sys.stderr, \
                      "Possible conflicting command line option '%s'." % opt
                break
