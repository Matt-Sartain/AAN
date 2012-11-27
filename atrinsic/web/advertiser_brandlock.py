from django.template import RequestContext
from atrinsic.util.imports import *
from atrinsic.util.aanapi.brandlock.brandlockApi import Brandlock

from django.utils import simplejson

from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.shortcuts import render_to_response
from django.template.defaultfilters import slugify
from forms import BrandForm,BrandEditForm


# Navigation Tab to View mappings for the Advertiser Messages Menu
tabset("Advertiser",6,"Brand Protection","advertiser_brandlock",
       [("Reports","advertiser_brandlock"),
        ("Edit","advertiser_brandlock_edit"), ])


@url(r"^brandlock/edit/$","advertiser_brandlock_edit")
@tab("Advertiser","Brand Protection","Edit")
@advertiser_required
def advertiser_brandlock_edit(request):    
    
    key = request.organization.brandlock_key
    bl = Brandlock(key)
    form = BrandEditForm(key)
    
    if request.POST:
        campaign = request.POST.get('campaigns',None)
        form.fields['campaigns'].initial = campaign
        action = request.POST.get('action',None)
        print action
        if action == '0':
            params = {}
            params['name'] = request.POST.get('name',None)
            if request.POST.get('active',None) == 'on':
                params['isActive'] = '1'
            else:
                params['isActive'] = '0'
            params['websiteUrls'] = request.POST.get('websites',None)
            params['destinationUrls'] = request.POST.get('domains',None)
            params['trademarkTerms'] = request.POST.get('trademarks',None)
            mylist = request.POST.getlist('searchp')
            newstr = ",".join(str(i) for i in mylist)
            params['searchProductIds'] = newstr
            
            result = bl.campaign_save(campaign,params)
            
    else:
        campaign = form.fields['campaigns'].choices[0][0]
        
    
    competitors_array = bl.list_competitors(campaign,2)
    keyword_groups_array = bl.list_keyword_groups(campaign,2)    
    #InitValues
    cinfo = bl.campaign_info(campaign)
    form.fields['active'].initial = cinfo['data']['isActive']
    initprov = {}
    strproviders = cinfo['data']['searchProductIds']
    providers = strproviders.split(',')
    for i in providers:
        initprov[i] = '1'

    form.fields['searchp'].initial = initprov
    form.fields['websites'].initial = cinfo['data']['websiteUrls']
    form.fields['domains'].initial = cinfo['data']['destinationUrls']
    form.fields['trademarks'].initial = cinfo['data']['trademarkTerms']    
        
    return AQ_render_to_response(request, 'advertiser/brandlock/brandlock_edit.html', {
            'form' : form,
            'comps' : competitors_array,
            'kwg' : keyword_groups_array,
        }, context_instance=RequestContext(request))

@url(r"^brandlock/$","advertiser_brandlock")
@tab("Advertiser","Brand Protection","Reports")
@advertiser_required
def avertiser_brandlock(request):
    from datetime import datetime
    key=""
    key = request.organization.brandlock_key

    try: 
        bl = Brandlock(key)
        cdata = bl.list_campaigns(True,False)
    except:
        return HttpResponseRedirect("/advertiser/") 
        
    report = ""
    form = BrandForm(key)
    
    return AQ_render_to_response(request, 'advertiser/brandlock/brandlock.html', {
            'form' : form,
            'report' : report,
            'JQ17' : True,
        }, context_instance=RequestContext(request))

    #return render_to_response('advertiser/brandlock/brandlock.html', {}, context_instance=RequestContext(request))  

