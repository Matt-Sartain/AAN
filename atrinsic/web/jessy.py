#from django.contrib.auth import authenticate
#from django.contrib.auth import login as django_login
#from django.contrib.auth import logout as django_logout
from django.shortcuts import render_to_response
#from django.template import RequestContext
#from django.template.defaultfilters import slugify
#from django.db.models.query import QuerySet
#from atrinsic.web.helpers import base36_encode
#from atrinsic.util.AceApi import createPO 

#CRITICAL IMPORTS
from atrinsic.util.imports import *
import xml.dom.minidom

@url(r"^$","jessy")
@register_api(None)
def jessy(request):
    output = """
            <p>You have found my test page congrats</p>
            <ul>
                <li><a href="/jessy/xml_test/">create xml test</a></li>
            </ul>
            """
    return HttpResponse(html(output))


@url("xml_test/","jessy_xml_test")
@register_api(None)
def jessy_xml_test(request):
    from atrinsic.base.models import KenshooDataFeed_Orders
    from atrinsic.base.models import Organization
    from atrinsic.base.models import Website
    import datetime
    now = datetime.datetime.now()
    
    # Var for output
    output = ""
    
    # Create the minidom document
    doc = xml.dom.minidom.Document()
    
    # Create the <advertiser_commission_report> base element
    kenshoo = doc.createElement("advertiser_commission_report")
    doc.appendChild(kenshoo)
    
    
    # Get the data so we can fill the xml object
    data = KenshooDataFeed_Orders.objects.all()
    
    for r in data:
        """
        Using a custom function called makeTag, it takes in 4 params.
        First is the xml.dom.minidom.Document() in this case its called doc.
        Second is the root element (Kenshoo in this case) the the name of the
        tag you want to create and its text field. an example :
        makeTag(doc,kenshoo,"ID",r.id)
        """
        makeTag(doc,kenshoo,"Posting_Date",now.strftime("%m/%d/%Y %H:%M:%S %p"))# <Posting_Date> tag eg: <Posting_Date>10/18/2009 03:35:46 PM</Posting_Date> # date and time the file pulled
        makeTag(doc,kenshoo,"Event_Date",r.datein)# <Event_Date> tag eg: <Event_Date>09/18/2009 11:19:05 AM</Event_Date> # order date
        makeTag(doc,kenshoo,"ID",r.id)# <ID> tag eg: <ID>948751638</ID>    # Internal Atrinsic Order ID
        makeTag(doc,kenshoo,"Action_Name",None)# <Action_Name> tag eg: <Action_Name>Atrinsic Advanced Sale I</Action_Name> # date and time file pulled
        makeTag(doc,kenshoo,"Type",None)# <Type> tag eg: <Type>item_sale</Type> # not included yet
        makeTag(doc,kenshoo,"Status",None)# <Status> tag eg: <Status>locked</Status>  # not included yet
        makeTag(doc,kenshoo,"Corrected",None) # <Corrected> tag eg: <Corrected>13.898</Corrected># If there is a value That need to be dedcuted/corrected for a certain conversion
        makeTag(doc,kenshoo,"Sale_Amount",r.amount)# <Sale_Amount> tag eg: <Sale_Amount>19.99</Sale_Amount> # amount
        makeTag(doc,kenshoo,"Order_Discount",None) # <Order_Discount>0.00</Order_Discount>
        makeTag(doc,kenshoo,"Publisher_Commission",None)   # <Publisher_Commission>-12.354</Publisher_Commission>
        makeTag(doc,kenshoo,"CJ_Fee",None) # <CJ_Fee></CJ_Fee>
        makeTag(doc,kenshoo,"Publisher_ID",r.publisher_id)# <Publisher_ID>2534039</Publisher_ID>
        orgData = Organization.objects.filter(id=r.publisher_id)# <Publisher_Name>crealytics GmbH</Publisher_Name>
        makeTag(doc,kenshoo,"Publisher_Name",orgData[0].company_name)
        makeTag(doc,kenshoo,"Website_ID",r.url_id)# <Website_ID>3228744</Website_ID>
        webData = Website.objects.filter(id=r.website_id)
        makeTag(doc,kenshoo,"Website_Name",webData[0].url)# <Website_Name>crealytics</Website_Name>
        makeTag(doc,kenshoo,"Link_ID",webData[0].id) # <Link_ID>10273706</Link_ID>
        makeTag(doc,kenshoo,"Order_ID",r.order_id)# <Order_ID>73964770</Order_ID>
        makeTag(doc,kenshoo,"Action_ID",None) # <Action_ID>320540</Action_ID>
        makeTag(doc,kenshoo,"Ad_Owner_Advertiser_ID",r.advertiser_id)# <Ad_Owner_Advertiser_ID>276652</Ad_Owner_Advertiser_ID>
        makeTag(doc,kenshoo,"click_date",None) #from click log on APE tracklist...? # <click_date>08/13/2009 09:31:50 AM</click_date>
        

    #output for displaying the xml (for testing)
    output += "<strong>XML Output</strong> :\n"
    output += "<hr />\n"
    preview = str(doc.toxml()).replace("<","\n&lt;")
    preview = str(preview).replace(">","&gt;")
    output += "<pre>"+preview+"</pre>"
    output += "<hr />\n"
    output += "<br/><br/><br/><br/><a href=\"..\\\">Go Back</a>"
    
    
    #Writting the file to disk
    import os.path
    filename = now.strftime("%Y%m%d%H%M%S")
    FILE = open(filename,"w")
    FILE.writelines(doc.toxml()) 
    FILE.close()
    
    return HttpResponse(html(output))


def makeTag(docObj,rootObj,tagName,tagText):
    """
    This takes the tag name and text creates a tag with the minidom object and
    returns the tag so it can be added.
    """
    try:
        tag = docObj.createElement(tagName)
        tag_text = docObj.createTextNode(toString(tagText))
        tag.appendChild(tag_text)
        rootObj.appendChild(tag)
    except Exception, e:
        raise e


def toString(val):
    """
    check val if None return empty string, else return a string
    """
    if val == None :
        return ""
    else :
        return str(val)

# this is used to simply have valid pages for my output
def html(data):
    html = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
    <html>
        <head>
            <title>Jessy's Test pages</title>
            <meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
        </head>
        <body>"""
    html += data
    html += """</body>
    </html>"""
    return html