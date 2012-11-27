from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from atrinsic.util.imports import *
from atrinsic.base.choices import *
from reports import *
from pywik.PyWik import *
import openFlashChart
import re

@url("^crossdomain.xml$", 'main')
def homepage(request):
    '''View for the main site homepage '''
    
    if request.GET.get("action",None) == "track":
        return old_invite_redirects(request)
    return HttpResponse("""<?xml version="1.0"?>
<!DOCTYPE cross-domain-policy SYSTEM "http://www.adobe.com/xml/dtds/cross-domain-policy.dtd">
<cross-domain-policy>
   <allow-access-from domain="*" />
</cross-domain-policy>
""")

@url(r"^$", 'main')
def homepage(request):
    '''View for the main site homepage '''
    
    if request.GET.get("action",None) == "track":
        return old_invite_redirects(request)
    return HttpResponseRedirect('/accounts/login/')


@url(r"^bp_readmore/$", 'bp_readmore')
def bp_readmore(request):
    ''' View for the main site homepage '''
    return render_to_response('misc/readmore.html', {}, context_instance=RequestContext(request))
    
@url(r"^chat/$", 'chat_view')
def chat_view(request):
    ''' View for the main site homepage '''
    return render_to_response('base/chat.html', {}, context_instance=RequestContext(request))
    
@url(r"^api/remove_notification/(?P<notification_type>.*)/(?P<id>.*)/$", 'remove_notification')
def remove_notification(request,notification_type,id):
    from atrinsic.base.models import Notifications
    """Ajax call to remove notifications"""
    notification = Notifications.objects.create(original_id=id,notification_type=notification_type,organization=request.organization)
    return HttpResponse(str(notification))

@url(r"^RSS/(?P<link_id_encoded>.*)/(?P<website_encode_id>.*)/$", 'process_rss_feed')
def process_rss_feed(request,link_id_encoded,website_encode_id):
    from atrinsic.base.models import Link,Website
    from atrinsic.web.helpers import base36_decode
    from elementtree.ElementTree import XML,tostring
    import urllib2
    link = Link.objects.get(pk=base36_decode(link_id_encoded))
    website = Website.objects.get(pk=base36_decode(website_encode_id))
    tracking_url = link.track_html_ape(website,link_only=True)
    try:
        raw_response = urllib2.urlopen(link.link_content)
    except:
        return AQ_render_to_response(request, 'base/custom_error.html', {
                'errmsg' : RSS_TIMEOUT,
            }, context_instance=RequestContext(request))

    tree = XML(raw_response.read())
    for node in tree.getiterator('link'):
        domain_position = node.text.find(".com") + 4
        node.text = tracking_url + "&url=" + node.text[domain_position:]
    
    return render_to_response("blank_xml_template.html", {"XML":tostring(tree)}, mimetype="application/xhtml+xml")
    
