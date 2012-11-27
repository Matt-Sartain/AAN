# $Id: TestAbstract.py 5755 2008-02-26 15:52:53Z brian $
#
# Nose program for testing @abstract decorator.

from invitemedia.library.decorator import *

class AbstractClass(object):
    @abstract
    def abs(self):
        """ Abstract method """
        pass

class NotReallyConcrete(AbstractClass):
    pass

class Concrete(AbstractClass):
    def abs(self):
        """ Abstract method """
        return 1


class TestAbstract:
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testAbstractCall(self):
        obj = NotReallyConcrete()
        try:
            obj.abs()
            assert(False, "Didn't get expected UnimplementedMethodError")
        except UnimplementedMethodError:
            pass

    def testConcreteCall(self):
        obj = NotReallyConcrete()
        try:
            value = obj.abs()
            print value
        except UnimplementedMethodError:
            assert(False, "Got unexpected UnimplementedMethodError")

