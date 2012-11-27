from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from atrinsic.util.imports import *

# Navigation Tab to View mappings for the Advertiser Messages Menu
tabset("Advertiser",3,"Messages","advertiser_messages",
       [("Folders","advertiser_messages"),
        ("Campaigns","advertiser_messages_campaigns"),
        ("Welcome Email","advertiser_messages_welcome_email"),
        ("Inquiries","advertiser_messages_inquiries"),
        ("Settings","advertiser_messages_settings"), ])



@url("^messages/$", "advertiser_messages")
@url("^messages/page/(?P<page>[0-9]+)/$", "advertiser_messages")
@url("^messages/(?P<folder>(inbox|sent|trash))/$", "advertiser_messages")
@url("^messages/(?P<folder>(inbox|sent|trash))/page/(?P<page>[0-9]+)/$", "advetiser_messages")
@tab("Advertiser","Messages","Folders")
@register_api(api_context=('id', 'sender', 'receiver', 'read', 'subject', 'message', 'created', ))
@advertiser_required
def advertiser_messages(request, folder="inbox", page=1):
    ''' This view lists all of the PrivateMessages in a particular folder '''
    from atrinsic.base.models import PrivateMessage
    from django.db.models import Q

    # Folder totals for sidebar    
    publisher_id = request.GET.get("publisher_id", None)
    #inbox = request.organization.received_messages.filter(is_active=True).order_by('-date_sent')
    #sent = request.organization.sent_messages.filter(is_active=True).order_by('-date_sent')
    #trash = request.organization.received_messages.filter(is_active=False,del_trash=False).order_by('-date_sent')

    inbox = PrivateMessage.objects.filter(receiver=request.organization.id, receiver_status=1).order_by('-date_sent')
    sent = PrivateMessage.objects.filter(sender=request.organization.id, sender_status=1).order_by('-date_sent')
    trash =  PrivateMessage.objects.filter(Q(sender=request.organization.id, sender_status=3) | Q(receiver=request.organization.id, receiver_status=3)).order_by('-date_sent')
    
    if folder.lower() == "trash":
        qs = trash
    elif folder.lower() == "sent":
        qs = sent
    else:
        qs = inbox

    data = {
        'inbox' : inbox,
        'sent' : sent,
        'trash' : trash,
        'folder' : folder,
        
        'total_results' : qs.count(),
        'publisher_id' : publisher_id,
    }
    return object_list(request, queryset=qs, allow_empty=True, page=page,
            template_name='advertiser/messages/inbox.html', paginate_by=50, extra_context=data)

@url("^messages/inquiries/$", "advertiser_messages_inquiries")
@url("^messages/inquiries/(?P<folder>(unresolved|resolved|closed))/$", "advertiser_messages_inquiries")
@url("^messages/inquiries/(?P<folder>(unresolved|resolved|closed))/page/(?P<page>[0-9]+)/$", "advertiser_messages_inquiries")
@tab("Advertiser","Messages","Inquiries")
@advertiser_required
def advertiser_messages_inquiries(request, folder="unresolved", page=1):
    #unresolved = request.organization.publisherinquiry_set.filter(status=INQUIRYSTATUS_UNRESOLVED).order_by('-date_created')
    #resolved = request.organization.publisherinquiry_set.filter(status=INQUIRYSTATUS_RESOLVED).order_by('-date_created')
    #closed = request.organization.publisherinquiry_set.filter(status=INQUIRYSTATUS_CLOSED).order_by('-date_created')
    from atrinsic.base.models import PublisherInquiry
    
    newdate = datetime.datetime.now()-datetime.timedelta(days=60)
    
    unresolved = PublisherInquiry.objects.filter(status=INQUIRYSTATUS_UNRESOLVED, advertiser=request.organization).order_by('-date_created')
    resolved = PublisherInquiry.objects.filter(status=INQUIRYSTATUS_RESOLVED, advertiser=request.organization,date_resolved__gt = newdate).order_by('-date_created')
    closed = PublisherInquiry.objects.filter(status=INQUIRYSTATUS_RESOLVED, advertiser=request.organization, date_resolved__lte = newdate).order_by('-date_created')
    if folder.lower() == "unresolved":
        qs = unresolved
        is_closed = False
    elif folder.lower() == "resolved":
        qs = resolved
        is_closed = False
    else:
        is_closed = True
        qs = closed
    inquiry_load_id = request.GET.get("inquiry_load_id",0)
    data = {
        'unresolved' : unresolved,
        'inquiry_load_id':inquiry_load_id,
        'resolved' : resolved,
        'closed' : closed,
        'is_closed':is_closed,
        'folder' : folder,
        'total_results' : qs.count(),
    }
    return object_list(request, queryset=qs, allow_empty=True, page=page,
            template_name='advertiser/messages/inquiries.html', paginate_by=50, extra_context=data)

