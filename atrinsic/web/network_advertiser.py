from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.db.models.query import QuerySet
from forms import NetworkActionForm

from atrinsic.util.tabfunctions import *
from atrinsic.util.imports import *
from atrinsic.web.helpers import base36_encode
from atrinsic.util.AceApi import createIO, updateIOStatus, createIODetail, updateIODetail, getIO, createFee, deleteFee, getFees,searchIOs
from atrinsic.util.ApeApi import Ape

# Navigation Tab to View mappings for the Network Advertiser Menu
tabset("Network", 1, "Advertiser", "network_advertiser_account_settings",
       [ ("Advertiser Account Settings", "network_advertiser_account_settings"),
         ("Advertiser Tracking", "network_advertiser_account_tracking"),
         ("Advertiser Data Feed", "network_advertiser_account_datafeed"),
         ])

@url(r"^advertiser/settings/$","network_advertiser_account_settings")
@tab("Network","Advertiser","Advertiser Account Settings")
@admin_required
def network_advertiser_account_settings(request):
    ''' View to display the Network Advertisers.  From this view a Network Admin can
        Assign a Network Contact, Edit the Advertiser's Organization Information,
        Update the Advertiser's Status, Impersonate an Advertiser, and edit the
        Trademark and Keywork Violations. '''

    return AQ_render_to_response(request, 'network/advertiser.html', {
            'buttons' : 'settings',
        }, context_instance=RequestContext(request))


@url("^advertiser/settings/contact/(?P<id>[0-9]+)/$", "network_advertiser_account_contact")
@tab("Network","Advertiser","Advertiser Account Settings")
@admin_required
def network_advertiser_account_contact(request, id):
    ''' Assigns Network Contact
    '''
    from atrinsic.base.models import Organization
    from forms import AdvertiserAssignContactForm
    
    advertiser = get_object_or_404(Organization, id=id)

    if request.method == 'POST':
        form = AdvertiserAssignContactForm(advertiser, request.POST)

        if form.is_valid():
            advertiser.network_admin = get_object_or_404(User, id=form.cleaned_data['contact'])
            advertiser.save()

            return HttpResponseRedirect('/network/advertiser/settings/')
    else:
        if advertiser.network_admin is not None:
            form = AdvertiserAssignContactForm(advertiser, initial={ 'contact' : advertiser.network_admin.id, })
        else:
            form = AdvertiserAssignContactForm(advertiser)

    return AQ_render_to_response(request, 'network/advertiser-contact.html', {
            'advertiser' : advertiser,
            'form' : form,
        }, context_instance=RequestContext(request))


@url(r"^advertiser/tracking/$","network_advertiser_account_tracking")
@tab("Network","Advertiser","Advertiser Tracking")
@admin_required
def network_advertiser_account_settings(request):
    ''' View to allow a Network Admin to edit the Tracking status of an Advertiser '''

    return AQ_render_to_response(request, 'network/advertiser.html', {
            'buttons' : 'tracking',
        }, context_instance=RequestContext(request))

@url(r"^advertiser/datafeed/$","network_advertiser_account_datafeed")
@tab("Network","Advertiser","Advertiser Data Feed")
@admin_required
def network_advertiser_account_settings(request):
    ''' View to allow a Network Admin to edit the Data Feed settings of an Organization '''

    return AQ_render_to_response(request, 'network/advertiser.html', {
            'buttons' : 'datafeed',
        }, context_instance=RequestContext(request))
  
 
