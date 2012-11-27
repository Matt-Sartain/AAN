from django.template import RequestContext
from atrinsic.util.imports import *
from atrinsic.util.ApeApi import Ape

# Navigation Tab to View mappings for the Publisher Settings Menu
tabset("Publisher",6,"Settings","publisher_settings",
       [("Settings","publisher_settings"),
        ("Users","publisher_settings_users"),
        ('Payment Info', 'publisher_settings_payment'),
        ("Alerts","publisher_settings_alerts"),
        ('Web Sites', 'publisher_settings_websites'),
        ('Incentive Site Settings', 'publisher_settings_incentive'),
        ("Data Feeds","publisher_settings_feeds"),
        ("Kenshoo","publisher_kenshoo"),
        ("Piggyback Pixels","publisher_piggyback_pixel"),
        ("Real Time Box","real_time_box_settings")])

@url("^settings/$", "publisher_settings")
@tab("Publisher","Settings","Settings")
@publisher_required
@register_api(None)
def publisher_settings(request):
    ''' View to display a Publishers Organizational Information and a link to Edit it '''
    from atrinsic.base.models import OrganizationContacts, PublisherVertical
    
    try:
        orgContact = OrganizationContacts.objects.get(organization=request.organization)
    except:
        orgContact = None
    
    return AQ_render_to_response(request, 'publisher/settings/index.html', {
            'verticals' : PublisherVertical.objects.filter(is_adult=request.organization.is_adult).order_by('order'),
            'contactInfo': orgContact,
        }, context_instance=RequestContext(request))


@url("^settings/vertical/add/$", "publisher_settings_vertical_add")
@tab("Publisher","Settings","Settings")
@publisher_required
@register_api(None)
def publisher_settings_vertical_add(request):
    ''' Add a Secondary Vertical to a Publisher
    '''
    from atrinsic.base.models import PublisherVertical
    
    id = request.REQUEST.get('vertical', None)

    if id:
        v = get_object_or_404(PublisherVertical, order=id)

        request.organization.secondary_vertical.add(v)

    return HttpResponseRedirect('/publisher/settings')


@url("^settings/vertical/remove/(?P<id>[0-9]+)/$", "publisher_settings_vertical_remove")
@tab("Publisher","Settings","Settings")
@publisher_required
@register_api(None)
def publisher_settings_vertical_remove(request, id):
    ''' Remove a Secondary Vertical from a Publisher
    '''
    from atrinsic.base.models import PublisherVertical
    v = get_object_or_404(PublisherVertical, order=id)

    request.organization.secondary_vertical.remove(v)
       
    return HttpResponseRedirect('/publisher/settings/')

 
@url("^settings/edit/$", "publisher_settings_edit")
@tab("Publisher","Settings","Settings")
@publisher_required
@register_api(None)
def publisher_settings_edit(request):
    ''' View to allow a Publisher to edit their Organization Information
        and Settings '''
    from atrinsic.base.models import OrganizationContacts
    from forms import ContactInfoFormSmall, PublisherOrganizationForm
    
    try:
        org,new = OrganizationContacts.objects.get_or_create(organization=request.organization)
    except:
        org = None
        
    if request.method == "POST":
        form = PublisherOrganizationForm(request.POST)
        formCI = ContactInfoFormSmall(request.POST)

        if form.is_valid() and formCI.is_valid():
            print"VALID"
            o = request.organization
            for k, v in form.cleaned_data.items():
                setattr(o, k, v)
            o.save()
            print "OrgSaved"
            if org != None:
                org.firstname = request.POST.get('firstname', None)
                org.lastname = request.POST.get('lastname', None)
                org.email = request.POST.get('email', None)
                org.phone = request.POST.get('phone', None)
                org.fax = request.POST.get('fax', None)
                org.save()
            print "load new"
            formCI.cleaned_data["organization"] = request.organization
            return HttpResponseRedirect('/publisher/settings/')
    else:
        vals = { }
        for v in [ 'company_name', 'address', 'address2', 'city', 'country', 'state', 'zipcode',]:
            vals[v] = getattr(request.organization, v)

        vals['province'] = vals['state']
        form = PublisherOrganizationForm(initial=vals)

        if org != None:
            cvals = { }
            for v in [ 'firstname', 'lastname', 'email', 'phone', 'fax',]:
                cvals[v] = getattr(org, v)
        else:
            cvals = {'firstname':'', 
                     'lastname':'',
                     'email':'', 
                     'phone':'', 
                     'fax':'',}

        formCI = ContactInfoFormSmall(instance = OrganizationContacts.objects.get(organization = request.organization))
    return AQ_render_to_response(request, 'publisher/settings/edit.html', {
        'form' : form,
        'formCI':formCI,
        }, context_instance=RequestContext(request))