def live_dashboard(request):
    this_page = 'live-dashboard'
    from atrinsic.base.models import OrganizationContacts,AqWidget,UserAqWidget
    if request.method == "POST":
        
        pywik_obj = PyWik(auth='8ea3806a0efcbc383600e6209ed557fc')
    
        #create the site first.
        status, code, site_response = pywik_obj('SitesManager_addSite', siteName = request.POST['sites'], urls = request.POST['urls'])
        print "site_response %s" % site_response
        if status == True and code == 200:
            if site_response.has_key('value'):
                idSite = site_response['value']
            else:
                return AQ_render_to_response(request, 'live/js_tracker.html', {
                    'js_tracker':site_response['message'],
                    'has_piwik':0,
                    'error':True,
                    }, context_instance=RequestContext(request))
        
        instant_password=str(datetime.datetime.now())
        import md5
        hash = md5.new(instant_password)
        print "instant_password %s" % instant_password
        print "hash %s" % hash.hexdigest()
        #then create the user, could have done this in reverse order, it really doenst matter.
        #used a regular expression to only keep alphanumeric characters.		
        
        user_login = re.sub('[^a-zA-Z0-9_]','',request.organization.company_name)[:20]
        
        oc = OrganizationContacts.objects.select_related("organization", "contact").get(organization=request.organization)

        status, code, user_response = pywik_obj('UsersManager_addUser',userLogin=user_login,password=instant_password,email=oc.email)            
        print "user_response %s" % user_response
        #now that we have a user and a site, we associate them
        status, code, access_response = pywik_obj('UsersManager_setUserAccess',userLogin=user_login,access="view",idSites=idSite)
        print "access_response %s" % access_response
        if status == True and code == 200:
            if not site_response.has_key('value'):
                return AQ_render_to_response(request, 'live/js_tracker.html', {
                'js_tracker':user_response['message'],
                'has_piwik':0,
                'error':True,
                }, context_instance=RequestContext(request))
        #now that he has access we need the auth code for the api calls he will do from now on.
        #first need the password hashed before you pass it for safety
        
        status, code, token_response = pywik_obj('UsersManager_getTokenAuth',userLogin=user_login,md5Password=hash.hexdigest())
        print "token_response %s" % token_response
        #finaly we need to get the JS tag the client needs for tracking.
        status, code, js_response = pywik_obj('SitesManager_getJavascriptTag',idSite=idSite)
        print "js_response %s" % js_response
        request.organization.pywik_token_auth_key = token_response['value']
        request.organization.pywik_siteId = idSite
        request.organization.save()
        
        return AQ_render_to_response(request, 'live/js_tracker.html', {
                'js_tracker':js_response['value'],
                'has_piwik':0,
                }, context_instance=RequestContext(request))
    else:
        if request.organization.pywik_token_auth_key != None:		
            x = UserAqWidget.objects.select_related("AqWidget").filter(page=this_page,organization=request.organization).order_by('sort_order')
            widgets = UserAqWidget.prep(x,request,None)
                    
            z = AqWidget.objects.filter(widget_type=2)
            widget_list = AqWidget.prep(z)
            
            return AQ_render_to_response(request, 'live/dashboard.html', {
        
                    'widgets':widgets,
                'widget_list':widget_list,
                'current_page':this_page,
                'has_piwik':1,
                }, context_instance=RequestContext(request))
        else:
            return AQ_render_to_response(request, 'live/signup.html', {
                'has_piwik':0,
                }, context_instance=RequestContext(request))
                
@url(r"^api/new_ajax_sort_order/$", 'new_ajax_sort_order')
def new_ajax_sort_order(request):
    import cjson,urllib
    from atrinsic.base.models import UserAqWidget
    
    for key in request.POST:
        print key
        print request.POST[key]
        user_widget = UserAqWidget.objects.get(pk=request.POST[key])
        user_widget.sort_order = key
        user_widget.save()

    return HttpResponse("updated")
                    
@url(r"^api/ajax_sort_order/(?P<update_data>.*)/(?P<page>.*)/$", 'ajax_sort_order')
def ajax_sort_order(request,update_data,page):
    import cjson,urllib
    from atrinsic.base.models import UserAqWidget
    user_widgets = UserAqWidget.objects.filter(page=page, organization=request.organization)
    zones = update_data.split(",")
    x=0
    for zone in zones:
        zones[x]=zone.split("|")
        x+=1
    widget_zone_id = 0
    for widget_zone in zones:
        widget_order_id = 1
        for widget in widget_zone:
            try:
                user_widget = UserAqWidget.objects.get(pk = widget)
                user_widget.zone=widget_zone_id
                user_widget.sort_order = widget_order_id
                user_widget.save()
            except:
                pass
            widget_order_id+=1
        widget_zone_id+=1
    return HttpResponse("updated")
    
@url(r"^api/ajax_new_chart/(?P<widget>.*)/(?P<new_style>.*)/$", 'ajax_new_chart')
def ajax_new_chart(request,widget,new_style):
    from atrinsic.base.models import UserAqWidget,AqWidget
    if request.GET.get('preview',None) == None:
        user_widget = UserAqWidget.objects.get(pk=widget)
        my_widget = user_widget.widget
    else:
        my_widget = AqWidget.objects.get(pk=widget)
        user_widget = UserAqWidget(widget=my_widget)
    if new_style == None:
        new_style = my_widget.widget_style
  
    return widget_layout(request,my_widget,user_widget,new_style)

@url(r"^api/ajax_add_widget/(?P<widget>.*)/(?P<page>.*)/$", 'ajax_add_widget')
def ajax_add_widget(request,widget,page):
    from atrinsic.base.models import UserAqWidget,AqWidget
    
    widget = AqWidget.objects.get(pk=widget)
    user_widget = UserAqWidget.objects.create(widget=widget, page=page, organization = request.organization, zone = 1, sort_order = 1, custom_style=widget.widget_style)#, custom_date_range='test'
    return widget_layout(request,widget,user_widget,widget.widget_style)