@url(r"^advertiser/add/$","network_advertiser_add")
@tab("Network","Advertiser","Advertiser Account Settings")
@admin_required
def network_advertiser_add(request):
    ''' View to allow a Network Admin to create a new Advertiser '''
    from atrinsic.base.models import Currency, Organization, OrganizationCurrency
    from forms import NetworkAdvertiserEditForm
    if request.method == 'POST':
        form = NetworkAdvertiserEditForm(request.POST)

        if form.is_valid():
            try:
                if form.cleaned_data["country"] == "CA":
                    form.cleaned_data["state"] = form.cleaned_data['province']
            except:
                pass
            del form.cleaned_data['province']
            del form.cleaned_data['salesperson']
            
            curID = form.cleaned_data['currency']
            del form.cleaned_data['currency']
            
            org = Organization.objects.create(**form.cleaned_data)
            org.org_type = ORGTYPE_ADVERTISER
            org.status = ORGSTATUS_TEST
            org.save()
            
            orgCur = OrganizationCurrency.objects.create(advertiser = org, currency = Currency.objects.get(order=curID))
            return HttpResponseRedirect('/network/advertiser/settings/')
        
    else:
        form = NetworkAdvertiserEditForm()

    return AQ_render_to_response(request, 'network/advertiser-add.html', {
            'form' : form,
        }, context_instance=RequestContext(request))


