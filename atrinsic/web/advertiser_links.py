import os
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from atrinsic.util.imports import *
from atrinsic.web.helpers import format_initial_dict, base36_encode
from atrinsic.util.zip import build_creatives
from django.core.mail import send_mail
from django.core.mail import EmailMessage
import StringIO, csv
import tempfile
from atrinsic.util.ApeApi import Ape

# Navigation Tab to View mappings for the Advertiser Menu
tabset("Advertiser",2,"Manage Links","advertiser_links",
       [("Links","advertiser_links"),
        ("Upload Multiple",'advertiser_links_bulk'),
        ("Upload Images",'advertiser_links_creatives')])


@url(r"^links/$","advertiser_links")
@tab("Advertiser","Manage Links","Links")
@advertiser_required
@register_api(None)
def advertiser_links(request):
    ''' View that displays the current Links for this Advertiser '''
    from atrinsic.base.models import ProgramTerm, ProgramTermAction
    createProgramTerm = False
    
    try:
        cl = ProgramTerm.objects.get(advertiser=request.organization,is_default=True)
        try:
            ptAction = ProgramTermAction.objects.select_related("action").filter(program_term=cl)[0]
        except:
            return AQ_render_to_response(request, 'advertiser/links/not-configured.html', {
                'createProgramTerm':createProgramTerm,
            }, context_instance=RequestContext(request))
    except:
        return AQ_render_to_response(request, 'advertiser/links/not-configured.html', {
            'createProgramTerm':createProgramTerm,
        }, context_instance=RequestContext(request))
    
    if ProgramTerm.objects.filter(advertiser = request.organization).count() == 0:    	
        print "they have a program term"
        createProgramTerm = True
        
    return AQ_render_to_response(request, 'advertiser/links/index.html', {
        'createProgramTerm':createProgramTerm,
        }, context_instance=RequestContext(request))

#Function to create and update links on Ape system
#Only used for bulk atm. Can be changed to accept a PT and used for other link functions
#l is Link Object
def ape_links(request,l):
    from atrinsic.base.models import Link, ProgramTerm, ProgramTermAction
    
    cl = ProgramTerm.objects.get(advertiser=request.organization,is_default=True)
    ptAction = ProgramTermAction.objects.filter(program_term=cl).order_by('id')
    apeClient = Ape()
    
    if l.ape_url_id == None:
        for x in reversed(range(ptAction.count())):
            # Create original link first, then cycle down, linking as we go.
            if x == ptAction.count()-1:
                apeClient.execute_url_create(ptAction[x].action, l)     
            else:
                if request.organization.id in(853,2302):
                    ape_redirect = base36_encode(ptAction[x+1].action.ape_redirect_id)
                    landingPage = settings.APE_TRACKER_URL + ape_redirect + "/{{int_pubid}}/{{int_websiteid}}/?url_id=%s" % l.ape_url_id                    
                    apeClient.execute_redirect_chain(ptAction[x].action, l, landingPage)
    else:
        if request.organization.id not in(853,2302):
            apeClient.execute_url_update(ptAction[0], l)
    

@url(r"^links/bulk/$","advertiser_links_bulk")
@tab("Advertiser","Manage Links","Upload Multiple")
@advertiser_required
@register_api(None)
def advertiser_links_bulk(request):
    ''' View to handle the bulk uploading of Advertiser Links '''
    from forms import BulkUploadForm
    from atrinsic.util.xls import get_rows, write_rows
    from atrinsic.base.models import Link, LinkPromotionType
                        
    # POST - PROCESS UPLOAD DATA:
    if request.method == 'POST':
        
        # CREATE AND VALIDATE POST FORM:
        form = BulkUploadForm(request.POST, request.FILES)
        if form.is_valid():
            
            # OPEN AND READ DATA FROM UPLOADED FILE:
            file_id,file_path = tempfile.mkstemp()
            file_obj = open(file_path,"wb")
            file_obj.write(form.cleaned_data['bulk_file'].read())
            file_obj.close()
            
            # LOG SETUP: 
            errors = []
            status = []
            output = []
           
##### PROCESSING BULK DELETE LINK #####   
            if int(form.cleaned_data["upload_action"]) == 3: 
                row_num = 2
                
                # CYCLE ALL ROWS IN FILE:
                for row in get_rows(file_path)[1:]:
                    row_base = row[:]
                    
                    # NUMBER OF FIELDS CHECK:
                    if len(row) != 8:
                        errors.append("Wrong number of fields at row %s" % row_num)        
                    else:                
                        # EXTRACT EACH LINK ID AND DELETE THE ASSOCIATED LINK
                        start_date,end_date,link_name,landing_page_url,banner_url,link_content,link_id,promotion_type = row
                        try:
                            link_id = int(link_id)
                            link = request.organization.link_set.get(link_id=link_id)#Change the id. Must be converted
                            link.delete()
                            
                        # WRITE STATUS:
                            status.append("Link ID %s at row %s deleted" % (link_id,row_num))
                            
                        # WRITE ERROR:
                        except Link.DoesNotExist:
                            errors.append("Link ID %s at row %s does not exist" % (link_id,row_num))
                            
                    # WRITE DATA LOG ENTRY:
                    output.append(row)
                    row_num += 1
                    
