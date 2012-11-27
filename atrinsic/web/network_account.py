from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.db.models.query import QuerySet
from atrinsic.util.imports import *
from atrinsic.util.tabfunctions import *
from atrinsic.util.AceApi import create_company, update_company, search_company
from atrinsic.util.ApeApi import Ape

# Navigation Tab to View mappings for the Network Account Menu
tabset("Network", 0, "Account", "network_account_publisher_applications",
       [ ("Network Account Settings", "network_account",superadmin_tab),
         ("Publisher Applications", "network_account_publisher_applications"),
         ("Advertiser Applications", "network_account_advertiser_applications"),
         ("Advertiser Requests", "network_account_advertiser_requests"),
         ("Publisher Requests", "network_account_publisher_requests"),
         ])


@url(r"^/page/(?P<page>[0-9]+)/$", "network_account")
@url(r"^account/$","network_account")
@url(r"^account/page/(?P<page>[0-9]+)/$", "network_account")
@tab("Network","Account","Network Account Settings")
@superadmin_required
def network_account_settings(request, page=None):
    ''' View to list and manage the Network Administrators '''
    from atrinsic.base.models import User
    qs = User.objects.filter(userprofile__admin_level__gte=1)

    return object_list(request, queryset=qs, allow_empty=True, page=page,
                template_name='network/account.html', paginate_by=50, extra_context={
                'total_results' : qs.count(),
              })

@url(r"^account/users/add/$", "network_account_users_add")
@tab("Network","Account","Network Account Settings")
@superadmin_required
def network_account_users_add(request):
    ''' View to allow Network Admins to create new Users '''
    from forms import NetworkUserForm
    from atrinsic.base.models import User,UserProfile
    from atrinsic.util.user import generate_username
    if request.method == 'POST':
        form = NetworkUserForm(request.POST)

        if form.is_valid():
            u = User.objects.create(first_name=form.cleaned_data['first_name'], last_name=form.cleaned_data['last_name'],
                            email=form.cleaned_data['email'], username=generate_username(form.cleaned_data['email']))

            u.set_password(form.cleaned_data['password'])
            u.save()

            up = UserProfile.objects.create(admin_level=form.cleaned_data['admin_level'], user=u)
            
            return HttpResponseRedirect('/network/')
    else:
        form = NetworkUserForm()

    return AQ_render_to_response(request, 'network/users-add.html', {
            'form' : form,
        }, context_instance=RequestContext(request))


@url(r"^account/users/(?P<user_id>\d+)/delete/$","network_account_users_delete")
@tab("Network","Account","Network Account Settings")
@superadmin_required
def network_account_users_delete(request, user_id):
    ''' View to allow Network Admins to delete Users '''
    from atrinsic.base.models import User
    u = User.objects.get(id=user_id)
    u.delete()

    return HttpResponseRedirect('/network/')
  
 
@url(r"^account/users/edit/(?P<user_id>\d+)/$", "network_account_users_edit")
@tab("Network","Account","Network Account Settings")
@superadmin_required
def network_account_users_edit(request, user_id):
    ''' View to allow Network Admins the ability to edit a User and their UserProfile '''
    from atrinsic.base.models import User
    from forms import NetworkUserEditForm
    
    u = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = NetworkUserEditForm(request.POST)
        form.user_id = u.id

        if form.is_valid():

            u.first_name = form.cleaned_data['first_name']
            u.last_name = form.cleaned_data['last_name']
            u.email = form.cleaned_data['email']

            if form.cleaned_data['password'] and len(form.cleaned_data['password']) > 0:
                u.set_password(form.cleaned_data['password'])
                u.save()

            up = u.userprofile_set.all()[0]
            up.admin_level=form.cleaned_data['admin_level']
            up.save()
            
            return HttpResponseRedirect('/network/')
    else:
        form = NetworkUserEditForm(initial={ 'first_name' : u.first_name, 'last_name' : u.last_name,
                                    'email' : u.email, 'admin_level' : u.userprofile_set.all()[0].admin_level, })
        form.user_id = u.id

    return AQ_render_to_response(request, 'network/users-edit.html', {
            'u': u,
            'form' : form,
        }, context_instance=RequestContext(request))



