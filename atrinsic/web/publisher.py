from django.template import RequestContext
from django.db.models.query import QuerySet
from atrinsic.util.AceApi import createPO 

#CRITICAL IMPORTS
from atrinsic.util.imports import *

# Navigation Tab to View mappings for the Publisher Menu
tabset("Publisher",1,"Advertisers","publisher_advertisers",
        [ ("My Advertisers",('publisher_advertisers',['my'])),
          ("Find New Advertisers",('publisher_advertisers',['find'])),
          ("Pending Offers","publisher_advertisers_offers"),
          ("Pending Applications","publisher_advertisers_applications"),
          ("Expired Advertisers",('publisher_advertisers',['expired'])),
        ] 
      )
      
"""tabset("Publisher",5,"Live","publisher_live_dashboard",[])
@url(r"^live/$","publisher_live_dashboard")
@tab("Publisher","Live","Live")
@publisher_required
@register_api(None)
def publisher_live_dashboard(request):
    from atrinsic.web.misc import live_dashboard
    return live_dashboard(request)
"""         
@url(r"^terms/$","terms")
@url(r"^terms/(?P<advertiser_id>\d+)/$","terms")
@tab("Publisher","Dashboard","Dashboard")
def terms(request,advertiser_id=""):
    from atrinsic.base.models import TermsCopy
    request.session['accepted']=1
    terms_conditions = TermsCopy.objects.get(pk=1)
    print "TERMS"
    print advertiser_id
    return AQ_render_to_response(request, 'signup/terms.html', {'terms_conditions': terms_conditions.text_copy, 'advertiser_id':advertiser_id }, context_instance=RequestContext(request))
        
@url(r"^advertisers/applications/$","publisher_advertisers_applications")
@url(r"^advertisers/applications/page/(?P<page>[0-9]+)/$","publisher_advertisers_applications")
@tab("Publisher","Advertisers","Pending Applications")
@register_api(api_context=('id', 'ticker', 'company_name', 'vertical', 'state', 'country', 
                           'contact_firstname', 'contact_lastname', 'network_rating', ))
@publisher_required
def publisher_advertisers_applications(request, page=None):
    ''' View to display a Publisher's Advertiser Applications.  This view takes a GET
        variable 'sort' to perform columnsorting, and also takes a POST variable 'o_id'
        for doing bulk changes. '''
    from atrinsic.base.models import Organization, PublisherRelationship

    if request.method == "POST" and request.POST.has_key('action'):
        ids = request.POST.getlist("o_id")
        for id in ids:
            try:
                advertiser = Organization.objects.get(id=id,org_type=ORGTYPE_ADVERTISER,status=ORGSTATUS_LIVE)
                if PublisherRelationship.objects.filter(advertiser=advertiser,publisher=request.organization).count()>0:
                    pr = PublisherRelationship.objects.filter(advertiser=advertiser,publisher=request.organization)[0]
                    pr.delete()
                
            except Organization.DoesNotExist:
                pass
        
    sort_next = '#'

    sort = request.GET.get('sort', 'date_joined').lower()

    qs = Organization.objects.filter(publisher_relationships__status=RELATIONSHIP_APPLIED,status=ORGSTATUS_LIVE,
            publisher_relationships__publisher=request.organization).extra(select={"publisher_id":"select publisher_id from base_organization where id="+str(request.organization.id)})

    sort_fields = [ 'ticker', 'company_name', 'state', 'country', 'vertical', 'network_rating',
                    'date_joined', 'contact_firstname', 'force','seven_day_epc','three_month_epc']

    for f in sort_fields:
        if sort.endswith(f):
            if sort.startswith('-'):
                sort_next = sort[1:]
            else:
                sort_next = '-%s' % sort

            qs = qs.order_by(sort)
            break

    return object_list(request, queryset=qs, allow_empty=True, page=page,
            template_name='publisher/advertisers/applications.html', paginate_by=50, extra_context={ 
                'total_results' : qs.count(),
                'sort' : sort,
                'sort_next' : sort_next,
              })

