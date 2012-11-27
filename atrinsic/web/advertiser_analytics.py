from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
import datetime
from forms import GA_ReportForm, GA_AccountForm
from atrinsic.base.models import GA_Report, GA_Metric, GA_Dimension, GA_Account, GA_Site, GA_Category
#from responses import HttpJSONResponse

from responses import HttpJSONResponse
from atrinsic.util.imports import *

# Navigation Tab to View mappings for the Advertiser Settings Menu


tabset("Advertiser",7,"Analytics","advertiser_ga_accounts",
       [("Account","advertiser_ga_accounts"),       
       ("Sites","advertiser_ga_sites"),
       ("Reports","advertiser_ga_report"),])

    

#===========================================---/ANALYTICS USERS TAB/---===========================================#
##################### List Users ########################
@url(r"^analytics/$", "advertiser_ga_accounts")
@url(r"^analytics/accounts/$", "advertiser_ga_accounts")
@tab("Advertiser","Analytics","Account")
def advertiser_ga_accounts(request, id=None, page=None):
    from atrinsic.base.models import GA_Account
    from forms import GA_AccountForm
    
    try:
        user = GA_Account.objects.get(organization=request.organization)
        sites = user.get_sites()
        ga_sites = user.get_ga_sites()
    except:
        user = None
        sites = None
        ga_sites = None
    
    return AQ_render_to_response(request, "advertiser/analytics/users.html", {
                                'ga_user': user, 
                                'sites': sites, 
                                'ga_sites':ga_sites,
                                'form':GA_AccountForm()
            },
            context_instance=RequestContext(request))


@url(r"^analytics/accounts/view/$", "advertiser_ga_accounts_view")
def advertiser_ga_accounts_view(request):
    user = get_object_or_404(GA_Account, organization=request.organization)
    sites = user.get_sites()
    return AQ_render_to_response(request,"advertiser/analytics/account_view.html", { 
                                        'ga_user': user, 
                                        'sites': sites, 
                                        'ga_sites': user.get_ga_sites() 
                                })

@url(r"^analytics/account_create/$", "advertiser_ga_account_create")
@tab("Advertiser","Analytics","Account")
def advertiser_ga_account_create(request):
    from forms import GA_AccountForm
    if(request.method == 'POST'):
        form = GA_AccountForm(request.POST)
        
        if(form.is_valid()):
            a = GA_Account(organization=request.organization)
            for k, v in form.cleaned_data.items():
                setattr(a, k, v)
            a.save()
            
    return HttpResponseRedirect(reverse('advertiser_ga_accounts'))
    

@url(r"^analytics/sites/$", "advertiser_ga_sites")
@tab("Advertiser","Analytics","Sites")
@advertiser_required
def advertiser_ga_sites(request):   
    from atrinsic.base.models import GA_Account
    try:
        user = GA_Account.objects.get(organization=request.organization)
        sites = user.get_sites()
    except:
        return HttpResponseRedirect(reverse('advertiser_ga_accounts'))
    return AQ_render_to_response(request, 'advertiser/analytics/site.html',{ 
                                        'ga_user': user, 
                                        'sites_configured': sites, 
                                        'sites_fromGA': user.get_ga_sites() 
                                }, context_instance=RequestContext(request))
    
@url(r"^analytics/account/(?P<id>\d+)/site/(?P<profile_id>\d+)/$", "advertiser_ga_user_site_add")
def advertiser_ga_user_site_add(request, id=None, profile_id=None):
    from atrinsic.base.models import GA_Account, GA_Site
    user = GA_Account.objects.get(organization=request.organization)
        
    if(GA_Site.objects.create_site(user, profile_id)):
        return HttpResponseRedirect(reverse("advertiser_ga_sites"))
    return render_to_response("error.html", { "message": "unable to add site" })   
    
#===========================================---/REPORTING TAB/---===========================================#
##################### SHOW REPORT(S) ########################
@url(r"^analytics/report/$", "advertiser_ga_report")
@tab("Advertiser","Analytics","Reports")
@advertiser_required
def advertiser_ga_report(request, id=None):
    from atrinsic.base.models import GA_Report
    reports = GA_Report.objects.all()
    return AQ_render_to_response(request,"advertiser/analytics/report_list.html", { 'reports': reports }, context_instance=RequestContext(request))

