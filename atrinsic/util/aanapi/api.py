from urllib import urlencode
from urllib2 import build_opener, HTTPHandler, Request
#Author: 	Michel Page
#date:		02/10/2010

#NOTES
# - When instantiating Api you must implicitly call its constructor if sub class also contains a constructor

class Api(object):
    def __init__(self,url):
        self.url = url
        self.params = {}
        self.method = "GET"
    
    def apiCall(self):
        print "URL: " + self.url
        if self.method != "POST":
            response = self.apiGet()
        else:
            response = self.apiPost(self.params)
        
        return response
                
    def apiGet(self):
        import urllib2
        print "APIGET"
        request_handler = build_opener(HTTPHandler)

        request = Request(self.url)
		
        if self.method == 'DELETE':
        	request.get_method = lambda: 'DELETE'

        print request.get_method()
        
        response = request_handler.open(request)

        return response.read()
        
    def apiPost(self, params):
        print "API POST"
    	import urllib
        import urllib2
        
        data = urllib.urlencode(params)
        '''print"data"
        print data'''
        #Works but returns invalid campaginId
        ''' 
        response = urllib.urlopen(self.url, data)
        print response.info()
        the_page = response.read()
        
        return the_page
        '''
        
        # Using urllib2 and itsd Request object returns HTTP 404
        
        req = urllib2.Request(self.url, data)
        #print data
        print "Before call"
        try:
            response = urllib2.urlopen(self.url, data)
            the_page = response.read()
        except Exception, e:
            print e
        print "after call"
        #print the_page
        return the_page
        
        
        
        
        '''
        request = urllib2.Request(self.url)
        print request.get_method()
        request.add_data(newparams)
        print request.get_method()
        response = urllib2.urlopen(request)
        #response = urllib.urlopen(self.url, newparams)
        return response.read()
        '''

        #Ace api way using headers etc...
        ''' 
        content_type = 'application/x-www-form-urlencoded'
        request_handler = build_opener(HTTPHandler)

        request_param = urlencode(params) or None
        request_url = self.url
        request = Request(request_url, data = 'true')
         
        request.add_header('Content-Type', content_type)
        request.add_header('Content-Length', len(request_param or ''))
        request.get_method = lambda: 'POST'
        request.add_data(request_param)
        
        response = request_handler.open(request)
        print "after:"      
        
        respCode = response.code
        respMsg = response.msg
        respContent = response.read()
        
        print "MSG:"
        print respMsg
        
        return respContent
        '''
        
        #using HTTPConnection object
        '''
        import httplib, urllib
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
        conn = httplib.HTTPConnection(self.url+':80')
        conn.request("POST", "/cgi-bin/query", params, headers)
        response = conn.getresponse()
        print "Query is done:"
        print response.status, response.reason
        
        data = response.read()
        print data
        conn.close()
        '''

        
        
        
        
        
        