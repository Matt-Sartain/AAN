from urllib import urlencode
from urllib2 import HTTPHandler
from urllib2 import Request
from urllib2 import build_opener

try:
	from cjson import decoded
	json_decode = decode
except:
	from django.utils import simplejson
	json_decode = simplejson.loads

class PyWik(object):
	__doc__ = '''
		Module Actions
		- Actions.getActions (idSite, period, date, expanded = '', idSubtable = '')
		- Actions.getDownloads (idSite, period, date, expanded = '', idSubtable = '')
		- Actions.getOutlinks (idSite, period, date, expanded = '', idSubtable = '')
		
		Module Referers
		- Referers.getRefererType (idSite, period, date, typeReferer = '')
		- Referers.getKeywords (idSite, period, date, expanded = '')
		- Referers.getSearchEnginesFromKeywordId (idSite, period, date, idSubtable)
		- Referers.getSearchEngines (idSite, period, date, expanded = '')
		- Referers.getKeywordsFromSearchEngineId (idSite, period, date, idSubtable)
		- Referers.getCampaigns (idSite, period, date, expanded = '')
		- Referers.getKeywordsFromCampaignId (idSite, period, date, idSubtable)
		- Referers.getWebsites (idSite, period, date, expanded = '')
		- Referers.getUrlsFromWebsiteId (idSite, period, date, idSubtable)
		- Referers.getNumberOfDistinctSearchEngines (idSite, period, date)
		- Referers.getNumberOfDistinctKeywords (idSite, period, date)
		- Referers.getNumberOfDistinctCampaigns (idSite, period, date)
		- Referers.getNumberOfDistinctWebsites (idSite, period, date)
		- Referers.getNumberOfDistinctWebsitesUrls (idSite, period, date)
		
		Module UserSettings
		- UserSettings.getResolution (idSite, period, date)
		- UserSettings.getConfiguration (idSite, period, date)
		- UserSettings.getOS (idSite, period, date)
		- UserSettings.getBrowser (idSite, period, date)
		- UserSettings.getBrowserType (idSite, period, date)
		- UserSettings.getWideScreen (idSite, period, date)
		- UserSettings.getPlugin (idSite, period, date)
		
		Module UserCountry
		- UserCountry.getCountry (idSite, period, date)
		- UserCountry.getContinent (idSite, period, date)
		- UserCountry.getNumberOfDistinctCountries (idSite, period, date)
		
		Module VisitsSummary
		- VisitsSummary.get (idSite, period, date, columns = 'Array')
		- VisitsSummary.getVisits (idSite, period, date)
		- VisitsSummary.getUniqueVisitors (idSite, period, date)
		- VisitsSummary.getActions (idSite, period, date)
		- VisitsSummary.getMaxActions (idSite, period, date)
		- VisitsSummary.getBounceCount (idSite, period, date)
		- VisitsSummary.getVisitsConverted (idSite, period, date)
		- VisitsSummary.getSumVisitsLength (idSite, period, date)
		- VisitsSummary.getSumVisitsLengthPretty (idSite, period, date)
		
		Module VisitFrequency
		- VisitFrequency.get (idSite, period, date, columns = 'Array')
		- VisitFrequency.getVisitsReturning (idSite, period, date)
		- VisitFrequency.getActionsReturning (idSite, period, date)
		- VisitFrequency.getMaxActionsReturning (idSite, period, date)
		- VisitFrequency.getSumVisitsLengthReturning (idSite, period, date)
		- VisitFrequency.getBounceCountReturning (idSite, period, date)
		- VisitFrequency.getConvertedVisitsReturning (idSite, period, date)
		
		Module VisitTime
		- VisitTime.getVisitInformationPerLocalTime (idSite, period, date)
		- VisitTime.getVisitInformationPerServerTime (idSite, period, date)
		
		Module UsersManager
		- UsersManager.getUsers () 
		- UsersManager.getUsersLogin ()
		- UsersManager.getUsersSitesFromAccess (access)
		- UsersManager.getUsersAccessFromSite (idSite)
		- UsersManager.getSitesAccessFromUser (userLogin)
		- UsersManager.getUser (userLogin)
		- UsersManager.getUserByEmail (userEmail)
		- UsersManager.addUser (userLogin, password, email, alias = '')
		- UsersManager.updateUser (userLogin, password = '', email = '', alias = '')
		- UsersManager.deleteUser (userLogin)
		- UsersManager.userExists (userLogin)
		- UsersManager.userEmailExists (userEmail)
		- UsersManager.setUserAccess (userLogin, access, idSites)
		- UsersManager.getTokenAuth (userLogin, md5Password)
		
		Module SitesManager
		- SitesManager.getJavascriptTag (idSite, piwikUrl = '', actionName = '')
		- SitesManager.getSiteFromId (idSite)
		- SitesManager.getSiteUrlsFromId (idSite)
		- SitesManager.getAllSitesId ()
		- SitesManager.getSitesWithAdminAccess ()
		- SitesManager.getSitesWithViewAccess () 
		- SitesManager.getSitesWithAtLeastViewAccess ()
		- SitesManager.getSitesIdWithAdminAccess ()
		- SitesManager.getSitesIdWithViewAccess ()
		- SitesManager.getSitesIdWithAtLeastViewAccess ()
		- SitesManager.addSite (siteName, urls)
		- SitesManager.deleteSite (idSite)
		- SitesManager.addSiteAliasUrls (idSite, urls)
		- SitesManager.updateSite (idSite, siteName, urls)
		
		Module Provider
		- Provider.getProvider (idSite, period, date)
		
		Module ExampleAPI
		- ExampleAPI.getPiwikVersion () 
		- ExampleAPI.getAnswerToLife () 
		- ExampleAPI.getGoldenRatio () 
		- ExampleAPI.getObject () 
		- ExampleAPI.getNull () 
		- ExampleAPI.getDescriptionArray () 
		- ExampleAPI.getCompetitionDatatable () 
		- ExampleAPI.getMoreInformationAnswerToLife () 
		
		Module LanguagesManager
		- LanguagesManager.isLanguageAvailable (languageCode)
		- LanguagesManager.getAvailableLanguages ()
		- LanguagesManager.getAvailableLanguagesInfo ()
		- LanguagesManager.getAvailableLanguageNames ()
		- LanguagesManager.getTranslationsForLanguage (languageCode)
		- LanguagesManager.getLanguageForUser (login)
		- LanguagesManager.setLanguageForUser (login, language) 
		
		Module DBStats
		- DBStats.getDBStatus ()
		- DBStats.getTableStatus (table, field = '')
		- DBStats.getAllTablesStatus ()
		
		Module VisitorInterest
		- VisitorInterest.getNumberOfVisitsPerVisitDuration (idSite, period, date)
		- VisitorInterest.getNumberOfVisitsPerPage (idSite, period, date)
		
		Module Goals
		- Goals.getGoals (idSite)
		- Goals.addGoal (idSite, name, matchAttribute, pattern, patternType, caseSensitive, revenue)
		- Goals.updateGoal (idSite, idGoal, name, matchAttribute, pattern, patternType, caseSensitive, revenue)
		- Goals.deleteGoal (idSite, idGoal)
		- Goals.getConversionRateReturningVisitors (idSite, period, date, idGoal = '')
		- Goals.getConversionRateNewVisitors (idSite, period, date, idGoal = '')
		- Goals.get (idSite, period, date, idGoal = '', columns = 'Array')
		- Goals.getConversions (idSite, period, date, idGoal = '')
		- Goals.getConversionRate (idSite, period, date, idGoal = '')
		- Goals.getRevenue (idSite, period, date, idGoal = '')
		
		Module Live
		- Live.getLastVisitForVisitor (visitorId, idSite)
		- Live.getLastVisitsForVisitor (visitorId, idSite, limit = '10')
		- Live.getLastVisits (idSite = '', limit = '10', minIdVisit = '')
	'''

	Functions = [
				'Actions_getActions','Actions_getDownloads','Actions_getOutlinks',
				'Referers_getRefererType','Referers_getKeywords','Referers_getSearchEnginesFromKeywordId','Referers_getSearchEngines','Referers_getKeywordsFromSearchEngineId','Referers_getCampaigns','Referers_getKeywordsFromCampaignId','Referers_getWebsites','Referers_getUrlsFromWebsiteId','Referers_getNumberOfDistinctSearchEngines','Referers_getNumberOfDistinctKeywords','Referers_getNumberOfDistinctCampaigns','Referers_getNumberOfDistinctWebsites','Referers_getNumberOfDistinctWebsitesUrls',
				'UserSettings_getResolution','UserSettings_getConfiguration','UserSettings_getOS','UserSettings_getBrowser','UserSettings_getBrowserType','UserSettings_getWideScreen','UserSettings_getPlugin',
				'UserCountry_getCountry','UserCountry_getContinent','UserCountry_getNumberOfDistinctCountries',
				'VisitsSummary_get','VisitsSummary_getVisits','VisitsSummary_getUniqueVisitors','VisitsSummary_getActions','VisitsSummary_getMaxActions','VisitsSummary_getBounceCount','VisitsSummary_getVisitsConverted','VisitsSummary_getSumVisitsLength','VisitsSummary_getSumVisitsLengthPretty',
				'VisitFrequency_get','VisitFrequency_getVisitsReturning','VisitFrequency_getActionsReturning','VisitFrequency_getMaxActionsReturning','VisitFrequency_getSumVisitsLengthReturning','VisitFrequency_getBounceCountReturning','VisitFrequency_getConvertedVisitsReturning',
				'VisitTime_getVisitInformationPerLocalTime','VisitTime_getVisitInformationPerServerTime',
				'UsersManager_getUsers','UsersManager_getUsersLogin''UsersManager_getUsersSitesFromAccess','UsersManager_getUsersAccessFromSite','UsersManager_getSitesAccessFromUser','UsersManager_getUser','UsersManager_getUserByEmail','UsersManager_addUser','UsersManager_updateUser','UsersManager_deleteUser','UsersManager_userExists','UsersManager_userEmailExists','UsersManager_setUserAccess','UsersManager_getTokenAuth',
				'SitesManager_getJavascriptTag','SitesManager_getSiteFromId','SitesManager_getSiteUrlsFromId','SitesManager_getAllSitesId','SitesManager_getSitesWithAdminAccess','SitesManager_getSitesWithViewAccess','SitesManager_getSitesWithAtLeastViewAccess','SitesManager_getSitesIdWithAdminAccess','SitesManager_getSitesIdWithViewAccess','SitesManager_getSitesIdWithAtLeastViewAccess','SitesManager_addSite','SitesManager_deleteSite','SitesManager_addSiteAliasUrls','SitesManager_updateSite',
				'Provider_getProvider',
				'ExampleAPI_getPiwikVersion','ExampleAPI_getAnswerToLife','ExampleAPI_getGoldenRatio','ExampleAPI_getObject','ExampleAPI_getNull','ExampleAPI_getDescriptionArray','ExampleAPI_getCompetitionDatatable','ExampleAPI_getMoreInformationAnswerToLife',
				'LanguagesManager_isLanguageAvailable','LanguagesManager_getAvailableLanguages','LanguagesManager_getAvailableLanguagesInfo','LanguagesManager_getAvailableLanguageNames','LanguagesManager_getTranslationsForLanguage','LanguagesManager_getLanguageForUser','LanguagesManager_setLanguageForUser',
				'DBStats_getDBStatus','DBStats_getTableStatus','DBStats_getAllTablesStatus',
				'VisitorInterest_getNumberOfVisitsPerVisitDuration','VisitorInterest_getNumberOfVisitsPerPage',
				'Goals_getGoals','Goals_addGoal','Goals_updateGoal','Goals_deleteGoal','Goals_getConversionRateReturningVisitors','Goals_getConversionRateNewVisitors','Goals_get','Goals_getConversions','Goals_getConversionRate','Goals_getRevenue',
				'Live_getLastVisitForVisitor','Live_getLastVisitsForVisitor','Live_getLastVisits',
				]
		
	def __init__(self, decode = True, **args):
		self.end_point = 'http://piwik.atrinsic.com/index.php?module=API&'
		self.__missing_method = None
		self.decode = decode
		self.auth = args.get("auth",None)
		self.data = None
		
	def __call__(self, name, **params):
		self.__missing_method = name
		return self.__virtual__(None, **params)

	def __getattr__(self, name):
		self.__missing_method = name
		return getattr(self, '__virtual__')

	def __virtual__(self, *args, **param):
		if(self.__missing_method in self.Functions):
			return self.__talk_to_piwik(self.__missing_method, param)
		else:
			raise AttributeError("'PyWik' object has no attribute '%s'" % self.__missing_method)

	def __talk_to_piwik(self, method, params):
		try:
			request_handler = build_opener(HTTPHandler)
			params.update({ 'token_auth': self.auth, 'format': 'json', 'method': method.replace('_','.') })
			request_param = urlencode(params)
			self.post_url = '%s%s' % (self.end_point, request_param)
			request = Request(self.post_url, data = None)
			response = request_handler.open(request)
			response_text = response.read()

			if(response.code == 200):
				if(self.decode):
					try:
						try:
							response_text = json_decode(response_text.replace("\\\\","\\"))
						except:
							pass
						self.data = response_text
					except Exception, e:
						return False, response.code, '%s -> %s' % (str(e), response_text)

			return True, response.code, response_text
		except Exception, e:
			return False, 500, str(e)

