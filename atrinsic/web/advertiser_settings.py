from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from atrinsic.web.helpers import format_initial_dict, parse_sku_file
from atrinsic.util.imports import *
from xlrd import XLRDError
from atrinsic.util.AceApi import createIODetail
from atrinsic.util.ApeApi import Ape

#===========================================---/SETTINGS TAB/---===========================================#
##################### Advertiser Settings ########################
@url("^settings/$", "advertiser_settings")
@tab("Advertiser","Settings","Settings")
@register_api(None)
@advertiser_required
def advertiser_settings(request):
    ''' Display the Advertisers Settings
    '''
    from atrinsic.base.models import OrganizationContacts,PublisherVertical
    from django.db.models import Q 
    try:
        orgContact = OrganizationContacts.objects.get(organization=request.organization)
    except:
        orgContact = None
            
        
    filter_vertical = request.organization.secondary_vertical.all()
    
    
    available_vertical = PublisherVertical.objects.filter(is_adult=request.organization.is_adult).exclude( Q(pk__in = filter_vertical) | Q(pk = request.organization.vertical.pk)).order_by('name')
        
    return AQ_render_to_response(request, 'advertiser/settings/index.html', {
            'verticals' : available_vertical,
            'contactInfo': orgContact,
        }, context_instance=RequestContext(request))
##################### END Advertiser Settings ########################
######################################################################

##################### Advertiser Settings - Add Vertical ########################
@url("^settings/vertical/add/$", "advertiser_settings_vertical_add")
@tab("Advertiser","Settings","Settings")
@register_api(None)
@advertiser_required
def advertiser_settings_vertical_add(request):
    ''' View to add a Secondary Vertical to this Advertiser '''
    from atrinsic.base.models import PublisherVertical
    id = request.REQUEST.get('vertical', None)

    if id:
        v = get_object_or_404(PublisherVertical, order=id)

        request.organization.secondary_vertical.add(v)

    return HttpResponseRedirect('/advertiser/settings')
##################### END Advertiser Settings - Add Vertical ########################
#####################################################################################

##################### Advertiser Settings - Remove Vertical ########################
@url("^settings/vertical/remove/(?P<id>[0-9]+)/$", "advertiser_settings_vertical_remove")
@tab("Advertiser","Settings","Settings")
@register_api(None)
@advertiser_required
def advertiser_settings_vertical_remove(request, id):
    ''' View to remove a Secondary Vertical from this Advertiser
    '''
    from atrinsic.base.models import PublisherVertical
    v = get_object_or_404(PublisherVertical, order=id)

    request.organization.secondary_vertical.remove(v)
       
    return HttpResponseRedirect('/advertiser/settings/')
##################### END Advertiser Settings - Remove Vertical ########################
########################################################################################
 
##################### Edit Advertiser Settings ########################
@url("^settings/edit/$", "advertiser_settings_edit")
@tab("Advertiser","Settings","Settings")
@register_api(None)
@advertiser_required
def advertiser_settings_edit(request):
    ''' View to edit this Advertisers Settings
    '''
    from atrinsic.base.models import OrganizationContacts,OrganizationPaymentInfo
    from forms import OrganizationForm,ContactInfoFormSmall,PaymentInfoForm
    try:
        org,new = OrganizationContacts.objects.get_or_create(organization=request.organization)
    except:
        org = None

    if request.method == "POST":
        form = OrganizationForm(request.POST)
        formCI = ContactInfoFormSmall(request.POST)
        '''formPI = PaymentInfoForm(request.POST)'''
        if form.is_valid() and formCI.is_valid():
            o = request.organization
            for k, v in form.cleaned_data.items():
                setattr(o, k, v)
            o.save()
            
            if org != None:
                org.firstname = request.POST.get('firstname', None)
                org.lastname = request.POST.get('lastname', None)
                org.email = request.POST.get('email', None)
                org.phone = request.POST.get('phone', None)
                org.fax = request.POST.get('fax', None)
                org.save()
            return HttpResponseRedirect('/advertiser/settings/')
    else:
        form = OrganizationForm(instance = request.organization)
        formCI = ContactInfoFormSmall(instance = OrganizationContacts.objects.get(organization = request.organization)) 
        #formPI = PaymentInfoForm(instance = OrganizationPaymentInfo.objects.get(organization = request.organization))
    return AQ_render_to_response(request, 'advertiser/settings/edit.html', {
            'form' : form,
            'formCI' : formCI,
        }, context_instance=RequestContext(request))
##################### END Edit Advertiser Settings ########################
###########################################################################
#===========================================---/SETTINGS TAB/---===========================================#

#===========================================---/USERS TAB/---===========================================#
##################### List Users ########################
@url("^settings/users/$", "advertiser_settings_users")
@tab("Advertiser","Settings","Users")
@register_api(api_context=('id', 'email', 'first_name', 'last_name', ))
@advertiser_required
def advertiser_settings_users(request, page=None):
    ''' View to display this Advertisers User Settings '''

    qs = request.organization.get_users()

    return object_list(request, queryset=qs, allow_empty=True, page=page,
                template_name='advertiser/settings/users.html', paginate_by=50, extra_context={
                'total_results' : qs.count(),
            })
##################### END List Users ########################
#############################################################

##################### Add Users ########################
@url("^settings/users/add/$", "advertiser_settings_users_add")
@tab("Advertiser","Settings","Users")
@register_api(None)
@advertiser_required
def advertiser_settings_users_add(request):
    ''' View to add a User to this Advertiser's Organization '''
    from forms import UserForm
    from atrinsic.base.models import User,UserProfile
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

            return HttpResponseRedirect('/advertiser/settings/users/')
    else:
        form = UserForm()

    return AQ_render_to_response(request, 'advertiser/settings/users-add.html', {
            'form' : form,
        }, context_instance=RequestContext(request))
##################### END Add Users ########################
############################################################

##################### Users - Make Manager ########################
@url("^settings/users/makeadmin/(?P<id>[0-9]+)/$", "advertiser_settings_users_makemanager")
@tab("Advertiser","Settings","Users")
@register_api(None)
@advertiser_required
def advertiser_settings_users_makemanager(request, id):
    ''' View to grant Manager permissions of a User to an Advertiser's Organization '''
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

    return HttpResponseRedirect('/advertiser/settings/users/')
##################### END Users - Make Manager ########################
#######################################################################

##################### Edit Users ########################
@url("^settings/users/edit/(?P<id>[0-9]+)/$", "advertiser_settings_users_edit")
@tab("Advertiser","Settings","Users")
@register_api(None)
@advertiser_required
def advertiser_settings_users_edit(request, id):
    ''' View to edit a User associated with this Advertiser's Organization ''' 
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
            if form.cleaned_data.get('password'):
                u.set_password(form.cleaned_data['password'])
            u.save()

            return HttpResponseRedirect('/advertiser/settings/users/')
    else:
        form = UserEditForm(initial={
                'first_name' : u.first_name,
                'last_name' : u.last_name,
                'email' : u.email,
            })

    return AQ_render_to_response(request, 'advertiser/settings/users-edit.html', {
            'u' : u,
            'form' : form,
        }, context_instance=RequestContext(request))