@url(r"^advertisers/applications/retract/$","publisher_advertisers_applications_retract")
@publisher_required
@register_api(None)
def publisher_advertisers_applications_retract(request):
    ''' View to allow a Publisher to retract Advertiser Applications '''
    from atrinsic.base.models import Organization, PublisherRelationship

    try:
        advertiser_ids = request.REQUEST.getlist('o_id')
    except:
        advertiser_ids = []

    if request.REQUEST.get("advertiser_id",None):
        advertiser_ids.append(request.REQUEST.get("advertiser_id"))
    
    for id in advertiser_ids:
        advertiser = Organization.objects.get(id=id,org_type=ORGTYPE_ADVERTISER,status=ORGSTATUS_LIVE)
        if PublisherRelationship.objects.filter(advertiser=advertiser,publisher=request.organization).count()>0:
            pr = PublisherRelationship.objects.filter(advertiser=advertiser,publisher=request.organization)[0]
            pr.delete()

    return AQ_render_to_response(request, 'publisher/advertisers/applications-retract.html', {
        }, context_instance=RequestContext(request))


@url(r"^advertisers/offers/$","publisher_advertisers_offers")
@url(r"^advertisers/offers/page/(?P<page>[0-9]+)/$","publisher_advertisers_offers")
@tab("Publisher","Advertisers","Pending Offers")
@register_api(api_context=('id', 'ticker', 'company_name', 'vertical', 'state', 'country',
                           'contact_firstname', 'contact_lastname', 'network_rating', ))
@publisher_required
def publisher_advertisers_offers(request, page=None):
    ''' View to display and manage pending offers for a Publisher.  This view takes a GET
        variable 'sort' to perform column sorting, and POST variable 'o_id' to perform
        bulk operations depending on the POST variable 'method' (accept/decline) '''
    from atrinsic.base.models import Organization, Organization_Followers, PublisherRelationship
    
    offerApproved = True
    
    if request.method == "POST" and request.POST.has_key('method'):
        ids = request.POST.getlist("o_id")
        for id in ids:
            try:
                advertiser = Organization.objects.get(publisher_relationships__status=RELATIONSHIP_INVITED,status=ORGSTATUS_LIVE,
                                                     publisher_relationships__publisher=request.organization, id=id)

                relationship = PublisherRelationship.objects.filter(publisher=request.organization,advertiser=advertiser)[0]
                    

                if request.POST["method"].lower().find('accept') != -1:
                    Organization_Followers.objects.get_or_create(stalker=advertiser, followed=request.organization)
                    Organization_Followers.objects.get_or_create(stalker=request.organization, followed=advertiser)
                    
                    relationship.approve()
                if request.POST["method"].lower().find('decline') != -1:
                    relationship.decline()
                    
                relationship.save()
            except:
                pass
    else:
        if request.GET.has_key('Approval'):
            offerApproved = request.GET['Approval']
                
    sort_next = '#'

    sort = request.GET.get('sort', 'date_joined').lower()

    qs = Organization.objects.filter(publisher_relationships__status=RELATIONSHIP_INVITED,status=ORGSTATUS_LIVE,
            publisher_relationships__publisher=request.organization).extra(select={"publisher_id":"select publisher_id from base_organization where id="+str(request.organization.id)})

    sort_fields = [ 'ticker', 'company_name', 'state', 'country', 'vertical', 'network_rating',
                    'date_joined', 'contact_firstname', 'force',]

    for f in sort_fields:
        if sort.endswith(f):
            if sort.startswith('-'):
                sort_next = sort[1:]
            else:
                sort_next = '-%s' % sort

            qs = qs.order_by(sort)
            break

    return object_list(request, queryset=qs, allow_empty=True, page=page,
            template_name='publisher/advertisers/offers.html', paginate_by=50, extra_context={ 
                'total_results' : qs.count(),
                'sort' : sort,
                'offerApproved' : offerApproved,
                'sort_next' : sort_next,
              })

