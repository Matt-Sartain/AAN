import datetime
from django.core.mail import mail_admins
from django.http import HttpResponse
from django.utils import simplejson
from django.utils.encoding import smart_str, smart_unicode
from atrinsic.base.models import Organization, Countries, OrganizationContacts, WebRequest,Organization_IO, ProgramTermAction
from atrinsic.base.choices import *
from atrinsic import settings
from urllib import urlencode
from urllib2 import build_opener, HTTPHandler, Request
from xml.dom.minidom import Document, parseString

__author__="charles.murray"
__date__ ="$Jul 14, 2009 4:32:50 PM$"

class Api(object):
    METHODS = [ 'GET', 'POST', 'PUT','DELETE', 'HEAD' ]

    def __init__(self):
        for x in range(0, len(self.METHODS)):
            setattr(self, self.METHODS[x], x)

    def __api__(self, url, method = None, params = {}, content_type = 'application/x-www-form-urlencoded'):

        
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
        
        print request_param
        request = Request(request_url, data = self.iif((method in [self.GET, self.HEAD]), None, request_param) )

        if(method in [self.POST, self.PUT, self.DELETE, self.HEAD]):
            request.add_header('Content-Type', content_type)
            request.add_header('Content-Length', len(request_param or ''))
            request.get_method = lambda: self.METHODS[method]
        
        response = request_handler.open(request)
        respCode = response.code
        respMsg = response.msg
        respContent = response.read()

        x = WebRequest.objects.create(method=self.POST,url=request_url, user='No User', length=0, status=respCode, request = 'URL:%s, POST:%s, ARGS:%s' % (request_url, self.POST, params))
        x.save()
        print "after webrequest"
        return True, respCode, respMsg, respContent
    #except Exception, e:
        #return False, 500, str(e), '<No Content>'
    
    def iif(self, condition, true, false):
        if(condition):
            return true
        else:
            return false