@url("^settings/users/$", "publisher_settings_users")
@tab("Publisher","Settings","Users")
@publisher_required
@register_api(api_context=('id', 'email', 'first_name', 'last_name', ))
def publisher_settings_users(request, page=None):
    ''' View to display a Publishers Users and links to add new ones,
        and edit existing ones.  '''

    qs = request.organization.get_users()
    print 'test'
    return object_list(request, queryset=qs, allow_empty=True, page=page,
                template_name='publisher/settings/users.html', paginate_by=50, extra_context={
                'total_results' : qs.count(),
            })

@url("^settings/users/add/$", "publisher_settings_users_add")
@tab("Publisher","Settings","Users")
@publisher_required
@register_api(None)
def publisher_settings_users_add(request):
    ''' View to allow a Publisher the ability to create a new User '''
    from atrinsic.base.models import User, UserProfile
    from forms import UserForm
    print 'test5'
    if request.method == "POST":
        form = UserForm(request.POST)

        if form.is_valid():
            u = User()

            u.first_name = form.cleaned_data['first_name']
            u.last_name = form.cleaned_data['last_name']
            u.email = form.cleaned_data['email']
            u.username = u.email.replace('@', '-')

            u.set_password(form.cleaned_data['password'])
            u.save()

            up = UserProfile.objects.create(user=u)
            up.organizations.add(request.organization)

            return HttpResponseRedirect('/publisher/settings/users/')
    else:
        form = UserForm()

    return AQ_render_to_response(request, 'publisher/settings/users-add.html', {
            'form' : form,
        }, context_instance=RequestContext(request))


@url("^settings/users/delete/(?P<id>[0-9]+)/$", "publisher_settings_users_delete")
@tab("Publisher","Settings","Users")
@publisher_required
@register_api(None)
def publisher_settings_users_delete(request, id):
    ''' Delete a user from a Publisher's Organization '''
    from atrinsic.base.models import User
    
    try:
        u = User.objects.get(id=id)

        if request.organization not in u.userprofile_set.all()[0].organizations.all():
            raise Http404

        if request.organization.network_admin != u:
            u.delete()

    except User.DoesNotExist:
        raise Http404

    return HttpResponseRedirect('/publisher/settings/users/')

@url("^settings/users/makeadmin/(?P<id>[0-9]+)/$", "publisher_settings_users_makemanager")
@tab("Publisher","Settings","Users")
@publisher_required
@register_api(None)
def publisher_settings_users_makemanager(request, id):
    ''' View to allow a Publisher to classify a User as a Manager '''
    from atrinsic.base.models import User
    
    try:
        u = User.objects.get(id=id)

        if request.organization not in u.userprofile_set.all()[0].organizations.all():
            raise Http404

        if request.organization.network_admin != u:
            request.organization.network_admin = u
            request.organization.save()
            

    except User.DoesNotExist:
        raise Http404

    return HttpResponseRedirect('/publisher/settings/users/')


@url("^settings/users/edit/(?P<id>[0-9]+)/$", "publisher_settings_users_edit")
@tab("Publisher","Settings","Users")
@publisher_required
@register_api(None)
def publisher_settings_users_edit(request, id):
    ''' View to edit a Publisher's User '''
    from atrinsic.base.models import User
    from forms import UserEditForm
    
    try:
        u = User.objects.get(id=id)

        if request.organization not in u.userprofile_set.all()[0].organizations.all():
            raise Http404

    except User.DoesNotExist:
        raise Http404

    if request.method == "POST":
        form = UserEditForm(request.POST)
        form.user_id = u.id

        if form.is_valid():
            u.first_name = form.cleaned_data['first_name']
            u.last_name = form.cleaned_data['last_name']
            u.email = form.cleaned_data['email']
            u.username = u.email.replace('@', '-')

            if form.cleaned_data.get("password",None):
                u.set_password(form.cleaned_data['password'])

            u.save()

            return HttpResponseRedirect('/publisher/settings/users/')
    else:
        form = UserEditForm(initial={
                'first_name' : u.first_name,
                'last_name' : u.last_name,
                'email' : u.email,
            })

    return AQ_render_to_response(request, 'publisher/settings/users-edit.html', {
            'u' : u,
            'form' : form,
        }, context_instance=RequestContext(request))


@url("^settings/alerts/$", "publisher_settings_alerts")
@tab("Publisher","Settings","Alerts")
@publisher_required
@register_api(api_context=('id', 'get_alert_field_display', 'get_time_period_display', 'change', ))
def publisher_settings_alerts(request, page=None):
    ''' View Publishers Alert Settings '''

    qs = request.organization.alert_set.all()

    return object_list(request, queryset=qs, allow_empty=True, page=page,
                template_name='publisher/settings/alerts.html', paginate_by=50, extra_context={
                'total_results' : qs.count(),
            })

