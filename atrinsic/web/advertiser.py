from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.db.models.query import QuerySet
from atrinsic.web.helpers import base36_encode
from atrinsic.util.AceApi import createPO 

#CRITICAL IMPORTS
from atrinsic.util.imports import *

#===========================================---/DASHBOARD/---===========================================#
####################### Advertiser Dashboard ##########################
@url(r"^$","advertiser_dashboard")
@advertiser_required
@register_api(None)
def advertiser_dashboard(request):
    from atrinsic.base.models import Organization, AqWidget, UserAqWidget
    from forms import WidgetSettingsForm
    this_page = 'advertiser-dashboard'
    
    all_publishers = Organization.objects.filter(advertiser_relationships__status=RELATIONSHIP_ACCEPTED,
                                                     advertiser_relationships__advertiser=request.organization)
            
    pids = [j.id for j in all_publishers]
    
    x = UserAqWidget.objects.select_related("AqWidget").filter(page=this_page,organization=request.organization).order_by('sort_order', '-id')
    widgets = UserAqWidget.prep(x,request,pids)
            
    z = AqWidget.objects.filter(widget_type__in=[1,4], Active=1)
    widget_list = AqWidget.prep(z)

    inbox = request.organization.received_messages.filter(is_active=True).order_by('-date_sent')
    
    hashed_ACEID = (request.organization.ace_id  + 148773) * 12

    return AQ_render_to_response(request, 'advertiser/dashboard.html', {
        'widgets':widgets,
        'widget_list':widget_list,
        'current_page':this_page,
        'msgcount' : inbox,
        'settings':True,
        'sdate':request.GET.get('start_date',''),
        'edate':request.GET.get('end_date',''),
        'current_tab':'Dashboard',
        'hashed_ACEID': hashed_ACEID,
        }, context_instance=RequestContext(request))

##################### END Advertiser Dashboard ########################
#######################################################################

####################### Advertiser Comparison ##########################
@url(r"^dashboard/comparisons/$","advertiser_dashboard_comparisons")
@advertiser_required
@register_api(None)
def advertiser_dashboard_comparisons(request):
    from atrinsic.base.models import PublisherRelationship,Organization,PeerToPeerComparisonHourly
    show_form = False
    comparison = None
    period = None
    metric = None
    data = { }
    data2 = { }
    orgs = [ ]

    if request.POST:
        form = AdvertiserComparisonForm(request.POST)

        if form.is_valid():
            comparison = int(form.cleaned_data.get('comparison', PEERTOPEER_VERTICAL))
            period = int(form.cleaned_data.get('period', PEERTOPEERPERIOD_DAILY))
            metric = form.cleaned_data.get('metric', METRIC_IMPRESSIONS)
            show_form = True

    if request.GET: 
            comparison = int(request.GET.get('comparison', PEERTOPEER_VERTICAL))
            period = int(request.GET.get('period', PEERTOPEERPERIOD_DAILY))
            metric = request.GET.get('metric', METRIC_IMPRESSIONS)

            if comparison == PEERTOPEER_VERTICAL:
                # Advertisers in the same vertical
                orgs = Organization.objects.filter(org_type=ORGTYPE_ADVERTISER, vertical__in =[w.vertical for w in request.organization.website_set.all()])

            elif comparison == PEERTOPEER_PUBLISHER:
                # Advertisers running the same Publishers
                publishers = [ r.publisher for r in PublisherRelationship.objects.filter(advertiser=request.organization) ]
                orgs = [ r.publisher for r in PublisherRelationship.objects.filter(publisher__in=publishers) ]

            elif comparison == PEERTOPEER_PUBLISHER_VERTICAL:   
                # Advertisers running the same Publishers who are in the same vertical 
                publishers = [ r.publisher for r in PublisherRelationship.objects.filter(advertiser=request.organization) ]
                orgs = Organization.objects.filter(id__in=[ p.id for p in publishers ], vertical=[w.vertical for w in request.organization.website_set.all()])

            if period == PEERTOPEERPERIOD_HOURLY:
                period = datetime.datetime.now() - datetime.timedelta(hours=24)
                all_comparisons = PeerToPeerComparisonHourly.objects.filter(organization__in=orgs, period__gte=period, metric=metric)
                comparisons = PeerToPeerComparisonHourly.objects.filter(organization=request.organization, period__gte=period, metric=metric)
            else:
                period = datetime.datetime.now() - datetime.timedelta(days=30)
                all_comparisons = PeerToPeerComparisonDaily.objects.filter(organization__in=orgs, period__gte=period, metric=metric)
                comparisons = PeerToPeerComparisonDaily.objects.filter(organization=request.organization, period__gte=period, metric=metric)

            data = { }

            for c in all_comparisons:
                val = data.get(c.period, 0)
                data[c.period] = val + c.value
             
            for c in comparisons:
                val = data2.get(c.period, 0)
                data2[c.period] = val + c.value
             
            max_scale = max(data.values())

            return AQ_render_to_response(request, 'advertiser/dashboard-comparisons.json', {
                'data' : data,
                'data2' : data2,
                'max_scale' : max_scale,
            }, context_instance=RequestContext(request))

    else:
        form = AdvertiserComparisonForm(initial={ 'comparison': comparison, 'period' : period, 'metric' : metric, })
 
    return AQ_render_to_response(request, 'advertiser/dashboard-comparisons.html', {
            'form' : form,
            'data' : data,
            'comparison' : comparison,
            'period' : period,
            'metric' : metric,
            'show_form' : show_form,
        }, context_instance=RequestContext(request))

####################### END Advertiser Comparison ##########################
############################################################################