class Ace(Api):
    __doc__ = 'A.C.E Api for creating and updating Company Information'
    # Refer to the URL for parameters that are required. Ex. http://sos.dev.corp.atrinsic.com/services/CompanyExt.asmx
    def __init__(self, service_id = 9, url = settings.ACE_COMPANYCONTACT_URL):
        super(Ace, self).__init__()

        if(not url.endswith('/')):
            url += '/'
        self.url = url
        self.service_id = service_id

    def create(self, **args):
        if(not args.has_key('compShort')):
            if(args.has_key('compLong')):
                args.update(dict(compShort = args['compLong'][:15] ))
        print "Execute"
        return self.__execute__('Create', args)
    
    def search(self, **args):
        print "Execute search"
        
        status, code, message, content = self.__api__('%s%s' % (self.url, 'Search'), self.POST, args)

        result = {}
        if(status and code == 200):
            xml_dom = parseString(content)
            for node in xml_dom.getElementsByTagName('CompanyInfo'):
                company = {}
                for child in node.childNodes:
                    if(child.nodeType == 1):
                        if child.nodeName == 'CompanyId':
                            aceid = child.childNodes[0].nodeValue
                        if child.nodeName != 'LegalEntity':      
                            if len(child.childNodes) > 0:
                                company[child.nodeName] = child.childNodes[0].nodeValue
                result[aceid] = company
                        
            return result        
        else:
            return False, None, '%s: %s' % (code, message)      

    def create_contact(self, **args):
        return self.__execute__('ContactCreate', args)
        
    def create_io(self, **args):    
        self.url = settings.ACE_IO_URL
        return self.__execute__('Create', args)
        
    def get_io(self, **args):      
        self.url = settings.ACE_IO_URL
        return self.__execute__('Get', args)
            
    def create_iodetail(self, **args):       
        self.url = settings.ACE_IO_URL
        return self.__execute__('DetailCreate', args)    
                
    def update_iodetail(self, **args):      
        self.url = settings.ACE_IO_URL
        return self.__execute__('DetailUpdate', args)
        
    def update_iostatus(self, **args):      
        self.url = settings.ACE_IO_URL
        return self.__execute__('OrderStatusUpdate', args)
        
    def search_ios(self, **args):       
        self.url = settings.ACE_IO_URL
        return self.__execute__('Search', args)
                
    def create_fee(self, **args):       
        self.url = settings.ACE_IO_URL
        return self.__execute__('FeeCreate', args)
                
    def get_fees(self, **args):       
        self.url = settings.ACE_IO_URL
        return self.__execute__('GetFees', args)
        
    def delete_fees(self, **args):        
        self.url = settings.ACE_IO_URL
        return self.__execute__('FeeDelete', args)
                
    def create_po(self, **args):
        self.url = settings.ACE_PO_URL
        return self.__execute__('CreateOrderAndDetail', args)
        
    def status_po(self, **args):  
        self.url = settings.ACE_PO_URL
        return self.__execute__('StatusGet', args)
        
    def update(self, **args):
        if(not args.has_key('compShort')):
            if(args.has_key('compLong')):
                args.update(dict(compShort = args['compLong'][:15] ))
        if(not args.has_key('compId')):
            if(not args.has_key('extCompId')):
                raise Exception('Require compId, or extCompId.')
        return self.__execute__('Update', args)        

    def update_contact(self, **args):
        return self.__execute__('ContactUpdate', args)
                    
    def get_country_code(self, country):
        if(country != None):
            if(len(country) == 2):
                return country
        else:
            country = 'US'
            return country

        try:
            country = Countries.objects.get( name = country )
            return country.abreviation
        except Countries.DoesNotExist:
            return country
        
    def __execute__(self, function, arguments):
        if(not arguments.has_key('extCompId')):
            arguments.update(dict(extCompId = '0'))
        if(arguments.has_key('country')):
            arguments['country'] = self.get_country_code(arguments['country'])
            if arguments['country'] == "USA":
                 arguments['country'] = "US"
        arguments.update(dict(serviceId = self.service_id))

        status, code, message, content = self.__api__('%s%s' % (self.url, function), self.POST, arguments)

        if(status and code == 200):
            return True, self.__parse__(content), (code, message)
        else:
            return False, None, '%s: %s' % (code, message)

    def __parse__(self, content):
        xml_dom = parseString(content)
        xml_dict = dict(Success = False)
        try:
            for content in xml_dom.getElementsByTagName('CompanyServiceResult'):
                for node in content.childNodes:
                    if(node.nodeType == 1):
                        if(node.nodeName in ['Success', 'ErrorMessage', 'CompanyId']):
                            xml_dict.update({ node.nodeName: node.childNodes[0].nodeValue })
            for content in xml_dom.getElementsByTagName('CompanyServiceContactResult'):
                for node in content.childNodes:
                    if(node.nodeType == 1):
                        if(node.nodeName in ['Success', 'ErrorMessage', 'ContactId']):
                            xml_dict.update({ node.nodeName: node.childNodes[0].nodeValue })
            for content in xml_dom.getElementsByTagName('InsertionOrderServiceResult'):                
                for node in content.childNodes:                    
                    if(node.nodeType == 1):
                        for IOnode in node.childNodes:
                            if(IOnode.nodeType == 1):
                                try:
                                    if(IOnode.nodeName in['InsertionOrderId', 'IoDetailId', 'InsertionOrderSymbol']):
                                        xml_dict.update({ IOnode.nodeName: IOnode.childNodes[0].nodeValue })
                                except:
                                    pass	                                
                        if(node.nodeName in ['Success', 'CompanyId', 'InsertionOrderId','ErrorMessage']):
                            try:
                                xml_dict.update({ node.nodeName: node.childNodes[0].nodeValue })
                            except:
                                xml_dict.update({ node.nodeName: '' })
            for content in xml_dom.getElementsByTagName('PurchaseOrderServiceResult'):
                for node in content.childNodes:                    	                
                    if(node.nodeType == 1):
                        if(node.nodeName in ['PurchaseOrder', 'PurchaseOrderDetail']):
                            for POnode in node.childNodes:
                                if(POnode.nodeType == 1):
                                    if(POnode.nodeName in['PurchaseOrderId', 'PoDetailId', 'PurchaseOrderSymbol']): 
                                        xml_dict.update({ POnode.nodeName: POnode.childNodes[0].nodeValue })
                        if(node.nodeName in ['Success']):
                            try:
                                xml_dict.update({ node.nodeName: node.childNodes[0].nodeValue })
                            except:
                                xml_dict.update({ node.nodeName: '' })
            for content in xml_dom.getElementsByTagName('InsertionOrderInfo'):
                for node in content.childNodes:                    
                    if(node.nodeType == 1):
                        for IOnode in node.childNodes:
                            if(IOnode.nodeType == 1):
                                if(IOnode.nodeName == 'StatusName'):
                                    xml_dict.update(trim({ IOnode.nodeName: IOnode.childNodes[0].nodeValue }))
                        if(node.nodeName in ['StatusName']):
                            try:
                                xml_dict.update({ node.nodeName: node.childNodes[0].nodeValue })
                            except:
                                xml_dict.update({ node.nodeName: '' })
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
 
            for content in xml_dom.getElementsByTagName('ArrayOfInsertionOrderInfo'):
                xml_dict.clear()
                arrReturn = []
                temp_list = {}  
                for node in content.childNodes:
                    if(node.nodeType == 1):
                        if(node.nodeName == 'InsertionOrderInfo'):
                            for IOnode in node.childNodes:
                                if(IOnode.nodeType == 1):  
                                    if(IOnode.nodeName in ['InsertionOrderSymbol','InsertionOrderId']):
                                        temp_list[IOnode.nodeName] = IOnode.childNodes[0].nodeValue
                                    if(IOnode.nodeName == 'Offer'):
                                        for Onode in IOnode.childNodes:
                                            if(Onode.nodeType == 1):  
                                                if(Onode.nodeName == 'OfferName'):
                                                    temp_list[Onode.nodeName] = Onode.childNodes[0].nodeValue
                            arrReturn.append(temp_list)  
                            temp_list = {} 

                xml_dict = arrReturn                 
        except Exception, e:
            xml_dict = dict(Success = False, ErrorMessage = str(e))
        return xml_dict

        
        
