import os, tempfile
from django.template import RequestContext
from atrinsic.web.helpers import format_initial_dict
from atrinsic.util.zip import build_creatives
from atrinsic.util.imports import *

# Navigation Tab to View mappings for the Publisher Links Menu
tabset("Publisher",2,"Links","publisher_links",
       [("text", "publisher_links_text"),
        ("banner", "publisher_links_banner"),
        ("flash", "publisher_links_flash"),
        ("keyword", "publisher_links_keyword"),
        ("email", "publisher_links_email"),
        ("html", "publisher_links_html"),
        ("rss", "publisher_links_rss"),
        ])

@url(r"^links/banner/$", "publisher_links_banner")
def publisher_links_banner(request, link_type=None):
    '''("adbuilder", "publisher_links_adbuilder"),'''
    return publisher_links(request, 'banner');

@url(r"^links/text/$", "publisher_links_text")
def publisher_links_text(request, link_type=None):
    return publisher_links(request, 'text');
    
@url(r"^links/html/$", "publisher_links_html")
def publisher_links_html(request, link_type=None):
    return publisher_links(request, 'html');

@url(r"^links/keyword/$", "publisher_links_keyword")
def publisher_links_keyword(request, link_type=None):
    return publisher_links(request, 'keyword');

@url(r"^links/flash/$", "publisher_links_flash")
def publisher_links_flash(request, link_type=None):
    return publisher_links(request, 'flash');

@url(r"^links/email/$", "publisher_links_email")
def publisher_links_email(request, link_type=None):
    return publisher_links(request, 'email');

@url(r"^links/rss/$", "publisher_links_rss")
def publisher_links_rss(request, link_type=None):
    return publisher_links(request, 'rss');	
    
