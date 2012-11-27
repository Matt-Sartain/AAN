from django.db.models.query import QuerySet
from atrinsic.util.format import *
from atrinsic.util.imports import *

def time_period(form):
    if form.cleaned_data.has_key('time_frame'):
        form.cleaned_data["time_frame"] = int(form.cleaned_data["time_frame"])
    form.cleaned_data["report_type"] = int(form.cleaned_data["report_type"])
    if form.cleaned_data.get("time_frame",None) == -2:
        ### specific month and year
        date_start = datetime.date(int(form.cleaned_data["specific_year"]),int(form.cleaned_data["specific_month"]),1)
        date_end = datetime.date((date_start + datetime.timedelta(0,3600*24*32)).year,(date_start + datetime.timedelta(0,3600*24*32)).month,1) - datetime.timedelta(0,3600*1)
    elif form.cleaned_data.get("time_frame",None) == -1:
        ### specific start_date and end_date
        date_start = form.cleaned_data["start_date"]
        date_end = form.cleaned_data["end_date"]
    elif form.cleaned_data.has_key('start_date') & form.cleaned_data.has_key('end_date'):
        date_start = form.cleaned_data["start_date"]
        date_end = form.cleaned_data["end_date"]
    else:
        date_start,date_end = compute_date_range(int(form.cleaned_data["time_frame"]))
    	yesterday_range = compute_date_range(REPORTTIMEFRAME_YESTERDAY)
    
    return (date_start,date_end)

def datelist(start_date,end_date,group_date_by):
    group_date_by = int(group_date_by)
    if group_date_by == REPORTGROUPBY_DAY:
        td= datetime.timedelta(0,3600*24,0)
    elif group_date_by == REPORTGROUPBY_WEEK:
        td= datetime.timedelta(0,3600*24*7,0)
    elif group_date_by == REPORTGROUPBY_MONTH:
        td = datetime.timedelta(0,3600*24*4.33*7,0)
    elif group_date_by == REPORTGROUPBY_QUARTER:
        td = datetime.timedelta(0,3600*24*365/4,0)

    results = []
    day = start_date
    while day <= end_date:
        results.append((day.strftime("%Y/%m/%d"),(day-td,day)))
        day += td

    return results
        

class Report(object):
    def __init__(self,start_date,end_date,organization,group_by=0,spec=[],publisher_set='',advertiser_set='',post_process=None):
        # spec takes a list of tuples, each defining the column.
        # Tuple will be (Display Name,field,formatter,aggregator)
        #  formatter is a function prototype that takes an input and returns a string
        #  aggregator is for generating the footer row
        
        from atrinsic.base.models import Organization

        self.group_iterator = "report_date,"
        self.start_date = start_date
        self.end_date = end_date
        self.table_cache = {}
        self.raw_data = []
        self.results = []
        self.organization = organization
        self.publisher_set = ''
        self.advertiser_set = ''
        self.iterator_header = ""
        self.post_process = post_process
        self.currency = None
        self.exchange_rate = None
        self.cache = {}
        self.data = None
        self.data_set = None
        self.report_query = None
        if int(group_by) == 0:
            self.group_by = "report_date"
        elif int(group_by) == 1:
            self.group_by = "WEEKOFYEAR(report_date)"
        elif int(group_by) == 2:
            self.group_by = "MONTH(report_date)"
        elif int(group_by) == 3:
            self.group_by = "QUARTER(report_date)"
        elif int(group_by) == 4:
            self.group_by = "website_url"
            self.group_iterator = "website_url,"
        
        if isinstance(self.organization,Organization):
            if self.organization.is_publisher():
                self.org_type = "publisher"
                self.organization_id = "and publisher_id = %d" % self.organization.id
            else:
                self.org_type = "advertiser"
                self.organization_id = "and advertiser_id = %d" % self.organization.id
        else:
            self.org_type = self.organization
            self.organization_id = ""
        
        self.spec = specs[self.org_type][spec]
        
        if self.group_by == "website_url":
            if self.spec[0][0] != 'Website' and self.spec[0][0] == "Date":
                self.spec.pop(0)
                self.spec.insert(0,('Website','website_url','null_formatter',null_aggregator))
        
        if publisher_set != '':
            if isinstance(publisher_set,type([])):
                id_set = ''
                for id in publisher_set:
                    if isinstance(id,unicode):
                        id_set+="%s," % id[2:]
                    else:
                        id_set+="%s," % id
                if id_set != '':
                    self.publisher_set = "and publisher_id in (%s)" % id_set[:-1]
            else:
                self.publisher_set = "and publisher_id = %s" % publisher_set[2:]
        if advertiser_set != '':
            if isinstance(advertiser_set,type([])):
                id_set = ''
                for id in advertiser_set:
                    if isinstance(id,unicode):
                        id_set+="%s," % id[2:]
                    else:
                        id_set+="%s," % id
                if id_set != '':
                    self.advertiser_set = "and advertiser_id in (%s)" % id_set[:-1]
            elif isinstance(advertiser_set,QuerySet):
                id_set = ''
                for adv in advertiser_set:
                    id_set+="%s," % adv.id
                if id_set != '':
                    self.advertiser_set = "and advertiser_id in (%s)" % id_set[:-1]
            else:
                self.advertiser_set = "and advertiser_id = %s" % advertiser_set[2:]
                
        self.GetBaseQuerySet()
    def GetBaseQuerySet(self):
        return []
        
    def RenderHeader(self):
        result = []
        for col in self.spec:
            result.append((col[0],col[1]))

        return result

    def RenderContents(self,as_rows = True):
        from django.db import connection, transaction
        from django.utils.encoding import smart_str
        cursor = connection.cursor()
        cursor.execute(self.report_query)

        query_set = today_var1 = cursor.fetchall()

        self.results = query_set
        formatted_row = []
        formatted_set = []
        row_count = 0
        
        for row in query_set:
            row_count += 1
            for_index = 0
            for col in row:                
                try:
                    formatter = self.spec[for_index][2]
                    if as_rows:
                        formatted_row.append(smart_str(getattr(self, formatter)(col,self.organization)))
                    else:
                        formatted_set.append(smart_str(getattr(self, formatter)(col,self.organization)))
                    for_index += 1
                except:
                    pass
            if as_rows:
                formatted_set.append(formatted_row)
                formatted_row = []
        if as_rows:
            return formatted_set
        else:
            return formatted_set,row_count

    def RenderFooter(self):
        i = 1
        result = [("Grand Total","Grand Total")]
        for display,field,formatter,aggregator in self.spec[1:]:
            try:
                if field == 'clicks':
                    click_index = i
                if field == 'leads':
                    lead_index = i
                if field == 'orders':
                    order_index = i
                if aggregator == average_aggregator:
                    if field == 'conversion_click_to_lead':
                        agg=float(result[lead_index][0])/float(result[click_index][0])*100
                        result.append((agg,getattr(self,formatter)(agg,self.organization)))
                    elif field == 'conversion_click_to_order':
                        agg=float(result[order_index][0])/float(result[click_index][0])*100
                        result.append((agg,getattr(self,formatter)(agg,self.organization)))
                    else:
                        agg = aggregator([x[i] for x in self.results])
                        result.append((agg,getattr(self,formatter)(agg,self.organization)))
                else:
                    agg = aggregator([x[i] for x in self.results])
                    result.append((agg,getattr(self,formatter)(agg,self.organization)))
            except:
                result.append("-")
            i += 1
        return result
        
    def currency_formatter(self,input,organization):
        from atrinsic.base.models import Currency,Organization
        if organization != None and isinstance(organization,Organization):
            currency_obj = Currency(order = 1, name= self.currency)
            if (self.currency == None) | (self.exchange_rate == None):
                self.currency = organization.organizationpaymentinfo_set.all()[0].currency.name
                self.currency_obj = Currency(order = 1, name = self.currency)
                self.exchange_rate = self.currency_obj.get_exchange_rate(self.currency)
            return currency_obj.convert_display_v2(input,float(self.exchange_rate),self.currency)
        else:
            currency_obj = Currency(order = 1, name= "USD")
            if self.currency == None:
                self.currency = 'USD'
            if self.exchange_rate == None:
                self.exchange_rate = currency_obj.get_exchange_rate(self.currency)
            return currency_obj.convert_display_v2(input,float(self.exchange_rate),self.currency)
        
    def null_formatter(self,input,organization):
        from django.utils.encoding import smart_str
        return smart_str(input)
        
    def percent_formatter(self,input,organization):
        return "%0.2f%%" % (input)
    
    def whole_formatter(self,input,organization):
        return FormatWithCommas("%d",int(round(input)))
    
    def link_formatter(self,input,organization):
        return u"<a href=''>%s</a>" % input
        
    def date_formatter(self,input,organization):
        try:
            return input.strftime("%m/%d/%Y")
        except:
            return null_formatter(input,organization)
        