def create_company(organization):
    try:
        print "AceApi - create_company"
        if organization.ace_id != None and int(organization.ace_id) != 0:
            return True

        if len(organization.company_alias) > 0:
            strCompLong = organization.company_alias
        else:
            strCompLong = organization.company_name
        client = Ace()
        response = client.create(   extCompId = organization.pk,
                                    compLong = smart_str(strCompLong),
                                    add1 = smart_str(organization.address),
                                    add2 = smart_str(organization.address2),
                                    city = smart_str(organization.city),
                                    state = organization.state,
                                    region = '',
                                    country = organization.country,
                                    zip = organization.zipcode
        )

        if(response[0]):
            if(response[1]['Success'].lower() == 'true'):
                # OnSuccess: set the ace_id to the returned CompanyId
                organization.ace_id = response[1]['CompanyId']
                organization.save()                
                create_contact(organization)
                return True
            raise Exception(response[1]['ErrorMessage'])
    except Exception, e:
        print str(e)
        mail_admins('Adquotient -> Ace: Create Company failed', 'Organization: %s \r\n Failed: %s  ' % (organization.pk, str(e)), True)
    return True  

def search_company(orgName):
    try:
        print "AceApi - search_company"
       
        client = Ace()
        response = client.search(searchString = orgName)

        return response

    except Exception, e:
        print str(e)
        return False
  
def update_company(organization):
    try:
        print "AceApi - update_company"
        client = Ace()	
        response = client.update(   compId = organization.ace_id or '0',
                                    extCompId = organization.pk,
                                    compLong = organization.company_name,
                                    add1 = organization.address,
                                    add2 = organization.address2,
                                    city = organization.city,
                                    state = organization.state,
                                    region = '',
                                    country = organization.country,
                                    zip = organization.zipcode
        )        
        if(response[0]):
            if(response[1]['Success'].lower() == 'true'):
                # OnSuccess: set the ace_id to the returned id if None or 0
                if(organization.ace_id == None or organization.ace_id == 0):
                    organization.ace_id = response[1]['CompanyId']    
                    organization.save()
                return True
            raise Exception(response[1]['ErrorMessage'])
    except Exception, e:
        print str(e)
        mail_admins('Adquotient: Ace company update failed', 'Organization: %s \r\n Failed: %s  ' % (organization.pk, str(e)), True)
    return True
    
        
