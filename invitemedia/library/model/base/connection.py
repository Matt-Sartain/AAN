from invitemedia.library.json import csimplejson as json
from invitemedia.library.decorator import abstract

import sys
import logging
from logging import StreamHandler

class BaseConnection(object):
    def __init__(self):
        log = logging.getLogger('dashboard')
        if log.handlers == []:
            log.setLevel(logging.DEBUG)
            
            h1 = logging.StreamHandler()
            h1.setLevel(logging.DEBUG)
            log.addHandler(h1)

            h2 = StreamHandler(sys.stderr)
            h2.setLevel(logging.ERROR)
            log.addHandler(h2)
        
        self.log = log
        
    
    @abstract
    def login(self, username, password):
        pass
    
    @abstract
    def model(self, model_name):
        """
        Retrieve a subclass of BaseModel with the given name
        """
        pass
    
    @abstract
    def get(self, url, get={}):
        pass
    
    @abstract
    def delete(self, url, get={}, post={}):
        pass
    
    @abstract
    def post(self, url, get={}, post={}):
        pass
    
    @abstract
    def put(self, url, get={}, post={}):
        pass
    
    @classmethod
    def json_load(cls, content):
        return json.loads(content)
    
    @classmethod
    def json_dump(cls, content):
        return json.dumps(content)