##### PROCESSING BULK UPDATE LINK #####  
            if int(form.cleaned_data["upload_action"]) == 2:
                row_num = 2                             
                      
                # UPLOAD THE LINK INFORMATION TO ALL ACCEPTED PUBLISHER:
                if int(form.cleaned_data["upload_type"]) == 1:
                    
                    #CYCLE ALL ROWS:
                    for row in get_rows(file_path):
                        row_base = row[:]
                        
                        # CHECK FOR VALID ROW DATA:                       
                        if len(row) != 8:
                            errors.append("Wrong number of fields at row %s" % row_num)
                        else:
                            start_date,end_date,link_name,landing_page_url,banner_url,link_content,link_id,promotion_type = row
                            
                            # GET PROMOTION TYPE:
                            promotion_type_obj = None
                            if promotion_type and LinkPromotionType.objects.filter(name__iexact=promotion_type).count() > 0:
                                promotion_type_obj = LinkPromotionType.objects.get(name__iexact=promotion_type)
                            elif promotion_type:
                                errors.append("Promotion Type %s at row %s is invalid" % (promotion_type,row_num))
                            
                            # DEFAULT DATES IF NEEDED: 
                            if not start_date:
                                start_date = datetime.date.today()
                            if not end_date:
                                end_date = None
                                    
                            # VALIDATE LINK DATA:
                            if not link_name:
                                errors.append("Link Name at row %s is missing or invalid" % (row_num))
                            else:                                
                                # UPDATE LINK:
                                try:
                                    link = request.organization.link_set.get(link_id=link_id)
                                    if start_date:
                                        link.start_date = start_date
                                    if end_date:
                                        link.end_date = end_date
                                    if link_name:
                                        link.name = link_name
                                    if landing_page_url:
                                        link.landing_page_url = landing_page_url
                                    if banner_url:
                                        link.banner_url = banner_url
                                    if link_content:
                                        link.link_content = link_content
                                    if promotion_type_obj:
                                        link.link_promotion_type = promotion_type_obj
                                        
                                    link.save()
                                                              
                                    # APE FUNCTION:
                                    ape_links(request,link)
                                    
                                # WRITE STATUS:
                                    status.append("Link ID %s at row %s updated" % (link_id,row_num))
                                         
                                # WRITE ERROR:
                                except Link.DoesNotExist:
                                    errors.append("Link ID %s at row %s does not exist" % (link_id,row_num))
                                
                        # WRITE DATA LOG ENTRY:
                        output.append(row)
                        row_num += 1
                            
                # UPLOAD FOR INDIVIDUAL PUBLISHERS:
                else:
                    #CYCLE ALL ROWS:                    
                    for row in get_rows(file_path):
                        row_base = row[:]
                        
                        # CHECK FOR VALID ROW DATA:
                        if len(row) != 6:
                            errors.append("Wrong number of fields at row %s" % row_num)
                        else:
                            link_name,publisher_id,landing_page_url,banner_url,link_content,link_id = row
                            
                            # CHECK FOR VALID PUBLISHER INFORMATION:
                            try:
                                publisher_id = int(round(float(publisher_id)))
                                row_base[1] = publisher_id
                                pub = Organization.objects.get(org_type=ORGTYPE_PUBLISHER,website__id=publisher_id)
    
                                # UPDATE LINK:
                                try:
                                    link = request.organization.link_set.get(link_id=link_id)
                                    if link_name:
                                        link.name = link_name
                                    if landing_page_url:
                                        link.landing_page_url = landing_page_url
                                    if banner_url:
                                        link.banner_url = banner_url
                                    if link_content:
                                        link.link_content = link_content
                                    link.assigned_to = LINKASSIGNED_INDIVIDUAL
                                    link.assigned_to_individual = pub
                                    link.save()
                                    
                                    # APE FUNCTION:
                                    ape_links(request,link)
                                    
                                # WRITE STATUS:
                                    status.append("Link ID %s at row %s updated" % (link_id,row_num))
                                
                                # WRITE ERRORS:
                                except Link.DoesNotExist:
                                    errors.append("Link ID %s at row %s does not exist" % (link_id,row_num))                             
                            except:
                                errors.append("Publisher ID %s at row %s does not exist" % (publisher_id,row_num))      
                                
                        # WRITE DATA LOG ENTRY:
                        output.append(row)
                        row_num += 1
                 
##### PROCESSING BULK ADD LINK #####               
            # :
            else:
                row_num = 2             
                                      
                # UPLOAD THE LINK INFORMATION TO ALL ACCEPTED PUBLISHER:
                if int(form.cleaned_data["upload_type"]) == 1:
                
                    # CHECK LINK AVAILABLE QUANTITIES:
                    new_banner = 0
                    new_text = 0
                    
                    # CYCLE ALL ROWS:
                    for row in get_rows(file_path):                   
                        if len(row) != 8:
                            errors.append("Wrong number of fields at row %s" % row_num)
                        else:
                            start_date,end_date,link_name,landing_page_url,banner_url,link_content,link_id,promotion_type = row
                            
                            if banner_url:
                                new_banner += 1
                            else:
                                new_text += 1
                    
                    current_banner_total = Link.objects.filter(link_type=LINKTYPE_BANNER, advertiser=request.organization).count()
                    current_text_total = Link.objects.filter(link_type=LINKTYPE_TEXT, advertiser=request.organization).count()
                    
                    # CHECK TOTALS AGAINST MAXIMUMS:
                    if int(request.organization.allowed_banner) <= int(current_banner_total + new_banner) :
                        errors.append("The number of Banner Links exceeds the allowed maximum.")                        
                    if int(request.organization.allowed_text) <= int(current_text_total + new_text) :
                        errors.append("The number of Text Links exceeds the allowed maximum.")                    
                    else:                                
                        # ADD ALL LINKS IN FILE:
                        # CYCLE ALL ROWS:        
                        for row in get_rows(file_path): 
                            row_base = row[:]
                                     
                            # CHECK FOR REQUIRED INFORMATION:
                            if not banner_url and not link_content :
                                errors.append("Row %s does not have banner_url or link_content" % row_num)
                            elif not landing_page_url:
                                errors.append("Row %s does not have a landing_page_url" % row_num)
                            else:                                    
                                # DEFINE LINK TYPE
                                if banner_url:
                                    link_type = LINKTYPE_BANNER
                                else:
                                    link_type = LINKTYPE_TEXT
                                
                                # CREATE LINK AND SAVE:
                                try:
                                    link = Link.objects.create(advertiser=request.organization,link_type=link_type,
                                                               start_date=start_date,
                                                               end_date=end_date,
                                                               name=link_name,
                                                               landing_page_url = landing_page_url,
                                                               banner_url = banner_url,
                                                               link_content = link_content,
                                                               link_promotion_type=promotion_type_obj)
                                    link.save()
                                    
                                    # APE FUNCTION:
                                    ape_links(request,link)
                                    
                                    # WRITE STATUS:
                                    status.append("Link ID %s at row %s added" % (link.link_id,row_num))
                                    row_base[6] = link.link_id 
                                except:
                                    errors.append("Link creation at row %s failed." % (row_num))                                    
                                
                            # WRITE DATA LOG ENTRY:
                            output.append(row_base)
                            row_num += 1                 
                    
                # UPLOAD FOR INDIVIDUAL PUBLISHERS:
                else:                
                    # CHECK LINK AVAILABLE QUANTITIES:
                    new_banner = 0
                    new_text = 0
                    
                    # CYCLE ALL ROWS:
                    for row in get_rows(file_path):                   
                        if len(row) != 6:
                            errors.append("Wrong number of fields at row %s" % row_num)
                        else:
                            link_name,publisher_id,landing_page_url,banner_url,link_content,link_id = row
                            
                            if banner_url:
                                new_banner += 1
                            else:
                                new_text += 1
                    
                    current_banner_total = Link.objects.filter(link_type=LINKTYPE_BANNER, advertiser=request.organization).count()
                    current_text_total = Link.objects.filter(link_type=LINKTYPE_TEXT, advertiser=request.organization).count()
                    
                    # CHECK TOTALS AGAINST MAXIMUMS:
                    if int(request.organization.allowed_banner) <= int(current_banner_total + new_banner) :
                        errors.append("The number of Banner Links exceeds the allowed maximum.")                        
                    if int(request.organization.allowed_text) <= int(current_text_total + new_text) :
                        errors.append("The number of Text Links exceeds the allowed maximum.")                    
                    else:         
                        # ADD ALL LINKS IN FILE:
                        # CYCLE ALL ROWS:        
                        for row in get_rows(file_path):
                            row_base = row[:]
                                                
                            # CHECK FOR VALID PUBLISHER INFORMATION:
                            try:
                                publisher_id = int(round(float(publisher_id)))
                                row_base[1] = publisher_id
                                pub = Organization.objects.get(org_type=ORGTYPE_PUBLISHER,website__id=publisher_id)
                                
                                # CHECK FOR REQUIRED INFORMATION:
                                if not banner_url and not link_content:
                                    errors.append("Row %s does not have banner_url or link_content" % row_num)
                                elif not landing_page_url:
                                    errors.append("Row %s does not have a landing_page_url" % row_num)
                                else:
                                    # DEFINE LINK TYPE
                                    if banner_url:
                                        link_type = LINKTYPE_BANNER
                                    else:
                                        link_type = LINKTYPE_TEXT
            
                                    try:
                                        link = Link.objects.create(advertiser=request.organization,link_type=link_type,
                                                                   start_date=datetime.datetime.now(),
                                                                   end_date=None,
                                                                   name=link_name,
                                                                   landing_page_url = landing_page_url,
                                                                   banner_url = banner_url,
                                                                   link_content = link_content,
                                                                   assigned_to=LINKASSIGNED_INDIVIDUAL,
                                                                   assigned_to_individual = pub
                                                                   )
                                        link.save()
                                        
                                        # APE FUNCTION:
                                        ape_links(request,link)                      
                                        
                                        status.append("Link ID %s at row %s added" % (link.link_id,row_num))
                                        row_base[5] = link.link_id 
                                    # WRITE ERRORS:
                                    except:
                                        errors.append("Link creation at row %s failed." % (row_num))                               
                            except:
                                errors.append("Publisher ID %s at row %s does not exist" % (publisher_id,row_num))  
                
                            # WRITE DATA LOG ENTRY:
                            output.append(row_base)
                            row_num += 1
                                 
