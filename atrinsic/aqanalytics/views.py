from aqanalytics.analytics import AqAnalytics
from atrinsic.util.imports import *
from django.template import RequestContext

def get_report(request,report_name):
    return HttpResponse(report_name)
    
def login(request):
    from forms import LoginForm
    from models import Users
    inits = {}
    inits['organization'] = request.organization.id
    if request.POST:
        inits['email'] = request.POST['email']
        inits['password'] = request.POST['password']
        form = LoginForm(inits)
        if form.is_valid():
            user,x = Users.objects.get_or_create(**form.cleaned_data)
            request.session['analytics'] = AqAnalytics(request.POST['email'],request.POST['password'])
            return HttpResponseRedirect("/analytics/site_list/")
    else:
        form = LoginForm(initial = inits)
        
    return render_to_response("login.html",{"form":form}, context_instance=RequestContext(request))
    
def site_list(request):
    if request.session.has_key("analytics"):
        aa_obj = request.session['analytics']
    else:
        user = Users.objects.get(organization = request.organization)
        aa_obj = AqAnalytics(user_name=user.email, password=user.password)
    if aa_obj.authenticate():
        sites = aa_obj.GetSiteList()
    else:
        sites = []
    return render_to_response("site_list.html",{"site_list":sites}, context_instance=RequestContext(request))
    
def select_site(request,table_id):
    request.session['selected_site'] = table_id
    return HttpResponseRedirect("/analytics/reporting/")
    
def reporting(request):
    from forms import ReportForm
    from analytics import get_html,get_html_table,get_flash_chart
    from models import Users
    report = ""
    errors = []
    if request.POST:
        report_form = ReportForm(request.POST)
        if report_form.is_valid():
            if request.session.has_key("analytics"):
                aa_obj = request.session['analytics']
            else:
                user = Users.objects.get(organization = request.organization)
                aa_obj = AqAnalytics(user_name=user.email, password=user.password)
            aa_obj.authenticate()
            
            if report_form.cleaned_data['chart_type'] == 'table':
                report,row_count,is_valid = aa_obj.DataFeedQuery(parse_as='flat',**report_form.cleaned_data)
                if is_valid == True:
                    report = get_html_table(report[0],report[1],row_count)
                
            elif report_form.cleaned_data['chart_type'][:5] == 'chart':
                report = get_flash_chart(**report_form.cleaned_data)
                
            else:
                report = ''
                errors = is_valid
    else:
        report_form = ReportForm(initial = {"table_id" : request.analytics.selected_site})
        
    if request.is_ajax():
        return report
    else:
        return render_to_response("reports.html",{ "report":report,"form":report_form, 'error_list':errors }, context_instance=RequestContext(request))

def get_flash_chart_data(request,chart_type,start_date,end_date):
    from datetime import datetime
    from atrinsic.web import openFlashChart
    from atrinsic.web.openFlashChart_varieties import Styler
    table_id = request.GET.get('table_id')
    report_type = request.GET.get('report_type')
    max_results = request.GET.get('max_results')
    sort = request.GET.get('sort')
    filters = request.GET.get('filters')
    if request.session.has_key("analytics"):
        aa_obj = request.session['analytics']
    else:
        user = Users.objects.get(organization = request.organization)
        aa_obj = AqAnalytics(user_name=user.email, password=user.password)
    aa_obj.authenticate()
    report,row_count,is_valid = aa_obj.DataFeedQuery(start_date,end_date,table_id,report_type,'array',sort,filters,max_results,chart_type)
    Style = Styler(chart_type[6:])
    
    labels = []
    var1 = []
    var2 = []
    for row in report[0]:
        try:
            labels.append(row[0])
        except:
            pass
        try:
            var1.append(row[1])
        except:
            pass
        try:
            var2.append(row[2])
        except:
            pass
    chart = openFlashChart.template('')
    chart.set_bg_colour(colour='#ffffff')
    if len(var1) > 0:
        range_y1_min = round(float(min(var1))*0.95,0)
        range_y1_max = round(float(max(var1))*1.05,0)
        range_y1_steps = round(round(float(max(var1))*1.05,0)/10,0)
    else:
        if len(var2) > 0:
            range_y1_min = round(float(min(var2))*0.95,0)
            range_y1_max = round(float(max(var2))*1.05,0)
            range_y1_steps = round(round(float(max(var2))*1.05,0)/10,0)
        else:
            range_y1_min = 0
            range_y1_max = 0
            range_y1_steps = 0
    if len(var2) > 0:
        range_y2_min = round(float(min(var2))*0.95,0)
        range_y2_max = round(float(max(var2))*1.05,0)
        range_y2_steps = round(round(float(max(var2))*1.05,0)/10,0)
    else:
        range_y2_min = 0
        range_y2_max = 0
        range_y2_steps = 0
        
    chart.set_y_axis(min = range_y1_min, max = range_y1_max, steps = range_y1_steps)
    if (range_y2_steps > 0):
        chart.set_y_axis_right(min = range_y2_min, max = range_y2_max, steps = range_y2_steps),
    chart.set_x_axis(labels = {'labels':labels, 'rotate':'vertical'})
    
    plot1 =  Style(fontsize = 20, values = var1)
    plot1.set_colour('#4f8dbc')

    plot2 =  Style(fontsize = 20, values = var2)
    plot2.set_colour('#54b928')
    plot2.set_y_axis_right()
    
    if chart_type != 'pie':
        chart.add_element(plot1)
        chart.add_element(plot2)
    else:
        chart.add_element(plot1)
    return HttpResponse(chart.encode())