@url("^messages/inquiry/(?P<id>[0-9]+)/$", "advertiser_messages_inquiry_view")
@advertiser_required
@register_api(None)
def advertiser_messages_inquiry_view(request, id=None):
    ''' View to display the details on a Publisher Inquiry '''
    from atrinsic.base.models import PublisherInquiry,InquiryMessage
    from forms import DenyInquiryForm
    inquiry = get_object_or_404(PublisherInquiry, id=id)

    init_dict = {
        'advertiser_reason':inquiry.advertiser_reason,
        'advertiser_reason_comment':inquiry.advertiser_reason_comment,
    }
    deny_mini_form = DenyInquiryForm(initial = init_dict)
    
    messages = InquiryMessage.objects.filter(inquiry = inquiry)
    
    return AQ_render_to_response(request, 'advertiser/messages/inquiry-view.html', {
            'inquiry' : inquiry,
            'deny_mini_form':deny_mini_form,
            'msgs':messages,
        }, context_instance=RequestContext(request))
        
@url("^messages/inquiry/update/(?P<id>[0-9]+)/$", "advertiser_messages_inquiry_update")
@advertiser_required
@register_api(None)
def advertiser_messages_inquiry_update(request, id):
    from atrinsic.base.models import PublisherInquiry,InquiryMessage
    from forms import DenyInquiryForm
    inquiry = get_object_or_404(PublisherInquiry, id=id)
    deny_mini_form = DenyInquiryForm(request.GET)
    if deny_mini_form.is_valid():
        "Form is valid"
        inquiry.status = INQUIRYSTATUS_RESOLVED
        inquiry.date_resolved = datetime.datetime.now()
        inquiry.advertiser_reason = request.GET.get("advertiser_reason",None)
        #inquiry.advertiser_reason_comment = request.GET.get("advertiser_reason_comment",None)
        inquiry.save()
        
        InquiryMessage.objects.create(inquiry = inquiry,sentby_publisher = 0,msg=request.GET.get("advertiser_reason_comment",None))
        
        return HttpResponseRedirect(reverse('advertiser_messages_inquiries')) 
    else:
        return AQ_render_to_response(request, 'advertiser/messages/inquiry-view.html', {
            'inquiry' : inquiry,
            'deny_mini_form':deny_mini_form,
        }, context_instance=RequestContext(request))
@url(r"^messages/settings/$","advertiser_messages_settings")
@tab("Advertiser","Messages","Settings")
@register_api(None)
@advertiser_required
def advertiser_messages_settings(request):
    ''' This View provides the Advertiser Settings for Messages '''
    from atrinsic.base.models import PrivateMessage,UserProfile
    from forms import AdvertiserEmailSettingsForm,ProfileRecvForm
    from django.db.models import Q
    
    # Folder totals for sidebar
    inbox = PrivateMessage.objects.filter(receiver=request.organization.id, receiver_status=1).order_by('-date_sent')
    sent = PrivateMessage.objects.filter(sender=request.organization.id, sender_status=1).order_by('-date_sent')
    trash =  PrivateMessage.objects.filter(Q(sender=request.organization.id, sender_status=3) | Q(receiver=request.organization.id, receiver_status=3)).order_by('-date_sent')

    org = request.organization
    users = UserProfile.objects.filter(organizations__id=org.id)

    if request.method == 'POST':
        rforms = [(f, ProfileRecvForm(request.POST, prefix="%s" % f.user.id, instance=f)) for f in users]
        form = AdvertiserEmailSettingsForm(request.POST, instance=request.organization)

        for x, rform in rforms:
            if rform.is_valid():
                rform.save()

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('advertiser_messages_settings'))
    else:
        rforms = [(f, ProfileRecvForm(prefix="%s" % f.user.id, instance=f)) for f in users]
        form = AdvertiserEmailSettingsForm(instance=request.organization)

    return AQ_render_to_response(request, 'advertiser/messages/settings.html', {
        'inbox' : inbox,
        'sent' : sent,
        'trash' : trash,
        'form': form,
        'rforms': rforms,
        }, context_instance=RequestContext(request))