@url(r"^brandlock/report/$","advertiser_brandlock_report")
def avertiser_brandlock_report(request):
    from datetime import datetime,date
    
    key = request.organization.brandlock_key
    bl = Brandlock(key)
    params = {}

    #Get request parameters
    excel = request.POST.get('xls',None)
    campaign = request.POST.get('campaigns',None)
    reportType = request.POST.get('reportType',None)
    competitors = request.POST.getlist('competitors')
    keyword_groups = request.POST.getlist('keyword_groups')
    keywords = request.POST.getlist('keywords')
    search_provider = request.POST.getlist('search_provider')
    ad_offer_type = request.POST.get('ad_offer_type', None)
    time_period = request.POST.get('time_period', None)
    listing_attributes = request.POST.getlist('listing_attributes')
    listing_attributes_ratings = request.POST.getlist('listing_attributes_ratings')
    listing_attributes_reviews = request.POST.getlist('listing_attributes_reviews')
    listing_section = request.POST.getlist('listing_section')
    exclude_tracking_urls = request.POST.get('exclude_tracking_urls')
    
    formSD = request.POST.get('start_date',None)
    formED = request.POST.get('end_date',None)

    if formSD == '' or formSD == None:
        startDate = ''
    else:
        startDate = datetime.strptime(formSD,"%m/%d/%Y").date()
        params['start_date'] = str(startDate)   
    if formED == '' or formED == None:
        endDate = ''
    else:
        endDate = datetime.strptime(formED,"%m/%d/%Y").date()
        params['end_date'] = str(endDate)            

    #keyword_group string formated for BrandLock API
    kwgStr = ""
    if keyword_groups != []:
        kwgStr = '['
        for i in keyword_groups:
            if i != '0':
                kinfo = i.split('|')
                kwgStr += ('"' + kinfo[1] + '"' + ',')
        kwgStr = kwgStr[:-1]
        kwgStr += ']'
        params['keyword_group'] = kwgStr

    #competitor string formated for BrandLock API
    params['advertiser_url'] = listToBL(competitors)
    #keyword string
    if keywords != []:
        params['keyword_term'] = listToBL(keywords)
    #Search provider
    params['ad_provider'] = listToBL(search_provider)
    #Time Period Param
    if time_period != '0':
       params['time_period'] = time_period
    #Offer type Param
    if ad_offer_type != '0' and ad_offer_type != None:
       params['ad_offer_type'] = ad_offer_type
    
    if reportType == 'listing_details' or reportType == 'listing':
        #Listing Attributes 
        params['listing_attributes'] = listToBL(listing_attributes)
        #Listing Attribute Ratings 
        params['listing_attributes_rating'] = listToBL(listing_attributes_ratings)
        #Listing Attribute Reviews
        params['listing_attributes_reviews'] = listToBL(listing_attributes_reviews)
        #Listing Attribute Sections
        params['listing_section'] = listToBL(listing_section)
    
    #Exclude tracking URL's
    if reportType == 'affiliate' or reportType == 'affiliate_details':
        params['exclude_tracking_urls'] = exclude_tracking_urls

    print params
    print request.POST
    if excel != 'on':
        report = bl.getReport(campaign,reportType,'json',params)
        return HttpResponse(report, mimetype="text/html")
    else:
        report = bl.getReport(campaign,reportType,'csv',params)	
        response = HttpResponse(report, mimetype="application/vnd.ms-excel")
        response['Content-Disposition'] = "attachment; filename=report.csv"
        return response
        
@url(r"^brandlock/competitors/(?P<id>\d+)/$","advertiser_brandlock_competitors")
@advertiser_required
def avertiser_brandlock_competitors(request, id):
    
    key = request.organization.brandlock_key
    bl = Brandlock(key)
    jsonObject = bl.list_competitors(id,1)
    sjsonObject = simplejson.JSONEncoder().encode(jsonObject)
    print "JSON OBJECT -----"
    #print sjsonObject 
    return HttpResponse(sjsonObject, mimetype="application/json")
    
@url(r"^brandlock/edit/competitors/(?P<id>\d+)/$","advertiser_brandlock_edit_competitors")
@advertiser_required
def avertiser_brandlock_edit_competitors(request, id):
    from django.utils import simplejson
    
    key = request.organization.brandlock_key
    bl = Brandlock(key)
    jsonObject = bl.list_competitors(id,2)
    sjsonObject = simplejson.JSONEncoder().encode(jsonObject)
    #print sjsonObject 
    return HttpResponse(sjsonObject, mimetype="application/json")
    
@url(r"^brandlock/edit/competitors/create/(?P<id>\d+)/$","avertiser_brandlock_create_competitors")
@advertiser_required
def avertiser_brandlock_update_competitors(request, id):
    
    key = request.organization.brandlock_key
    bl = Brandlock(key)
   
    url = request.POST.get('url',None)
    name = request.POST.get('name',None)
    
    jsonObject = bl.create_competitor(id,url,name)
    #sjsonObject = simplejson.JSONEncoder().encode(jsonObject)
    
    print jsonObject 
    return HttpResponse(jsonObject, mimetype="application/json")
        
@url(r"^brandlock/edit/competitors/update/(?P<id>\d+)/$","avertiser_brandlock_update_competitors")
@advertiser_required
def avertiser_brandlock_update_competitors(request, id):
    
    cid = request.POST.get('id',None)
    url = request.POST.get('url',None)
    name = request.POST.get('name',None)
    
    key = request.organization.brandlock_key
    bl = Brandlock(key)

    jsonObject = bl.update_competitor(id,cid,url,name)
    #sjsonObject = simplejson.JSONEncoder().encode(jsonObject)
    
    print jsonObject 
    return HttpResponse(jsonObject, mimetype="application/json")
    