def null_aggregator(items):
    return "-"

def sum_aggregator(items):
    return sum(items)

def max_aggregator(items):
    if len(items) == 0: return 0
    return max(items)

def average_aggregator(items):
    if len(items) == 0:
        return 0

    return float(sum(items))/len(items)

def ignore_aggregator(items):
    return "-"


def currency_formatter(input,organization):
    if organization != None:
        for payment_info in organization.organizationpaymentinfo_set.all():
            return payment_info.currency.convert_display(input)
    else:
        currency_obj = Currency(order = 1, name= "USD")
        return currency_obj.convert_display(input)
        
def null_formatter(input,organization):
    return str(input)

def percent_formatter(input,organization):
    return "%0.2f%%" % (input*100)

def whole_formatter(input,organization):
    return int(round(input))

def link_formatter(input,organization):
    return u"<a href=''>%s</a>" % input
    
class DateReport(Report):
    def __init__(self,*args,**kwargs):
        super(DateReport,self).__init__(*args,**kwargs)

    def GetBaseQuerySet(self):
        if self.org_type == 'advertiser':
            self.report_query = "SELECT min(report_date),IFNULL(count(distinct publisher_id),0) as publishers,IFNULL(sum(impressions),0) as impressions,IFNULL(sum(clicks),0) as clicks,IFNULL(sum(leads),0) as leads,IFNULL(sum(orders),0) as orders,IFNULL(sum(amount),0) as amounts,IFNULL((sum(leads) / sum(clicks) * 100),0) as lead_conversions,IFNULL((sum(orders) / sum(clicks) * 100),0) as order_conversions,IFNULL(sum(cast(publisher_commission as decimal(10,2))),0) as publisher_commissions,IFNULL(sum(cast(network_fee as decimal(10,2))),0) as network_fees,IFNULL(sum(cast(publisher_commission as decimal(10,2))) + sum(cast(network_fee as decimal(10,2))), 0) as total_fees,IFNULL((sum(amount) / sum(orders)),0) as avg_order_size,IFNULL((IFNULL((sum(publisher_commission) + sum(network_fee)),0) / sum(impressions)),0.00) as cpm,IFNULL((IFNULL((sum(publisher_commission) + sum(network_fee)),0) / sum(clicks)),0.00) as cpc,IFNULL((sum(publisher_commission) / sum(clicks)),0) as epc FROM base_report_adv_pub a WHERE report_date BETWEEN '%s' and '%s' %s %s GROUP BY %s order by report_date ASC" % (self.start_date,self.end_date,self.organization_id,self.publisher_set,self.group_by)
        else:
            self.report_query = "SELECT %sIFNULL(count(distinct advertiser_id),0) as advertisers,IFNULL(sum(impressions),0) as impressions,IFNULL(sum(clicks),0) as clicks,IFNULL(sum(leads),0) as leads,IFNULL(sum(orders),0) as orders,IFNULL(sum(amount),0) as amounts,IFNULL((sum(leads) / sum(clicks) * 100),0) as lead_conversions,IFNULL((sum(orders) / sum(clicks) * 100),0) as order_conversions,sum(publisher_commission),IFNULL((sum(amount) / sum(orders)),0) as avg_order_size,IFNULL((IFNULL((sum(publisher_commission) + sum(network_fee)),0) / sum(impressions)),0.00) as cpm,IFNULL((IFNULL((sum(publisher_commission) + sum(network_fee)),0) / sum(clicks)),0.00) as cpc,IFNULL((sum(publisher_commission) / sum(clicks)),0) as epc FROM base_report_adv_pub a WHERE report_date BETWEEN '%s' and '%s'  %s %s GROUP BY %s order by report_date ASC" % (self.group_iterator,self.start_date,self.end_date,self.organization_id,self.advertiser_set,self.group_by)
        return self.report_query