@url("^messages/(?P<id>[0-9]+)/$", 'advertiser_messages_view')
@tab("Advertiser","Messages","Folders")
@register_api(None)
@advertiser_required
def advertiser_messages_view(request, id):
    ''' View a PrivateMessage '''
    from atrinsic.base.models import PrivateMessage
    from django.db.models import Q
    message = get_object_or_404(PrivateMessage, id=id)

    if message.receiver != request.organization  and message.sender != request.organization:
        raise Http404

    if message.receiver == request.organization:
        message.read = True
        message.save()

    # Folder totals for sidebar
    inbox = PrivateMessage.objects.filter(receiver=request.organization.id, receiver_status=1).order_by('-date_sent')
    sent = PrivateMessage.objects.filter(sender=request.organization.id, sender_status=1).order_by('-date_sent')
    trash =  PrivateMessage.objects.filter(Q(sender=request.organization.id, sender_status=3) | Q(receiver=request.organization.id, receiver_status=3)).order_by('-date_sent')

    return AQ_render_to_response(request, 'advertiser/messages/view.html', {
            'message' : message,
            'inbox' : inbox,
            'trash' : trash,
            'sent' : sent,
        }, context_instance=RequestContext(request))


@url("^messages/compose/$", 'advertiser_messages_compose')
@url("^messages/compose/(?P<id>[0-9]+)/$", 'advertiser_messages_compose')
@tab("Advertiser","Messages","Folders")
@register_api(None)
@advertiser_required
def advertiser_messages_compose(request, id=None):
    ''' View to Compose Private Message.  The recipient ID can be passed in the URL
        or through a GET variable "rid" and passing an ID on the URL for replying 
        to a message pass'''

    from atrinsic.base.models import PrivateMessage,Organization_Status,Organization,MsgStatus
    from forms import StatusUpdateForm,AdvertiserPrivateMessageForm,PrivateMessageForm
    from django.db.models import Q
    composeTo = None
    if id != None:
        publisher_id = [PrivateMessage.objects.get(id=id).sender.id]
    else:
        publisher_id = request.REQUEST.getlist('publisher_id')
        
    if request.POST.get('MessageOrStatus', 'Msg') == 'Status':
        
        form = StatusUpdateForm(request.POST)
        if form.is_valid():
            Organization_Status.objects.create(message=form.cleaned_data['message'], organization=request.organization)
            return HttpResponseRedirect('/advertiser/messages/')

    if request.method == "POST":

        if len(publisher_id) > 0:
            form = PrivateMessageForm(request.POST)
        else:
            form = AdvertiserPrivateMessageForm(request.POST,org=request.organization)			

        if form.is_valid():
            if not publisher_id:
                publisher_id = [ form.cleaned_data['receiver'], ]

            for p_id in publisher_id:
                try:
                    publisher = Organization.objects.get(id=p_id)
    
                    PrivateMessage.objects.create(subject=form.cleaned_data['subject'], date_sent=datetime.datetime.now(),
                        message=form.cleaned_data['message'], sender=request.organization, 
                        receiver=publisher, is_active=True, sender_status=MsgStatus(pk=1),receiver_status=MsgStatus(pk=1))

                except Organization.DoesNotExist:
                    pass

            referer = request.META.get('HTTP_REFERER', None)
            if referer == None:
                return HttpResponseRedirect("/advertiser/messages/")
            else:
                return HttpResponseRedirect(referer)
    else:
        d = { }

        if 'rid' in request.GET:

            try:
                rid = int(request.GET.get('rid', 0))

            except ValueError:
                rid = 0

            if rid > 0:
                try:
                    recip = Organization.objects.get(id=rid)
                    d['receiver'] = recip.name
                    publisher_id = [rid]
                except Organizaion.DoesNotExist:
                    pass

        if id:
            try:
                m = PrivateMessage.objects.get(id=id, receiver=request.organization)
                d['subject'] = 'Re: %s' % m.subject
                d['receiver'] = m.sender.name
                d['message'] = "On %s, %s wrote:\n%s" % (m.date_sent, m.sender.name, m.message, )
            except PrivateMessage.DoesNotExist:
                raise Http404

        if d.get('receiver'):
            form = PrivateMessageForm(initial=d)
        else:					
            composeTo = request.GET.get("compose_to", None)
            form = AdvertiserPrivateMessageForm(org=request.organization,initial=d)

    # This is used to load the compose form within the 2nd level of lightboxes..ie, Lightbox loading a lightbox.
    if 'secondtier' in request.GET:
        secondTier = request.GET.get('secondtier')
    else:
        secondTier = 0

    # Folder totals for sidebar
    inbox = PrivateMessage.objects.filter(receiver=request.organization.id, receiver_status=1).order_by('-date_sent')
    sent = PrivateMessage.objects.filter(sender=request.organization.id, sender_status=1).order_by('-date_sent')
    trash =  PrivateMessage.objects.filter(Q(sender=request.organization.id, sender_status=3) | Q(receiver=request.organization.id, receiver_status=3)).order_by('-date_sent')
    
    return AQ_render_to_response(request, 'advertiser/messages/compose.html', {
            'form' : form,
            'inbox' : inbox,
            'trash' : trash,
            'sent' : sent,
            'publisher_id' : publisher_id,
            'composeTo' : composeTo,
            'secondTier' : secondTier,
        }, context_instance=RequestContext(request))