@url("^settings/alerts/add/$", "publisher_settings_alerts_add")
@tab("Publisher","Settings","Alerts")
@publisher_required
@register_api(None)
def publisher_settings_alerts_add(request):
    ''' View to allow a Publisher to Add an Alert '''
    from atrinsic.base.models import Alert
    from forms import AlertForm
    
    if request.method == "POST":
        form = AlertForm(request.POST)

        if form.is_valid():
            change = form.cleaned_data['change']

            if not form.cleaned_data['up_or_down']:
                change = change * -1.00

            Alert.objects.create(organization=request.organization,
                alert_field=form.cleaned_data['alert_field'],
                time_period=form.cleaned_data['time_period'],
                change=str(change))

            return HttpResponseRedirect('/publisher/settings/alerts/')
    else:
        form = AlertForm()

    return AQ_render_to_response(request, 'publisher/settings/alerts-add.html', {
            'form' : form,
        }, context_instance=RequestContext(request))


@url("^settings/alerts/edit/(?P<id>[0-9]+)/$", "publisher_settings_alerts_edit")
@tab("Publisher","Settings","Alerts")
@publisher_required
@register_api(None)
def publisher_settings_alerts_edit(request, id):
    ''' View to allow a Publisher the ability to edit an Alert '''
    from forms import AlertForm
    
    alert = get_object_or_404(request.organization.alert_set, id=id)

    if request.method == "POST":
        form = AlertForm(request.POST)

        if form.is_valid():
            alert.alert_field = form.cleaned_data['alert_field']
            alert.time_period = form.cleaned_data['time_period']

            if not form.cleaned_data['up_or_down']:
                alert.change = str(form.cleaned_data['change'] * -1.00)
            else:
                alert.change = str(form.cleaned_data['change'])

            alert.save()

            return HttpResponseRedirect('/publisher/settings/alerts/')
    else:
        form = AlertForm(initial=alert.__dict__)

    return AQ_render_to_response(request, 'publisher/settings/alerts-edit.html', {
            'form' : form,
            'alert': alert,
        }, context_instance=RequestContext(request))


@url("^settings/alerts/delete/(?P<id>[0-9]+)/$", "publisher_settings_alerts_delete")
@tab("Publisher","Settings","Alerts")
@publisher_required
@register_api(None)
def publisher_settings_alerts_delete(request, id):
    ''' View to allow a Publisher to Delete an Alert '''

    alert = get_object_or_404(request.organization.alert_set, id=id)
    alert.delete()

    return HttpResponseRedirect('/publisher/settings/alerts/')



@url("^settings/feeds/$", "publisher_settings_feeds")
@tab("Publisher","Settings","Data Feeds")
@register_api(api_context=('id', 'name', 'get_datafeed_type_display', 'get_datafeed_format_display', ))
@publisher_required
def publisher_settings_feeds(request,page=None):
    ''' View a Publishers Feed Settings '''
    from atrinsic.base.models import PublisherDataFeed
    from forms import PublisherFeedForm
    
    if request.method == "POST":
        form = PublisherFeedForm(request.POST,org=request.organization)

        if form.is_valid():
            df = PublisherDataFeed.objects.create(publisher=request.organization,
                                                  advertiser=form.cleaned_data["advertiser"],
                                                  datafeed_type=form.cleaned_data['datafeed_type'],
                                                  datafeed_format=form.cleaned_data['datafeed_format'],
                                                  username=form.cleaned_data['username'] or '',
                                                  password=form.cleaned_data['password'] or '',
                                                  server=form.cleaned_data['server'] or '')


            if df.datafeed_type != DATAFEEDTYPE_FTPPULL:
                # XXX Call function to send messages to network admins??
                return AQ_render_to_response(request, 'publisher/settings/feeds-notice.html', {
                    'feed': df,
                    }, context_instance=RequestContext(request))
            return HttpResponseRedirect('/publisher/settings/feeds/')
    else:
        form = PublisherFeedForm(org=request.organization)
    qs = request.organization.publisherdatafeed_set.all()
    return object_list(request, queryset=qs, allow_empty=True, page=page,
        template_name='publisher/settings/feeds.html', paginate_by=50, extra_context={
        'total_results' : qs.count(), 'form' : form,
        })