@url(r"^$","network_account_publisher_applications")
@url(r"^account/publisher/applications/$","network_account_publisher_applications")
@url(r"^account/publisher/applications/page/(?P<page>[0-9]+)/$", "network_account_publisher_applications")
@tab("Network","Account","Publisher Applications")
@admin_required
def network_account_publisher_applications(request, page=None):
    ''' View to show and manage Publisher Account Applications  '''
    from atrinsic.base.models import Organization
    
    from django.db import connection, transaction
    cursor = connection.cursor()
    qs = Organization.objects.filter(org_type=ORGTYPE_PUBLISHER,status=ORGSTATUS_UNAPPROVED).extra(
    select={
        'phone': 'select phone FROM base_organizationcontacts oc WHERE oc.organization_id = base_organization.id ORDER BY ID limit 1'
    }).extra(select={
        'fax': 'select fax FROM base_organizationcontacts oc WHERE oc.organization_id = base_organization.id ORDER BY ID limit 1'
    }).extra(select={
        'email': 'select email FROM base_organizationcontacts oc WHERE oc.organization_id = base_organization.id ORDER BY ID limit 1'
    }).extra(select={
        'firstname': 'select firstname FROM base_organizationcontacts oc WHERE oc.organization_id = base_organization.id ORDER BY ID limit 1'
    }).extra(select={
        'lastname': 'select lastname FROM base_organizationcontacts oc WHERE oc.organization_id = base_organization.id ORDER BY ID limit 1'
    }).extra(select={
        'currency': 'select c.name FROM base_organizationpaymentinfo opi INNER JOIN base_currency c on opi.currency_id = c.order WHERE opi.organization_id = base_organization.id ORDER BY ID limit 1'
    }).extra(select={
        'publishervertical': 'select v.name FROM base_website w INNER JOIN base_publishervertical v on w.vertical_id = v.order WHERE w.publisher_id = base_organization.id ORDER BY ID limit 1'
    }).extra(select={
        'promo_method': 'select name FROM base_website w INNER JOIN base_promotionmethod v on w.promo_method_id  = v.order WHERE w.publisher_id = base_organization.id ORDER BY ID limit 1'
    }).extra(select={
        'url': 'select url FROM base_website oc WHERE oc.publisher_id = base_organization.id ORDER BY ID limit 1'
    }
    )
    return AQ_render_to_response(request, 'network/publisher-applications.html', {
        'qs': qs,
    }, context_instance=RequestContext(request))

@url(r"^account/publisher/applications/viewcontact/(?P<id>[0-9]+)/$","network_account_publisher_applications_view_contact")
@tab("Network","Account","Publisher Applications")
@admin_required
def network_account_publisher_applications_view_contact(request, id=None):
    ''' View that displays a specific Publisher Application '''

    publisher = get_object_or_404(OrganizationContacts, organization=id)
    return AQ_render_to_response(request, 'network/publisher-applications-view.html', {
            'publisher' : publisher,
        }, context_instance=RequestContext(request))


@url(r"^account/publisher/applications/view/(?P<id>[0-9]+)/$","network_account_publisher_applications_view")
@tab("Network","Account","Publisher Applications")
@admin_required
def network_account_publisher_applications_view(request, id=None):
    ''' View that displays a specific Publisher Application '''
    from atrinsic.base.models import Organization
    publisher = get_object_or_404(Organization, id=id)

    return AQ_render_to_response(request, 'network/publisher-applications-view.html', {
            'publisher' : publisher,
        }, context_instance=RequestContext(request))


@url(r"^account/advertiser/applications/view/(?P<id>[0-9]+)/$","network_account_advertiser_applications_view")
@tab("Network","Account","Advertiser Applications")
@admin_required
def network_account_advertiser_applications_view(request, id=None):
    ''' View that displays a specific Advertiser Application '''
    from atrinsic.base.models import AdvertiserApplication
    application = get_object_or_404(AdvertiserApplication, id=id)

    return AQ_render_to_response(request, 'network/advertiser-applications-view.html', {
            'application' : application,
        }, context_instance=RequestContext(request))

@url(r"^account/advertiser/applications/delete/(?P<id>[0-9]+)/$","network_account_advertiser_applications_delete")
@tab("Network","Account","Advertiser Applications")
@superadmin_required
def network_account_advertiser_applications_delete(request, id=None):
    ''' View to allow Network Admins to delete Advertiser Applications'''
    from atrinsic.base.models import AdvertiserApplication
    if id:
        aApp = AdvertiserApplication.objects.get(id=id)
        aApp.delete()
    elif request.GET.has_ley('marked_for_deletion'):
        aApp = AdvertiserApplication.objects.filter(id__in=request.GET.getlist('marked_for_deletion'))
    

    return HttpResponseRedirect('/network/account/advertiser/applications/')
    
