from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from atrinsic.util.imports import *

tabset("Advertiser",4,"Reports","advertiser_reports",
       [("Reports","advertiser_reports"),
        ("Reporting API","reporting_api_adv"),
        ])


from reports import *
import	openFlashChart
from	openFlashChart_varieties import (Line,Line_Dot,Line_Hollow,Bar,Bar_Filled,Bar_Glass,Bar_3d,Bar_Sketch,HBar,Bar_Stack,Area_Line,Area_Hollow,Pie,Scatter,Scatter_Line)
from	openFlashChart_varieties import (dot_value,hbar_value,bar_value,bar_3d_value,bar_glass_value,bar_sketch_value,bar_stack_value,pie_value,scatter_value,x_axis_labels,x_axis_label)

@url(r"^reports/$","advertiser_reports")
@tab("Advertiser","Reports","Reports")
@advertiser_required
@register_api(None)
def advertiser_reports(request):
    from atrinsic.base.models import Organization,PublisherGroup,UserAqWidget,AqWidget, Report_Adv_Pub
    from forms import ReportForm
    inits = {}
    inits = {
        'start_date':request.GET.get('start_date',None),
        'end_date':request.GET.get('end_date',None),
        'group_by':request.GET.get('group_by',0),
        'run_reporting_by':request.GET.get('run_reporting_by',0),
        'report_type':request.GET.get('report_type',0),
        'specific_advertiser':request.GET.get('specific_advertiser',None),
        'advertiser_category':request.GET.get('advertiser_category',None),
        'run_reporting_by_publisher':request.GET.getlist('run_reporting_by_publisher'),
        'run_reporting_by_vertical':request.GET.getlist('run_reporting_by_vertical'),
        'run_reporting_by_group':request.GET.getlist('run_reporting_by_group'),
    }
        
    this_page = 'advertiser-reports'
    form = ReportForm(request.organization,inits)
    refilter=0
    widget_report = None
    if request.GET:
        if form.is_valid():
            refilter=1
            date_start,date_end = time_period(form)
            if date_start == None:
                date_start = datetime.datetime.now()
            if date_end == None:
                date_end = datetime.datetime.now()
            all_publishers = Organization.objects.filter(advertiser_relationships__status=RELATIONSHIP_ACCEPTED,
                                                     advertiser_relationships__advertiser=request.organization)
            
            pids = []
            if form.cleaned_data["run_reporting_by"] == '0': # all publishers
                pids = [j.id for j in all_publishers]
            elif form.cleaned_data["run_reporting_by"] == '3': # specific publisher
                if inits.has_key("run_reporting_by_publisher"):
                    pids.extend([int(x[2:]) for x in inits["run_reporting_by_publisher"]])
                else:
                    pids = []
                    for j in all_publishers:
                        pids.append(j.id)
            elif form.cleaned_data["run_reporting_by"] == '2': # publisher by category
                pids = []
                
                for j in all_publishers:
                    for site in j.website_set.all():
                        try:
                            if site.vertical in form.cleaned_data["run_reporting_by_vertical"]:
                                pids.append(j.id)
                        except:
                            print '   -  web site with bad vertical: %s -- %s' % (site,site.id)
                
                
            elif form.cleaned_data["run_reporting_by"] == '1': # publisher by group
                for g_id in form.cleaned_data["run_reporting_by_group"]:
                    group = PublisherGroup.objects.get(id=int(g_id[2:]))
                    pids.extend([g.id for g in group.publishers.all()])
            z,created = UserAqWidget.objects.get_or_create(page=this_page,zone=4,organization=request.organization, widget=AqWidget.objects.get(pk=form.cleaned_data["report_type"]))
            z.custom_date_range = date_start.strftime('%m/%d/%Y')+","+date_end.strftime('%m/%d/%Y')
            z.save()
            widget = UserAqWidget.prep([z],request,pids)
            widget_report = widget[0]
        else:
            report = None
            form = ReportForm(request.organization)
    
        if request.GET.get("target",None) or int(request.GET['report_type']) == REPORTTYPE_ORDER_DETAIL:
            if int(request.GET['report_type']) == REPORTTYPE_ORDER_DETAIL:
                target = REPORTFORMAT_CSV
            else:
                target = int(request.GET.get("target"))
                
            from AqWidgets import QuickReports
            if int(form.cleaned_data["report_type"]) == REPORTTYPE_SALES:
                report = DateReport(date_start,date_end,request.organization,group_by=form.cleaned_data["group_by"], spec=REPORTTYPE_SALES, publisher_set=pids)
                                          
            if form.cleaned_data["report_type"] == REPORTTYPE_SALES_BY_PUBLISHER:
                report = OrgDateReport(date_start,date_end,request.organization,group_by=form.cleaned_data["group_by"], spec=REPORTTYPE_SALES_BY_PUBLISHER, publisher_set=pids)
    
            if form.cleaned_data["report_type"] == REPORTTYPE_REVENUE:
                report = RevenueReport(date_start,date_end,request.organization,group_by=form.cleaned_data["group_by"], spec=REPORTTYPE_REVENUE, publisher_set=pids)
    
            if form.cleaned_data["report_type"] == REPORTTYPE_REVENUE_BY_PUBLISHER:
                report = OrgRevenueReport(date_start,date_end,request.organization,group_by=form.cleaned_data["group_by"], spec=REPORTTYPE_REVENUE_BY_PUBLISHER, publisher_set=pids)
    
            if form.cleaned_data["report_type"] == REPORTTYPE_CREATIVE:
                report = CreativeReport(date_start,date_end,request.organization,group_by=form.cleaned_data["group_by"], spec=REPORTTYPE_CREATIVE, publisher_set=pids)
    
            if form.cleaned_data["report_type"] == REPORTTYPE_CREATIVE_BY_PROMO:
                report = PromoReport(date_start,date_end,request.organization,group_by=form.cleaned_data["group_by"], spec=REPORTTYPE_CREATIVE_BY_PROMO, publisher_set=pids)
            
            if form.cleaned_data["report_type"] == REPORTTYPE_ORDER_DETAIL:
                report = OrderReport(date_start,date_end,request.organization,group_by=form.cleaned_data["group_by"], spec=REPORTTYPE_ORDER_DETAIL, publisher_set=pids)
                
            if form.cleaned_data["report_type"] == REPORTTYPE_ACCOUNTING:
                report = AccountingReport(date_start,date_end,request.organization,group_by=form.cleaned_data["group_by"], spec=REPORTTYPE_ACCOUNTING, publisher_set=pids)    

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
                
                #return HttpResponse(str(res))
                write_rows(file_path,res)
                res = open(file_path).read()
                
                #return HttpResponse(str(res))
                
                response = HttpResponse(res,mimetype="application/vnd.ms-excel")
                response['Content-Disposition'] = 'attachment; filename=download.xls'
                return response
                
                
                
                
                
                
                
                
                """ Old way of doing it"""
                response = render_to_response("misc/reports/dataxls.html", {'report': report,})
                filename = "misc/reports/download.xls"                
                response['Content-Disposition'] = 'attachment; filename='+filename
                response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
                return response
            elif target == REPORTFORMAT_CSV:
                response =  HttpResponse(render_to_string("misc/reports/download.csv",{"report":report}),mimetype="text/csv")
                response['Content-Disposition'] = 'attachment; filename=report.csv'
                return response
            elif target == REPORTFORMAT_TSV:
                response =  HttpResponse(render_to_string("misc/reports/download.txt",{"report":report}),mimetype="application/octet-stream")
                response['Content-Disposition'] = 'attachment; filename=report.txt'
                return response
    return AQ_render_to_response(request, "advertiser/reports/index.html",{
        "form":form,
        'refilter':refilter,
        "widget":widget_report,
        "reporting":1,
        "url": 'advertiser/reports/download'#request.META['REQUEST_URI'].replace('advertiser/reports','advertiser/reports/download'),
        },context_instance=RequestContext(request))

    