##### END PROCESSING #####
                            
            # WRITE LOG ENTRIES TO FILE:
            file_id,file_path = tempfile.mkstemp()
            res = []
            write_rows(file_path,output)            
            output_text = open(file_path).read()

            # EMAIL RESULTS OF THE MASS OPERATIONS:
            msg = EmailMessage('Bulk Upload Result',
                               """Here are the results of your recent bulk upload

# Successes: %s
# Failures: %s

Errors:
%s

""" % (len(status),len(errors),"\r\n\r\n".join(errors)),settings.SITE_CONTACT,[form.cleaned_data["confirmation_email"]])

            msg.attach('result.xls',output_text,'application/vnd.ms-excel')
            msg.send(fail_silently=True)
            return HttpResponseRedirect(reverse('advertiser_links'))
    else:
        form = BulkUploadForm()
    
    return AQ_render_to_response(request, 'advertiser/links/bulk.html', {
        'form':form,
        }, context_instance=RequestContext(request))


@url(r"^links/creatives/$", "advertiser_links_creatives")
@tab("Advertiser","Manage Links","Upload Images")
@advertiser_required
@register_api(api_context=('id', 'get_url', 'size', 'link_id', ))
def advertiser_links_creatives(request,page=None):
    ''' YYY: View to display and upload bulk AdvertiserImages '''
    from forms import AdvertiserImageForm,AdvertiserImageBulkForm
    from atrinsic.base.models import AdvertiserImage
    from atrinsic.util.list_detail import object_list
    
    if request.method == 'POST':
        form = AdvertiserImageForm(request.POST, request.FILES)
        bulk_form = AdvertiserImageBulkForm(request.POST, request.FILES)
        if form.is_valid():
            aimg = AdvertiserImage(image=form.cleaned_data['image'],
                                   advertiser=request.organization,
                                   )
                                                       
            name,extension = os.path.splitext(str(aimg.image.name))
            import random
            aimg.image.name = "%s_%s%s" % (aimg.advertiser.id,random.randint(0,1000),extension.lower())
            aimg.save()
            return HttpResponseRedirect(reverse('advertiser_links_creatives'))
        elif bulk_form.is_valid():
            file = request.FILES['file']
            creatives =  build_creatives(request.organization, file)
            if len(creatives) > 0:
                for c in creatives:
                    print c
                msg = EmailMessage('Bulk Image Upload Result',
                                   "\r\n".join(["""%s\t%s uploaded successfully\r\n""" % (ai.original_filename,ai.get_url()) for ai in creatives]),settings.SITE_CONTACT,[bulk_form.cleaned_data["confirmation_email"]])
                msg.send(fail_silently=True)

                return HttpResponseRedirect(reverse('advertiser_links_creatives'))
            else:
                bulk_form.errors['file'] = [u'Error processing file']

    else:
        form = AdvertiserImageForm()
        bulk_form = AdvertiserImageBulkForm()

    qs = request.organization.advertiserimage_set.all()
    return object_list(request, queryset=qs, allow_empty=True, page=page,
        template_name='advertiser/links/creatives.html', paginate_by=6,
        extra_context={
            'total_results' : qs.count(),
            'form': form,
            'bulk_form': bulk_form,
        },
    )


@url(r"^links/creatives/delete/(?P<id>\d+)/$","advertiser_links_creatives_delete")
@tab("Advertiser","Manage Links","Add Links")
@advertiser_required
@register_api(None)
def advertiser_links_delete(request, id):
    ''' View to delete an Advertiser Image '''
    from atrinsic.base.models import AdvertiserImage
    creative = get_object_or_404(AdvertiserImage, id=id, advertiser=request.organization)

    if creative.can_delete():
        creative.delete()

    return HttpResponseRedirect(reverse("advertiser_links_creatives"))


@url(r"^links/(?P<view>(text|keyword|banner|email|flash|html|rss))/$","advertiser_links_view")
@tab("Advertiser","Manage Links","Links")
@advertiser_required
@register_api(api_context=('id', 'get_banner_url', 'get_link_type_display', 'assignment',))
def advertiser_links_view(request, view='text', page=None):
    ''' View Specific Type of Links with links to manage them '''
    from atrinsic.base.models import Link
    from atrinsic.util.list_detail import object_list
    from datetime import datetime 
    from django.db.models import Q
    
    qs = Link.objects.filter(advertiser=request.organization).filter(Q(end_date__gte=datetime.now()) | Q(end_date = None))

    if view.lower() == 'banner':
        qs = qs.filter(link_type=LINKTYPE_BANNER)
        current_count = request.organization.current_link_count(LINKTYPE_BANNER)
        linkType = LINKTYPE_BANNER
        link_limit = request.organization.allowed_banner
    elif view.lower() == 'keyword':
        qs = qs.filter(link_type=LINKTYPE_KEYWORD)
        current_count = request.organization.current_link_count(LINKTYPE_KEYWORD)
        linkType = LINKTYPE_KEYWORD
        link_limit = request.organization.allowed_keyword
    elif view.lower() == 'flash':
        qs = qs.filter(link_type__in=[LINKTYPE_FLASH,LINKTYPE_AB])
        current_count = request.organization.current_link_count(LINKTYPE_FLASH)
        linkType = LINKTYPE_FLASH
        link_limit = request.organization.allowed_flash
    elif view.lower() == 'email':
        qs = qs.filter(link_type=LINKTYPE_EMAIL)
        current_count = request.organization.current_link_count(LINKTYPE_EMAIL)
        linkType = LINKTYPE_EMAIL
        link_limit = request.organization.allowed_email_link
    elif view.lower() == 'html':
        qs = qs.filter(link_type=LINKTYPE_HTML)
        current_count = request.organization.current_link_count(LINKTYPE_HTML)
        linkType = LINKTYPE_HTML
        link_limit = request.organization.allowed_html
    elif view.lower() == 'rss':
        qs = qs.filter(link_type=LINKTYPE_RSS)
        current_count = request.organization.current_link_count(LINKTYPE_RSS)
        linkType = LINKTYPE_RSS
        link_limit = request.organization.allowed_rss
    else:
        qs = qs.filter(link_type=LINKTYPE_TEXT)
        current_count = request.organization.current_link_count(LINKTYPE_TEXT)
        linkType = LINKTYPE_TEXT
        link_limit = request.organization.allowed_text
        
    if current_count >= link_limit:
        add_new = False
    else:
        add_new = True
    return object_list(request, queryset=qs, allow_empty=True, page=page,
            template_name='advertiser/links/view.html', extra_context={
                'total_results' : qs.count(),
                'view' : view,
                'add_new' : add_new,
                'linkType' : linkType,
                'hostPath' : settings.CDN_HOST_URL
            })
                            