####################### Dashboard Settings ##########################
@url(r"^dashboard/settings/$","advertiser_dashboard_settings")
@advertiser_required
@register_api(None)
def advertiser_dashboard_settings(request):
    if request.method == 'POST':
        from forms import WidgetSettingsForm
        form = WidgetSettingsForm(request.POST)
        if form.is_valid():
            from atrinsic.base.models import UserAqWidget
            widget = UserAqWidget.objects.get(pk=request.POST['wid'])
            widget.custom_group = form.cleaned_data.get('dashboard_group_data_by',0)
            widget.custom_columns = str(form.cleaned_data['variable1'])+","+str(form.cleaned_data['variable2'])
            request.organization.dashboard_variable1 = form.cleaned_data['variable1']
            request.organization.dashboard_variable2 = form.cleaned_data['variable2']
            request.organization.save()
            db_date_string = ''
            if (request.POST.has_key("start_date")):
                if (request.POST['start_date'] != "") & (request.POST['start_date'] != None):
                    db_date_string+=str(request.POST['start_date'])
                    if request.POST.has_key("end_date"):
                        if (request.POST['end_date'] != "") & (request.POST['end_date'] != None):
                            db_date_string+=','+str(request.POST['end_date'])
                        else:
                            db_date_string+=','+str(request.POST['start_date'])
                    else:
                        db_date_string+=','+str(request.POST['start_date'])
            widget.custom_date_range = db_date_string
            widget.save()
    return HttpResponseRedirect('/advertiser/')

####################### END Dashboard Settings ##########################
#########################################################################       

####################### Set Dashboard Timeframe ##########################
@url(r"^set_dashboard_time_frame/(?P<time_frame>[0-9]+)/$","advertiser_set_dashboard_timeframe")
@advertiser_required
@register_api(None)
def advertiser_set_dashboard_timeframe(request,time_frame):
    request.session["date_range"] = int(time_frame)

    return HttpResponseRedirect("/advertiser/")

####################### END Set Dashboard Timeframe ##########################
##############################################################################     

############################ Get Chart Data(Widgets) ###############################
@url(r"^get_chart_data/$","advertiser_get_chart_data")
@advertiser_required
@register_api(None)
def advertiser_get_chart_data(request):

    report = construct_dashboard_report(request,request.organization)

    cols = report.RenderHeader()
    return AQ_render_to_response(request, 'advertiser/json_post.html',{
        'cols':cols,
        'report':report})

############################ END Get Chart Data(Widgets) ###############################
########################################################################################
#===========================================---/END DASHBOARD/---===========================================#

#===========================================---/ADVERTISER PUBLISHER SECTION/---===========================================#
####################### Search For Publishers ##########################
@url(r"^publishers/$","advertiser_publishers")
@url(r"^publishers/(?P<view>(my|find))/$","advertiser_publishers")
@url(r"^publishers/(?P<view>(my|find))/page/(?P<page>[0-9]+)/$","advertiser_publishers")
@register_api(api_context=('id', 'ticker', 'company_name', 'vertical', 'state', 'country',
                           'contact_firstname', 'contact_lastname', 'network_rating', ))