class TableWidget(PyWik):
	def __init__(self, auth, decode = True, headers = ['Field', 'Value'], data_columns = ['label', 'nb_visits']):
		super(TableWidget, self).__init__(decode=decode, auth=auth)
		self.headers = headers
		self.data_columns = data_columns
		self.data = None
	def execute(self):
		var1 = []
		labels = []
		val_dict = self.data
		if self.data_columns[0] == 'value':
			return self.data
		else:
			x = self.data_columns[0]
			y = self.data_columns[1]
			if (isinstance(val_dict,type([]))) & (val_dict != None):
				labels = []
				var1 = []
				for var in val_dict:
					if isinstance(var,type([])):
						for z in var:
							labels.append(z[x])
							var1.append(int(z[y]))
					else:
						x = self.data_columns[0]
						y = self.data_columns[1]
						labels.append(var[x])
						var1.append(int(var[y]))
			elif (isinstance(val_dict,dict)) & (val_dict != None):
				for key in val_dict:
					if isinstance(val_dict[key],type([])):
						for z in val_dict[key]:
							labels.append(z[x])
							var1.append(z[y])
					else:
						labels.append(key)
						var1.append(val_dict[key])
		return { 'headers': labels, 'data': var1 }

class ChartWidget(PyWik):
	def __init__(self, auth, decode = True, title = '', data_columns = ['label','nb_visits']):
		super(ChartWidget, self).__init__(decode=decode, auth=auth)
		self.title = title
		self.data_columns = data_columns

	def execute(self, style):
		from atrinsic.web import openFlashChart
		from atrinsic.web.openFlashChart_varieties import Styler
		Style = Styler(style)
		#try:
		var1 = []
		labels = []
		val_dict = self.data
		url = self.post_url
		if self.data_columns[0] == 'value':
			return self.data
		else:
			x = self.data_columns[0]
			y = self.data_columns[1]
			if (isinstance(val_dict,type([]))) & (val_dict != None):
				labels = []
				var1 = []
				for var in val_dict:
					if isinstance(var,type([])):
						for z in var:
							labels.append(z[x])
							var1.append(int(z[y]))
					else:
						x = self.data_columns[0]
						y = self.data_columns[1]
						labels.append(var[x])
						var1.append(int(var[y]))
			elif (isinstance(val_dict,dict)) & (val_dict != None):
				for key in val_dict:
					if isinstance(val_dict[key],type([])):
						for z in val_dict[key]:
							labels.append(z[x])
							var1.append(z[y])
					else:
						labels.append(key)
						var1.append(val_dict[key])
		
		chart = openFlashChart.template('')
		chart.set_bg_colour(colour='#ffffff')
					
		if isinstance(var1,type([])):
			try:
				z = min(var1)
				y = max(var1)
				range_y1_min = round(z*0.95,0)
				range_y1_max = round(y*1.05,0)
				range_y1_steps = round(round(y*1.05,0)/10,0)
			except:
				y=0
				z=0
				for dict_item in var1:
					try:
						if 	int(dict_item['nb_visits']) > y:
							y=dict_item['nb_visits']
						if 	int(dict_item['nb_visits']) < z:
							z=dict_item['nb_visits']
					except:
						y=int(dict_item)
						z=int(dict_item)
				range_y1_min = round(z*0.95,0)
				range_y1_max = round(y*1.05,0)
				range_y1_steps = round(round(y*1.05,0)/10,0)
		else:
			range_y1_min = 0
			range_y1_max = 0
			range_y1_steps = 0
		
		chart.set_y_axis(min = range_y1_min, max = range_y1_max, steps = range_y1_steps)
		chart.set_x_axis(labels = {'labels':labels, 'rotate':'vertical'})
		
		if style == 'pie':
			plot = Style(text = self.title, fontsize = 20, values = var1, colours = ['#4f8dbc','#54b928'])
		else:
			plot = Style(text = self.title, fontsize = 20, values = var1)
		
		plot.set_colour('#4f8dbc')
		chart.add_element(plot)
		return chart.encode()