@url(r"^get_chart/(?P<style>.*)/(?P<date_start>.*)/(?P<date_end>.*)/$","get_chart") 
def get_chart(request,style,date_start,date_end):
    raw_data = get_chart_vars(request,date_start,date_end)
    var1 = []
    var2 = []
    dates = []
    if raw_data['variable1'] != None:
        var_legend = raw_data['variable1_name']
        for items in raw_data['variable1']:
            var1.append(int(items[1]))
            dates.append(str(items[0]))
    if raw_data['variable2'] != None:
        var_legend = raw_data['variable2_name']
        for items in raw_data['variable2']:
            var2.append(int(items[1]))	
    chart = openFlashChart.template('')
    chart.set_bg_colour(colour='#ffffff')
    if len(var1) > 0:
        range_y1_min = round(min(var1)*0.95,0)
        range_y1_max = round(max(var1)*1.05,0)
        range_y1_steps = round(round(max(var1)*1.05,0)/10,0)
    else:
        range_y1_min = 0
        range_y1_max = 0
        range_y1_steps = 0
    if len(var2) > 0:
        range_y2_min = round(min(var2)*0.95,0)
        range_y2_max = round(max(var2)*1.05,0)
        range_y2_steps = round(round(max(var2)*1.05,0)/10,0)
    else:
        range_y2_min = 0
        range_y2_max = 0
        range_y2_steps = 0
    chart.set_y_axis(min = range_y1_min, max = range_y1_max, steps = range_y1_steps)
    chart.set_x_axis(labels = {'labels':dates, 'rotate':'vertical'})
    if style == 'lines':
        plot1 = Line(text = raw_data['variable1_name'], fontsize = 20, values = var1)
        plot2 = Line(text = raw_data['variable2_name'], fontsize = 20, values = var2)
        plot2['axis'] = "right"
        plot2.set_colour('#54b928')
        chart.set_y_axis_right(min = range_y2_min, max = range_y2_max, steps = range_y2_steps)
        if request.GET.get('onevar',None) == None:
            chart.add_element(plot2)
    elif style == 'pie':
        plot1 = Pie(text = raw_data['variable1_name'], fontsize = 20, values = var1, colours = ['#4f8dbc','#54b928'])
    elif style == 'columns':
        plot1 = Bar_Filled(text = raw_data['variable1_name'], fontsize = 20, values = var1)
        plot2 = Bar_Filled(text = raw_data['variable2_name'], fontsize = 20, values = var2)
        plot2['axis'] = "right"
        plot2.set_colour('#54b928')		
        chart.set_y_axis_right(min = range_y2_min, max = range_y2_max, steps = range_y2_steps)
        if request.GET.get('onevar',None) == None:
            chart.add_element(plot2)
    plot1.set_colour('#4f8dbc')
    chart.add_element(plot1)
    return HttpResponse(chart.encode())


