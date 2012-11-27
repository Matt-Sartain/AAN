from django.template import RequestContext
from atrinsic.util.imports import *

# Navigation Tab to View mappings for the Publisher Messages Menu
tabset("Publisher",3,"Messages","publisher_messages",
       [("Inbox","publisher_messages"),
        ("Inquiries","publisher_messages_inquiries"),
        ("Settings","publisher_messages_settings"), ])



@url("^messages/$", "publisher_messages")
@url("^messages/page/(?P<page>[0-9]+)/$", "publisher_messages")
@url("^messages/(?P<folder>(inbox|sent|trash))/$", "publisher_messages")
@url("^messages/(?P<folder>(inbox|sent|trash))/page/(?P<page>[0-9]+)/$", "publisher_messages")
@tab("Publisher","Messages","Folders")
@publisher_required
@register_api(api_context=('id', 'sender', 'receiver', 'read', 'subject', 'message', 'created', ))
def publisher_messages(request, folder="inbox", page=1):
    ''' View to display a Publishers Private Messages.  This view handles different folders
        determined by the URL as well as folder totals in the sidebar.'''
    from atrinsic.base.models import PrivateMessage
    from django.db.models import Q

    advertiser_id = request.GET.get("advertiser_id", None)
    #inbox = request.organization.received_messages.filter(is_active=True).order_by('-date_sent')
    #sent = request.organization.sent_messages.filter(is_active=True).order_by('-date_sent')
    #trash = request.organization.received_messages.filter(is_active=False).order_by('-date_sent')
    
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
        'advertiser_id' : advertiser_id,
    }
    return object_list(request, queryset=qs, allow_empty=True, page=page,
            template_name='publisher/messages/inbox.html', paginate_by=50, extra_context=data)

@url(r"^messages/settings/$","publisher_messages_settings")
@tab("Publisher","Messages","Settings")
@publisher_required
@register_api(None)
def publisher_messages_settings(request):
    ''' View to allow a Publisher to specify their Private Message Settings and Email 
        Settings.  This view dispalys folder totals in the sidebar. '''
    from atrinsic.base.models import UserProfile,PrivateMessage
    from forms import PublisherEmailSettingsForm, PublisherProfileRecvForm
    from django.db.models import Q
    
    inbox = PrivateMessage.objects.filter(receiver=request.organization.id, receiver_status=1).order_by('-date_sent')
    sent = PrivateMessage.objects.filter(sender=request.organization.id, sender_status=1).order_by('-date_sent')
    trash =  PrivateMessage.objects.filter(Q(sender=request.organization.id, sender_status=3) | Q(receiver=request.organization.id, receiver_status=3)).order_by('-date_sent')
    org = request.organization
    users = UserProfile.objects.filter(organizations__id=org.id)

    if request.method == 'POST':
        rforms = [(f, PublisherProfileRecvForm(request.POST, prefix=f.user.id, instance=f)) for f in users]
        form = PublisherEmailSettingsForm(request.POST)

        for x, rform in rforms:
            if rform.is_valid():
                rform.save()

        if form.is_valid():
            org.pub_program_email = form.cleaned_data['pub_program_email']
            org.save()
            return HttpResponseRedirect(reverse('publisher_messages_settings'))
    else:
        rforms = [(f, PublisherProfileRecvForm(prefix=f.user.id, instance=f)) for f in users]
        form = PublisherEmailSettingsForm(initial={
            'pub_program_email': org.pub_program_email,
        })

    return AQ_render_to_response(request, 'publisher/messages/settings.html', {
        'inbox' : inbox,
        'sent' : sent,
        'trash' : trash,
        'form': form,
        'rforms': rforms,
        }, context_instance=RequestContext(request))


@url("^messages/(?P<id>[0-9]+)/$", 'publisher_messages_view')
@tab("Publisher","Messages","Folders")
@publisher_required
@register_api(None)
def publisher_messages_view(request, id):
    ''' View a Message
    '''
    from atrinsic.base.models import PrivateMessage
    from django.db.models import Q
        
    message = get_object_or_404(PrivateMessage, id=id)

    if message.receiver != request.organization  and message.sender != request.organization:
        raise Http404

    if message.receiver == request.organization:
        message.read = True
        message.save()

    inbox = PrivateMessage.objects.filter(receiver=request.organization.id, receiver_status=1).order_by('-date_sent')
    sent = PrivateMessage.objects.filter(sender=request.organization.id, sender_status=1).order_by('-date_sent')
    trash =  PrivateMessage.objects.filter(Q(sender=request.organization.id, sender_status=3) | Q(receiver=request.organization.id, receiver_status=3)).order_by('-date_sent')

    return AQ_render_to_response(request, 'publisher/messages/view.html', {
            'message' : message,
            'inbox' : inbox,
            'trash' : trash,
            'sent' : sent,
        }, context_instance=RequestContext(request))


