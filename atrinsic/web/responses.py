from django.template import loader
from django.conf import settings
from django.http import HttpResponse

# Attempt to import JSON serialization libraries
# cjson: C implementation (external)(fast)
# simplejson: Python implementation (django)(slower then cjson)
try:
    from cjson import encode
    json_encode = encode
except:
    from django.utils import simplejson
    json_encode = simplejson.dumps

class HttpNoCacheResponse(HttpResponse):
    def __init__(self, * args, ** kwargs):
        HttpResponse.__init__(self, * args, ** kwargs)

        self['Last-Modified'] = 'Mon, 01 Jan 1970 05:00:00 GMT'
        self['Cache-Control'] = 'no-store, no-cache, must-revalidate'
        self['Pragma'] = 'no-cache'

class HttpJSONResponse(HttpNoCacheResponse):
    def __init__(self, dict, status = 200):
        mimetype = 'application/json'
        if(settings.DEBUG):
            mimetype = 'text/html'
        HttpResponse.__init__(self, content = json_encode(dict), mimetype = mimetype, status = status)