##################### END Edit Users ########################
#############################################################

##################### Delete Users ########################
@url("^settings/users/delete/(?P<id>[0-9]+)/$", "advertiser_settings_users_delete")
@tab("Advertiser","Settings","Users")
@register_api(None)
@advertiser_required
def advertiser_settings_users_delete(request, id):
    ''' View to delete a User from this Advertiser's Organization '''
    from atrinsic.base.models import User
    try:
        u = User.objects.get(id=id)

        if request.organization not in u.userprofile_set.all()[0].organizations.all():
            raise Http404

        if request.organization.network_admin != u:
            u.delete()

    except User.DoesNotExist:
        raise Http404

    return HttpResponseRedirect('/advertiser/settings/users/')
##################### END Delete Users ########################
###############################################################
#===========================================---/USERS TAB/---===========================================#

#===========================================---/ALERTS TAB/---===========================================#
##################### List Alerts ########################
@url("^settings/alerts/$", "advertiser_settings_alerts")
@tab("Advertiser","Settings","Alerts")
@register_api(api_context=('id', 'get_alert_field_display', 'get_time_period_display', 'change', ))
@advertiser_required
def advertiser_settings_alerts(request, page=None):
    ''' View to display this Advertiser's current Alerts '''

    qs = request.organization.alert_set.all()

    return object_list(request, queryset=qs, allow_empty=True, page=page,
                template_name='advertiser/settings/alerts.html', paginate_by=50, extra_context={
                'total_results' : qs.count(),
            })
##################### END List Alerts ########################
##############################################################

##################### Add Alerts ########################
@url("^settings/alerts/add/$", "advertiser_settings_alerts_add")
@tab("Advertiser","Settings","Alerts")
@register_api(None)
@advertiser_required
def advertiser_settings_alerts_add(request):
    ''' View that allowws an Advertiser to create a new Alert '''
    from forms import AlertForm
    from atrinsic.base.models import Alert
    if request.method == "POST":
        form = AlertForm(request.POST)

        if form.is_valid():
            change = form.cleaned_data['change']
            if form.cleaned_data['up_or_down'] == '0':
                change = change * -1.00

            Alert.objects.create(organization=request.organization,
                alert_field=form.cleaned_data['alert_field'],
                time_period=form.cleaned_data['time_period'],
                change=str(change))

            return HttpResponseRedirect('/advertiser/settings/alerts/')
    else:
        form = AlertForm()

    return AQ_render_to_response(request, 'advertiser/settings/alerts-add.html', {
            'form' : form,
        }, context_instance=RequestContext(request))
##################### END Add Alerts ########################
#############################################################

##################### Edit Alerts ########################
@url("^settings/alerts/edit/(?P<id>[0-9]+)/$", "advertiser_settings_alerts_edit")
@tab("Advertiser","Settings","Alerts")
@register_api(None)
@advertiser_required
def advertiser_settings_alerts_edit(request, id):
    ''' This view allows an Advertiser to edit a specific Alert '''
    from forms import AlertForm
    alert = get_object_or_404(request.organization.alert_set, id=id)

    if request.method == "POST":
        form = AlertForm(request.POST)

        if form.is_valid():
            alert.alert_field = form.cleaned_data['alert_field']
            alert.time_period = form.cleaned_data['time_period']
            alert.change = form.cleaned_data['change']

            if not form.cleaned_data['up_or_down']:
                alert.change = alert.change * -1.00
            
            alert.change = str(alert.change)

            alert.save()
    
            return HttpResponseRedirect('/advertiser/settings/alerts/')
    else:
        form = AlertForm(initial=alert.__dict__)

    return AQ_render_to_response(request, 'advertiser/settings/alerts-edit.html', {
            'form' : form,
            'alert': alert,
        }, context_instance=RequestContext(request))
##################### END Edit Alerts ########################
##############################################################

##################### Delete Alerts ########################
@url("^settings/alerts/delete/(?P<id>[0-9]+)/$", "advertiser_settings_alerts_delete")
@tab("Advertiser","Settings","Alerts")
@register_api(None)
@advertiser_required
def advertiser_settings_alerts_delete(request, id):
    ''' View which allows an Advertiser to Delete an Alert '''

    alert = get_object_or_404(request.organization.alert_set, id=id)
    alert.delete()

    return HttpResponseRedirect('/advertiser/settings/alerts/')
##################### END Delete Alerts ########################
################################################################
#===========================================---/ALERTS TAB/---===========================================#

#===========================================---/APPLICATION FILTERS TAB/---===========================================#
##################### List Application Filters ########################
@url("^settings/filters/$", "advertiser_settings_filters")
@tab("Advertiser","Settings","Application Filters")
@register_api(api_context=('id', 'get_field_display', 'get_display_value', ))
@advertiser_required
def advertiser_settings_filters(request, page=None):
    ''' This view shows the Advertiser's current AutoDeclineCriteria '''

    qs = request.organization.autodeclinecriteria_set.all()

    return object_list(request, queryset=qs, allow_empty=True, page=page,
                template_name='advertiser/settings/filters.html', paginate_by=50, extra_context={
                'total_results' : qs.count(),
            })
##################### END List Application Filters ########################
###########################################################################

##################### Add Application Filters ########################
@url("^settings/filters/add/$", "advertiser_settings_filters_add")
@tab("Advertiser","Settings","Application Filters")
@register_api(None)
@advertiser_required
def advertiser_settings_filters_add(request):
    ''' View to allow an Advertiser to add a new AutoDeclineCriteria '''
    from forms import FilterForm
    from atrinsic.base.models import AutoDeclineCriteria
    if request.method == "POST":
        form = FilterForm(request.organization, request.POST)

        if form.is_valid():
            field = int(form.cleaned_data['field'])
            ad = AutoDeclineCriteria(
                        field=field, advertiser=request.organization)
            if field == AUTODECLINEFIELD_PROMOTION_METHOD:
                ad.promotion_method = form.cleaned_data['promotion_method']
            elif field == AUTODECLINEFIELD_PUBLISHER_VERTICAL:
                ad.publisher_vertical = form.cleaned_data['publisher_vertical']
            elif field == AUTODECLINEFIELD_STATE:
                ad.value = form.cleaned_data['state']
            elif field == AUTODECLINEFIELD_COUNTRY:
                ad.value = form.cleaned_data['country']
            else:
                ad.value = form.cleaned_data['value']
            ad.save()

            return HttpResponseRedirect('/advertiser/settings/filters/')
    else:
        form = FilterForm(organization=request.organization)

    return AQ_render_to_response(request, 'advertiser/settings/filters-add.html', {
        'form' : form,
        }, context_instance=RequestContext(request))
##################### END Application Filters ########################
#######################################################################