@url("^settings/feeds/add/$", "publisher_settings_feeds_add")
@tab("Publisher","Settings","Feeds")
@publisher_required
@register_api(None)
def publisher_settings_feeds_add(request):
    ''' View to allow a Publisher to add a DataFeed '''
    from atrinsic.base.models import PublisherDataFeed
    from forms import PublisherFeedForm
    
    if request.method == "POST":
        form = PublisherFeedForm(request.POST,org=request.organization)
        if form.is_valid():
            df = PublisherDataFeed.objects.create(publisher=request.organization,
                                                  advertiser=form.cleaned_data["advertiser"],
                                                  datafeed_type=form.cleaned_data['datafeed_type'],
                                                  datafeed_format=form.cleaned_data['datafeed_format'],
                                                  username=form.cleaned_data['username'] or '',
                                                  password=form.cleaned_data['password'] or '',
                                                  server=form.cleaned_data['server'] or '')


            if df.datafeed_type != DATAFEEDTYPE_FTPPULL:
                # XXX Call function to send messages to network admins??
                return AQ_render_to_response(request, 'publisher/settings/feeds-notice.html', {
                    'feed': df,
                    }, context_instance=RequestContext(request))
            return HttpResponseRedirect('/publisher/settings/feeds/')
    else:
        form = PublisherFeedForm(org=request.organization)

    return AQ_render_to_response(request, 'publisher/settings/feeds-add.html', {
            'form' : form,
        }, context_instance=RequestContext(request))


@url("^settings/feeds/edit/(?P<id>[0-9]+)/$", "publisher_settings_feeds_edit")
@tab("Publisher","Settings","Feeds")
@publisher_required
@register_api(None)
def publisher_settings_feeds_edit(request, id):
    ''' View to allow a Publisher to edit a DataFeed '''
    from forms import PublisherFeedForm
    
    feed = get_object_or_404(request.organization.publisherdatafeed_set, id=id)

    if request.method == "POST":
        form = PublisherFeedForm(request.POST,org=request.organization)

        if form.is_valid():
            feed.advertiser = form.cleaned_data['advertiser']
            feed.datafeed_type = form.cleaned_data['datafeed_type']
            feed.datafeed_format = form.cleaned_data['datafeed_format']
            feed.username = form.cleaned_data['username'] or ''
            feed.password = form.cleaned_data['password'] or ''
            feed.server = form.cleaned_data['server'] or ''
            
            feed.save()
    
            return HttpResponseRedirect('/publisher/settings/feeds/')
    else:
        feed_dict = feed.__dict__
        feed_dict['advertiser'] = feed.advertiser.id
        form = PublisherFeedForm(initial=feed_dict,org=request.organization)

    return AQ_render_to_response(request, 'publisher/settings/feeds-edit.html', {
            'form' : form,
            'feed': feed,
        }, context_instance=RequestContext(request))


@url("^settings/feeds/delete/(?P<id>[0-9]+)/$", "publisher_settings_feeds_delete")
@tab("Publisher","Settings","Feeds")
@publisher_required
@register_api(None)
def publisher_settings_feeds_delete(request, id):
    ''' View to allow a Publisher to Delete a Data Feed '''

    feed = get_object_or_404(request.organization.publisherdatafeed_set, id=id)
    feed.delete()

    return HttpResponseRedirect('/publisher/settings/feeds/')


@url("^settings/websites/$", "publisher_settings_websites")
@tab("Publisher","Settings","Web Sites")
@publisher_required
@register_api(api_context=('id', 'url', 'promotion_method', 'vertical', ))
def publisher_settings_websites(request):
    ''' View to display a a Publishers WebSites '''

    qs = request.organization.website_set.all()

    return object_list(request, queryset=qs, allow_empty=True,
        template_name='publisher/settings/websites.html', paginate_by=50, extra_context={
            'total_results' : qs.count(),
        })


@url("^settings/websites/delete/(?P<id>[0-9]+)/$", "publisher_settings_websites_delete")
@tab("Publisher","Settings","Web Sites")
@publisher_required
@register_api(None)
def publisher_settings_websites_delete(request, id):
    ''' View to allow a Publisher to delete a WebSite '''

    website = get_object_or_404(request.organization.website_set, id=id)
    website.delete()
    return HttpResponseRedirect(reverse('publisher_settings_websites'))


@url("^settings/websites/add/$", "publisher_settings_websites_add")
@tab("Publisher","Settings","Web Sites")
@publisher_required
@register_api(None)
def publisher_settings_websites_add(request):
    ''' View to allow a Publisher the ability to add a WebSite '''
    from atrinsic.base.models import Website
    from forms import WebsiteForm
    
    if request.method == 'POST':
        form = WebsiteForm(request.POST)
        if form.is_valid():
            Website.objects.create(publisher=request.organization, url=form.cleaned_data['url'],
                    desc=form.cleaned_data['desc'], promo_method=form.cleaned_data['promo_method'],
                    vertical=form.cleaned_data['vertical'], is_incentive=form.cleaned_data['is_incentive'],
                    incentive_desc=form.cleaned_data['incentive_desc'])

            return HttpResponseRedirect(reverse('publisher_settings_websites'))
    else:
        form = WebsiteForm()

    return AQ_render_to_response(request, 'publisher/settings/websites-add.html', {
        'form': form,
        }, context_instance=RequestContext(request))