def create_contact(organization):
    try:    
        print "AceApi - create_contact"
        orgContact = OrganizationContacts.objects.get(organization=organization)

        if(organization.org_type == ORGTYPE_ADVERTISER):                
            # Send default Contact if Advertiser
            orgContactName = orgContact.firstname + " " + orgContact.lastname
        else:
            # Send Payee Contact if Publisher
            orgContactName = orgContact.payeename
        
        # Send Contact Information to ACE
        client = Ace()
        responseContact = client.create_contact( compId = organization.ace_id,
                                                 contactName = smart_str(orgContactName),
                                                 add1 = smart_str(orgContact.address),
                                                 add2 = smart_str(orgContact.address2),
                                                 city = smart_str(orgContact.city),
                                                 state = orgContact.state,
                                                 country = orgContact.country,
                                                 region = '',
                                                 zip = orgContact.zipcode,
                                                 phone = orgContact.phone.replace(" ",""),
                                                 ext = 0,
                                                 pager = orgContact.phone.replace(" ",""),
                                                 mobile = orgContact.phone.replace(" ",""),
                                                 fax = orgContact.fax,
                                                 email = orgContact.email,
                                                 extCompanyId = organization.pk,
                                                 extContactId = orgContact.id,
                                                 remit = False,
        )
        if(responseContact[0]):
            if(responseContact[1]['Success'].lower() == 'true'):
                print "create_contact - id = " + str(responseContact[1]['ContactId'])
                orgContact.ace_contact_id = responseContact[1]['ContactId']
                orgContact.save()
                return True
            raise Exception(responseContact[1]['ErrorMessage'])
    except Exception, e:
        print str(e)
        mail_admins('Adquotient -> Ace: Create Contact failed', 'Organization: %s \r\n Failed: %s  ' % (organization.pk, str(e)), True)
    return True       
     
def update_contact(organization):
    try:    
        print "AceApi - update_contact"
        orgContact = OrganizationContacts.objects.get(organization=organization)
        if(organization.org_type == ORGTYPE_ADVERTISER):                
            # Send default Contact if Advertiser
            orgContactName = orgContact.firstname + " " + orgContact.lastname
        else:
            # Send Payee Contact if Publisher
            orgContactName = orgContact.payeename
        
        # Send Contact Information to ACE
        client = Ace()
        responseContact = client.update_contact( contactId = orgContact.ace_contact_id,
                                                 compId = organization.ace_id,
                                                 contactName = orgContactName,
                                                 add1 = orgContact.address,
                                                 add2 = orgContact.address2,
                                                 city = orgContact.city,
                                                 state = orgContact.state,
                                                 country = orgContact.country,
                                                 region = '',
                                                 zip = orgContact.zipcode,
                                                 phone = orgContact.phone.replace(" ",""),
                                                 ext = 0,
                                                 pager = orgContact.phone.replace(" ",""),
                                                 mobile = orgContact.phone.replace(" ",""),
                                                 fax = orgContact.fax,
                                                 email = orgContact.email,
                                                 extCompanyId = organization.pk,
                                                 extContactId = orgContact.id
        )        
        if(responseContact[0]):
            if(responseContact[1]['Success'].lower() == 'true'):
                return True
            raise Exception(responseContact[1]['ErrorMessage'])
    except Exception, e:
        print str(e)
        mail_admins('Adquotient -> Ace: Create Contact failed', 'Organization: %s \r\n Failed: %s  ' % (organization.pk, str(e)), True)
    return True

def createIO(organization, args):

    print "AceApi - createIO"
    orgContact = OrganizationContacts.objects.get(organization=organization)
    # ACE API call for IO creation.            
    client = Ace()
    responseIO = client.create_io (company = organization.ace_id,
                                 placement = 1,
                                 offer = smart_str(organization.company_name),
                                 startDate = str(datetime.date.today()),
                                 endDate = str(datetime.date.today() + datetime.timedelta(weeks=104)),
                                 salesrep = args["salesrep"],
                                 contactbill = orgContact.ace_contact_id,
                                 contactop = orgContact.ace_contact_id         
    )
    if(responseIO[0]):
        if(responseIO[1]['Success'].lower() == 'true'):
            try:
                orgIO = Organization_IO.objects.get(organization=organization)
            except:
                orgIO = None
            if orgIO == None:
                Organization_IO.objects.create(organization=organization, 
                                                     ace_id = organization.ace_id,
                                                     ace_ioid = responseIO[1]['InsertionOrderId'],
                                                     ace_iosymbol = responseIO[1]['InsertionOrderSymbol'],
                                                     salesrep = args["salesrep"]
                )                    
            else:	
                orgIO.ace_id = organization.ace_id
                orgIO.ace_ioid = responseIO[1]['InsertionOrderId']
                orgIO.salesrep = args["salesrep"]
                orgIO.save()
            return True
        print responseIO[1]['ErrorMessage']
        return False
        #raise Exception(responseIO[1]['ErrorMessage'])
    #except Exception, e:
    #mail_admins('Adquotient -> Ace: Create Insertion Order failed', 'Organization: %s \r\n Failed: %s  ' % (organization.pk, str(e)), True)
    
    #return True
    
