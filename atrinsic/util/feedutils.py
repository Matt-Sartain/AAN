from atrinsic.base.models import *
from atrinsic.util.date import *
from django.conf import settings

from django.utils.encoding import smart_str, smart_unicode

import os

import csv,StringIO

import xls

def input_feedformat(format,data):
    if format == DATAFEEDFORMAT_CSV:
        reader = csv.reader(StringIO.StringIO(data))
        output = []
        for row in reader:
            output.append(row)
        return output

    if format == DATAFEEDFORMAT_PIPEDELIM:
        reader = csv.reader(StringIO.StringIO(data),delimiter="|")
        output = []
        for row in reader:
            output.append(row)
        return output

    if format == DATAFEEDFORMAT_TABDELIM:
        reader = csv.reader(StringIO.StringIO(data),delimiter="\t")
        output = []
        for row in reader:
            output.append(row)
        return output

    if format == DATAFEEDFORMAT_EXCEL:
        return get_rows_string(data)


def output_feedformat(format,data):
    if format == DATAFEEDFORMAT_CSV:
        print "DATAFEEDFORMAT_CSV"
        output = StringIO.StringIO()
        writer = csv.writer(output)
        for d in data:
            writer.writerow([unicode(d[0]),unicode(d[1]),unicode(d[2]),unicode(d[3]),unicode(d[4]),unicode(d[5]),unicode(d[6])])

        return output.getvalue()

    if format == DATAFEEDFORMAT_PIPEDELIM:
        print "DATAFEEDFORMAT_PIPEDELIM"
        output = StringIO.StringIO()
        writer = csv.writer(output,delimiter="|")
        writer.writerows(data)
        return output.getvalue()

    if format == DATAFEEDFORMAT_TABDELIM:
        print "DATAFEEDFORMAT_TABDELIM"
        output = StringIO.StringIO()
        writer = csv.writer(output,delimiter="\t")
        writer.writerows(data)
        return output.getvalue()

    if format == DATAFEEDFORMAT_EXCEL:
        print "DATAFEEDFORMAT_EXCEL"
        return write_rows_string(data)

    

def grab_datafeed(datafeed,prefix):
	# they push to us, file lives in settings.localftp_root / <organization_id> / *.files
    if datafeed.datafeed_type == DATAFEEDTYPE_FTPPUSH: 
        directory = os.path.join(settings.LOCALFTP_ROOT,str(datafeed.advertiser.id))
        if os.path.exists(directory) == False:
            raise Exception,"Directory %s doesn't exist" % directory

        files = []
        for filename in os.listdir(directory):
            if filename.lower().startswith(prefix.lower()):
                fn = os.path.join(directory,filename)
                files.append((os.path.getmtime(fn),fn))
            
        files.sort()
        files.reverse()
        if len(files) == 0:
            return None
        
        return open(files[0][1],"rb").read()

    if datafeed.datafeed_type == DATAFEEDTYPE_FTPPULL: # we pull from them
        import ftplib
        if datafeed.server.find(":") != -1:
            server,port = datafeed.server.split(":")
        else:
            server = datafeed.server
            port = 21
        ftp = ftplib.FTP(server,datafeed.username,datafeed.password,port=port)
        files = []
        for filename in ftp.nlst():
            if filename.lower().startswith(prefix.lower()):
                files.append(filename)

        if len(files) == 0:
            return None

        fn = files[-1]
        output = StringIO.StringIO()
        ftp.retrbinary("RETR %s" % fn,output.write)
        return output.getvalue()

    if datafeed.datafeed_type == DATAFEEDTYPE_HTTP: # we pull from them
        import urllib2,base64

        req = urllib2.Request(datafeed.server)

        base64string = base64.encodestring(
            '%s:%s' % (datafeed.username, datafeed.password))[:-1]
        authheader =  "Basic %s" % base64string
        req.add_header("Authorization", authheader)
        
        return urllib2.urlopen(req).read()
        

