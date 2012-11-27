from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from atrinsic.util.imports import *

tabset("Publisher",4,"Reports","publisher_reports",
       [("Reports","publisher_reports"),
       ("Reporting API","reporting_api_pub"),
       ])

@url(r"^reports/$","publisher_reports")
@tab("Publisher","Reports","Reports")
@publisher_required
@register_api(None)
def publisher_reports(request):
    from forms import ReportFormPublisher
    from atrinsic.base.models import Organization,AqWidget,UserAqWidget
    from reports import *
    inits = {}
    inits = {
        'start_date':request.GET.get('start_date',None),
        'end_date':request.GET.get('end_date',None),
        'group_by':request.GET.get('group_by',0),
        'run_reporting_by':request.GET.get('run_reporting_by',0),
        'report_type':request.GET.get('report_type',0),
        'specific_advertiser':request.GET.get('specific_advertiser'),
        'advertiser_category':request.GET.getlist('advertiser_category'),
    }
    this_page = 'publisher-reports'
    widget_report = None
    report = None
    refilter = 0
    if request.GET:
        form = ReportFormPublisher(request.organization, inits)
        if form.is_valid():
            refilter = 1
            date_start,date_end = time_period(form)
            if date_start == None:
                date_start = datetime.datetime.now()
            if date_end == None:
                date_end = datetime.datetime.now()
            all_advertisers = Organization.objects.filter(publisher_relationships__status=RELATIONSHIP_ACCEPTED,
                                                     publisher_relationships__publisher=request.organization)
    
            aids = []
            
            if form.cleaned_data["run_reporting_by"] == '0': # all advertisers
                aids = [j.id for j in all_advertisers]
            elif form.cleaned_data["run_reporting_by"] == '1': # specific advertiser
                abc = form.cleaned_data["specific_advertiser"]
                aids.append(int(form.cleaned_data["specific_advertiser"][2:]))
            elif form.cleaned_data["run_reporting_by"] == '2': # advertiser by category
                aids = []
                for j in all_advertisers:
                    for site in j.website_set.all():
                        if site.vertical in form.cleaned_data["advertiser_category"]:
                            aids.append(j.id)
                
            z,created = UserAqWidget.objects.get_or_create(page=this_page,zone=4,organization=request.organization, widget=AqWidget.objects.get(pk=form.cleaned_data["report_type"]))
            z.custom_date_range = date_start.strftime('%m/%d/%Y')+","+date_end.strftime('%m/%d/%Y')
            z.save()
            
            widget = UserAqWidget.prep([z],request,aids)
            widget_report = widget[0]
            
        else:
            report = None
            form = ReportFormPublisher(request.organization)

        #if request.GET.get("target",None):
            #target = int(request.GET.get("target"))
            
        if request.GET.get("target",None) or int(request.GET['report_type']) == REPORTTYPE_ORDER_DETAIL:
            if int(request.GET['report_type']) == REPORTTYPE_ORDER_DETAIL:
                target = REPORTFORMAT_CSV
            else:
                target = int(request.GET.get("target"))
            
            if int(form.cleaned_data["report_type"]) == REPORTTYPE_SALES:
                report = DateReport(date_start,date_end,request.organization,form.cleaned_data["group_by"],spec=REPORTTYPE_SALES,
                                    advertiser_set=aids,
                                    )          
    
            if form.cleaned_data["report_type"] == REPORTTYPE_SALES_BY_ADVERTISER:
                report = OrgDateReport(date_start,date_end,request.organization,spec=REPORTTYPE_SALES_BY_ADVERTISER,
                                          advertiser_set=aids,
                                          )
    
            if form.cleaned_data["report_type"] == REPORTTYPE_REVENUE:
                report = RevenueReport(date_start,date_end,request.organization,form.cleaned_data["group_by"],spec=REPORTTYPE_REVENUE,
                                    advertiser_set=aids,
                                    )
    
            if form.cleaned_data["report_type"] == REPORTTYPE_REVENUE_BY_ADVERTISER:
                report = OrgRevenueReport(date_start,date_end,request.organization,form.cleaned_data["group_by"],spec=REPORTTYPE_REVENUE_BY_ADVERTISER,
                                          advertiser_set=aids,
                                          )
                
            if form.cleaned_data["report_type"] == REPORTTYPE_CREATIVE:
                report = CreativeReport(date_start,date_end,request.organization,form.cleaned_data["group_by"],spec=REPORTTYPE_CREATIVE,
                                    advertiser_set=aids,
                           )
    
            if form.cleaned_data["report_type"] == REPORTTYPE_CREATIVE_BY_PROMO:
                report = PromoReport(date_start,date_end,request.organization,form.cleaned_data["group_by"],spec=REPORTTYPE_CREATIVE_BY_PROMO,
                                     advertiser_set=aids,
                           )

            if form.cleaned_data["report_type"] == REPORTTYPE_ORDER_DETAIL:
                report = OrderReport(date_start,date_end,request.organization,spec=REPORTTYPE_ORDER_DETAIL,
                                     advertiser_set=aids,
                           )
    
            if form.cleaned_data["report_type"] == REPORTTYPE_ACCOUNTING:
                report = OrgDateReport(date_start,date_end,request.organization,form.cleaned_data["group_by"],spec=REPORTTYPE_ACCOUNTING,
                                          advertiser_set=aids,
                           )
            """
            if form.cleaned_data["report_type"] == REPORTTYPE_ORDER_DETAIL:
                report = OrderReport(date_start,date_end,request.organization,form.cleaned_data["group_by"],spec=REPORTTYPE_ORDER_DETAIL,
                                     publisher_set=pids,
                           )
            """
            
            if form.cleaned_data["report_type"] == REPORTTYPE_ACCOUNTING:
                report = OrgDateReport(date_start,date_end,request.organization,form.cleaned_data["group_by"],spec=REPORTTYPE_ACCOUNTING,
                                    publisher_set=pids,
                           )
            if report:
                if target == REPORTFORMAT_EXCEL:
                    from atrinsic.util.xls import write_rows
                    import tempfile
                    
                    file_id,file_path = tempfile.mkstemp()
                    
                    res = [[]]
                    
                    for row in report.RenderHeader():
                        res[0].append(row[0])
                    
                    for row in report.RenderContents():
                        res.append(row)
                    
                    last_row = []
                    res.append([])
                    for row in report.RenderFooter():
                        last_row.append(row[1])
                    res.append(last_row)
                    
                    #return HttpResponse('test')
                    write_rows(file_path,res)
                    res = open(file_path).read()
                    
                    response = HttpResponse(res,mimetype="application/vnd.ms-excel")
                    response['Content-Disposition'] = 'attachment; filename=report.xls'
                    return response
                    
                    """ The foloowing is the old way of doing it. """
                    #response =  HttpResponse(render_to_string("misc/reports/download.xls",{"report":report}),mimetype="application/vnd.ms-excel")
                    #response['Content-Disposition'] = 'attachment; filename=report.xls'
                    return response
                elif target == REPORTFORMAT_CSV:
                    response =  HttpResponse(render_to_string("misc/reports/download.csv",{"report":report}),mimetype="text/csv")
                    response['Content-Disposition'] = 'attachment; filename=report.csv'
                    return response
        
                elif target == REPORTFORMAT_TSV:
                    response =  HttpResponse(render_to_string("misc/reports/download.txt",{"report":report}),mimetype="application/octet-stream")
                    response['Content-Disposition'] = 'attachment; filename=report.txt'
                    return response
    else:
        form = ReportFormPublisher(request.organization)
    return AQ_render_to_response(request, "publisher/reports/index.html",{
        "form":form,
        'refilter':refilter,
        "widget":widget_report,
        "reporting":1,
        "url":'publisher/reports/download'#request.META['REQUEST_URI'].replace('publisher/reports','publisher/reports/download'),
        },context_instance=RequestContext(request))



