from atrinsic.web.reports import *
class QuickReports():
    def __init__(self,**args):
        from datetime import datetime
        from pywik import prep_date
        from atrinsic.base.models import PublisherGroup,Organization,Website,PublisherVertical
        start = None
        end = None
        if args.has_key('date_range'):
            if args['date_range'] != '':
                if args['date_range'].find(",") > 0:
                    start,end=args['date_range'].split(",")
                else:
                    try:
                        start = datetime.strptime(args['date_range'],"%m/%d/%Y")
                        end = start
                    except:
                        pass
                if (start != None and end != None) & (not isinstance(start,datetime) and not isinstance(end,datetime)):
                    try:
                        self.date_start = datetime.strptime(start,"%m/%d/%Y")
                        self.date_end = datetime.strptime(end,"%m/%d/%Y")
                    except:
                        self.date_start = datetime.strptime(start,"%Y-%m-%d")
                        self.date_end = datetime.strptime(end,"%Y-%m-%d")
                else:
                    var_now = datetime.now()
                    self.date_start = var_now
                    self.date_end = var_now
            else:
                var_now = datetime.now()
                self.date_start = var_now
                self.date_end = var_now
        else:
            #need handling for text date formats like yesterday for example, not sure where this comes from yet might just be able to remove yesterday and put a date range there.
            calc_date = prep_date(args.get('date',','))
            if (calc_date == 'None,None') | (calc_date == '') | (calc_date == None) | (calc_date == ','):
                var_now = datetime.now()
                calc_date = var_now
            if isinstance(calc_date, str):
                if calc_date.find(",") > 0:
                    start,end = calc_date.split(",")
                    try:
                        self.date_start = datetime.strptime(start,"%m/%d/%Y")
                        self.date_end = datetime.strptime(end,"%m/%d/%Y")
                    except:
                        self.date_start = datetime.strptime(start,"%Y-%m-%d")
                        self.date_end = datetime.strptime(end,"%Y-%m-%d")
                else:
                    try:
                        self.date_start = datetime.strptime(calc_date,"%m/%d/%Y") 
                        self.date_end = datetime.strptime(calc_date,"%m/%d/%Y")
                    except:
                        self.date_start = datetime.strptime(calc_date,"%Y-%m-%d") 
                        self.date_end = datetime.strptime(calc_date,"%Y-%m-%d")
            else:
                self.date_start = calc_date
                self.date_end = calc_date
        request = args.get("request",None)
        self.group_by = request.GET.get('group_by',0)
        self.widget_id=args.get("widget_id",None)
        self.user_widget_id=args.get("user_widget_id",None)
        self.data_columns = args.get("custom_columns",None)
        self.publisher_set = []
        self.advertiser_set = []
        if request.GET.getlist('run_reporting_by_publisher') != []:
            self.publisher_set = request.GET.getlist('run_reporting_by_publisher')
        elif request.GET.get('run_reporting_by_group', None) != None:
            for publisher in PublisherGroup.objects.get(pk=request.GET.get('run_reporting_by_group')[2:]).publishers.all():
                self.publisher_set.append(publisher.id)
        elif request.GET.getlist('advertiser_category') != []:
            org_set = Organization.objects.filter(vertical__in = request.GET.getlist('advertiser_category'))
            for org in org_set:
                self.advertiser_set.append(int(org.id))
        elif request.GET.getlist('run_reporting_by_vertical') != []:
            int_ids = []
            for string_id in request.GET.getlist('run_reporting_by_vertical'):
                int_ids.append(int(string_id))
            for x in Website.objects.filter(vertical__in = PublisherVertical.objects.filter(order__in = int_ids)):
                self.publisher_set.append(int(x.publisher_id))
        elif request.GET.get('specific_advertiser',None) and int(request.GET.get('run_reporting_by',0)) == 1 :
            self.advertiser_set = request.GET['specific_advertiser']
    def getSalesReport(self, request, chart_style):
        if request.organization.is_advertiser():
            report_obj = DateReport(self.date_start,self.date_end,request.organization,group_by=self.group_by, spec=REPORTTYPE_SALES, publisher_set=self.publisher_set)
        else:
            report_obj = DateReport(self.date_start,self.date_end,request.organization,group_by=self.group_by,spec=REPORTTYPE_SALES,advertiser_set=self.advertiser_set)
        return self.FormattedContent(report_obj, chart_style, request)
        
    def getOrgSalesReport(self, request, chart_style, publisher_set = []):
        if request.organization.is_advertiser():
            report_obj = OrgDateReport(self.date_start,self.date_end,request.organization,group_by=self.group_by,spec=REPORTTYPE_SALES_BY_PUBLISHER,publisher_set=publisher_set)
        else:
            report_obj = OrgDateReport(self.date_start,self.date_end,request.organization,group_by=self.group_by,spec=REPORTTYPE_SALES_BY_ADVERTISER,advertiser_set=self.advertiser_set)
        return self.FormattedContent(report_obj, chart_style, request)
        
    def getRevenueReport(self,request,chart_style):
        if request.organization.is_advertiser():
            report_obj = RevenueReport(self.date_start,self.date_end,request.organization,group_by=self.group_by,spec=REPORTTYPE_REVENUE,publisher_set=self.publisher_set)
        else:
            report_obj = RevenueReport(self.date_start,self.date_end,request.organization,group_by=self.group_by,spec=REPORTTYPE_REVENUE,advertiser_set=self.advertiser_set)
        return self.FormattedContent(report_obj, chart_style, request)
        
    def getOrgRevenueReport(self, request, chart_style):
        if request.organization.is_advertiser():
            report_obj = OrgRevenueReport(self.date_start,self.date_end,request.organization,group_by=self.group_by,spec=REPORTTYPE_REVENUE_BY_PUBLISHER,publisher_set=self.publisher_set)
        else:
            report_obj = OrgRevenueReport(self.date_start,self.date_end,request.organization,group_by=self.group_by,spec=REPORTTYPE_REVENUE_BY_ADVERTISER,advertiser_set=self.advertiser_set)
        return self.FormattedContent(report_obj, chart_style, request)   
        
    def getLinksReport(self, request, chart_style):
        if request.organization.is_advertiser():
            report_obj = CreativeReport(self.date_start,self.date_end,request.organization,group_by=self.group_by,spec=REPORTTYPE_CREATIVE,publisher_set=self.publisher_set)
        else:
            report_obj = CreativeReport(self.date_start,self.date_end,request.organization,group_by=self.group_by,spec=REPORTTYPE_CREATIVE,advertiser_set=self.advertiser_set)
        return self.FormattedContent(report_obj, chart_style, request)
            
    def getAccountingReport(self, request, chart_style):
        if request.organization.is_advertiser():
            report_obj = AccountingReport(self.date_start,self.date_end,request.organization,group_by=self.group_by,spec=REPORTTYPE_ACCOUNTING,publisher_set=self.publisher_set)
        else:
            report_obj = AccountingReport(self.date_start,self.date_end,request.organization,group_by=self.group_by,spec=REPORTTYPE_ACCOUNTING,advertiser_set=self.advertiser_set)
        return self.FormattedContent(report_obj, chart_style, request)
            
    def getPromoReport(self, request, chart_style):
        if request.organization.is_advertiser():
            report_obj = PromoReport(self.date_start,self.date_end,request.organization,group_by=self.group_by,spec=REPORTTYPE_CREATIVE_BY_PROMO,publisher_set=self.publisher_set)
        else:
            report_obj = PromoReport(self.date_start,self.date_end,request.organization,group_by=self.group_by,spec=REPORTTYPE_CREATIVE_BY_PROMO,advertiser_set=self.advertiser_set)
        return self.FormattedContent(report_obj, chart_style, request)
        
    def getOrderReport(self, request, chart_style):
        if request.organization.is_advertiser():
            report_obj = OrderReport(self.date_start,self.date_end,request.organization,group_by=self.group_by,spec=REPORTTYPE_ORDER_DETAIL,publisher_set=self.publisher_set)
        else:
            report_obj = OrderReport(self.date_start,self.date_end,request.organization,group_by=self.group_by,spec=REPORTTYPE_ORDER_DETAIL,advertiser_set=self.advertiser_set)
        return self.FormattedContent(report_obj, chart_style, request)
    
    def getProductReport(self, request, chart_style):
        if request.organization.is_advertiser():
            report_obj = ProductReport(self.date_start,self.date_end,request.organization,group_by=self.group_by,spec=REPORTTYPE_PRODUCT_DETAIL,publisher_set=self.publisher_set)
        else:
            report_obj = OrderReport(self.date_start,self.date_end,request.organization,group_by=self.group_by,spec=REPORTTYPE_ORDER_DETAIL,advertiser_set=self.advertiser_set)
            
        return self.FormattedContent(report_obj,chart_style,request)
            
    def FormattedContent(self, report_obj, chart_style, request):
        from atrinsic.base.models import AqWidget,UserAqWidget
        x = self.widget_id
        widget = AqWidget.objects.get(pk=self.widget_id)
        var_columns = None
        
        if self.user_widget_id != None:
            user_widget = UserAqWidget.objects.get(pk=self.user_widget_id)
            if user_widget.custom_columns != None:
                var_columns = user_widget.custom_columns
        if (var_columns == None) & (self.data_columns != None):
            var_columns = self.data_columns	
        else:
            var_columns = widget.data_columns
        if var_columns.find(",") > 0:
            col1,col2 = var_columns.split(",")
        else:
            col1 = var_columns
            col2 = None
        columns = { 'var1': col1, 'var2':col2 }
        if chart_style == "table":
            html = self.getReportHTML(report_obj)
            return html
        elif chart_style == "json-array":
            import cjson
            return cjson.encode(report_obj.RenderContents())
        elif chart_style == "json":
            import cjson
            json = self.get_json(report_obj)
            return cjson.encode(json)
        elif chart_style == "xml":
            from elementtree import ElementTree
            from elementtree.ElementTree import Element,tostring,SubElement,ElementTree,dump
            xmldict = {}
            xmldict["xml"] = self.get_json(report_obj)
            root = Element("xml")
            for row in xmldict["xml"]:
                item_element = SubElement(root,"item")
                for field in row:
                    SubElement(item_element,field).text = row[field]
            return tostring(root)
            
        else:
            return self.getAQChart(request=request,chart_style=chart_style,report_obj=report_obj,columns=columns)
    def _ConvertDictToXmlRecurse(self,parent, array_of_dicts):
        array_of_dicts
        if isinstance(dictitem, dict):
            for (tag, child) in dictitem.iteritems():
                if str(tag) == '_text':
                    parent.text = str(child)
                elif type(child) is type([]):
                    # iterate through the array and convert
                    for listchild in child:
                        elem = ElementTree.Element(tag)
                        parent.append(elem)
                        _ConvertDictToXmlRecurse(elem, listchild)
                else:                
                    elem = ElementTree.Element(tag)
                    parent.append(elem)
                    _ConvertDictToXmlRecurse(elem, child)
        else:
            parent.text = str(dictitem)      
    def get_json(self,report_obj):
        headers = report_obj.RenderHeader()
        body = report_obj.RenderContents()
        json_dict = {}
        json = []
        for row in body:
            for index,keys in enumerate(headers):
                json_dict[keys[1]] = row[index]
            json.append(json_dict)
            json_dict = {}
        return json
    def getReportHTML(self,report_obj):

        from datetime import datetime
        html = """	<table class="widget_table" border="0" cellspacing="0" cellpading="0">
                    <thead>
                    <tr>"""
        template_row="<tr>"
        for field in report_obj.RenderHeader():
            html+="""<th ><div class="widget_table_headers">"""+str(field[0])+"""</div></th>"""
            template_row += "<td>%s</td>"
        template_row+="</tr>"
        html+="""</tr>
        </thead>
        <tbody>"""
        table_content,row_count = report_obj.RenderContents(False)
        html += template_row * row_count
        html+="""</tbody>
        <tfoot>
        <tr class="total">"""
        html = html % tuple(table_content)
        for col in report_obj.RenderFooter():
            try:
                html+="""<td>"""+col[1]+"""</td>"""
            except:
                html+="""<td> - </td>"""
        html+="""</tr>
        </tfoot>
        </table>"""
        return html
    def getAQChart(self,request,chart_style, report_obj, columns):
        from datetime import datetime
        from atrinsic.web import openFlashChart
        from atrinsic.web.openFlashChart_varieties import Styler
            
        Style = Styler(chart_style)
        
        var1 = []
        var2 = []
        labels = []
        
        index_one = 0
        index_two = 0
        try:
            column_id1 = int(columns['var1'])
            column_id2 = int(columns['var2'])
        except:
            column_id1 = columns['var1']
            column_id2 = columns['var2']
        if column_id1 == 1:
            columns['var1']="impressions"
        if column_id1 == 2:
            columns['var1']="clicks"
        if column_id1 == 3:
            columns['var1']="leads"
        if column_id1 == 4:
            columns['var1']="orders"
        if column_id1 == 5:
            columns['var1']="amount"
        if column_id1 == 6:
            columns['var1']="publisher_payout"
        if column_id2 == 1:
            columns['var2']="impressions"
        if column_id2 == 2:
            columns['var2']="clicks"
        if column_id2 == 3:
            columns['var2']="leads"
        if column_id2 == 4:
            columns['var2']="orders"
        if column_id2 == 5:
            columns['var2']="amount"
        if column_id2 == 6:
            columns['var2']="publisher_payout"
        
        for header in report_obj.RenderHeader():
            if header[1] == columns['var1']:
                break
            index_one+=1
        if columns.get('var2',None) != None:
            headers = report_obj.RenderHeader()
            for header in report_obj.RenderHeader():	
                if header[1] == columns['var2']:
                    break
                index_two+=1
        content = report_obj.RenderContents()
        
        for row in report_obj.RenderContents():
            col_counter = 0
            for col in row:
                if col_counter == 0:
                    try:
                        y,m,d=col.split('/')
                        reformat_date = datetime(int(y),int(m),int(d))
                        x=reformat_date.strftime('%m/%d/%Y')
                    except:
                        x=col
                    labels.append(str(x))
                if col_counter == index_one:
                    col = col.replace("$","")
                    col = col.replace(",","")
                    col = re.sub("[^0-9\.]*", "", col)
                    try:
                        var1.append(int(float(col)))
                    except:
                        var1.append(int(float(0)))
                if index_two > 0:
                    if col_counter == index_two:
                        col = col.replace("$","")
                        col = col.replace(",","")
                        var2.append(int(float(re.sub("[^0-9\.]*", "", col))))
                col_counter += 1
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
        
        if chart_style != 'pie':
            chart.add_element(plot1)
            chart.add_element(plot2)
        else:
            chart.add_element(plot1)
        return chart.encode()
    def error_graphic(self):
        from atrinsic.web.openFlashChart_varieties import Styler
        from atrinsic.web import openFlashChart
        chart = openFlashChart.template('No data to display')
        chart.set_bg_colour(colour='#ffffff')
        Style = Styler('lines')
        plot1 =  Style(text = "No data to display", fontsize = 20, values = [])
        chart.add_element(plot1)
        return chart.encode()
class Dashboard():
    def __init__(self, **args):
        pass
        
    def Events(self):
        return None
        
    def Alerts(self):
        return None
    
    def News(self):
        return None