##################### Edit Application Filters ########################
@url("^settings/filters/edit/(?P<id>[0-9]+)/$", "advertiser_settings_filters_edit")
@tab("Advertiser","Settings","Application Filters")
@register_api(None)
@advertiser_required
def advertiser_settings_filters_edit(request, id):
    ''' This view allows an Advertiser to edit a specific AutoDeclineCriteria '''
    from forms import FilterForm
    filter = get_object_or_404(request.organization.autodeclinecriteria_set, id=id)

    if request.method == "POST":
        form = FilterForm(request.organization, request.POST)

        if form.is_valid():
            field = int(form.cleaned_data['field'])
            filter.field = field
            if field == AUTODECLINEFIELD_PROMOTION_METHOD:
                filter.promotion_method = form.cleaned_data['promotion_method']
            elif field == AUTODECLINEFIELD_PUBLISHER_VERTICAL:
                filter.publisher_vertical = form.cleaned_data['publisher_vertical']
            elif field == AUTODECLINEFIELD_STATE:
                filter.value = form.cleaned_data['state']
            elif field == AUTODECLINEFIELD_COUNTRY:
                filter.value = form.cleaned_data['country']
            else:
                filter.value = form.cleaned_data['value']
            filter.save()

            return HttpResponseRedirect('/advertiser/settings/filters/')
    else:
        form = FilterForm(initial=format_initial_dict(filter.__dict__))

    return AQ_render_to_response(request, 'advertiser/settings/filters-edit.html', {
            'form' : form,
            'filter': filter,
        }, context_instance=RequestContext(request))
##################### END Edit Application Filters ########################
#######################################################################

##################### Delete Application Filters ########################
@url("^settings/filters/delete/(?P<id>[0-9]+)/$", "advertiser_settings_filters_delete")
@tab("Advertiser","Settings","Application Filters")
@register_api(None)
@advertiser_required
def advertiser_settings_filters_delete(request, id):
    ''' View to delete an AutoDeclineCriteria from this Advertiser's Organization '''

    filter = get_object_or_404(request.organization.autodeclinecriteria_set, id=id)
    filter.delete()

    return HttpResponseRedirect('/advertiser/settings/filters/')
##################### END Edit Application Filters ########################
###########################################################################
#===========================================---/APPLICATION FILTERS TAB/---===========================================#            
            
#===========================================---/PROGRAM SETTINGS TAB/---===========================================#
##################### List Program Terms ########################
@url("^settings/programs/$", "advertiser_settings_programs")
@tab("Advertiser","Settings","Program Settings")
@advertiser_required
@register_api(api_context=('id', 'name', 'date_created', 'is_default', 'is_archived', 'number_enrolled',))
def advertiser_settings_programs(request, page=None):
    ''' View which displays an Advertiser's Programs Settings '''

    qs = request.organization.programterm_set.all().filter(is_archived=False)

    return object_list(request, queryset=qs, allow_empty=True, page=page,
                template_name='advertiser/settings/programs.html', paginate_by=50, extra_context={
                'total_results' : qs.count(),
            })
#################### END List Program Terms #####################
#################################################################            

##################### Add\Edit Program Term \ Program Term Action ########################
@url("^settings/programs/add/$", "advertiser_settings_programs_add")
@tab("Advertiser","Settings","Program Settings")
@register_api(None)
@advertiser_required
def advertiser_settings_programs_add(request):
    ''' This view allows an Advertiser to create a new ProgramTerm '''
    from forms import ProgramForm,ProgramActionForm
    from atrinsic.base.models import ProgramTerm, ProgramTermAction, Action
    action_choices = [ (a.id, a.name) for a in request.organization.action_set.all() ]
    if request.method == "POST":
        form = ProgramForm(request.POST)
        formPTA = ProgramActionForm(action_choices, request.POST)
        if form.is_valid() and formPTA.is_valid():
            t = ProgramTerm.objects.create(advertiser=request.organization, date_created=datetime.datetime.now(),
                is_default=False, name=form.cleaned_data['name'])
            if ProgramTerm.objects.filter(advertiser=request.organization).count() == 1:
                t.is_default=True
                t.save()

            action = Action.objects.get(id=formPTA.cleaned_data['action'].pk)
            a = ProgramTermAction.objects.create(program_term=t, action=action,
                is_custom_action_lifecycle=False, 
                custom_action_lifecycle=0,
                commission=str(formPTA.cleaned_data['commission']), 
                is_fixed_commission=formPTA.cleaned_data['is_fixed_commission'],
                action_referral_period=formPTA.cleaned_data['action_referral_period'])

            args = {}
            args["tag"] = action.name
            args["payTerms"] = 30    
            args["rate"] = action.advertiser_payout_amount
            args["unitType"] = action.advertiser_payout_type
            args["salesrep"] = request.POST.get("salesperson")
            #createIODetail(request.organization, args, t)       
            #return HttpResponseRedirect('/advertiser/settings/programs/%d/' % t.id)
            sendToPage = dict(programId=str(t.id), programName=str(t.name))
            return HttpResponse("%s" % sendToPage)

    else:
        form = ProgramForm()        
        formPTA = ProgramActionForm(action_choices)

    return AQ_render_to_response(request, 'advertiser/settings/programs-add.html', {
            'form' : form,
            'formPTA' : formPTA,
        }, context_instance=RequestContext(request))
        
@url("^settings/programs/(?P<id>[0-9]+)/$", "advertiser_settings_programs_edit")
@tab("Advertiser","Settings","Program Settings")
@register_api(None)
@advertiser_required
def advertiser_settings_programs_edit(request, id):
    ''' This view allows an Advertiser to edit a specific Program Term '''
    from forms import ProgramActionForm
    from atrinsic.util.AceFieldLists import Ace
    from atrinsic.base.models import Action,ProgramTermAction,Organization_IO
    program = get_object_or_404(request.organization.programterm_set, id=id)
    hide_form = True

    if program.programtermaction_set.all().count() > 0:
        action_choices = [ (a.id, a.name) for a in request.organization.action_set.all().exclude(id__in=[ pta.action.id for pta in program.programtermaction_set.all() ])]
    else:
        action_choices = [ (a.id, a.name) for a in request.organization.action_set.all() ]
    
    actionsAvailable = True
    if len(action_choices) == 0:
        actionsAvailable = False
    if request.method == "POST":
        form = ProgramActionForm(action_choices, request.POST)

        if form.is_valid():
            action = Action.objects.get(id=form.cleaned_data['action'].pk)
            a = ProgramTermAction.objects.create(program_term=program, action=action,
                is_custom_action_lifecycle=False, 
                custom_action_lifecycle=0,
                commission=str(form.cleaned_data['commission']), 
                is_fixed_commission=form.cleaned_data['is_fixed_commission'],
                action_referral_period=form.cleaned_data['action_referral_period'])

            args = {}
            args["tag"] = action.name
            args["payTerms"] = 30    
            args["rate"] = action.advertiser_payout_amount
            args["unitType"] = action.advertiser_payout_type
            args["salesrep"] = request.POST.get("salesperson")
            createIODetail(request.organization, args, program)       
            
            
            sendToPage = dict(programId=str(id), programName=str(program.name))
            return HttpResponse("%s" % sendToPage)
            
            #referer = request.META.get('HTTP_REFERER', None)
            #if referer == None:
            #    return HttpResponseRedirect("/advertiser/settings/programs")
            #else:
            #    return HttpResponseRedirect(referer)
        else:
            hide_form = False        
    else:
        form = ProgramActionForm(action_choices)

    client = Ace()
    chosenSalesPerson = 0
    try:
        orgIO = Organization_IO.objects.get(organization=request.organization)
        if orgIO.salesrep != None and orgIO.salesrep != 0:
            chosenSalesPerson = orgIO.salesrep 
    except:
        orgIO = None
        
    return AQ_render_to_response(request, 'advertiser/settings/programs-edit.html', {
            'form' : form,
            'hide_form' : hide_form,
            'program' : program,
            'action_choices' : action_choices,            
            'SalesPersonList' : client.getSalesPersonList(),
            'chosenSalesPerson' : chosenSalesPerson,
            'actionsAvailable' : actionsAvailable,
        }, context_instance=RequestContext(request))
    