@url(r"^reports/download/$","advertiser_reports_download")
@tab("Advertiser","Reports","Reports")
@advertiser_required
@register_api(None)
def advertiser_reports_download(request):

    if request.POST:
        form = ReportFormatForm(request.POST)
        if form.is_valid():
            redir = request.POST.get('redir')
            redir += '&target='
            redir += form.cleaned_data['target']

            return HttpResponseRedirect(redir)

    else:
        redir = request.META['REQUEST_URI'].replace('advertiser/reports/download', 'advertiser/reports')
        form = ReportFormatForm()

    return AQ_render_to_response(request, "advertiser/reports/download.html",{
            'redir' : redir,
            'form' : form,
        },context_instance=RequestContext(request))


@url("^reports/reporting_api/$", "reporting_api_adv")
@tab("Advertiser","Reports","Reporting API")
@register_api(None)
def reporting_api_adv(request):
    import md5
    unique_start_key = str(request.organization)+str(request.organization.date_created)
    m = md5.new()
    m.update(unique_start_key)
    x = m.hexdigest()
    request.organization.api_key = x
    request.organization.save()
    return AQ_render_to_response(request, "advertiser/reports/get_api_key.html",{ 
        'API_KEY' : x,
        'SITE_URL':settings.SITE_URL
    },context_instance=RequestContext(request))