@url(r"^api/get_report/(?P<report_type>.*)/(?P<response_type>.*)/$", 'reporting_api')
def reporting_api(request,report_type,response_type):
    from atrinsic.base.models import UserAqWidget,AqWidget,Organization
    import cjson
    if report_type == "sales-report":
        report_type=0
    elif report_type == "sales-by-publishers":
        report_type=1
    elif report_type == "revenue-report":
        report_type=REPORTTYPE_REVENUE
    elif report_type == "revenue-report-by-advertisers":
        report_type=REPORTTYPE_REVENUE_BY_PUBLISHER
    elif report_type == "revenue-report-by-publisher":
        report_type=REPORTTYPE_REVENUE_BY_PUBLISHER
    elif report_type == "link-report":
        report_type=REPORTTYPE_CREATIVE
    elif report_type == "link-report-by-promo":
        report_type=REPORTTYPE_CREATIVE_BY_PROMO
    elif report_type == "product-detail-report":
        report_type=REPORTTYPE_PRODUCT_DETAIL
    elif report_type == "order-details-report":
        report_type=REPORTTYPE_ORDER_DETAIL
    elif report_type == "accounting-report":
        report_type=REPORTTYPE_ACCOUNTING
    elif report_type == "sales-by-advertiser":
        report_type=REPORTTYPE_SALES_BY_ADVERTISER
    elif report_type == "advertiser-revenue-report":
        report_type=REPORTTYPE_REVENUE_BY_ADVERTISER
    else:
        json = {}
        json["status"] = "error"
        json["error"] = "Invalid Report Type"
        return HttpResponse(cjson.encode(json))
    try:
        request.organization = Organization.objects.get(pk=request.GET['organization'],api_key = request.GET['auth_key'])
    except:
        json = {}
        json["status"] = "error"
        json["error"] = "Invalid Credentials - Access denied"
        return HttpResponse(cjson.encode(json))
    widget = AqWidget.objects.get(pk=report_type)
    request_get = {}
    request_get['widget_id'] = report_type
    for x in request.GET:
        request_get[str(x)] = request.GET[x]
    if response_type == "xml":
        xml_data = widget.getAqDataTable(request,response_type,**request_get)
        return render_to_response("blank_xml_template.html", {"XML":xml_data}, mimetype="application/xhtml+xml")
    else:
        return HttpResponse(widget.getAqDataTable(request,response_type,**request_get))
        
@url(r"^api/ajax_remove_widget/(?P<widget>.*)/$", 'ajax_remove_widget')
def ajax_remove_widget(request,widget):
    from atrinsic.base.models import UserAqWidget
    user_widget = UserAqWidget.objects.get(pk=widget).delete()
    return HttpResponse("deleted")
    
def widget_layout(request,widget,user_widget,style):
    import cjson,urllib
    from pywik import prep_date
    from forms import WidgetSettingsForm
    if user_widget.custom_date_range != None:
        calc_date = user_widget.custom_date_range
    elif (request.GET.has_key('start_date')) & (request.GET.has_key('end_date')):
        calc_date = str(request.GET['start_date'])+","+str(request.GET['end_date'])
    elif (request.POST.has_key('start_date')) & (request.POST.has_key('end_date')):
        calc_date = str(request.POST['start_date'])+","+str(request.POST['end_date'])
    else:
        calc_date = prep_date(user_widget.widget.widget_date_range)
    d = { }
    if user_widget.custom_group != None:
        d['group_data_by'] = user_widget.custom_group
    if user_widget.custom_columns != None:
        x,y = user_widget.custom_columns.split(",")
        d['variable1'] = x
        d['variable2'] = y
    if calc_date != "" and calc_date.find(","):
        d['start_date'] = calc_date.split(",")[0]
        d['end_date'] = calc_date.split(",")[1]
    else:
        d['start_date'] = ""
        d['end_date'] = ""
    my_widget = {}
    my_widget['form'] = WidgetSettingsForm(initial=d).as_p()
    if style == 'None':
        style = widget.widget_style
    if style == "table":
        if widget.widget_type == 2:
            my_widget['html'] = widget.getDataTable(auth=request.organization.pywik_token_auth_key, idSite=request.organization.pywik_siteId,group_by = request.GET.get('group_by',0), period='day', date=calc_date, headers = widget.headers.split(','), data_columns = widget.data_columns.split(","))
        else:
            my_widget['html'] = widget.getAqDataTable(request=request, chart_style=style, date=calc_date, group_by = user_widget.custom_group, widget_id=widget.id, user_widget_id = user_widget.id)
        my_widget['header'] = widget.widget_name
        user_widget.custom_style = style
        if request.GET.get('preview',None) == None:
            user_widget.save()
    
        
    else:
        if user_widget.widget.widget_type == 2:
            my_widget['html'] = openFlashChart.flashHTML('100%', '300', '/api/'+str(user_widget.widget.id)+'/'+str(style)+'/?data=idSite='+str(request.organization.pywik_siteId)+'|date='+str(calc_date)+'|period=day', '/ofc/')
        else:
            if user_widget.custom_columns != None:
                custom_columns = "|custom_columns="+str(user_widget.custom_columns)
            else:
                custom_columns = ""
            my_widget['html'] = openFlashChart.flashHTML('100%', '300', '/api/'+str(user_widget.widget.id)+'/'+str(style)+'/?data=date='+str(calc_date)+'|group_by='+str(user_widget.custom_group)+str(custom_columns), '/ofc/')
        my_widget['header'] = user_widget.widget.widget_name
        user_widget.custom_style = style
        
    if request.GET.get('preview',None) == None:
        user_widget.save()
        
    my_widget['widget_id'] = user_widget.id
    return HttpResponse(str(cjson.encode(my_widget)))
