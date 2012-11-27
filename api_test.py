#!/usr/bin/python

import urllib2,urllib
import httplib2
import simplejson

base_url = "http://atrinsic11.80concepts.com"

api_string ="api=True&api-version=1.0&api-output=json"

class Connection(object):
    def __init__(self,base_url,api_string):
        self.conn = httplib2.Http()
        self.api_string = api_string
        self.base_url = base_url
        self.cookies = ""

    def request(self,url,method="GET",headers=None,**kwargs):
        if headers:
            headers.update({'Content-type': 'application/x-www-form-urlencoded'})
        else:
            headers = {'Content-type': 'application/x-www-form-urlencoded'}
            
        if self.cookies:
            headers['Cookie'] = self.cookies

        url = self.base_url + url
        if url.find("?") == -1:
            url = url + "?%s" % self.api_string
        else:
            url = url + "&%s" % self.api_string
        
        response,content = self.conn.request(url,method,headers=headers,**kwargs)
        if response.has_key('set-cookie'):
            self.cookies = response['set-cookie']
            print self.cookies
        try:
            return response,simplejson.loads(content)
        except:
            pass
            
        return response,content
        
conn = Connection(base_url,api_string)

conn.request("/accounts/login/","POST",body=urllib.urlencode({'email':"demo@80concepts.com",'password':"123abc"}))
conn.request("/accounts/choice/3/")
import pprint


pprint.pprint(conn.request("/publisher/advertisers/my/")[1])
pprint.pprint(conn.request("/publisher/reports/?start_date=07/01/2009&end_date=07/17/2009&group_by=0&run_reporting_by=0&report_type=0&specific_advertiser=a_1&target=0")[1])