@url(r"^links/$","publisher_links")
@url(r"^links/(?P<link_type>(text|banner|keyword|flash|email|html|rss|all))/$", "publisher_links")
@tab("Publisher","Links","Links")
@register_api(api_context=('id', 'name', 'link_type', 'advertisers', ))
@publisher_required
def publisher_links(request, link_type='text'):
    ''' View to display and manage a Publisher's Links.  This View had multiple
        resultsets based on the type of link determined by the URL.  Additionally
        a POST variable 'advertiser_id' can be defined to limit the resultset
        to that of specific Advertisers. '''

    from forms import GetBannerLinkForm, GetTextLinkForm, GetKeywordLinkForm, GetHtmlLinkForm, GetFlashLinkForm, GetEmailLinkForm, GetRssLinkForm, adbuilderForm, GetLinkWebsiteForm
    from atrinsic.base.models import Organization
    from datetime import datetime 
    from django.db.models import Q
    
    link_choices = [ 'banner', 'text', 'keyword', 'email', 'flash', 'html', 'rss', 'all']
    links = [ ]
    form = { }
    found = False
    if link_type:
        if request.method == "POST" or request.GET.get("advertiser_id",None) or request.GET.get("promotion_id",None):                       
            links = request.organization.available_links().filter(start_date__lte=datetime.now()).filter(Q(end_date__gte=datetime.now()) | Q(end_date = None))
            if request.POST.getlist("vertical"):
                if request.POST.getlist('vertical')[0] != '-1':
                    links = links.filter(advertiser__vertical__order__in=request.POST.getlist('vertical'))
                    print request.POST.getlist('vertical')
            if request.GET.get("advertiser_id",None):
                links = links.filter(advertiser=request.GET.get("advertiser_id"))
            if request.POST.get("promotion_id",None):
                links = links.filter(link_promotion_type=request.GET.get("promotion_id"))
            if link_type == 'banner':
                form = GetBannerLinkForm(request.organization, request.POST)

                if form.is_valid():
                    if form.cleaned_data.get("size",None):
                        links = links.filter(banner__banner_size__order__in=form.cleaned_data["size"])
                    links = links.filter(link_type=LINKTYPE_BANNER)
                    
            elif link_type == 'keyword':
                form = GetKeywordLinkForm(request.organization, request.POST)
           
                if form.is_valid():
                    if form.cleaned_data.get("allow_third_party_email_campaigns",None):
                        links = links.filter(advertiser__allow_third_party_email_campaigns=form.cleaned_data['allow_third_party_email_campaigns'])
                    if form.cleaned_data.get("allow_direct_linking_through_ppc",None):
                        links = links.filter(advertiser__allow_direct_linking_through_ppc=form.cleaned_data['allow_direct_linking_through_ppc'])
                    if form.cleaned_data.get("allow_trademark_bidding_through_ppc",None):
                        links = links.filter(advertiser__allow_trademark_bidding_through_ppc=form.cleaned_data['allow_trademark_bidding_through_ppc'])

                    links = links.filter(link_type=LINKTYPE_KEYWORD)
                    
            elif link_type == 'text':
                form = GetTextLinkForm(request.organization, request.POST)
                if form.is_valid():
                    promotions = form.cleaned_data.get('link_promotion_type')
                    if "-1" not in promotions and promotions != [ ]:
                        links = links.filter(link_promotion_type__order__in=form.cleaned_data["link_promotion_type"])
                    verticals = form.cleaned_data.get('vertical')
                    if "-1" not in verticals and len(verticals) > 0:
                        links = links.filter(advertiser__vertical__order__in=verticals)
            
                    links = links.filter(link_type=LINKTYPE_TEXT)   
                
            elif link_type == 'html':
                form = GetHtmlLinkForm(request.organization, request.POST)
                if form.is_valid():
                    promotions = form.cleaned_data.get('link_promotion_type')
                    if "-1" not in promotions and promotions != [ ]:
                        links = links.filter(link_promotion_type__order__in=form.cleaned_data["link_promotion_type"])
                    verticals = form.cleaned_data.get('vertical')
                    if "-1" not in verticals and len(verticals) > 0:
                        links = links.filter(advertiser__vertical__order__in=verticals)
            
                    links = links.filter(link_type=LINKTYPE_HTML)
                    
            elif link_type == 'flash':
                form = GetFlashLinkForm(request.organization, request.POST)
                if form.is_valid():
                    links = links.filter(link_type__in=[LINKTYPE_FLASH,LINKTYPE_AB])

            elif link_type == 'email':
                form = GetEmailLinkForm(request.organization, request.POST)
                if form.is_valid():
                    links = links.filter(link_type=LINKTYPE_EMAIL)
            elif link_type == 'rss':
                form = GetRssLinkForm(request.organization, request.POST)
                if form.is_valid():
                    links = links.filter(link_type=LINKTYPE_RSS)
                
            elif link_type == 'all':
                pass
            else:
                raise Http404

            #if form.cleaned_data.get("vertical") != None:
            if link_type != 'all' and form.is_valid():
                verticals = form.cleaned_data.get('vertical')
                print verticals
                if "-1" not in verticals and len(verticals) > 0:
                    links = links.filter(advertiser__vertical__order__in=verticals)

            if link_type == 'all' or form.is_valid():
                found = True
                
            
            
        else:
            print "ELSE"
            print link_type
            if link_type == 'banner':
                form = GetBannerLinkForm(organization=request.organization)
                print form
            elif link_type == 'keyword':
                form = GetKeywordLinkForm(organization=request.organization)
            elif link_type == 'email':
                form = GetEmailLinkForm(organization=request.organization)
            elif link_type == 'text':
                form = GetTextLinkForm(organization=request.organization)
            elif link_type == 'flash':
                form = GetFlashLinkForm(organization=request.organization)
            elif link_type == 'html':
                form = GetHtmlLinkForm(organization=request.organization)
            elif link_type == 'rss':
                form = GetRssLinkForm(organization=request.organization)
            else:
                raise Http404

    
    if found:
        if link_type == 'all':
            view = ""
            if request.GET.get("view",None):
                view = request.GET.get("view",None)
            return object_list(request,queryset=links,allow_empty=True,page=None,
                template_name='publisher/links/show_all.html',paginate_by=1000, extra_context={
                    'found': found,
                'form' : form,
                'websiteform': GetLinkWebsiteForm(request.organization),
                'link_choices' :link_choices[:-1],
                'link_type' : link_type,
                'img_path' : settings.CDN_HOST_URL,	       
                'view' : view, 
                })
        print "!!!!!!!"
        return object_list(request,queryset=links,allow_empty=True,page=None,
            template_name='publisher/links/show_results.html',paginate_by=1000, extra_context={
                'found': found,
            'form' : form,
            'link_choices' :link_choices[:-1],
            'link_type' : link_type,
            'img_path' : settings.CDN_HOST_URL,	        
            })

    else:
        print "@@@@@@@"
        print form
        from django.db import connection
        return object_list(request,queryset=links,allow_empty=True,page=None,
                           template_name='publisher/links/index.html',paginate_by=1000, extra_context={
                   'found': found,
                   'form' : form,
                   'link_choices' :link_choices[:-1],
                   'link_type' : link_type,
                   'img_path' : settings.CDN_HOST_URL,
                   })