@url(r"^links/add/textlink/$","advertiser_links_add_textlink")
@tab("Advertiser","Manage Links","Add Links")
@advertiser_required
@register_api(None)
def advertiser_links_add_textlink(request):
    ''' View to add an Advertiser TextLink '''
    from forms import TextLinkForm
    from atrinsic.base.models import Link,ProgramTerm,ProgramTermAction
    if request.method == "POST":
        form = TextLinkForm(request.organization, request.POST)
        if form.is_valid():
            l = Link(link_type=LINKTYPE_TEXT)
            l.advertiser = request.organization

            for k, v in form.cleaned_data.items():
                setattr(l, k, v)

            if int(form.cleaned_data["assigned_to"]) == int(LINKASSIGNED_PROGRAM_TERM):
                cl = form.cleaned_data['assigned_to_program_term']
            else:
                cl = ProgramTerm.objects.get(advertiser=request.organization,is_default=True)

            
            l.save()
            ptAction = ProgramTermAction.objects.filter(program_term=cl).order_by('id')

            apeClient = Ape()
            for x in reversed(range(ptAction.count())):
                # Create original link first, then cycle down, linking as we go.
                if x == ptAction.count()-1:
                    apeClient.execute_url_create(ptAction[x].action, l)     
                else:
                    if request.organization.id in(853,2302):
                        ape_redirect = base36_encode(ptAction[x+1].action.ape_redirect_id)
                        landingPage = settings.APE_TRACKER_URL + ape_redirect + "/{{int_pubid}}/{{int_websiteid}}/?url_id=%s" % l.ape_url_id                    
                        apeClient.execute_redirect_chain(ptAction[x].action, l, landingPage)     
            
            return HttpResponseRedirect(reverse("advertiser_links_view",args=["text"]))

    else:
        form = TextLinkForm(request.organization, initial={
                    'start_date' : datetime.date.today(),
                    'end_date' : datetime.date.today() + datetime.timedelta(days=365),
               })

    return AQ_render_to_response(request, 'advertiser/links/add-textlink.html', {
            'form' : form,
        }, context_instance=RequestContext(request))

@url(r"^links/add/rsslink/$","advertiser_links_add_rsslink")
@tab("Advertiser","Manage Links","Add Links")
@advertiser_required
@register_api(None)
def advertiser_links_add_rsslink(request):
    ''' View to add an Advertiser TextLink '''
    from forms import RssLinkForm
    from atrinsic.base.models import Link,ProgramTerm,ProgramTermAction
    if request.method == "POST":
        form = RssLinkForm(request.organization, request.POST)
        print form.is_valid()
        print form.errors
        if form.is_valid():
            l = Link(link_type=LINKTYPE_RSS)
            l.advertiser = request.organization

            for k, v in form.cleaned_data.items():
                setattr(l, k, v)

            if int(form.cleaned_data["assigned_to"]) == int(LINKASSIGNED_PROGRAM_TERM):
                cl = form.cleaned_data['assigned_to_program_term']
            else:
                cl = ProgramTerm.objects.get(advertiser=request.organization,is_default=True)

            l.save()
            ptAction = ProgramTermAction.objects.filter(program_term=cl).order_by('id')

            apeClient = Ape()
            for x in reversed(range(ptAction.count())):
                # Create original link first, then cycle down, linking as we go.
                if x == ptAction.count()-1:
                    apeClient.execute_url_create(ptAction[x].action, l)     
                else:
                    if request.organization.id in(853,2302):
                        ape_redirect = base36_encode(ptAction[x+1].action.ape_redirect_id)
                        landingPage = settings.APE_TRACKER_URL + ape_redirect + "/{{int_pubid}}/{{int_websiteid}}/?url_id=%s" % l.ape_url_id                    
                        apeClient.execute_redirect_chain(ptAction[x].action, l, landingPage)     
                        
            return HttpResponseRedirect(reverse("advertiser_links_view",args=["rss"]))
    else:
        form = RssLinkForm(request.organization, initial={
                    'start_date' : datetime.date.today(),
                    'end_date' : datetime.date.today() + datetime.timedelta(days=365),
               })

    return AQ_render_to_response(request, 'advertiser/links/add-rsslink.html', {
            'form' : form,
        }, context_instance=RequestContext(request))
        
@url(r"^links/add/htmllink/$","advertiser_links_add_htmllink")
@tab("Advertiser","Manage Links","Add Links")
@advertiser_required
@register_api(None)
def advertiser_links_add_htmllink(request):
    ''' View to add an Advertiser TextLink '''
    from forms import HtmlLinkForm
    from atrinsic.base.models import Link,ProgramTerm,ProgramTermAction
    if request.method == "POST":
        form = HtmlLinkForm(request.organization, request.POST)
        if form.is_valid():
            l = Link(link_type=LINKTYPE_HTML)
            l.advertiser = request.organization

            for k, v in form.cleaned_data.items():
                setattr(l, k, v)

            if int(form.cleaned_data["assigned_to"]) == int(LINKASSIGNED_PROGRAM_TERM):
                cl = form.cleaned_data['assigned_to_program_term']
            else:
                cl = ProgramTerm.objects.get(advertiser=request.organization,is_default=True)

            l.save()
            ptAction = ProgramTermAction.objects.filter(program_term=cl).order_by('id')

            apeClient = Ape()
            for x in reversed(range(ptAction.count())):
                # Create original link first, then cycle down, linking as we go.
                if x == ptAction.count()-1:
                    apeClient.execute_url_create(ptAction[x].action, l)     
                else:
                    if request.organization.id in(853,2302):
                        ape_redirect = base36_encode(ptAction[x+1].action.ape_redirect_id)
                        landingPage = settings.APE_TRACKER_URL + ape_redirect + "/{{int_pubid}}/{{int_websiteid}}/?url_id=%s" % l.ape_url_id                    
                        apeClient.execute_redirect_chain(ptAction[x].action, l, landingPage)     
                          
            return HttpResponseRedirect(reverse("advertiser_links_view",args=["html"]))
    else:
        form = HtmlLinkForm(request.organization, initial={
                    'start_date' : datetime.date.today(),
                    'end_date' : datetime.date.today() + datetime.timedelta(days=365),
               })

    return AQ_render_to_response(request, 'advertiser/links/add-htmllink.html', {
            'form' : form,
        }, context_instance=RequestContext(request))