@url(r"^reports/download/$","publisher_reports_download")
@tab("Publisher","Reports","Reports")
@publisher_required
def publisher_reports_download(request):

    if request.POST:
        form = ReportFormatForm(request.POST)

        if form.is_valid():
            redir = request.POST.get('redir')
            redir += '&target='
            redir += form.cleaned_data['target']
            
            return HttpResponseRedirect(redir)

    else:
        redir = request.META['REQUEST_URI'].replace('publisher/reports/download', 'publisher/reports')
        form = ReportFormatForm()
        
    return AQ_render_to_response(request, "publisher/reports/download.html",{
            'redir' : redir,
            'form' : form,
        },context_instance=RequestContext(request))

                        
@url("^reports/reporting_api/$", "reporting_api_pub")
@tab("Publisher","Reports","Reporting API")
@register_api(None)
def reporting_api_pub(request):
    import md5
    unique_start_key = str(request.organization)+str(request.organization.date_created)
    
    m = md5.new()
    m.update(unique_start_key)
    x = m.hexdigest()
    request.organization.api_key = x
    request.organization.save()
    inits = {}
    if request.POST:
        inits['report_type'] = request.POST['report_type']
        inits['format_type'] = request.POST['format_type']
        inits['start_date'] = request.POST['start_date']
        inits['end_date'] = request.POST['end_date']
    return AQ_render_to_response(request, "publisher/reports/get_api_key.html",{ 
        'API_KEY' : x,
        'SITE_URL':settings.SITE_URL,
        'inits' : inits,
    },context_instance=RequestContext(request))