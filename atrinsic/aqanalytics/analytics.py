__author__ = 'landry.jeanluc@gmail.com (Jean-Luc Landry)'

import gdata.analytics.client
import gdata.sample_util
from gdata.analytics.client import AccountFeedQuery
from elementtree.ElementTree import XML,tostring
from models import Users
from reports import *
import sys

class AqAnalytics(object):
    def __init__(self,user_name,password):
        self.SOURCE_APP_NAME = 'Atrinsic-Network'
        self.my_client = gdata.analytics.client.AnalyticsClient(source=self.SOURCE_APP_NAME)
        self.account_feed = ''
        self.data_feed = ''
        self.table_ids = None
        self.user_name = user_name
        self.password = password

    def authenticate(self):
        try:
            self.my_client.client_login(self.user_name, self.password,self.SOURCE_APP_NAME,'analytics')
        except gdata.client.BadAuthentication:
            raise Exception('Invalid user credentials given.')
        except gdata.client.Error:
            raise Exception('Invalid user credentials given.')
        return True
        
    def AccountFeedQuery(self,max_results='50'):
        # DataFeedQuery simplifies constructing API queries and uri encodes params.
        self.account_feed_query = AccountFeedQuery({'max-results': max_results})
        self.account_feed = self.my_client.GetDataFeed(self.account_feed_query)
        self.parsed_account_feed = XML(str(self.account_feed))
        return self.parsed_account_feed
        
    def GetSiteList(self,feed_query = None):
        if feed_query == None:
            feed_query = self.AccountFeedQuery()
        complete_feed = []
        feed_details = {}
        for elem in feed_query:
            if list(elem):
                for node in elem:
                    NS1='{http://schemas.google.com/analytics/2009}'
                    NS2='{http://www.w3.org/2005/Atom}'
                    if node.tag[len(NS1):] == "tableId":
                        feed_details['table_id']=node.text
                    elif node.tag[len(NS2):] == "title":
                        feed_details['site_url']=node.text
                if feed_details:
                    complete_feed.append(feed_details)
                feed_details = {}
            
        return complete_feed
    def DataFeedQuery(self,start_date,end_date,table_id,report_type,parse_as="flat",sort='',filters='',max_results='50',chart_type="table"):
        m_indx = report_type.index("m-")
        d_indx = report_type.index("d-")
        dimensions = report_type[d_indx+2:m_indx-1]
        for d in dimensions.split(","):
            d = "ga:" + d +","
        dim = d[:-1]
        metrics = report_type[m_indx+2:]
        for m in metrics.split(","):
            m = "ga:" + m +","
        metr = m[:-1]
        #try:            
        print "TEST3"
        if max_results == '':
            max_results = 50
        self.data_feed_query = gdata.analytics.client.DataFeedQuery({
            'ids': table_id,
            'start-date': start_date,
            'end-date': end_date,
            'dimensions':dim,
            'metrics':metr,
            'sort': sort,
            'filters': filters,
            'max-results': max_results})
        print self.data_feed_query
        self.data_feed = self.my_client.GetDataFeed(self.data_feed_query)
        self.parsed_data_feed = XML(str(self.data_feed))
        print self.parsed_data_feed
        if parse_as == "raw":
            return self.parsed_data_feed,len(self.parsed_data_feed.getiterator('{http://www.w3.org/2005/Atom}entry')),True
        else:
            return self.ParseDataFeedResults(self.parsed_data_feed,parse_as),len(self.parsed_data_feed.getiterator('{http://www.w3.org/2005/Atom}entry')),True
        """except:
            'body', 'headers', 'message', 'reason', 'status'
            error = sys.exc_info()[1]
            error_xml = XML(error.message[error.message.index("<"):])
            error_list = []
            for node in error_xml.getiterator("{http://schemas.google.com/g/2005}error"):
                for err in node.getchildren():
                    if err.tag == "{http://schemas.google.com/g/2005}internalReason":
                        error_list.append(err.text)
            return (False,False,error_list)"""
            
    def ParseDataFeedResults(self,data_feed_query,parse_as):
        NS = '{http://schemas.google.com/analytics/2009}'
        e_list = []
        headers = []
        self.parse_as = parse_as
        for elem in data_feed_query.getiterator('{http://www.w3.org/2005/Atom}entry'):
            if parse_as == "dict":
                e_dict = {}
            elif parse_as == "array" or parse_as == "flat":
                e_dict = []
            else:
                e_dict = ""
            for node in elem.getchildren():
                e_dict,headers = self.SuperAppend(node,e_dict,headers)
                
            if parse_as == "flat":
                for x in e_dict:
                    e_list.append(x)
            else:
                e_list.append(e_dict)
        return e_list,headers
        
    def SuperAppend(self,node,e_dict,headers):
        if node.attrib.has_key('value'):
            try:
                headers.index(node.attrib['name'][3:])
            except:
                headers.append(node.attrib['name'][3:])
            if self.parse_as == "dict":
                e_dict[node.attrib['name'][3:]] = node.attrib['value']
            elif self.parse_as == "array" or self.parse_as == "flat":
                e_dict.append(node.attrib['value'])
            else:
                e_dict = node.attrib['value']
        return e_dict,headers

def get_html(data,headers,row_count,chart_type):
    if chart_type == "table":
        return get_html_table(data,headers,row_count)
    elif chart_type[:5] == "chart":
        return get_flash_chart(data,headers,row_count,chart_type[6:])
    return ""

def get_html_table(table_content,headers,row_count):
    from datetime import datetime
    html = """	<table class="widget_table" border="0" cellspacing="0" cellpading="0">
                <thead>
                <tr>"""
    template_row="<tr>"
    for column in headers:
        html+="""<th ><div class="widget_table_headers">%s</div></th>""" % column
        template_row += "<td>%s</td>"
    template_row+="</tr>"
    html+="""</tr>
    </thead>
    <tbody>"""
    html += template_row * row_count
    html += """</tbody>"""
    html = html % tuple(table_content)
    html+="""</table>"""
    return html
    
def get_flash_chart(chart_type,start_date,end_date,table_id,report_type,max_results,sort,filters):
    from atrinsic.web import openFlashChart
    import urllib
    x = urllib.urlencode({'table_id':table_id,'report_type':report_type,'sort':sort, 'filters':filters,'max_results':max_results})
    #url = '/analytics/reporting/%s/%s/%s/%s/%s/%s/%s/' % (chart_type,start_date,end_date,table_id,report_type,max_results,sort)
    #url = '/api/0/columns/?data=date=07/01/2009,08/31/2009|group_by=0|custom_columns=1,2'
    url = '/analytics/reporting/chart-columns/%s/%s/?%s' % (start_date,end_date,x)
    print url
    return openFlashChart.flashHTML('100%', '300', url, '/ofc/')    

class AnalyticsMiddleware(object):
    def process_view(self,request,view_func,view_args,view_kwargs):
        if request.session.get("analytics",None):
            request.analytics = request.session['analytics']
        if request.session.get("selected_site",None):
            request.analytics.selected_site = request.session['selected_site']
        return None