@url(r"^advertiser/edit/(?P<id>\d+)/$","network_advertiser_edit")
@tab("Network","Advertiser","Advertiser Account Settings")
@admin_required
def network_advertiser_edit(request, id):
    ''' View to allow a Network Admin to edit and update an Advertiser's
        Organization Information '''    
    from atrinsic.base.models import ProgramTermSpecialAction,OrganizationContacts, Organization_IO, OrganizationPaymentInfo, Organization, OrganizationCurrency, Currency
    from atrinsic.util.AceFieldLists import Ace
    from forms import NetworkAdvertiserEditForm,NetworkAdvertiserContactEditForm,NetworkAdvertiserOrgIOEditForm,NetworkAdvertiserBillingEditForm,NetworkAdvertiserSettingsEditForm,ProgramTermSpecialActionForm
    advertiser = get_object_or_404(request.user.get_profile().admin_assigned_advertisers(), id=id)
    
    try:
        orgContact = OrganizationContacts.objects.get(organization=advertiser)
    except:
        orgContact = None
    try:
        orgIO = Organization_IO.objects.get(organization=advertiser)
    except:
        orgIO = None
    
    client = Ace()
    form = None
    
    special_term,x = ProgramTermSpecialAction.objects.get_or_create(organization = advertiser)
        
    if request.method == 'POST':
        if request.POST.get("formtype",None):
            formType = request.POST.get("formtype")
            if formType == "form":
                form = NetworkAdvertiserEditForm(request.POST, request.FILES, instance=advertiser)
            elif formType == "formContactEdit":
                form = NetworkAdvertiserContactEditForm(request.POST, instance=OrganizationContacts.objects.get(organization=advertiser))
            elif formType == "formBillingEdit":
                form = NetworkAdvertiserBillingEditForm(request.POST, instance=OrganizationPaymentInfo.objects.get(organization=advertiser))
            elif formType == "formSettingsEdit":
                form = NetworkAdvertiserSettingsEditForm(request.POST, instance=advertiser)
            elif formType == "formTermsEdit":
                form = ProgramTermSpecialActionForm(request.POST, instance=special_term)
            elif formType == "formIOStatusUpdate":
                form = None
                if orgIO != None:
                    args = {}
                    args["ioId"] = orgIO.ace_ioid  
                    args["statusId"] = APPROVED_BY_SALES_MANAGER  
                    args["spId"] = request.POST.get("salesperson")  
                    updateIOStatus(advertiser,args)
            elif formType == "formIOFeeSettingsEdit":  
                form = NetworkAdvertiserOrgIOEditForm(request.POST, instance=advertiser)
                if orgIO != None:
                    if form.is_valid():
                        orgIO.transaction_fee_type = request.POST.get("transaction_fee_type")
                        orgIO.transaction_fee_amount = request.POST.get("transaction_fee_amount")
                        orgIO.save()
                    else:
                        return HttpResponseRedirect('/network/advertiser/edit/%d/?error=1' % int(id))
                        
                    form = None
                    
                    if orgIO.salesrep == 0 or orgIO.salesrep == None:
                        orgIO.salesrep = request.POST.get("salesperson")
                        orgIO.save()
                    args = {}
                    args["ioId"] = orgIO.ace_ioid  
                    args["spId"] = request.POST.get("salesperson")  
                    for x in request.POST:
                        '''
                            Since the intitial Placement fees were pulled dynamically, 
                            we need to check based on checkboxes being "on" as unchecked boxes do not post.
                        '''
                        if request.POST.get(x) == "on":
                            args["feeId"] = x.replace("idplacement_", "")
                            args["feeAmount"] = request.POST.get(x + "amt")
                            createFee(advertiser,args)
                        
                        '''
                            When placement fees were intially pulled, added a hidden field to keep track
                            of which fees were already chosen. Compare initial values(tracker), against
                            whther or not its corresponding checkbox is "on".
                            If theres a discrepency, ie. Was on, now off, deleteFee                            
                        '''
                        if x.find("pftracker_") > -1:
                            args["feeId"] = x.replace("pftracker_", "")
                            if request.POST.get(x) == "1" and request.POST.get("idplacement_" + str(args["feeId"])) == None:
                                deleteFee(advertiser,args)
            
            if form != None and form.is_valid():
                if formType == "formContactEdit":
                    if orgContact != None:
                        orgContact.firstname = form.cleaned_data.get('firstname')
                        orgContact.lastname = form.cleaned_data.get('lastname')
                        orgContact.email = form.cleaned_data.get('email')
                        orgContact.phone = form.cleaned_data.get('phone') 
                        orgContact.fax =  form.cleaned_data.get('fax')
                        orgContact.save()
                else:
                    form.save()
                    if formType == "form":
                        try:
                            currency_obj = OrganizationCurrency.objects.get(advertiser = advertiser)
                            currency_obj.currency = Currency.objects.get(order=form.cleaned_data.get('currency'))
                            currency_obj.save()
                        except:
                            currency_obj = OrganizationCurrency.objects.create(advertiser=advertiser, currency = Currency.objects.get(order=form.cleaned_data.get('currency')))
               
            return HttpResponseRedirect('/network/advertiser/settings/')
        else:
            #print form.errors #this is crashing when  formType == "formIOStatusUpdate":
            return HttpResponseRedirect('/network/advertiser/edit/%d/' % int(id))
        
    else:
        #Obtain the Currency used by the advertiser and pass it to the form:
        cur_inits = {}
        
        cur_obj = OrganizationCurrency.objects.filter(advertiser=advertiser)
        curID = 0
        if cur_obj.count() != 0:
            curID = cur_obj[0].currency.order    		
        cur_inits = {'currency':curID,}
        form = NetworkAdvertiserEditForm(instance=advertiser,initial=cur_inits)
        
        inits = {}
        if orgContact != None:
            inits = {'firstname':orgContact.firstname, 
                     'lastname':orgContact.lastname,
                     'email':orgContact.email, 
                     'phone':orgContact.phone, 
                     'fax':orgContact.fax,}
        else:
            inits = {'firstname':'', 
                     'lastname':'',
                     'email':'', 
                     'phone':'', 
                     'fax':'',}
        
        paymentInfo,t = OrganizationPaymentInfo.objects.get_or_create(organization = Organization.objects.get(pk=id))
        formContactEdit = NetworkAdvertiserContactEditForm(instance=advertiser,initial=inits)
        formBillingEdit = NetworkAdvertiserBillingEditForm(instance=paymentInfo)
        formSettingsEdit = NetworkAdvertiserSettingsEditForm(instance=advertiser)
        formTermsEdit = ProgramTermSpecialActionForm(instance=special_term)
        if orgIO != None:
            formOrgIOEdit = NetworkAdvertiserOrgIOEditForm(instance=orgIO)
        else:
            formOrgIOEdit = None
            
        chosenSalesPerson = 0

        if orgIO != None:
            showIOFees = True
            args = {}
            args["ioId"] = orgIO.ace_ioid            
            placementFeesList = getFees(advertiser)
            try:
                io = getIO(advertiser,args)
                ioStatus = io['StatusName']
            except:
                ioStatus = "Unavailable"
                
            if ioStatus != "Pending Sales Approval":
                ioStatus = False
            
            if orgIO.salesrep != None and orgIO.salesrep != 0:
                chosenSalesPerson = orgIO.salesrep           
            
        else:
            showIOFees = False
            placementFeesList = None
            ioStatus = False        
    
    return AQ_render_to_response(request, 'network/advertiser-edit.html', {
            'advertiser' : advertiser,
            'form' : form,
            'formContactEdit' : formContactEdit,
            'formBillingEdit' : formBillingEdit,
            'formTermsEdit' : formTermsEdit,
            'formSettingsEdit' : formSettingsEdit,
            'formOrgIOEdit' : formOrgIOEdit,
            'placementFeesList' : placementFeesList,
            'showIOFees' : showIOFees,
            'SalesPersonList' : client.getSalesPersonList(),
            'chosenSalesPerson' : chosenSalesPerson,
            #'arrIOs' : searchIOs(),
            'ioStatus' : ioStatus,
        }, context_instance=RequestContext(request))


