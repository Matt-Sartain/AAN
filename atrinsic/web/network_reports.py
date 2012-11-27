from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.db.models.query import QuerySet
from atrinsic.util.imports import *
from atrinsic.util.date import compute_date_range
#from publisher_reports import * 
from reports import *
tabset("Network", 4, "Reports", "network_reports_network_advertiser_reports",
       [ ("Network Advertiser Reports", "network_reports_network_advertiser_reports"),
         ("Network Publisher Reports", "network_reports_network_publisher_reports"),
         ("Advertiser Reports", "network_reports_advertiser_reports"),
         ("Publisher Reports", "network_reports_publisher_reports"),
         ])


@url(r"^reports/network/advertiser/$","network_reports_network_advertiser_reports")
@tab("Network","Reports","Network Advertiser Reports")
@admin_required
def network_reports_network_advertiser_reports(request):
    # IMPORTS
    from forms import ReportFormNetworkAdvertiser
    
    #INITIALIZATIONS
    form = ReportFormNetworkAdvertiser(request.user)
    report = None
    reportTitle = None
    
    # POST : GENERATE AND DISPLAY REPORT
    # - OR - 
    # GET : GENERATE AND SERVE DOWNLOAD REPORT
    if request.POST:
        # 1 - SET FROM WITH POST DATA & VALIDATE       
        form = ReportFormNetworkAdvertiser(request.user,request.POST)
        
        if form.is_valid():
        # 2 - PROCESS DATES
            x = request.POST['start_date'].split("/")
            start_date_array = []
            for numbers in x:
                start_date_array.append(int(numbers))
            date_start = datetime.datetime(start_date_array[2],start_date_array[0],start_date_array[1])
            
            x = request.POST['end_date'].split("/")
            end_date_array = []
            for numbers in x:
                end_date_array.append(int(numbers))
            date_end = datetime.datetime(end_date_array[2],end_date_array[0],end_date_array[1])

        # 3 - PROCESS PUBLISHER IDS
            all_advertisers = request.user.get_profile().admin_assigned_advertisers()
            
            aids = []
            if form.cleaned_data["run_reporting_by"] == '0': # all advertisers
                aids = [j.id for j in all_advertisers]
            elif form.cleaned_data["run_reporting_by"] == '1': # specific advertiser
                aids.append(int(form.cleaned_data["specific_advertiser"][2:]))
            elif form.cleaned_data["run_reporting_by"] == '2': # advertiser by category
                aids = []
                for j in all_advertisers:
                    for site in j.website_set.all():
                        if site.vertical in form.cleaned_data["advertiser_category"]:
                            aids.append(j.id)
            
        # 4 - PROCESS REPORT TYPE     
            if int(form.cleaned_data["report_type"]) == REPORTTYPE_SALES:
                report = DateReport(date_start,date_end,'advertiser',form.cleaned_data["group_by"],spec=REPORTTYPE_SALES,advertiser_set=aids,)
                reportTitle = "Sales and Activity Report - %s to %s" % (str(request.POST['start_date']), str(request.POST['end_date']))
                
            if int(form.cleaned_data["report_type"]) == REPORTTYPE_SALES_BY_PUBLISHER:
                report = OrgDateReport(date_start,date_end,'advertiser',form.cleaned_data["group_by"],spec=REPORTTYPE_SALES_BY_PUBLISHER,advertiser_set=aids,)
                reportTitle = "Sales and Activity Report by Publisher - %s to %s" % (str(request.POST['start_date']), str(request.POST['end_date']))
                
            if int(form.cleaned_data["report_type"]) == REPORTTYPE_REVENUE:
                report = RevenueReport(date_start,date_end,'advertiser',form.cleaned_data["group_by"],spec=REPORTTYPE_REVENUE,advertiser_set=aids,)
                reportTitle = "Revenue Report - %s to %s" % (str(request.POST['start_date']), str(request.POST['end_date']))
                
            if int(form.cleaned_data["report_type"]) == REPORTTYPE_REVENUE_BY_PUBLISHER:
                report = OrgRevenueReport(date_start,date_end,'advertiser',form.cleaned_data["group_by"],spec=REPORTTYPE_REVENUE_BY_PUBLISHER,advertiser_set=aids,)
                reportTitle = "Revenue Report by Publisher - %s to %s" % (str(request.POST['start_date']), str(request.POST['end_date']))
                
            if int(form.cleaned_data["report_type"]) == REPORTTYPE_CREATIVE:
                report = CreativeReport(date_start,date_end,'advertiser',form.cleaned_data["group_by"],spec=REPORTTYPE_CREATIVE,advertiser_set=aids,)
                reportTitle = "Link Report - %s to %s" % (str(request.POST['start_date']), str(request.POST['end_date']))
                
            if int(form.cleaned_data["report_type"]) == REPORTTYPE_CREATIVE_BY_PROMO:
                report = PromoReport(date_start,date_end,'advertiser',form.cleaned_data["group_by"],spec=REPORTTYPE_CREATIVE_BY_PROMO,advertiser_set=aids,)
                reportTitle = "Link Report by Promo Type - %s to %s" % (str(request.POST['start_date']), str(request.POST['end_date']))
                
            if int(form.cleaned_data["report_type"]) == REPORTTYPE_ORDER_DETAIL:
                report = OrderReport(date_start,date_end,'advertiser',form.cleaned_data["group_by"],spec=REPORTTYPE_ORDER_DETAIL,advertiser_set=aids,)
                reportTitle = "Order Detail Report - %s to %s" % (str(request.POST['start_date']), str(request.POST['end_date']))
                
            if int(form.cleaned_data["report_type"]) == REPORTTYPE_PRODUCT_DETAIL:
                report = ProductReport(date_start,date_end,'advertiser',form.cleaned_data["group_by"],spec=REPORTTYPE_PRODUCT_DETAIL,advertiser_set=aids,)
                reportTitle = "Product Detail Report - %s to %s" % (str(request.POST['start_date']), str(request.POST['end_date']))
                 
            if int(form.cleaned_data["report_type"]) == REPORTTYPE_ACCOUNTING:
                report = AccountingReport(date_start,date_end,'advertiser',form.cleaned_data["group_by"],spec=REPORTTYPE_ACCOUNTING,advertiser_set=aids,)
                reportTitle = "Accounting Report - %s to %s" % (str(request.POST['start_date']), str(request.POST['end_date']))
            
        # 5 - GENERATE & DOWNLOAD REPORT (GET)
        if request.POST.get("target",None) is not None:        	
            target = request.POST.get("target")
            if target == "xls":	        
                response =  HttpResponse(render_to_string("misc/reports/download.xls",{"report":report}),mimetype="application/vnd.ms-excel")
                response['Content-Disposition'] = 'attachment; filename=report.xls'
                return response
            elif target == "csv":
                response =  HttpResponse(render_to_string("misc/reports/download.csv",{"report":report}),mimetype="text/csv")
                response['Content-Disposition'] = 'attachment; filename=report.csv'
                return response
    
            elif target == "tab":
                response =  HttpResponse(render_to_string("misc/reports/download.txt",{"report":report}),mimetype="application/octet-stream")
                response['Content-Disposition'] = 'attachment; filename=report.txt'
                return response

        # 6 - GENERATE & DISPLAY REPORT (POST)
        else:
            return AQ_render_to_response(request, "network/reports/network-advertiser.html",{
                "form":form,
                "report":report,
                },context_instance=RequestContext(request))
                
    return AQ_render_to_response(request, "network/reports/network-advertiser.html",{
        "form":form,
        "report":report,
        "reportTitle": reportTitle
        },context_instance=RequestContext(request))


