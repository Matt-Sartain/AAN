from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.db.models.query import QuerySet
from atrinsic.util.imports import *
from atrinsic.util.tabfunctions import *
from atrinsic.base.models import Organization
from forms import ForceForm
# Navigation Tab to View mappings for the Network Manage Relationships Menu
tabset("Network", 3, "Manage Relationships", "network_relationships_publisher_advertiser",
       [ ("Advertiser Relationships", "network_relationships_advertiser",superadmin_tab),
         ("Publisher Relationships", "network_relationships_publisher",superadmin_tab),
         ("Publisher Advertiser Relationships", "network_relationships_publisher_advertiser"),
         ])


@url(r"^relationships/advertiser/$","network_relationships_advertiser")
@url(r"^relationships/advertiser/page/(?P<page>[0-9]+)/$", "network_relationships_advertiser")
@tab("Network","Manage Relationships","Advertiser Relationships")
@superadmin_required
def network_relationships_advertiser(request, page=None):
    ''' View to display all Network Admins and links to allow the assignment of Advertisers
        to the Network Admins'''
    from atrinsic.base.models import User
    qs = User.objects.filter(userprofile__admin_level__gt=0)
    
    return object_list(request, queryset=qs, allow_empty=True, page=page,
                template_name='network/advertiser-relationships.html', paginate_by=50, extra_context={
                'total_results' : qs.count(),
              })

@url(r"^relationships/publisher/$","network_relationships_publisher")
@url(r"^relationships/publisher/page/(?P<page>[0-9]+)/$", "network_relationships_publisher")
@tab("Network","Manage Relationships","Publisher Relationships")
@superadmin_required
def network_relationships_publisher(request, page=None):
    ''' View to display all the Network Admins and links to allow the assignment of Publishers
        to the Network Admins '''
    from atrinsic.base.models import User
    qs = User.objects.filter(userprofile__admin_level__gt=0)

    return object_list(request, queryset=qs, allow_empty=True, page=page,
                template_name='network/publisher-relationships.html', paginate_by=50, extra_context={
                'total_results' : qs.count(),
              })

@url(r"^relationships/publisher-advertiser/$","network_relationships_publisher_advertiser")
@url(r"^relationships/publisher-advertiser/page/(?P<page>[0-9]+)/$", "network_relationships_publisher_advertiser")
@tab("Network","Manage Relationships","Publisher Advertiser Relationships")
@admin_required
def network_relationships_publisher_advertiser(request, page=None):
    
    qs = request.user.get_profile().admin_assigned_advertisers()

    return object_list(request, queryset=qs, allow_empty=True, page=page,
                template_name='network/relationships/publisher-advertiser.html', paginate_by=50, extra_context={
                'total_results' : qs.count(),
              })


@url(r"^relationships/advertiser/(?P<user_id>\d+)/assign/$","network_relationships_advertiser_assign")
@tab("Network","Manage Relationships","Advertiser Relationships")
@superadmin_required
def network_relationships_advertiser_assign(request, user_id):
    ''' View to assign Advertisers to a Network Admin '''
    from atrinsic.base.models import User,Organization
    from forms import NetworkAdvertiserAssignForm
    admin = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = NetworkAdvertiserAssignForm(request.POST)

        if form.is_valid():
            for o in admin.get_profile().admin_assigned_organizations.filter(org_type=ORGTYPE_ADVERTISER):
                admin.get_profile().admin_assigned_organizations.remove(o)

            for id in form.cleaned_data['advertiser']:
                try:
                    org = Organization.objects.get(id=id)
                    admin.get_profile().admin_assigned_organizations.add(org)
                except User.DoesNotExist:
                    pass

            return HttpResponseRedirect('/network/relationships/advertiser/')

    else:
        form = NetworkAdvertiserAssignForm(initial= { 'advertiser' : [ o.id for o in admin.get_profile().admin_assigned_organizations.filter(org_type=ORGTYPE_ADVERTISER)], })

    return AQ_render_to_response(request, 'network/advertiser-assign.html', {
                'form' : form,
                'admin' : admin,
            }, context_instance=RequestContext(request))

 
@url(r"^relationships/publisher/(?P<user_id>\d+)/assign/$","network_relationships_publisher_assign")
@tab("Network","Manage Relationships","Publisher Relationships")
@superadmin_required
def network_relationships_publisher_assign(request, user_id):
    ''' View to assign Publishers to Network Admins '''
    from atrinsic.base.models import User,Organization
    from forms import NetworkPublisherAssignForm

    admin = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = NetworkPublisherAssignForm(request.POST)

        if form.is_valid():
            for o in admin.get_profile().admin_assigned_organizations.filter(org_type=ORGTYPE_PUBLISHER):
                admin.get_profile().admin_assigned_organizations.remove(o)

            for id in form.cleaned_data['publisher']:
                try:
                    org = Organization.objects.get(id=id)
                    admin.get_profile().admin_assigned_organizations.add(org)
                except User.DoesNotExist:
                    pass

            return HttpResponseRedirect('/network/relationships/publisher/')

    else:
        form = NetworkPublisherAssignForm(initial= { 'publisher' : [ o.id for o in admin.get_profile().admin_assigned_organizations.filter(org_type=ORGTYPE_PUBLISHER)], })

    return AQ_render_to_response(request, 'network/publisher-assign.html', {
                'form' : form,
                'admin' : admin,
            }, context_instance=RequestContext(request))

 