@url(r"^advertiser/violations/(?P<id>\d+)/$","network_advertiser_violations")
@tab("Network","Advertiser","Advertiser Account Settings")
@admin_required
def network_advertiser_violations(request, id):
    ''' View to allow a Network Admin the ability to edit the Keyword and
        Trademarke Violations of an Advertiser '''
    from forms import NetworkViolationForm        
    advertiser = get_object_or_404(request.user.get_profile().admin_assigned_advertisers(), id=id)

    if request.method == 'POST':
        form = NetworkViolationForm(request.POST)
        if form.is_valid():
            advertiser.keyword_violation = form.cleaned_data['keyword_violation']
            advertiser.trademark_violation = form.cleaned_data['trademark_violation']
            
            advertiser.save()

            return HttpResponseRedirect('/network/advertiser/settings/')
    else:
        d = { }
        if advertiser.keyword_violation:
            d['keyword_violation'] = '1'
        else:
            d['keyword_violation'] = '0'

        if advertiser.trademark_violation:
            d['trademark_violation'] = '1'
        else:
            d['trademark_violation'] = '0'

        form = NetworkViolationForm(initial=d)

    return AQ_render_to_response(request, 'network/violations.html', {
            'advertiser' : advertiser,
            'form' : form,
        }, context_instance=RequestContext(request))


@url(r"^advertiser/tracking/(?P<id>\d+)/$","network_advertiser_tracking")
@tab("Network","Advertiser","Advertiser Tracking")
@admin_required
def network_advertiser_tracking(request, id):
    ''' View to allow a Network Admin to edit and add Tracking Actions 
        for an Advertiser '''

    advertiser = get_object_or_404(request.user.get_profile().admin_assigned_advertisers(), id=id)
    
    return AQ_render_to_response(request, 'network/tracking.html', {
            'advertiser' : advertiser,
        }, context_instance=RequestContext(request))