@url(r"^links/view/(?P<id>[0-9]+)/$","publisher_links_view")
@tab("Publisher","Links","Links")
@publisher_required
@register_api(None)
def publisher_links_view(request, id=None):
    ''' View to display details on a Publishers Link '''
    from atrinsic.base.models import AdvertiserImage, Link, Website
    from forms import GetLinkWebsiteForm
    
    link = get_object_or_404(Link, id=id)
    website = None
    form = None
    multiSites = False

    #retrieving publisher websites
    if Website.objects.filter(publisher=request.organization).count() > 1: 
        if request.method == 'POST':
            form = GetLinkWebsiteForm(request.organization, request.POST)
            if form.is_valid():
                website = get_object_or_404(Website, id=form.cleaned_data['website'])
                form = None
                multiSites = True
        else:
            form = GetLinkWebsiteForm(request.organization, request.POST)
    else:
        website = request.organization.get_default_website()
  
    bannerPreview = ""
    if website:
        track_html = link.track_html_ape(website)
        if track_html == None:
            track_html = "There is no link to display."
        
        #Previews for all link types        
        if link.link_type == 1:
            print "TESTING LINK_TYPE1"
            if link.banner == None:
                bannerPreview = link.banner_url
                if bannerPreview == '':                        
                    bannerPreview = settings.CDN_HOST_URL + str(link.banner.image)
            else:
                bannerPreview = settings.CDN_HOST_URL + str(link.banner.image)
        if link.link_type == 2:
            bannerPreview = link.link_content   
        if link.link_type == 4:
            bannerPreview = "<embed src='http://cdn.network.atrinsic.com/" + str(link.swf_file) + "' width='"+str(link.swf_width)+"' height='"+str(link.swf_height)+"' quality='high' allowScriptAccess='sameDomain' allowFullScreen='false' type='application/x-shockwave-flash' pluginspage='http://www.adobe.com/go/getflashplayer' />"
        if link.link_type == 6:    
            bannerPreview = link.track_html_ape(website,noImp=True)    
            #print bannerPreview
                     
    else:
        track_html = "Please add a Web Site before attempting to get a link"
    
    print form
    view = ""
    if request.GET.get("view",None):
        view = request.GET.get("view",None)
    return AQ_render_to_response(request, 'publisher/links/view.html', {
            'link' : link,
            'bannerPreview' : bannerPreview,
            'form' : form,
            'track_html': track_html,
            'multi_sites': multiSites,
            'view' : view,
            #'track_html_ape': track_html_ape,
        }, context_instance=RequestContext(request))


@url(r"^links/preview_link/(?P<id>[0-9]+)/$","publisher_links_preview")
@publisher_required
@register_api(None)
def publisher_links_preview(request, id=None):
    ''' View to display details on a Publishers Link '''
    from atrinsic.base.models import AdvertiserImage, Link, Website
    from forms import GetLinkWebsiteForm
    
    link = get_object_or_404(Link, id=id)
    website = None
    form = None
    multiSites = False


    website = request.organization.get_default_website()
  
    bannerPreview = ""
    if website:
        track_html = link.track_html_ape(website)
        if track_html == None:
            track_html = "There is no link to display."
        
        #Previews for all link types        
        if link.link_type == 1:
            if link.banner == None:
                bannerPreview = link.banner_url
            else:
                bannerPreview = settings.CDN_HOST_URL + str(link.banner.image)
        if link.link_type == 2:
            bannerPreview = link.link_content   
        if link.link_type == 4:
            bannerPreview = "<embed src='http://cdn.network.atrinsic.com/" + str(link.swf_file) + "' width='"+str(link.swf_width)+"' height='"+str(link.swf_height)+"' quality='high' allowScriptAccess='sameDomain' allowFullScreen='false' type='application/x-shockwave-flash' pluginspage='http://www.adobe.com/go/getflashplayer' />"
        if link.link_type == 6:    
            bannerPreview = link.track_html_ape(website,noImp=True)    
            #print bannerPreview
                     
    else:
        track_html = "Please add a Web Site before attempting to get a link"
    
    print form
    view = ""
    if request.GET.get("view",None):
        view = request.GET.get("view",None)
    return AQ_render_to_response(request, 'publisher/links/preview_link.html', {
            'track_html': track_html,
        }, context_instance=RequestContext(request))
        