@url(r"^relationships/publisher/(?P<publisher_id>\d+)/assign/$","network_relationships_publisher_assign")
@tab("Network","Manage Relationships","Publisher Relationships")
@superadmin_required
def network_relationships_publisher_assign(request, publisher_id):
    ''' View to assign Publishers to Network Admins '''

    publisher = get_object_or_404(Organization, id=publisher_id)

    if request.method == 'POST':
        form = NetworkAdvertiserAssignForm(request.POST)

        if form.is_valid():
            publisher.assigned_admins.clear()
            for uid in form.cleaned_data['user']:
                try:
                    u = User.objects.get(id=uid)
                    # XXX
                    request.user.get_profile().admin_assigned_organizations.add(publisher)
                except User.DoesNotExist:
                    pass

        return HttpResponseRedirect('/network/relationships/publisher/')

    else:
        # XXX: initial = 
        form = NetworkAdvertiserAssignForm(initial= { 'users' : [ u.id for u in request.user.get_profile().admin_assigned_organizations.all().filter(org_type = ORGTYPE_PUBLISHER) ], })

    return AQ_render_to_response(request, 'network/publisher-assign.html', {
                'form' : form,
                'publisher' : publisher,
            }, context_instance=RequestContext(request))
 

@url(r"^relationships/advertiser/(?P<advertiser_id>\d+)/contact/$","network_relationships_advertiser_contact")
@tab("Network","Manage Relationships","Advertiser Relationships")
@admin_required
def network_relationships_advertiser_contact(request, advertiser_id):
    ''' View to assign Advertiser to Network Admins '''

    advertiser = get_object_or_404(Organization, id=advertiser_id)

    if request.method == 'POST':
        form = NetworkAdvertiserContactForm(request.POST)

        if form.is_valid():
            advertiser.contact_firstname = form.cleaned_data['contact_firstname']
            advertiser.contact_lastname = form.cleaned_data['contact_lastname']
            advertiser.contact_email = form.cleaned_data['contact_email']
            advertiser.contact_phone = form.cleaned_data['contact_phone']
            advertiser.contact_fax = form.cleaned_data['contact_fax']
            advertiser.save()

            return HttpResponseRedirect('/network/relationships/advertiser/')

    else:
        form = NetworkAdvertiserContactForm(initial={
                        'contact_firstname' : advertiser.contact_firstname,
                        'contact_lastname' : advertiser.contact_lastname,
                        'contact_phone' : advertiser.contact_phone,
                        'contact_email' : advertiser.contact_email,
                        'contact_fax' : advertiser.contact_fax,
                    })

    return AQ_render_to_response(request, 'network/advertiser-contact.html', {
                'form' : form,
                'advertiser' : advertiser,
            }, context_instance=RequestContext(request))
 


@url(r"^relationships/publisher/(?P<publisher_id>\d+)/force/$", "network_relationships_publisher_force")
@tab("Network","Manage Relationships","Publisher Relationships")
@admin_required
def network_relationships_publisher_force(request, publisher_id):
    ''' View to allow a Network Admin to update the Force for a Publisher '''

    publisher = get_object_or_404(Organization, id=publisher_id)

    if request.method == "POST":
        form = ForceForm(request.POST)  

        if form.is_valid():
            publisher.force = str(form.cleaned_data['force'])
            publisher.save()

            return HttpResponseRedirect('/network/publisher/settings/')

    else:
        form = ForceForm(initial={ 'force' : publisher.force, })  

    return AQ_render_to_response(request, 'network/publisher-force.html', {
                'form' : form,
                'publisher' : publisher,
            }, context_instance=RequestContext(request))

 
@url(r"^relationships/publisher/(?P<publisher_id>\d+)/rating/$", "network_relationships_publisher_rating")
@tab("Network","Manage Relationships","Publisher Relationships")
@admin_required
def network_relationships_publisher_rating(request, publisher_id):
    ''' View to allow a Network Admin to update the Network Rating for a Publisher '''
    from atrinsic.base.models import Organization,QualityScoringSystemMetric,QualityScoringSystem
    from forms import NetworkRatingForm
    
    publisher = get_object_or_404(Organization, id=publisher_id)

    if request.method == "POST":
        form = NetworkRatingForm(request.POST)
        
        if form.is_valid():
            publisher.qualityscoringsystem_set.all().delete()

            rating = 0.00

            for m in QualityScoringSystemMetric.objects.all():
                if form.cleaned_data.has_key(m.key):
                    QualityScoringSystem.objects.create(publisher=publisher, metric=m, value=str(form.cleaned_data[m.key]))
                    rating += form.cleaned_data[m.key] * float(m.weight)

            publisher.network_rating = str(rating)
            publisher.save()

            return HttpResponseRedirect('/network/publisher/settings/')

    else:
        d = { }

        for m in publisher.qualityscoringsystem_set.all():
            d[m.metric.key] = m.value

        form = NetworkRatingForm(initial=d)

    return AQ_render_to_response(request, 'network/publisher-rating.html', {
                'form' : form,
                'publisher' : publisher,
            }, context_instance=RequestContext(request))
 