@url(r"^advertiser/tracking/(?P<id>\d+)/add/$","network_advertiser_tracking_add")
@tab("Network","Advertiser","Advertiser Tracking")
@admin_required
def network_advertiser_tracking_add(request, id):
    ''' View to allow a Network Admin to create new Tracking Actions for an Advertiser '''
    from atrinsic.base.models import Action
    from forms import NetworkActionForm
    advertiser = get_object_or_404(request.user.get_profile().admin_assigned_advertisers(), id=id)
    if request.method == 'POST':
        form = NetworkActionForm(request.POST)
        if form.is_valid():                
            apeClient = Ape()
            ape_redirect_id = None   
            ape_action_id = None 

            getActions = Action.objects.filter(advertiser=advertiser).order_by('id')
            if getActions.count() == 0:
                #Call APE to create new REDIRECT
                success, createPixel = apeClient.execute_redirect_create()            
                if success:
                    ape_redirect_id = createPixel['redirect_id']

            else:
                #Use RedirectID from Oldest Action(order_by('id')) and create actions under that RedirectID
                ape_redirect_id = getActions[0].ape_redirect_id
            
                
            #Call APE and create Action with redirect determined above.
            success, createAction = apeClient.execute_action_create(ape_redirect_id,form.cleaned_data['name'])       
            if success:
                print "createAction - %s" % createAction
                ape_action_id = createAction['action_id']      
            
            a = Action.objects.create(advertiser=advertiser, name=form.cleaned_data['name'],
                                      status=form.cleaned_data['status'], network_fee=0,
                                      ape_redirect_id=ape_redirect_id,
                                      ape_action_id=ape_action_id,
                                      advertiser_payout_type=str(form.cleaned_data['advertiser_payout_type']),
                                      advertiser_payout_amount=str(form.cleaned_data['advertiser_payout_amount']))
            
            return HttpResponseRedirect('/network/advertiser/tracking/%d/' % advertiser.id)
    else:
        form = NetworkActionForm()

    return AQ_render_to_response(request, 'network/tracking-add.html', {
            'advertiser' : advertiser,
            'form' : form,
        }, context_instance=RequestContext(request))


@url(r"^advertiser/tracking/(?P<advertiser_id>\d+)/action/(?P<action_id>\d+)/edit/$","network_advertiser_tracking_edit")
@tab("Network","Advertiser","Advertiser Tracking")
@admin_required
def network_advertiser_tracking_edit(request, advertiser_id, action_id):
    ''' View to allow a Network Admin to edit the tracking actions of an Advertiser '''

    advertiser = get_object_or_404(request.user.get_profile().admin_assigned_advertisers(), id=advertiser_id)
    action = get_object_or_404(advertiser.action_set, id=action_id)
    apeRedirect = 0
    securePixel = ""
    nonSecurePixel = ""
    if request.method == 'POST':
        form = NetworkActionForm(request.POST)

        if form.is_valid():
            
            if action.ape_redirect_id == None or action.ape_redirect_id == 0:
                apeClient = Ape()
                success, createPixel = apeClient.execute_redirect_create()
                if success:
                    action.ape_redirect_id = createPixel['redirect_id']
            
            action.status = form.cleaned_data['status']
            action.name = form.cleaned_data['name']
            if form.cleaned_data['invite_id']:
                action.invite_id = form.cleaned_data['invite_id']
                
            action.network_fee = 0
            action.advertiser_payout_type=str(form.cleaned_data['advertiser_payout_type'])
            action.advertiser_payout_amount=str(form.cleaned_data['advertiser_payout_amount'])
            action.save()            
            return HttpResponseRedirect('/network/advertiser/tracking/%d/' % advertiser.id)
    else:
        if action.ape_redirect_id > 0:
            apeRedirect = base36_encode(action.ape_redirect_id)            
            securePixel = settings.APE_SECURE_PIXEL_URL + str(apeRedirect)
            nonSecurePixel = settings.APE_PIXEL_URL + str(apeRedirect)
            if action.ape_action_id != None:
                apeAction = base36_encode(action.ape_action_id)      
                securePixel = '%s/%s/' % (securePixel, apeAction)
                nonSecurePixel = '%s/%s/' % (nonSecurePixel, apeAction)
                
        else:
            apeRedirect = 0
        form = NetworkActionForm(initial={ 'name' : action.name, 'status' : action.status,
                                           'advertiser_payout_type' : action.advertiser_payout_type,
                                           'advertiser_payout_amount' : action.advertiser_payout_amount,
                                           'invite_id' : action.invite_id })

    
    return AQ_render_to_response(request, 'network/tracking-edit.html', {
            'advertiser' : advertiser,
            'action' : action,
            'form' : form,
            'apeRedirect' : apeRedirect,
            'securePixel' : securePixel,
            'nonSecurePixel' : nonSecurePixel,
        }, context_instance=RequestContext(request))
        
        