@url("^reports/payment_status/$", "reporting_payment_status")
def reporting_payment_status(request):
    from atrinsic.base.models import Organization, Report_Adv_Pub
    from django.db import connection, transaction
    from django.utils.encoding import smart_str
    cursor = connection.cursor()

    getPubs = """SELECT DISTINCT publisher_id FROM base_report_adv_pub WHERE advertiser_id = %d ORDER BY publisher_id""" % (request.organization.id) 
    cursor.execute(getPubs)
    listOfPubs = cursor.fetchall()
    
    getOrgs = Organization.objects.filter(id__in = [ p[0] for p in listOfPubs ]).order_by("company_name")    
    PaymentStatusQry = """SELECT publisher_id,report_date, sum(impressions), sum(clicks), format(sum(amount),2) 
                          FROM base_report_adv_pub 
                          WHERE advertiser_id = %d
                          GROUP BY MONTH(report_date), publisher_id""" % (request.organization.id)                          
    cursor.execute(PaymentStatusQry)
    paymentStatusRpt = cursor.fetchall()
    
    # Convert dates to Month Year
    for row in paymentStatusRpt:
        row[1].strftime("%B %Y")


    return AQ_render_to_response(request, "advertiser/reports/payment_status_report.html",{ 
        'monthByMonth' : paymentStatusRpt,
        'byPublisher' : getOrgs,
        'total_results' : getOrgs.count(),
    },context_instance=RequestContext(request))         
    

@url("^reports/payment_status/(?P<pub_id>\d+)/$", "reporting_payment_status_by_publisher")
def reporting_payment_status_by_publisher(request, pub_id):
    from atrinsic.base.models import Organization, Report_Adv_Pub
    from django.db import connection, transaction
    from django.utils.encoding import smart_str

    cursor = connection.cursor()        
    PaymentStatusQry = "SELECT a.publisher_id, DATE_FORMAT(a.report_date, '%%Y/%%m/01'), sum(a.impressions), sum(a.clicks), format(sum(a.amount),2), not IsNull(max(b.id)) as approved FROM base_report_adv_pub a LEFT JOIN base_payout_approval_log b on a.advertiser_id = b.advertiser_id and a.publisher_id = b.publisher_id and DATE_FORMAT(a.report_date, '%%Y/%%m/01') = DATE_FORMAT(b.report_date, '%%Y/%%m/01') WHERE a.advertiser_id = " + str(request.organization.id) + " AND a.publisher_id = " + str(pub_id) + " GROUP BY MONTH(a.report_date), a.publisher_id ORDER BY a.report_date DESC"

    cursor.execute(PaymentStatusQry)
    paymentStatusRpt = cursor.fetchall()
    
    outputHTML = """<tr><td>&nbsp;</td><td colspan='3'><table id='rowData' cellspacing='0' width='100%'>"""
    outputHTML += """<tr><th>Month</th><th>Amount</th><th>Action</th></tr>"""
    rowIndex = 0
    strRowClass = ""

    for row in paymentStatusRpt:
        rptDate = datetime.datetime.strptime(row[1], "%Y/%m/%d")        
        if (rowIndex % 2) == 0:
            strRowClass = " class='byMonthStatsOdd'" 
        else:
            strRowClass = ""
        outputHTML += """<tr%s><td>%s</td>
                             <td>%s</td>""" % (strRowClass, rptDate.strftime("%B %Y"), row[4])
        
        if int(row[5]) == 0:
            outputHTML += """<td style='width:30%%;'><a href="" id='/advertiser/reports/payment_status/approve/%s/%s/' class='approveMonth' style='color:blue !important;'>Approve</a></td></tr>""" % (row[0],rptDate.strftime("%B%Y"))
        else:
            outputHTML += """<td>Approved</td></tr>"""
        rowIndex += 1

        if len(paymentStatusRpt) == rowIndex:
            outputHTML += """<tr style='height:10px;'><td colspan='4'>&nbsp;</td></tr>"""
        
    outputHTML += "</table></td></tr>"            
    return HttpResponse(outputHTML)
      