def put_datafeed(datafeed,data,filename):
    
    strDeliminator = ""
    if datafeed.datafeed_format == DATAFEEDFORMAT_CSV:
        strDeliminator = ""
    if datafeed.datafeed_format == DATAFEEDFORMAT_PIPEDELIM:
        strDeliminator = "|"
    if datafeed.datafeed_format == DATAFEEDFORMAT_TABDELIM:
        strDeliminator = "\t"
    if datafeed.datafeed_type == DATAFEEDTYPE_FTPPUSH: # we push to them
        import ftplib
        if datafeed.server.find(":") != -1:
            server,port = datafeed.server.split(":")
        else:
            server = datafeed.server
            port = 21
        
        ftp = ftplib.FTP()

        ftp.connect(server,int(port))
        ftp.login(datafeed.username,datafeed.password)
        ftp.storbinary("STOR %s" % filename,StringIO.StringIO(data))

    if datafeed.datafeed_type == DATAFEEDTYPE_FTPPULL: # they pull from us
        directory = os.path.join(settings.LOCALFTP_ROOT,str(datafeed.publisher.id))
        writer = csv.writer(open(os.path.join(directory,filename),"wb"), delimiter=strDeliminator)
        writer.writerows(data)
        

        """
            Code to output CSV file, along with the CSV extension. May be needed in future.
            createCSV = csv.writer(open(os.path.join (sendToNetworkSharePath, newFilename), "wb"), delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            createCSV.writerow([eachRow[0], base36_decode(eachRow[1]), base36_decode(eachRow[2]), base36_decode(eachRow[3]), eachRow[4], eachRow[5], eachRow[6]])
        """

    if datafeed.datafeed_type == DATAFEEDTYPE_EMAIL: # we email to them
        datafeed.publisher.send_email(EMAILTYPE_ADVERTISER_MESSAGE,
                                      "Your data feed from %s" % datafeed.advertiser.name,
                                      settings.SITE_CONTACT,
                                      "Attached is your data feed",
                                      "Attached is your data feed",
                                      (filename,data))
                                      




def load_productlist(datafeed, data):
    
    #data = grab_datafeed(datafeed,"apl_")
    #if data:
    lines = input_feedformat(datafeed.datafeed_format,data)
    
    header = lines[1]
    
    url_id = GetUrlID(lines)
    rec_RemoveHeaders(lines)   
    
    print "Headers - %s" % header
    pl = ProductList.objects.create(advertiser = datafeed.advertiser, url_id = datafeed.ape_url_id)

    for line in lines[1:]:
        fields = {}

        for i in range(0,len(header)):
            head_v = header[i]
            field_v = line[i]                    
            if field_v == "":
                field_v = "0"
            fields[head_v.lower()]  = unicode(field_v, errors='ignore')

        ProductItem.objects.create(product_list=pl,
                                   **fields)

    for i in ProductList.objects.filter(advertiser=datafeed.advertiser):
        i.active=False
        i.save()
    pl.active=True
    pl.save()
    for i in ProductList.objects.filter(advertiser=datafeed.advertiser,active=False):
        i.delete()
            
def GetUrlID(fileContents):
    for line in fileContents:
        for l in line:
            if l.find("&", 0, 1) > -1:
                if l.find("&url_id") > -1:
                    # Parse any and all header values.
                    curRow = l.lstrip("&")
                    var_name,var_value = curRow.split("=")
                    return var_value
    return 0

def rec_RemoveHeaders(fileContents):
    intCounter = 0 
    for line in fileContents:
        for l in line:
            if l.find("&", 0, 1) > -1:
                fileContents.pop(intCounter)
                rec_RemoveHeaders(fileContents)
    intCounter += 1	
    
    