@url(r"^links/view/pub/(?P<id>[0-9]+)/(?P<pubid>[0-9]+)/(?P<hash>[a-z0-9]+)/$","publisher_links_pubview")
def publisher_links_pubview(request, id=None,pubid=None,hash=None):
    ''' View to display details on a Publishers Link. This is a public link that can be reached without logging in'''
    from atrinsic.base.models import Link, Organization, AdvertiserImage

    pub = get_object_or_404(Organization, id=pubid)
    link = get_object_or_404(Link, id=id)

    if hash != pub.generate_link_hash(link):
        raise Http404
    
    website = pub.get_default_website()
    if website:            
        track_html = link.track_html_ape(website)
        
        #Previews for all link types        
        if link.link_type == 1:
            if link.banner == None:
                bannerPreview = link.banner_url
            else:
                bannerPreview = settings.CDN_HOST_URL + str(link.banner.image)
        if link.link_type == 2:
            bannerPreview = link.link_content   
        if link.link_type == 4:
            bannerPreview = "<embed src='http://cdn.network.atrinsic.com/" + str(link.swf_file) + "' width='"+str(link.swf_width)+"' height='"+str(link.swf_height)+"' quality='high' allowScriptAccess='sameDomain' allowFullScreen='false' type='application/x-shockwave-flash' pluginspage='http://www.adobe.com/go/getflashplayer' />"
        if link.link_type == 6:    
            bannerPreview = link.track_html_ape(website,noImp=True)    
            #print bannerPreview
    else:
        track_html = "Please add a Web Site before attempting to get a link"

    return AQ_render_to_response(request, 'publisher/links/view.html', {
            'link' : link,
            'bannerPreview': bannerPreview,
            'track_html':track_html,
        }, context_instance=RequestContext(request))


@url("^links/download/$","publisher_links_download")
@publisher_required
@register_api(None)
def publisher_links_download(request):
    ''' View to download Publishers Links '''
    from atrinsic.util.xls import write_rows
    import tempfile
    
    filename = None

    try:
        link_ids = request.REQUEST.getlist('link_id')
    except:
        link_ids = []

    qs = request.organization.available_links().filter(id__in=link_ids)
    default_website = request.organization.get_default_website()

    file_id,file_path = tempfile.mkstemp()
    res = [["Link ID", "Link Type", "Link Name", "Link Copy", "Link" ]]
        
    for l in qs:
        if filename is None:
            filename = '%s.xls' % l.get_link_type_display()

        res.append([ str(l.link_id),
             str(l.get_link_type_display()),
             str(l.name),
             str(l.link_content),
             str(l.track_text(default_website))
                   ])

    if filename is None:
        filename = 'links.xls'

    write_rows(file_path,res)
    res = open(file_path).read()

    response = HttpResponse(res,mimetype="application/vnd.ms-excel")
    response['Content-Disposition'] = 'attachment; filename=%s' % filename

    return response

@url("^links/download/suppression/(?P<link_id>\d+)/$","publisher_links_download_suppression")
@publisher_required
@register_api(None)
def publisher_links_download_suppression(request, link_id):
    
    from atrinsic.base.models import Link
    
    l = get_object_or_404(Link, id=link_id)

    if l.suppression_list is None:
        raise Http404
    
        
    res = open(l.suppression_list.path).read()

    response = HttpResponse(res,mimetype="application/vnd.ms-excel")
    response['Content-Disposition'] = 'attachment; filename=suppression.xls' 
   
    return response
    
@url(r"^links/testpubids/$", "publisher_links_adbuilder")
@publisher_required
def publisher_links_adbuilder(request):
    '''@tab("Publisher","Links","Links")'''
    from forms import adbuilderForm
    from atrinsic.base.models import Organization,PublisherRelationship
    from atrinsic.util.xls import write_rows
    import tempfile
    from atrinsic.web.helpers import base36_encode 
    
    pubs =  PublisherRelationship.objects.filter(advertiser='711')
    res = [["pub id", "encrypted"]]
    
    file_id,file_path = tempfile.mkstemp()
    filename = 'pubs.xls'
    
    for p in pubs:
        res.append([str(p.publisher.pk),str(base36_encode(p.publisher.pk))])
    
    write_rows(file_path,res)
    res = open(file_path).read()

    response = HttpResponse(res,mimetype="application/vnd.ms-excel")
    response['Content-Disposition'] = 'attachment; filename=%s' % filename

    return response