class OrgDateReport(Report):
    def __init__(self,*args,**kwargs):
        super(OrgDateReport,self).__init__(*args,**kwargs)
        self.current_publisher = None
                
    def GetBaseQuerySet(self):
        if self.org_type == 'advertiser':
            self.report_query = "SELECT publisher_id,publisher_name,IFNULL(sum(impressions),0) as impressions,IFNULL(sum(clicks),0) as clicks,IFNULL(sum(leads),0) as leads,IFNULL(sum(orders),0) as orders,IFNULL(sum(amount),0) as amounts,IFNULL((sum(leads) / sum(clicks) * 100),0) as lead_conversions,IFNULL((sum(orders) / sum(clicks) * 100),0) as order_conversions,IFNULL(sum(cast(publisher_commission as decimal(10,2))),0) as publisher_commissions,IFNULL(sum(cast(network_fee as decimal(10,2))),0) as network_fees,IFNULL(sum(cast(publisher_commission as decimal(10,2))) + sum(cast(network_fee as decimal(10,2))), 0) as total_fees,IFNULL((sum(amount) / sum(orders)),0) as avg_order_size,IFNULL((IFNULL((sum(publisher_commission) + sum(network_fee)),0) / sum(impressions)),0.00) as cpm,IFNULL((IFNULL((sum(publisher_commission) + sum(network_fee)),0) / sum(clicks)),0.00) as cpc,IFNULL((sum(publisher_commission) / sum(clicks)),0) as epc FROM base_report_adv_pub a WHERE report_date BETWEEN '%s' and '%s'  %s %s GROUP BY publisher_id,publisher_name order by report_date ASC" % (self.start_date,self.end_date,self.organization_id,self.publisher_set)
        else:
            if self.group_iterator == "report_date,":
                self.group_iterator = ""
            if self.group_by == "report_date":
                self.group_by = ""
            elif self.group_by == "website_url":
                self.group_by = "website_url,"
                if self.spec[0][0] != 'Website':
                    self.spec.insert(0,('Website','website_url','null_formatter',null_aggregator))
            elif self.group_by[-1:] != ",":
                self.group_by = self.group_by + ","
            self.report_query = "SELECT %sadvertiser_id,advertiser_name,IFNULL(sum(impressions),0) as impressions,IFNULL(sum(clicks),0) as clicks,IFNULL(sum(leads),0) as leads,IFNULL(sum(orders),0) as orders,IFNULL(sum(amount),0) as amounts,IFNULL((sum(leads) / sum(clicks) * 100),0) as lead_conversions,IFNULL((sum(orders) / sum(clicks) * 100),0) as order_conversions,IFNULL(sum(publisher_commission),0) as publisher_commissions,IFNULL((sum(amount) / sum(orders)),0) as avg_order_size,IFNULL((IFNULL((sum(publisher_commission) + sum(network_fee)),0) / sum(impressions)),0.00) as cpm,IFNULL((IFNULL((sum(publisher_commission) + sum(network_fee)),0) / sum(clicks)),0.00) as cpc,IFNULL((sum(publisher_commission) / sum(clicks)),0) as epc FROM base_report_adv_pub a WHERE report_date BETWEEN '%s' and '%s'  %s %s GROUP BY %sadvertiser_id,advertiser_name order by advertiser_name ASC" % (self.group_iterator,self.start_date,self.end_date,self.organization_id,self.advertiser_set,self.group_by)
        return self.report_query    
class RevenueReport(Report):
    def __init__(self,*args,**kwargs):
        super(RevenueReport,self).__init__(*args,**kwargs)
        
    def GetBaseQuerySet(self):
        if self.org_type == 'advertiser':
            self.report_query = "SELECT min(report_date),IFNULL(count(distinct publisher_id),0) as publishers,IFNULL(sum(orders),0) as orders,IFNULL(sum(amount),0) as amounts,IFNULL(sum(cast(publisher_commission as decimal(10,2))),0) as publisher_commissions,IFNULL(sum(cast(network_fee as decimal(10,2))),0) as network_fees,IFNULL(sum(cast(publisher_commission as decimal(10,2))) + sum(cast(network_fee as decimal(10,2))), 0) as total_fees,IFNULL((sum(amount) / sum(orders)),0) as avg_order_size,IFNULL((sum(publisher_commission) + sum(network_fee)/sum(orders)),0) as avg_order_cost, IFNULL(((sum(publisher_commission) + sum(network_fee))/sum(leads)),0) as avg_lead_cost, IFNULL((sum(publisher_commission) / (sum(publisher_commission) + sum(network_fee))),0)*100 as commission_percent,IFNULL((sum(network_fee) / (sum(publisher_commission) + sum(network_fee))),0)*100 as transaction_percent  FROM base_report_adv_pub a WHERE report_date BETWEEN '%s' and '%s' %s %s GROUP BY %s order by report_date ASC" % (self.start_date,self.end_date,self.organization_id,self.publisher_set,self.group_by)
        else:
            self.report_query = "SELECT %sIFNULL(count(distinct advertiser_id),0) as advertisers,IFNULL(sum(orders),0) as orders,IFNULL(sum(amount),0) as amounts,IFNULL(sum(publisher_commission),0) as publisher_commissions,IFNULL((sum(amount) / sum(orders)),0) as avg_order_size,IFNULL((sum(publisher_commission) + sum(network_fee)/sum(orders)),0) as avg_order_cost, IFNULL(((sum(publisher_commission) + sum(network_fee))/sum(leads)),0) as avg_lead_cost FROM base_report_adv_pub a WHERE report_date BETWEEN '%s' and '%s'  %s %s GROUP BY %s order by report_date ASC" % (self.group_iterator,self.start_date,self.end_date,self.organization_id,self.advertiser_set,self.group_by)
        return self.report_query
        