@url("^messages/delete/$", 'advertiser_messages_delete')
@url("^messages/delete/(?P<id>[0-9]+)/$", 'advertiser_messages_delete')
@register_api(None)
@advertiser_required
def advertiser_messages_delete(request, id=None):
    ''' Delete a Private Message.  The Message to delete can be passed in the URL
        or multiple IDs can be passed as the POST variable "m_id" '''
    from atrinsic.base.models import PrivateMessage,MsgStatus    
    if request.method == "POST":  
        ids = request.POST.getlist("m_id")
        
        if request.POST.get('folder','') != 'trash':
            for id in ids:
                try:
                    message = PrivateMessage.objects.get(id=id)
                
                    if message.receiver == request.organization:
                        message.is_active = False
                        message.receiver_status=MsgStatus(pk=3)
                        message.save()
                    if message.sender == request.organization:
                        message.is_active = False
                        message.sender_status=MsgStatus(pk=3)
                        message.save()

                except PrivateMessage.DoesNotExist:
                    continue
        
        if request.POST.get('folder','') == 'trash':
            for id in ids:
                try:
                    message = PrivateMessage.objects.get(id=id)
                    
                    if message.receiver == request.organization:
                        message.is_active = False
                        message.receiver_status=MsgStatus(pk=4)
                        message.save()
                    if message.sender == request.organization:
                        message.is_active = False
                        message.sender_status=MsgStatus(pk=4)
                        message.save()
                        
                except PrivateMessage.DoesNotExist:
                    continue  
                
    else:
        message = get_object_or_404(PrivateMessage, id=id)

        if message.receiver != request.organization and message.sender != request.organization:
            raise Http404

        if message.receiver == request.organization:
            message.is_active = False
            message.receiver_status=MsgStatus(pk=3)
            message.save()
        elif message.sender == request.organization:
            message.is_active = False
            message.sender_status=MsgStatus(pk=3)
            message.save()
            return HttpResponseRedirect('/advertiser/messages/sent/')
        

    return HttpResponseRedirect('/advertiser/messages/')

@url("^messages/delete/trash/$", 'advertiser_messages_delete_trash')
@url("^messages/delete/trash/(?P<id>[0-9]+)/$", 'advertiser_messages_delete_trash')
@advertiser_required
@register_api(None)
def advertiser_messages_delete_trash(request, id=None):
    ''' Delete a PrivateMessage thats already trashed.  This view handles bulk deleting through the POST variable
        'm_id' '''
    from atrinsic.base.models import PrivateMessage,MsgStatus    

    message = get_object_or_404(PrivateMessage, id=id)

    if message.receiver != request.organization and message.sender != request.organization:
        raise Http404

    if message.receiver == request.organization:
        message.del_trash = True
        message.receiver_status=MsgStatus(pk=4)
        message.save()
    if message.sender == request.organization:
        message.del_trash = True
        message.sender_status=MsgStatus(pk=4)
        message.save()

    return HttpResponseRedirect('/advertiser/messages/trash/')