@url(r"^reports/network/publisher/$","network_reports_network_publisher_reports")
@tab("Network","Reports","Network Publisher Reports")
@admin_required
def network_reports_network_publisher_reports(request):
    # IMPORTS
    from forms import ReportFormNetworkPublisher
    
    # INITIALIZATIONS
    report = None
    form = ReportFormNetworkPublisher(request.user)
    reportTitle = None
    
    # POST : GENERATE AND DISPLAY REPORT
    # - OR - 
    # GET : GENERATE AND SERVE DOWNLOAD REPORT
    if request.POST:
        # 1 - SET FROM WITH POST DATA & VALIDATE
        form = ReportFormNetworkPublisher(request.user,request.POST)
        
        if form.is_valid():
        # 2 - PROCESS DATES
            x = request.POST['start_date'].split("/")
            start_date_array = []
            for numbers in x:
                start_date_array.append(int(numbers))
            date_start = datetime.datetime(start_date_array[2],start_date_array[0],start_date_array[1])
            
            x = request.POST['end_date'].split("/")
            end_date_array = []
            for numbers in x:
                end_date_array.append(int(numbers))
            date_end = datetime.datetime(end_date_array[2],end_date_array[0],end_date_array[1])
            
        # 3 - PROCESS PUBLISHER IDS
            all_publishers = request.user.get_profile().admin_assigned_publishers()
    
            pids = []
            if form.cleaned_data["run_reporting_by"] == '0': # all publishers
                pids = [j.id for j in all_publishers]
            elif form.cleaned_data["run_reporting_by"] == '1': # specific publisher
                pids.append(int(form.cleaned_data["specific_publisher"][2:]))
            elif form.cleaned_data["run_reporting_by"] == '2': # publisher by category
                pids = []
                for j in all_publishers:
                    for site in j.website_set.all():
                        if site.vertical in form.cleaned_data["publisher_category"]:
                            pids.append(j.id)
                            
        # 4 - PROCESS REPORT TYPE        
            if int(form.cleaned_data["report_type"]) == REPORTTYPE_SALES:
                report = DateReport(date_start,date_end,'publisher',form.cleaned_data["group_by"],spec=REPORTTYPE_SALES,publisher_set=pids,)
                reportTitle = "Sales and Activity Report - %s to %s" % (str(request.POST['start_date']), str(request.POST['end_date']))
                
            if int(form.cleaned_data["report_type"]) == REPORTTYPE_SALES_BY_ADVERTISER:
                report = OrgDateReport(date_start,date_end,'publisher',form.cleaned_data["group_by"],spec=REPORTTYPE_SALES_BY_ADVERTISER,publisher_set=pids,)
                reportTitle = "Sales and Activity Report by Advertiser - %s to %s" % (str(request.POST['start_date']), str(request.POST['end_date']))
                
            if int(form.cleaned_data["report_type"]) == REPORTTYPE_REVENUE:
                report = RevenueReport(date_start,date_end,'publisher',form.cleaned_data["group_by"],spec=REPORTTYPE_REVENUE,publisher_set=pids,)
                reportTitle = "Revenue Report - %s to %s" % (str(request.POST['start_date']), str(request.POST['end_date']))
                
            if int(form.cleaned_data["report_type"]) == REPORTTYPE_REVENUE_BY_ADVERTISER:
                report = OrgRevenueReport(date_start,date_end,'publisher',form.cleaned_data["group_by"],spec=REPORTTYPE_REVENUE_BY_ADVERTISER,publisher_set=pids,)
                reportTitle = "Revenue Report by Advertiser - %s to %s" % (str(request.POST['start_date']), str(request.POST['end_date']))
                
            if int(form.cleaned_data["report_type"]) == REPORTTYPE_CREATIVE:
                report = CreativeReport(date_start,date_end,'publisher',form.cleaned_data["group_by"],spec=REPORTTYPE_CREATIVE,publisher_set=pids,)
                reportTitle = "Link Report - %s to %s" % (str(request.POST['start_date']), str(request.POST['end_date']))
                
            if int(form.cleaned_data["report_type"]) == REPORTTYPE_ORDER_DETAIL:
                report = OrderReport(date_start,date_end,'publisher',form.cleaned_data["group_by"],spec=REPORTTYPE_ORDER_DETAIL,publisher_set=pids,)
                reportTitle = "Order Detail Report - %s to %s" % (str(request.POST['start_date']), str(request.POST['end_date']))
                
            if int(form.cleaned_data["report_type"]) == REPORTTYPE_ACCOUNTING:
                report = AccountingReport(date_start,date_end,'publisher',form.cleaned_data["group_by"],spec=REPORTTYPE_ACCOUNTING,publisher_set=pids,)
                reportTitle = "Accounting Report - %s to %s" % (str(request.POST['start_date']), str(request.POST['end_date']))
        
        # 5 - GENERATE & DOWNLOAD REPORT (GET)
        if request.POST.get("target",None) is not None:
            if report:
                target = request.POST.get("target")
                if target == "xls":
                    response =  HttpResponse(render_to_string("misc/reports/download.xls",{"report":report}),mimetype="application/vnd.ms-excel")
                    response['Content-Disposition'] = 'attachment; filename=report.xls'
                    return response
                elif target == "csv":
                    response =  HttpResponse(render_to_string("misc/reports/download.csv",{"report":report}),mimetype="text/csv")
                    response['Content-Disposition'] = 'attachment; filename=report.csv'
                    return response
                elif target == "tab":
                    response =  HttpResponse(render_to_string("misc/reports/download.txt",{"report":report}),mimetype="application/octet-stream")
                    response['Content-Disposition'] = 'attachment; filename=report.txt'
                    return response
                    
        # 6 - GENERATE & DISPLAY REPORT (POST)
        else:
            return AQ_render_to_response(request, "network/reports/network-publisher.html",{
                "form":form,
                "report":report,
                "reportTitle":reportTitle,
                },context_instance=RequestContext(request))
            
    return AQ_render_to_response(request, "network/reports/network-publisher.html",{
        "form":form,
        "report":report
        },context_instance=RequestContext(request))
                
        
@url(r"^reports/publisher/$","network_reports_publisher_reports")
@tab("Network","Reports","Publisher Reports")
@admin_required
def network_reports_publisher_reports(request):
    return AQ_render_to_response(request, 'network/reports/publisher.html', {
        }, context_instance=RequestContext(request))


@url(r"^reports/advertiser/$","network_reports_advertiser_reports")
@tab("Network","Reports","Advertiser Reports")
@admin_required
def network_reports_advertiser_reports(request):
    return AQ_render_to_response(request, 'network/reports/advertiser.html', {
        }, context_instance=RequestContext(request))

