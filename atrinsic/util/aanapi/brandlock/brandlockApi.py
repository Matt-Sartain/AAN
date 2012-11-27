from atrinsic.util.aanapi.api import Api
from django.utils import simplejson

#Author: 	Michel Page
#date:		02/10/2010

class Brandlock(Api):
    
    #key is to identify witch advertiser we are requesting information for
    
    def __init__(self, key):
        self.blUrl = "http://brandlock.atrinsic.com/api/"
        self.key = key
        super(Brandlock, self).__init__(self.blUrl)
    
    #Get a list of all campaigns for this account. Array is used to populate a django choice field        
    def list_campaigns(self,all,array):
        self.blResource = (self.blUrl + self.key + "/campaigns")
        self.url = self.blResource
        response = self.apiCall()
        
        if array == True:
            newdata = simplejson.JSONDecoder().decode(response)
            choices = []
            if all == True:
                for i in newdata["items"]:
                    choices.append((i["id"],i["name"]))
            else:
                for i in newdata["items"]:
                    if i["isActive"] == True:
                        choices.append((i["id"],i["name"]))
            return choices
        else:
            return response
    def campaign_info(self,id):
        self.blResource = (self.blUrl + self.key + "/campaigns/" + str(id))
        self.url = self.blResource
        response = self.apiCall()
        newdata = simplejson.JSONDecoder().decode(response)
        return newdata
        
    def campaign_save(self,id,values):
        self.blResource = (self.blUrl + self.key + "/campaigns/" + str(id))
        self.url = self.blResource
        self.method = "POST"
        self.params = values
        response = self.apiCall()
        newdata = simplejson.JSONDecoder().decode(response)
        return newdata
    
    def campaign_create(self,values):
        self.blResource = (self.blUrl + self.key + "/campaigns/")
        self.url = self.blResource
        self.method = "POST"
        self.params = values
        response = self.apiCall()
        return response        
        
    def list_competitors(self,campaignid,type):
        #type 0=array for drop down,1=json for drop down,2=all values 
        self.blResource = (self.blUrl + self.key + "/campaigns/" + str(campaignid) + "/hotCompetitors")
        self.url = self.blResource
        self.method = "GET"
        response = self.apiCall()
        newdata = simplejson.JSONDecoder().decode(response)
        if type == 0:
            #Array for Drop Down
            choices = []
            choices.append(('0','(all)'))
            for i in newdata["items"]:
                choices.append((i["url"],i["name"]))
        elif type == 1:
            #JSON
            choices = {}
            choices[0] = "(all)" 
            for i in newdata["items"]:
                choices[i["url"]] = i["name"]
        elif type == 2:
            #Array (all values)
            choices = []
            for i in newdata["items"]:
                choices.append((i["id"],i["url"],i["name"]))   
        return choices
            
    def list_keyword_groups(self,campaignid,type):
        self.blResource = (self.blUrl + self.key + "/campaigns/" + str(campaignid) + "/groups")
        self.url = self.blResource
        response = self.apiCall()
        newdata = simplejson.JSONDecoder().decode(response)
        if type == 0:
            choices = []
            choices.append(('0','(all)'))
            for i in newdata["items"]:
                choices.append((str(i["id"])+"|"+i["name"],i["name"]))
        elif type == 1:
            choices = {}
            choices[0] = "(all)" 
            for i in newdata["items"]:
                choices[str(i["id"])+"|"+i["name"]] = i["name"]
        elif type == 2:
            choices = []
            for i in newdata["items"]:
                choices.append((i["id"],i["name"],i["numTerms"]))
                
        return choices
    
    def list_keywords(self,campaignid,groupid):    
        self.blResource = (self.blUrl + self.key + "/campaigns/" + str(campaignid) + "/groups/" + str(groupid))
        self.url = self.blResource
        response = self.apiCall()
        newdata = simplejson.JSONDecoder().decode(response)
        kwlist = newdata["data"]["terms"]
        return kwlist
                
    #Get details about a campaign  
    def campaign_details(self,campaignId):
        self.blResource = (self.blUrl + self.key + "/campaigns/" + campaignId)
        self.url = self.blResource
        response = self.apiCall()
        return response
        
    def getReport(self,campaignId,report,format,values):
        self.method = "POST"
        self.blResource = (self.blUrl + self.key + "/reports/" + campaignId + "/" + report + "/" + format)
        self.url = self.blResource
        self.params = values
        response = self.apiCall()
        
        if format == "json":
            newdata = simplejson.JSONDecoder().decode(response)
            self.values = []
            for i in newdata["rows"]:
                #for i in range(1, 7): 
                #print i["advertiser_url"]
                for j in specs['brandlock'][report]:
                    self.values.append(i[j[1]])
                    #print i[j[1]]
                     
            #print values
            self.specSize = len(specs['brandlock'][report])
    
            return self.getReportHTML(report)
        else:
            return response
            
    def getReportHTML(self,report):
        from django.utils.encoding import smart_str, smart_unicode
        html = "<table class='dataTableSearchResults blreport' id='reportTbl'><thead><tr>"
        for j in specs['brandlock'][report]:
            html += ( "<th>" + j[0] + "</th>" )   
        html+="</tr></thead><tbody><tr>"
        count=0    
        for i in self.values:
            html += ("<td>" + smart_str(i) + "</td>" )
            count += 1
            if count ==  (self.specSize):
                html+="</tr><tr>"
                count = 0
        html = html[:-4]        
        html+="</tbody></table>"
        return html 

    def create_competitor(self,campaignId,url,name):
        self.method = "POST"
        self.blResource = (self.blUrl + self.key + "/campaigns/" + campaignId + "/hotCompetitors/")
        self.url = self.blResource
        self.params = {'name':name,'url':url}

        response = self.apiCall()
        return response
    def update_competitor(self,campaignId,competitorId,url,name):
        self.method = "POST"
        self.blResource = (self.blUrl + self.key + "/campaigns/" + campaignId + "/hotCompetitors/" + competitorId)
        self.url = self.blResource
        self.params = {'name':name,'url':url}

        response = self.apiCall()
        return response
    def delete_competitor(self,campaignId,competitorId):
        self.method = "DELETE"
        self.blResource = (self.blUrl + self.key + "/campaigns/" + campaignId + "/hotCompetitors/" + competitorId)
        self.url = self.blResource

        response = self.apiCall()
        return response
        
    def update_keywords(self,campaignId,groupId,name,terms):
        self.method = "POST"
        self.blResource = (self.blUrl + self.key + "/campaigns/" + campaignId + "/groups/" + groupId)
        self.url = self.blResource
        self.params = {'name':name,'terms':terms}
        
        response = self.apiCall()
        return response
        
    def create_keywords(self,campaignId,name,terms):
        self.method = "POST"
        self.blResource = (self.blUrl + self.key + "/campaigns/" + campaignId + "/groups")
        self.url = self.blResource
        self.params = {'name':name,'terms':terms}
        
        response = self.apiCall()
        return response         