@url("^settings/websites/edit/(?P<id>[0-9]+)/$", "publisher_settings_websites_edit")
@tab("Publisher","Settings","Web Sites")
@publisher_required
@register_api(None)
def publisher_settings_websites_edit(request, id):
    ''' View to allow a Publisher to edit a WebSite '''
    from forms import WebsiteForm
    
    website = get_object_or_404(request.organization.website_set, id=id)

    
    if request.method == 'POST':
        form = WebsiteForm(request.POST, instance=website)
        if form.is_valid():
            website.url = form.cleaned_data.get('url', None)
            website.desc = form.cleaned_data.get('desc', None)
            website.promo_method = form.cleaned_data.get('promo_method', None)
            website.vertical = form.cleaned_data.get('vertical', None)
            website.is_incentive = form.cleaned_data.get('is_incentive', None)
            website.incentive_desc = form.cleaned_data.get('incentive_desc', None)
            website.is_default = form.cleaned_data.get('is_default', False)
            website.save()

            return HttpResponseRedirect(reverse('publisher_settings_websites'))
    else:
        if(website.promo_method == None):
            promoPKFix = None
        else:
            promoPKFix = website.promo_method.pk
        if(website.vertical == None):
            vertFix = None
        else:
            vertFix = website.vertical.pk
        inits = {
            'url':website.url,
            'desc':website.desc,
            'promo_method':promoPKFix,
            'vertical':vertFix,
            'is_incentive':website.is_incentive,
            'incentive_desc':website.incentive_desc,
            'is_default':website.is_default,
        }
        form = WebsiteForm(initial=inits)

    return AQ_render_to_response(request, 'publisher/settings/websites-edit.html', {
        'form': form,
        'website':website
        }, context_instance=RequestContext(request))


@url("^settings/payment/$", "publisher_settings_payment")
@tab("Publisher","Settings","Payment Info")
@publisher_required
@register_api(None)
def publisher_settings_payment(request):
    ''' View to display a Publisher's Payment Settings '''

    return AQ_render_to_response(request, 'publisher/settings/payment.html', {
        'org': request.organization,
        }, context_instance=RequestContext(request))


@url("^settings/payment/edit/$", "publisher_settings_payment_edit")
@tab("Publisher","Settings","Payment Info")
@publisher_required
@register_api(None)
def publisher_settings_payment(request):
    ''' View to edit a Publishers Payment Settings '''
    from atrinsic.base.models import OrganizationContacts, OrganizationPaymentInfo
    from forms import ContactInfoForm, PaymentInfoForm
    global_err = ''
    
    if request.method == 'POST':
        formPI = PaymentInfoForm(request.POST)
        formCI = ContactInfoForm(request.POST)
        if formPI.is_valid():
            OrganizationPaymentInfo.objects.filter(organization=request.organization).update(**formPI.cleaned_data)
            if formPI.cleaned_data['payment_method'] == PAYMENT_CHECK:
                if formCI.is_valid():
                    OrganizationContacts.objects.filter(organization=request.organization).update(**formCI.cleaned_data)
                else:              
                    return AQ_render_to_response(request, 'publisher/settings/payment-edit.html', {
                        'formPI': formPI,
                        'formCI': formCI,
                        'global_err' : global_err
                        }, context_instance=RequestContext(request))
            return HttpResponseRedirect(reverse('publisher_settings_payment'))
        else:
            global_err = formCI.errors
            print global_err
    else:
        try:
            formPI = PaymentInfoForm(instance = OrganizationPaymentInfo.objects.get(organization=request.organization))
            formCI = ContactInfoForm(instance = OrganizationContacts.objects.get(organization=request.organization))
        except:
            formPI = PaymentInfoForm()
            formCI = ContactInfoForm()
            
    return AQ_render_to_response(request, 'publisher/settings/payment-edit.html', {
        'formPI': formPI,
        'formCI': formCI,
        'global_err' : global_err
        }, context_instance=RequestContext(request))


@url("^settings/incentive/$", "publisher_settings_incentive")
@tab("Publisher","Settings","Incentive Site Settings")
@publisher_required
@register_api(None)
def publisher_settings_incentive(request):
    ''' View to allow a Publisher to set their Incentive Site Settings '''
    from atrinsic.base.models import DataTransfer
    from forms import PublisherDataTransferForm

    org = request.organization
    if request.method == 'POST':
        form = PublisherDataTransferForm(request.POST, org=org)
        
        if form.is_valid():
            dt = DataTransfer.objects.get_or_create(publisher=request.organization)[0]
            dt.format = form.cleaned_data["format"]
            dt.datafeed_type=form.cleaned_data["datafeed_type"]
            dt.username = form.cleaned_data['username']
            dt.password = form.cleaned_data['password']
            dt.server = form.cleaned_data['server']
            dt.save()
            return HttpResponseRedirect(reverse('publisher_settings_incentive'))
        else:
            print "form not valid"
    else:
        form = PublisherDataTransferForm(org=org)

    transfers = org.datatransfer_set.all()
    return AQ_render_to_response(request, 'publisher/settings/incentive.html', {
        'form': form,
        'transfers': transfers,
        'total_results': transfers.count(),
        }, context_instance=RequestContext(request))