@url(r"^account/advertiser/applications/create/(?P<id>[0-9]+)/$","network_account_advertiser_applications_create")
@tab("Network","Account","Advertiser Applications")
@admin_required
def network_account_advertiser_applications_create(request, id=None):
    ''' View to allow Network Admins the ability to create a new Advertiser Organization
        using their AdvertiserApplication as a base template.  This view creates the
        initial User login as well. '''
    from atrinsic.base.models import AdvertiserApplication,Currency,Organization,UserProfile,User,OrganizationContacts,OrganizationPaymentInfo,OrganizationCurrency
    from forms import NetworkAdvertiserEditForm,UserForm
    application = get_object_or_404(AdvertiserApplication, id=id)
    application.company_name = application.organization_name

    if request.method == 'POST':
        form = NetworkAdvertiserEditForm(request.POST)
        user_form = UserForm(request.POST)

        if form.is_valid() and user_form.is_valid():
            if form.cleaned_data["country"] == "CA":
                form.cleaned_data["state"] = form.cleaned_data['province']
            del form.cleaned_data['province']
            del form.cleaned_data['salesperson']
            
            curID = form.cleaned_data['currency']
            del form.cleaned_data['currency']
            org = Organization.objects.create(org_type = ORGTYPE_ADVERTISER, status = ORGSTATUS_TEST, **form.cleaned_data)
            org.save()

            orgCur = OrganizationCurrency.objects.create(advertiser = org, currency = Currency.objects.get(order=curID))
            
            u = User.objects.create(username=user_form.cleaned_data['email'], email=user_form.cleaned_data['email'],
                        first_name=user_form.cleaned_data['first_name'], last_name=user_form.cleaned_data['last_name'])

            u.set_password(user_form.cleaned_data['password'])
            u.save()

            up = UserProfile.objects.create(user=u)
            up.organizations.add(org)
            up.save()

            del form.cleaned_data['show_alias']
            del form.cleaned_data['company_name']
            del form.cleaned_data['company_alias']
            del form.cleaned_data['ticker']
            del form.cleaned_data['is_private']
            del form.cleaned_data['ticker_symbol']
            del form.cleaned_data['vertical']
            del form.cleaned_data['brandlock_key']
            del form.cleaned_data['brandlock']
            
            org_contacts = OrganizationContacts.objects.create(organization=org,firstname=application.contact_firstname, lastname=application.contact_lastname,email=application.contact_email,phone=application.contact_phone,fax=application.contact_fax)
            org_contacts.save()
            
            orgPayeeInfo = OrganizationPaymentInfo(organization=org)
            orgPayeeInfo.save()
            
            # Assign all ADMINLEVEL_ADMINISTRATOR to this
            for up in UserProfile.objects.filter(admin_level=ADMINLEVEL_ADMINISTRATOR):
                up.admin_assigned_organizations.add(org)
                up.save()


            application.delete()
            
            #ACE INSERT IF NO MATCHES ARE FOUND
            matches = search_company(application.organization_name)
            if len(matches) > 0:
                #redirect to new url and template to display list. Chose or create
                return AQ_render_to_response(request, 'network/search-ace.html', {'matches':matches,'orgId':org.id}, context_instance=RequestContext(request))         
            else:
                create_company(org)
                
            #args = {}
            #args["salesrep"] = form.cleaned_data['salesperson']
            #createIO(advertiser, args)
            
            
                                                
            return HttpResponseRedirect('/network/account/advertiser/applications/')
    else:
        #form = OrganizationForm(initial=application.__dict__)
        form = NetworkAdvertiserEditForm(initial=application.__dict__)
        user_form = UserForm(initial= {
                            'first_name' : application.contact_firstname,
                            'last_name' : application.contact_lastname,
                            'email' : application.contact_email,
                        })

    return AQ_render_to_response(request, 'network/advertiser-applications-create.html', {
            'application' : application,
            'form' : form,
            'user_form' :  user_form,
        }, context_instance=RequestContext(request))


