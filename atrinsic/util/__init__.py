def right_side(request):
    ''' The usual 4 colums on the right side to be returned'''
    from atrinsic.base.models import Alert, Events, News, Notifications, Organization, Organization_Followers, Organization_Status,  PrivateMessage, PublisherInquiry, PublisherRelationship
    from atrinsic.util.score_board import *
    from django.template import RequestContext
    from django.db import connection

    try:
        x=request.organization
        show=True
    except:
        show=False
  
    the_board=None
    news_vb = []
    newAdvResult = {}
    if show:
        if request.path_info[:11] == '/publisher/':
            org_live_type = "publisher"
            the_board = GetScoreBoard(request)
            news_vb = [1,2]
        elif request.path_info[:12] == '/advertiser/':
            org_live_type = "advertiser"
            the_board = GetScoreBoard(request)
            news_vb = [0,2]
        else:
            org_live_type = ''
        if request.GET.has_key('group_by'):
            group_by = request.GET['group_by']
        else:
            try:
                group_by = request.organization.dashboard_group_data_by	
            except:
                group_by = None
        var_inboxcount = 0
        status_rightside = None
        inquiries_list = None
        alerts_list = None
        news_list = None
        events_list = None
        notification_list = None
        pending_applications_list = None
        if (request.path_info[:11] == '/publisher/') or (request.path_info[:12] == '/advertiser/'):            
            try:
                var_inboxcount = PrivateMessage.objects.filter(receiver=request.organization.id, receiver_status=1, read=0).count()
    
    
                status_rightside = Organization_Status.objects.order_by('-created').extra(where=[' organization_id IN (SELECT followed_id FROM base_organization_followers WHERE stalker_id = '+str(request.organization.id)+') or organization_id = ' + str(request.organization.id) +''])
    
                inquiries_list = PublisherInquiry.objects.select_related("publisher").filter(status=INQUIRYSTATUS_UNRESOLVED,advertiser=request.organization).order_by('-date_created')
    
                alerts_list = Alert.objects.filter(organization = request.organization).order_by('-id')
                news_list = News.objects.filter(news_status = 1, viewed_by__in=news_vb).order_by('-created')
                z_date = datetime.datetime.now() - datetime.timedelta(days=7)
                events_list = Events.objects.filter(events_date__gte = z_date.strftime('%Y-%m-%d'), events_status = 1)
    
                old_notes = Notifications.objects.filter(organization = request.organization)
            
                notification_list = []
                exists = False
                
                if request.path_info[:12] == '/advertiser/':
                    exists = False
                    pending_applications_list = Organization.objects.filter(advertiser_relationships__status=RELATIONSHIP_APPLIED,advertiser_relationships__advertiser=request.organization, status=ORGSTATUS_LIVE)
                    for s in pending_applications_list:
                        if s:
                            for notes in old_notes:
                                if notes.original_id == s.id and notes.notification_type == 'Pending Application':
                                    exists = True
                            if exists == False:
                                notification_list.append((s.id, s.date_created.strftime("%m/%d/%Y"), s.name, """<a href="/advertiser/publishers/applications/" class="notification_anchor">Pending Application</a>"""))
                        exists = False
                for s in status_rightside:
                    if s:
                        for notes in old_notes:
                            if notes.original_id == s.id and notes.notification_type == 'Status Update':
                                exists = True
                        if exists == False:
                            notification_list.append((s.id, s.created.strftime("%m/%d/%Y"), s.message, 'Status Update'))
                    exists = False        
                for s in inquiries_list:
                    if s:
                        for notes in old_notes:
                            if notes.original_id == s.id and notes.notification_type == 'Publisher Inquiry':
                                exists = True
                        if exists == False:
                            notification_list.append((s.id, s.date_created.strftime("%m/%d/%Y"), s.comments[:20],"""<a href="/advertiser/messages/inquiries/" class="notification_anchor">Publisher Inquiry</a>"""))
                    exists = False
                for s in alerts_list:
                    if s:
                        for notes in old_notes:
                            if notes.original_id == s.id and notes.notification_type == 'Alert':
                                exists = True
                        if exists == False:
                            notification_list.append((s.id, s.date.strftime("%m/%d/%y"), s.organization.name, 'Alert'))
                    exists = False
                for s in news_list:
                    if s:
                        for notes in old_notes:
                            if notes.original_id == s.id and notes.notification_type == 'News Item':
                                exists = True
                        if exists == False:
                            notification_list.append((s.id, s.created.strftime("%m/%d/%Y"),s.news_status,'News Item'))        
                    exists = False
        
                notification_list.sort()
                notification_list = notification_list[:10]
                newadvs = Organization.objects.filter(org_type=2,status=3,is_private=0,is_adult=request.organization.is_adult).order_by('-date_joined')[:5]

                for adv in newadvs:

                    relationship = PublisherRelationship.objects.filter(publisher=request.organization,advertiser=adv,status__in=[1,2,3])
                    if len(relationship) == 1:

                        newAdvResult[adv.pk] = [adv.ticker_symbol,relationship[0].status,adv.company_name]
                    else:
                        newAdvResult[adv.pk] = [adv.ticker_symbol,0,adv.company_name] 
 
            except:
                pass
        if show != '':
            return {
                'right_side_alerts': alerts_list,
                'right_side_news': news_list,
                'right_side_events': events_list,
                'right_side_status': status_rightside,
                'right_side_inquiries': inquiries_list,
                'notification_list':notification_list,
                'pending_applications_list':pending_applications_list,
                'inbox_count':  var_inboxcount,
                'score_board':the_board,
                'org_live_type':org_live_type,
                'group_by':group_by,
                'newAdvResults':newAdvResult,
                'queries' : connection.queries[:],
            }
    return {}