@url(r"^advertisers/offers/approve/(?P<advertiser_id>[0-9]+)/$","publisher_advertisers_offers_approve")
@publisher_required
@register_api(None)
def publisher_advertisers_offers_approve(request, advertiser_id):
    ''' View to approve an Advertiser Offer to a Publisher '''
    from atrinsic.base.models import Organization, Organization_Followers, PublisherRelationship,ProgramTermAction
    
    #try:
    advertiser = Organization.objects.get(publisher_relationships__publisher=request.organization,id=advertiser_id)

    Organization_Followers.objects.get_or_create(stalker=advertiser, followed=request.organization)
    Organization_Followers.objects.get_or_create(stalker=request.organization, followed=advertiser)
    
    relationship = PublisherRelationship.objects.filter(publisher=request.organization, advertiser=advertiser)[0]
        
    PTAction = ProgramTermAction.objects.filter(program_term=relationship.program_term)[0]
    
    #PO = createPO(advertiser, PTAction, relationship)
    #if PO:
    relationship.approve()

    #except:
    #    raise Http404
    return HttpResponseRedirect('/publisher/advertisers/offers/')


@url(r"^advertisers/offers/deny/(?P<advertiser_id>[0-9]+)/$","publisher_advertisers_offers_deny")
@publisher_required
@register_api(None)
def publisher_advertisers_offers_deny(request, advertiser_id):
    ''' View to deny an Advertiser Offer to a Publisher '''
    from atrinsic.base.models import Organization, PublisherRelationship

    try:
        advertiser = Organization.objects.get(publisher_relationships__status=RELATIONSHIP_INVITED,status=ORGSTATUS_LIVE,
            publisher_relationships__publisher=request.organization, id=advertiser_id)

        relationship = PublisherRelationship.objects.filter(publisher=request.organization,advertiser=advertiser)[0]
        relationship.status = RELATIONSHIP_DECLINED
        relationship.save()

    except:
        raise Http404

    return HttpResponseRedirect('/publisher/advertisers/offers/')

@url(r"^advertisers/$","publisher_advertisers")
@url(r"^advertisers/(?P<view>(my|find|expired))/$","publisher_advertisers")
@url(r"^advertisers/(?P<view>(my|find|expired))/page/(?P<page>[0-9]+)/$","publisher_advertisers")
@tab("Publisher","Advertisers","Find New Advertisers")
@publisher_required
@register_api(api_context=('id', 'ticker', 'company_name', 'vertical', 'state', 'country',
                           'contact_firstname', 'contact_lastname', 'network_rating', ))
