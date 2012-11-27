from django.utils import simplejson
from urllib2 import HTTPHandler
from urllib2 import Request
from urllib2 import build_opener
from atrinsic.base.models import WebRequest, AdvertiserImage
from atrinsic import settings
from atrinsic.web.helpers import base36_encode
from django.core.mail import mail_admins
from atrinsic.base.choices import *

class Api(object):
    METHODS = [ 'GET', 'POST', 'DELETE' ]
    
    def __init__(self):
        for x in range(0, len(self.METHODS)):
            setattr(self, self.METHODS[x], x)

    def __api__(self, url, method = None, data = {}, headers = {}):
    #try:
        request_handler = build_opener(HTTPHandler)
        request_url = url
        if len(data):
            request = Request(request_url, data = data)
        else:
            request = Request(request_url)        
 
        request.get_method = method
        
        if len(headers):
            for k, v in headers.iteritems():
                request.add_header(str(k), str(v))

        secureLog = 'Basic ' + 'adquotient:PrUt2ech'.encode('base64')[:-1]
        request.add_header('Authorization', secureLog)
        
        #print request_url
        response = request_handler.open(request)
        #print "about the return"
        return True, response.code, response.msg, response.read()
            
    #except Exception, e:
        #return False, None


class Ape(Api):
    __doc__ = 'APE System Calls'
        
    def execute_redirect_create(self):
        try:
            data = dict( max_age = 43200, default_url = '' )
            request_url = settings.APE_CREATE + 'redirect/'
            request_param = simplejson.dumps(data)
            method = lambda: 'POST'
            headers = {'Content-Type':'application/application/json','Content-Length':len(request_param) } 
    
            return self.__execute__(request_url, method, request_param, headers)

        
        except Exception, e:
            print str(e)
            mail_admins('Adquotient: APE Redirect Creation failed', '\r\n Failed: %s  ' % (str(e)), True)
        return False, None
        
    def execute_action_create(self, redirectId, actionName):
        try:
            data = dict( max_age = 60, default_url = '', name=actionName )
            #request_url = settings.APE_CREATE + 'redirect/' #/a/redirect/{redirect_id}/actions/
            request_url = '%sredirect/%s/actions/' % (settings.APE_CREATE, redirectId)
            request_param = simplejson.dumps(data)
            method = lambda: 'POST'
            headers = {'Content-Type':'application/application/json','Content-Length':len(request_param) } 
            print request_url
            return self.__execute__(request_url, method, request_param, headers)

        
        except Exception, e:
            print str(e)
            mail_admins('Adquotient: APE Redirect Creation failed', '\r\n Failed: %s  ' % (str(e)), True)
        return False, None
            
    def execute_url_create(self, Action, link = None, df = None):
    # Link is the link object passed to the function, df is the datafeed.
    
        method = lambda: 'POST'
        if Action.ape_redirect_id == None:
            success, content = self.execute_redirect_create()
            if success:
                Action.ape_redirect_id = content['redirect_id']
                Action.save()

        if link != None:      
            if link.landing_page_url == None or link.landing_page_url == "":
                return False, None
                
            if link.ape_banner_id == None or link.ape_banner_id == 0:
                if link.link_type == LINKTYPE_BANNER:                  
                    if link.banner_url == None or link.banner_url == "":
                        img = AdvertiserImage.objects.get(id=link.banner_id, advertiser=link.advertiser)
                        bannerURL = "http://cdn.network.atrinsic.com/" + str(img.image)
                    else:
                        bannerURL = link.banner_url
                else:
                    bannerURL = settings.CDN_HOST_URL + settings.APE_IMG_PIXEL
                       
                dataBanner = dict( url = str(bannerURL),
                             name = link.name,
                             ext_media_id = link.pk,
                             is_active = True,
                )
                request_url = settings.APE_CREATE + 'banner/'
                request_param = simplejson.dumps(dataBanner)            
                headers = {'Content-Type':'application/application/json','Content-Length':len(request_param) }
                success, content = self.__execute__(request_url, method, request_param, headers)

                if success:
                    link.ape_banner_id = content["banner_id"]
                    link.save()
                               
        if link != None:
            urltoApe = link.landing_page_url
        else:
            urltoApe = df.landing_page_url
          
            
        data = dict( url = urltoApe,
                     is_active = True,
        )
        request_url = settings.APE_CREATE + 'redirect/' + str(Action.ape_redirect_id) + "/urls/"

        request_param = simplejson.dumps(data)            
        headers = {'Content-Type':'application/application/json','Content-Length':len(request_param) } 
        success, content =  self.__execute__(request_url, method, request_param, headers)
        print content
        if success:
            if link != None:
                link.ape_url_id = content["url_id"]
                link.save()
            else:
                return content["url_id"]
        return True
    
   
        return False, None  
        
    def execute_piggyback_create(self, request, redirectId, pixelType, pbContent):
        try:
            data = dict( url = pbContent, type = pixelType)
            if request.organization.org_type == ORGTYPE_PUBLISHER:
                data.update({'pub_id': request.organization.id})

            request_url = '%sredirect/%s/pixels/' % (settings.APE_CREATE, redirectId)
            request_param = simplejson.dumps(data)
            method = lambda: 'POST'
            headers = {'Content-Type':'application/application/json','Content-Length':len(request_param) } 
            print request_url
            return self.__execute__(request_url, method, request_param, headers)

        
        except Exception, e:
            print str(e)
            mail_admins('Adquotient: APE Redirect Creation failed', '\r\n Failed: %s  ' % (str(e)), True)
        return False, None
        
    def execute_piggyback_update(self, request, redirectId, pixelID, pbContent):
        try:
            data = dict( url = pbContent)
            request_url = '%sredirect/%s/pixels/%s/' % (settings.APE_CREATE, redirectId, pixelID)
            request_param = simplejson.dumps(data)
            method = lambda: 'POST'
            headers = {'Content-Type':'application/application/json','Content-Length':len(request_param) } 
            print request_url
            return self.__execute__(request_url, method, request_param, headers)

        
        except Exception, e:
            print str(e)
            mail_admins('Adquotient: APE Redirect Creation failed', '\r\n Failed: %s  ' % (str(e)), True)
        return False, None
        
    def execute_piggyback_delete(self, request, redirectId, pixelID):
        try:
            request_url = '%sredirect/%s/pixels/%s/' % (settings.APE_CREATE, redirectId, pixelID)
            request_param = ""
            method = lambda: 'DELETE'
            headers = {'Content-Type':'application/application/json','Content-Length':len(request_param) } 
            print request_url
            return self.__execute__(request_url, method, request_param, headers)

        
        except Exception, e:
            print str(e)
            mail_admins('Adquotient: APE Redirect Creation failed', '\r\n Failed: %s  ' % (str(e)), True)
        return False, None

        