@url("^settings/programs/clone/(?P<id>[0-9]+)/$", "advertiser_settings_programs_clone")
@tab("Advertiser","Settings","Program Settings")
@register_api(None)
@advertiser_required
def advertiser_settings_programs_clone(request, id):
    ''' This view allows an Advertiser to create a new ProgramTerm '''
    from forms import ProgramForm,ProgramActionForm
    from atrinsic.base.models import ProgramTerm, ProgramTermAction, Action
    
    prg = get_object_or_404(ProgramTerm, id=id)
    action_choices = [ (a.id, a.name) for a in request.organization.action_set.all() ]
    
    inits = { 'name':prg.name, }
    form = ProgramForm(inits)        
    formPTA = ProgramActionForm(action_choices)

    return AQ_render_to_response(request, 'advertiser/settings/programs-add.html', {
            'form' : form,
            'formPTA' : formPTA,
        }, context_instance=RequestContext(request))        
            
##################### END Add\Edit Program Term \ Program Term Action ########################
##############################################################################################

##################### List Archived Program Terms ########################
@url("^settings/programs/viewarchived/$", "advertiser_settings_programs_view_archived")
@tab("Advertiser","Settings","Program Settings")
@advertiser_required
@register_api(api_context=('id', 'name', 'date_created', 'is_default', 'is_archived', 'number_enrolled',))
def advertiser_settings_programs_view_archived(request, page=None):
    ''' View which displays an Advertiser's Programs Settings '''


    qs = request.organization.programterm_set.all().filter(is_archived=True)

    return object_list(request, queryset=qs, allow_empty=True, page=page,
                template_name='advertiser/settings/programs.html', paginate_by=50, extra_context={
                'total_results' : qs.count(),
            })
##################### END List Archived Program Terms ########################
##############################################################################       
     
##################### Add Commission Tier to Program Term Action ########################
@url("^settings/programs/actions/(?P<id>[0-9]+)/addtier/$", "advertiser_settings_programs_actions_addtier")
@tab("Advertiser","Settings","Program Settings")
@register_api(None)
@advertiser_required
def advertiser_settings_programs_actions_addtier(request, id):
    ''' This view allows an Advertiser to add a new CommissionTier to a ProgramTerm '''
    from atrinsic.base.models import ProgramTermAction,CommissionTier
    from forms import CommissionTierForm
    action = get_object_or_404(ProgramTermAction, id=id)

    if action.program_term.advertiser != request.organization:
        raise Http404
    else:

        if request.method == "POST":

            if request.POST.get('cancel', None):
                return HttpResponseRedirect('/advertiser/settings/programs/')

            form = CommissionTierForm(request.POST)

            if form.is_valid():
                CommissionTier.objects.create(program_term_action=action, incentive_type=form.cleaned_data['incentive_type'],
                        threshold=str(form.cleaned_data['threshold']), 
                        new_commission=str(form.cleaned_data['new_commission']),
                        bonus=str(form.cleaned_data['bonus']))

                return HttpResponseRedirect('/advertiser/settings/programs/%d/'% action.program_term.id)
        else:
            form = CommissionTierForm()
        
    return AQ_render_to_response(request, 'advertiser/settings/programs-addtier.html', {
            'form' : form,
            'action' : action,
        }, context_instance=RequestContext(request))
##################### END Add Commission Tier to Program Term Action ########################
#############################################################################################

##################### Delete Commission Tier from Program Term Action ########################
@url("^settings/programs/actions/(?P<id>[0-9]+)/delete/tier/(?P<t_id>[0-9]+)/$", "advertiser_settings_programs_actions_deletetier")
@register_api(None)
@advertiser_required
def advertiser_settings_programs_actions_deletetier(request, id, t_id):
    ''' View which allows an Advertiser to delete a CommissionTier from a
        ProgramTermAction '''
    from atrinsic.base.models import ProgramTermAction
    action = get_object_or_404(ProgramTermAction, id=id)

    if action.program_term.advertiser != request.organization:
        raise Http404
    else:
        tier = action.commissiontier_set.filter(id=t_id).delete()

    return HttpResponseRedirect('/advertiser/settings/programs/%d/' % action.program_term.id)
##################### END Delete Commission Tier from Program Term Action ########################
##################################################################################################

##################### Add SKU List Program Term Action ########################
@url("^settings/programs/skulist/add/(?P<id>[0-9]+)/$", "advertiser_programs_skulist_add")
@tab("Advertiser","Settings","Program Settings")
@register_api(None)
@advertiser_required
def advertiser_programs_skulist_add(request,id):
    from forms import SKUListProgramTermActionForm
    from atrinsic.base.models import SKUList,SKUListProgramTerm,SKUListChangeLog,ProgramTermAction
    form = SKUListProgramTermActionForm(request.organization, request.POST)

    if request.POST:
        if form.is_valid():
            skulist = SKUList.objects.get(pk=request.POST['skulist'])
            action = ProgramTermAction.objects.get(id=id)
            term,created = SKUListProgramTerm.objects.get_or_create(skulist=skulist, programterm_action=action)
            term.is_fixed_commission=form.cleaned_data['is_fixed_commission']
            term.commission=str(form.cleaned_data['commission'])
            term.save()
            SKUListChangeLog.objects.create(skulist_programterm=term, new_commission=str(form.cleaned_data['commission']),
                    old_commission=str(action.commission))
            
            progAction = ProgramTermAction.objects.get(id=id)
            prog = progAction.program_term_id        
                    
            return HttpResponseRedirect('/advertiser/settings/programs/' + str(prog))

    else:
        form = SKUListProgramTermActionForm(organization=request.organization)
        
    return AQ_render_to_response(request, 'advertiser/settings/skulists-add-action.html', {
            'form' : form,
            'programterm_id' : id,
        }, context_instance=RequestContext(request))
##################### END Add SKU List Program Term Action ########################
###################################################################################