@url("^messages/orgnames/$", 'advertiser_messages_orgnames')
@advertiser_required
@register_api(None)
def advertiser_messages_orgnames(request):
    ''' This view provides a jQuery autocompletion '''

    q = request.GET.get('q', None)
    organizations = Organization.objects.filter(company_name__istartswith=q) 

    return AQ_render_to_response(request, 'advertiser/messages/orgnames.html', {
            'organizations' : organizations,
        }, context_instance=RequestContext(request))



@url(r"^messages/campaigns/$","advertiser_messages_campaigns")
@tab("Advertiser","Messages","Campaigns")
@register_api(api_context=('id', 'name', 'date_created', 'publisher_vertical', 'program_term',
                           'promotion_method', 'email_from', 'reply_to_address', 'body',
                           'html_body', 'publisher_group', 'emailcampaigncriteria_set', ))
@advertiser_required
def advertiser_messages_campaigns(request, page=None):
    ''' This view provides a list of all EmailCampaigns for an Advertiser '''
    
    inbox = request.organization.received_messages.filter(is_active=True).order_by('-date_sent')
    sent = request.organization.sent_messages.filter(is_active=True).order_by('-date_sent')
    trash = request.organization.received_messages.filter(is_active=False).order_by('-date_sent')

    qs = request.organization.emailcampaign_set.all()

    return object_list(request, queryset=qs, allow_empty=True, page=page,
            template_name='advertiser/messages/campaigns.html', paginate_by=50, extra_context={
                'total_results' : qs.count(),
                'inbox' : inbox,
                'sent' : sent,
                'trash' : trash,
            })


@url(r"^messages/campaigns/add/$","advertiser_messages_campaigns_add")
@tab("Advertiser","Messages","Campaigns")
@advertiser_required
@register_api(None)
def advertiser_messages_campaigns_add(request):
    ''' This view allows Advertisers to create a new EmailCampaign.  Additionally
        the Campaign can be assigned to a Group by providing a group_id '''
    from forms import EmailCampaignForm
    from atrinsic.base.models import EmailCampaign, PublisherGroup
    group_id = request.REQUEST.get('group_id', None)
 
    if request.method == "POST":
        form = EmailCampaignForm(request.POST, org=request.organization)

        if form.is_valid():
            c = EmailCampaign(advertiser=request.organization)
            for k, v in form.cleaned_data.items():
                setattr(c, k, v)
            c.save()

            if group_id:
                try:
                    g = PublisherGroup.objects.get(id=group_id)
                    c.publisher_group.add(g)
                except PublisherGroup.DoesNotExist:
                    pass
            return HttpResponseRedirect('/advertiser/messages/campaigns/%d/' % c.id)
    else:
        form = EmailCampaignForm(initial={'date_send': datetime.date.today()}, org=request.organization)

    return AQ_render_to_response(request, 'advertiser/messages/campaign-add.html', {
            'form' : form,
            'group_id' : group_id,
        }, context_instance=RequestContext(request))