def getIO(organization, args):
    # TODO: issue ACE API call to get IO based on ioId.
    client = Ace()
    responseGetIO = client.get_io (ioId = args["ioId"])
    print responseGetIO
    return responseGetIO[1]    

    
def createIODetail(organization, args, prgmTerm):
    try:
        try:
            orgIO = Organization_IO.objects.get(organization=organization)   
        except:
            createIO(organization, args)    
            orgIO = Organization_IO.objects.get(organization=organization)   
     
        client = Ace()
        responseIODetail = client.create_iodetail (ioid = orgIO.ace_ioid,
                                             tag = args["tag"],
                                             rate = args["rate"],
                                             startDate = str(datetime.date.today()),
                                             endDate = str(datetime.date.today() + datetime.timedelta(weeks=12)),
                                             payTerms = 4,
                                             unitType = args["unitType"],
                                             feeid = orgIO.transaction_fee_type,
                                             feeAmount = orgIO.transaction_fee_amount,
                                             spid = args["salesrep"]
        )    
        #jsonResult = simplejson.dumps(responseIODetail[1])
        if(responseIODetail[0]):
            if(responseIODetail[1]['Success'].lower() == 'true'):
                prgmTerm.ace_iodetailid = responseIODetail[1]['IoDetailId']
                prgmTerm.save()
                return True
            print responseIODetail
            raise Exception(responseIODetail[1]['ErrorMessage'])
    except Exception, e:
        mail_admins('Adquotient -> Ace: Create Insertion Order Detail failed', 'Organization: %s \r\n Failed: %s  ' % (organization.pk, str(e)), True)
        
    return True   
     
def updateIODetail(organization, args, action):
    try:
        # TODO: issue ACE API call for IODetail Create.
        orgIO = Organization_IO.objects.get(organization=organization)   
     
        client = Ace()
        responseIODetail = client.update_iodetail (ioid = orgIO.ace_ioid,
                                             ioDetail = args["ioDetail"],
                                             tag = args["tag"],
                                             rate = args["rate"],
                                             startDate = str(datetime.date.today()),
                                             endDate = str(datetime.date.today() + datetime.timedelta(weeks=12)),
                                             payTerms = 4,
                                             unitType = args["unitType"],
                                             feeid = orgIO.transaction_fee_type,
                                             feeAmount = orgIO.transaction_fee_amount,
                                             spid = args["salesrep"]
        )    
        if(responseIODetail[0]):
            if(responseIODetail[1]['Success'].lower() == 'true'):
                orgIO.salesrep = args["salesrep"]
                orgIO.save()
                return True
            raise Exception(responseIODetail[1]['ErrorMessage'])
    except Exception, e:
        mail_admins('Adquotient -> Ace: Update Insertion Order Detail failed', 'Organization: %s \r\n Failed: %s  ' % (organization.pk, str(e)), True)
        
    return True

def createFee(organization, args):
    try:
        # TODO: issue ACE API call for IODetail Create.
        orgIO = Organization_IO.objects.get(organization=organization)   
     
        client = Ace()
        responseFee = client.create_fee(ioid = orgIO.ace_ioid,
                                             feeid = args["feeId"],
                                             ioDetail = 0,
                                             feeAmount = args["feeAmount"],
                                             spid = args["spId"])    
    
        if(responseFee[0]):
            if(responseFee[1]['Success']):
                return True
    except Exception, e:
        mail_admins('Adquotient -> Ace: Create Insertion Order Detail failed', 'Organization: %s \r\n Failed: %s  ' % (organization.pk, str(e)), True)
        
    return True 

def getFees(organization):
    try:
        orgIO = Organization_IO.objects.get(organization=organization)   
     
        client = Ace()
        responseFee = client.get_fees(ioid = orgIO.ace_ioid)    
        return responseFee[1]
    except Exception, e:
        mail_admins('Adquotient -> Ace: Get Fees failed', 'Organization: %s \r\n Failed: %s  ' % (organization.pk, str(e)), True)
        
    return True 
      
def deleteFee(organization, args):
    try:
        orgIO = Organization_IO.objects.get(organization=organization)   
        client = Ace()

        responseFee = client.delete_fees(ioid = orgIO.ace_ioid,
                             ioDetail = 0,
                             feeId = args["feeId"],
                             spId = args["spId"])  

    except Exception, e:
        mail_admins('Adquotient -> Ace: Delete Placement Fee failed', 'Organization: %s \r\n Failed: %s  ' % (organization.pk, str(e)), True)
        
    return True    
      