@url(r"^account/publisher/applications/approve/(?P<id>[0-9]+)/$","network_account_publisher_applications_approve")
@tab("Network","Account","Publisher Applications")
@admin_required
def network_account_publisher_applications_approve(request, id=None):
    ''' View to allow Network Admins the ability to approve a publisher Application '''
    from atrinsic.base.models import Organization,OrganizationContacts
    from django.core.mail import EmailMultiAlternatives
    from forms import TickerForm
    publisher = get_object_or_404(Organization, id=id)
    
    no_email_sent = False
    if publisher.status != ORGSTATUS_LIVE:
        try:
            pubContact = OrganizationContacts.objects.get(email__isnull=False, organization=publisher)
            subject, from_email, to = 'Atrinsic Affiliate Network Publisher Application Status', 'admin@network.atrinsic.com', pubContact.email
            text_content = """
        Dear """ + pubContact.firstname + ' ' + pubContact.lastname + """,
        
        Congratulations!  Your application to the Atrinsic Affiliate Network has been approved.
        
        You may now login to the Atrinsic Affiliate Network http://network.atrinsic.com/accounts/login/ with your username and password created at the time of sign up.  Your username is your email address used at time of sign-up.  If you have forgotten your login password, please visit our login page to reset the password for your account.
        
        You may reset your password at any time by visiting "Settings" and updating your individual password in the "Users" section of the interface.
        
        When you are ready, just follow the three easy steps below:
        
        1.  Join Programs
        Visit "Manage Advertisers" and "Find New Advertisers" to location programs that interest you. Apply for any and all programs that you would like to join. Advertisers will notify you with approval via email.
        
        2.  Create Links
        Once you are approved to partner with Advertiser, log in to your account again. Find the merchant on the "Manage Advertisers" section of the interface.  Select "Get Links" and then, the type of link you would like to place on your website, and copy and paste the appropriate code directly into your site.
        
        3.  Run Reports
        Once Advertiser links are placed in your website, you can login to check your reports at any time to see how your links are performing.
        
        Choose to partner with Advertisers who offer products and services that are most likely to be of interest to your visitors. Once you have chosen appropriate Advertisers, you can increase the likelihood of purchase from your site by placing product, text, banners, product links and content on your site to provide more relevance for visitors.  Use our reports to evaluate your successes, so that you can focus on making all your partnerships work.
        
        Please contact us at publishers@network.atrinsic.com with any questions as they may arise.
        
        We look forward to a long and successful partnership with you!
        
        
        Warm Regards,
        
        The Atrinsic Affiliate Network Publisher Team
        publishers@network.atrinsic.com
        """
            html_content = """
        Dear """ + pubContact.firstname + ' ' + pubContact.lastname + """,<br>
        <br>
        Congratulations!  Your application to the Atrinsic Affiliate Network has been approved.<br>
        <br>
        You may now <a href="http://network.atrinsic.com/accounts/login/">login to the Atrinsic Affiliate Network</a> with your username and password created at the time of sign up.  Your username is your email address used at time of sign-up.  If you have forgotten your login password, please visit our login page to reset the password for your account.<br>
        <br>
        You may reset your password at any time by visiting "Settings" and updating your individual password in the "Users" section of the interface.<br>
        <br>
        When you are ready, just follow the three easy steps below:<br>
        <br>
        1.  Join Programs<br>
        Visit "Manage Advertisers" and "Find New Advertisers" to location programs that interest you. Apply for any and all programs that you would like to join. Advertisers will notify you with approval via email.<br>
        <br>
        2.  Create Links<br>
        Once you are approved to partner with Advertiser, log in to your account again. Find the merchant on the "Manage Advertisers" section of the interface.  Select "Get Links" and then, the type of link you would like to place on your website, and copy and paste the appropriate code directly into your site.<br>
        <br>
        3.  Run Reports<br>
        Once Advertiser links are placed in your website, you can login to check your reports at any time to see how your links are performing.<br>
        <br>
        Choose to partner with Advertisers who offer products and services that are most likely to be of interest to your visitors. Once you have chosen appropriate Advertisers, you can increase the likelihood of purchase from your site by placing product, text, banners, product links and content on your site to provide more relevance for visitors.  Use our reports to evaluate your successes, so that you can focus on making all your partnerships work.<br>
        <br>
        Please contact us at <a href="mailto:publishers@network.atrinsic.com">publishers@network.atrinsic.com</a> with any questions as they may arise.<br>
        <br>
        We look forward to a long and successful partnership with you!<br>
        <br>
        <br>
        Warm Regards,<br>
        <br>
        The Atrinsic Affiliate Network Publisher Team<br>
        <a href="mailto:publishers@network.atrinsic.com">publishers@network.atrinsic.com</a>"""
            
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        except:
            no_email_sent = True
    
        #create_company(publisher)
        
        publisher.status = ORGSTATUS_LIVE
        publisher.date_joined = datetime.datetime.now()
        publisher.save()
    
    #ACE INSERT IF NO MATCHES ARE FOUND
    matches = search_company(publisher.company_name)
    if len(matches) > 0:
        
        if request.method == 'POST':
            form = TickerForm(request.POST)

        if form.is_valid():
            publisher.ticker = form.cleaned_data['ticker']
            publisher.save()
            
        #redirect to new url and template to display list. Chose or create
        if no_email_sent == True:
            error_msg = 'An error occured when trying to contact the publisher automaticly to advise him of the approval. Please attempt this manualy. This is likely cause by the publisher not entering valid contact info.'
        else:
            error_msg = ''
        
        return AQ_render_to_response(request, 'network/search-ace.html', {
                'matches':matches,
                'orgId':publisher.id,
                'error':error_msg,
            }, context_instance=RequestContext(request))         
    else:
        create_company(publisher)


    if request.method == 'POST':
        form = TickerForm(request.POST)

        if form.is_valid():
            publisher.ticker = form.cleaned_data['ticker']
            publisher.save()

            return HttpResponseRedirect('/network/account/publisher/applications/')

    else:
        form = TickerForm(initial={ 'ticker' : publisher.ticker, })


    if no_email_sent == True:
       return AQ_render_to_response(request, 'network/publisher-applications-deny.html', {
                'publisher' : publisher,
                'error':'An error occured when trying to contact the publisher automaticly to advise him of the approval. Please attempt this manualy. This is likely cause by the publisher not entering valid contact info.',
            }, context_instance=RequestContext(request))
    else:
        return AQ_render_to_response(request, 'network/publisher-applications-approve.html', {
                'publisher' : publisher,
                'form' : form,
            }, context_instance=RequestContext(request))