@url(r"^links/add/emaillink/$","advertiser_links_add_emaillink")
@tab("Advertiser","Manage Links","Add Links")
@advertiser_required
@register_api(None)
def advertiser_links_add_emaillink(request):
    ''' View to add an Advertiser EmailLink '''
    from forms import EmailLinkForm
    from atrinsic.base.models import Link,ProgramTerm,ProgramTermAction
    if request.method == "POST":
        form = EmailLinkForm(request.organization, request.POST,request.FILES)
        if form.is_valid():
            l = Link(link_type=LINKTYPE_EMAIL)
            l.advertiser = request.organization

            for k, v in form.cleaned_data.items():
                setattr(l, k, v)
            
            if int(form.cleaned_data["assigned_to"]) == int(LINKASSIGNED_PROGRAM_TERM):
                cl = form.cleaned_data['assigned_to_program_term']
            else:
                cl = ProgramTerm.objects.get(advertiser=request.organization,is_default=True)
                                
            l.save()
            ptAction = ProgramTermAction.objects.filter(program_term=cl).order_by('id')

            apeClient = Ape()
            for x in reversed(range(ptAction.count())):
                # Create original link first, then cycle down, linking as we go.
                if x == ptAction.count()-1:
                    apeClient.execute_url_create(ptAction[x].action, l)     
                else:
                    if request.organization.id in(853,2302):
                        ape_redirect = base36_encode(ptAction[x+1].action.ape_redirect_id)
                        landingPage = settings.APE_TRACKER_URL + ape_redirect + "/{{int_pubid}}/{{int_websiteid}}/?url_id=%s" % l.ape_url_id                    
                        apeClient.execute_redirect_chain(ptAction[x].action, l, landingPage)     
        
            return HttpResponseRedirect(reverse("advertiser_links_view",args=["email"]))
    else:
        form = EmailLinkForm(request.organization, initial={
                    'start_date' : datetime.date.today(),
                    'end_date' : datetime.date.today() + datetime.timedelta(days=365),
               })

    return AQ_render_to_response(request, 'advertiser/links/add-emaillink.html', {
            'form' : form,
        }, context_instance=RequestContext(request))


@url(r"^links/add/flashlink/$","advertiser_links_add_flashlink")
@tab("Advertiser","Manage Links","Add Links")
@advertiser_required
@register_api(None)
def advertiser_links_add_flashlink(request):
    ''' View to Add an Advertiser FlashLink '''
    from forms import FlashLinkForm
    from atrinsic.base.models import Link,ProgramTerm,ProgramTermAction
    if request.method == "POST":
        form = FlashLinkForm(request.organization, request.POST, request.FILES)
        if form.is_valid():
            l = Link(link_type=LINKTYPE_FLASH)
            l.advertiser = request.organization

            for k, v in form.cleaned_data.items():
                setattr(l, k, v)        

            if int(form.cleaned_data["assigned_to"]) == int(LINKASSIGNED_PROGRAM_TERM):
                cl = form.cleaned_data['assigned_to_program_term']
            else:
                cl = ProgramTerm.objects.get(advertiser=request.organization,is_default=True)

            l.save()
            ptAction = ProgramTermAction.objects.filter(program_term=cl).order_by('id')

            apeClient = Ape()
            for x in reversed(range(ptAction.count())):
                # Create original link first, then cycle down, linking as we go.
                if x == ptAction.count()-1:
                    apeClient.execute_url_create(ptAction[x].action, l)     
                else:
                    if request.organization.id in(853,2302):
                        ape_redirect = base36_encode(ptAction[x+1].action.ape_redirect_id)
                        landingPage = settings.APE_TRACKER_URL + ape_redirect + "/{{int_pubid}}/{{int_websiteid}}/?url_id=%s" % l.ape_url_id                    
                        apeClient.execute_redirect_chain(ptAction[x].action, l, landingPage)     
            return HttpResponseRedirect('/advertiser/links/flash')
    else:
        form = FlashLinkForm(request.organization, initial={
                    'start_date' : datetime.date.today(),
                    'end_date' : datetime.date.today() + datetime.timedelta(days=365),
               })

    return AQ_render_to_response(request, 'advertiser/links/add-flashlink.html', {
            'form' : form,
        }, context_instance=RequestContext(request))


@url(r"^links/add/bannerlink/$","advertiser_links_add_bannerlink")
@tab("Advertiser","Manage Links","Add Links")
@advertiser_required
@register_api(None)
def advertiser_links_add_bannerlink(request):
    ''' View to add and upload an Advertiser Banner Link and Image '''
    from atrinsic.base.models import AdvertiserImage,ProgramTermAction,ProgramTerm,Link
    from forms import BannerLinkForm
    if request.method == 'POST':
        form = BannerLinkForm(request.organization, request.POST,request.FILES)
        if form.is_valid():
            error = False
            l = Link(link_type=LINKTYPE_BANNER)
            l.advertiser = request.organization

            for k, v in form.cleaned_data.items():
                setattr(l, k, v)
                
            try:
                if not form.cleaned_data['ad_image_id']:
                    ad_image_id = 0
                else:
                    ad_image_id = int(form.cleaned_data.get('ad_image_id', 0))
                if ad_image_id > 0:
                    img = AdvertiserImage.objects.get(id=ad_image_id, advertiser=request.organization)
                    l.banner = img
            except (AdvertiserImage.DoesNotExist, ValueError):
                form.errors['image'] = [u'You must select a previous image or upload a new one']
                error = True
        
            if not l.banner:
                img = form.cleaned_data.get('image', None)
                if img is None:
                    form.errors['image'] = [u'You must select a previous image or upload a new one']
                    error = True
                else:
                    l.banner = AdvertiserImage.objects.create(advertiser=request.organization,image=form.cleaned_data['image'])
            
            if int(form.cleaned_data["assigned_to"]) == int(LINKASSIGNED_PROGRAM_TERM):
                cl = form.cleaned_data['assigned_to_program_term']
            else:
                try:
                    cl = ProgramTerm.objects.get(advertiser=request.organization,is_default=True)
                except:
                    error = True
                       
            if not error:
                l.save()
                ptAction = ProgramTermAction.objects.filter(program_term=cl).order_by('id')
    
                apeClient = Ape()
                for x in reversed(range(ptAction.count())):
                    # Create original link first, then cycle down, linking as we go.
                    if x == ptAction.count()-1:
                        apeClient.execute_url_create(ptAction[x].action, l)     
                    else:
                        if request.organization.id in(853,2302):
                            ape_redirect = base36_encode(ptAction[x+1].action.ape_redirect_id)
                            landingPage = settings.APE_TRACKER_URL + ape_redirect + "/{{int_pubid}}/{{int_websiteid}}/?url_id=%s" % l.ape_url_id                    
                            apeClient.execute_redirect_chain(ptAction[x].action, l, landingPage)     		                
                return HttpResponseRedirect(reverse("advertiser_links_view",args=["banner"]))
    else:
        form = BannerLinkForm(request.organization, initial={
                    'start_date' : datetime.date.today(),
                    'end_date' : datetime.date.today() + datetime.timedelta(days=365),
                    'ad_image_id': 0,
               })

    return AQ_render_to_response(request, 'advertiser/links/add-bannerlink.html', {
            'form' : form,
        }, context_instance=RequestContext(request))