@url("^settings/incentive/delete/(?P<id>[0-9]+)/$", "publisher_settings_incentive_delete")
@tab("Publisher","Settings","Incentive Site Settings")
@publisher_required
@register_api(None)
def publisher_settings_incentive_delete(request, id):
    ''' View to allow a Publisher to delete their Incentive Site Settings '''

    t = get_object_or_404(request.organization.datatransfer_set, id=id)
    t.delete()
    return HttpResponseRedirect(reverse('publisher_settings_incentive'))


@url("^settings/incentive/request/$", "publisher_settings_incentive_request")
@tab("Publisher","Settings","Incentive Site Settings")
@publisher_required
@register_api(None)
def publisher_settings_incentive_request(request):
    ''' View to request SID Site Settings '''

    request.organization.sid_status = STATUS_PENDING
    request.organization.save()

    #org = request.organization
    #msg = 'The organization %s has requested an SID ' % org.name + 'enabled account.'
    #if org.network_admin is not None:
    #    org.network_admin.email_user('Organization SID Request', msg)

    
    return AQ_render_to_response(request, 'publisher/settings/request.html', {
        }, context_instance=RequestContext(request))


@url("^settings/pixel/$", "publisher_piggyback_pixel")
@tab("Publisher","Settings","Piggyback Pixels")
@publisher_required
@register_api(None)
def publisher_piggyback_pixel(request):
    ''' View to allow a Publisher to edit their pixel '''   

    qs = request.organization.piggybackpixel_set.all()

    return object_list(request, queryset=qs, allow_empty=True,
        template_name='publisher/settings/pixel.html', paginate_by=50, extra_context={
            'total_results' : qs.count(),
        })
    
@url("^settings/pixel/add/$", "publisher_settings_pixel_add")
@tab("Publisher","Settings","Pixels")
@publisher_required
@register_api(None)
def publisher_settings_pixel_add(request):
    ''' View to allow a Publisher the ability to add a WebSite '''
    from atrinsic.base.models import Action, PiggybackPixel
    from forms import PiggybackForm
    
    if request.method == 'POST':
        form = PiggybackForm(request.organization, request.POST)
        if form.is_valid():         
            ##################
            apeClient = Ape()
            ape_redirect_id = None   
            getActions = Action.objects.filter(advertiser=form.cleaned_data['advertiser']).order_by('id')
            
            if getActions.count() == 0:
                # Do not create Pixel
                pass
            else:
                #Use RedirectID from Oldest Action(order_by('id')) and create actions under that RedirectID
                ape_redirect_id = getActions[0].ape_redirect_id
            
            # If script pixel, then we must create a piggy back 
            # for both the JS Include(jsinclude), as well as the JS Code(content)
            includePixelID = 0
            if form.cleaned_data['pixel_type'] == PIXEL_TYPE_SCRIPT and form.cleaned_data['jsinclude'] != "":                
                success, createPixel = apeClient.execute_piggyback_create(request,ape_redirect_id,PIXEL_TYPE_IFRAME,form.cleaned_data['jsinclude']) 
                if success:
                    includePixelID = createPixel['pixel_id']
            #Call APE and create Piggyback Pixel with redirect determined above.
            success, createPixel = apeClient.execute_piggyback_create(request,ape_redirect_id,form.cleaned_data['pixel_type'],form.cleaned_data['content'])       
            if success:
                PiggybackPixel.objects.create(publisher=request.organization, advertiser=form.cleaned_data['advertiser'],
                        pixel_type=form.cleaned_data['pixel_type'], jsinclude=form.cleaned_data['jsinclude'], ape_content_pixel_id = createPixel['pixel_id'], ape_include_pixel_id = includePixelID, content=form.cleaned_data['content'])

            return HttpResponseRedirect(reverse('publisher_settings_websites'))
    else:
        form = PiggybackForm(request.organization)

    return AQ_render_to_response(request, 'publisher/settings/pixel-add.html', {
        'form': form,
        }, context_instance=RequestContext(request))

