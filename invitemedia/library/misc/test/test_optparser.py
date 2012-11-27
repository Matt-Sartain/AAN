#
# $Id: sharedopts.py 7103 2008-04-10 15:07:35Z steves $
#

"""
Shared command line options example.
"""

from invitemedia.library.misc.IMOptionParser import IMOptionParserShared as OptionParser
from invitemedia.library.iocapture import IOCapture

import sys



        
def test_conflicting():        
    #Option parser instances (should all be the same)
    assert One.optParser == Two.optParser
    assert One.optParser == Three.optParser
    validOutput = "Possible conflicting command line option '--conflicting'."
    IOCapture.startCapture()
    index = IOCapture.startListening()
        
    One.addOpts()
    Two.addOpts()
    
    result = IOCapture.getListener(index)
    IOCapture.stopCapture()            
    assert result == validOutput+"\n","result should be '"+validOutput+"\n' but its '"+result+"'"
    
    
    #ensure that possible conflict was printed
    


def test_double_dash():
    optParser = OptionParser()
    sys.argv = ["","--field1=value"]
    optParser.add_option("--field1", dest="field1")
    (opts, args) = optParser.parse_args()
    print opts
    print args    
    assert opts.field1 == "value"


def test_single_dash():
    optParser = OptionParser()
    sys.argv = ["","-f","value"]
    optParser.add_option("-f", dest="field1")
    (opts, args) = optParser.parse_args()
    print opts
    print args
    assert opts.field1 == "value"
    
def test_differing_destination_and_name():
    optParser = OptionParser()
    sys.argv = ["","--field3=value3"]
    optParser.add_option("--field3", dest="field2")
    (opts, args) = optParser.parse_args()
    print opts
    print args
    assert opts.field2 == "value3"
    

#@TODO reset opt parser between tests    
def test_defaults():
    optParser = OptionParser()
    sys.argv = [""]
    optParser.add_option("--field4", dest="field4",default="defaultValue")
    (opts, args) = optParser.parse_args()
    print opts
    print args
    assert opts.field4 == "defaultValue"


class One(object):
    optParser = OptionParser()

    @classmethod
    def addOpts(self):
        self.optParser.add_option("--opt1", dest="opt1")
        self.optParser.add_option("--shared", dest="shared")
        self.optParser.add_option("--conflicting", dest="conflicting1")

    @classmethod
    def getOpts(self):
        (opts, args) = self.optParser.parse_args()
        print "%s opts: %s, %s" % (self.__name__, opts, args) 


class Two(object):
    optParser = OptionParser()

    @classmethod
    def addOpts(self):
        self.optParser.add_option("--opt2", dest="opt2")
        self.optParser.add_option("--conflicting", dest="conflicting2")

    @classmethod
    def getOpts(self):
        (opts, args) = self.optParser.parse_args()
        print "%s opts: %s, %s" % (self.__name__, opts, args) 

class Three(object):
    optParser = OptionParser()

    @classmethod
    def addOpts(self):
        self.optParser.add_option("--opt3", dest="opt3")
        self.optParser.add_option("--shared", dest="shared")

    @classmethod
    def getOpts(self):
        (opts, args) = self.optParser.parse_args()
        print "%s opts: %s, %s" % (self.__name__, opts, args) 

    