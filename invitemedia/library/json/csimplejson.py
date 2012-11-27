#!/usr/bin/env python
#
# $Id: csimplejson.py 11779 2008-10-08 22:24:25Z scott $
# ---------------------------------------------------------------------------

# NOTE: Documentation is intended to be processed by epydoc and contains
# epydoc markup.

"""
Wrapper to make python-cjson look like more like C{simplejson}. The
C{simplejson} module uses methods that mimic those in C{cPickle} and
C{marshal}. The CJSON library, on the other hand, provides just C{encode}
and C{decode} methods. This module wraps CJSON and provides methods that
make it look like C{simplejson}. Thus, you can substitute CSJON for
C{simplejson} by replacing::

    import simplejson

with::

    import csimplejson as simplejson

"""

import cjson
import traceback

def dumps(obj, skipkeys=False, ensure_ascii=True, check_circular=True,
          allow_nan=True, cls=None, indent=None, separators=None,
          encoding='utf-8', **kw):
    """
    Serialize C{obj} as a JSON formatted string, returning the string.

    @type obj:  any
    @param obj: The object to serialize

    @rtype: string
    @return: the JSON version of the object

    NOTE: The various keywords arguments are ignored; they only exist
    for calling compatibility with C{simplejson}.
    """
    try:    
        return cjson.encode(obj)
    except cjson.EncodeError:
        raise cjson.EncodeError("cannot encode object, "+\
                                "object was %s. Stack %s"%(obj,traceback.format_exc()))
 

def dump(obj, fp, skipkeys=False, ensure_ascii=True, check_circular=True,
         allow_nan=True, cls=None, indent=None, separators=None,
         encoding='utf-8', **kw):
    """
    Serialize C{obj} as a JSON formatted string, writing it to the
    specified file.

    @type obj:  any
    @param obj: The object to serialize

    @type fp:   file
    @param fp:  The file to which to write the JSON object

    NOTE: The various keywords arguments are ignored; they only exist
    for calling compatibility with C{simplejson}.
    """
    fp.write(dumps(obj))

def loads(string, encoding=None, cls=None, object_hook=None, **kw):
    """
    Deserialize a JSON string to a Python object.

    @type string:  string
    @param string: The JSON object to deserialize

    @rtype:  object
    @return: the deserialized Python object

    NOTE: The various keywords arguments are ignored; they only exist
    for calling compatibility with C{simplejson}.
    """
    try:
        return cjson.decode(string)
    except cjson.DecodeError:
        raise cjson.DecodeError("cannot decode string, "+\
                                "string was %s. Stack %s"%(string,traceback.format_exc()))

def load(fp, encoding=None, cls=None, object_hook=None, **kw):
    """
    Deserialize the contents of a file containing a JSON object to a Python
    object.

    @type fp:  file
    @param fp: The file to read

    @rtype:  object
    @return: the deserialized Python object

    NOTE: The various keywords arguments are ignored; they only exist
    for calling compatibility with C{simplejson}.
    """
    return loads(fp.read())
