from django.template import RequestContext
from atrinsic import settings
import openFlashChart
import urllib

#CRITICAL IMPORTS
from atrinsic.util.imports import *

tabset("Publisher",0,"Dashboard","publisher_dashboard",
       [("Dashboard","publisher_dashboard"),
        ("Settings", "publisher_dashboard_settings"), ])

@url(r"^dashboard/w9/$","publisher_dashboard_w9")
@publisher_required
@register_api(None)
def publisher_dashboard_w9(request):
    
    return HttpResponseRedirect('/publisher/')
                
@url(r"^$","publisher_dashboard")
@tab("Publisher","Dashboard","Dashboard")
@publisher_required
@register_api(None)
def publisher_dashboard(request):
    from atrinsic.base.models import AqWidget, Organization, PublisherVertical, UserAqWidget, W9Status
    from forms import DashboardSettingsForm, w9UploadForm
    from atrinsic.util.AceApi import create_company
    
    this_page = 'publisher-dashboard'
    all_advertisers = Organization.objects.filter(publisher_relationships__status=RELATIONSHIP_ACCEPTED,
                                                     publisher_relationships__publisher=request.organization)
    
    aids = []
    aids = [j.id for j in all_advertisers]

    x = UserAqWidget.objects.select_related("AqWidget").filter(page=this_page,organization=request.organization).order_by('sort_order')
    widgets = UserAqWidget.prep(x,request,aids)
            
    z = AqWidget.objects.filter(widget_type__in=[1,3], Active=1)
    widget_list = AqWidget.prep(z)

    inbox = request.organization.received_messages.filter(is_active=True).order_by('-date_sent')
    
    # Check W9 Status form, if record doesnt exist, or set to Not Received
    # pass bool to page to display warning Lightbox
    showW9Warning = False

    #if request.organization.country != None and request.organization.country.lower().find("us") > -1:
    try:
        wNine = W9Status.objects.get(organization=request.organization)
    except:        
        wNine = W9Status.objects.create(organization=request.organization, status = W9_STATUS_NOT_RECEIVED, datereceived=datetime.datetime.now())
    
    if wNine.status != W9_STATUS_NOT_RECEIVED:
        showW9Warning = False    
        uploadForm = ""
    else:
        showW9Warning = True
        uploadForm = ""
    
    if request.organization.ace_id == None:        
        create_company(request.organization)
    
    hashed_ACEID = (int(request.organization.ace_id)  + 148773) * 12
    
    return AQ_render_to_response(request, 'publisher/dashboard.html', {
        'verticals' : PublisherVertical.objects.filter(is_adult=request.organization.is_adult).order_by('order'),
        'widgets':widgets,
        'widget_list':widget_list,
        'current_page':this_page,
        'msgcount' : inbox,
        'settings':True,
        'sdate':request.GET.get('start_date',''),
        'edate':request.GET.get('end_date',''),
        'showW9Warning':showW9Warning,
        'wNineForm':w9UploadForm(),
        'w9Link': settings.W9_PATH,
        'hashed_ACEID' : hashed_ACEID,
        #'w9Up' : W9UploadForm()
        }, context_instance=RequestContext(request))

@url(r"^dashboard/settings/$","publisher_dashboard_settings")
@tab("Publisher","Dashboard","Settings")
@publisher_required
@register_api(None)
def publisher_dashboard_settings(request):

    from atrinsic.base.models import UserAqWidget
    from forms import DashboardSettingsForm
    
    if request.method == 'POST':
        form = DashboardSettingsForm(request.POST)
        if form.is_valid():
            widget = UserAqWidget.objects.get(pk=request.POST['wid'])
            widget.custom_group = form.cleaned_data.get('dashboard_group_data_by',0)
            widget.custom_columns = str(form.cleaned_data['dashboard_variable1'])+","+str(form.cleaned_data['dashboard_variable2'])
            request.organization.dashboard_variable1 = form.cleaned_data['dashboard_variable1']
            request.organization.dashboard_variable2 = form.cleaned_data['dashboard_variable2']
            request.organization.save()
            db_date_string = ''
            if (request.POST.has_key("start_date")):
                if (request.POST['start_date'] != "") & (request.POST['start_date'] != None):
                    db_date_string+=str(request.POST['start_date'])
                    if request.POST.has_key("end_date"):
                        if (request.POST['end_date'] != "") & (request.POST['end_date'] != None):
                            db_date_string+=','+str(request.POST['end_date'])
            widget.custom_date_range = db_date_string
            widget.save()
    return HttpResponseRedirect('/publisher/')



@url(r"^dashboardAjax/$","publisher_dashboardAjax")
@url(r"^dashboardAjax/category/$","publisher_dashboardAjax")
@url(r"^dashboardAjax/category/(?P<vertid>.*)/$","publisher_dashboardAjax")
@publisher_required
@register_api(None)
def publisher_dashboardAjax(request, pagetype='featured', vertid=None, page=None):
	
    from atrinsic.base.models import Organization, PublisherRelationship

    advs = Organization.objects.filter(org_type=ORGTYPE_ADVERTISER,vertical=vertid,status=3,is_adult = request.organization.is_adult)
    relationships = PublisherRelationship.objects.filter(publisher=request.organization)

    rel = advs.filter(id__in=[ p.advertiser_id for p in relationships.filter(status=3)])
    norelationships = advs.exclude(id__in=[ p.advertiser_id for p in relationships.filter(status__in=[3,2])]).filter(is_private=0)


    return AQ_render_to_response(request, 'publisher/dashboardajax.html', {

        'acc_object_list' : rel,
        'norel_object_list' : norelationships,


        }, context_instance=RequestContext(request))

@url(r"^w9Uploader/$","w9_upload_file")
@publisher_required
def w9_upload_file(request):
    import os
    from atrinsic.base.models import W9Status
    uploadSuc = False
    if(request.method == 'POST'):
        if(request.FILES):
            try:
                file_in = request.FILES.get('wNineFile', None)
                if(file_in):
                    filename = file_in.name
                    file_out = os.path.join(settings.W9_UPLOAD_PATH, filename)
                    writer = open(file_out, 'wb+')
                    for chunk in file_in.chunks():
                        writer.write(chunk)
                    writer.close()
                    uploadSuc = True
                    try:
                        wnine = W9Status.objects.get(organization=request.organization)
                        wnine.status = W9_STATUS_RECEIVED
                        wnine.filename = filename
                        wnine.datereceived = datetime.datetime.now()
                        wnine.save()
                    except:
                        W9Status.objects.create(organization=request.organization, status=W9_STATUS_RECEIVED, filename=filename, datereceived=datetime.datetime.now())
                            
            except:
                pass
    if not uploadSuc:
        return HttpResponse('False')
    else:
        return HttpResponse('True')
        