specs = {}
specs['brandlock'] = {}        

#Spec for reports       
specs['brandlock']['rank'] = [
    ('Advertiser url','advertiser_url'),
    ('Avg Rank','avg_rank'),
    ('Avg Prev Rank','avg_rank_prev'),
    ('Avg Rank Change','avg_rank_change'),
    ('Times Seen','times_seen'),
    ('Times Seen Prev','times_seen_prev'),
    ('Times Seen Change','times_seen_change'),
    ]
    
specs['brandlock']['market_share'] = [
    ('Advertiser url','advertiser_url'),
    ('Avg Market Share Yest','avg_market_share_yesterday'),
    ('Avg Market Share Week','avg_market_share_week'),
    ('Avg Market Share Cust','avg_market_share_custom'),
    ('Avg Market Share Prev','avg_market_share_custom_prev'),
    ('pct Market Share Custom Change','pct_market_share_custom_change'),
    ]
    
specs['brandlock']['day_part'] = [
    ('time day part','time_day_part'),
    ('avg sun rank','avg_sun_rank'),
    ('avg mon rank','avg_mon_rank'),
    ('avg tue rank','avg_tue_rank'),
    ('avg wed rank','avg_wed_rank'),
    ('avg thu rank','avg_thu_rank'),
    ('avg fri rank','avg_fri_rank'),
    ('avg sat rank','avg_sat_rank'),
    ]
    
specs['brandlock']['copy_changes'] = [
    ('keyword_group','keyword_group'),
    ('keyword_term','keyword_term'),
    ('advertiser_url','advertiser_url'),
    ('num_ads','num_ads'),
    ]
          
specs['brandlock']['copy_details'] = [
    ('advertiser url','advertiser_url'),
    ('ad title','ad_title'),
    ('ad text','ad_text'),
    ('ad display url','ad_display_url'),
    ('url','url_url'),
    ('keyword terms','keyword_terms'),
    ('first seen','first_seen'),
    ('last seen','last_seen'),
    ('times seen','times_seen'),
    ]
    
specs['brandlock']['keyword'] = [
    ('advertiser url','advertiser_url'),
    ('num keywords','num_keywords'),
    ('num matching keywords','num_matching_keywords'),
    ('pct matching keywords','pct_matching_keywords'),
    ]      
    