@url(r"^brandlock/edit/competitors/delete/(?P<campid>\d+)/(?P<compid>\d+)/$","advertiser_brandlock_delete_competitors")
@advertiser_required
def advertiser_brandlock_delete_competitors(request, campid, compid):
    
    key = request.organization.brandlock_key
    bl = Brandlock(key)

    jsonObject = bl.delete_competitor(campid,compid)
    #sjsonObject = simplejson.JSONEncoder().encode(jsonObject)
    
    print jsonObject 
    return HttpResponse(jsonObject, mimetype="application/json")
    
@url(r"^brandlock/keywordgroups/(?P<id>\d+)/$","advertiser_brandlock_keyword_groups")
@advertiser_required
def advertiser_brandlock_keyword_group(request, id):
    
    key = request.organization.brandlock_key
    bl = Brandlock(key)
    jsonObject = bl.list_keyword_groups(id,1)
    sjsonObject = simplejson.JSONEncoder().encode(jsonObject)
    print "JSON OBJECT -----"
    #print sjsonObject 
    return HttpResponse(sjsonObject, mimetype="application/json")
    
@url(r"^brandlock/keywords/$","advertiser_brandlock_keywords")
@advertiser_required
def advertiser_brandlock_keywords(request):

    idlist = request.POST.get('idlist')
    campaign = request.POST.get('campaign')
    
    idArray = idlist.split(",")
    print idArray
    
    options = ""
    key = request.organization.brandlock_key
    bl = Brandlock(key)
    for i in idArray:
        options += bl.list_keywords(campaign,i)
        options += "\n"
    
    options = options[:-1]
    print "JSON OBJECT -----"
    #sjsonObject = simplejson.JSONEncoder().encode(jsonObject)
    print options 
    
    return HttpResponse(options, mimetype="text/plain")
    
@url(r"^brandlock/edit/keywords/(?P<campId>\d+)/(?P<kwgId>\d+)/$","advertiser_brandlock_keywords_singlelist")
@advertiser_required
def advertiser_brandlock_keywords_singlelist(request,campId,kwgId):
    
    key = request.organization.brandlock_key
    bl = Brandlock(key)
    keywords = bl.list_keywords(campId,kwgId)  

    return HttpResponse(keywords, mimetype="text/plain")
    
@url(r"^brandlock/edit/keywords/update/(?P<campId>\d+)/(?P<kwgId>\d+)/$","advertiser_brandlock_keywords_update")
@advertiser_required
def advertiser_brandlock_keywords_update(request,campId,kwgId):
    from django.utils import simplejson

    terms = request.POST.get('terms',None)
    name = request.POST.get('name',None)
    
    key = request.organization.brandlock_key
    bl = Brandlock(key)
    keywords = bl.update_keywords(campId,kwgId,name,terms)  

    return HttpResponse(keywords, mimetype="text/plain")
    
@url(r"^brandlock/edit/keywords/create/(?P<campId>\d+)/$","advertiser_brandlock_keywords_create")
@advertiser_required
def advertiser_brandlock_keywords_create(request,campId):

    terms = request.POST.get('terms',None)
    name = request.POST.get('name',None)
    
    key = request.organization.brandlock_key
    bl = Brandlock(key)
    keywords = bl.create_keywords(campId,name,terms)  

    return HttpResponse(keywords, mimetype="text/plain")
                     
@url(r"^brandlock/edit/campaign/create/$","advertiser_brandlock_campaign_create")
@advertiser_required
def advertiser_brandlock_campaign_create(request):

    params  = {}
    params['name'] = request.POST.get('name',None)
    params['isActive '] = '1'
    params['countryCode'] = 'US'
    params['languageCode'] = 'EN'
    params['websiteUrls'] = request.POST.get('websites',None)
    params['destinationUrls'] = request.POST.get('domains',None)
    params['trademarkTerms'] = request.POST.get('trademarks',None)
    mylist = request.POST.getlist('sproviders')
    newstr = ",".join(str(i) for i in mylist)
    params['searchProductIds'] = newstr
    
    key = request.organization.brandlock_key
    bl = Brandlock(key)
    result = bl.campaign_create(params)
    print "Create Camp Rez"
    print result
    return HttpResponse(result, mimetype="text/plain")   
        
def listToBL(name):
    result = ""
    if name != []:
        result = '['
        for i in name:
            if i != '0':
                result += ('"' + i + '"' + ',')
        result = result[:-1]
        result += ']'  
    return result    
        