@advertiser_required
def advertiser_publishers(request, view='find', page=None, template='advertiser/publishers/index.html'):
    ''' Manage Publishers.  This is the main Advertiser Publisher's listing view.  This view takes
        a form POST for search attributes to be used in filtering the result set.  This view also
        handles multiple result sets based on the type of view being requested (My Publishers, versus
        all Publishers, etc).  This view also handles column based sorting via GET and has paginated
        results.  Additionally these results can be downloaded by passing the "download" argument 
        in the query string (eg: ?download=1)
    '''
    from forms import PublisherSearchForm
    from atrinsic.base.models import Organization,PublisherVertical,PublisherRelationship
    from atrinsic.util.xls import write_rows
    from django.utils.encoding import smart_str
    from atrinsic.web.helpers import base36_encode
    import tempfile
    q, vertical, date_joined = None, None, None
    sort_next = '#'
    verticalName = ""
    download = False

    if request.GET:
        form = PublisherSearchForm(request.organization, request.GET)

        if form.is_valid():
            q = form.cleaned_data.get('q', None)
            try:
                pub_id = int(form.cleaned_data.get('pub_id', None))
            except ValueError:
                pub_id = None
                
            vertical = form.cleaned_data.get('vertical', None)
            date_from = form.cleaned_data.get('date_from', None)
            date_to = form.cleaned_data.get('date_to', None)
            min_force = form.cleaned_data.get('force',None)
            min_rating = form.cleaned_data.get('network_rating',None)
            pub_url = form.cleaned_data.get('pub_url',None)
            
            
            if (vertical == '-1') or len(vertical) < 1:
                vertical = None                
            else:
                verticalName = PublisherVertical.objects.get(order=vertical).name
                
            if view == 'my':
                # My Publishers
                qs = Organization.objects.filter(advertiser_relationships__status=RELATIONSHIP_ACCEPTED,status=ORGSTATUS_LIVE,org_type=ORGTYPE_PUBLISHER,
                    advertiser_relationships__advertiser=request.organization).extra(select={"advertiser_id":"select id from base_organization where id="+str(request.organization.id)})

                if request.GET.get('download', None) is not None:
                    template = 'advertiser/publishers/download.csv'
                    download = True

            else:
                # Default Publisher Finder
                qs = Organization.objects.filter(org_type=ORGTYPE_PUBLISHER,status=ORGSTATUS_LIVE)

            if q is not None:
                qs = qs.filter(company_name__icontains=q)
           
            if pub_id is not None:
                qs = qs.filter(website__id=pub_id)

            if vertical is not None:
                qs = qs.filter(website__vertical=vertical)
            else:
                qs = qs.filter(is_adult=request.organization.is_adult)
            
            if date_from is not None:
                qs = qs.filter(advertiser_relationships__date_accepted__gte=date_from)

            if date_to is not None:
                qs = qs.filter(advertiser_relationships__date_accepted__lte=date_to)

            if min_force is not None:
                qs = qs.filter(force__gte=str(min_force))

            if min_rating is not None:
                qs = qs.filter(network_rating__gte=str(min_rating))

            if pub_url is not None:
                qs = qs.filter(website__url__icontains=pub_url)

        else:
            qs = QuerySet()

    else:
        form = PublisherSearchForm(organization=request.organization)

        if view == 'my':
            # My Publishers
            qs = Organization.objects.filter(advertiser_relationships__status=RELATIONSHIP_ACCEPTED,status=ORGSTATUS_LIVE,org_type=ORGTYPE_PUBLISHER,
            advertiser_relationships__advertiser=request.organization).extra(select={"advertiser_id":"select advertiser_id from base_organization where id="+str(request.organization.id)})
        else:
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
                if request.organization.get_advertiser_relationship(i) == None or request.organization.get_advertiser_relationship(i).status == RELATIONSHIP_DECLINED:                    
                    result.append(i)
            total_results = len(result)
            qs = result
        else:
            total_results = qs.count()

        seen_hash = {}
        result = []
        for i in qs:
            if seen_hash.has_key(i):
                continue
            result.append(i)
            seen_hash[i] = 1
        total_results = len(result)
        qs = result
    elif form.is_valid():
            display_results = True
            total_results = 0    
    else:
        display_results = False
        total_results = 0
        
    if download == True:
        """
        file_id,file_path = tempfile.mkstemp()
        print request.organization.get_relationship_date_accepted(2)
        res = [["Publisher ID","Encoded Publisher ID","Publisher Name","Company Name","URL","Network Rating","Force","State","Email","igCode", "Date Joined"]]
        for row in qs:
            res.append([str(int(row.pk)),
                        str(base36_encode(int(row.pk))),
                        str(row.organizationcontacts_set.all()[0].firstname + " " + row.organizationcontacts_set.all()[0].lastname),
                        smart_str(row.name),
                        str(row.get_default_website()),
                        str(row.get_network_rating()),
                        str(row.force),
                        str(row.state),
                        str(row.organizationcontacts_set.all()[0].email),
                        str([int(x.id) for x in row.website_set.filter(is_default=True)]).replace("[","").replace("]",""),
                        str(request.organization.get_relationship_date_accepted(row.pk))])
            
        write_rows(file_path,res)
        res = open(file_path).read()
        
        response = HttpResponse(res,mimetype="application/vnd.ms-excel")
        response['Content-Disposition'] = 'attachment; filename=mypublishers.xls'

        return response
        """
        
        file_id,file_path = tempfile.mkstemp()
		
        #date joined in PublisherRelationship
		
        res = [["Publisher ID","Encoded id","Company Name","Approval Date","URL","Network Rating","Force","State","Email"]]
        #res = [["Publisher ID","Encoded id","Date Joined","Publisher Name","Company Name","URL","Network Rating","Force","State","Email"]]
        for row in qs:
            """dateJoined = smart_str(PublisherRelationship.objects.get(advertiser=request.organization, publisher=row, status = 3).date_accepted)
            if dateJoined == 'None':
                dateJoined = smart_str(PublisherRelationship.objects.get(advertiser=request.organization, publisher=row, status = 3).date_initiated)
                print '****** %s', dateJoined"""
            #base publisher relationship.. for Date Joined
            try:
                date_joined = PublisherRelationship.objects.filter(publisher=row, advertiser=request.organization, status = 3).order_by('date_accepted')[0].date_accepted
                if date_joined == None:
                    date_joined = PublisherRelationship.objects.filter(publisher=row, advertiser=request.organization, status = 3).order_by('date_accepted')[0].date_initiated
            except:
                date_joined = ''
            res.append([str(int(row.pk)),
                        str(base36_encode(int(row.pk))),
                        #dateJoined,
                        #str(row.organizationcontacts_set.all()[0].firstname + " " + row.organizationcontacts_set.all()[0].lastname),
                        smart_str(row.name),
                        str(date_joined),
                        str(row.get_default_website()),
                        str(row.get_network_rating()),
                        str(row.force),
                        str(row.state),
                        str(row.organizationcontacts_set.all()[0].email)])
        write_rows(file_path,res)
        print res
        res = open(file_path).read()
        
        response = HttpResponse(res,mimetype="application/vnd.ms-excel")
        response['Content-Disposition'] = 'attachment; filename=mypublishers.xls'
        return response
        
        
    else:
        return AQ_render_to_response(request, 'advertiser/publishers/index.html', {
            'display_results':display_results,            
            'form' : form,
            'object_list': qs,
            'view' : view,
            'vertical':verticalName
        }, context_instance=RequestContext(request))

####################### END Search For Publishers ##########################
############################################################################       

