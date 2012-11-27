# $Id: TestJSON.py 6369 2008-03-13 00:32:53Z brian $
#
# Nose program for testing JSON libraries

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

from invitemedia.library.json import csimplejson

# ---------------------------------------------------------------------------
# Classes
# ---------------------------------------------------------------------------

class TestJSON(object):

    def testEncodeDecodeDict(self):
        d1 = {'a' : 1, 'b' : 2, 'c' : 300, 'd' : 'foo'}
        s = csimplejson.dumps(d1)
        d2 = csimplejson.loads(s)
        print '\nunencoded: %s\nencoded: %s\ndecoded: %s' % (d1, s, d2)
        assert d2 == d1

    def testEncodeDecodeList(self):
        list1 = [1, 2, 10, 3, 'abc', 'foobar', 3.1415]
        s = csimplejson.dumps(list1)
        list2 = csimplejson.loads(s)
        print '\nunencoded: %s\nencoded: %s\ndecoded: %s' % (list1, s, list2)
        assert list2 == list1

    def testEncodeDecodeComplicated(self):
        d1 = {'a' : 1, 'b' : 2, 'c' : 300, 'd' : 'foo'}
        list1 = [1, 2, 10, 3, 'abc', 'foobar', 3.1415, d1]
        s = csimplejson.dumps(list1)
        list2 = csimplejson.loads(s)
        print '\nunencoded: %s\nencoded: %s\ndecoded: %s' % (list1, s, list2)
        assert list2 == list1