@url(r"^links/banners/list/(?P<id>[\w]+)/$", "advertiser_links_edit_banner_list")
@advertiser_required
@register_api(None)
def advertiser_links_banner_list(request, id):
    ''' View of an ADvertisers Banner Link List '''
    from atrinsic.base.models import Link, AdvertiserImage

    l = Link.objects.get(link_id=id)
    
    return AQ_render_to_response(request, 'advertiser/links/edit-banner-list.html', {
        'banners': request.organization.advertiserimage_set.filter(banner_size=l.banner.banner_size),
        }, context_instance=RequestContext(request))

@url(r"^links/banners/list/$", "advertiser_links_banner_list")
@advertiser_required
@register_api(None)
def advertiser_links_banner_list(request):
    ''' View of an ADvertisers Banner Link List '''

    return AQ_render_to_response(request, 'advertiser/links/banner-list.html', {
        'banners': request.organization.advertiserimage_set.all(),
        }, context_instance=RequestContext(request))


@url(r"^links/add/keywordlink/$","advertiser_links_add_keywordlink")
@tab("Advertiser","Manage Links","Add Links")
@advertiser_required
@register_api(None)
def advertiser_links_add_keywordlink(request):
    ''' View to add an Advertiser Keyword Link '''
    from atrinsic.base.models import AdvertiserImage,ProgramTermAction,ProgramTerm,Link
    from forms import KeywordLinkForm
    global_err = ''
    if request.method == "POST":
        form = KeywordLinkForm(request.organization, request.POST)
        if form.is_valid():
            l = Link(link_type=LINKTYPE_KEYWORD)
            l.advertiser = request.organization

            for k, v in form.cleaned_data.items():
                setattr(l, k, v)

            l.save()

            if int(form.cleaned_data["assigned_to"]) == int(LINKASSIGNED_PROGRAM_TERM):
                cl = form.cleaned_data['assigned_to_program_term']
            else:
                cl = ProgramTerm.objects.get(advertiser=request.organization,is_default=True)
            
            l.save()
            ptAction = ProgramTermAction.objects.filter(program_term=cl).order_by('id')

            apeClient = Ape()
            for x in reversed(range(ptAction.count())):
                # Create original link first, then cycle down, linking as we go.
                if x == ptAction.count()-1:
                    apeClient.execute_url_create(ptAction[x].action, l)     
                else:
                    if request.organization.id in(853,2302):
                        ape_redirect = base36_encode(ptAction[x+1].action.ape_redirect_id)
                        landingPage = settings.APE_TRACKER_URL + ape_redirect + "/{{int_pubid}}/{{int_websiteid}}/?url_id=%s" % l.ape_url_id                    
                        apeClient.execute_redirect_chain(ptAction[x].action, l, landingPage)            
                
            return HttpResponseRedirect(reverse("advertiser_links_view",args=["keyword"]))
        else:
            print form.non_field_errors
            global_err = form.errors
    else:
        form = KeywordLinkForm(request.organization, initial={
                    'start_date' : datetime.date.today(),
                    'end_date' : datetime.date.today() + datetime.timedelta(days=365),
               })

    return AQ_render_to_response(request, 'advertiser/links/add-keywordlink.html', {
            'form' : form,
            'global_err' : global_err
        }, context_instance=RequestContext(request))


@url(r"^links/edit/(?P<id>[\w]+)/$","advertiser_links_edit")
@tab("Advertiser","Manage Links","Add Links")
@advertiser_required
@register_api(None)
def advertiser_links_edit(request, id):
    ''' View to edit Advertiser Links.  Form is determined based on the type
    of link being edited, as part of the URL '''
    from atrinsic.base.models import Link,AdvertiserImage,ProgramTerm,ProgramTermAction
    from forms import KeywordLinkForm,TextLinkForm,HtmlLinkForm,FlashLinkForm,editFlashLinkForm,EmailLinkForm,BannerLinkForm,RssLinkForm
    
    link = get_object_or_404(Link, link_id=id, advertiser=request.organization)
    template = 'advertiser/links/edit-bannerlink.html'
    if link.link_type == LINKTYPE_KEYWORD:
        form_type = KeywordLinkForm
        template = 'advertiser/links/edit-keywordlink.html'
        var_link_type = 'keyword'
    elif link.link_type == LINKTYPE_TEXT:
        form_type = TextLinkForm
        template = 'advertiser/links/edit-textlink.html'
        var_link_type = 'text'
    elif link.link_type == LINKTYPE_HTML:
        form_type = HtmlLinkForm
        template = 'advertiser/links/edit-htmllink.html'
        var_link_type = 'html'
    elif link.link_type == LINKTYPE_RSS:
        form_type = RssLinkForm
        template = 'advertiser/links/edit-rsslink.html'
        var_link_type = 'html'
    elif link.link_type == LINKTYPE_FLASH:
        form_type = editFlashLinkForm
        template = 'advertiser/links/edit-flashlink.html'
        var_link_type = 'flash'    
    elif link.link_type == LINKTYPE_AB:
        form_type = editFlashLinkForm
        template = 'advertiser/links/edit-flashlink.html'
        var_link_type = 'flash'
    elif link.link_type == LINKTYPE_EMAIL:
        form_type = EmailLinkForm
        template = 'advertiser/links/edit-emaillink.html'
        var_link_type = 'email'
    elif link.link_type == LINKTYPE_BANNER:
        form_type = BannerLinkForm
        template = 'advertiser/links/edit-bannerlink.html'
        var_link_type = 'banner'
        if link.banner != None:
            try:
                orig_size = (link.banner.image.width, link.banner.image.height)
            except:
                orig_size = None
        else:
            orig_size = None
    else:
        raise Http404

    if request.method == "POST":
        form = form_type(request.organization, request.POST,request.FILES, is_edit=True)
        error = False

        if form.is_valid():
            #raise SyntaxError,form.cleaned_data.items()
            for k, v in form.cleaned_data.items():     
                setattr(link, k, v)
                

            if link.link_type == LINKTYPE_BANNER:
                img = form.cleaned_data.get('image', None)
                if img != None:        
                    link.banner = AdvertiserImage.objects.create(advertiser=request.organization,image=form.cleaned_data['image'])
                else:
                    try:
                        if not form.cleaned_data['ad_image_id']:
                            ad_image_id = 0
                        else:
                            ad_image_id = int(form.cleaned_data.get('ad_image_id', 0))
                        if ad_image_id > 0:
                            img = AdvertiserImage.objects.get(id=ad_image_id, advertiser=request.organization)
                            if img.size() == link.banner.size():
                                link.banner = img
                            else:
                                form.errors['banner_url'] = [u'You must select an image with the same dimensions as the previous image']
                    except (AdvertiserImage.DoesNotExist, ValueError):
                        form.errors['image'] = [u'You must select a previous image or upload a new one']
                        error = True   
                    
            if int(form.cleaned_data["assigned_to"]) == int(LINKASSIGNED_PROGRAM_TERM):
                cl = form.cleaned_data['assigned_to_program_term']
            else:
                cl = ProgramTerm.objects.get(advertiser=request.organization,is_default=True)
            
            ptAction = ProgramTermAction.objects.select_related("action").filter(program_term=cl)[0]
            updateApeUlrId = False
            
            apeClient = Ape()
            if link.ape_url_id == None:
                apeClient.execute_url_create(ptAction.action, link)
            else:
                if request.organization.id not in(853,2302):
                    apeClient.execute_url_update(ptAction, link)

            if not form.errors and not error:
                link.save()
                return HttpResponseRedirect('/advertiser/links/'+str(var_link_type)+'/')
            else:
                return AQ_render_to_response(request, template, {
                        'form' : form,
                        'link' : link,
                    }, context_instance=RequestContext(request))
    else:        
        init = format_initial_dict(link.__dict__)
        if link.link_type == LINKTYPE_BANNER and link.banner:
            init['ad_image_id'] = link.banner.id

        form = form_type(
            request.organization,
            initial=init,
            is_edit=True,
        )
    
    return AQ_render_to_response(request, template, {
            'form' : form,
            'link' : link,
        }, context_instance=RequestContext(request))