def save_productlist(datafeed):

    # get productlist    
    pls = ProductList.objects.filter(advertiser=datafeed.advertiser,active=True)

    if len(pls) == 0:
        return

    data = []
    ct = 0
    website = datafeed.publisher.get_default_website()

    if not website:
        return
    
    for pl in pls:
        ct += 1

    data.append(["NAME","KEYWORDS","DESCRIPTION","SKU","BUYURL","AVAILABLE","IMAGEURL","PRICE","RETAILPRICE","SALEPRICE","CURRENCY","UPC","PROMOTIONALTEXT","ADVERTISERCATEGORY","MANUFACTURER","MANUFACTURERID","ISBN","AUTHOR","ARTIST","PUBLISHER","TITLE","LABEL","FORMAT","SPECIAL","GIFT","THIRDPARTYID","THIRDPARTYCATEGORY","OFFLINE","ONLINE","FROMPRICE","STARTDATE","ENDDATE","INSTOCK","CONDITION","WARRANTY","STANDARDSHIPPINGCOST","MERCHANDISETYPE","SKULIST","SKUCOMMISSIONLEVEL","SALESRANK"])
    
    for prod in pl.productitem_set.all():

        buyurl = pl.get_product_url(datafeed,pls[0],prod.buyurl,website)

        data.append([smart_str(prod.name),
                     smart_str(prod.keywords),
                     smart_str(prod.description),
                     prod.sku,
                     buyurl,
                     prod.available,
                     prod.imageurl,
                     prod.price,
                     prod.retailprice,
                     prod.saleprice,
                     prod.currency,
                     prod.upc,
                     prod.promotionaltext,
                     prod.advertisercategory,
                     prod.manufacturer,
                     prod.manufacturerid,
                     prod.isbn,
                     prod.author,
                     prod.artist,
                     prod.publisher,
                     prod.title,
                     prod.label,
                     prod.format,
                     prod.special,
                     prod.gift,
                     prod.thirdpartyid,
                     prod.thirdpartycategory,
                     prod.offline,
                     prod.online,
                     prod.fromprice,
                     prod.startdate,
                     prod.enddate,
                     prod.instock,
                     prod.condition,
                     prod.standardshippingcost,
                     prod.merchandisetype,                         
                     prod.sku_list,
                     prod.sku_commission_level,
                     prod.sales_rank
                     ])
        
    #string_data = output_feedformat(datafeed.datafeed_format,data)
    if datafeed.datafeed_format == DATAFEEDFORMAT_CSV:
        filename = "%s-%s-DataFeed.csv" % (datafeed.advertiser.name,ct)
    elif datafeed.datafeed_format == DATAFEEDFORMAT_PIPEDELIM:
        filename = "%s-%s-DataFeed.txt" % (datafeed.advertiser.name,ct)
    elif datafeed.datafeed_format == DATAFEEDFORMAT_TABDELIM:
        filename = "%s-%s-DataFeed.txt" % (datafeed.advertiser.name,ct)
    elif datafeed.datafeed_format == DATAFEEDFORMAT_EXCEL:
        filename = "%s-%s-DataFeed.xls" % (datafeed.advertiser.name,ct)
        
    datafeed.status = 0
    datafeed.save()
    put_datafeed(datafeed,data,filename)
        

from atrinsic.web.reports import *
def send_datatransfer(datatransfer):

    date_start,date_end = compute_date_range(REPORTTIMEFRAME_YESTERDAY)

    aids = Organization.objects.filter(publisher_relationships__status=RELATIONSHIP_ACCEPTED,
                                       publisher_relationships__publisher=datatransfer.publisher)
    
                                       
    report = DataTransfer_OrderReport(date_start,date_end,datatransfer.publisher,spec=REPORTTYPE_DATATRANSFER_ORDERREPORT,
                         advertiser_set=aids)

    data = []
    data.append([x[0] for x in report.RenderHeader()])
    contents = report.RenderContents()
    print contents
    for line in contents:
        print line
        data.append([x for x in line])


    string_data = output_feedformat(datatransfer.format,data)
    if datatransfer.format == DATAFEEDFORMAT_CSV:
        filename = "%s.csv" % datatransfer.publisher.name
    elif datatransfer.format == DATAFEEDFORMAT_PIPEDELIM:
        filename = "%s.txt" % datatransfer.publisher.name
    elif datatransfer.format == DATAFEEDFORMAT_TABDELIM:
        filename = "%s.txt" % datatransfer.publisher.name

    put_datatransfer(datatransfer,string_data,filename)


        
def put_datatransfer(datatransfer,data,filename):
    if datatransfer.datafeed_type == DATAFEEDTYPE_EMAIL: # we email to them
        print "DATAFEEDTYPE_EMAIL"
        datatransfer.publisher.send_email(EMAILTYPE_ADVERTISER_MESSAGE,
                                          "Your data transfer from Atrinsic",
                                          settings.SITE_CONTACT,
                                          "Attached is your data transfer",
                                          "Attached is your data transfer",
                                          (filename,data))
                                          
    elif datatransfer.datafeed_type == DATAFEEDTYPE_FTPPUSH:
        print "DATAFEEDTYPE_FTPPUSH"
        import ftplib
        ftp = ftplib.FTP()

        ftp.connect(datatransfer.server,int(21))
        ftp.login(datatransfer.username,datatransfer.password)
        ftp.storbinary("STOR %s" % filename,StringIO.StringIO(data))    
        # Close FTP Socket
        ftp.quit()

    elif datatransfer.datafeed_type == DATAFEEDTYPE_FTPPULL: 
        print "DATAFEEDTYPE_FTPPULL"
        directory = os.path.join(settings.LOCALFTP_ROOT,str(datatransfer.publisher.id))
        if os.path.exists(directory) == False:
            os.makedirs(directory)

        createFile = open(os.path.join (settings.LOCALFTP_ROOT,str(datatransfer.publisher.id), filename), "wb")
        for eachRow in data:
            createFile.write(str(eachRow))
                                      
        createFile.close()                                     