@url("^settings/pixel/edit/(?P<id>[0-9]+)/$", "publisher_settings_pixel_edit")
@tab("Publisher","Settings","Pixelss")
@publisher_required
@register_api(None)
def publisher_settings_pixel_edit(request, id):
    ''' View to allow a Publisher to edit a WebSite '''
    from forms import PiggybackForm    
    from atrinsic.base.models import Action
    pbPixel = get_object_or_404(request.organization.piggybackpixel_set, id=id)

    
    if request.method == 'POST':
        form = PiggybackForm(request.organization, request.POST)
        if form.is_valid():
            
            ##################
            apeClient = Ape()
            ape_redirect_id = None   
            getActions = Action.objects.filter(advertiser=form.cleaned_data['advertiser']).order_by('id')
            
            if getActions.count() == 0:
                # Do not create Pixel
                pass
            else:
                #Use RedirectID from Oldest Action(order_by('id')) and create actions under that RedirectID
                ape_redirect_id = getActions[0].ape_redirect_id
            
            # If script pixel, then we must create a piggy back 
            # for both the JS Include(jsinclude), as well as the JS Code(content)
            if form.cleaned_data['pixel_type'] == PIXEL_TYPE_SCRIPT and pbPixel.ape_include_pixel_id != 0:                
                success, updatePixel = apeClient.execute_piggyback_update(request,ape_redirect_id,pbPixel.ape_include_pixel_id,form.cleaned_data['jsinclude']) 
                
            #Call APE and create Piggyback Pixel with redirect determined above.
            success, createPixel = apeClient.execute_piggyback_update(request,ape_redirect_id,pbPixel.ape_content_pixel_id,form.cleaned_data['content'])       

                
            
            pbPixel.advertiser = form.cleaned_data['advertiser']
            pbPixel.pixel_type = form.cleaned_data['pixel_type']
            pbPixel.jsinclude=form.cleaned_data['jsinclude']
            pbPixel.content = form.cleaned_data['content']                    
            
            pbPixel.save()

            return HttpResponseRedirect(reverse('publisher_piggyback_pixel'))
    else:
        inits = {
            'advertiser':pbPixel.advertiser.pk,
            'pixel_type':pbPixel.pixel_type,
            'jsinclude':pbPixel.jsinclude,
            'content':pbPixel.content,
        }
        form = PiggybackForm(request.organization, initial=inits)

    return AQ_render_to_response(request, 'publisher/settings/pixel-edit.html', {
        'form': form,
        'pixel':pbPixel
        }, context_instance=RequestContext(request))
        
@url("^settings/pixel/delete/(?P<id>[0-9]+)/$", "publisher_settings_pixel_delete")
@tab("Publisher","Settings","Pixelss")
@publisher_required
@register_api(None)
def publisher_settings_pixel_delete(request, id):
    ''' View to allow a Publisher to delete a WebSite '''    
    from atrinsic.base.models import Action
    
    pbPixel = get_object_or_404(request.organization.piggybackpixel_set, id=id)
    
    apeClient = Ape()            
    ape_redirect_id = None   
    getActions = Action.objects.filter(advertiser=pbPixel.advertiser).order_by('id')
    
    if getActions.count() == 0:
        # Do not create Pixel
        pass
    else:
        #Use RedirectID from Oldest Action(order_by('id')) and create actions under that RedirectID
        ape_redirect_id = getActions[0].ape_redirect_id
        
    
    if pbPixel.ape_content_pixel_id != 0:
        success, createPixel = apeClient.execute_piggyback_delete(request,ape_redirect_id,pbPixel.ape_content_pixel_id)
         
    if pbPixel.ape_include_pixel_id != 0:
        success, createPixel = apeClient.execute_piggyback_delete(request,ape_redirect_id,pbPixel.ape_include_pixel_id)       
                         
    #pbPixel.delete()
    return HttpResponseRedirect(reverse('publisher_piggyback_pixel'))

@url("^settings/dashboard/$", "real_time_box_settings")
@tab("Publisher","Settings","Real Time Box")
@register_api(None)
@publisher_required
def real_time_box_settings(request):
    from forms import DashboardSettingsForm
    if request.POST:
        form = DashboardSettingsForm(request.POST)
        if form.is_valid():
            request.organization.dashboard_variable1 = request.POST['dashboard_variable1']
            #request.organization.dashboard_variable2 = request.POST['dashboard_variable2']
            request.organization.save()
            referer = request.META.get('HTTP_REFERER', None)
            if referer == None:
                return HttpResponseRedirect("/publisher/")
            else:
                return HttpResponseRedirect(referer)
    else:
        inits = {
            'dashboard_variable1':request.organization.dashboard_variable1,
            #'dashboard_variable2':request.organization.dashboard_variable2
        }
        form = DashboardSettingsForm(inits)
    if request.organization.is_advertiser():
        org_type="advertiser"
    else:
        org_type="publisher"
    return AQ_render_to_response(request, 'base/real-time-settings.html', { 
                        'var_choices':DASHBOARDMETRIC_CHOICES,
                        'form':form,
                        'org_type':org_type }, context_instance=RequestContext(request))
                        

@url("^settings/kenshoo/$", "publisher_kenshoo")
@tab("Publisher","Settings","Kenshoo")
@publisher_required
@register_api(None)
def publisher_kenshoo(request):
    ''' View to allow a Publisher to view kenshoo stuff '''   
    qs = request.organization.kenshoointegration_set.all()
    return object_list(request, queryset=qs, allow_empty=True,
        template_name='publisher/settings/kenshoo.html', paginate_by=50, extra_context={
            'total_results' : qs.count(),
        })        