@url(r"^account/publisher/applications/deny/(?P<id>[0-9]+)/$","network_account_publisher_applications_deny")
@url(r"^account/publisher/applications/deny/$","network_account_publisher_applications_deny")
@tab("Network","Account","Publisher Applications")
@admin_required
@url(r"^account/publisher/applications/api_deny/(?P<id>[0-9]+)/$","network_account_publisher_applications_deny")
def network_account_publisher_applications_deny(request, id=None):
    ''' View to allow Network Admins the ability to deny a Publisher Application '''
    from django.core.mail import EmailMultiAlternatives
    from atrinsic.base.models import Organization,OrganizationContacts
    redir = True
    id_list = []
    if not id:
        id_list = request.GET.getlist('publisher_id')
        redir = False
    else:
        id_list.append(id)
    publisher_list = []
    print id
    for id in id_list:
        publisher = get_object_or_404(Organization, id=id)
        publisher_list.append(publisher)
        try:
            pubContact = OrganizationContacts.objects.get(email__isnull=False, organization=publisher)
            subject = 'Atrinsic Affiliate Network Publisher Application Status'
            from_email = 'admin@network.atrinsic.com'
            to = pubContact.email
            
            text_content = """Dear """ + pubContact.firstname + ' ' + pubContact.lastname + """,
            
            Thank you for your interest in the Atrinsic Affiliate Network. 
            We regret to inform you that after reviewing your website, we have chosen not to accept your application at this time.
            
            Your application may have been declined due to one or more of the following:
            - Inability to access your website
            - Website is not yet live
            - Inability to verify the phone number submitted on your application
            - Inability to verify other information contained within your application
            - Website is not relevant to one or more of our merchant programs
            
            If you feel an error has been made, or if you would like to discuss further, please contact us at <a href="mailto:publisherapplication@network.atrinsic.com">publisherapplication@network.atrinsic.com</a>.  
            
            Sincerely,
            
            The Atrinsic Affiliate Network Publisher Team
            <a href="mailto:publisherapplication@network.atrinsic.com">publisherapplication@network.atrinsic.com</a>
            """
            html_content = """Dear """ + pubContact.firstname + ' ' + pubContact.lastname + """,<br>
            <br>
            Thank you for your interest in the Atrinsic Affiliate Network. <br>
            We regret to inform you that after reviewing your website, we have chosen not to accept your application at this time.<br>
            <br>
            Your application may have been declined due to one or more of the following:<br>
            - Inability to access your website<br>
            - Website is not yet live<br>
            - Inability to verify the phone number submitted on your application<br>
            - Inability to verify other information contained within your application<br>
            - Website is not relevant to one or more of our merchant programs<br>
            <br>
            If you feel an error has been made, or if you would like to discuss further, please contact us at <a href="mailto:publisherapplication@network.atrinsic.com">publisherapplication@network.atrinsic.com</a>.  <br>
            <br>
            Sincerely,<br>
            <br>
            The Atrinsic Affiliate Network Publisher Team<br>
            <a href="mailto:publisherapplication@network.atrinsic.com">publisherapplication@network.atrinsic.com</a>"""
        
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
    
            try:
                msg.send()
            except:
                pass
                """return AQ_render_to_response(request, 'network/publisher-applications-deny.html', {
                    'publisher' : publisher,
                    'error':'An error occured when trying to contact the publisher automaticly to advise him of the denial. Please attempt this manualy. This is likely cause by the publisher not entering valid contact info.',
                }, context_instance=RequestContext(request))"""
        except:
            pass    
        publisher.status = ORGSTATUS_DEACTIVATED
        publisher.save()

    if redir:
        return HttpResponseRedirect('/network/account/publisher/applications/')

    return AQ_render_to_response(request, 'network/publisher-applications-deny.html', {
            'publisher_list' : publisher_list,
        }, context_instance=RequestContext(request))