##################### Delete Program Term Action ########################
@url("^settings/programs/actions/(?P<id>[0-9]+)/delete/$", "advertiser_settings_programs_actions_delete")
@register_api(None)
@advertiser_required
def advertiser_settings_programs_actions_delete(request, id):
    ''' This view deltes an Action from a ProgramTerm '''
    from atrinsic.base.models import ProgramTerm, ProgramTermAction
    action = get_object_or_404(ProgramTermAction, id=id)


    t_id = action.program_term.id    
    # Cannot delete the last Program Term Action on a Program Term.
    if action.program_term.number_program_term_actions() == 1:
        if action.program_term.number_enrolled() == 0:
            action.delete()
            prgmTerm = ProgramTerm.objects.get(id=t_id)
            if ProgramTermAction.objects.filter(program_term = prgmTerm).count() == 0:
                prgmTerm.delete()
    elif action.program_term.number_program_term_actions() > 1:
        action.delete()
        
    return HttpResponseRedirect('/advertiser/settings/programs/')

##################### END Delete Program Term Action ########################
#############################################################################

##################### Set Default Program Term #########################
@url("^settings/programs/(?P<id>[0-9]+)/default/$", "advertiser_settings_programs_default")
@register_api(None)
@advertiser_required
def advertiser_settings_programs_default(request, id):
    ''' This view allows an Advertiser to declare their default ProgramTerm '''
    from atrinsic.base.models import ProgramTerm
    program = get_object_or_404(ProgramTerm, id=id)

    if program.advertiser != request.organization:
        raise Http404
    else:
        for p in request.organization.programterm_set.filter(is_default=True):
            p.is_default = False
            p.save()

        program.is_default = True 
        program.save()

    return HttpResponseRedirect('/advertiser/settings/programs/')
##################### END Set Default Program Term #########################    
############################################################################

##################### Archive\Unarchive Program Terms #########################
@url("^settings/programs/(?P<id>[0-9]+)/archive/$", "advertiser_settings_programs_archive")
@tab("Advertiser","Settings","Program Settings")
@register_api(None)
@advertiser_required
def advertiser_settings_programs_archive(request, id):
    ''' This view archives an active ProgramTerm '''

    program = get_object_or_404(request.organization.programterm_set, id=id)

    program.is_archived = True
    program.save()

    return HttpResponseRedirect('/advertiser/settings/programs/')


@url("^settings/programs/(?P<id>[0-9]+)/unarchive/$", "advertiser_settings_programs_unarchive")
@tab("Advertiser","Settings","Program Settings")
@register_api(None)
@advertiser_required
def advertiser_settings_programs_unarchive(request, id):
    ''' This view unarchives an archived ProgramTerm '''

    program = get_object_or_404(request.organization.programterm_set, id=id)

    program.is_archived = False
    program.is_default = False
    program.save()

    return HttpResponseRedirect('/advertiser/settings/programs/')
##################### END Archive\Unarchive Program Terms #########################

##################### Edit Program Term CPM #########################    
@url("^settings/programs/(?P<id>[0-9]+)/cpm/$", "advertiser_settings_programs_edit_cpm")
@tab("Advertiser","Settings","Program Settings")
@register_api(None)
@advertiser_required
def advertiser_settings_programs_edit_cpm(request,id):
    ''' This view allows the advertiser to update their CPM/CPC for a program term
    '''
    from forms import ProgramCPMForm
    program = get_object_or_404(request.organization.programterm_set, id=id)
    if request.method == "POST":
        form = ProgramCPMForm(request.POST, request.FILES)
        
        if form.is_valid():
            program.cpm = str(form.cleaned_data["cpm"])
            program.cpc = str(form.cleaned_data["cpc"])
            program.save()
            return HttpResponseRedirect('/advertiser/settings/programs/%s/' % program.id)
    else:
        form = ProgramCPMForm(initial={'cpm':program.cpm,
                                       'cpc':program.cpc})
    
    
    return AQ_render_to_response(request, 'advertiser/settings/cpm_edit.html', {
            'form' : form,
        }, context_instance=RequestContext(request))
##################### END Edit Program Term CPM ######################  
######################################################################
#===========================================---/PROGRAM SETTINGS TAB/---===========================================#


#===========================================---/DATA FEEDS TAB/---===========================================#
##################### List Data Feeds ########################
@url("^settings/feeds/$", "advertiser_settings_feeds")
@tab("Advertiser","Settings","Data Feeds")
@register_api(api_context=('id', 'name', 'get_datafeed_type_display', 'get_datafeed_format_display', ))
@advertiser_required
def advertiser_settings_feeds(request,page=None):
    ''' This view displays and Advertisers Data Feeds '''

    qs = request.organization.datafeed_set.all()

    return object_list(request, queryset=qs, allow_empty=True, page=page,
        template_name='advertiser/settings/feeds.html', paginate_by=50, extra_context={
        'total_results' : qs.count(),
        })
##################### END List Data Feeds ########################
##################################################################

##################### Add Data Feeds ########################
@url("^settings/feeds/add/$", "advertiser_settings_feeds_add")
@tab("Advertiser","Settings","Feeds")
@register_api(None)
@advertiser_required
def advertiser_settings_feeds_add(request):
    ''' View to allow an Advertiser to add a DataFeed '''
    from forms import FeedForm
    from atrinsic.base.models import DataFeed
    if request.method == "POST":
        form = FeedForm(request.POST)

        if form.is_valid():
            df = DataFeed.objects.create(advertiser=request.organization,
                                    name=form.cleaned_data['name'],
                                    landing_page_url=form.cleaned_data['landing_page_url'],
                                    datafeed_type=form.cleaned_data['datafeed_type'],
                                    datafeed_format=form.cleaned_data['datafeed_format'],
                                    username=form.cleaned_data['username'] or '',
                                    password=form.cleaned_data['password'] or '',
                                    server=form.cleaned_data['server'] or '')

            if df.datafeed_type != DATAFEEDTYPE_FTPPULL:
                # XXX Call function to send messages to network admins??
                return AQ_render_to_response(request, 'advertiser/settings/feeds-notice.html', {
                    'feed': df,
                    }, context_instance=RequestContext(request))

            return HttpResponseRedirect('/advertiser/settings/feeds/')
    else:
        form = FeedForm()

    return AQ_render_to_response(request, 'advertiser/settings/feeds-add.html', {
            'form' : form,
        }, context_instance=RequestContext(request))
##################### END Add Data Feeds ########################
#################################################################

##################### Edit Data Feeds ########################
@url("^settings/feeds/edit/(?P<id>[0-9]+)/$", "advertiser_settings_feeds_edit")
@tab("Advertiser","Settings","Feeds")
@register_api(None)
@advertiser_required
def advertiser_settings_feeds_edit(request, id):
    ''' This view allows an Advertiser to edit a specific Data Feed '''
    from forms import FeedForm    
    from atrinsic.base.models import ProgramTerm, ProgramTermAction
    
    feed = get_object_or_404(request.organization.datafeed_set, id=id)

    if request.method == "POST":
        form = FeedForm(request.POST)
        if form.is_valid():
            feed.name = form.cleaned_data['name']
            feed.landing_page_url = form.cleaned_data['landing_page_url']
            feed.datafeed_type = form.cleaned_data['datafeed_type']
            feed.datafeed_format = form.cleaned_data['datafeed_format']
            feed.username = form.cleaned_data['username'] or ''
            feed.password = form.cleaned_data['password'] or ''
            feed.server = form.cleaned_data['server'] or ''
            feed.save()

            pt = ProgramTerm.objects.get(advertiser=request.organization,is_default=True)
            ptAction = ProgramTermAction.objects.select_related("action").get(program_term=pt)
            apeClient = Ape()            
            if feed.ape_url_id == 0 or feed.ape_url_id == None:
                feed.ape_url_id = apeClient.execute_url_create(ptAction.action, None, feed) 
                feed.save() 
            else:     
                apeClient.execute_url_update(ptAction.action, None, feed)
                
            return HttpResponseRedirect('/advertiser/settings/feeds/')

    else:
        form = FeedForm(initial=feed.__dict__)

    return AQ_render_to_response(request, 'advertiser/settings/feeds-edit.html', {
            'form' : form,
            'feed': feed,
        }, context_instance=RequestContext(request))