@url(r"^links/delete/(?P<id>[\w]+)/$","advertiser_links_delete")
@tab("Advertiser","Manage Links","Add Links")
@advertiser_required
@register_api(None)
def advertiser_links_delete(request, id):
    ''' View to delete a specific Link '''
    from atrinsic.base.models import Link
    link = get_object_or_404(Link, link_id=id, advertiser=request.organization)

    link.delete()

    '''
    LINKTYPE_NONE = 0
    LINKTYPE_BANNER = 1
    LINKTYPE_TEXT = 2
    LINKTYPE_KEYWORD = 3
    LINKTYPE_FLASH = 4
    LINKTYPE_EMAIL = 5
    LINKTYPE_HTML = 6
    LINKTYPE_RSS = 7
    '''
    return HttpResponseRedirect(reverse('advertiser_links'))


@url(r"^links/download_banners/(?P<link_type>[0-9]+)/$","download_banners")
@tab("Advertiser","Manage Links","Links")
@advertiser_required
def download_banners(request,link_type):
    from atrinsic.base.models import Link
    from atrinsic.util.xls import write_rows
    import tempfile
    
    file_id,file_path = tempfile.mkstemp()
    
    res = [["Link ID","Name","Size","Assigned To","Landing Page URL"]]
    banners = Link.objects.filter(advertiser=request.organization,link_type=link_type)
    
    size = ""
    
    for row in banners:
        if link_type == "1":
            if row.banner != None:
                size = row.banner.size()
        res.append([str(int(row.ape_url_id)),
                        str(row.name),
                        str(size),
                        str(row.get_assignment()),
                        str(row.landing_page_url)])
                        
    write_rows(file_path,res)
    res = open(file_path).read()
    
    response = HttpResponse(res,mimetype="application/vnd.ms-excel")
    response['Content-Disposition'] = 'attachment; filename=links.xls'

    return response
    
    #response = render_to_response("misc/links/dataxls_%s.html" % link_type, {'banners': banners,})
    #filename = "misc/links/download.xls"                
    #response['Content-Disposition'] = 'attachment; filename='+filename
    #response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
    #return HttpResponse(str(banners[0].banner.image))
    #return response
    
#Turn on or off DeepLinking    
@url(r"^links/deeplinking/(?P<state>\d+)/$","advertiser_deeplinking")
@tab("Advertiser","Manage Links","Add Links")
@advertiser_required
@register_api(None)
def advertiser_deeplinking(request, state):
    ''' set adbuilder feature on or off '''
    from atrinsic.base.models import AdvertiserImage, Organization

    org = Organization.objects.get(id = request.organization.pk)    

    if state == "0":
        org.adbuilder = False
    else:    
        org.adbuilder = True
        
    org.save()

    return HttpResponseRedirect('/advertiser/links')

#AD BUILDER ---------------------------------------------------------------------
@url(r"^links/adbuilder/preview/(?P<ad_id>\d+)/$", "advertiser_adbuilder_preview")
def advertiser_adbuilder_preview(request,ad_id):
    
    return AQ_render_to_response(request, 'advertiser/links/adbuilderpreview.html', {
            'template' : ad_id,
        }, context_instance=RequestContext(request))
        
@url(r"^links/adbuilder/advadbuilder/(?P<ad_id>\d+)/$", "advertiser_adbuilder_advanced")
@tab("Advertiser","Manage Links","Links")
@advertiser_required
def advertiser_adbuilder_advanced(request,ad_id):
    
    template = ad_id
    
    return AQ_render_to_response(request, 'advertiser/links/adbuilderadv.html', {
            'template' : template,
            'org' : request.organization.id,
            'path' : settings.CDN_HOST + 'adbuilder/'  
        }, context_instance=RequestContext(request))
        
@url(r"^links/adbuilder/templates/$", "advertiser_adbuilder_templates")
@tab("Advertiser","Manage Links","Links")
@advertiser_required
def advertiser_adbuilder_templates(request):
    from atrinsic.base.models import AdbuilderTemplates
    from django.core.paginator import Paginator, InvalidPage, EmptyPage
    
    template_list =  AdbuilderTemplates.objects.all()
    paginator = Paginator(template_list, 1)
    
    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
        
    # If page request (9999) is out of range, deliver last page of results.
    try:
        templates = paginator.page(page)
    except (EmptyPage, InvalidPage):
        templates = paginator.page(paginator.num_pages)

    return AQ_render_to_response(request, 'advertiser/links/adbuildertemps.html', {
            'templates' : templates,  
        }, context_instance=RequestContext(request))        