#START OF DEEP Linking FUNCTIONS#
@url("^links/build/$","publisher_links_build")
@publisher_required
@register_api(None)
@tab("Publisher","Links","Links")
def publisher_links_build(request):
    from atrinsic.base.models import Link,ProgramTerm,ProgramTermAction,Organization
    from forms import adbuilderForm
    from atrinsic.util.ApeApi import Ape
    from atrinsic.util.links.CustomLinks import CustomLinks
    
    try:
        adv = Organization.objects.get(id=request.POST['advertisers'])
        cl = CustomLinks()
        
        if request.POST['linkId'] == "0":
            l = Link(link_type=LINKTYPE_TEXT)
        else:
            l = Link.objects.get(id=request.POST['linkId'])	    
        
        l.byo = True
        l.advertiser = adv
        l.publisher = request.organization
        l.name = request.POST['name']
        l.landing_page_url = request.POST['destination']
        l.landing_page = request.POST['destination']
        l.link_content = request.POST['content']
        
        pt = ProgramTerm.objects.get(advertiser=adv,is_default=True)
        ptAction = ProgramTermAction.objects.select_related("action").get(program_term=pt)
        apeClient = Ape()
        
        #Create custom landing page if needed
        lp = cl.generate_link(adv.name,l)
        if lp != "":
            l.landing_page_url = lp
        
        #Create APE tracking
        if request.POST['linkId'] == "0":
            apeClient.execute_url_create(ptAction.action, l)            
        else:
            apeClient.execute_url_update(ptAction, l)
        
        l.save()
        link_id = l.id
        
        result = "Your link was created successfully"
    except:
        result = "A problem accoured while creating your link. Please contact your system administrator"
        
    return HttpResponse(str(link_id), mimetype="text/html")
    
    
    '''
    return HttpResponseRedirect("/publisher/links/adbuilder/%s" %link_id)
    return HttpResponse(str(link_id), mimetype="text/html")
    
    return AQ_render_to_response(request, 'publisher/links/adbuilder.html', {
            'link' : link,
            'form' : form,
            'link_type' : 'adbuilder',
            'track_html' : track_html, 
        }, context_instance=RequestContext(request))
    '''  

@url(r"^links/deeplinking/$", "publisher_links_deeplinking")
@publisher_required
def publisher_links_deeplinking(request):
    '''@tab("Publisher","Links","Links")'''
    from forms import adbuilderForm
    from atrinsic.base.models import Organization,Link
    
    form = adbuilderForm(request.organization)
    pub = request.organization
    links =  Link.objects.filter(byo=True,publisher=pub)
    
    return AQ_render_to_response(request, 'publisher/links/deeplinking.html', {
            'links' : links,
            'form' : form,
            'link_id' : '0',
            'link_type' : 'adbuilder',

        }, context_instance=RequestContext(request))
                
@url(r"^links/deeplinking/(?P<link_id>\d+)/$", "publisher_edit_custom")
@tab("Publisher","Links","Links")
@publisher_required
def publisher_edit_custom(request, link_id):
    from forms import adbuilderForm
    from atrinsic.base.models import Link
    
    pub = request.organization
    link = Link.objects.get(id = link_id)
    links =  Link.objects.filter(byo=True,publisher=pub)
    
    form = adbuilderForm(request.organization)
    form.fields['name'].initial = link.name
    form.fields['advertisers'].initial = link.advertiser
    form.fields['destination'].initial = link.landing_page
    form.fields['content'].initial = link.link_content
    
            
    return AQ_render_to_response(request, 'publisher/links/deeplinking.html', {

            'form' : form,
            'link_type' : 'adbuilder',
            'link_id' : link_id,
            'links' : links,
            
        }, context_instance=RequestContext(request))

@url("^links/getCustom/$","publisher_links_getCustom")
@publisher_required
def publisher_links_getCustom(request):
    from atrinsic.base.models import Link,Organization,Website
    from atrinsic.util.ApeApi import Ape
    
    l = Link.objects.get(id=request.POST['id'])	    
    
    ws = request.POST['wsid']
    pub = request.organization
    if ws == "":
        website = request.organization.get_default_website()
    else:
        website = Website.objects.get(publisher=pub,id=ws)
    
    track_html = ""
    if website:
        track_html = l.track_html_ape(website)
        
    return HttpResponse(track_html, mimetype="text/html")

@url(r"^links/adbuilder/del/$", "publisher_delete_custom")
@tab("Publisher","Links","Links")
@publisher_required
def publisher_delete_custom(request):
    from atrinsic.base.models import Link
    
    l = Link.objects.get(id=request.POST['id'])
    l.delete()
          
    return HttpResponse("Link Deleted", mimetype="text/html")


@url(r"^links/adbuilder/getlinks/$", "publisher_adbuilder_links")
@tab("Publisher","Links","Links")
@publisher_required
def publisher_adbuilder_links(request):
    from atrinsic.base.models import Link
    from django.utils import simplejson
    from django.core import serializers

    
    pub = request.organization 
    links =  Link.objects.filter(byo=True,publisher=pub)
    newlinks = serializers.serialize("json", links)


    print pub
    track_html = "nothing yet"
    return HttpResponse(newlinks, mimetype="text/html")