##################### END Edit Data Feeds ########################
##################################################################

##################### Delete Data Feeds ########################
@url("^settings/feeds/delete/(?P<id>[0-9]+)/$", "advertiser_settings_feeds_delete")
@tab("Advertiser","Settings","Feeds")
@register_api(None)
@advertiser_required
def advertiser_settings_feeds_delete(request, id):
    ''' View to allow an Advertiser to delete a Data Feed '''

    feed = get_object_or_404(request.organization.datafeed_set, id=id)
    feed.delete()

    return HttpResponseRedirect('/advertiser/settings/feeds/')
##################### END Delete Data Feeds ########################
####################################################################
#===========================================---/DATA FEEDS TAB/---===========================================#

#===========================================---/SKU LISTS TAB/---===========================================#
##################### List SKU Lists ########################
@url("^settings/skulists/$", "advertiser_settings_skulists")
@tab("Advertiser","Settings","SKU Lists")
@register_api(api_context=('id', 'name', 'skulistitem_set', ))
@advertiser_required
def advertiser_settings_skulists(request, page=None):
    ''' View to allow an Advertiser to manage SKULists '''

    qs = request.organization.skulist_set.all()

    return object_list(request, queryset=qs, allow_empty=True, page=page,
                template_name='advertiser/settings/skulists.html', paginate_by=50, extra_context={
                'total_results' : qs.count(),
            })
##################### END List SKU Lists ########################
#################################################################

##################### Add SKU Lists ########################
@url("^settings/skulists/add/$", "advertiser_settings_skulists_add")
@tab("Advertiser","Settings","SKU Lists")
@register_api(None)
@advertiser_required
def advertiser_settings_skulists_add(request):
    ''' View to allow an Advertiser to create a SKUList'''
    from forms import SKUListForm
    from atrinsic.base.models import SKUList
    if request.POST:
        form = SKUListForm(request.POST, request.FILES)

        if form.is_valid():
            sl = SKUList.objects.create(name=form.cleaned_data['name'], advertiser=request.organization)
            parse_sku_file(form.cleaned_data['skufile'],request.organization,sl,form.cleaned_data['name'])
                
            return HttpResponseRedirect('/advertiser/settings/skulists/edit/%d/' % sl.id)
    else:
        form = SKUListForm()

    return AQ_render_to_response(request, 'advertiser/settings/skulists-add.html', {
            'form' : form,
        }, context_instance=RequestContext(request))
##################### END Add SKU Lists ########################
################################################################

##################### Edit SKU List ######################## 
@url("^settings/skulists/edit/(?P<id>[0-9]+)/$", "advertiser_settings_skulists_edit")
@tab("Advertiser","Settings","SKU Lists")
@register_api(None)
@advertiser_required
def advertiser_settings_skulists_edit(request, id):
    ''' View to allow an Advertiser to edita SKU List'''
    from forms import SKUListForm
    l = get_object_or_404(request.organization.skulist_set, id=id)

    if request.POST:
            l.name = request.POST['name']
            l.save()
            return HttpResponseRedirect('/advertiser/settings/skulists/')
    else:
        form = SKUListForm(initial={ 'name' : l.name, }, editing=True)

    return AQ_render_to_response(request, 'advertiser/settings/skulists-edit.html', {
            'form' : form,
            'skulist' : l,
        }, context_instance=RequestContext(request))
##################### END Edit SKU List ######################## 
################################################################ 

##################### Delete SKU Lists ########################            
@url("^settings/skulists/delete/(?P<id>[0-9]+)/$", "advertiser_settings_skulists_delete")
@tab("Advertiser","Settings","SKU Lists")
@register_api(None)
@advertiser_required
def advertiser_settings_skulists_delete(request, id):
    ''' View to allow an Advertiser to delete a SKU List'''

    l = get_object_or_404(request.organization.skulist_set, id=id)
    l.delete()

    return HttpResponseRedirect('/advertiser/settings/skulists/')
##################### END Delete SKU Lists ########################            
###################################################################            

##################### Add SKU List Item ########################  
@url("^settings/skulists/(?P<skulist_id>[0-9]+)/item/add/$", "advertiser_settings_skulists_item_add")
@tab("Advertiser","Settings","SKU Lists")
@register_api(None)
@advertiser_required
def advertiser_settings_skulists_item_add(request, skulist_id):
    ''' View to allow an Advertiser to add a SKU List Item'''
    from forms import SKUListItemForm
    from atrinsic.base.models import SKUListItem
    l = get_object_or_404(request.organization.skulist_set, id=skulist_id)

    if request.POST:
        form = SKUListItemForm(request.POST)

        if form.is_valid():
            SKUListItem.objects.create(skulist=l, item=form.cleaned_data['item'])

            return HttpResponseRedirect('/advertiser/settings/skulists/edit/%d/' % l.id)

    else:
        form = SKUListItemForm()
 
    return AQ_render_to_response(request, 'advertiser/settings/skulists-add-item.html', {
            'form' : form,
            'skulist' : l,
        }, context_instance=RequestContext(request))
##################### END Add SKU List Item ########################  
#################################################################### 

##################### Delete SKU List Item ######################## 
@url("^settings/skulists/(?P<skulist_id>[0-9]+)/item/delete/(?P<item_id>[0-9]+)/$", "advertiser_settings_skulists_item_delete")
@tab("Advertiser","Settings","SKU Lists")
@register_api(None)
@advertiser_required
def advertiser_settings_skulists_item_delete(request, skulist_id, item_id):
    ''' View to allow an Advertiser to delete a SKU List Item'''

    l = get_object_or_404(request.organization.skulist_set, id=skulist_id)
    i = get_object_or_404(l.skulistitem_set, id=item_id)
    i.delete()

    return HttpResponseRedirect('/advertiser/settings/skulists/edit/%d/' % l.id)
##################### END Delete SKU List Item ######################## 
####################################################################### 

