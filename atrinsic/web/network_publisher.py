from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.db.models.query import QuerySet
from atrinsic.util.imports import *

# Navigation Tab to View mappings for the Network Publisher Menu
tabset("Network", 2, "Publisher", "network_publisher_account_settings",
       [ ("Publisher Account Settings", "network_publisher_account_settings"),
         #("Publisher Web Site Settings", "network_publisher_incentive"), # removed referencing ticket 5
         ])


@url(r"^publisher/settings/$","network_publisher_account_settings")
@tab("Network","Publisher","Publisher Account Settings")
@admin_required
def network_publisher_account_settings(request):
    ''' View to display Publishers and links to do the following:
        Assign Network Contact, Update Status, Impersonate, Edit Rating, 
        and Edit Force.  The variable "buttons" is passed to the template
        to determine what buttons to display. '''
    from atrinsic.base.models import Organization, UserProfile
        
    if UserProfile.objects.get(user = request.user).admin_level == 3 or UserProfile.objects.get(user = request.user).admin_level == 4:
        qs = UserProfile.objects.get(user = request.user).admin_assigned_organizations.filter(org_type=ORGTYPE_PUBLISHER)
    else:
        qs = Organization.objects.filter(org_type=ORGTYPE_PUBLISHER)
    
    qs.extra(select={
        'email': 'select email FROM base_organizationcontacts oc WHERE oc.organization_id = base_organization.id ORDER BY ID limit 1'
    }).extra(select={
        'firstname': 'select firstname FROM base_organizationcontacts oc WHERE oc.organization_id = base_organization.id ORDER BY ID limit 1'
    }).extra(select={
        'lastname': 'select lastname FROM base_organizationcontacts oc WHERE oc.organization_id = base_organization.id ORDER BY ID limit 1'
    })
    
    return AQ_render_to_response(request, 'network/publisher.html', {
            'buttons' : 'settings',
            'qs' : qs
        }, context_instance=RequestContext(request))


@url("^publisher/settings/contact/(?P<id>[0-9]+)/$", "network_publisher_account_contact")
@tab("Network","Publisher","Publisher Account Settings")
@admin_required
def network_publisher_account_contact(request, id):
    ''' Assigns Network Contact'''
    from atrinsic.base.models import Organization
    from forms import PublisherAssignContactForm
    
    publisher = get_object_or_404(Organization, id=id)

    if request.method == 'POST':
        form = PublisherAssignContactForm(publisher, request.POST)

        if form.is_valid():
            publisher.network_admin = get_object_or_404(User, id=form.cleaned_data['contact'])
            publisher.save()

            return HttpResponseRedirect('/network/publisher/settings/')
    else:
        if publisher.network_admin is not None:
            form = PublisherAssignContactForm(publisher, initial={ 'contact' : publisher.network_admin.id, })
        else:
            form = PublisherAssignContactForm(publisher)

    return AQ_render_to_response(request, 'network/publisher-contact.html', {
            'publisher' : publisher,
            'form' : form,
        }, context_instance=RequestContext(request))
        
@url("^publisher/settings/w9/(?P<id>[0-9]+)/$", "network_publisher_settings_w9")
@tab("Network","Publisher","Publisher W9 Status")
@admin_required
def network_publisher_settings_w9(request, id):
    ''' Assigns Network Contact
    '''
    from atrinsic.base.models import W9Status, Organization
    from forms import W9StatusForm
    from django.utils import dateformat 
    publisher = get_object_or_404(Organization, id=id)

    try:
        wnine = W9Status.objects.get(organization=id)
    except:
        wnine = None
        

    if request.method == 'POST':
        form = W9StatusForm(publisher, request.POST)

        if form.is_valid():
            if wnine == None:
                W9Status.objects.create(organization=publisher, status = form.cleaned_data['status'], datereceived = 
                form.cleaned_data['datereceived'])
            else:
                wnine.status = form.cleaned_data['status']
                wnine.datereceived = form.cleaned_data['datereceived']
                wnine.save()
            return HttpResponseRedirect('/network/publisher/settings/')
    else:
        if wnine != None:
            inits = { 'status' : wnine.status, 'datereceived' : dateformat.format(wnine.datereceived, 'm/d/Y')}
            form = W9StatusForm(request, initial=inits)    
        else:
            form = W9StatusForm(request)

    if publisher.ace_id == None:        
        create_company(publisher)
	hashed_ACEID = (publisher.ace_id  + 148773) * 12

    return AQ_render_to_response(request, 'network/publisher-w9.html', {
            'publisher' : publisher,
            'form' : form,
            'hashed_ACEID' : hashed_ACEID,
        }, context_instance=RequestContext(request))


