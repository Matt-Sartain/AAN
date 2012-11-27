import urllib
import httplib2
import re
from invitemedia.library.json import csimplejson as simplejson
from urlparse import urlparse
from cgi import parse_qs
from atrinsic.base.models import WebRequest
from atrinsic import settings
from invitemedia.library.model import Model, BaseConnection
from invitemedia.library.decorator import reset_defaults

class Connection(BaseConnection):
    
    conn_cache = None
    cached = False
    
    def __init__(self, base_url, response_type='json'):       
        super(Connection, self).__init__()
        self.base_url = base_url
        self.response_type = response_type
        self.cookie = None
        self.connection = httplib2.Http("/tmp/.cache")
        self.username = None
        self.password = None
        Connection.conn_cache = self
        Connection.cached = True
        
    def login(self, username, password):
        self.username = username
        self.password = password
        url = "login/"
        self._request("GET", url, ignore_response=True)
        self._request("POST", url,
                      post={'username': username, 'password': password},
                      ignore_response=True)
    
    def model(self, model_name):
        return Model(model_name, self)

    def get(self, url, get={}, headers={}):
        return self._request("GET", url, get=get, headers=headers)
    
    def delete(self, url, get={}, post={}, headers={}):
        return self._request("DELETE", url, get=get, post=post, headers=headers)
    
    def post(self, url, get={}, post={}, headers={}):
        return self._request("POST", url, get=get, post=post, headers=headers)
    
    def put(self, url, get={}, post={}, headers= {}):
        get['_method'] = "PUT"
        return self._request("POST", url, get=get, post=post, headers=headers)

    @reset_defaults
    def _request(self, method, url, get={}, post={}, ignore_response=False, headers={}):
        orig_url = url
        orig_get = get
        orig_post = post
        
        url = self.base_url + url
        
        get['response_type'] = self.response_type
        if 'api_version' in get and isinstance(get['api_version'], list):
            get['api_version'] = get['api_version'][0]
        
        sep = '&' if '?' in url else '?'
        url = "%s%s%s" % (url, sep, urllib.urlencode(get))
        
        if self.cookie is not None:
            headers['Cookie'] = self.cookie
        
        # This is to handle lists of values being sent. Otherwise they show up
        # as the string representation of a Python list.
        post_tuples = []
        for key, value in post.items():
            if isinstance(value, list):
                for v in value:
                    post_tuples.append((key, v))
            else:
                post_tuples.append((key, value))
        
        body = urllib.urlencode(post_tuples)
        headers['Content-Length'] = str(len(body))

        print url
        try:
            response, content = self.connection.request(url, method,body=body,headers=headers)
            print "response : %s" % response
        except Exception, e:
            import sys
            import traceback
            raise Exception("%s" % [traceback.format_exc(), e, url, 
                                    method, urllib.urlencode(post)])
        
        if 'set-cookie' in response.keys():
            self._set_cookie(response['set-cookie'])
        location=''
        print response['status']
        if response['status'] == '302' or \
           ('content-location' in response and response.get('content-location') != url):
            if response['status'] == '302':
                raw_location = response['location']
                
            else:
                raw_location = response['content-location']
            
            location = urlparse(raw_location)
            path = location[2].replace("/", "", 1)
            
            if location[2].startswith('/login/'):
                self.login(self.username, self.password)
                return self._request(method, orig_url, orig_get, orig_post, 
                                     ignore_response)
            
            get_params = parse_qs(location[4])
            return self._request('GET', path, get=get_params, 
                                 ignore_response=ignore_response)
        
        print "ignore_response : %s" % ignore_response
        if not ignore_response:
            try:
                return self.json_load(content)
            
            except Exception, e:
                import traceback
                django_error = self.get_django_error_from_response(content)
                raise Exception("%s" % ["------------------------------------------------", 
                                        content, traceback.format_exc(), e, url, 
                                        method, urllib.urlencode(post), 
                                        "django_error = %s" % django_error])
                                        
        log=WebRequest(organization='Cronjob pid=%d  postparams%s' % (settings.INVITE_PARTNER_ID,post_tuples)  ,method=method ,url=url,request='%s%s' % (response,content),status=response['status'])
        log.save()                
    def _set_cookie(self, cookie_str):
        self.cookie = cookie_str.split(';')[0]
        
    def get_django_error_from_response(self,content):
        title_regex = re.compile(r'title>([^>]+)</title>')
        match = title_regex.search(content)
        if not match:
            return None
        else:
            return match.groups()[0]
