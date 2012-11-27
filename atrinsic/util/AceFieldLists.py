from urllib import urlencode
from urllib2 import HTTPHandler
from django.http import HttpResponse
from urllib2 import Request
from urllib2 import build_opener
from xml.dom.minidom import Document
from xml.dom.minidom import parseString
from django.core.mail import mail_admins
from atrinsic.base.choices import *
from atrinsic import settings
import datetime

class Api(object):
    METHODS = [ 'GET', 'POST', 'PUT','DELETE', 'HEAD' ]

    def __init__(self):
        for x in range(0, len(self.METHODS)):
            setattr(self, self.METHODS[x], x)

    def __api__(self, url, method = None, params = {}, content_type = 'application/x-www-form-urlencoded'):
        try:        
            if(params.has_key('placement')):
                del params['extCompId']
            #try:
            if(not method): method = self.GET
    
            request_handler = build_opener(HTTPHandler)
            request_param = urlencode(params) or None
            request_url = url
        
            if(method in [self.GET, self.HEAD] and request_param):
                if(not request_url.endswith('?')):
                    request_url += '?'
                request_url += request_param
            print request_url
    
            request = Request(request_url, data = self.iif((method in [self.GET, self.HEAD]), None, request_param) )
    
            if(method in [self.POST, self.PUT, self.DELETE, self.HEAD]):
                request.add_header('Content-Type', content_type)
                request.add_header('Content-Length', len(request_param or ''))
                request.get_method = lambda: self.METHODS[method]
                
            response = request_handler.open(request)
    
            return True, response.code, response.msg, response.read()
        except Exception, e:
            return False, 500, str(e), '<No Content>'
    
    def iif(self, condition, true, false):
        if(condition):
            return true
        else:
            return false

class Ace(Api):
    __doc__ = 'A.C.E Api for creating and updating Company Information'

    def __init__(self, service_id = 9, url = 'http://sos.dev.corp.atrinsic.com/services/InsertionOrder.asmx/'):
        super(Ace, self).__init__()

        if(not url.endswith('/')):
            url += '/'
        self.url = url
        self.service_id = service_id
        
    def getSalesPersonList(self, **args):        
        return self.__execute__('SalesPersonList', args)
        
    def getPlacementFeesList(self, args):        
        return self.__execute__('GetFees', args)
        
    def getUnitTypesList(self, **args):        
        return self.__execute__('UnitTypesList', args)
        
    def __execute__(self, function, arguments):
        
        status, code, message, content = self.__api__('%s%s' % (self.url, function), self.POST, arguments)
        
        if(status and code == 200):
            return self.__parse__(content)
        else:
            return None

    def __parse__(self, content):
        #print content
        xml_dom = parseString(content)
        xml_dict = dict(Success = False)

        try:
            for content in xml_dom.getElementsByTagName('ArrayOfSalesPersonInfo'):
                xml_dict.clear()
                arrReturn = []
                for node in content.childNodes:
                    if(node.nodeType == 1):
                        if(node.nodeName in ['SalesPersonInfo']):   
                            temp_list = {}
                            for SPnode in node.childNodes:
                                if(SPnode.nodeType == 1):
                                    temp_list[SPnode.nodeName] = SPnode.childNodes[0].nodeValue
                            arrReturn.append(temp_list)
                            del xml_dict
                            xml_dict = arrReturn   
            for content in xml_dom.getElementsByTagName('ArrayOfUnitTypeInfo'):
                xml_dict.clear()
                arrReturn = []
                for node in content.childNodes:
                    if(node.nodeType == 1):
                        if(node.nodeName in ['UnitTypeInfo']):   
                            temp_list = {}
                            for SPnode in node.childNodes:
                                if(SPnode.nodeType == 1):
                                    temp_list[SPnode.nodeName] = SPnode.childNodes[0].nodeValue
                            arrReturn.append(temp_list)
                            del xml_dict
                            xml_dict = arrReturn   
            for content in xml_dom.getElementsByTagName('ArrayOfPlacementInfo'):
                xml_dict.clear()
                arrReturn = []
                temp_list = {}  
                for node in content.childNodes:
                    if(node.nodeType == 1):
                        if(node.nodeName in ['PlacementInfo']):
                            for PInode in node.childNodes:
                                if(PInode.nodeType == 1):  
                                    if(PInode.nodeName == 'Fees'):
                                        for Fnode in PInode.childNodes:
                                            if(Fnode.nodeType == 1):  
                                                if(Fnode.nodeName == 'PlacementFee'):
                                                    for PFnode in Fnode.childNodes:
                                                        if(PFnode.nodeType == 1):  
                                                            temp_list[PFnode.nodeName] = PFnode.childNodes[0].nodeValue
                                                    arrReturn.append(temp_list)  
                                                    temp_list = {}                          						
                                                
                xml_dict = arrReturn   
                print xml_dict
        except Exception, e:
            xml_dict = dict(Success = False, ErrorMessage = str(e))
        return xml_dict