@url(r"^api/settings/$","widget_settings")
@tab("Advertiser","Dashboard","Settings")
@register_api(None)
def widget_settings(request):    
    if request.method == 'POST':
        from forms import WidgetSettingsForm
        form = WidgetSettingsForm(request.POST)
        if form.is_valid():
            from atrinsic.base.models import UserAqWidget
            widget = UserAqWidget.objects.get(pk=request.POST['wid'])
            widget.custom_group = form.cleaned_data['group_data_by']
            widget.custom_columns = str(form.cleaned_data['variable1'])+","+str(form.cleaned_data['variable2'])
            db_date_string = ''
            if (request.POST.has_key("start_date")):
                if (request.POST['start_date'] != "") & (request.POST['start_date'] != None):
                    db_date_string+=str(request.POST['start_date'])
                    if request.POST.has_key("end_date"):
                        if (request.POST['end_date'] != "") & (request.POST['end_date'] != None):
                            db_date_string+=','+str(request.POST['end_date'])
                        else:
                            db_date_string+=','+str(request.POST['start_date'])
                    else:
                        db_date_string+=','+str(request.POST['start_date'])
            widget.custom_date_range = db_date_string
            widget.save()
        if request.organization.is_advertiser():
            return HttpResponseRedirect('/advertiser/')
        else:
            return HttpResponseRedirect('/publisher/')
            
@url(r"^api/(?P<widget>.*)/(?P<chart_style>.*)/$", 'flash_data_pump')
def flash_data_pump(request,widget,chart_style):
    from atrinsic.base.models import AqWidget

    module = __import__("AqWidgets")
    my_widget=AqWidget.objects.get(pk=widget)
    args = {}
    url_get_data = request.GET['data'].split("|")
    for arg in url_get_data:
        args[str(arg[:arg.find("=")])]=str(arg[arg.find("=")+1:])
    args['request']	= request
    args['widget_id'] = widget
    widget_class_name,widget_method = my_widget.widget_function.split("_")
    widget_class = getattr(module, widget_class_name)(**args)
    data = getattr(widget_class,widget_method)(request=request, chart_style = chart_style)
    return HttpResponse(data)
        
@url(r"^track_click$", 'old_invite_redirects')
def old_invite_redirects(request):
    from atrinsic.base.models import Action, Link, Website
    from atrinsic.web.helpers import base36_encode
    params = request.GET
    url = ""
    if request.GET.get('pixelID',None):
        #if its conversion reported by the advertiser
        action = Action.objects.get(invite_id=request.GET.get('pixelID',None))
        apeRedirect = base36_encode(action.ape_redirect_id)
        if request.is_secure():
            url = settings.APE_SECURE_PIXEL_URL + str(apeRedirect)
        else:
            url = settings.APE_PIXEL_URL + str(apeRedirect)
    elif params.get('igCode',None) and params.get('crID',None):
        #if its click/impression reported by the publisher
        website = Website.objects.get(pk = params['igCode'])
        link = Link.objects.get(invite_id = params['crID'])
        url = link.track_html_ape(website,True)
    return HttpResponseRedirect(url)