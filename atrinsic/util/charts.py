""" 
FULL DOCUMENTATION IS AVAILABLE ON THE CONTENT TEAM SHARE POINT. PROBABLY SHOULD READ IT ALL BEFORE YOU USE THIS.
"""

def get_chart_vars(request,date_start,date_end):
	from atrinsic.util.imports import *
	from atrinsic.web.reports import *
	
	pids,aids = request.organization.get_dashboard_filtered_orgs()
	
	variable1 = request.organization.dashboard_variable1,
	var1_name = request.organization.get_dashboard_variable1_display(),
	variable2 = request.organization.dashboard_variable2,
	var2_name = request.organization.get_dashboard_variable2_display(),
	date_range = [date_start,date_end]
	var1_results = request.organization.get_chart_vars(variable1[0],date_range,request.organization.dashboard_group_data_by,aids,pids)
	var2_results = request.organization.get_chart_vars(variable2[0],date_range,request.organization.dashboard_group_data_by,aids,pids)
	
	graph_data = {
		'variable1':var1_results,
		'variable1_name':var1_name[0],
		'variable2':var2_results,
		'variable2_name':var2_name[0],
	}
	return graph_data



def simpleEncode(valueArray,maxValue):
	simpleEncoding = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
	chartData = []
	for i in valueArray:
		currentValue = i
		if (currentValue != None) & (currentValue >= 0):
			chartData.append(simpleEncoding[round(len(simpleEncoding) -1 * currentValue / maxValue)])
		else:
	  		chartData.append('_');
	return chartData.replace(", ","")
	
class AtrinsicChart(object):
	def __init__(self, chart_data):
		#tags		
		self.chart_api_url = 'http://chart.apis.google.com/chart?'
		self.chart_type_tag = 'cht='
		self.chart_data_tag = 'chd='+str(chart_data['data']['encoding'])+':'
		self.grid_tag = "chg="	
		scale = str(chart_data['data']['data_scaling'])
		scale = scale.replace("[","")
		scale = scale.replace("]","")
		self.chart_data_scale = "chds="+scale
		self.chart_color_tag = 'chco='
		self.chart_axis_tag = 'chxt='
		self.chart_axis_range_tag = 'chxr='
		self.chart_axis_labels_tag = 'chxl='
		self.chart_bar_width_tag = 'chbh='
		self.chart_size_tag = 'chs='
		self.chart_type = ''
		self.chart_legend_tag = 'chdl='
		self.chart_data_points_tag = 'chm='
		
		_type = chart_data.get('type','line')
		if _type=='lines':
			self.chart_type = "lc"
		elif _type =='bars':
			self.chart_type = 'bhg'
		elif _type =='columns':
			self.chart_type = 'bvg'
		elif _type =='pie':
			self.chart_type = 'p'
		elif _type =='pie_3d':
			self.chart_type = 'p3'
		
		temp_size = {}
		temp_size = chart_data.get('size',None)
		if temp_size != None:
			self.chart_width = temp_size.get('width',0)
			self.chart_height = temp_size.get('height',0)
		else:
			self.chart_width = None
			self.chart_height = None
			
		self.grid = str(chart_data.get('grid',None))			
			
		temp_data = {}
		temp_data = chart_data.get('data',None)
		if temp_data != None:
			self.var1 = temp_data.get('var1', None)
			self.var1_legend = temp_data.get('var1_legend', None)
			self.var2 = temp_data.get('var2', None)
			self.var2_legend = temp_data.get('var2_legend', None)
			self.axis = temp_data.get('axis', None)
			self.chart_legend = str(self.axis.get('legend',None))
		else:
			self.var1 = None
			self.var1_label = None
			self.var2 = None
			self.var2_label = None
			self.axis = None
			self.axis_labels = None
			self.chart_legend = None
			
		self.chart_colors = chart_data.get('colors',None)
		self.chart_bar_options = chart_data.get('bar_options', None)
		self.grid = chart_data.get('grid',None)
		self.data_points = chart_data.get('data_points',None)
		
	def getChart(self, _type = None):
		'''gets a chart based on the parameters set when you created the chart object,
		see list of other functions to get other types of charts'''
		if _type=='lines':
			self.chart_type = "lc"
		elif _type =='bars':
			self.chart_type = 'bhg'
		elif _type =='columns':
			self.chart_type = 'bvg'
		elif _type =='pie':
			self.chart_type = 'p'
		elif _type =='pie_3d':
			self.chart_type = 'p3'
		
		
		return_link = self.chart_api_url
		return_link += self.chart_type_tag + self.chart_type + "&" + self.chart_data_scale + "&"
		
		if self.grid != None:
			return_link += self.grid_tag + self.grid + "&"
		
		
		#bar colors and size
		if self.chart_color_tag != None:
			return_link += self.chart_color_tag + str(self.chart_colors) + "&"
		if self.chart_bar_options != None:
			if self.chart_bar_options.get('width',None) != None:
				return_link += self.chart_bar_width_tag + str(self.chart_bar_options['width'])
				if (self.chart_bar_options.get('spacing',None) != None) & (self.chart_bar_options.get('width',None) == 'r'):
			 		return_link += "," + str(self.chart_bar_options['spacing']) + "&"
		 		else:
		 			return_link += "&"
		
		#size the graphic up, this is a must or you wont see it on the page.
		if (self.chart_width != None) & (self.chart_height != None):
			return_link += self.chart_size_tag + str(self.chart_width) +'x'+ str(self.chart_height) + '&'
		
		if self.data_points != None:
			return_link += self.chart_data_points_tag + self.data_points + '&'
			
		#process data into a compiled string the api can understand.	    
		data_part_link = ''
		if self.var1 != None:
			data_part_link = self.chart_data_tag + str(self.var1).replace(', ',',')
		if (self.var2 != None) & (self.chart_type[0:1] != "p"):
			if self.var1 != None:
				data_part_link += "|" + str(self.var2).replace(', ',',')
			else:
				data_part_link += str(self.var2).replace(', ',',')
		return_link += data_part_link + "&"
		
		#process every axis.
		if self.axis != None:
			axis_list = []
			axis_labels = []
			axis_range = []
			index = 0
			#Range Processing
			my_range_var = self.axis['range']
			legend = self.axis.get('legend',None)
			total_range_vars = len(my_range_var) - 1
			if (legend != None) & (self.chart_type[0:1] == "p"):
				return_link += self.chart_legend_tag + legend.split("|")[0]
			elif legend != None:
				return_link += self.chart_legend_tag + legend
			
			for x in my_range_var:
				if index < total_range_vars:
					range = str(my_range_var[x])+"|"
				else:
					range = str(my_range_var[x])
				axis_range.append(str(index)+','+range)
				index += 1
			
			
			my_label_var = self.axis.get('labels', None)
			if my_label_var != None:
				index = 0
				for item in my_label_var:
					axis_list.append(item)
					axis_labels.append(str(index)+":|"+str(my_label_var[item]).replace(', ','|')+"|")
					index += 1
				
				return_link += '&' + self.chart_axis_range_tag + str(axis_range) 
				return_link += '&' + self.chart_axis_tag + str(axis_list)
				return_link += "&" + self.chart_axis_labels_tag + str(axis_labels)
				
		return_link = return_link.replace("'",'')
		return_link = return_link.replace('"','')
		return_link = return_link.replace("[",'')
		return_link = return_link.replace("]",'')
		return_link = return_link.replace(", ",',')
		return_link = return_link.replace("|,",'|')
		return return_link