class OrgRevenueReport(Report):
    def __init__(self,*args,**kwargs):
        super(OrgRevenueReport,self).__init__(*args,**kwargs)
        
    def GetBaseQuerySet(self):
        if self.org_type == 'advertiser':
            self.report_query = "SELECT publisher_id, publisher_name, IFNULL(sum(orders),0) as orders,IFNULL(sum(amount),0) as amounts,IFNULL(sum(cast(publisher_commission as decimal(10,2))),0) as publisher_commissions,IFNULL(sum(cast(network_fee as decimal(10,2))),0) as network_fees,IFNULL(sum(cast(publisher_commission as decimal(10,2))) + sum(cast(network_fee as decimal(10,2))), 0) as total_fees,IFNULL((sum(amount) / sum(orders)),0) as avg_order_size,IFNULL((sum(publisher_commission) + sum(network_fee)/sum(orders)),0) as avg_order_cost, IFNULL(((sum(publisher_commission) + sum(network_fee))/sum(leads)),0) as avg_lead_cost, IFNULL((sum(publisher_commission) / (sum(publisher_commission) + sum(network_fee))),0)*100 as commission_percent,IFNULL((sum(network_fee) / (sum(publisher_commission) + sum(network_fee))),0)*100 as transaction_percent  FROM base_report_adv_pub a WHERE report_date BETWEEN '%s' and '%s' %s %s GROUP BY publisher_id, publisher_name order by report_date ASC" % (self.start_date,self.end_date,self.organization_id,self.publisher_set)
        else:
            if self.group_iterator == "report_date,":
                self.group_iterator = ""
            if self.group_by == "report_date":
                self.group_by = ""
            elif self.group_by == "website_url":
                self.group_by = "website_url,"
                if self.spec[0][0] != 'Website':
                    self.spec.insert(0,('Website','website_url','null_formatter',null_aggregator))
            elif self.group_by[-1:] != ",":
                self.group_by = self.group_by + ","
            self.report_query = "SELECT %sadvertiser_id, advertiser_name, IFNULL(sum(orders),0) as orders,IFNULL(sum(amount),0) as amounts,IFNULL(sum(publisher_commission),0) as publisher_commissions,IFNULL((sum(amount) / sum(orders)),0) as avg_order_size,IFNULL((sum(publisher_commission) + sum(network_fee)/sum(orders)),0) as avg_order_cost, IFNULL(((sum(publisher_commission) + sum(network_fee))/sum(leads)),0) as avg_lead_cost  FROM base_report_adv_pub a WHERE report_date BETWEEN '%s' and '%s' %s %s GROUP BY %sadvertiser_id, advertiser_name order by report_date ASC" % (self.group_iterator,self.start_date,self.end_date,self.organization_id,self.advertiser_set,self.group_by)
        return self.report_query
    
class CreativeReport(Report):
    def __init__(self,*args,**kwargs):
        super(CreativeReport,self).__init__(*args,**kwargs)
        
    def GetBaseQuerySet(self):
        if self.org_type == 'advertiser':
            self.report_query = "SELECT creative_id,creative_size,promotion_type,count(distinct publisher_id) as publishers,IFNULL(sum(impressions),0) as impressions,IFNULL(sum(clicks),0) as clicks,IFNULL(sum(leads),0) as leads,IFNULL(sum(orders),0) as orders,IFNULL(sum(amount),0) as amounts,IFNULL((sum(leads) / sum(clicks) * 100),0) as lead_conversions,IFNULL((sum(orders) / sum(clicks) * 100),0) as order_conversions,IFNULL(sum(cast(publisher_commission as decimal(10,2))),0) as publisher_commissions,IFNULL(sum(cast(network_fee as decimal(10,2))),0) as network_fees,IFNULL(sum(cast(publisher_commission as decimal(10,2))) + sum(cast(network_fee as decimal(10,2))), 0) as total_fees,IFNULL((sum(amount) / sum(orders)),0) as avg_order_size FROM base_report_link a WHERE report_date BETWEEN '%s' and '%s' %s %s GROUP BY creative_id,creative_size,promotion_type order by creative_id ASC" % (self.start_date,self.end_date,self.organization_id,self.publisher_set)
        else:
            self.report_query = "SELECT creative_id,creative_size,count(distinct advertiser_id) as advertisers,IFNULL(sum(impressions),0) as impressions,IFNULL(sum(clicks),0) as clicks,IFNULL(sum(leads),0) as leads,IFNULL(sum(orders),0) as orders,IFNULL(sum(amount),0) as amounts,IFNULL((sum(leads) / sum(clicks) * 100),0) as lead_conversions,IFNULL((sum(orders) / sum(clicks) * 100),0) as order_conversions,IFNULL(sum(publisher_commission),0) as publisher_commissions,IFNULL((sum(amount) / sum(orders)),0) as avg_order_size FROM base_report_link a WHERE report_date BETWEEN '%s' and '%s' %s %s GROUP BY creative_id,creative_size,promotion_type order by creative_id ASC" % (self.start_date,self.end_date,self.organization_id,self.advertiser_set)
        return self.report_query
        
class PromoReport(Report):
    def __init__(self,*args,**kwargs):
        super(PromoReport,self).__init__(*args,**kwargs)
        
    def GetBaseQuerySet(self):          
        self.report_query = "SELECT promotion_type,creative_size,count(distinct publisher_id) as publishers,IFNULL(sum(impressions),0) as impressions,IFNULL(sum(clicks),0) as clicks,IFNULL(sum(leads),0) as leads,IFNULL(sum(amount),0) as amounts,IFNULL(sum(orders),0) as orders,IFNULL((sum(leads) / sum(clicks) * 100),0) as lead_conversions,IFNULL((sum(orders) / sum(clicks) * 100),0) as order_conversions,IFNULL(sum(cast(publisher_commission as decimal(10,2))),0) as publisher_commissions,IFNULL(sum(cast(network_fee as decimal(10,2))),0) as network_fees,IFNULL(sum(cast(publisher_commission as decimal(10,2))) + sum(cast(network_fee as decimal(10,2))), 0) as total_fees,IFNULL((sum(amount) / sum(orders)),0) as avg_order_size FROM base_report_link a WHERE report_date BETWEEN '%s' and '%s' %s %s GROUP BY promotion_type,creative_size order by report_date ASC" % (self.start_date,self.end_date,self.organization_id,self.publisher_set)
        return self.report_query