@url(r"^publisher/status/(?P<id>\d+)/$","network_publisher_status")
@tab("Network","Publisher","Publisher Account Settings")
@admin_required
def network_publisher_status(request, id):
    ''' View to allow a Network Admin to update a Publisher's Status '''
    from forms import PubNetworkStatusForm
    
    publisher = get_object_or_404(request.user.get_profile().admin_assigned_publishers(), id=id)

    if request.method == 'POST':
        form = PubNetworkStatusForm(request.POST)

        if form.is_valid():
            publisher.status = form.cleaned_data['status']
            publisher.is_adult = int(form.cleaned_data['is_adult'])
            publisher.save()

            return HttpResponseRedirect('/network/publisher/settings/')
    else:
        form = PubNetworkStatusForm(initial={ 'status' : publisher.status, 'is_adult' : publisher.is_adult})
    print dir(form)
    return AQ_render_to_response(request, 'network/publisher/status.html', {
            'publisher' : publisher,
            'form' : form,
        }, context_instance=RequestContext(request))



@url(r"^publisher/incentive/$","network_publisher_incentive")
@tab("Network","Publisher","Publisher Web Site Settings")
@admin_required
def network_publisher_incentive(request):
    ''' View to display a Publishers Incentives '''
    from atrinsic.base.models import DataTransfer
    return AQ_render_to_response(request, 'network/publisher/incentive.html', {
        'transfers':DataTransfer.objects.all(),
        }, context_instance=RequestContext(request))



@url(r"^publisher/incentive/status/(?P<id>\d+)/$","network_publisher_incentive_status")
@tab("Network","Publisher","Publisher Web Site Settings")
@admin_required
def network_publisher_incentive_status(request, id):
    ''' View to allow a Network Admin to update a Publishers Data Transfer status '''
    from atrinsic.base.models import DataTransfer
    from forms import IncentiveStatusForm
    datatransfer = get_object_or_404(DataTransfer.objects.all(), id=id)

    if request.method == 'POST':
        form = IncentiveStatusForm(request.POST)

        if form.is_valid():
            datatransfer.status = form.cleaned_data['status']
            datatransfer.save()

            return HttpResponseRedirect('/network/publisher/incentive/')
    else:
        form = IncentiveStatusForm(initial={ 'status' : datatransfer.status, })

    return AQ_render_to_response(request, 'network/publisher/incentive_status.html', {
            'datatransfer' : datatransfer,
            'form' : form,
        }, context_instance=RequestContext(request))