@url(r"^account/advertiser/requests/$","network_account_advertiser_requests")
@url(r"^account/advertiser/requests/page/(?P<page>[0-9]+)/$", "network_account_advertiser_requests")
@tab("Network","Account","Advertiser Requests")
@admin_required
def network_account_advertiser_requests(request, page=None):
    ''' View to displays all Advertiser DataFeed requests '''
    from atrinsic.base.models import DataFeed
    qs = DataFeed.objects.filter(status=STATUS_PENDING)

    return object_list(request, queryset=qs, allow_empty=True, page=page,
                template_name='network/advertiser-requests.html', paginate_by=50, extra_context={
                'total_results' : qs.count(),
              })

@url(r"^account/advertiser/requests/(?P<id>[0-9]+)/approve/$", "network_account_advertiser_requests_approve")
@tab("Network","Account","Advertiser Requests")
@admin_required
def network_account_advertiser_requests_approve(request, id):
    ''' View to approve an Advertiser DataFeed Request '''
    from atrinsic.base.models import DataFeed, ProgramTermAction, ProgramTerm
    
    d = get_object_or_404(DataFeed, id=id)
    # Get default Program Term, Action so we can get the Adv.'s redirect_id
    pt = ProgramTerm.objects.get(advertiser=d.advertiser,is_default=True)
    ptAction = ProgramTermAction.objects.select_related("action").get(program_term=pt)
    
    print ptAction.action.name
    apeClient = Ape()
    d.ape_url_id = apeClient.execute_url_create(ptAction.action, None, d)
    d.status = STATUS_LIVE
    d.save()

    return HttpResponseRedirect('/network/account/advertiser/requests/')


@url(r"^account/advertiser/requests/(?P<id>[0-9]+)/deny/$", "network_account_advertiser_requests_deny")
@tab("Network","Account","Advertiser Requests")
@admin_required
def network_account_advertiser_requests_deny(request, id):
    ''' View to approve an Advertiser DataFeed Request '''
    from atrinsic.base.models import DataFeed
    d = get_object_or_404(DataFeed, id=id)
    d.status = STATUS_DEACTIVATED
    d.save()

    return HttpResponseRedirect('/network/account/advertiser/requests/')