@url(r"^messages/campaigns/(?P<id>[0-9]+)/$","advertiser_messages_campaigns_view")
@tab("Advertiser","Messages","Campaigns")
@advertiser_required
@register_api(None)
def advertiser_messages_campaigns_edit(request, id):
    ''' This view provides a mechanism for editing a particular EmailCampaign and
        associating Criteria for the Campaign being viewed. '''
    from atrinsic.base.models import PublisherVertical,PromotionMethod,ProgramTerm,PublisherGroup,EmailCampaignCriteria
    from forms import EmailCampaignCriteriaForm
    
    form = EmailCampaignCriteriaForm()
    campaign = get_object_or_404(request.organization.emailcampaign_set, id=id)
    verticals = PublisherVertical.objects.filter(is_adult=request.organization.is_adult).order_by('order')
    terms = request.organization.programterm_set.all()
    groups = request.organization.publisher_groups.all()
    methods = PromotionMethod.objects.all().order_by('order')
    hide_form = True

    vertical = request.POST.get('updateVertical', None)
    vertical_list = request.POST.getlist("hiddenVerticals")
    
    term = request.POST.get('updateTerm', None)
    term_list = request.POST.getlist("hiddenTerms")
    
    group = request.POST.get('updateGroup', None)
    group_list = request.POST.getlist("hiddenGroups")
    
    method = request.POST.get('updateMethod', None)
    method_list = request.POST.getlist("hiddenMethods")
    

    if vertical:
        try:
            for v in campaign.publisher_vertical.filter(is_adult=request.organization.is_adult):
                    campaign.publisher_vertical.remove(v)
            for v in vertical_list:
                campaign.publisher_vertical.add(v)
        except PublisherVertical.DoesNotExist:
            pass

    elif method:
        try:
            for m in campaign.promotion_method.all():
                campaign.promotion_method.remove(m)
            for m in method_list:
                campaign.promotion_method.add(m)
        except PublisherVertical.DoesNotExist:
            pass

    elif term:
        try:
            for t in campaign.program_term.all():
                campaign.program_term.remove(t)
            for t in term_list:
                campaign.program_term.add(t)
        except ProgramTerm.DoesNotExist:
            pass

    elif group:
        try:
            for g in campaign.publisher_group.all():
                campaign.publisher_group.remove(g)
            for g in group_list:
                campaign.publisher_group.add(g)
        except PublisherGroup.DoesNotExist:
            pass

    elif request.method == "POST":
        form = EmailCampaignCriteriaForm(request.POST)

        if form.is_valid():
            c = EmailCampaignCriteria.objects.create(email_campaign=campaign,
                                                     time_period=form.cleaned_data['time_period'],
                                                     alert_field=form.cleaned_data['alert_field'],
                                                     field_is_less_than_threshold=form.cleaned_data['field_is_less_than_threshold'],
                                                     threshold=form.cleaned_data['threshold'])

            form = EmailCampaignCriteriaForm()
        else:
            hide_form = False

    return AQ_render_to_response(request, 'advertiser/messages/campaign-view.html', {
                'verticals' : verticals,
                'methods' : methods,
                'groups' : groups,
                'terms' : terms,
                'hide_form': hide_form,
                'form' : form,
                'campaign' : campaign,
            }, context_instance=RequestContext(request))

@url(r"^messages/campaigns/(?P<id>[0-9]+)/deletevertical/(?P<v_id>[0-9]+)/$", "advertiser_messages_campaigns_delete_vertical")
@advertiser_required
@register_api(None)
def advertiser_messages_campaigns_delete_vertical(request, id, v_id):
    ''' This view deletes a vertical assotiated with an EmailCampaign '''
    from atrinsic.base.models import PublisherVertical
    
    campaign = get_object_or_404(request.organization.emailcampaign_set, id=id)
    campaign.publisher_vertical.remove(PublisherVertical.objects.get(order=v_id))
    
    return HttpResponseRedirect('/advertiser/messages/campaigns/%d' % campaign.id)


@url(r"^messages/campaigns/(?P<id>[0-9]+)/deletemethod/(?P<m_id>[0-9]+)/$", "advertiser_messages_campaigns_delete_method")
@advertiser_required
@register_api(None)
def advertiser_messages_campaigns_delete_method(request, id, m_id):
    ''' View to delete PromotionMethods associated with a Campaign '''
    from atrinsic.base.models import PromotionMethod

    campaign = get_object_or_404(request.organization.emailcampaign_set, id=id)
    campaign.promotion_method.remove(PromotionMethod.objects.get(order=m_id))
    
    return HttpResponseRedirect('/advertiser/messages/campaigns/%d' % campaign.id)


@url(r"^messages/campaigns/(?P<id>[0-9]+)/deleteterm/(?P<t_id>[0-9]+)/$", "advertiser_messages_campaigns_delete_term")
@advertiser_required
@register_api(None)
def advertiser_messages_campaigns_delete_term(request, id, t_id):
    ''' View to delete ProgramTerms associated with an EmailCampaign ['''
    from atrinsic.base.models import ProgramTerm
    
    campaign = get_object_or_404(request.organization.emailcampaign_set, id=id)
    campaign.program_term.remove(ProgramTerm.objects.get(id=t_id))
    
    return HttpResponseRedirect('/advertiser/messages/campaigns/%d' % campaign.id)