#START OF ADBUILDER 2 FLASH APP
#This is to create the config file
@url(r"^links/adbuilder/createad/$", "advertiser_adbuilder_createAd")
def advertiser_adbuilder_createAd(request):   
    from atrinsic.base.models import Link,ProgramTerm,ProgramTermAction,Organization
   
    tempid = request.POST['templateId']
    adv = request.POST['advertiser']
    #path = "C:/adbuilderNew/adbuilder/adbuilder/configs/advertisers/" + request.POST['advertiser'] + "/" + request.POST['templateId'] + "/"
    path = "/mnt/nfs/adquotient/user_images/adbuilder/configs/advertisers/" + adv + "/" + tempid + "/" 
    fileName = "1.xml"
    
    print "cjecking path: " + path
    if os.path.isdir(path):
        print os.listdir(path)
        print len(os.listdir(path))
        confId = str(len(os.listdir(path)) + 1)
        fileName = confId + ".xml"
        print fileName 
    else:
        os.makedirs(path)
      
    path = path + fileName		
    f = open(path, 'w')
    f.write(request.POST["config"])
    
    link = tempid + "/" + tempid + ".swf?adv=" + adv + "&conf=" + confId
    
    try:
        #Need to add all the tracking elements  _-_-_-__-_-_-__-_-_------___--__--__--
        advert = Organization.objects.get(id=adv)
        l = Link(link_type=LINKTYPE_AB)
        l.advertiser = advert
        l.name = request.POST['linkname']
        l.landing_page_url = request.POST['landingpage']
        l.swf_file = link
        l.save()
    
        print "link saved"
        
        cl = ProgramTerm.objects.get(advertiser=advert,is_default=True)
        ptAction = ProgramTermAction.objects.filter(program_term=cl).order_by('id')

        apeClient = Ape()
        for x in reversed(range(ptAction.count())):
            # Create original link first, then cycle down, linking as we go.
            if x == ptAction.count()-1:
                apeClient.execute_url_create(ptAction[x].action, l)     
            else:
                if adv in(853,2302):
                    ape_redirect = base36_encode(ptAction[x+1].action.ape_redirect_id)
                    landingPage = settings.APE_TRACKER_URL + ape_redirect + "/{{int_pubid}}/{{int_websiteid}}/?url_id=%s" % l.ape_url_id                    
                    apeClient.execute_redirect_chain(ptAction[x].action, l, landingPage)       
                        
    except Exception, e:
        print str(e)
    
    #---------------------------------------------------------------------------------------------------
    return HttpResponse(link, mimetype="text/html")
    
@url(r"^links/adbuilder/img/(?P<adv_id>\d+)/$", "advertiser_adbuilder_img")
def advertiser_adbuilder_img(request, adv_id):
    import xml.dom.minidom
    import Image
    #print request.FILES
    #print request.POST.get("Upload", None)
    #for name,f in request.FILES:
    myfile = request.FILES['Filedata']

    path = "/mnt/nfs/adquotient/user_images/adbuilder/configs/advertisers/" + adv_id + "/imgs/"
    #Check if folder exists, if not create
    if not os.path.exists(path):
        os.makedirs(path)
        os.makedirs(path + '/thumbs')
        file = open(path + 'lib.xml', 'w')
        file.write('<?xml version="1.0" ?><lib><images></images></lib>')
        file.close()

        
    #1- Write uploaded img(binary) to path    
    try:
        destination = open(path + myfile.name, 'wb')
        for chunk in myfile.chunks():
            destination.write(chunk)
        destination.close()
    except:
        print "error creating Image"
        
    #2- Create a thubnail of that image
    try:
        image = Image.open(path + myfile.name, 'r')
        width = image.size[0]
        height = image.size[1]
        image = image.resize((60, 60), Image.ANTIALIAS)
        image.save(path + 'thumbs/t_' + myfile.name )
    except:
        print "Error creating thumbnail"
    
    
    #3- Adding new file to lib.xml
    try:
        doc = xml.dom.minidom.parse(path + "lib.xml")
        image = doc.getElementsByTagName("images")[0]
        newtag = doc.createElement("img")
        newtag.setAttribute("w", str(width))
        newtag.setAttribute("h", str(height))
        txt = doc.createTextNode(myfile.name)
        newtag.appendChild(txt)
        image.appendChild(newtag)
         
        f = open(path + "lib.xml", "w")
        doc.writexml(f)
        f.close()
    except:
        print "xml error"        
    
    try:    
        xml = "<image><w>"
        xml += str(width)
        xml += "</w><h>"
        xml += str(height)
        xml += "</h></image>"
        print xml 
    except:
         print "problem" 
        
    return HttpResponse(xml, mimetype="text/xml")

def createThumbnail(path,fileName):
    import Image
    image = Image.open(path + fileName)
    image = image.resize((60, 60), Image.ANTIALIAS)
    image.save(path + 'thumbs/t_' + fileName )
    
#This will be the new get Lib
@url(r"^links/adbuilder/getLib/(?P<adv_id>\d+)/$", "advertiser_adbuilder_getLib")
def advertiser_adbuilder_getLib(request, adv_id):   
    import os
    import xml.dom.minidom
    print "sending Lib"
    
    from os.path import join, dirname, abspath
    from os import environ, sep

    #path = 'C:/adbuilderNew/adbuilder/adbuilder/configs/advertisers/' + adv_id +'/imgs/lib.xml'
    path = os.path.join("/mnt/nfs/adquotient/user_images/adbuilder",'configs','advertisers',adv_id,'imgs','lib.xml')
    
    print path
    
    if os.path.exists(path):
        libxml = xml.dom.minidom.parse(path)
        libxml = libxml.toxml()
    else:
        libxml = '<lib></lib>'	
        
    response =  HttpResponse(libxml, mimetype="text/xml")
    response['Cache-Control'] = 'no-cache'
    return response   

@url(r"^links/adbuilder/delImg/(?P<adv_id>\d+)/(?P<fileName>.*)/$", "advertiser_adbuilder_delImg")
def advertiser_adbuilder_delImg(request, adv_id,fileName):
    import os
    import xml.dom.minidom
    from os.path import join, dirname, abspath
    from os import environ, sep

    print adv_id
    print fileName
    #path = "C://adbuilder/configs/advertisers/" + adv_id + "/imgs/"
    path = os.path.join("/mnt/nfs/adquotient/user_images/adbuilder",'configs','advertisers',adv_id,'imgs','lib.xml')
    
    doc = xml.dom.minidom.parse(path)
    images = doc.getElementsByTagName("img")
    for node in images:
        if node.firstChild.data == fileName:
            node.parentNode.removeChild(node)
            
    f = open(path, "w")
    doc.writexml(f)
    f.close()    
    
    response = "<result>success</result>"
    
    return HttpResponse(response, mimetype="text/xml")

@url(r"^links/adbuilder/cleanImgs/(?P<adv_id>\d+)/$", "advertiser_adbuilder_cleanImgs")
def advertiser_adbuilder_cleanImgs(request, adv_id):
    import os
    import fnmatch
    import xml.dom.minidom
    
    path = "C://adbuilder/configs/advertisers/" + adv_id + "/imgs/" 
    
    doc = xml.dom.minidom.parse(path + "lib.xml")
    images = doc.getElementsByTagName("img")
    
    dirList=os.listdir(path)
    
    for fname in dirList:
        if os.path.isfile(path + fname):
            if not fnmatch.fnmatch ( path + fname, '*.xml' ):
                found = False
                for node in images:
                    if node.firstChild.data == fname:
                        found = True
                       
                if found:
                     print fname + " was found in xml"
                else:
                     print fname + " was not found in xml"
                     try:
                        os.remove(path + fname)
                        print "File Deleted"
                     except:	        
                        print "could not delete file"
    

    #os.remove(path + "thumbs/t_" +  fileName + "." + ext)
    
    response = "<result>success</result>"
    
    return HttpResponse(response, mimetype="text/xml")
    