@url(r"^advertiser/tracking/(?P<advertiser_id>\d+)/action/(?P<action_id>\d+)/delete/$","network_advertiser_tracking_delete")
@tab("Network","Advertiser","Advertiser Tracking")
@admin_required
def network_advertiser_tracking_delete(request, advertiser_id, action_id):
    ''' View to remove an Action from an Advertiser's Tracking Settings '''

    advertiser = get_object_or_404(request.user.get_profile().admin_assigned_advertisers(), id=advertiser_id)
    action = get_object_or_404(advertiser.action_set, id=action_id)

    action.delete()

    return HttpResponseRedirect('/network/advertiser/tracking/%d' % advertiser.id)
   
@url(r"^advertiser/status/(?P<id>\d+)/$","network_advertiser_status")
@tab("Network","Advertiser","Advertiser Account Settings")
@admin_required
def network_advertiser_status(request, id):
    ''' View to allow a Network Admin to update the status of an Advertiser '''
    from forms import NetworkStatusForm
    advertiser = get_object_or_404(request.user.get_profile().admin_assigned_advertisers(), id=id)

    if request.method == 'POST':
        form = NetworkStatusForm(request.POST)

        if form.is_valid():
            advertiser.status = form.cleaned_data['status']
            advertiser.is_adult = int(form.cleaned_data['is_adult'])
            advertiser.save()

            return HttpResponseRedirect('/network/advertiser/settings/')
    else:
        form = NetworkStatusForm(initial={ 'status' : advertiser.status, 'is_adult' : advertiser.is_adult, })

    return AQ_render_to_response(request, 'network/status.html', {
            'advertiser' : advertiser,
            'form' : form,
        }, context_instance=RequestContext(request))


@url(r"^advertiser/datafeed/(?P<id>\d+)/$","network_advertiser_datafeed")
@tab("Network","Advertiser","Advertiser Data Feed")
@admin_required
def network_advertiser_datafeed(request, id):
    ''' View to display an Advertiser's Data Feeds and links to edit/delete/add '''

    advertiser = get_object_or_404(request.user.get_profile().admin_assigned_advertisers(), id=id)

    return AQ_render_to_response(request, 'network/datafeed.html', {
            'advertiser' : advertiser,
        }, context_instance=RequestContext(request))


@url(r"^advertiser/datafeed/(?P<id>\d+)/add/$","network_advertiser_datafeed_add")
@tab("Network","Advertiser","Advertiser Data Feed")
@admin_required
def network_advertiser_datafeed_add(request, id):
    ''' View to create an Advertiser DataFeed '''
    from atrinsic.base.models import DataFeed, ProgramTerm, ProgramTermAction
    from forms import NetworkDataFeedForm
    
    advertiser = get_object_or_404(request.user.get_profile().admin_assigned_advertisers(), id=id)

    if request.method == 'POST':
        form = NetworkDataFeedForm(request.POST)

        if form.is_valid():            
                
            
            df = DataFeed.objects.create(advertiser=advertiser, name=form.cleaned_data['name'],
                    landing_page_url=form.cleaned_data['landing_page_url'],status=form.cleaned_data['status'], 
                    datafeed_type=form.cleaned_data['datafeed_type'],datafeed_format=form.cleaned_data['datafeed_format'], 
                    username=form.cleaned_data['username'],password=form.cleaned_data['password'], 
                    server=form.cleaned_data['server'])
                    
            try:
                pt = ProgramTerm.objects.get(advertiser=advertiser,is_default=True)
                ptAction = ProgramTermAction.objects.select_related("action").get(program_term=pt)
                
                apeClient = Ape()
                df.ape_url_id = apeClient.execute_url_create(ptAction.action, None, df)
                df.save()
            except:
                pass
            return HttpResponseRedirect('/network/advertiser/datafeed/%d/' % advertiser.id)
    else:
        form = NetworkDataFeedForm()

    return AQ_render_to_response(request, 'network/datafeed-add.html', {
            'advertiser' : advertiser,
            'form' : form,
        }, context_instance=RequestContext(request))