@url(r"^messages/campaigns/(?P<id>[0-9]+)/deletegroup/(?P<g_id>[0-9]+)/$", "advertiser_messages_campaigns_delete_group")
@advertiser_required
@register_api(None)
def advertiser_messages_campaigns_delete_group(request, id, g_id):
    ''' View to delete a PublisherGroup associated with an EmailCampaign '''
    from atrinsic.base.models import PublisherGroup

    campaign = get_object_or_404(request.organization.emailcampaign_set, id=id)
    campaign.publisher_group.remove(PublisherGroup.objects.get(id=g_id))
    
    return HttpResponseRedirect('/advertiser/messages/campaigns/%d' % campaign.id)


@url(r"^messages/campaigns/(?P<id>[0-9]+)/deletecriteria/(?P<c_id>[0-9]+)/$", "advertiser_messages_campaigns_delete_criteria")
@advertiser_required
@register_api(None)
def advertiser_messages_campaigns_delete_criteria(request, id, c_id):
    ''' View to delete Criteria associated with an EmailCampaign '''

    campaign = get_object_or_404(request.organization.emailcampaign_set, id=id)
    criteria = get_object_or_404(campaign.emailcampaigncriteria_set, id=c_id)

    criteria.delete()

    return HttpResponseRedirect('/advertiser/messages/campaigns/%d/' % campaign.id)


@url(r"^messages/campaigns/(?P<id>[0-9]+)/activate/$", "advertiser_messages_campaigns_activate")
@advertiser_required
@register_api(None)
def advertiser_messages_campaigns_activate(request, id):
    ''' Activate an EmailCampaign '''

    campaign = get_object_or_404(request.organization.emailcampaign_set, id=id)
    campaign.is_active = True
    campaign.save()
    
    return HttpResponseRedirect('/advertiser/messages/campaigns/')

@url(r"^messages/campaigns/(?P<id>[0-9]+)/deactivate/$", "advertiser_messages_campaigns_deactivate")
@advertiser_required
@register_api(None)
def advertiser_messages_campaigns_deactivate(request, id):
    ''' De-Activate an EmailCampaign '''

    campaign = get_object_or_404(request.organization.emailcampaign_set, id=id)
    campaign.is_active = False
    campaign.save()
 
    return HttpResponseRedirect('/advertiser/messages/campaigns/')


@url(r"^messages/campaigns/(?P<id>[0-9]+)/edit/$","advertiser_messages_campaigns_edit")
@tab("Advertiser","Messages","Campaigns")
@advertiser_required
@register_api(None)
def advertiser_messages_campaigns_edit(request, id):
    ''' View to edit an EmailCampaign '''
    from forms import EmailCampaignForm
    campaign = get_object_or_404(request.organization.emailcampaign_set, id=id)

    if request.method == "POST":
        form = EmailCampaignForm(request.POST, org=request.organization)

        if form.is_valid():
            for k, v in form.cleaned_data.items():
                setattr(campaign, k, v)

            campaign.save()
            return HttpResponseRedirect('/advertiser/messages/campaigns/%d/' % campaign.id)

    else:
        form = EmailCampaignForm(initial={
                    'name' : campaign.name,
                    'email_from' : campaign.email_from,
                    'reply_to_address' : campaign.reply_to_address,
                    'subject' : campaign.subject,
                    'body' : campaign.body,
                    'html_body' : campaign.html_body,
                    'date_send': datetime.date.today(),
               }, org=request.organization)

    return AQ_render_to_response(request, 'advertiser/messages/campaign-edit.html', {
                'campaign' : campaign,
                'form' : form,
            }, context_instance=RequestContext(request))

@url(r"^messages/welcome_email/view/html/$", "advertiser_messages_welcome_email_view_html")
@advertiser_required
@register_api(None)
def advertiser_messages_welcome_email_view_html(request):
    from atrinsic.util.mail import *
    ''' View to display the current Welcome Email HTML for this Advertiser '''

    return AQ_render_to_response(request, 'advertiser/messages/welcome-email-view.html', {
        'data' : render_html(request.organization.publisher_welcome_mail_html,request.organization,None),
                }, context_instance=RequestContext(request))