def publisher_advertisers(request, view='my', page=None, template='publisher/advertisers/index.html'):
    ''' View to manage Publisher's Advertisers.  This view has three different resultsets
        based on the URL specified.  '/my/' displays this Publishers Advertisers.
        '/find/' provides a search interface to all Advertisers, and '/expired/'
        displays this Publisher's expired Advertisers.  This View has sortable result
        columns based on the GET variable 'sort' and the template displays different
        actions for each View based upon the form variable "view" which is derived
        from the URL.
    '''
    from atrinsic.base.models import Organization
    from atrinsic.util.xls import write_rows
    from forms import AdvertiserSearchForm
    import tempfile
    from django.db.models import Q
    
    q = None
    vertical = None
    sort_next = '#'

    download = False
    
    if request.GET:
        form = AdvertiserSearchForm(request.organization, request.GET)

        if form.is_valid():
            q = form.cleaned_data.get('q', None)
            vertical = form.cleaned_data.get('vertical', None)
            min_rating = form.cleaned_data.get('network_rating', None)
            date_from = form.cleaned_data.get('date_from', None)
            date_to = form.cleaned_data.get('date_to', None)
            
            
            if (vertical == '-1') or len(vertical) < 1:
                vertical = None

            if view == 'my':
                settab(request,"Publisher","Advertisers","My Advertisers")
                # My Advertisers
                qs = Organization.objects.filter(publisher_relationships__status=RELATIONSHIP_ACCEPTED,status=ORGSTATUS_LIVE,
                    publisher_relationships__publisher=request.organization).extra(select={"publisher_id":"select publisher_id from base_organization where id="+str(request.organization.id)})

                if request.GET.get('download', None) is not None:
                    template = 'publisher/advertisers/download.csv'
                    download = True

            elif view == 'expired':
                settab(request,"Publisher","Advertisers","Expired Advertisers")
                qs = Organization.objects.filter(publisher_relationships__status__in=[RELATIONSHIP_EXPIRED,RELATIONSHIP_DECLINED],status=ORGSTATUS_LIVE,
                    publisher_relationships__publisher=request.organization).extra(select={"publisher_id":"select publisher_id from base_organization where id="+str(request.organization.id)})

            else:
                # Default Advertiser Finder
                qs = Organization.objects.filter(org_type=ORGTYPE_ADVERTISER,status=ORGSTATUS_LIVE).filter(has_program_term=True, is_private=False)
            if q is not None:
                qs = qs.filter((Q(show_alias=True) & Q(company_alias__icontains=q)) | (Q(show_alias=False) & Q(company_name__icontains=q)))

            if vertical is not None:
                qs = qs.filter(vertical__order=vertical)
            else:
                qs = qs.filter(is_adult=request.organization.is_adult)
                
            if min_rating is not None:
                qs = qs.filter(network_rating__gte=str(min_rating))

            if form.cleaned_data.get('email_marketing', False):
                qs = qs.filter(allow_third_party_email_campaigns=True)
           
            if form.cleaned_data.get('direct_linking', False):
                qs = qs.filter(allow_direct_linking_through_ppc=True)
             
            if form.cleaned_data.get('trademark_bidding', False):
                qs = qs.filter(allow_trademark_bidding_through_ppc=True)                
            
            if date_from is not None:
                qs = qs.filter(date_joined__gte=date_from)

            if date_to is not None:
                qs = qs.filter(date_joined__lte=date_to)
        else:
            qs = QuerySet()

    else:
        form = AdvertiserSearchForm(organization=request.organization)

        if view == 'my':
            settab(request,"Publisher","Advertisers","My Advertisers")
            # My Advertisers
            qs = Organization.objects.filter(publisher_relationships__status=RELATIONSHIP_ACCEPTED,status=ORGSTATUS_LIVE,
                                             publisher_relationships__publisher=request.organization).extra(select={"publisher_id":"select publisher_id from base_organization where id="+str(request.organization.id)})
        elif view == 'expired':
            settab(request,"Publisher","Advertisers","Expired Advertisers")
            qs = Organization.objects.filter(publisher_relationships__status__in=[RELATIONSHIP_EXPIRED,RELATIONSHIP_DECLINED],status=ORGSTATUS_LIVE,
                publisher_relationships__publisher=request.organization).extra(select={"publisher_id":"select publisher_id from base_organization where id="+str(request.organization.id)})
        else:
            # XXX
            qs = Organization.objects.none()

    sort = request.GET.get('sort', 'date_joined').lower()
    if qs.model and qs.count():
        display_results = True
        sort_fields = [ 'ticker', 'company_name', 'state', 'country', 'vertical', 'network_rating',
                    'date_joined', 'contact_firstname', 'force', ]

        for f in sort_fields:
            if sort.endswith(f):
                if sort.startswith('-'):
                    sort_next = sort[1:]
                else:
                    sort_next = '-%s' % sort

                qs = qs.order_by(sort)
                break
        # if finding, remove all the advertisers that have outstanding relationships
        if view == 'find':
            result = []
            for i in qs:
                rs = i.get_advertiser_relationship(request.organization)
                if rs == None:
                    result.append(i)
                elif rs.status == RELATIONSHIP_NONE:
                    result.append(i)
            total_results = len(result)
            qs = result
        else:
            total_results = qs.count()
        
    else:
        if view == 'expired':
            display_results = True
            total_results = 0
        elif form.is_valid():
            display_results = True
            total_results = 0
        else:
            display_results = False
            total_results = 0

    if download == True:
        file_id,file_path = tempfile.mkstemp()

        res = [[ 'Ticker', 'Company Name', 'State', 'Country', 'Vertical', 'Network Rating','Date Joined', 'Force']]
        for row in qs:
            res.append([str(row.ticker),
                        str(row.company_name),
                        str(row.state),
                        str(row.country),
                        str(row.vertical),
                        str(row.network_rating),
                        str(row.date_joined),
                        str(row.force)])
            
        write_rows(file_path,res)
        res = open(file_path).read()
        
        response = HttpResponse(res,mimetype="application/vnd.ms-excel")
        response['Content-Disposition'] = 'attachment; filename=myadvertisers.xls'
        return response
    else:
        return object_list(request, queryset=qs, allow_empty=True, page=page,
                           template_name='publisher/advertisers/index.html', paginate_by=50, extra_context={ 
            'q' : q,
            'display_results' : display_results,
            'form' : form,
            'sort' : sort,
            'sort_next' : sort_next,
            'total_results' : total_results,
                'view' : view,

            })