class ProductReport(Report):
    def __init__(self,*args,**kwargs):
        super(ProductReport,self).__init__(*args,**kwargs)
    def GetBaseQuerySet(self):
        self.report_query = "SELECT report_date,product_sku,product_name,IFNULL(sum(orders),0) as orders,product_quantity,sum(product_quantity),amount,sum(amount) FROM base_report_orderdetail a WHERE report_date BETWEEN '%s' and '%s' %s %s GROUP BY %s,product_sku,product_name order by report_date ASC" % (self.start_date,self.end_date,self.organization_id,self.publisher_set,self.group_by)
        return self.report_query

class OrderReport(Report):
    def __init__(self,*args,**kwargs):
        super(OrderReport,self).__init__(*args,**kwargs)
        
    def GetBaseQuerySet(self):
        if self.org_type == 'advertiser':
            self.report_query = "SELECT report_date,publisher_id, publisher_name, order_id, product_sku,product_name,sum(product_quantity),sum(product_price),IFNULL(sum(cast(publisher_commission as decimal(10,2))),0) as publisher_commissions,IFNULL(sum(cast(network_fee as decimal(10,2))),0) as network_fees,IFNULL(sum(cast(publisher_commission as decimal(10,2))) + sum(cast(network_fee as decimal(10,2))), 0) as total_fees, IFNULL(sum(cast(amount as decimal(10,2))),0) as amount FROM base_report_orderdetail a WHERE report_date BETWEEN '%s' and '%s' %s %s GROUP BY %s,order_id,publisher_id, publisher_name,product_sku,product_name order by report_date ASC" % (self.start_date,self.end_date,self.organization_id,self.publisher_set,self.group_by)
        else:
            self.report_query = "SELECT report_date,advertiser_id, advertiser_name, order_id, product_sku,product_name,sum(product_quantity),sum(product_price),sum(publisher_commission), IFNULL(sum(cast(amount as decimal(10,2))),0) as amount FROM base_report_orderdetail a WHERE report_date BETWEEN '%s' and '%s' %s %s GROUP BY %s,order_id,advertiser_id, advertiser_name,product_sku,product_name order by report_date ASC" % (self.start_date,self.end_date,self.organization_id,self.advertiser_set,self.group_by)
        return self.report_query

class AccountingReport(Report):
    def __init__(self,*args,**kwargs):
        super(AccountingReport,self).__init__(*args,**kwargs)

    def GetBaseQuerySet(self):
        if self.org_type == 'advertiser':
            self.report_query = "SELECT publisher_id,publisher_name,IFNULL(sum(leads),0) as leads,IFNULL(sum(orders),0) as orders,IFNULL(sum(amount),0) as amounts,IFNULL((sum(amount) / sum(orders)),0) as avg_order_size, IFNULL(sum(cast(publisher_commission as decimal(10,2))),0) as publisher_commissions,IFNULL(sum(cast(network_fee as decimal(10,2))),0) as network_fees,IFNULL(sum(cast(publisher_commission as decimal(10,2))) + sum(cast(network_fee as decimal(10,2))), 0) as total_fees FROM base_report_adv_pub a WHERE report_date BETWEEN '%s' and '%s' %s %s GROUP BY publisher_id,publisher_name order by report_date ASC" % (self.start_date,self.end_date,self.organization_id,self.publisher_set)
        else:
            self.report_query = "SELECT advertiser_id, advertiser_name,IFNULL(sum(leads),0) as leads,IFNULL(sum(orders),0) as orders,IFNULL(sum(amount),0) as amounts,IFNULL((sum(amount) / sum(orders)),0) as avg_order_size, sum(publisher_commission) FROM base_report_adv_pub a WHERE report_date BETWEEN '%s' and '%s' %s %s GROUP BY publisher_id,publisher_name order by report_date ASC" % (self.start_date,self.end_date,self.organization_id,self.advertiser_set)
        return self.report_query

class DataTransfer_OrderReport(Report):
    def __init__(self,*args,**kwargs):
        super(DataTransfer_OrderReport,self).__init__(*args,**kwargs)
        
    def GetBaseQuerySet(self):
        if self.org_type == 'advertiser':
            self.report_query = "SELECT report_date,publisher_id, publisher_name, order_id, IFNULL(sum(cast(amount as decimal(10,2))),0) as amount, IFNULL(sum(cast(publisher_commission as decimal(10,2))),0) as publisher_payout, sub_id FROM base_report_orderdetail a WHERE report_date BETWEEN '%s' and '%s' %s %s GROUP BY %s,order_id,publisher_id, publisher_name order by report_date ASC" % (self.start_date,self.end_date,self.organization_id,self.publisher_set,self.group_by)
        else:
            self.report_query = "SELECT report_date,advertiser_id, advertiser_name, order_id, IFNULL(sum(cast(amount as decimal(10,2))),0) as amount, IFNULL(sum(cast(publisher_commission as decimal(10,2))),0) as publisher_payout, sub_id FROM base_report_orderdetail a WHERE report_date BETWEEN '%s' and '%s' %s %s GROUP BY %s,order_id,advertiser_id, advertiser_name order by report_date ASC" % (self.start_date,self.end_date,self.organization_id,self.advertiser_set,self.group_by)
                
        return self.report_query        
        
specs = {}

specs['publisher'] = {}

specs['advertiser'] = {}

specs['advertiser'][REPORTTYPE_SALES] = [
    ('Date','report_date','date_formatter',max_aggregator),
    ('Publishers','publisher_count','whole_formatter',max_aggregator),
    ('Impressions','impressions','whole_formatter',sum_aggregator),
    ('Clicks','clicks','whole_formatter',sum_aggregator),
    ('Lead','leads','whole_formatter',sum_aggregator),
    ('Order','orders','whole_formatter',sum_aggregator),
    ('Amount','amount','currency_formatter',sum_aggregator),
    ('C/L','conversion_click_to_lead','percent_formatter',average_aggregator),
    ('C/O','conversion_click_to_order','percent_formatter',average_aggregator),
    ('Payout','publisher_payout','currency_formatter',sum_aggregator),
    ('Trans Fees','transaction_fee','currency_formatter',sum_aggregator),
    ('Total Fees','total_fee','currency_formatter',sum_aggregator),
    ('Avg Order Size','average_order_size','currency_formatter',average_aggregator),
    ('CPM','advertiser_cpm','currency_formatter',average_aggregator),
    ('CPC','advertiser_cpc','currency_formatter',average_aggregator),
    ('EPC','advertiser_epc','currency_formatter',average_aggregator)]