def updateIOStatus(organization, args):
    try:
        orgIO = Organization_IO.objects.get(organization=organization)   
        client = Ace()

        responseIOStatus = client.update_iostatus(ioid = orgIO.ace_ioid,
                                             statusId = args["statusId"],
                                             spId = args["spId"])  

    except Exception, e:
        mail_admins('Adquotient -> Ace: Update IO Status failed', 'Organization: %s \r\n Failed: %s  ' % (organization.pk, str(e)), True)
        
    return True   
    
def searchIOs():
    try:
        client = Ace()
        responseIOSearch = client.search_ios(placement = 1,
                                             recordcount = 0)  
        if responseIOSearch[0] == True:
            return responseIOSearch[1]
        else:
            return False
    
    except Exception, e:
        mail_admins('Adquotient -> Ace: Search IO', 'Organization: %s \r\n Failed: %s  ' % (organization.pk, str(e)), True)


def createPO(organization, PTAction, relationship):
    #try:

    try:
        orgIO = Organization_IO.objects.get(organization=organization)		
    except:
        return False
    # If Company Ace Id doesn't exist, create it. 
    # It will cause the PO Creation to error out if it invalid.
    if organization.ace_id == None or int(organization.ace_id) == 0:
        print "createPO - create_company"
        create_company(organization)
    
    orgContact = OrganizationContacts.objects.get(organization=organization)
    
    # If there is no Ace Contact ID associated with any internal contacts, create one.
    # It will cause the PO Creation to error out if it invalid.
    if orgContact.ace_contact_id == None or int(orgContact.ace_contact_id) == 0:
        print "createPO - create_contact"
        create_contact(organization)

    # ACE API call for PO creation.            
    client = Ace()
    responsePO = client.create_po(placementid = 1,
                                  compId = organization.ace_id,
                                  extCompId = organization.id,
                                  specialTerms = "",
                                  payable = 1,
                                  notes = "",
                                  startDate = str(datetime.date.today()),
                                  endDate = str(datetime.date.today() + datetime.timedelta(weeks=104)),
                                  customerPO = "",
                                  rate = PTAction.action.advertiser_payout_amount,
                                  unitType = PTAction.action.advertiser_payout_type,
                                  tag = PTAction.action.name,
                                  paymentTerms = 6,
                                  detailTerms = "",
                                  loginId = orgIO.salesrep,
                                  ioId = orgIO.ace_ioid,
                                  ioDetail = relationship.program_term.ace_iodetailid,
                                  contactbill = orgContact.ace_contact_id,
                                  contactop = orgContact.ace_contact_id)       
    
    
    # Maybe use JSON for responseIO[1]
    # simplejson.dumps(data)
    print responsePO
    if(responsePO[0]):
        if(responsePO[1]['Success'].lower() == 'true'):
            relationship.poId = responsePO[1]['PurchaseOrderId']
            relationship.poDetailId = responsePO[1]['PoDetailId']
            relationship.poSymbol = responsePO[1]['PurchaseOrderSymbol']
            relationship.save()
            return True
        #print "responsePO :%s" % responsePO
        #raise Exception(responsePO[1]['ErrorMessage'])
    #except Exception, e:
    #mail_admins('Adquotient -> Ace: Create Purchase Order failed', 'Organization: %s \r\n Failed: %s  ' % (organization.pk, str(e)), True)
        
    #return True

if __name__ == "__main__":
    client = Ace()
    '''
    response = client.update( compId = '11597',
                            compLong = 'Charles Murray Inc.',
                            compShort = 'CMInc',
                            add1 = '654 Malenfant Blvd',
                            add2 = 'PO BOX 153',
                            city = 'Dieppe',
                            state = 'NB',
                            region = 'SOUTH',
                            country = 'ca',
                            zip = '90210')
                     
    '''    
    #response = client.status_po(poId = 1655)    
    response = client.create_po(placementid=1,
                                compId=11717,
                                serviceId=9,
                                extCompId=46,
                                specialTerms="",
                                payable=1,
                                notes="no notes",
                                startDate=str(datetime.date.today()),
                                endDate=str(datetime.date.today() + datetime.timedelta(weeks=104)),
                                customerPO="",
                                rate=1,
                                unitType=8,
                                tag="",
                                paymentTerms=6,
                                detailTerms="",
                                loginId=361,
                                ioId=16631,
                                ioDetail=16658,
                                contactbill=14269,
                                contactop=14269)
    print response
    
    