@url("^messages/compose/$", 'publisher_messages_compose')
@url("^messages/compose/(?P<id>[0-9]+)/$", 'publisher_messages_compose')
@tab("Publisher","Messages","Folders")
@publisher_required
@register_api(None)
def publisher_messages_compose(request, id=None):
    ''' View to Compose a PrivateMessage.  This view can be passed multiple
        recipients through the GET variable "r_id" '''
    from atrinsic.base.models import Organization, Organization_Status, PrivateMessage, PublisherRelationship, MsgStatus
    from forms import PrivateMessageForm, PublisherPrivateMessageForm, StatusUpdateForm
    from django.db.models import Q
    from django.core.mail import EmailMultiAlternatives

    composeTo = None
        
    if request.POST.get('MessageOrStatus', 'Msg') == 'Status':
        form = StatusUpdateForm(request.POST)
        if form.is_valid():
            Organization_Status.objects.create(message=form.cleaned_data['message'], organization=request.organization)
            return HttpResponseRedirect('/publisher/messages/')
            
        if id != None:
            advertiser_id = [PrivateMessage.objects.get(id=id).sender.id]
        else:
            advertiser_id = request.REQUEST.getlist('advertiser_id')
    else:    	
        if id != None:
            advertiser_id = [PrivateMessage.objects.get(id=id).sender.id]
        else:
            advertiser_id = request.REQUEST.getlist('advertiser_id')

        if request.method == "POST":            
            if len(advertiser_id) > 0:
                form = PrivateMessageForm(request.POST)
            else:
                form = PublisherPrivateMessageForm(request.POST,org=request.organization)
    
            if form.is_valid():            	
                if not advertiser_id:
                    advertiser_id = [ form.cleaned_data['receiver'], ]
                    print "here"
                for p_id in advertiser_id:
                    try:
                        advertiser = Organization.objects.get(id=p_id)
    
                        PrivateMessage.objects.create(subject=form.cleaned_data['subject'], date_sent=datetime.datetime.now(),
                            message=form.cleaned_data['message'], sender=request.organization, 
                            receiver=advertiser, is_active=True, sender_status=MsgStatus(pk=1), receiver_status=MsgStatus(pk=1))
                            
                        #For Kayak advertiser, we want to send a copy of that message.
                        if int(advertiser_id[0]) == 711: 
                            destinations = ['Matthew.Sosnowski@atrinsic.com']
                            try:
                                msg = EmailMultiAlternatives('MSG to Kayak.com: ' + form.cleaned_data['subject'],form.cleaned_data['message'],'affiliates-dev@atrinsic.com',destinations)
                                msg.send()
                            except:
                                pass
                                
                    except Organization.DoesNotExist:
                        pass
    
    
                referer = request.META.get('HTTP_REFERER', None)
                if referer == None:
                    return HttpResponseRedirect("/publisher/messages/")
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
                        advertiser_id = [rid]
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
            elif advertiser_id:
                d['receiver'] = 'Multiple Recipients'
                form = PrivateMessageForm(initial=d)
            else:
                composeTo = request.GET.get("compose_to", None)
                form = PublisherPrivateMessageForm(org=request.organization,initial=d)
    
    inbox = PrivateMessage.objects.filter(receiver=request.organization.id, receiver_status=1).order_by('-date_sent')
    sent = PrivateMessage.objects.filter(sender=request.organization.id, sender_status=1).order_by('-date_sent')
    trash =  PrivateMessage.objects.filter(Q(sender=request.organization.id, sender_status=3) | Q(receiver=request.organization.id, receiver_status=3)).order_by('-date_sent')

    return AQ_render_to_response(request, 'publisher/messages/compose.html', {
            'form' : form,
            'inbox' : inbox,
            'trash' : trash,
            'sent' : sent,
            'advertiser_id' : advertiser_id,
            'composeTo' : composeTo,
        }, context_instance=RequestContext(request))

@url("^messages/delete/$", 'publisher_messages_delete')
@url("^messages/delete/(?P<id>[0-9]+)/$", 'publisher_messages_delete')
@publisher_required
@register_api(None)
def publisher_messages_delete(request, id=None):
    ''' Delete a PrivateMessage.  This view handles bulk deleting through the POST variable
        'm_id' '''
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
        if message.sender == request.organization:
            message.is_active = False
            message.sender_status=MsgStatus(pk=3)
            message.save()
            return HttpResponseRedirect('/publisher/messages/sent/')

    return HttpResponseRedirect('/publisher/messages/')
    
