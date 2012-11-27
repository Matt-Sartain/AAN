#Author: 	Michel Page
#date:		02/10/2010

class CustomLinks(object):
    
    #key is to identify witch advertiser we are requesting information for
    
    def __init__(self):
        #do nothing
        print "Class instantiated"
                
    def generate_link(self,advertiser,link):
        from atrinsic.base.models import Link
        newlink = ""
        print advertiser
        if advertiser == "Kayak.com":
            lp = link.landing_page_url
            
            domain = lp.partition('.com/')
            
            newlink = (domain[0] + domain[1] + "in?ai=atrinsic&p={{url_id}}%2F{{int_websiteid}}%2F{{int_pubid}}&url=/" + domain[2])
        
        return newlink        
        