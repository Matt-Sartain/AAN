from atrinsic.util.imports import *
from forms import *
from reports import *
import openFlashChart
from openFlashChart_varieties import (Line,Line_Dot,Line_Hollow,Bar,Bar_Filled,Bar_Glass,Bar_3d,Bar_Sketch,HBar,Bar_Stack,Area_Line,Area_Hollow,Pie,Scatter,Scatter_Line)
from openFlashChart_varieties import (dot_value,hbar_value,bar_value,bar_3d_value,bar_glass_value,bar_sketch_value,bar_stack_value,pie_value,scatter_value,x_axis_labels,x_axis_label)

def dashboard(request, org):
	pids,aids = request.organization.get_dashboard_filtered_orgs()
	
	var1 = request.organization.dashboard_variable1
	var1_name = request.organization.get_dashboard_variable1_display()
	
	today_range = compute_date_range(REPORTTIMEFRAME_TODAY,True)
	yesterday_range = compute_date_range(REPORTTIMEFRAME_YESTERDAY,True)
	mtd_range = compute_date_range(REPORTTIMEFRAME_MONTHTODATE,True)
	ytd_range = compute_date_range(REPORTTIMEFRAME_YEARTODATE,True)
	
	number_of_var1 = request.organization.get_metric(var1,today_range,aids,pids)
	yesterday = request.organization.get_metric(var1,yesterday_range,aids,pids)
	
	monthly_var1 = request.organization.get_chart_vars(var1,mtd_range,0,aids,pids)
	yearly_var1 = request.organization.get_chart_vars(var1,ytd_range,0,aids,pids)
	try:
		month_high = int(max([monthly_var1[1][1]]))
		month_low = int(min([monthly_var1[1][1]]))
	except:
		month_high = 0
		month_low = 0
	try:
		ytd_high = int(max([yearly_var1[1][1]]))
		ytd_low = int(min([yearly_var1[1][1]]))
	except:
		ytd_high = 0
		ytd_low = 0
	total_mtd = request.organization.get_metric(var1,mtd_range,aids,pids)
	total_ytd = request.organization.get_metric(var1,ytd_range,aids,pids)
	daily_avg = request.organization.get_metric(var1,ytd_range,aids,pids)/(ytd_range[1]-ytd_range[0]).days
	orders = request.organization.get_metric(METRIC_ORDERS,ytd_range,aids,pids)
	clicks = request.organization.get_metric(METRIC_CLICKS,ytd_range,aids,pids)
	amount = request.organization.get_metric(METRIC_AMOUNT,ytd_range,aids,pids)
	impressions = request.organization.get_metric(METRIC_IMPRESSIONS,ytd_range,aids,pids)
	if orders == 0: aov = 0
	else:
		aov = float(amount) / float(orders)
		aov = currency_formatter(aov,request.organization)
	if clicks == 0: epc = 0
	else:
		epc = float(amount) / float(clicks)
		epc = currency_formatter(epc,request.organization)
	
	if clicks == 0: cpc = 0
	else:
		cpc = float(amount) / float(clicks)
		cpc = currency_formatter(cpc,request.organization)
	
	if impressions == 0: cpm = 0
	else:
		cpm = float(amount) / float(impressions)
		cpm = currency_formatter(cpm,request.organization)
	custom_date_range_start = request.GET.get('custom_date_range_start', None)
	custom_date_range_end = request.GET.get('custom_date_range_end',None)
	if request.session.has_key("date_range") == False:
		date_range = REPORTTIMEFRAME_PAST30DAYS
	else:
		date_range = request.session["date_range"]
	
	if (custom_date_range_start != None) & (custom_date_range_end != None):
		try:
			date_start = datetime.date(int(custom_date_range_start[6:10]),int(custom_date_range_start[:2]),int(custom_date_range_start[3:5]))
			date_end = datetime.date(int(custom_date_range_end[6:10]),int(custom_date_range_end[:2]),int(custom_date_range_end[3:5]))
		except:
			date_start,date_end = compute_date_range(date_range,True)
	else:
		date_start,date_end = compute_date_range(date_range,True)
	
	date_range_name = "Custom"
	for rtf_v,rtf_n in REPORTTIMEFRAME_CHOICES:
		if rtf_v == date_range:
			date_range_name = rtf_n
	
	link_report = CreativeReport(date_start,date_end,request.organization,spec=specs['advertiser'][REPORTTYPE_CREATIVE],publisher_set=pids)
	if request.organization.org_type == 1:
		publisher_report = AdvertiserReport(date_start,date_end,request.organization,spec=specs['publisher'][REPORTTYPE_REVENUE_BY_ADVERTISER],advertiser_set=aids)
		sales_report = DateReport(request.organization.dashboard_group_data_by,date_start,date_end,request.organization,spec=specs['publisher'][REPORTTYPE_SALES],advertiser_set=aids)
	else:
		publisher_report = PublisherReport(date_start,date_end,request.organization,spec=specs['advertiser'][REPORTTYPE_REVENUE_BY_PUBLISHER],publisher_set=pids)
		sales_report = DateReport(request.organization.dashboard_group_data_by,date_start,date_end,request.organization,spec=specs['advertiser'][REPORTTYPE_SALES],publisher_set=pids)
		
	pending_applications = Organization.objects.filter(advertiser_relationships__status=RELATIONSHIP_APPLIED, status=ORGSTATUS_LIVE,advertiser_relationships__advertiser=request.organization).extra(select={"advertiser_id":"select advertiser_id from base_or ganization where id="+str(request.organization.id)}).count()
	inquiries = PublisherInquiry.objects.filter(status=INQUIRYSTATUS_UNRESOLVED,advertiser=request.organization)
	from datetime import date
	today = date.today()
	month_span = date(today.year, today.month, 1)
	chart_links = {
		'main_graph':openFlashChart.flashHTML('100%', '200', '/advertiser/get_chart/columns/'+str(month_span)+'/'+str(today)+'/?onevar=1', '/ofc/'),
		'lines':openFlashChart.flashHTML('100%', '400', '/advertiser/get_chart/lines/'+str(date_start)+'/'+str(date_end)+'/', '/ofc/'),
		'pie':openFlashChart.flashHTML('100%', '400', '/advertiser/get_chart/pie/'+str(date_start)+'/'+str(date_end)+'/', '/ofc/'),
		'columns':openFlashChart.flashHTML('100%', '400', '/advertiser/get_chart/columns/'+str(date_start)+'/'+str(date_end)+'/', '/ofc/'),
		'bars':openFlashChart.flashHTML('100%', '400', '/advertiser/get_chart/bars/'+str(date_start)+'/'+str(date_end)+'/', '/ofc/')
	}
	
	return AQ_render_to_response(request, 'commons/dashboard.html', {
		'number_of_var1' : number_of_var1,
		'date_start':date_start.strftime("%m-%d-%Y"),
		'date_end':date_end.strftime("%m-%d-%Y"),
		'date_range_name':date_range_name,
		'var1_name' : var1_name,
		'yesterday' : yesterday,
		'month_high' : month_high,
		'month_low' : month_low,
		'ytd_high' : ytd_high,
		'ytd_low' : ytd_low,
		'total_mtd' : total_mtd,
		'total_ytd' : total_ytd,
		'daily_avg' : daily_avg,
		'aov' : aov,
		'epc' : epc,
		'cpm' : cpm,
		'cpc' : cpc,
		'org': org,
		'sales_report': sales_report,
		'link_report': link_report,
		'publisher_report': publisher_report,
		'pending_applications': pending_applications,
		'inquiries':inquiries,
		'chart_links':chart_links,
	}, context_instance=RequestContext(request))
def dashboard_settings(request,org):
	''' View for the Advertiser Dashboard Settings. '''
	
	if request.method == 'POST':
		form = DashboardSettingsForm(request.POST)
		if form.is_valid():
			for k, v in form.cleaned_data.items():
				setattr(request.organization, k, v)
		request.organization.save()
		return HttpResponseRedirect('/'+str(org)+'/')
	else:
		form = DashboardSettingsForm(initial=request.organization.__dict__)
		return AQ_render_to_response(request, 'commons/dashboard-settings.html', {
		'form': form,
		'org': org,
		}, context_instance=RequestContext(request))