#############################################################################################################################
    def execute_redirect_chain(self, Action, link, landingPage = ""):
    	# Link is the link object passed to the function, df is the datafeed.
        try:
            method = lambda: 'POST'
            if Action.ape_redirect_id == None:
                success, content = self.execute_redirect_create()
                if success:
                    Action.ape_redirect_id = content['redirect_id']
                    Action.save()
                            
            if landingPage == None or landingPage == "":
                return False, None
            
            data = dict( url = landingPage,
                         is_active = True,
            )
            request_url = settings.APE_CREATE + 'redirect/' + str(Action.ape_redirect_id) + "/urls/"

            request_param = simplejson.dumps(data)            
            headers = {'Content-Type':'application/application/json','Content-Length':len(request_param) } 
            success, content =  self.__execute__(request_url, method, request_param, headers)
            if success:
                if link != None:
                    link.ape_url_id = content["url_id"]
                    link.save()
                else:
                    return content["url_id"]
            return True
        
        except Exception, e:
            print str(e)
            mail_admins('Adquotient: APE Chain Creation failed', '\r\n Failed: %s  ' % (str(e)), True)
        return False, None  
#############################################################################################################################

        
    def execute_url_update(self, ptAction, link = None, df = None):
    #try:
        method = lambda: 'POST'
        if link != None:      
            if link.ape_banner_id == None or link.ape_banner_id == 0:
                if link.link_type == LINKTYPE_BANNER:                  
                    if link.banner_url == None or link.banner_url == "":
                        img = AdvertiserImage.objects.get(id=link.banner_id, advertiser=link.advertiser)
                        bannerURL = "http://cdn.network.atrinsic.com/" + str(img.image)
                    else:
                        bannerURL = link.banner_url
                else:
                    # http://cdn.network.atrinsic.com/ + aan_pixel.gif
                    bannerURL = settings.CDN_HOST_URL + settings.APE_IMG_PIXEL
                        
                dataBanner = dict( url = bannerURL,
                             name = link.name,
                             ext_media_id = link.pk,
                             is_active = True,
                )
                request_url = settings.APE_CREATE + 'banner/'
                request_param = simplejson.dumps(dataBanner)            
                headers = {'Content-Type':'application/application/json','Content-Length':len(request_param) } 
                success, content = self.__execute__(request_url, method, request_param, headers)
                if success:
                    link.ape_banner_id = content["banner_id"]
                    link.save()
            
        if link != None:
            urltoApe = link.landing_page_url
            apeUrlID = link.ape_url_id
        else:
            urltoApe = df.landing_page_url
            apeUrlID = df.ape_url_id
                            
        data = dict( url = urltoApe,
                     is_active = True,
        )
        request_url = settings.APE_CREATE + 'redirect/' + str(ptAction.action.ape_redirect_id) + "/urls/" + str(apeUrlID) + "/"
        request_param = simplejson.dumps(data)
        headers = {'Content-Type':'application/application/json','Content-Length':len(request_param) } 
            
        return self.__execute__(request_url, method, request_param, headers)

    def execute_get_links(self,action):
        try:
            request_url = settings.APE_CREATE + 'redirect/'+str(action.ape_redirect_id)+'/urls/'
            method = lambda: 'GET'
            request_param = {}
            headers = {'Content-Type':'application/application/json'} 
            excution_response = self.__execute__(request_url, method, request_param, headers)
            return excution_response[1]['urls']

        except Exception, e:
            print str(e)
            mail_admins('Adquotient: APE Get Links failed', '\r\n Failed: %s  ' % (str(e)), True)
        return False, None