@url(r"^advertisers/view/(?P<id>[0-9]+)/$","publisher_advertisers_view")
@publisher_required
@register_api(None)
def publisher_advertisers_view(request, id):
    ''' View that displays detailed information on a Publishers Advertiser '''

    from atrinsic.base.models import LinkPromotionType, Organization, PublisherRelationship

    try:
        advertiser  = Organization.objects.get(id=id,org_type = ORGTYPE_ADVERTISER,status=ORGSTATUS_LIVE)
    except Organization.DoesNotExist:
        raise Http404

    try:
        relationship = PublisherRelationship.objects.filter(advertiser=advertiser,publisher=request.organization,status=RELATIONSHIP_ACCEPTED)[0]
        program_term = relationship.program_term
    except:
        relationship =  None
        program_term = None

    return AQ_render_to_response(request, 'publisher/advertisers/view.html', {
            'adv' : advertiser,
            'promotion_types' : LinkPromotionType.objects.all(),
            'program_term':program_term,
        }, context_instance=RequestContext(request))


@url("^advertisers/expire/(?P<id>[0-9]+)/$","publisher_advertisers_expire")
@url("^advertisers/expire/$","publisher_advertisers_expire")
@publisher_required
@register_api(None)
def publisher_advertisers_expire(request, id=None):
    ''' View that allows a Publisher to expire Advertisers. '''

    from atrinsic.base.models import Organization, PublisherRelationship

    try:
        advertiser_ids = request.REQUEST.getlist('advertiser_id')
    except:
        advertiser_ids = []

    if id != None:
        advertiser_ids.append(id)
    

    for id in advertiser_ids:
        advertiser = Organization.objects.get(id=id,org_type=ORGTYPE_ADVERTISER,status=ORGSTATUS_LIVE)
        try:
            pr = PublisherRelationship.objects.filter(advertiser=advertiser,publisher=request.organization)[0]
            pr.status = RELATIONSHIP_EXPIRED
            pr.save()
        except:
            pass
        
    return HttpResponseRedirect("/publisher/advertisers/my/")

@url("^advertisers/apply/$","publisher_advertisers_apply")
@url("^advertisers/apply/(?P<id>[0-9]+)/$","publisher_advertisers_apply")
@url("^advertisers/apply/ajax/$","publisher_advertisers_apply")
@publisher_required
@register_api(None)
def publisher_advertisers_apply(request, id=None):
    ''' View that allows a Publisher to Apply to an Advertiser '''

    from atrinsic.base.models import AutoDeclineCriteria, Organization, PublisherRelationship
    
    #redir = request.REQUEST.get('redir', '/publisher/advertisers/')

    referer = request.META.get('HTTP_REFERER', None)
    if referer == None:
        redir = "/publisher/advertisers/"
    else:
        redir = referer
        
    try:
        advertiser_ids = request.REQUEST.getlist('advertiser_id')
    except:
        advertiser_ids = []

    if id != None:
        advertiser_ids.append(id)
                
    show_preterms_list = []
    
    for id in advertiser_ids:
        advertiser = Organization.objects.get(id=id,org_type=ORGTYPE_ADVERTISER,status=ORGSTATUS_LIVE)
        terms = advertiser.get_special_terms()
        
        if (bool(terms) & bool(request.GET.get("terms_accepted",0) == 0)):
            for term in terms:
                if term.special_action != "":
                    show_preterms_list.append(id)
                            
        if PublisherRelationship.objects.filter(advertiser=advertiser,publisher=request.organization).exclude(status=RELATIONSHIP_ACCEPTED).count() > 0:
            try:
                show_terms = show_preterms_list.index(id)
            except:
                pr = PublisherRelationship.objects.filter(advertiser=advertiser,publisher=request.organization).exclude(status=RELATIONSHIP_ACCEPTED)[0]
                for ad in AutoDeclineCriteria.objects.filter(advertiser=advertiser):
                    if ad.test_publisher(request.organization) == False:
                        pr.decline()
                        break
                if advertiser.publisher_approval == 1:
                    pr.approve()
                else:
                    pr.status = RELATIONSHIP_APPLIED
                pr.save()

        elif PublisherRelationship.objects.filter(advertiser=advertiser,publisher=request.organization).count() == 0:
            try:
                show_terms = show_preterms_list.index(id)
            except:
                pr,not_needed = PublisherRelationship.objects.get_or_create(advertiser=advertiser,publisher=request.organization,status=RELATIONSHIP_APPLIED,program_term=advertiser.get_default_program_term())
                for ad in AutoDeclineCriteria.objects.filter(advertiser=advertiser):
                    if ad.test_publisher(request.organization) == False:
                        pr.decline()
                        break
                if advertiser.publisher_approval == 1:
                    pr.approve()
                pr.save()
    if request.is_ajax():
        if show_preterms_list:
            return show_advertiser_preterms(request,show_preterms_list)
        else:
            return HttpResponse("Applied")
    else:
        return HttpResponseRedirect(redir)