@url("^reports/payment_status/approve/(?P<pub_id>\d+)/(?P<approve_month>.*)/$", "reporting_payment_status_approve_bymonth")
def reporting_payment_status_approve_bymonth(request, pub_id, approve_month):
    from atrinsic.base.models import Organization, Payout_Approval_Log, PublisherRelationship, Report_Adv_Pub
    from django.db import connection, transaction
    from django.utils.encoding import smart_str

    try:
        rptDate = datetime.datetime.strptime(approve_month, "%B%Y")      
    
        cursor = connection.cursor()            
        PaymentStatusQry = "SELECT a.publisher_id, DATE_FORMAT(a.report_date, '%%Y/%%m/01'), sum(a.impressions), sum(a.clicks), format(sum(a.amount),2) FROM base_report_adv_pub a WHERE a.advertiser_id = " + str(request.organization.id) + " AND a.publisher_id = " + str(pub_id) + " AND DATE_FORMAT(a.report_date, '%%Y/%%m/01') = '" + str(rptDate.strftime("%Y/%m/%d")) + "' GROUP BY MONTH(a.report_date), a.publisher_id ORDER BY a.report_date DESC"    
        
        cursor.execute(PaymentStatusQry)        
        paymentStatusRpt = cursor.fetchall()
    
        getPubOrg = Organization.objects.get(id=pub_id)
        p = PublisherRelationship.objects.get(publisher=getPubOrg, advertiser=request.organization)
    
        for row in paymentStatusRpt:    
            if Payout_Approval_Log.objects.filter(advertiser = request.organization,publisher = getPubOrg,report_date = datetime.datetime.strptime(row[1], "%Y/%m/%d")).count() == 0:
                Payout_Approval_Log.objects.create(advertiser = request.organization,
                                                   advertiser_ace_id = request.organization.ace_id,
                                                   publisher = getPubOrg,
                                                   publisher_ace_id = getPubOrg.ace_id,
                                                   program_term = p.program_term,
                                                   report_date = datetime.datetime.strptime(row[1], "%Y/%m/%d"))
                                                    
        return HttpResponse("Approved")
    except:
        return HttpResponse("Declined")   
       
@url("^reports/payment_status/approve/(?P<pub_id>\d+)/$", "reporting_payment_status_approve_bypub")
def reporting_payment_status_approve_bypub(request, pub_id):
    from atrinsic.base.models import Organization, Payout_Approval_Log, PublisherRelationship, Report_Adv_Pub
    from django.db import connection, transaction

    try:
        cursor = connection.cursor()    
        
        PaymentStatusQry = "SELECT a.publisher_id, DATE_FORMAT(a.report_date, '%%Y/%%m/01'), sum(a.impressions), sum(a.clicks), format(sum(a.amount),2) FROM base_report_adv_pub a WHERE a.advertiser_id = " + str(request.organization.id) + " AND a.publisher_id = " + str(pub_id) + " GROUP BY MONTH(a.report_date), a.publisher_id ORDER BY a.report_date DESC"    
        cursor.execute(PaymentStatusQry)        
        paymentStatusRpt = cursor.fetchall()
    
        getPubOrg = Organization.objects.get(id=pub_id)
        p = PublisherRelationship.objects.get(publisher=getPubOrg, advertiser=request.organization)
    
        for row in paymentStatusRpt:  
            if Payout_Approval_Log.objects.filter(advertiser = request.organization,publisher = getPubOrg,report_date = datetime.datetime.strptime(row[1], "%Y/%m/%d")).count() == 0:             
                Payout_Approval_Log.objects.create(advertiser = request.organization,
                                                   advertiser_ace_id = request.organization.ace_id,
                                                   publisher = getPubOrg,
                                                   publisher_ace_id = getPubOrg.ace_id,
                                                   program_term = p.program_term,
                                                   report_date = datetime.datetime.strptime(row[1], "%Y/%m/%d"))
                                                
        return HttpResponse("Approved")
    except:
        return HttpResponse("Declined")      
    