@url(r"^publisher/create/$","network_publisher_create")
@url(r"^publisher/edit/(?P<oid>[0-9]+)/$","network_publisher_create")
@tab("Network","Publisher","Publisher Signup")
@admin_required
def network_publisher_create(request,oid=None):
    from atrinsic.base.models import Organization,Website,OrganizationContacts,OrganizationPaymentInfo,UserProfile,User
    from forms import PublisherSignupForm2,PublisherSignupForm3,PaymentInfoForm,ContactInfoForm,WebsiteForm

    if request.POST:
        update = False
        if oid:
            org = Organization.objects.get(pk=oid)
            update = True
            
        form_step2 = PublisherSignupForm2(update, request.POST)
        form_step3 = PublisherSignupForm3(update, request.POST)
        form_payment = PaymentInfoForm(request.POST)
        form_contact_info = ContactInfoForm(request.POST)
        website_form = WebsiteForm(request.POST)
        
        if form_step2.is_valid() & form_step3.is_valid() & form_payment.is_valid() & form_contact_info.is_valid() & website_form.is_valid():
            if oid:
                org = Organization.objects.get(pk=oid)
            else:
                org = Organization.objects.create(org_type=ORGTYPE_PUBLISHER, status=ORGSTATUS_UNAPPROVED)
           
            org.company_name = form_step3.cleaned_data['company_name']
            org.address = form_step3.cleaned_data['pub_address']
            org.address2 = form_step3.cleaned_data['pub_address2']
            org.city = form_step3.cleaned_data['pub_city']
            org.state = form_step3.cleaned_data['pub_state']
            org.zipcode = form_step3.cleaned_data['pub_zipcode']
            org.country = form_step3.cleaned_data['pub_country']
            org.save()     
                
                
            if update:
                website = Website.objects.filter(publisher=org,is_default=True).update(**website_form.cleaned_data)
                org_contact = OrganizationContacts.objects.filter(organization=org).update(**form_contact_info.cleaned_data)
                org_payment = OrganizationPaymentInfo.objects.filter(organization=org).update(**form_payment.cleaned_data)
                '''
                user_form_cleaned = form_step2.cleaned_data
                del user_form_cleaned['password2']
                up = UserProfile.objects.get(organizations=org)
                up.user.first_name=user_form_cleaned['first_name']
                up.user.last_name=user_form_cleaned['last_name']
                up.user.email=user_form_cleaned['email']
                up.user.username=user_form_cleaned['username']
                if user_form_cleaned['password']:
                    up.user.set_password(user_form_cleaned['password'])
                up.user.save()
                up.save()
                '''
            else:
                website = Website.objects.create(publisher = org, is_default = True, **website_form.cleaned_data)
                org_contact = OrganizationContacts.objects.create(organization=org, email=form_step2.cleaned_data['email'], **form_contact_info.cleaned_data)
                org_payment = OrganizationPaymentInfo.objects.create(organization=org, **form_payment.cleaned_data)
                org_contact.save()
                org_payment.save()
                website.save()
                
                user_form_cleaned = form_step2.cleaned_data
                del user_form_cleaned['password2']
                u = User.objects.create(**user_form_cleaned)
                up = UserProfile.objects.create(user=u)
                up.organizations.add(org)

            
            for up in UserProfile.objects.filter(admin_level=ADMINLEVEL_ADMINISTRATOR):
                up.admin_assigned_organizations.add(org)
                up.save()
            return HttpResponseRedirect("/network/publisher/settings/")
    else:
        if oid:
            org = Organization.objects.get(pk=oid)
            org_contact = OrganizationContacts.objects.get(organization=org)
            org_payment_info = OrganizationPaymentInfo.objects.get(organization=org)
            website = Website.objects.get(publisher=org, is_default = True)
            up = UserProfile.objects.filter(organizations=org).select_related("user")[0]
            
            form_step2 = PublisherSignupForm2(True, initial={'first_name':up.user.first_name, 'last_name':up.user.last_name, 'email':up.user.email, })
            form_step3 = PublisherSignupForm3(True, initial={'company_name':org.company_name,'pub_address':org.address,'pub_address2':org.address2, 'pub_city':org.city,
                                                'pub_state':org.state,'pub_zipcode':org.zipcode, 'pub_country':org.country, 'pub_province':org.state})
            form_payment = PaymentInfoForm(instance=org_payment_info)
            form_contact_info = ContactInfoForm(instance=org_contact)
            website_form = WebsiteForm(instance=website)
        else:
            form_step2 = PublisherSignupForm2()
            form_step3 = PublisherSignupForm3()
            form_payment = PaymentInfoForm()
            form_contact_info = ContactInfoForm()
            website_form = WebsiteForm(organization=request.organization)
        
    return AQ_render_to_response(request, 'network/publisher/create.html', {
            'form_step2':form_step2,
            'form_step3':form_step3,
            'form_payment':form_payment,
            'website_form':website_form,
            'form_contact_info':form_contact_info,
        }, context_instance=RequestContext(request))