@url("^messages/delete/trash/$", 'publisher_messages_delete_trash')
@url("^messages/delete/trash/(?P<id>[0-9]+)/$", 'publisher_messages_delete_trash')
@publisher_required
@register_api(None)
def publisher_messages_delete_trash(request, id=None):
    ''' Delete a PrivateMessage thats already trashed.  This view handles bulk deleting through the POST variable 'm_id' '''
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

    return HttpResponseRedirect('/publisher/messages/trash/')

""" #Can't find where this is called
@url("^messages/orgnames/$", 'publisher_messages_orgnames')
@publisher_required
@register_api(None)
def publisher_messages_orgnames(request):
    ''' This view provides jQuery autocompletion of an Organization name '''
    from atrinsic.base.models import Organization

    q = request.GET.get('q', None)
    organizations = Organization.objects.filter(name__istartswith=q) 

    return AQ_render_to_response(request, 'publisher/messages/orgnames.html', {
            'organizations' : organizations,
        }, context_instance=RequestContext(request))
"""


@url("^messages/inquiries/$", "publisher_messages_inquiries")
@url("^messages/inquiries/page/(?P<page>[0-9]+)/$", "publisher_messages_inquiries")
@url("^messages/inquiries/(?P<folder>(unresolved|resolved|closed))/$", "publisher_messages_inquiries")
@url("^messages/inquiries/(?P<folder>(unresolved|resolved|closed))/page/(?P<page>[0-9]+)/$", "publisher_messages_inquiries")
@tab("Publisher","Messages","Inquiries")
@publisher_required
@register_api(api_context=('id', 'transaction_date', 'advertiser', 'order_id', 'transaction_amount', ))
def publisher_messages_inquiries(request, folder="unresolved", page=1):
    ''' View to display a Publishers Inquiries.  This view has three different resultsets
        based on the URL:  'unresolved', 'resolved', and 'closed' respectively.  '''
    from atrinsic.base.models import PublisherInquiry
    
    newdate = datetime.datetime.now()-datetime.timedelta(days=60)
        
    unresolved = PublisherInquiry.objects.filter(status=INQUIRYSTATUS_UNRESOLVED, publisher=request.organization).order_by('-date_created')
    resolved = PublisherInquiry.objects.filter(status=INQUIRYSTATUS_RESOLVED, publisher=request.organization, date_resolved__gt = newdate).order_by('-date_created')
    archived = PublisherInquiry.objects.filter(status=INQUIRYSTATUS_RESOLVED, publisher=request.organization, date_resolved__lte = newdate).order_by('-date_created')
    
    if folder.lower() == "unresolved":
        qs = unresolved
    elif folder.lower() == "resolved":
        qs = resolved
    else:
        qs = archived

    data = {
        'unresolved' : unresolved,
        'resolved' : resolved,
        'archived' : archived,
        'folder' : folder,
        'total_results' : qs.count(),
    }
    return object_list(request, queryset=qs, allow_empty=True, page=page,
            template_name='publisher/messages/inquiry.html', paginate_by=50, extra_context=data)

@url("^messages/inquiry/new_order_inquiry/$", 'publisher_messages_new_order_inquiry')
@tab("Publisher","Messages","Inquiries")
@publisher_required
@register_api(None)
def publisher_messages_new_order_inquiry(request):
    ''' View to create a new OrderInquiry for a Publisher '''
    from atrinsic.base.models import Organization, PublisherInquiry, InquiryMessage
    from forms import OrderInquiryForm

    if request.method == "POST":
        form = OrderInquiryForm(request.POST,org=request.organization)

        if form.is_valid():
            advertiser = Organization.objects.get(id=form.cleaned_data['advertiser'])
            
            newInq = PublisherInquiry.objects.create(advertiser=advertiser,publisher=request.organization,
                                            transaction_date=form.cleaned_data["transaction_date"],
                                            is_transaction_inquiry = 1,
                                            order_id=form.cleaned_data["order_id"],
                                            transaction_amount = str(form.cleaned_data["transaction_amount"]),
                                            member_id = form.cleaned_data["member_id"],
                                            comments = form.cleaned_data["comments"],
                                            advNew='1')
                                            
            InquiryMessage.objects.create(inquiry = newInq,sentby_publisher = 1,msg=form.cleaned_data["comments"])                                

            return HttpResponseRedirect('/publisher/messages/inquiries/')
    else:

        form = OrderInquiryForm(org=request.organization)

    unresolved = request.organization.publisherinquiry_set.filter(status=INQUIRYSTATUS_UNRESOLVED).order_by('-date_created')
    resolved = request.organization.publisherinquiry_set.filter(status=INQUIRYSTATUS_RESOLVED).order_by('-date_created')
    closed = request.organization.publisherinquiry_set.filter(status=INQUIRYSTATUS_CLOSED).order_by('-date_created')

    return AQ_render_to_response(request, 'publisher/messages/new_order_inquiry.html', {
        'unresolved' : unresolved,
        'resolved' : resolved,
        'closed' : closed,
        'form' : form,
        }, context_instance=RequestContext(request))