specs['advertiser'][REPORTTYPE_SALES_BY_PUBLISHER] = [
    ('Publisher ID','publisher_id','null_formatter',null_aggregator),
    ('Publisher Name','publisher_name','null_formatter',null_aggregator),
    ('Impressions','impressions','whole_formatter',sum_aggregator),
    ('Clicks','clicks','whole_formatter',sum_aggregator),
    ('Lead','leads','whole_formatter',sum_aggregator),
    ('Order','orders','whole_formatter',sum_aggregator),
    ('Amount','amount','currency_formatter',sum_aggregator),
    ('C/L','conversion_click_to_lead','percent_formatter',average_aggregator),
    ('C/O','conversion_click_to_order','percent_formatter',average_aggregator),
    ('Publisher Payout','publisher_payout','currency_formatter',sum_aggregator),
    ('Transaction Fee','transaction_fee','currency_formatter',sum_aggregator),
    ('Total Fees','total_fee','currency_formatter',sum_aggregator),
    ('Average Size','average_order_size','currency_formatter',average_aggregator),
    ('CPM','advertiser_cpm','currency_formatter',average_aggregator),
    ('CPC','advertiser_cpc','currency_formatter',average_aggregator),
    ('EPC','advertiser_epc','currency_formatter',average_aggregator)]

specs['advertiser'][REPORTTYPE_REVENUE] = [
    ('Date','report_date','date_formatter',max_aggregator),
    ('Publishers','publisher_count','whole_formatter',max_aggregator),
    ('Order','orders','whole_formatter',sum_aggregator),
    ('Amount','amount','currency_formatter',sum_aggregator),
    ('Publisher Payout','publisher_payout','currency_formatter',sum_aggregator),
    ('Transaction Fee','transaction_fee','currency_formatter',sum_aggregator),
    ('Total Fees','total_fee','currency_formatter',sum_aggregator),
    ('Avg Order Size','average_order_size','currency_formatter',average_aggregator),
    ('Average Cost per Order','average_cost_per_order','currency_formatter',average_aggregator),
    ('Average Cost per Lead','average_cost_per_lead','currency_formatter',average_aggregator),
    ('%% of Publisher Fee','percent_of_publisher_fee','percent_formatter',null_aggregator),
    ('%% of Transaction Fee','percent_of_transaction_fee','percent_formatter',null_aggregator),
    #('% of Total Fee','percent_of_total_fee','null_formatter',null_aggregator)
    ]


specs['advertiser'][REPORTTYPE_REVENUE_BY_PUBLISHER] = [
    ('Publisher ID','publisher_id','null_formatter',null_aggregator),
    ('Publisher Name','publisher_name','null_formatter',null_aggregator),
    ('Order','orders','whole_formatter',sum_aggregator),
    ('Amount','amount','currency_formatter',sum_aggregator),
    ('Publisher Payout','publisher_payout','currency_formatter',sum_aggregator),
    ('Transaction Fee','transaction_fee','currency_formatter',sum_aggregator),
    ('Total Fees','total_fee','currency_formatter',sum_aggregator),
    ('Avg Order Size','average_order_size','currency_formatter',average_aggregator),
    ('Average Cost per Order','average_cost_per_order','currency_formatter',average_aggregator),
    ('Average Cost per Lead','average_cost_per_lead','currency_formatter',average_aggregator),
    ('%% of Publisher Fee','percent_of_publisher_fee','percent_formatter',null_aggregator),
    ('%% of Transaction Fee','percent_of_transaction_fee','percent_formatter',null_aggregator),
    #('% of Total Fee','percent_of_total_fee','null_formatter',null_aggregator)
    ]

specs['advertiser'][REPORTTYPE_CREATIVE] = [
    ('ID','creative_id','null_formatter',null_aggregator),
    ('Size','creative_size','null_formatter',null_aggregator),
    ('Type','creative_type','null_formatter',null_aggregator),
    ('Publishers','publisher_count','whole_formatter',max_aggregator),
    ('Impressions','impressions','whole_formatter',sum_aggregator),
    ('Clicks','clicks','whole_formatter',sum_aggregator),
    ('Lead','leads','whole_formatter',sum_aggregator),
    ('Order','orders','whole_formatter',sum_aggregator),
    ('Amount','amount','currency_formatter',sum_aggregator),
    ('C/L','conversion_click_to_lead','percent_formatter',average_aggregator),
    ('C/O','conversion_click_to_order','percent_formatter',average_aggregator),
    ('Publisher Payout','publisher_payout','currency_formatter',sum_aggregator),
    ('Transaction Fee','transaction_fee','currency_formatter',sum_aggregator),
    ('Total Fees','total_fee','currency_formatter',sum_aggregator),
    ('Avg Order Size','average_order_size','currency_formatter',average_aggregator),]

specs['advertiser'][REPORTTYPE_CREATIVE_BY_PROMO] = [
    ('Promotion Type','creative_type','null_formatter',null_aggregator),    
    ('Creative Size','creative_size','null_formatter',null_aggregator),
    ('Publishers','publisher_count','whole_formatter',max_aggregator),
    ('Impressions','impressions','whole_formatter',sum_aggregator),
    ('Clicks','clicks','whole_formatter',sum_aggregator),
    ('Lead','leads','whole_formatter',sum_aggregator),
    ('Order','orders','whole_formatter',sum_aggregator),
    ('Amount','amount','currency_formatter',sum_aggregator),
    ('C/L','conversion_click_to_lead','percent_formatter',average_aggregator),
    ('C/O','conversion_click_to_order','percent_formatter',average_aggregator),
    ('Publisher Payout','publisher_payout','currency_formatter',sum_aggregator),
    ('Transaction Fee','transaction_fee','currency_formatter',sum_aggregator),
    ('Total Fees','total_fee','currency_formatter',sum_aggregator),
    ('Avg Order Size','average_order_size','currency_formatter',average_aggregator),]