##################### END SHOW REPORT(S) ########################
#################################################################  

##################### CREATE REPORT ########################  
@url(r"^analytics/report/add/$", "advertiser_ga_report_create")
@tab("Advertiser","Analytics","Reports")
def advertiser_ga_report_create(request):    
    from forms import GA_ReportForm
    if(request.method == 'POST'):
        form = GA_ReportForm(request.POST)
        
        if(form.is_valid()):
            form.cleaned_data['organization'] = request.organization
            form.cleaned_data['metric'] = request.POST.getlist("metric")
            form.cleaned_data['dimension'] = request.POST.getlist("dimension")
            form.save()
            return HttpResponseRedirect(reverse('advertiser_ga_report'))
    else:        
        form = GA_ReportForm()
    return AQ_render_to_response(request,"advertiser/analytics/report_create.html", { 'form': form }, context_instance=RequestContext(request))    
##################### END CREATE REPORT ########################  
################################################################  

##################### RUN REPORT ########################
@url(r"^analytics/site/(?P<site_id>\d+)/(?P<report_id>\d+)/$", "advertiser_ga_site_report")
@url(r"^analytics/site/(?P<site_id>\d+)/(?P<report_id>\d+)/(?P<tier>\d+)/$", "advertiser_ga_site_report")
def advertiser_ga_site_report(request, site_id, report_id, tier = 0, tier_filter = ""):
    site = get_object_or_404(GA_Site, pk=site_id)
    report = get_object_or_404(GA_Report, pk=report_id)
    
    startdate = datetime.date(2010, 01, 01)
    enddate = datetime.date(2010, 01, 15)
        
    # Filter names and expressions are seperated by a colon(:)
    # and filters are seperated by the pipe delim (|)
    # Example: filters=browser:Firefox|browserVersion:2.0
    tier_filters = request.GET.get('filters',None) 
    data = report.get_report(startdate, enddate, tier, tier_filters)
    
    dimensionHeaders = currentDimension = report.get_dimensions()[int(tier)]
    metricsHeaders = report.get_metrics()
    
    for dimensions, metrics in data.list:
        for x in reversed(range(len(dimensions))):
            if x != int(tier):
                dimensions.pop(x)
    
    nexttier = int(tier) + 1    
    gotoNextTier = True
    if int(tier) == len(report.get_dimensions()) - 1:
        gotoNextTier = False
        
    return render_to_response("advertiser/analytics/site_report.html", { 
                                            "data": data.list, 
                                            "hdrDimension": dimensionHeaders,
                                            "hdrMetrics": metricsHeaders, 
                                            "siteid": site_id,
                                            "reportid": report_id,
                                            "currentDimension": currentDimension,
                                            "tier": tier,
                                            "gotoNextTier": gotoNextTier,
                                            "nexttier": nexttier,
                                            "filters":request.GET.get('filters',None),})
##################### END RUN REPORT ########################
#############################################################   
#=========================================---/END REPORTING TAB/---=========================================#
 
#===========================================---/AJAX CALLS/---===========================================#
##################### GET METRICS ########################
@url(r"^analytics/report/metrics/(?P<category_id>\d+)/$", "advertiser_ga_report_get_metrics")
def advertiser_ga_report_get_metrics(request, category_id):
    from atrinsic.base.models import GA_Category
    category = GA_Category.objects.get(pk=category_id)
    return HttpJSONResponse([{ 'name': metric.name, 'id': metric.pk} for metric in category.metrics()])
##################### END GET METRICS ########################
##############################################################

##################### GET DIMENSIONS ########################
@url(r"^analytics/report/dimensions/(?P<category_id>\d+)/$", "advertiser_ga_report_get_dimensions")    
def advertiser_ga_report_get_dimensions(request, category_id):
    from atrinsic.base.models import GA_Category
    category = GA_Category.objects.get(pk=category_id)
    return HttpJSONResponse([{ 'name': dimension.name, 'id': dimension.pk} for dimension in category.dimensions()])
##################### END GET DIMENSIONS ########################
#################################################################
#=========================================---/END AJAX CALLS/---=========================================#    