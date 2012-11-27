from atrinsic.util.imports import *
from atrinsic.util.date import *
from atrinsic.web.reports import *

def GetScoreBoard(request):
    score_board = {
        'number_of_var1' : 0,
        'var1_name' : '',
        'yesterday' : 0,
        'month_high' : 0,
        'month_low' : 0,
        'ytd_high' : 0,
        'ytd_low' : 0,
        'total_mtd' : 0,
        'total_ytd' : 0,
        'daily_avg' : 0,
        'aov' : 0,
        'epc' : 0,
        'cpm' : 0,
        'cpc' : 0
    }
    
    pids,aids = request.organization.get_dashboard_filtered_orgs()
    
    var1 = request.organization.dashboard_variable1
    var1_name = request.organization.get_dashboard_variable1_display()
    
    today_range = compute_date_range(REPORTTIMEFRAME_TODAY)
    yesterday_range = compute_date_range(REPORTTIMEFRAME_YESTERDAY)
    mtd_range = compute_date_range(REPORTTIMEFRAME_MONTHTODATE)
    ytd_range = compute_date_range(REPORTTIMEFRAME_YEARTODATE)
    abort = False
    number_of_var1 = 0
    yesterday = 0
    from django.db import connection, transaction	
    cursor = connection.cursor()
    if request.organization.is_advertiser():
        query_relation = " advertiser_id = "+str(int(request.organization.id))
    elif request.organization.is_publisher():
        query_relation = " publisher_id = "+str(int(request.organization.id))
    if var1 == METRIC_IMPRESSIONS:
        yesterday_query = "SELECT ceiling(sum(impressions)) FROM base_report_adv_pub WHERE report_date BETWEEN '" +yesterday_range[0].strftime("%Y-%m-%d %H:%M:%S")+ "' and '" +yesterday_range[1].strftime("%Y-%m-%d %H:%M:%S")+ "' and "+query_relation+" GROUP BY report_date"
        today_query = "SELECT ceiling(sum(impressions)) FROM base_report_adv_pub WHERE report_date BETWEEN '"+today_range[0].strftime("%Y-%m-%d %H:%M:%S")+"' and '"+today_range[1].strftime("%Y-%m-%d %H:%M:%S")+"' and "+query_relation+" GROUP BY report_date"
        month_query = "SELECT ceiling(sum(impressions)) FROM base_report_adv_pub WHERE report_date BETWEEN '"+mtd_range[0].strftime("%Y-%m-%d %H:%M:%S")+"' and '"+mtd_range[1].strftime("%Y-%m-%d %H:%M:%S")+"' and "+query_relation+" GROUP BY report_date"
        year_query = "SELECT ceiling(sum(impressions)) FROM base_report_adv_pub WHERE report_date BETWEEN '"+ytd_range[0].strftime("%Y-%m-%d %H:%M:%S")+"' and '"+ytd_range[1].strftime("%Y-%m-%d %H:%M:%S")+"' and "+query_relation+" GROUP BY report_date" 
    elif var1 == METRIC_CLICKS:
        yesterday_query = "SELECT ceiling(sum(clicks)) FROM base_report_adv_pub WHERE report_date BETWEEN '"+yesterday_range[0].strftime("%Y-%m-%d %H:%M:%S")+"' and '"+yesterday_range[1].strftime("%Y-%m-%d %H:%M:%S")+"' and "+query_relation+" GROUP BY report_date"
        today_query = "SELECT ceiling(sum(clicks)) FROM base_report_adv_pub WHERE report_date BETWEEN '"+today_range[0].strftime("%Y-%m-%d %H:%M:%S")+"' and '"+today_range[1].strftime("%Y-%m-%d %H:%M:%S")+"' and "+query_relation+" GROUP BY report_date"
        month_query = "SELECT ceiling(sum(clicks)) FROM base_report_adv_pub a WHERE report_date BETWEEN '"+mtd_range[0].strftime("%Y-%m-%d %H:%M:%S")+"' and '"+mtd_range[1].strftime("%Y-%m-%d %H:%M:%S")+"' and "+query_relation+" GROUP BY report_date"
        year_query = "SELECT ceiling(sum(clicks)) FROM base_report_adv_pub a WHERE report_date BETWEEN '"+ytd_range[0].strftime("%Y-%m-%d %H:%M:%S")+"' and '"+ytd_range[1].strftime("%Y-%m-%d %H:%M:%S")+"' and "+query_relation+" GROUP BY report_date"
    elif var1 == METRIC_LEADS:
        yesterday_query = "SELECT ceiling(sum(leads)) FROM base_report_adv_pub WHERE report_date BETWEEN '"+yesterday_range[0].strftime("%Y-%m-%d %H:%M:%S")+"' and '"+yesterday_range[1].strftime("%Y-%m-%d %H:%M:%S")+"' and "+query_relation+" GROUP BY date(report_date)"
        today_query = "SELECT ceiling(sum(leads)) FROM base_report_adv_pub WHERE report_date BETWEEN '"+today_range[0].strftime("%Y-%m-%d %H:%M:%S")+"' and '"+today_range[1].strftime("%Y-%m-%d %H:%M:%S")+"' and "+query_relation+" GROUP BY date(report_date)"
        month_query = "SELECT ceiling(sum(leads)) FROM base_report_adv_pub a WHERE report_date BETWEEN '"+mtd_range[0].strftime("%Y-%m-%d %H:%M:%S")+"' and '"+mtd_range[1].strftime("%Y-%m-%d %H:%M:%S")+"' and "+query_relation+" GROUP BY date(report_date)"
        year_query = "SELECT ceiling(sum(leads)) FROM base_report_adv_pub a WHERE report_date BETWEEN '"+ytd_range[0].strftime("%Y-%m-%d %H:%M:%S")+"' and '"+ytd_range[1].strftime("%Y-%m-%d %H:%M:%S")+"' and "+query_relation+" GROUP BY date(report_date)" 
    elif var1 == METRIC_ORDERS:
        yesterday_query = "SELECT ceiling(sum(orders)) FROM base_report_adv_pub a WHERE report_date BETWEEN '"+yesterday_range[0].strftime("%Y-%m-%d %H:%M:%S")+"' and '"+yesterday_range[1].strftime("%Y-%m-%d %H:%M:%S")+"' and "+query_relation+" GROUP BY date(a.report_date)"
        today_query = "SELECT ceiling(sum(orders)) FROM base_report_adv_pub a WHERE report_date BETWEEN '"+today_range[0].strftime("%Y-%m-%d %H:%M:%S")+"' and '"+today_range[1].strftime("%Y-%m-%d %H:%M:%S")+"' and "+query_relation+" GROUP BY date(a.report_date)" 
        month_query = "SELECT ceiling(sum(orders)) FROM base_report_adv_pub a WHERE report_date BETWEEN '"+mtd_range[0].strftime("%Y-%m-%d %H:%M:%S")+"' and '"+mtd_range[1].strftime("%Y-%m-%d %H:%M:%S")+"' and "+query_relation+" GROUP BY date(a.report_date)"
        year_query = "SELECT ceiling(sum(orders)) FROM base_report_adv_pub a WHERE report_date BETWEEN '"+ytd_range[0].strftime("%Y-%m-%d %H:%M:%S")+"' and '"+ytd_range[1].strftime("%Y-%m-%d %H:%M:%S")+"' and "+query_relation+" GROUP BY date(a.report_date)" 
    elif var1 == METRIC_AMOUNT:
        yesterday_query =   "SELECT ceiling(sum(amount)) FROM base_report_adv_pub a WHERE report_date BETWEEN '"+yesterday_range[0].strftime("%Y-%m-%d %H:%M:%S")+"' and '"+yesterday_range[1].strftime("%Y-%m-%d %H:%M:%S")+"' and "+query_relation+" GROUP BY date(a.report_date)"
        today_query =       "SELECT ceiling(sum(amount)) FROM base_report_adv_pub a WHERE report_date BETWEEN '"+today_range[0].strftime("%Y-%m-%d %H:%M:%S")+"' and '"+today_range[1].strftime("%Y-%m-%d %H:%M:%S")+"' and "+query_relation+" GROUP BY date(a.report_date)" 
        month_query =       "SELECT ceiling(sum(amount)) FROM base_report_adv_pub a WHERE report_date BETWEEN '"+mtd_range[0].strftime("%Y-%m-%d %H:%M:%S")+"' and '"+mtd_range[1].strftime("%Y-%m-%d %H:%M:%S")+"' and "+query_relation+" GROUP BY date(a.report_date)"
        year_query =        "SELECT ceiling(sum(amount)) FROM base_report_adv_pub a WHERE report_date BETWEEN '"+ytd_range[0].strftime("%Y-%m-%d %H:%M:%S")+"' and '"+ytd_range[1].strftime("%Y-%m-%d %H:%M:%S")+"' and "+query_relation+" GROUP BY date(a.report_date)" 
    elif var1 == METRIC_COMMISSION_EARNED:
        yesterday_query =   "SELECT ceiling(sum(publisher_commission)) FROM base_report_adv_pub a WHERE report_date BETWEEN '"+yesterday_range[0].strftime("%Y-%m-%d %H:%M:%S")+"' and '"+yesterday_range[1].strftime("%Y-%m-%d %H:%M:%S")+"' and "+query_relation+" GROUP BY date(a.report_date)"
        today_query =       "SELECT ceiling(sum(publisher_commission)) FROM base_report_adv_pub a WHERE report_date BETWEEN '"+today_range[0].strftime("%Y-%m-%d %H:%M:%S")+"' and '"+today_range[1].strftime("%Y-%m-%d %H:%M:%S")+"' and "+query_relation+" GROUP BY date(a.report_date)" 
        month_query =       "SELECT ceiling(sum(publisher_commission)) FROM base_report_adv_pub a WHERE report_date BETWEEN '"+mtd_range[0].strftime("%Y-%m-%d %H:%M:%S")+"' and '"+mtd_range[1].strftime("%Y-%m-%d %H:%M:%S")+"' and "+query_relation+" GROUP BY date(a.report_date)"
        year_query =        "SELECT ceiling(sum(publisher_commission)) FROM base_report_adv_pub a WHERE report_date BETWEEN '"+ytd_range[0].strftime("%Y-%m-%d %H:%M:%S")+"' and '"+ytd_range[1].strftime("%Y-%m-%d %H:%M:%S")+"' and "+query_relation+" GROUP BY date(a.report_date)" 
    else:
        yesterday_query = ""
        today_query = "" 
        month_query = ""
        year_query  = ""
        abort = True
    if not abort:
        cursor.execute(today_query)
        today_var1 = cursor.fetchall()
        cursor.execute(yesterday_query)
        yest_var1 = cursor.fetchall()
        cursor.execute(month_query)
        monthly_var1 = cursor.fetchall()
        cursor.execute(year_query)
        yearly_var1 = cursor.fetchall()
        
        month_high = 0
        ytd_high = 0
            
        if len(today_var1) > 0:
            try:
                number_of_var1 = int(today_var1[0][0])
            except:
                number_of_var1= 0
        else:
            number_of_var1= 0
        
        if len(yest_var1) > 0:
            yesterday = yest_var1[0][0]
        else:
            yesterday = 0
        
        try : 
            month_low = monthly_var1[0][0]    
        except:
            month_low = 0
        for item_m in monthly_var1:
            if int(item_m[0]) > month_high:
                month_high = int(item_m[0])
            if int(item_m[0]) < month_low:
                month_low = int(item_m[0])
            #if item_m[0].day == datetime.datetime.now().day:
            #if item_m[0].day == datetime.datetime.now().day-1:
                #yesterday = int(item_m[1])
                
        try : 
            ytd_low = yearly_var1[0][0]         
        except:
            ytd_low = 0
        for item_y in yearly_var1:
            if int(item_y[0]) > ytd_high:
                ytd_high = int(item_y[0])
            if int(item_y[0]) < ytd_low:
                ytd_low = int(item_y[0])	
       
        total_mtd = request.organization.get_metric(var1,mtd_range,aids,pids)
        total_ytd = request.organization.get_metric(var1,ytd_range,aids,pids)
        try:
            daily_avg = request.organization.get_metric(var1,ytd_range,aids,pids)/(ytd_range[1]-ytd_range[0]).days
        except:
            daily_avg = 'n/a'
        orders = request.organization.get_metric(METRIC_ORDERS,mtd_range,aids,pids)
        clicks = request.organization.get_metric(METRIC_CLICKS,mtd_range,aids,pids)
        amount = request.organization.get_metric(METRIC_AMOUNT,mtd_range,aids,pids)
        impressions = request.organization.get_metric(METRIC_IMPRESSIONS,mtd_range,aids,pids)
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
            
        #Currency Formating for Sales and Commission:
        if var1 == METRIC_AMOUNT or var1 == METRIC_COMMISSION_EARNED:
            yesterday = currency_formatter(yesterday,request.organization)
            month_high = currency_formatter(month_high,request.organization)
            month_low = currency_formatter(month_low,request.organization)
            ytd_high = currency_formatter(ytd_high,request.organization)
            ytd_low = currency_formatter(ytd_low,request.organization)
            total_mtd = currency_formatter(total_mtd,request.organization)
            total_ytd = currency_formatter(total_ytd,request.organization)
            daily_avg = currency_formatter(daily_avg,request.organization)
            
        score_board = {
            'number_of_var1' : number_of_var1,
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
            'cpc' : cpc
        }
        return score_board
    else:
        return {}