####################### Recruit Publisher ##########################
@url("^publishers/recruit/(?P<id>[0-9]+)/$","advertiser_publishers_recruit")
@url("^publishers/recruit/$","advertiser_publishers_recruit")
@advertiser_required
@register_api(None)
def advertiser_publishers_recruit(request, id=None):
    ''' View that allows an Advertiser to Recruit a Publisher. '''
    from atrinsic.base.models import Organization,PublisherRelationship,ProgramTerm, ProgramTerm_Historical_Data
    from forms import RecruitForm
    import time
    
    redir = None
    closewindow = False
    minEffectiveDate = False    
    
    try:
        publisher_ids = request.REQUEST.getlist('publisher_id')
    except:
        publisher_ids = []
        
    if id != None:
        publisher_ids.append(id)
    redir = request.GET.get('redir',None)
    if redir == None:
        redir = request.POST.get('redir', '/advertiser/publishers/groups/')
        
    print publisher_ids
    if request.method == 'POST':

        form = RecruitForm(request.organization, request.POST)

        if form.is_valid():
            program_term = ProgramTerm.objects.get(advertiser=request.organization,id=form.cleaned_data["program_term"])
            for id in publisher_ids:
                publisher = Organization.objects.get(id=id,org_type=ORGTYPE_PUBLISHER,status=ORGSTATUS_LIVE)
                if PublisherRelationship.objects.filter(publisher=publisher,advertiser=request.organization).count() == 0:
                    print "A"
                    PublisherRelationship.objects.create(publisher=publisher,advertiser=request.organization,status=RELATIONSHIP_INVITED,program_term=program_term)
                elif PublisherRelationship.objects.filter(publisher=publisher,advertiser=request.organization)[0].status not in [RELATIONSHIP_ACCEPTED]:
                    print "B"
                    pr = PublisherRelationship.objects.get(publisher=publisher,advertiser=request.organization)
                    pr.status = RELATIONSHIP_INVITED
                    pr.date_initiated = datetime.date.fromtimestamp(time.time())
                    pr.program_term = program_term
                    pr.save()
                elif PublisherRelationship.objects.filter(publisher=publisher,advertiser=request.organization)[0].status ==RELATIONSHIP_ACCEPTED:     
                    # If relationship already accepted, do not update PublisherRelationship object. 
                    pass
                    #pr = PublisherRelationship.objects.get(publisher=publisher,advertiser=request.organization)
                    #pr.program_term = program_term
                    #pr.date_initiated = datetime.date.fromtimestamp(time.time())
                    #pr.save()
                else:
                    print "D"
                    pr = PublisherRelationship.objects.get(publisher=publisher,advertiser=request.organization)
                    pr.program_term = program_term
                    pr.date_initiated = datetime.date.fromtimestamp(time.time())
                    pr.save()
                
                prgmTermHistData = ProgramTerm_Historical_Data.objects.filter(advertiser=request.organization, publisher=publisher).order_by('-effective_date')
                #prgmTermHistData = None
                if prgmTermHistData != None and prgmTermHistData.count() > 0:
                    endDate = time.strptime(str(form.cleaned_data["effective_date"]),"%Y-%m-%d")
                    endDate = datetime.date(int(time.strftime("%Y", endDate)), int(time.strftime("%m", endDate)), int(time.strftime("%d", endDate))) - datetime.timedelta(days=1)
                    ptHD = ProgramTerm_Historical_Data.objects.get(id=prgmTermHistData[0].id)
                    ptHD.end_date = endDate
                    ptHD.save()
                ProgramTerm_Historical_Data.objects.create(advertiser=request.organization,publisher=publisher,
                program_term=program_term, effective_date=form.cleaned_data["effective_date"])                    


           
            if redir:         
                return HttpResponseRedirect(redir)
    else:
    	view = request.GET.get('view',None)
        relHistory = ProgramTerm_Historical_Data.objects.filter(advertiser=request.organization, publisher=id).order_by('-effective_date')
        #relHistory = None
        
        if relHistory != None and relHistory.count() > 0:
            minEffectiveDate = relHistory[0].effective_date
            c = time.strptime(str(relHistory[0].effective_date),"%Y-%m-%d")
            minEffectiveDate = True
        form = RecruitForm(request.organization)    
    
    if minEffectiveDate:
        effectiveYear = time.strftime("%Y", c)
        effectiveMonth = time.strftime("%m", c)
        effectiveDay = time.strftime("%d", c)
        effDate = datetime.date(int(effectiveYear), int(effectiveMonth), int(effectiveDay)) + datetime.timedelta(days=1)
        effDate = time.strptime(str(effDate),"%Y-%m-%d")
        effectiveYear = time.strftime("%Y", effDate)
        effectiveMonth = time.strftime("%m", effDate)
        effectiveDay = time.strftime("%d", effDate)
    else:
    	d = time.strptime(str(datetime.date.today()),"%Y-%m-%d")
        effectiveYear = time.strftime("%Y", d)
        effectiveMonth = time.strftime("%m", d)
        effectiveDay = time.strftime("%d", d)        
        
    return AQ_render_to_response(request, 'advertiser/publishers/recruit.html', {
            'publisher_ids' : publisher_ids,
            'form' : form,
            'redir' : redir,
            'closewindow' : closewindow,
            'effectiveYear' : effectiveYear,
            'effectiveMonth' : effectiveMonth,
            'effectiveDay' : effectiveDay,
            'minEffectiveDate' : minEffectiveDate,
            'view' : request.GET.get('view',None),
        }, context_instance=RequestContext(request))

####################### END Recruit Publisher ##########################
########################################################################

