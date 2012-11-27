# $Id: __init__.py 13003 2008-11-25 22:06:06Z kyle $

"""
Python decorators. To get all the decorators into the namespace, use::

    from invitemedia.library.decorator import *
"""

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

import sys

from invitemedia.library.misc import BaseException

# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class UnimplementedMethodError(BaseException.ExceptionWithMessage):
    """
    Thrown to indicate an unimplemented abstract method.
    """

    def __init__(self, msg):
        self.errorMessage = msg

    def __str__(self):
        return '%s: %s' % (self.__class__.__name__, self.errorMessage)

# ---------------------------------------------------------------------------
# Decorators
# ---------------------------------------------------------------------------

def abstract(func):
    """
    Decorator for marking a function abstract. Throws an
    L{UnimplementedMethodError} if an abstract method is called.

    Usage::

        from invitemedia.library.decorator import abstract

        class MyAbstractClass(object):

            @abstract
            def abstractMethod(self):
                pass

        class NotReallyConcrete(MyAbstractClass):
            # Class doesn't define abstractMethod().

    Given the above declaration, the following code will cause an
    L{UnimplementedMethodError}::

        obj = NotReallyConcrete()
        obj.abstractMethod()
    """
    def wrapper(*__args, **__kw):
        raise UnimplementedMethodError('Missing required %s() method' %\
                                       func.__name__)
    wrapper.__name__ = func.__name__
    wrapper.__dict__ = func.__dict__
    wrapper.__doc__ = func.__doc__
    return wrapper

import warnings
def deprecated(func):
    """
    Decorator for marking a function deprecated. Generates a warning on
    standard output if the function is called.

    Usage::

        from invitemedia.library.decorator import abstract

        class MyClass(object):

            @deprecated
            def oldMethod(self):
                pass

    Given the above declaration, the following code will cause a
    warning to be printed (though the method call will otherwise succeed).
    L{UnimplementedMethodError}::

        obj = MyClass()
        obj.oldMethod()
    """
    def wrapper(*__args, **__kw):
        warnings.warn('Method %s is deprecated.' % func.__name__,
                      category=DeprecationWarning, stacklevel=2)
        return func(*__args,**__kw)

    wrapper.__name__ = func.__name__
    wrapper.__dict__ = func.__dict__
    wrapper.__doc__ = func.__doc__
    return wrapper
    
def debug_call(func):
    out = sys.stderr
    
    def wrapper(*args, **kwds):
        dbg_message = ['- ' * 50]
        dbg_message.append('Function Call: %s' % func.__name__)
        
        dbg_message += ['- %s' % str(arg) for arg in args]
        dbg_message += ['- %s = %s' % (str(k), str(kwds[k])) for k in kwds.keys()]
        dbg_message.append('')
        
        out.write('\n'.join(dbg_message))
        result = func(*args, **kwds)
        
        out.write('\n*** Returned: %s\n\n' % str(result))
        return result
        
    wrapper.__name__ = func.__name__
    wrapper.__dict__ = func.__dict__
    wrapper.__doc__ = func.__doc__
    return wrapper
    
class with_retry:
    """
    Retry a method a maximum of `max_retry` times.  This is helpful for
    something like long-lived database or API connections which may need to be
    refreshed over time.

    For example, a connection to someone else's REST API which may time out
    after 30 minutes.  If being called from a long-running process, this will
    throw errors and die once the service has been running for 30 minutes.

    If an exception is thrown in the method, this decorator will re-try the call
    a maximum of `max_retry` times before giving up and re-raising the
    exception.
    """

    def __init__(self, max_retry=3):
        self.max_retry = max_retry

    def __call__(self, function):
        def retry_wrapper(*args, **kwds):
            print '- ' * 30
            print 'In retry wrapper'
            for i in range(0, self.max_retry):
                print 'ITERATING'
                try:
                    print 'Calling function'
                    return function(*args, **kwds)
                except:
                    if i == max_retry:
                        raise

        retry_wrapper.__name__ = function.__name__
        retry_wrapper.__dict__ = function.__dict__
        retry_wrapper.__doc__  = function.__doc__

        return retry_wrapper


from copy import deepcopy

def reset_defaults(f):
    """
    
    Decorator.
    
    Example:
    
    @reset_defaults
    def function(item, stuff = []):
        stuff.append(item)
        print stuff
    
    function(1)
    # prints '[1]'
    
    function(2)
    # prints '[2]', as expected
    
    Without this decorator:
    
     function(1)
    # prints '[1]'
    
    function(2)
    # prints '[1,2]', .... unexpected
    
    
    """
    defaults = f.func_defaults
    def resetter(*args, **kwds):
        f.func_defaults = deepcopy(defaults)
        return f(*args, **kwds)
    resetter.__name__ = f.__name__
    return resetter