@url("^advertisers/pre_terms/(?P<advertiser_id>[0-9]+)/$","publisher_advertisers_apply")
@publisher_required
@register_api(None)
def show_advertiser_preterms(request,advertiser_id):
    """view to show the advertisers special terms"""
    from atrinsic.base.models import ProgramTermSpecialAction
    
    return AQ_render_to_response(request, 'publisher/advertisers/applications-preterms.html', {'terms' : ProgramTermSpecialAction.objects.filter(organization__in = advertiser_id).exclude(special_action = '') }, context_instance=RequestContext(request))

@url("^advertisers/terms/(?P<advertiser_id>[0-9]+)/$","publisher_advertisers_apply")
@publisher_required
@register_api(None)
def show_advertiser_terms(request,advertiser_id):
    """view to show the advertisers special terms"""
    from atrinsic.base.models import Organization
    
    advertiser = Organization.objects.get(pk=advertiser_id)
    terms = advertiser.get_special_terms()
    return AQ_render_to_response(request, 'publisher/advertisers/applications-terms.html', {'terms' : terms, 'id':advertiser_id,'print':request.GET.get("print","0"), }, context_instance=RequestContext(request))

@url("^terms/accepted/(?P<advertiser_id>[0-9]+)/$","terms_accepted")
@publisher_required
@register_api(None)
def terms_accepted(request,advertiser_id):
    from atrinsic.base.models import Terms_Accepted_Log
    y = Terms_Accepted_Log.objects.create(ip = request.META['REMOTE_ADDR'], organization = request.organization, term_id = advertiser_id)
    return HttpResponse("logged")
    
@url("^help/$","publisher_help")
@publisher_required
def help(request):
    return render_to_response("help/pub/help.html")

@url("^helpdata/$","get_pub_help_data")
@publisher_required
def get_help_data(request):
    content = request.POST.get('page',None)
    return render_to_response("help/pub/" + content)
    

##################### Update Status ########################
@url("^updatestatus/$", 'update_status')
def update_status(request, id=None):
    ''' View to Update Status '''

    from atrinsic.base.models import Organization_Status,Organization
    from forms import StatusUpdateForm
        
    if request.POST:        
        form = StatusUpdateForm(request.POST)
        if form.is_valid():
            Organization_Status.objects.create(message=form.cleaned_data['message'], organization=request.organization)
            referer = request.META.get('HTTP_REFERER', None)
            if referer == None:
                return HttpResponseRedirect("/publisher/")
            else:
                return HttpResponseRedirect(referer)
    else:
        form = StatusUpdateForm()
    
    return AQ_render_to_response(request, 'base/AAN_UpdateStatus.html', {
            'form' : form,
        }, context_instance=RequestContext(request))
##################### END Update Status ########################            