@url("^messages/inquiry/new_payment_inquiry/$", 'publisher_messages_new_payment_inquiry')
@tab("Publisher","Messages","Inquiries")
@publisher_required
@register_api(None)
def publisher_messages_new_payment_inquiry(request):
    ''' View to create a New Payment Inquiry for a Publisher '''
    from atrinsic.base.models import Organization, PublisherInquiry, InquiryMessage
    from forms import PaymentInquiryForm

    if request.method == "POST":
        form = PaymentInquiryForm(request.POST,org=request.organization)

        if form.is_valid():
            advertiser = Organization.objects.get(id=form.cleaned_data['advertiser'])
            
            newInq = PublisherInquiry.objects.create(advertiser=advertiser,publisher=request.organization,
                                            is_transaction_inquiry=False,
                                            amount_due= str(form.cleaned_data['amount_due']),
                                            period_beginning = form.cleaned_data['period_beginning'],
                                            period_ending = form.cleaned_data['period_ending'],
                                            transaction_date = form.cleaned_data['period_ending'],
                                            comments = form.cleaned_data["comments"],
                                            advNew='1')
                                            
            InquiryMessage.objects.create(inquiry = newInq,sentby_publisher = 1,msg=form.cleaned_data["comments"])                           

            return HttpResponseRedirect('/publisher/messages/inquiries/')
    else:
        form = PaymentInquiryForm(org=request.organization)

    unresolved = request.organization.publisherinquiry_set.filter(status=INQUIRYSTATUS_UNRESOLVED).order_by('-date_created')
    resolved = request.organization.publisherinquiry_set.filter(status=INQUIRYSTATUS_RESOLVED).order_by('-date_created')
    closed = request.organization.publisherinquiry_set.filter(status=INQUIRYSTATUS_CLOSED).order_by('-date_created')

    return AQ_render_to_response(request, 'publisher/messages/new_payment_inquiry.html', {
        'unresolved' : unresolved,
        'resolved' : resolved,
        'closed' : closed,
        'form' : form,
        }, context_instance=RequestContext(request))

@url("^messages/inquiry/publisher_inquiry_add_msg/$", 'publisher_inquiry_add_msg')
@tab("Publisher","Messages","Inquiries")
@publisher_required
@register_api(None)
def publisher_inquiry_add_msg(request):
    from atrinsic.base.models import PublisherInquiry,InquiryMessage
    
    inq = PublisherInquiry.objects.get(id = request.POST['inq_id'])
    inq.advNew = True
    inq.save()
    
    InquiryMessage.objects.create(inquiry = inq, sentby_publisher = 1,msg=request.POST["additional"])
    
    return HttpResponseRedirect('/publisher/messages/inquiries/')
    
    
@url("^messages/inquiry/(?P<id>[0-9]+)/$", "publisher_messages_inquiry_view")
@publisher_required
@register_api(None)
def publisher_messages_inquiry_view(request, id=None):
    ''' View to display the details on a Publisher Inquiry '''
    from atrinsic.base.models import PublisherInquiry, InquiryMessage
    
    inquiryObj = get_object_or_404(PublisherInquiry, id=id)
    
    inquiryObj.pubNew = False
    inquiryObj.save()

    unresolved = request.organization.publisherinquiry_set.filter(status=INQUIRYSTATUS_UNRESOLVED).order_by('-date_created')
    resolved = request.organization.publisherinquiry_set.filter(status=INQUIRYSTATUS_RESOLVED).order_by('-date_created')
    closed = request.organization.publisherinquiry_set.filter(status=INQUIRYSTATUS_CLOSED).order_by('-date_created')
    
    messages = InquiryMessage.objects.filter(inquiry = inquiryObj.id)

    return AQ_render_to_response(request, 'publisher/messages/inquiry-view.html', {
            'inquiry' : inquiryObj,
            'unresolved' : unresolved,
            'resolved' : resolved,
            'closed' : closed,
            'msgs' : messages,
        }, context_instance=RequestContext(request))