##################### Add SKU List Action ######################## 
@url("^settings/skulists/(?P<skulist_id>[0-9]+)/action/add/$", "advertiser_settings_skulists_action_add")
@tab("Advertiser","Settings","SKU Lists")
@register_api(None)
@advertiser_required
def advertiser_settings_skulists_action_add(request, skulist_id):
    ''' View to allow an Advertiser to add a SKUListProgramTerm'''
    from forms import SKUListProgramTermActionForm
    from atrinsic.base.models import ProgramTermAction,SKUListProgramTerm,SKUListChangeLog
    print "in function"
    
    l = get_object_or_404(request.organization.skulist_set, id=skulist_id)

    if request.POST:
        form = SKUListProgramTermActionForm(request.organization, request.POST)
        print request.POST
        if form.is_valid():
            action = ProgramTermAction.objects.get(id=form.cleaned_data['programterm_action'])

            term = SKUListProgramTerm.objects.create(skulist=l, programterm_action=action,
                    is_fixed_commission=form.cleaned_data['is_fixed_commission'], commission=str(form.cleaned_data['commission']))

            SKUListChangeLog.objects.create(skulist_programterm=term, new_commission=str(form.cleaned_data['commission']),
                    old_commission=str(action.commission))

            return HttpResponseRedirect('/advertiser/settings/skulists/edit/%d/' % l.id)

    else:
        form = SKUListProgramTermActionForm(organization=request.organization)
 
    return AQ_render_to_response(request, 'advertiser/settings/skulists-add-action.html', {
            'form' : form,
            'skulist' : l,
        }, context_instance=RequestContext(request))
##################### END Add SKU List Action ######################## 
###################################################################### 

##################### Delete SKU List Action ######################## 
@url("^settings/skulists/(?P<skulist_id>[0-9]+)/action/delete/(?P<action_id>[0-9]+)/$", "advertiser_settings_skulists_action_delete")
@tab("Advertiser","Settings","SKU Lists")
@register_api(None)
@advertiser_required
def advertiser_settings_skulists_action_delete(request, skulist_id, action_id):
    ''' View to allow an Advertiser to delete a SKU List ProgramTerm Action'''

    l = get_object_or_404(request.organization.skulist_set, id=skulist_id)
    i = get_object_or_404(l.skulistprogramterm_set, id=action_id)
    i.delete()

    return HttpResponseRedirect('/advertiser/settings/skulists/edit/%d/' % l.id)
##################### END Delete SKU List Action ######################## 
######################################################################### 
#===========================================---/SKU LISTS TAB/---===========================================#

#===========================================---/REAL TIME BOX TAB/---===========================================#
##################### Real Time Box Settings ######################## 
@url("^settings/dashboard/$", "real_time_box_settings_adv")
@tab("Advertiser","Settings","Real Time Box")
@register_api(None)
@advertiser_required
def real_time_box_settings_adv(request):
    from forms import DashboardSettingsForm

    if request.POST:
        form = DashboardSettingsForm(request.POST,request.organization)
        if form.is_valid():
            request.organization.dashboard_variable1 = request.POST['dashboard_variable1']
            #request.organization.dashboard_variable2 = request.POST['dashboard_variable2']
            request.organization.save()
            referer = request.META.get('HTTP_REFERER', None)
            if referer == None:
                return HttpResponseRedirect("/advertiser/")
            else:
                return HttpResponseRedirect(referer) 
    else:
        inits = {
            'dashboard_variable1':request.organization.dashboard_variable1,
            #'dashboard_variable2':request.organization.dashboard_variable2
        }
        
        form = DashboardSettingsForm(inits)
        form.fields['dashboard_variable1'].choices = DASHBOARDMETRIC_CHOICES
    if request.organization.is_advertiser():
        org_type="advertiser"
    else:
        org_type="publisher"
    
    return AQ_render_to_response(request, 'base/real-time-settings.html', { 
                        'var_choices':DASHBOARDMETRIC_CHOICES,
                        'form':form,
                        'org_type':org_type }
                        , context_instance=RequestContext(request))
##################### END Real Time Box Settings ######################## 
#########################################################################                         
#===========================================---/REAL TIME BOX TAB/---===========================================#

#===========================================---/MANAGE ORDERS TAB/---===========================================#
##################### Manage Orders ######################## 
@url("^settings/manage_orders/$", "manage_orders")
@register_api(None)
@advertiser_required
def manage_orders(request):
    from forms import ManageOrders
    import time
    if request.POST:
        pass
    else:
        form = ManageOrders(request.organization)
    today = datetime.date.fromtimestamp(time.time())
    # If January, go to December of last year
    if today.month == 1:
        firstOfLastMonth = datetime.date(today.year - 1, 12, 1)
    else:
        firstOfLastMonth = datetime.date(today.year, today.month - 1, 1)

    initFirst = firstOfLastMonth
    initToday = today
    
    firstOfLastMonth = firstOfLastMonth.strftime("%b %d, %Y")
    todaysDate = today.strftime("%b %d, %Y")
    
    return AQ_render_to_response(request, 'advertiser/settings/manageorders.html', { 
                        'form':form, 
                        'firstOfLast':firstOfLastMonth,
                        'todaysDate':todaysDate,
                        'initFirst':initFirst,
                        'initToday':initToday,}
                        , context_instance=RequestContext(request))
##################### END Manage Orders ######################## 
################################################################           

##################### Manage Orders Results ########################  
@url("^settings/manage_orders/results/$", "manage_orders_results")
@advertiser_required
def manage_orders_results(request, page=None):
    from atrinsic.base.models import Organization, Report_OrderDetail
    orderList = []
    if request.POST:
        searchForm = request.POST.get("searchForm")
        if searchForm == "byIds":
            orderList = request.POST["orderids"].split("\n")
            for order in orderList:
                try:
                    x = int(order)
                except ValueError:
                    orderList.remove(order)
            print orderList
    
            qs = Report_OrderDetail.objects.filter(order_id__in = orderList) 
        else:

            searchBy = int(request.POST["searchby"])
            havingOrderAmounts = int(request.POST["orderamtby"])
            orderAmounts = request.POST["orderamt"]
            all_publishers = Organization.objects.filter(advertiser_relationships__status=RELATIONSHIP_ACCEPTED,
                                         advertiser_relationships__advertiser=request.organization) 
                                         
            pids = []
            
            if searchBy == SRCHPUBORDERSBY_ALL:
                pids = [j.id for j in all_publishers]
            elif searchBy == int(SRCHPUBORDERSBY_SPECIFIC):
                pids.extend([int(x[2:]) for x in request.POST.getlist("searchByPublisher")])            
            
            qs = Report_OrderDetail.objects.filter(publisher__in = pids)
            if request.POST["hStartDate"] != None:
                strDate = request.POST["hStartDate"] + " 00:00:00"
                d = datetime.datetime.strptime(strDate,"%Y-%m-%d %H:%M:%S")
                qs = qs.filter(report_date__gte = d)
                
            if request.POST["hEndDate"] != None:
                strDate = request.POST["hEndDate"] + " 00:00:00"
                d = datetime.datetime.strptime(strDate,"%Y-%m-%d %H:%M:%S")
                qs = qs.filter(report_date__lte = d)

            if havingOrderAmounts == int(ORDERAMTSBY_ALL):
                print "Count1 = %s" % qs.count()
                qs = qs.extra()[:250]
                pass
            elif havingOrderAmounts == int(ORDERAMTSBY_GREATER_THAN):
                print "Count2 = %s" % qs.count()
                qs = qs.extra(where=['amount > ' + orderAmounts ]).order_by('report_date')[:500]
            elif havingOrderAmounts == int(ORDERAMTSBY_LESS_THAN):
                print "Count3 = %s" % qs.count()
                qs = qs.extra(where=['amount < ' + orderAmounts ]).order_by('report_date')[:500]
            elif havingOrderAmounts == int(ORDERAMTSBY_EQUAL_TO):
                print "Count4 = %s" % qs.count()
                qs = qs.extra(where=['amount = ' + orderAmounts ]).order_by('report_date')[:500]
                
    else:
        pass
    return object_list(request, queryset=qs, allow_empty=True, page=page,
            template_name='advertiser/settings/manageordersresults.html', extra_context={
            'total_results' : qs.count(),
        })
    return AQ_render_to_response(request, 'advertiser/settings/manageordersresults.html')