@url(r"^account/publisher/requests/$","network_account_publisher_requests")
@url(r"^account/publisher/requests/page/(?P<page>[0-9]+)/$", "network_account_publisher_requests")
@tab("Network","Account","Publisher Requests")
@admin_required
def network_account_publisher_requests(request, page=None):
    ''' View to dispplay all pending Publisher DataTransfer requests and PublisherInquiries. '''
    from atrinsic.base.models import DataTransfer,PublisherDataFeed,PublisherInquiry,Organization
    qs = []
    qs.extend(PublisherDataFeed.objects.filter())
    qs.extend(DataTransfer.objects.filter(status=STATUS_PENDING))
    #qs.extend(PublisherInquiry.objects.filter(status=INQUIRYSTATUS_UNRESOLVED))
    qs.extend(Organization.objects.filter(sid_status=STATUS_PENDING)) 	
    
    #objDataTransfer = PublisherDataFeed.objects.filter()
    #objPubInquiry = PublisherInquiry.objects.filter(status=INQUIRYSTATUS_UNRESOLVED)
    #objSIDRequest = Organization.objects.filter(sid_status=STATUS_PENDING)

    return object_list(request, queryset=qs, allow_empty=True, page=page,
                template_name='network/publisher-requests.html', paginate_by=50, extra_context={
                'total_results' : len(qs),
                #'objDataTransfer': objDataTransfer, 
                #'objPubInquiry': objPubInquiry, 
                #'objSIDRequest': objSIDRequest,
              })


@url(r"^account/advertiser/applications/$","network_account_advertiser_applications")
@url(r"^account/advertiser/applications/page/(?P<page>[0-9]+)/$", "network_account_advertiser_applications")
@tab("Network","Account","Advertiser Applications")
@admin_required
def network_account_advertiser_applications(request, page=None):
    ''' View to display all Advertiser Applications '''
    from atrinsic.base.models import AdvertiserApplication
    qs = AdvertiserApplication.objects.all() 

    return object_list(request, queryset=qs, allow_empty=True, page=page,
                template_name='network/advertiser-applications.html', paginate_by=50, extra_context={
                'total_results' : qs.count(),
              })

@url(r"^account/publisher/sid_requests/approve/(?P<id>[0-9]+)/$", "network_account_publisher_sidrequests_approve")
@tab("Network","Account","Publisher Requests")
@admin_required
def network_account_publisher_sidrequests_approve(request, id):
    from atrinsic.base.models import Organization
    publisher = get_object_or_404(Organization, id=id)

    publisher.sid_status = STATUS_LIVE
    publisher.save()

    return HttpResponseRedirect('/network/account/publisher/requests/')


@url(r"^account/publisher/sid_requests/deny/(?P<id>[0-9]+)/$", "network_account_publisher_sidrequests_deny")
@tab("Network","Account","Publisher Requests")
@admin_required
def network_account_publisher_sidrequests_deny(request, id):
    from atrinsic.base.models import Organization
    publisher = get_object_or_404(Organization, id=id)

    publisher.sid_status = STATUS_DEACTIVATED
    publisher.save()

    return HttpResponseRedirect('/network/account/publisher/requests/')


@url(r"^account/publisher/datatransfer_requests/approve/(?P<id>[0-9]+)/$", "network_account_publisher_datatransfer_approve")
@tab("Network","Account","Publisher Requests")
@admin_required
def network_account_publisher_datatransfer_approve(request, id):
    from atrinsic.base.models import DataTransfer
    d = get_object_or_404(DataTransfer, id=id)
    
    d.status = STATUS_LIVE
    d.save()

    return HttpResponseRedirect('/network/account/publisher/requests/')

@url(r"^account/publisher/datatransfer_requests/deny/(?P<id>[0-9]+)/$", "network_account_publisher_datatransfer_deny")
@tab("Network","Account","Publisher Requests")
@admin_required
def network_account_publisher_datatransfer_deny(request, id):
    from atrinsic.base.models import DataTransfer
    d = get_object_or_404(DataTransfer, id=id)

    d.status = STATUS_DEACTIVATED
    d.save()

    return HttpResponseRedirect('/network/account/publisher/requests/')
    
    
@url(r"^account/search/acematch/$", "network_ace_match")
@superadmin_required
def network_ace_match(request):
    from atrinsic.util.AceApi import search_company, create_company
    from atrinsic.base.models import Organization
    from forms import TickerForm

    if request.POST:
        currentOrg = request.POST['currentOrg']
        useOrg = request.POST['company']
        org = Organization.objects.get(id=currentOrg)
        if useOrg == '0':
            create_company(org)
        else:
            org.ace_id = useOrg
            org.save()    
        
    if org.org_type == 1:
        form = TickerForm(initial={ 'ticker' : org.ticker, })

        return HttpResponseRedirect('/network/')
    else:        
        return HttpResponseRedirect('/network/account/advertiser/applications/')