specs['advertiser'][REPORTTYPE_ORDER_DETAIL] = [
    ('Date','report_date','date_formatter',max_aggregator),
    ('Publisher ID','order_publisher_id','null_formatter',null_aggregator),
    ('Publisher Name','order_publisher_name','null_formatter',null_aggregator),
    ('Order ID','order_id','null_formatter',null_aggregator),
    ('Product SKU','product_sku','null_formatter',null_aggregator),
    ('Product Name','product_name','null_formatter',null_aggregator),
    ('Product Quantity','product_quantity','null_formatter',sum_aggregator),
    ('Product Price','product_price','null_formatter',null_aggregator),
    ('Publisher Payout','publisher_payout','currency_formatter',sum_aggregator),
    ('Transaction Fee','transaction_fee','currency_formatter',sum_aggregator),
    ('Totel Fees','total_fee','currency_formatter',sum_aggregator),
    ('Amount','amount','currency_formatter',sum_aggregator)
    ]

specs['advertiser'][REPORTTYPE_PRODUCT_DETAIL] = [
    ('Order Date','report_date','date_formatter',max_aggregator),
    ('Product SKU','item','null_formatter',null_aggregator),    
    ('Product Name','name','null_formatter',null_aggregator),
    ('Orders','order_id','whole_formatter',max_aggregator),
    ('Total Quantity','quantity','whole_formatter',sum_aggregator),
    ('Average Quantity','quantity','whole_formatter',average_aggregator),
    ('Average Price','amount','currency_formatter',average_aggregator),
    ('Total Amount','amount','currency_formatter',sum_aggregator)]

specs['advertiser'][REPORTTYPE_ACCOUNTING] = [
    ('Publisher ID','order_publisher_id','null_formatter',null_aggregator),
    ('Publisher Name','publisher_name','null_formatter',null_aggregator),
    ('Lead','leads','whole_formatter',sum_aggregator),
    ('Order','orders','whole_formatter',sum_aggregator),
    ('Amount','amount','currency_formatter',sum_aggregator),
    ('Avg Order Size','average_order_size','currency_formatter',average_aggregator),
    ('Publisher Payout','publisher_payout','currency_formatter',sum_aggregator),
    ('Transaction Fee','transaction_fee','currency_formatter',sum_aggregator),
    ('Total Fees','total_fee','currency_formatter',sum_aggregator)]


specs['publisher'][REPORTTYPE_SALES] = [
    ('Date','report_date','date_formatter',max_aggregator),
    ('Advertisers','advertiser_count','whole_formatter',max_aggregator),
    ('Impressions','impressions','whole_formatter',sum_aggregator),
    ('Clicks','clicks','whole_formatter',sum_aggregator),
    ('Lead','leads','whole_formatter',sum_aggregator),
    ('Order','orders','whole_formatter',sum_aggregator),
    ('Amount','amount','currency_formatter',sum_aggregator),
    ('C/L','conversion_click_to_lead','percent_formatter',average_aggregator),
    ('C/O','conversion_click_to_order','percent_formatter',average_aggregator),
    ('Commission Earned','publisher_payout','currency_formatter',sum_aggregator),
    ('Avg Order Size','average_order_size','currency_formatter',average_aggregator),
    ('CPM','publisher_cpm','currency_formatter',average_aggregator),
    ('CPC','publisher_cpc','currency_formatter',average_aggregator),
    ('EPC','publisher_epc','currency_formatter',average_aggregator)]

specs['publisher'][REPORTTYPE_SALES_BY_ADVERTISER] = [
    ('Advertiser ID','advertiser_id','null_formatter',null_aggregator),
    ('Advertiser Name','advertiser_name','null_formatter',null_aggregator),
    ('Impressions','impressions','whole_formatter',sum_aggregator),
    ('Clicks','clicks','whole_formatter',sum_aggregator),
    ('Lead','leads','whole_formatter',sum_aggregator),
    ('Order','orders','whole_formatter',sum_aggregator),
    ('Amount','amount','currency_formatter',sum_aggregator),
    ('C/L','conversion_click_to_lead','percent_formatter',average_aggregator),
    ('C/O','conversion_click_to_order','percent_formatter',average_aggregator),
    ('Commission Earned','publisher_payout','currency_formatter',sum_aggregator),
    ('Avg Order Size','average_order_size','currency_formatter',average_aggregator),
    ('CPM','publisher_cpm','currency_formatter',average_aggregator),
    ('CPC','publisher_cpc','currency_formatter',average_aggregator),
    ('EPC','publisher_epc','currency_formatter',average_aggregator)]

specs['publisher'][REPORTTYPE_REVENUE] = [
    ('Date','report_date','date_formatter',max_aggregator),
    ('Advertisers','advertiser_count','whole_formatter',max_aggregator),
    ('Order','orders','whole_formatter',sum_aggregator),
    ('Amount','amount','currency_formatter',sum_aggregator),
    ('Commission Earned','publisher_payout','currency_formatter',sum_aggregator),
    ('Avg Order Size','average_order_size','currency_formatter',average_aggregator),
    ('Average Cost per Order','average_cost_per_order','currency_formatter',average_aggregator),
    ('Average Cost per Lead','average_cost_per_lead','currency_formatter',average_aggregator)]
specs['publisher'][REPORTTYPE_REVENUE_BY_ADVERTISER] = [
    ('Advertiser ID','advertiser_id','null_formatter',null_aggregator),
    ('Advertiser Name','advertiser_name','null_formatter',null_aggregator),
    ('Order','orders','whole_formatter',sum_aggregator),
    ('Amount','amount','currency_formatter',sum_aggregator),
    ('Commission Earned','publisher_payout','currency_formatter',sum_aggregator),
    ('Avg Order Size','average_order_size','currency_formatter',average_aggregator),
    ('Average Cost per Order','average_cost_per_order','currency_formatter',average_aggregator),
    ('Average Cost per Lead','average_cost_per_lead','currency_formatter',average_aggregator)]
