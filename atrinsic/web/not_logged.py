from django.http import HttpResponse
from atrinsic.base.models import Organization, Countries, OrganizationContacts, WebRequest,Organization_IO, ProgramTermAction
from atrinsic import settings
from atrinsic.util.imports import *
from django.template import RequestContext


def advertisers(request, test=''):

    page_data = {}
    page_data["top_menu"] = "advertisers"
    return render_to_response("notlogged/advertisers.html",page_data, context_instance=RequestContext(request))

def publishers(request, test=''):

    page_data = {}
    page_data["top_menu"] = "publishers"
    return render_to_response("notlogged/publishers.html",page_data, context_instance=RequestContext(request))

def home(request, test=''):

    page_data = {}
    page_data["top_menu"] = "home"
    return render_to_response("notlogged/home.html",page_data, context_instance=RequestContext(request))

def agencies(request, test=''):

    page_data = {}
    page_data["top_menu"] = "agencies"
    return render_to_response("notlogged/agencies.html",page_data, context_instance=RequestContext(request))


def phil_test(request):
    import tempfile
    from atrinsic.base.models import Website
    from atrinsic.web.helpers import base36_encode
    from django.utils.encoding import smart_str
    from atrinsic.util.xls import write_rows
    
    file_id,file_path = tempfile.mkstemp()
	
    #date joined in PublisherRelationship
	
    res = [["Website ID","Encoded id","Website Url"]]
    qs = Website.objects.filter(publisher=1101)
    for row in qs:
        """dateJoined = smart_str(PublisherRelationship.objects.get(advertiser=request.organization, publisher=row, status = 3).date_accepted)
        if dateJoined == 'None':
            dateJoined = smart_str(PublisherRelationship.objects.get(advertiser=request.organization, publisher=row, status = 3).date_initiated)
            print '****** %s', dateJoined"""
        #base publisher relationship.. for Date Joined

        res.append([str(int(row.pk)),
                    str(base36_encode(int(row.pk))),
                    smart_str(row.url)])
    write_rows(file_path,res)
    print res
    res = open(file_path).read()
    
    response = HttpResponse(res,mimetype="application/vnd.ms-excel")
    response['Content-Disposition'] = 'attachment; filename=mypublishers.xls'
    return response