@url(r"^messages/welcome_email/view/$", "advertiser_messages_welcome_email_view")
@advertiser_required
@register_api(None)
def advertiser_messages_welcome_email_view(request):
    from atrinsic.util.mail import *
    ''' View to display the current Welcome Email for this Advertiser '''
    return AQ_render_to_response(request, 'advertiser/messages/welcome-email-view.html', {
                    'data' : render_text(request.organization.publisher_welcome_mail,request.organization,None),
                }, context_instance=RequestContext(request))


@url(r"^messages/welcome_email/$","advertiser_messages_welcome_email")
@tab("Advertiser","Messages","Welcome Email")
@advertiser_required
@register_api(None)
def advertiser_messages_welcome_email(request):
    ''' View this Advertisers Welcome Email.  If the Welcome Email has not been set yet, go 
        directly to the Editing page '''
    from forms import WelcomeEmailForm
    from atrinsic.util.mail import *
    from atrinsic.base.models import PrivateMessage
    from django.db.models import Q
    
    if request.organization.publisher_welcome_mail is None or request.organization.publisher_welcome_mail_html is None or len(request.organization.publisher_welcome_mail) < 1 or len(request.organization.publisher_welcome_mail_html) < 1:
        return HttpResponseRedirect('/advertiser/messages/welcome_email/edit/')

    # Folder totals for sidebar
    inbox = PrivateMessage.objects.filter(receiver=request.organization.id, receiver_status=1).order_by('-date_sent')
    sent = PrivateMessage.objects.filter(sender=request.organization.id, sender_status=1).order_by('-date_sent')
    trash =  PrivateMessage.objects.filter(Q(sender=request.organization.id, sender_status=3) | Q(receiver=request.organization.id, receiver_status=3)).order_by('-date_sent')

    form = WelcomeEmailForm(initial={'body' : render_text(request.organization.publisher_welcome_mail,request.organization,None),
                                     'html_body' : render_html(request.organization.publisher_welcome_mail_html,request.organization,None), 
                                     'subject' : request.organization.publisher_welcome_mail_subject, })

    return AQ_render_to_response(request, 'advertiser/messages/welcome-email.html', {
                'inbox' : inbox,
                'sent' : sent,
                'trash' : trash,
                'body' : request.organization.publisher_welcome_mail,
                'html_body' : request.organization.publisher_welcome_mail_html,
                'subject' : request.organization.publisher_welcome_mail_subject,
            }, context_instance=RequestContext(request))

@url(r"^messages/welcome_email/edit/$","advertiser_messages_welcome_email_edit")
@tab("Advertiser","Messages","Welcome Email")
@advertiser_required
@register_api(None)
def advertiser_messages_welcome_email_edit(request):
    ''' View to edit this Advertiser's Welcome Email '''
    from forms import WelcomeEmailForm
    from atrinsic.base.models import PrivateMessage
    from django.db.models import Q
    # Folder totals for sidebar
    inbox = PrivateMessage.objects.filter(receiver=request.organization.id, receiver_status=1).order_by('-date_sent')
    sent = PrivateMessage.objects.filter(sender=request.organization.id, sender_status=1).order_by('-date_sent')
    trash =  PrivateMessage.objects.filter(Q(sender=request.organization.id, sender_status=3) | Q(receiver=request.organization.id, receiver_status=3)).order_by('-date_sent')

    if request.method == 'POST':
        form = WelcomeEmailForm(request.POST)

        if form.is_valid():
            request.organization.publisher_welcome_mail_subject = form.cleaned_data['subject']
            request.organization.publisher_welcome_mail = form.cleaned_data['body']
            request.organization.publisher_welcome_mail_html = form.cleaned_data['html_body']
            request.organization.save()

            return HttpResponseRedirect('/advertiser/messages/welcome_email/')
    else:
        form = WelcomeEmailForm(initial={'body' : request.organization.publisher_welcome_mail,
                                         'html_body' : request.organization.publisher_welcome_mail_html, 
                                         'subject' : request.organization.publisher_welcome_mail_subject, })

    return AQ_render_to_response(request, 'advertiser/messages/welcome-email-edit.html', {
                'inbox' : inbox,
                'sent' : sent,
                'trash' : trash,
                'form' : form,
            }, context_instance=RequestContext(request))