@url("^settings/kenshoo/add/$", "publisher_settings_kenshoo_add")
@tab("Publisher","Settings","kenshoo")
@publisher_required
@register_api(None)
def publisher_settings_kenshoo_add(request):
    ''' View to allow a Publisher the ability to add a WebSite '''
    from atrinsic.base.models import Action, KenshooIntegration
    from forms import KenshooIntegrationAddForm
    
    if request.method == 'POST':
        form = KenshooIntegrationAddForm(request.organization, request.POST)
        if form.is_valid():
            apeClient = Ape()
            ape_redirect_id = None
            getActions = Action.objects.filter(advertiser=form.cleaned_data['advertiser']).order_by('id')
            
            if getActions.count() == 0:
                pass
            else:
                ape_redirect_id = getActions[0].ape_redirect_id
            
            kenshooURL = settings.KENSHOO_URL.replace("{{token}}", form.cleaned_data['content'])
            success, createPixel = apeClient.execute_piggyback_create(
                request
                ,ape_redirect_id
                ,PIXEL_TYPE_IMAGE
                ,kenshooURL
            )
            ape_content_id_value = createPixel['pixel_id']
            
            if success :
                KenshooIntegration.objects.create(
                    publisher=request.organization
                    ,advertiser=form.cleaned_data['advertiser']
                    ,pixel_type=PIXEL_TYPE_IMAGE
                    ,ape_content_pixel_id = ape_content_id_value
                    ,content=form.cleaned_data['content']
                )
            
            return HttpResponseRedirect(reverse('publisher_kenshoo'))
    else:
        form = KenshooIntegrationAddForm(request.organization)

    return AQ_render_to_response(request, 'publisher/settings/kenshoo-add.html', {
        'form': form,
        }, context_instance=RequestContext(request))

@url("^settings/kenshoo/edit/(?P<id>[0-9]+)/$", "publisher_settings_kenshoo_edit")
@tab("Publisher","Settings","kenshoo")
@publisher_required
@register_api(None)
def publisher_settings_kenshoo_edit(request, id):
    ''' View to allow a Publisher to edit a WebSite '''
    from forms import KenshooIntegrationEditForm    
    from atrinsic.base.models import Action, Organization
    pbPixel = get_object_or_404(request.organization.kenshoointegration_set, id=id)
    if request.method == 'POST':
        form = KenshooIntegrationEditForm(request.organization, request.POST)
        advertiserID = request.POST.get("advertiser",None)
        if form.is_valid():
            apeClient = Ape()
            ape_redirect_id = None   
            getActions = Action.objects.filter(advertiser=Organization.objects.get(id=advertiserID)).order_by('id')
            if getActions.count() == 0:
                pass
            else:
                ape_redirect_id = getActions[0].ape_redirect_id
            success, createPixel = apeClient.execute_piggyback_update(request,ape_redirect_id,pbPixel.ape_content_pixel_id,form.cleaned_data['content'])     

            if success:
                pbPixel.pixel_type = PIXEL_TYPE_IMAGE
                pbPixel.content = form.cleaned_data['content']                    
                pbPixel.save()
            return HttpResponseRedirect(reverse('publisher_kenshoo'))
    else:
        inits = {
            'advertiser':pbPixel.advertiser.pk,
            'pixel_type':pbPixel.pixel_type,
            'content':pbPixel.content,
        }
        form = KenshooIntegrationEditForm(request.organization, initial=inits)
        
    return AQ_render_to_response(request, 'publisher/settings/kenshoo-edit.html', {
        'form': form,
        'pixel':pbPixel,
        }, context_instance=RequestContext(request))
        
@url("^settings/kenshoo/delete/(?P<id>[0-9]+)/$", "publisher_settings_kenshoo_delete")
@tab("Publisher","Settings","kenshoo")
@publisher_required
@register_api(None)
def publisher_settings_kenshoo_delete(request, id):
    from atrinsic.base.models import Action, KenshooIntegration
    try:
        pbPixel = KenshooIntegration.objects.get(id=id)
    except:
        return HttpResponseRedirect(reverse('publisher_kenshoo'))
    
    apeClient = Ape()            
    ape_redirect_id = None   
    getActions = Action.objects.filter(advertiser=pbPixel.advertiser).order_by('id')
    if getActions.count() == 0:
        pass
    else:
        ape_redirect_id = getActions[0].ape_redirect_id
    if pbPixel.ape_content_pixel_id != 0:
        success, createPixel = apeClient.execute_piggyback_delete(request,ape_redirect_id,pbPixel.ape_content_pixel_id)       
    if success:
        try:
            pbPixel.delete()
        except:
            pass
    return HttpResponseRedirect(reverse('publisher_kenshoo'))