##################### END Manage Orders Results ########################  
#######################################################################

##################### Create Manage Orders ########################               
@url("^settings/manage_orders/create/$", "manage_orders_create")
@advertiser_required
def manage_orders_create(request):
    from forms import CreateOrders
    from atrinsic.base.models import Organization,Report_OrderDetail_UpdateLog
    if request.POST:
        print request.POST
        formCreate = CreateOrders(request.organization, request.POST)
        if formCreate.is_valid():
            pub = Organization.objects.get(pk=formCreate.cleaned_data['publisherid'])
            Report_OrderDetail_UpdateLog.objects.create(publisher= pub,publisher_name=pub.company_name, advertiser=request.organization,advertiser_name=request.organization.company_name, order_id=formCreate.cleaned_data['orderid'], amount=formCreate.cleaned_data['orderamt'], publisher_commission=formCreate.cleaned_data['publisherfee'], network_fee=formCreate.cleaned_data['networkfee'], report_date=formCreate.cleaned_data['order_date'])
        else:
            print formCreate.errors
            print "INVALID"
    else:
        formCreate = CreateOrders(request.organization, initial={'orderfees': CREATEORDER_FEES_SYSTEMCALCULATED})
    
    return AQ_render_to_response(request, 'advertiser/settings/manageorders-create.html', { 
                        'formCreate':formCreate, }
                        , context_instance=RequestContext(request))
##################### END Create Manage Orders ########################               
######################################################################                                                                                  
##################### Manage Orders Update ########################  
@url("^settings/manage_orders/results/update_order$", "manage_orders_results_update")
@advertiser_required
def manage_orders_results_update(request):
    from atrinsic.base.models import Report_OrderDetail, Report_OrderDetail_UpdateLog
    if request.POST:
        print "update order id %s " % request.POST["orderid"]
        orderid = request.POST["orderid"]
        amount = request.POST["neworderamount"]
        cancelled = request.POST["cancelorder"]        
        
        updateOrderLog = Report_OrderDetail.objects.filter(id=orderid).values()[0]
        
        if cancelled == False or cancelled == 0:        
            updateOrderLog["amount"] = amount  
        else:
            updateOrderLog["order_cancelled"] = True
              
        Report_OrderDetail_UpdateLog.objects.create(**updateOrderLog)
    return HttpResponseRedirect('/advertiser/settings/manage_orders/')        
##################### END Manage Orders Update ########################
#######################################################################  

##################### Manage Orders Bulk Cancel ########################  
@url("^settings/manage_orders/results/bulk_cancel_orders$", "manage_orders_bulk_cancel")
@advertiser_required
def manage_orders_bulk_cancel(request):
    from atrinsic.base.models import Report_OrderDetail, Report_OrderDetail_UpdateLog
    if request.POST:
        orderid = request.POST["orderid"]
        amount = request.POST["neworderamount"]
        cancelled = request.POST["cancelorder"]        

        updateOrderLog = Report_OrderDetail.objects.filter(id=orderid).values()[0]
        if cancelled == False or cancelled == 0:        
            updateOrderLog["amount"] = amount  
        else:
            updateOrderLog["order_cancelled"] = True
              

        Report_OrderDetail_UpdateLog.objects.create(**updateOrderLog)
    return HttpResponseRedirect('/advertiser/settings/manage_orders/')
##################### END Manage Orders Bulk Cancel ########################          
############################################################################  
#===========================================---/MANAGE ORDERS TAB/---===========================================#
        
                            

@url("^settings/signup_page/$", "advertiser_settings_signup_page")
@register_api(None)
@advertiser_required
def advertiser_settings_signup_page(request):
    ''' This view allows an Advertiser to update their Branded Signup Page Header,
        Copy, Custom Program, and Profile Detail Page Settings '''
    from forms import PublisherPageForm
    if request.method == "POST":
        form = PublisherPageForm(request.POST, request.FILES)

        if form.is_valid():
            if not 'branded_signup_page_header_url' in request.FILES:
                del form.cleaned_data["branded_signup_page_header_url"]
            else:
                request.organization.branded_signup_page_header_url = form.cleaned_data["branded_signup_page_header_url"]
                
            request.organization.branded_signup_page_copy = form.cleaned_data["branded_signup_page_copy"]
            request.organization.advertiser_custom_program_page = form.cleaned_data["advertiser_custom_program_page"]
            request.organization.advertiser_profile_detail_page = form.cleaned_data["advertiser_profile_detail_page"]
            request.organization.save() 

            return HttpResponseRedirect('/advertiser/settings/signup_page')
    
    return AQ_render_to_response(request, 'advertiser/settings/signuppage.html', {
        }, context_instance=RequestContext(request))
        
@url("^settings/signup_page/edit/$", "advertiser_settings_signup_page_edit")
@register_api(None)
@advertiser_required
def advertiser_settings_signup_page_edit(request):
    ''' This view allows an Advertiser to update their Branded Signup Page Header,
        Copy, Custom Program, and Profile Detail Page Settings '''
    from forms import PublisherPageForm
    form = PublisherPageForm(initial=request.organization.__dict__)
    
    return AQ_render_to_response(request, 'advertiser/settings/signuppage_edit.html', {
            'form' : form,
        }, context_instance=RequestContext(request))


@url("^settings/signup_page/preview/(?P<view>[\w]+)/$", "advertiser_settings_signup_page_preview")
@register_api(None)
@advertiser_required
def advertiser_settings_signup_page_preview(request, view):
    ''' This view provides a preview to an Advertisers Signup Page Settings'''
    content = request.REQUEST.get('content')

    return AQ_render_to_response(request, 'advertiser/settings/signup-preview.html', {
            'content' : content,
        }, context_instance=RequestContext(request))
        
        
##################### SKU Sample ########################
@url("^settings/skulists/sample/$", "advertiser_settings_skulists_sample")
@tab("Advertiser","Settings","SKU Lists")
@register_api(None)
@advertiser_required
def advertiser_settings_skulists_sample(request): 
    from django.template import Template, Context
    from django.template.loader import get_template
    t = get_template('advertiser/settings/sample_sku.txt')
    c = Context()
    response = HttpResponse(t.render(c), mimetype="attachement; filename=sample_sku.txt;") 
    response['Content-Disposition'] = 'attachement; filename=sample_sku.txt'
    return response
    
    