######################################################################################
# COMMISSION JUNCTION MAPPING
######################################################################################
    def execute_cj_create(self, pub_id, cj_pid):
        try:
            data = dict( publisher_id = pub_id, cj_id = cj_pid, is_active = True)

            request_url = settings.APE_CJ_CREATE_DEV
            request_param = simplejson.dumps(data)
            method = lambda: 'POST'
            headers = {'Content-Type':'application/application/json','Content-Length':len(request_param) }
            
            print request_url
            return self.__execute__(request_url, method, request_param, headers)
        
        except Exception, e:
            print str(e)
            mail_admins('Adquotient: APE Redirect Creation failed', '\r\n Failed: %s  ' % (str(e)), True)
        return False, None
        
    def execute_cj_update(self, pub_id, cj_pid, active=True):
        try:
            data = dict( publisher_id = pub_id, cj_id = cj_pid, is_active = active)

            request_url = "%s%s/" % (settings.APE_CJ_CREATE_DEV, data['publisher_id'])
            request_param = simplejson.dumps(data)
            method = lambda: 'POST'
            headers = {'Content-Type':'application/application/json','Content-Length':len(request_param) } 
            print request_url
            return self.__execute__(request_url, method, request_param, headers)
        
        except Exception, e:
            print str(e)
            mail_admins('Adquotient: APE Redirect Creation failed', '\r\n Failed: %s  ' % (str(e)), True)
        return False, None
        
    def execute_cj_get(self, pub_id, active=True):
        try:
            data = dict( publisher_id = pub_id, is_active = active)

            request_url = "%s%s/" % (settings.APE_CJ_CREATE_DEV, data['publisher_id'])
            request_param = simplejson.dumps(data)
            method = lambda: 'GET'
            headers = {'Content-Type':'application/application/json','Content-Length':len(request_param) } 
            print request_url
            return self.__execute__(request_url, method, request_param, headers)
        
        except Exception, e:
            print str(e)
            mail_admins('Adquotient: APE Redirect Creation failed', '\r\n Failed: %s  ' % (str(e)), True)
        return False, None
######################################################################################
    
    def __execute__(self, url, method, params, headers):

        status, code, message, content = self.__api__(url, method, params, headers)

        contentj = simplejson.loads(content)
        
        if(status and code == 200 and contentj['success'] == True):
            return True, contentj
        else:
            return False, None
        return False, None
                    
if __name__ == "__main__":
    client = Ape()
    #data = dict( max_age = 60, default_url = 'http://www.google.com' )
    response = client.execute_url_create()