####################### Recruit Selected Publishers ##########################
@url("^publishers/recruit/all(?P<id>[0-9]+)/$","advertiser_publishers_recruit_all")
@url("^publishers/recruit/all/$","advertiser_publishers_recruit_all")
@advertiser_required
@register_api(None)
def advertiser_publishers_recruit_all(request, id=None):
    ''' View that allows an Advertiser to Recruit a Publisher. '''
    try:
        publisher_ids = request.REQUEST.getlist('publisher_id_h')
    except:
        publisher_ids = []
        
    print "PUBLISHERS - %s" % publisher_ids
    from atrinsic.base.models import Organization,PublisherRelationship,ProgramTerm
    program_term = ProgramTerm.objects.get(advertiser=request.organization,is_default=True)
    for id in publisher_ids:
        try:
            publisher = Organization.objects.get(id=id,org_type=ORGTYPE_PUBLISHER,status=ORGSTATUS_LIVE)
            if PublisherRelationship.objects.filter(publisher=publisher,advertiser=request.organization).count() == 0:
                PublisherRelationship.objects.create(publisher=publisher,advertiser=request.organization,status=RELATIONSHIP_INVITED,program_term=program_term)
            elif PublisherRelationship.objects.filter(publisher=publisher,advertiser=request.organization)[0].status not in [RELATIONSHIP_ACCEPTED]:
                pr = PublisherRelationship.objects.get(publisher=publisher,advertiser=request.organization)
                pr.status = RELATIONSHIP_INVITED
                pr.program_term = program_term
                pr.save()
            else:
                pr = PublisherRelationship.objects.get(publisher=publisher,advertiser=request.organization)
                pr.program_term = program_term
                pr.save()
        except:
            pass
            
    referer = request.META.get('HTTP_REFERER', None)
    if referer == None:
        return HttpResponseRedirect("/advertiser/publishers/")
    else:
        return HttpResponseRedirect(referer)
        
####################### END Recruit Selected Publishers ##########################
##################################################################################

####################### Publisher Applications ##########################
@url(r"^publishers/applications/$","advertiser_publishers_applications")
@url(r"^publishers/applications/page/(?P<page>[0-9]+)/$","advertiser_publishers_applications")
@register_api(api_context=('id', 'ticker', 'company_name', 'vertical', 'state', 'country',                      
                           'contact_firstname', 'contact_lastname', 'network_rating', ))                        
@advertiser_required
def advertiser_publishers_applications(request, page=None):
    ''' List of this Advertiser's Publisher Applications.  Takes a form submission
        via POST for accepting or declining applications in bulk. Handles column
        sorting of results via GET '''
    from atrinsic.base.models import Organization,Organization_Followers,PublisherRelationship

    if request.method == "POST" and request.POST.has_key('method'):
        ids = request.POST.getlist("o_id")
        for id in ids:
            try:
                publisher = Organization.objects.get(advertiser_relationships__status=RELATIONSHIP_APPLIED,
                                                     advertiser_relationships__advertiser=request.organization, id=id, status=ORGSTATUS_LIVE)
                
                relationship = PublisherRelationship.objects.filter(advertiser=request.organization,publisher=publisher)[0]
                if request.POST["method"] == 'approve':
                    Organization_Followers.objects.get_or_create(stalker=publisher, followed=request.organization)
                    Organization_Followers.objects.get_or_create(stalker=request.organization, followed=publisher)
                    
                    relationship.approve()
                elif request.POST["method"] == 'deny':
                    relationship.decline()
                    
                relationship.save()
            except:
                pass
        
    sort_next = '#'

    sort = request.GET.get('sort', 'date_joined').lower()

    qs = Organization.objects.filter(advertiser_relationships__status=RELATIONSHIP_APPLIED, status=ORGSTATUS_LIVE,
            advertiser_relationships__advertiser=request.organization).extra(select={"advertiser_id":"select advertiser_id from base_organization where id="+str(request.organization.id)})

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
            template_name='advertiser/publishers/applications.html', paginate_by=50, extra_context={ 
                'total_results' : qs.count(),
                'sort' : sort,
                'sort_next' : sort_next,
              })

####################### END Publisher Applications ##########################
############################################################################

####################### Approve Publisher Application ##########################
@url(r"^publishers/applications/approve/$","advertiser_publishers_applications_approve")
@url(r"^publishers/applications/approve/(?P<publisher_id>\d+)/$","advertiser_publishers_applications_approve")
@advertiser_required
@register_api(None)
def advertiser_publishers_applications_approve(request, publisher_id=None):
    ''' Method to handle the approval of an Advertisers Publisher Application.  Takes the
        publisher_id in the URL and redirects, or can be specified via a GET/POST which
        will render a template (to be used as an AJAX call).'''
    from atrinsic.base.models import Organization,Organization_Followers,PublisherRelationship,ProgramTermAction
    redir = True

    if publisher_id is None:
        publisher_id = request.REQUEST.get('publisher_id')
        redir = False

    #try:
    publisher = Organization.objects.get(advertiser_relationships__status=RELATIONSHIP_APPLIED,status=ORGSTATUS_LIVE,
        advertiser_relationships__advertiser=request.organization, id=publisher_id)
    
    # Comment out for Testing	TODO: Uncomment
    Organization_Followers.objects.get_or_create(stalker=publisher, followed=request.organization)
    Organization_Followers.objects.get_or_create(stalker=request.organization, followed=publisher)

    relationship = PublisherRelationship.objects.filter(advertiser=request.organization,publisher=publisher)[0]
    PTActions = ProgramTermAction.objects.filter(program_term=relationship.program_term)    
    # This still needs to be tested on LIVE. DO not remove this code:
    #for PTAction in PTActions:
        #PO = createPO(request.organization, PTAction, relationship)
    #if PO:
    relationship.approve()
        
        
    #except:   #Was failing out when the relationship was already accepted
    #publisher = Organization.objects.get(advertiser_relationships__status=RELATIONSHIP_ACCEPTED,status=ORGSTATUS_LIVE,
    #        advertiser_relationships__advertiser=request.organization, id=publisher_id)


    if redir:
        return HttpResponseRedirect('/advertiser/publishers/applications/')


    return AQ_render_to_response(request, 'advertiser/publishers/applications-approve.html', {
            'publisher' : publisher,
        }, context_instance=RequestContext(request))