@url(r"^advertiser/(?P<advertiser_id>\d+)/datafeed/(?P<datafeed_id>\d+)/delete/$","network_advertiser_datafeed_delete")
@tab("Network","Advertiser","Advertiser Data Feed")
@admin_required
def network_advertiser_datafeed_delete(request, advertiser_id, datafeed_id):
    ''' View to allow a Network Admin to delete an Advertiser's Data Feed '''

    advertiser = get_object_or_404(request.user.get_profile().admin_assigned_advertisers(), id=advertiser_id)
    datafeed= get_object_or_404(advertiser.datafeed_set, id=datafeed_id)

    datafeed.delete()

    return HttpResponseRedirect('/network/advertiser/datafeed/%d' % advertiser.id)
  
 
@url(r"^advertiser/(?P<advertiser_id>\d+)/datafeed/(?P<datafeed_id>\d+)/edit/$","network_advertiser_datafeed_edit")
@tab("Network","Advertiser","Advertiser Data Feed")
@admin_required
def network_advertiser_datafeed_edit(request, advertiser_id, datafeed_id):
    ''' View to allow a Network Admin to edit the DataFeed of an Advertiser '''    
    from atrinsic.base.models import ProgramTermAction, ProgramTerm
    from forms import NetworkDataFeedForm
    
    advertiser = get_object_or_404(request.user.get_profile().admin_assigned_advertisers(), id=advertiser_id)
    datafeed = get_object_or_404(advertiser.datafeed_set, id=datafeed_id)

    if request.method == 'POST':
        form = NetworkDataFeedForm(request.POST)

        if form.is_valid():
            datafeed.status = form.cleaned_data['status']
            datafeed.name = form.cleaned_data['name']
            datafeed.landing_page_url = form.cleaned_data['landing_page_url']
            datafeed.datafeed_type = form.cleaned_data['datafeed_type']
            datafeed.datafeed_format = form.cleaned_data['datafeed_format']
            datafeed.username = form.cleaned_data['username']
            datafeed.password = form.cleaned_data['password']
            datafeed.server = form.cleaned_data['server']
            datafeed.save()
            
            pt = ProgramTerm.objects.get(advertiser=advertiser,is_default=True)
            ptAction = ProgramTermAction.objects.select_related("action").get(program_term=pt)
            apeClient = Ape()      
            
            if datafeed.ape_url_id == 0 or datafeed.ape_url_id == None:
                datafeed.ape_url_id = apeClient.execute_url_create(ptAction.action, None, datafeed)  
                datafeed.save()
            else:     
                apeClient.execute_url_update(ptAction.action, None, datafeed)
            
                  
            apeClient.execute_url_update(ptAction.action, None, datafeed)
            return HttpResponseRedirect('/network/advertiser/datafeed/%d/' % advertiser.id)
    else:
        form = NetworkDataFeedForm(initial={ 'name' : datafeed.name, 'landing_page_url' : datafeed.landing_page_url, 
                                             'status' : datafeed.status,'datafeed_type' : datafeed.datafeed_type, 
                                             'datafeed_format' : datafeed.datafeed_format,
                                             'username' : datafeed.username, 'password' : datafeed.password,
                                             'server' : datafeed.server, })

    
    return AQ_render_to_response(request, 'network/datafeed-edit.html', {
            'advertiser' : advertiser,
            'datafeed' : datafeed,
            'form' : form,
        }, context_instance=RequestContext(request))