specs['brandlock']['keyword_details'] = [
    ('advertiser url','keyword_group'),
    ('num keywords','keyword_term'),
    ('num matching keywords','does_keyword_overlap'),
    ('pct_matching_keywords','first_seen'),
    ('num keywords','last_seen'),
    ('num matching keywords','times_seen'),
    ]
    
specs['brandlock']['offer_keywords'] = [
    ('advertiser url','keyword_group'),
    ('num keywords','keyword_term'),
    ('Free Shipping','Free Shipping'),
    ('Discount Shipping','Discount Shipping'),
    ('Free Trial','Free Trial'),
    ('Sale','Sale'),
    ('In-Store','In-Store'),
    ('Cash Back','Cash Back'),
    ('Gift Card','Gift Card'),
    ('Subscription','Subscription'),
    ('Free Product','Free Product'),
    ]
    
specs['brandlock']['offer_advertisers'] = [
    ('advertiser url','advertiser_url'),
    ('Free Shipping','Free Shipping'),
    ('Discount Shipping','Discount Shipping'),
    ('Free Trial','Free Trial'),
    ('Sale','Sale'),
    ('In-Store','In-Store'),
    ('Cash Back','Cash Back'),
    ('Gift Card','Gift Card'),
    ('Subscription','Subscription'),
    ('Free Product','Free Product'),
    ]

specs['brandlock']['listing'] = [
    ('keyword term','keyword_term'),
    ('competitor','advertiser_url'),
    ('worst rank section','worst_rank_section'),
    ('best rank section','best_rank_section'),
    ('worst rank overall','worst_rank_overall'),
    ('best rank overall','best_rank_overall'),
    ('times listed','times_listed'),
    ]   
    
specs['brandlock']['listing_details'] = [
    ('keyword term','keyword_term'),
    ('listing provider','listing_provider'),
    ('competitor','advertiser_url'),
    ('listing title','listing_title'),
    ('rank section','rank_section'),
    ('rank overall','rank_overall'),
    ]
            
specs['brandlock']['trademark'] = [
    ('trademark term','trademark_term'),
    ('ad provider','ad_provider'),
    ('keyword seen','keyword_seen'),
    ('copy seen','copy_seen'),
    ('web seen','web_seen'),
    ('news seen','news_seen'),
    ('blogs seen','blogs_seen'),
    ]     
specs['brandlock']['trademark_details'] = [
    ('trademark term','trademark_term'),
    ('violator domain','violator_domain'),
    ('violation type','violation_type'),
    ('violation details','violation_details1'),
    ('ad provider','ad_provider'),
    ('keyword term','keyword_term'),
    ('avg rank','avg_rank'),
    ('first seen','first_seen'),
    ('last seen','last_seen'),
    ('times seen','times_seen'),
    ]   
    
specs['brandlock']['url_highjacks'] = [
    ('Advertiser url','advertiser_url'),
    ('url domain','url_domain'),
    ('ad provider','ad_provider'),
    ('first seen','first_seen'),
    ('last seen','last_seen'),
    ('times seen','times_seen'),
    ]  
        
specs['brandlock']['url_highjacks_details'] = [
    ('Competitor','advertiser_url'),
    ('Destination Domain','url_domain'),
    ('url network','url_network'),
    ('url affiliate','url_affiliate'),
    ('ad title','ad_title'),
    ('ad text','ad_text'),
    ('ad display_url','ad_display_url'),
    ('ad provider','ad_provider'),
    ('keyword term','keyword_term'),
    ('avg rank','avg_rank'),
    ('first seen','first_seen'),
    ('last seen','last_seen'),
    ('times seen','times_seen'),
    ]    
    
specs['brandlock']['url_path'] = [
    ('url isbottom','url_isbottom'),
    ('url depth','url_depth'),
    ('url url','url_url'),
    ('url network','url_network'),
    ('url affiliate','url_affiliate'),
    ('url redirect delay','url_redirect_delay'),
    ('url redirect type','url_redirect_type'),
    ]
    
specs['brandlock']['affiliate'] = [
    ('advertiser url','advertiser_url'),
    ('ad provider','ad_provider'),
    ('num affiliates','num_affiliates'),
    ('avg rank','avg_rank'),
    ('times seen','times_seen'),
    ('pct affiliate ads','pct_affiliate_ads'),
    ]
    
specs['brandlock']['affiliate_details'] = [
    ('Competitor','advertiser_url'),
    ('url network','url_network'),
    ('url affiliate','url_affiliate'),
    ('ad title','ad_title'),
    ('ad text','ad_text'),
    ('ad display_url','ad_display_url'),
    ('ad provider','ad_provider'),
    ('keyword term','keyword_term'),
    ('avg rank','avg_rank'),
    ('first seen','first_seen'),
    ('last seen','last_seen'),
    ('times seen','times_seen'),               
    ]