####################### END Approve Publisher Application ##########################
####################################################################################

########################## Offer Status ##############################
@url(r"^publishers/offers/$","advertiser_publisher_offers")
@url(r"^publishers/offers/page/(?P<page>[0-9]+)/$","advertiser_publisher_offers")
@advertiser_required
def advertiser_publisher_offers(request, page=None):
    ''' View to display and manage pending offers for a Publisher.  This view takes a GET
        variable 'sort' to perform column sorting, and POST variable 'o_id' to perform
        bulk operations depending on the POST variable 'method' (accept/decline) '''
    from atrinsic.base.models import Organization, Organization_Followers, PublisherRelationship, ProgramTerm
    from django.db import connection

    
    
    offerApproved = True
    
    if request.method == "POST" and request.POST.has_key('method'):
        ids = request.POST.getlist("o_id")
        for id in ids:
            try:
                publisher = Organization.objects.get(publisher_relationships__status=RELATIONSHIP_INVITED,status=ORGSTATUS_LIVE,
                                                     publisher_relationships__advertiser=request.organization, id=id)

                relationship = PublisherRelationship.objects.filter(advertiser=request.organization,publisher=publisher)[0]
                    

                if request.POST["method"].lower().find('accept') != -1:
                    Organization_Followers.objects.get_or_create(stalker=publisher, followed=request.organization)
                    Organization_Followers.objects.get_or_create(stalker=request.organization, followed=publisher)              
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

    
    qs_pr = PublisherRelationship.objects.filter(advertiser=request.organization, advertiser__status=ORGSTATUS_LIVE, publisher__status=ORGSTATUS_LIVE, status__in=[RELATIONSHIP_ACCEPTED,RELATIONSHIP_INVITED,RELATIONSHIP_DECLINED,RELATIONSHIP_RETRACTED], show_history=1).select_related("program_term").order_by("status")
    """
    sort_fields = [ 'company_name', 'state', 'country', 'URL', '7 dAY epc',
                    '3 Month EPC',]

    for f in sort_fields:
        if sort.endswith(f):
            if sort.startswith('-'):
                sort_next = sort[1:]
            else:
                sort_next = '-%s' % sort

            qs = qs.order_by(sort)
            break
    """
    return object_list(request, queryset=qs_pr, allow_empty=True, page=page,
            template_name='advertiser/publishers/offers.html', paginate_by=25, extra_context={ 
                'total_results' : qs_pr.count(),
                #'sort' : sort,
                'offerApproved' : offerApproved,
                #'sort_next' : sort_next,
              })

########################## END Offer Status ##############################
##########################################################################

########################## Retract Offer ##############################
@url(r"^publishers/offers/retract/$","advertisers_publisher_applications_retract")
@url(r"^publishers/offers/retract/(?P<publisher_id>\d+)/$","advertisers_publisher_applications_retract")
@advertiser_required
@register_api(None)
def publisher_advertisers_applications_retract(request, publisher_id=None):
    ''' View to allow a Publisher to retract Advertiser Applications '''
    from atrinsic.base.models import Organization, PublisherRelationship

    try:
        publisher_ids = request.REQUEST.getlist('o_id')
    except:
        publisher_ids = []
    
    if publisher_id != None:
        publisher_ids.append(publisher_id)
    print publisher_ids
    for id in publisher_ids:
        publisher = Organization.objects.get(id=id,org_type=ORGTYPE_PUBLISHER,status=ORGSTATUS_LIVE)
        try:
            pr = PublisherRelationship.objects.get(advertiser=request.organization,publisher=publisher, status=RELATIONSHIP_INVITED)
            pr.status = RELATIONSHIP_RETRACTED
            pr.save()
        except:
            pass


    return HttpResponseRedirect('/advertiser/publishers/offers/')

########################## END Retract Offer ##############################
###########################################################################    

########################## Remove From History ##############################
@url(r"^publishers/offers/remove_history/$","")
@url(r"^publishers/offers/remove_history/(?P<publisher_id>\d+)/$","advertisers_publisher_applications_remove_history")
@advertiser_required
@register_api(None)
def advertisers_publisher_applications_remove_history(request, publisher_id=None):
    ''' View to allow a Publisher to retract Advertiser Applications '''
    from atrinsic.base.models import Organization, PublisherRelationship

    try:
        publisher_ids = request.REQUEST.getlist('o_id')
    except:
        publisher_ids = []
    
    if publisher_id != None:
        publisher_ids.append(publisher_id)

    for id in publisher_ids:
        publisher = Organization.objects.get(id=id,org_type=ORGTYPE_PUBLISHER,status=ORGSTATUS_LIVE)
        try:
            pr = PublisherRelationship.objects.get(advertiser=request.organization,publisher=publisher, status__in=[2,3,4,5,6,7])
            pr.show_history = 0
            pr.save()
        except:
            pass


    return HttpResponseRedirect('/advertiser/publishers/offers/')

########################## END Remove From History ##############################
#################################################################################