specs['publisher'][REPORTTYPE_CREATIVE] = [
    ('ID','creative_id','null_formatter',null_aggregator),
    ('Size','creative_size','link_formatter',null_aggregator),
    ('Advertisers','advertiser_count','whole_formatter',max_aggregator),
    ('Impressions','impressions','whole_formatter',sum_aggregator),
    ('Clicks','clicks','whole_formatter',sum_aggregator),
    ('Lead','leads','whole_formatter',sum_aggregator),
    ('Order','orders','whole_formatter',sum_aggregator),
    ('Amount','amount','currency_formatter',sum_aggregator),
    ('C/L','conversion_click_to_lead','percent_formatter',average_aggregator),
    ('C/O','conversion_click_to_order','percent_formatter',average_aggregator),
    ('Commission Earned','publisher_payout','currency_formatter',sum_aggregator),
    ('Avg Order Size','average_order_size','currency_formatter',average_aggregator)]
    
specs['publisher'][REPORTTYPE_CREATIVE_BY_PROMO] = [
                ('Advertisers','advertiser_count','whole_formatter',max_aggregator),
                ('Impressions','impressions','whole_formatter',sum_aggregator),
                ('Clicks','clicks','whole_formatter',sum_aggregator),
                ('Lead','leads','whole_formatter',sum_aggregator),
                ('Order','orders','whole_formatter',sum_aggregator),
                ('Amount','amount','currency_formatter',sum_aggregator),
                ('C/L','conversion_click_to_lead','percent_formatter',average_aggregator),
                ('C/O','conversion_click_to_order','percent_formatter',average_aggregator),
                ('Commission Earned','publisher_payout','currency_formatter',sum_aggregator),
                ('Avg Order Size','average_order_size','currency_formatter',average_aggregator)]

specs['publisher'][REPORTTYPE_ORDER_DETAIL] = [
    ('Date','report_date','date_formatter',max_aggregator),
    ('Advertiser ID','order_advertiser_id','null_formatter',null_aggregator),
    ('Advertiser Name','order_advertiser_name','null_formatter',null_aggregator),
    ('Order ID','order_id','null_formatter',null_aggregator),
    ('Product SKU','','null_formatter',null_aggregator),
    ('Product Name','','null_formatter',null_aggregator),
    ('Product Quantity','','null_formatter',null_aggregator),
    ('Product Price','','null_formatter',null_aggregator),
    ('Commission Earned','publisher_payout','currency_formatter',sum_aggregator),
    ('Amount','amount','currency_formatter',sum_aggregator)]

specs['publisher'][REPORTTYPE_ACCOUNTING] = [
    ('Advertiser ID','advertiser_id','null_formatter',null_aggregator),
    ('Advertiser Name','advertiser_name','null_formatter',null_aggregator),
    ('Lead','leads','whole_formatter',sum_aggregator),
    ('Order','orders','whole_formatter',sum_aggregator),
    ('Amount','amount','currency_formatter',sum_aggregator),
    ('Avg Order Size','average_order_size','currency_formatter',average_aggregator),
    ('Commission Earned','publisher_payout','currency_formatter',sum_aggregator)]

specs['publisher'][REPORTTYPE_DATATRANSFER_ORDERREPORT] = [
    ('Order Date','report_date','date_formatter',max_aggregator),
    ('Advertiser ID','order_advertiser_id','null_formatter',null_aggregator),
    ('Advertiser Name','order_advertiser_name','null_formatter',null_aggregator),
    ('Order ID','order_id','null_formatter',null_aggregator),
    ('Amount','amount','null_formatter',null_aggregator),
    ('Publisher Fee','publisher_payout','null_formatter',null_aggregator),
    ('SubID','sub_id','null_formatter',null_aggregator)]    

# from an organization, return a Report object
def construct_dashboard_report(request,organization):
    if request.session.has_key("date_range") == False:
        date_range = REPORTTIMEFRAME_PAST30DAYS
    else:
        date_range = request.session["date_range"]
        
    date_start,date_end = compute_date_range(date_range)

    spec = []
    if organization.dashboard_variable1 == DASHBOARDMETRIC_IMPRESSIONS:
        spec.append(('impressions','impressions',whole_formatter,sum_aggregator))
    elif organization.dashboard_variable1 == DASHBOARDMETRIC_CLICKS:
        spec.append(('clicks','clicks',whole_formatter,sum_aggregator))
    elif organization.dashboard_variable1 == DASHBOARDMETRIC_LEADS:
        spec.append(('leads','leads',whole_formatter,sum_aggregator))
    elif organization.dashboard_variable1 == DASHBOARDMETRIC_ORDERS:
        spec.append(('orders','orders',whole_formatter,sum_aggregator))
    elif organization.dashboard_variable1 == DASHBOARDMETRIC_SALES:
        spec.append(('amount','amount',currency_formatter,sum_aggregator))
    elif organization.dashboard_variable1 == DASHBOARDMETRIC_COMMISSION_EARNED:
        spec.append(('commission_earned','publisher_payout',currency_formatter,sum_aggregator))
    else:
        spec.append(('impressions','impressions',whole_formatter,sum_aggregator))
        
    if organization.dashboard_variable2 == DASHBOARDMETRIC_IMPRESSIONS:
        spec.append(('impressions','impressions',whole_formatter,sum_aggregator))
    elif organization.dashboard_variable2 == DASHBOARDMETRIC_CLICKS:
        spec.append(('clicks','clicks',whole_formatter,sum_aggregator))
    elif organization.dashboard_variable2 == DASHBOARDMETRIC_LEADS:
        spec.append(('leads','leads',whole_formatter,sum_aggregator))
    elif organization.dashboard_variable2 == DASHBOARDMETRIC_ORDERS:
        spec.append(('orders','orders',whole_formatter,sum_aggregator))
    elif organization.dashboard_variable2 == DASHBOARDMETRIC_SALES:
        spec.append(('amount','amount',currency_formatter,sum_aggregator))
    elif organization.dashboard_variable2 == DASHBOARDMETRIC_COMMISSION_EARNED:
        spec.append(('commission_earned','publisher_payout',currency_formatter,sum_aggregator))
    else:
        spec.append(('clicks','clicks',whole_formatter,sum_aggregator))
        


    
    return DateReport(organization.dashboard_group_data_by,date_start,date_end,organization,spec=spec)

