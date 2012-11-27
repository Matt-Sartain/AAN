from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.db.models.query import QuerySet
from atrinsic.util.imports import *
from atrinsic.util.tabfunctions import *
# Navigation Tab to View mappings for the Network Account Menu
tabset("Network", 5, "Dashboard Management", "network_dashboard_news",
       [ ("News Management", "network_dashboard_news", superadmin_tab),
         ("Events Management", "network_dashboard_events", superadmin_tab),
         ("Manage Features", "network_dashboard_features", superadmin_tab),
         ])


@url(r"^dashboard/news/(?P<page>[0-9]+)/$", "network_dashboard_news")
@url(r"^dashboard/news/$", "network_dashboard_news")
@tab("Network","Dashboard Management","News Management")
@superadmin_required
def network_dashboard_news(request, page=None):
    ''' View to list and manage the Network News'''
    from atrinsic.base.models import News
    qs = News.objects.all().order_by('-created')

    return object_list(request, queryset=qs, allow_empty=True, page=page,
                template_name='network/news.html', paginate_by=50, extra_context={
                'total_results' : qs.count(),
              })

@url(r"^dashboard/news/add/$", "network_dashboard_news_add")
@tab("Network","Dashboard Management","News Management")
@superadmin_required
def network_dashboard_news_add(request):
    from atrinsic.base.models import News
    from forms import NewsForm
    if request.method == 'POST':
        form = NewsForm(request.POST)
        if form.is_valid():
            News.objects.create(news_status=form.cleaned_data['news_status'], data=form.cleaned_data['data'], viewed_by=form.cleaned_data['viewed_by'])
            return HttpResponseRedirect('/network/dashboard/news/')
    else:
        form = NewsForm()

    return AQ_render_to_response(request, 'network/news-add.html', {
            'form' : form,                                                                                        
        }, context_instance=RequestContext(request))                                                              


@url(r"^dashboard/news/edit/(?P<id>[0-9]+)/$", "network_dashboard_news_edit")
@tab("Network","Dashboard Management","News Management")
@superadmin_required
def network_dashboard_news_edit(request, id):
    from atrinsic.base.models import News
    from forms import NewsForm
    news = get_object_or_404(News, id=id)

    if request.method == 'POST':
        form = NewsForm(request.POST)
        if form.is_valid():
            news.news_status = form.cleaned_data['news_status']
            news.data = form.cleaned_data['data']
            news.viewed_by = form.cleaned_data['viewed_by']
            news.save()

            return HttpResponseRedirect('/network/dashboard/news/') 
    else:
        form = NewsForm(initial=news.__dict__)

    return AQ_render_to_response(request, 'network/news-edit.html', {
            'news' : news,
            'form' : form,                                                                                        
        }, context_instance=RequestContext(request))                                                              


@url(r"^dashboard/events/(?P<page>[0-9]+)/$", "network_dashboard_events")
@url(r"^dashboard/events/$", "network_dashboard_events")
@tab("Network","Dashboard Management","Events Management")
@superadmin_required
def network_dashboard_events(request, page=None):
    ''' View to list and manage the Network Events'''
    from atrinsic.base.models import Events
    qs = Events.objects.all().order_by('-created')

    return object_list(request, queryset=qs, allow_empty=True, page=page,
                template_name='network/events.html', paginate_by=50, extra_context={
                'total_results' : qs.count(),
              })

@url(r"^dashboard/events/add/$", "network_dashboard_events_add")
@tab("Network","Dashboard Management","Events Management")
@superadmin_required
def network_dashboard_events_add(request):
    from atrinsic.base.models import Events
    from forms import EventsForm
    if request.method == 'POST':
        form = EventsForm(request.POST)
        if form.is_valid():
            Events.objects.create(events_status=form.cleaned_data['events_status'], 
                                  data=form.cleaned_data['data'],
                                  events_name = form.cleaned_data['events_name'],
                                  events_date = form.cleaned_data['events_date'],
                                  location = form.cleaned_data['location'],
                                  registration = form.cleaned_data['registration'],
                                 )
            return HttpResponseRedirect('/network/dashboard/events/')
            
    else:
        form = EventsForm()

    return AQ_render_to_response(request, 'network/events-add.html', {
            'form' : form,                                                                                        
        }, context_instance=RequestContext(request))                                                              


@url(r"^dashboard/events/edit/(?P<id>[0-9]+)/$", "network_dashboard_events_edit")
@tab("Network","Dashboard Management","Events Management")
@superadmin_required
def network_dashboard_events_edit(request, id):
    from atrinsic.base.models import Events
    from forms import EventsForm
    events = get_object_or_404(Events, id=id)

    if request.method == 'POST':
        form = EventsForm(request.POST)
        if form.is_valid():
            events.events_status = form.cleaned_data['events_status']
            events.data = form.cleaned_data['data']
            events.events_name = form.cleaned_data['events_name']
            events.events_date = form.cleaned_data['events_date']
            events.location = form.cleaned_data['location']
            events.registration = form.cleaned_data['registration']
            events.save()

            return HttpResponseRedirect('/network/dashboard/events/') 
    else:
        form = EventsForm(initial=events.__dict__)

    return AQ_render_to_response(request, 'network/events-edit.html', {
            'events' : events,
            'form' : form,                                                                                        
        }, context_instance=RequestContext(request))
        
        
@url(r"^dashboard/feature/$", "network_dashboard_features")
@tab("Network","Dashboard Management","Manage Features")
@superadmin_required
def network_dashboard_features(request):
    from atrinsic.base.models import Organization_FilterTypes
    
    qs = Organization_FilterTypes.objects.all().order_by('-created')
    
    return AQ_render_to_response(request, 'network/dashboard/features.html', {
            'features' : qs,
            #'form' : form,                                                                                        
        }, context_instance=RequestContext(request))
        
        
@url(r"^dashboard/feature/add/$", "network_dashboard_feature_add")
@tab("Network","Dashboard Management","Manage Features")
@superadmin_required
def network_dashboard_feature_add(request):
    from atrinsic.base.models import Organization_FilterTypes
    from forms import OrgFilterForm
    if request.method == 'POST':
        form = OrgFilterForm(request.POST)
        if form.is_valid():
            Organization_FilterTypes.objects.create(organization=form.cleaned_data['org_to_add'], 
                                  filterchoice=1,
                                 )
            return HttpResponseRedirect('/network/dashboard/feature/')
            
    else:
        form = OrgFilterForm()

    return AQ_render_to_response(request, 'network/dashboard/feature-add.html', {
            'form' : form,
        }, context_instance=RequestContext(request))
        
@url(r"^dashboard/feature/delete/(?P<id>[0-9]+)/$", "network_dashboard_feature_delete")
@tab("Network","Dashboard Management","Manage Features")
@superadmin_required
def network_dashboard_feature_delete(request, id):
    from atrinsic.base.models import Organization_FilterTypes
    filter = get_object_or_404(Organization_FilterTypes, id=id)
    filter.delete()
    return HttpResponseRedirect('/network/dashboard/feature/')