####################### Deny Publisher Application ##########################
@url(r"^publishers/applications/deny/$","advertiser_publishers_applications_deny")
@url(r"^publishers/applications/deny/(?P<publisher_id>\d+)/$","advertiser_publishers_applications_deny")
@advertiser_required
@register_api(None)
def advertiser_publishers_applications_deny(request, publisher_id=None):
    ''' Method to handle the denial of an Advertisers Publisher Application.  Takes the
        publisher_id in the URL and redirects, or can be specified via a GET/POST which
        will render a template (to be used as an AJAX call).'''
    from atrinsic.base.models import Organization,PublisherRelationship
    redir = True

    if publisher_id is None:
        publisher_id = request.REQUEST.get('publisher_id')
        redir = False

    try:
        publisher = Organization.objects.get(advertiser_relationships__status=RELATIONSHIP_APPLIED,status=ORGSTATUS_LIVE,
            advertiser_relationships__advertiser=request.organization, id=publisher_id)

        relationship = PublisherRelationship.objects.filter(advertiser=request.organization,publisher=publisher)[0]
        relationship.decline()

        if redir:
            return HttpResponseRedirect('/advertiser/publishers/applications/')

    except:
        raise Http404

    return AQ_render_to_response(request, 'advertiser/publishers/applications-deny.html', {
            'publisher' : publisher,
        }, context_instance=RequestContext(request))

####################### END Deny Publisher Application ##########################
####################################################################################
 


####################### Advertiser Groups ##########################
@url(r"^publishers/groups/$","advertiser_publishers_groups")
@register_api(api_context=('id', 'name', 'publishers', ))
@advertiser_required
@register_api(None)
def advertiser_publishers_groups(request):
    ''' Manage & Creating Publisher Groups
    '''
    from atrinsic.base.models import PublisherGroup
    from forms import GroupCreateForm
    next = request.REQUEST.get('next', None)
    publisher_ids = request.REQUEST.getlist('publisher_id')

    if request.method == "POST" and request.POST.has_key('name'):
        form = GroupCreateForm(request.POST)

        if form.is_valid():
            g = None
            name = form.cleaned_data['name']

            try:
                g = PublisherGroup.objects.get(advertiser=request.organization, name=name)
            except PublisherGroup.DoesNotExist:
                g = PublisherGroup.objects.create(advertiser=request.organization, name=name)

            for publisher_id in publisher_ids:
                if publisher_id is not None:
                    g.add_publisher(publisher_id) 

            if next is not None: 
                return HttpResponseRedirect(next)
            form = GroupCreateForm()

    else:
        form = GroupCreateForm()


    return AQ_render_to_response(request, 'advertiser/publishers/groups.html', {
            'publisher_ids' : publisher_ids,
            'form' : form,
        }, context_instance=RequestContext(request))

####################### END Advertiser Groups ##########################
########################################################################

####################### View Advertiser Groups ##########################
@url(r"^publishers/groups/(?P<id>[0-9]+)/$","advertiser_publishers_groups_view")
@register_api(api_context=('id', 'name', 'publishers', ))
@advertiser_required
def advertiser_publishers_groups_view(request, id):
    ''' View a specific Publisher Group.  This view also handles the bulk approval/contacting
        of Publishers within the result list '''
    from atrinsic.base.models import PublisherGroup
    group = get_object_or_404(PublisherGroup.objects.filter(advertiser=request.organization),id=id)

    if request.method == "POST":
        if request.POST.get("target",None):
            target = int(request.POST.get("target"))
            if target == REPORTFORMAT_EXCEL:
                response = render_to_response("misc/groups/dataxls.html", {'groups': group,})
                filename = "misc/groups/download.xls"                
                response['Content-Disposition'] = 'attachment; filename='+filename
                response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
                return response
            elif target == REPORTFORMAT_CSV:
                response =  HttpResponse(render_to_string("misc/groups/download.csv",{"groups":group}),mimetype="text/csv")
                response['Content-Disposition'] = 'attachment; filename=groups.csv'
                return response
            elif target == REPORTFORMAT_TSV:
                response =  HttpResponse(render_to_string("misc/groups/download.txt",{"groups":group}),mimetype="application/octet-stream")
                response['Content-Disposition'] = 'attachment; filename=groups.txt'
                return response
        
        publisher_ids = request.REQUEST.getlist('publisher_id')
    
        if request.POST.get('remove'):
            for publisher_id in publisher_ids:
                group.remove_publisher(publisher_id) 
        if request.POST.get('contact'):
            return HttpResponseRedirect('/advertiser/messages/campaigns/add/?group_id=%d' % group.id)            

    return AQ_render_to_response(request, 'advertiser/publishers/groups-view.html', {
            'group' : group,
        }, context_instance=RequestContext(request))

####################### END View Advertiser Groups ##########################
#############################################################################

####################### Delete Advertiser Groups ##########################
@url(r"^publishers/groups/(?P<id>[0-9]+)/delete/$","advertiser_publishers_groups_delete")
@advertiser_required
@register_api(None)
def advertiser_publishers_groups_delete(request, id):
    ''' View to delete a Publisher Group '''
    from atrinsic.base.models import PublisherGroup
    group = get_object_or_404(PublisherGroup.objects.filter(advertiser=request.organization),id=id)
    group.publishers.clear()
    group.delete()

    return HttpResponseRedirect('/advertiser/publishers/groups/')

####################### END Delete Advertiser Groups ########################
#############################################################################

####################### Add Pub To Advertiser Groups ##########################
@url(r"^publishers/groups/addto/$","advertiser_publishers_groups_addto")
@advertiser_required
@register_api(None)
def advertiser_publishers_groups_addto(request):
    ''' View to add members to a Publisher Group '''
    from atrinsic.base.models import Organization,PublisherGroup
    from forms import GroupAddtoForm
    closewindow = False
    redir = request.REQUEST.get('redir', None)
    publisher_ids = request.REQUEST.getlist('publisher_id')


    if request.method == 'POST':

        form = GroupAddtoForm(request.organization, request.POST)

        if form.is_valid():
            group = get_object_or_404(PublisherGroup, id=form.cleaned_data['group'])

            for publisher_id in publisher_ids:
                try:
                    publisher  = Organization.objects.get(advertiser_relationships__status=RELATIONSHIP_ACCEPTED,status=ORGSTATUS_LIVE,
                        advertiser_relationships__advertiser=request.organization, id=publisher_id)
                except Organization.DoesNotExist:
                    raise Http404

                group.add_publisher(publisher)

            if redir != None:
                return HttpResponseRedirect(redir)
            else:
                return HttpResponseRedirect('/advertiser/publishers/my/')

    else:
        form = GroupAddtoForm(request.organization)

    return AQ_render_to_response(request, 'advertiser/publishers/groups-addto.html', {
            'form' : form,
            'publisher_ids' : publisher_ids,
            'closewindow' : closewindow, 
            'redir' : redir,
        }, context_instance=RequestContext(request))

####################### END Add Pub To Advertiser Groups ##########################
###################################################################################

####################### Remove Pub from Advertiser Groups ##########################
@url(r"^publishers/groups/(?P<id>[0-9]+)/removefrom/(?P<p_id>[0-9]+)/$","advertiser_publishers_groups_removefrom")
@advertiser_required
@register_api(None)
def advertiser_publishers_groups_removefrom(request, id, p_id):
    ''' View to remove members from a Publisher Group '''
    from atrinsic.base.models import PublisherGroup
    group = get_object_or_404(PublisherGroup.objects.filter(advertiser=request.organization),id=id)
    group.remove_publisher(p_id)

    return HttpResponseRedirect('/advertiser/publishers/groups/')

####################### END Remove Pub From Advertiser Groups ##########################
########################################################################################
#===========================================---/END ADVERTISER PUBLISHER SECTION/---===========================================#

####################### Display Publisher Info. ##########################
@url(r"^publishers/view/(?P<id>[0-9]+)/$","advertiser_publishers_view")
def advertiser_publishers_view(request, id):
    ''' Publisher View.  This view displays details on an individual Publisher '''
    from atrinsic.base.models import Organization
    try:
        publisher  = Organization.objects.get(id=id,org_type = ORGTYPE_PUBLISHER,status=ORGSTATUS_LIVE)
    except Organization.DoesNotExist:
        raise Http404
    from atrinsic.util.date import compute_date_range
 
    d_range = compute_date_range(int(request.POST.get("date_range",9)))
    imps = request.organization.get_metric(METRIC_IMPRESSIONS,d_range,"All",[publisher])
    clicks = request.organization.get_metric(METRIC_CLICKS,d_range,"All",[publisher])
    ctr = 0
    
    if imps != 0 :
        ctr = float(clicks) / float(imps) * 100
        
    return AQ_render_to_response(request, 'advertiser/publishers/view.html', {
            'pub' : publisher,
            'report_types' : REPORTTIMEFRAME_CHOICES,
            'commission':request.organization.get_metric(METRIC_AMOUNT,d_range,"All",[publisher]),
            'sales':request.organization.get_metric(METRIC_ORDERS,d_range,"All",[publisher]),
            'leads':request.organization.get_metric(METRIC_LEADS,d_range,"All",[publisher]),
            'clicks':clicks,
            'impressions':imps,
            'ctr':ctr,
            'date_range':int(request.POST.get("date_range",9)),
        }, context_instance=RequestContext(request))

####################### END Display Publisher Info. ##########################
##############################################################################

####################### Expire Publisher ##########################
@url("^publishers/expire/(?P<id>[0-9]+)/$","advertiser_publishers_expire")
@url("^publishers/expire/$","advertiser_publishers_expire")
@advertiser_required
@register_api(None)
def advertiser_publishers_expire(request, id=None):
    ''' View to expire an Advertiser's recruitment of a Publisher '''
    from atrinsic.base.models import Organization,PublisherRelationship,ProgramTerm
    try:
        publisher_ids = request.REQUEST.getlist('publisher_id')
    except:
        publisher_ids = []

    if id != None:
        publisher_ids.append(id)
    

    default_program = ProgramTerm.objects.get(advertiser=request.organization,is_default=True)
    for id in publisher_ids:
        publisher = Organization.objects.get(id=id,org_type=ORGTYPE_PUBLISHER,status=ORGSTATUS_LIVE)
        try:
            pr = PublisherRelationship.objects.filter(publisher=publisher,advertiser=request.organization)[0]
            pr.status = RELATIONSHIP_EXPIRED
            pr.save()
        except:
            pass
        
    return HttpResponseRedirect("/advertiser/publishers/my/")

####################### END Expire Publisher ##########################
#######################################################################

############################ Update Status ###############################
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
                return HttpResponseRedirect("/advertiser/")
            else:
                return HttpResponseRedirect(referer)
    else:
        form = StatusUpdateForm()
    
    return AQ_render_to_response(request, 'base/AAN_UpdateStatus.html', {
            'form' : form,
        }, context_instance=RequestContext(request))

############################ END Update Status ###############################
##############################################################################

############################ Delete Status ###############################
@url("^deletestatus/id/(?P<id>\d+)/$", 'delete_status')
def delete_status(request, id=None):
    from atrinsic.base.models import Organization_Status    
    try:
        o = Organization_Status.objects.get(pk=id, organization = request.organization)
        o.delete() 
    except:
        """dummy data"""
    return HttpResponse("return data", mimetype="text/html")

############################ END Delete Status ###############################
##############################################################################          

############################ Help Section ###############################
@url("^help/$","advertiser_help")
@advertiser_required
def help(request):
    return render_to_response("help/adv/help.html")
    
@url("^helpdata/$","get_adv_help_data")
@advertiser_required
def get_help_data(request):
    content = request.POST.get('page',None)
    return render_to_response("help/adv/" + content)

############################ END Help Section ###############################
#############################################################################         
     
     
     
     