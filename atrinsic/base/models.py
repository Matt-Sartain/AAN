#!/usr/bin/python
# -*- coding: utf-8 -*-

import md5
import datetime
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.utils.safestring import mark_safe

from choices import *
import decimal
from atrinsic.util.smartforms import CountryField, StateField, ProvinceField
from atrinsic.web.helpers import base36_encode
from atrinsic.web.ga_managers import GA_SiteManager


class OrganizationCurrency(models.Model):
    ''' Model for Publisher Quality Scoring System '''

    advertiser = models.ForeignKey("Organization")
    currency = models.ForeignKey("Currency")

class QualityScoringSystemMetric(models.Model):
    ''' Model for Publisher Quality Scoring System Metrics '''

    key = models.CharField(max_length=256)
    weight = models.DecimalField(max_digits=10, decimal_places=2, default='0.00')


class QualityScoringSystem(models.Model):
    ''' Model for Publisher Quality Scoring System '''

    publisher = models.ForeignKey("Organization")
    metric = models.ForeignKey("QualityScoringSystemMetric")
    value = models.DecimalField(max_digits=10, decimal_places=2, default='0.00')


class SKUList(models.Model):
    ''' Model to define a SKU List '''

    advertiser = models.ForeignKey('Organization')
    name = models.CharField(max_length=256)


class SKUListItem(models.Model):
    ''' Model for a SKU List Item '''

    skulist = models.ForeignKey(SKUList)
    item = models.CharField(max_length=256)
    external_sku = models.CharField(blank=True, max_length=93)

class SKUListProgramTerm(models.Model):
    ''' Model to associate a Program Term Action to a SKUList '''

    programterm_action = models.ForeignKey('ProgramTermAction')
    skulist = models.ForeignKey(SKUList)
    is_fixed_commission = models.BooleanField(default=True) # if false, commission is a % of total sale
    commission = models.DecimalField(max_digits=10, decimal_places=2, default='0.00')


class SKUListConversion(models.Model):
    ''' Model to manage SKUList Conversions '''

    conversion = models.ForeignKey('Conversion')
    item = models.CharField(max_length=256, blank=True, null=True) # this references a item number from a product feed
    commission = models.DecimalField(max_digits=10, decimal_places=2, default='0.00')
    quantity = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, default='0.00')



class SKUListChangeLog(models.Model):
    ''' Model to store changes to SKUList commissions '''

    skulist_programterm = models.ForeignKey(SKUListProgramTerm)
    created = models.DateTimeField(auto_now_add=True)
    old_commission = models.DecimalField(max_digits=10, decimal_places=2, default='0.00')
    new_commission= models.DecimalField(max_digits=10, decimal_places=2, default='0.00')


class PeerToPeerComparisonDaily(models.Model):
    ''' Model to store Daily Peer to Peer Comparison Data '''

    organization = models.ForeignKey('Organization')
    metric = models.IntegerField(choices=METRIC_CHOICES)
    period = models.DateField()
    value = models.IntegerField()


class PeerToPeerComparisonHourly(models.Model):
    ''' Model to store Hourly Peer to Peer Comparison Data '''

    organization = models.ForeignKey('Organization')
    metric = models.IntegerField(choices=METRIC_CHOICES)
    period = models.DateTimeField()
    value = models.IntegerField()


class ServerApplication(models.Model):
    ''' Model to specify a Server Side Application '''

    name = models.CharField(max_length=255)
    description = models.TextField()
    last_run = models.DateTimeField() # time of last execution
    sla = models.PositiveIntegerField(default=0) # period in minutes

    def get_last_report(self):
       reports = self.reports.order_by('-created')

       if reports:
          return reports[0]

       return None

    last_report = property(get_last_report)
 
    def __unicode__(self):
       return self.name

class ServerApplicationReport(models.Model):
    ''' Model for tracking Server Applications '''
    
    created = models.DateTimeField(auto_now_add=True)
    application = models.ForeignKey(ServerApplication, related_name='reports')
    status = models.IntegerField(default=SERVERSTATUS_OK, choices=SERVERSTATUS_CHOICES)
    result = models.CharField(max_length=255)

    def __unicode__(self):
       return u"%s: %s: %s (%d)" % (self.created, self.application, self.result, self.status, )

class Events(models.Model):
    ''' This is the model for system News '''
    created = models.DateTimeField(auto_now_add=True)
    events_status = models.PositiveIntegerField(default=NEWSSTATUS_DRAFT, choices=NEWSSTATUS_CHOICES)
    events_name = models.CharField(blank=True, max_length=150)
    events_date = models.DateField(default=datetime.datetime.today)
    location = models.CharField(blank=True, max_length=150)
    registration = models.URLField(blank=True, verify_exists=True)
    data = models.TextField()

class WebRequest(models.Model):
    ''' This is the model for logging all WebRequests through Middleware '''

    created = models.DateTimeField(auto_now_add=True)
    method = models.CharField(max_length=6)
    url = models.CharField(max_length=255)
    organization = models.CharField(max_length=255)
    user = models.CharField(max_length=255)
    length = models.PositiveIntegerField(default=0)
    status = models.SmallIntegerField(default=0)
    request = models.TextField(default="")
    

class News(models.Model):
    ''' This is the model for system News '''

    created = models.DateTimeField(auto_now_add=True)
    news_status = models.PositiveIntegerField(default=NEWSSTATUS_DRAFT, choices=NEWSSTATUS_CHOICES)
    data = models.TextField()
    viewed_by = models.PositiveIntegerField(default=NEWS_VIEWED_BY_BOTH, choices=NEWS_VIEWED_BY_CHOICES)


class UserPasswordReset(models.Model):
    ''' This is the model for resetting user passwords '''

    user = models.ForeignKey(User, unique=True)
    reset = models.CharField(max_length=255, unique=True)

class UserProfile(models.Model):
    ''' This is an extension of the user model, this will be created as part of the user creation process'''
    user = models.ForeignKey(User,unique=True)

    recv_network = models.BooleanField(default=False)
    recv_legal = models.BooleanField(default=False)
    recv_newsletter = models.BooleanField(default=False)

    # Publisher specific
    recv_adv_emails = models.BooleanField(default=False)
    recv_net_newsletter = models.BooleanField(default=False)
    recv_promo_offers = models.BooleanField(default=False)
    
    organizations = models.ManyToManyField("Organization",blank=True,null=True)

    admin_assigned_organizations  = models.ManyToManyField("Organization",blank=True,null=True,related_name="assigned_admins")

    
    def admin_assigned_advertisers(self):
       '''Returns a list of Advertiser Organizations which the user has administrative access for'''
       if self.admin_level == ADMINLEVEL_NONE:
          return Organization.objects.none()

       if self.admin_level in [ADMINLEVEL_ACCOUNT_MANAGER_SECONDARY_ACCOUNT,ADMINLEVEL_ACCOUNT_MANAGER_PRIMARY_ACCOUNT,ADMINLEVEL_AFFILIATE_MANAGER,ADMINLEVEL_AFFILIATE_DIRECTOR]:
          return self.admin_assigned_organizations.filter(org_type=ORGTYPE_ADVERTISER, status__in=[ORGSTATUS_TEST,ORGSTATUS_LIVE])

       return Organization.objects.filter(org_type=ORGTYPE_ADVERTISER, status__in=[ORGSTATUS_TEST,ORGSTATUS_LIVE])
    
    def admin_assigned_publishers(self):
       '''Returns a list of Publisher Organizations which the user has administrative access for'''

       if self.admin_level == ADMINLEVEL_NONE:
          return Organization.objects.none()

       if self.admin_level in [ADMINLEVEL_ACCOUNT_MANAGER_SECONDARY_ACCOUNT,ADMINLEVEL_ACCOUNT_MANAGER_PRIMARY_ACCOUNT,ADMINLEVEL_AFFILIATE_MANAGER]:
          return self.admin_assigned_organizations.filter(org_type=ORGTYPE_PUBLISHER)

       return Organization.objects.filter(org_type=ORGTYPE_PUBLISHER)
       
    admin_level = models.PositiveIntegerField(default=ADMINLEVEL_NONE,choices=ADMINLEVEL_CHOICES)

    
class Organization(models.Model):
    '''This Model represents all Organizations (Publishers and Advertisers) and their respective
      properties and attributes'''
    def get_branded_signup_page_link(self):
       return "/signup/publisher/%d/" % self.id
    def get_name(self):
       '''Returns a string representing the display name of this Organization'''

       if self.show_alias == True:
          return self.company_alias

       return self.company_name    
    status = models.PositiveIntegerField(default=ORGSTATUS_UNAPPROVED,choices=ORGSTATUS_CHOICES)
    date_created = models.DateTimeField(auto_now_add=True) #  date an organization was created
    date_joined = models.DateTimeField(null=True,blank=True) # date the organization was approved by atrinsic
    show_alias = models.BooleanField(default=False)
    name = property(get_name)
    company_name = models.CharField(max_length=255) # name of the organization
    company_alias = models.CharField(max_length=255,blank=True) # alias of the organization, shown instead of name if advertiser_account_type = ADVERTISERTYPE_CPA
    ticker = models.CharField(max_length=255,blank=True) # ticker symbol of the organization.
    ticker_symbol = models.ImageField(upload_to="user_images/%Y/%m/%d", null=True, blank=True)
    org_type = models.PositiveIntegerField(default=ORGTYPE_PUBLISHER, choices=ORGTYPE_CHOICES)
    address = models.CharField(max_length=255, null=True, blank=True)
    address2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    state = StateField(null=True, blank=True)
    zipcode = models.CharField(max_length=255, null=True, blank=True)
    country = CountryField(null=True, blank=True)
    network_rating = models.DecimalField(max_digits=10, decimal_places=2, default='0.00')
    force = models.DecimalField(max_digits=10, decimal_places=2, default='0.00')
    sid_status = models.PositiveIntegerField(choices=STATUS_CHOICES,default=STATUS_DEACTIVATED)
    piggybackpixel_url = models.TextField(null=True,blank=True)
    seven_day_epc = models.DecimalField(max_digits=10, decimal_places=2, default='0.00')
    three_month_epc = models.DecimalField(max_digits=10, decimal_places=2, default='0.00')
    keyword_violation = models.BooleanField(default=False)
    trademark_violation = models.BooleanField(default=False)
    advertiser_account_type = models.PositiveIntegerField(default=ADVERTISERTYPE_SELFMANAGED, choices=ADVERTISERTYPE_CHOICES)
    network_admin = models.ForeignKey(User,blank=True,null=True,related_name="Organization_admined")
    secondary_vertical = models.ManyToManyField("PublisherVertical",null=True,blank=True,related_name="organization_secondaries")
    vertical = models.ForeignKey("PublisherVertical",null=True,blank=True)
    promotion_method = models.ForeignKey("PromotionMethod",null=True,blank=True, related_name="advertiser_promo_methods")
    allowed_banner = models.IntegerField(default=100)
    allowed_text = models.IntegerField(default=100)
    allowed_keyword = models.IntegerField(default=1)
    allowed_flash = models.IntegerField(default=15)
    allowed_email_link = models.IntegerField(default=2)
    allowed_datafeed = models.IntegerField(default=1)
    allowed_html = models.IntegerField(default=5)
    allowed_rss = models.IntegerField(default=1)
    allow_third_party_email_campaigns = models.BooleanField(default=False)
    allow_direct_linking_through_ppc = models.BooleanField(default=False)
    allow_trademark_bidding_through_ppc = models.BooleanField(default=False)
    publisher_welcome_mail_subject = models.CharField(max_length=255, null=True, blank=True)
    publisher_welcome_mail = models.TextField(null=True,blank=True)
    publisher_welcome_mail_html = models.TextField(null=True,blank=True)
    branded_signup_page_link = property(get_branded_signup_page_link)
    branded_signup_page_copy = models.TextField(null=True,blank=True)
    branded_signup_page_header_url = models.ImageField(upload_to='user_images/%Y/%m/%d', null=True, blank=True)
    advertiser_custom_program_page = models.TextField(null=True,blank=True) # html
    advertiser_profile_detail_page = models.TextField(null=True,blank=True) # html
    # Advertiser email settings
    pub_program_email = models.EmailField(blank=True)
    non_pub_program_email = models.EmailField(blank=True)
    has_program_term = models.BooleanField(default=False,blank=True,null=True)
    # Invite Integration
    invite_id = models.IntegerField(blank=True,null=True)    
    invite_campid = models.IntegerField(blank=True,null=True)    
    invite_ioid = models.IntegerField(blank=True,null=True)
    invite_piggybackpixelid = models.IntegerField(blank=True,null=True)
    # Dashboard Settings
    dashboard_group_data_by = models.PositiveIntegerField(default=REPORTGROUPBY_DAY, choices=REPORTGROUPBY_CHOICES)
    dashboard_viewing_settings = models.PositiveIntegerField(default=DASHBOARDVIEWING_ALL, choices=DASHBOARDVIEWING_CHOICES)
    dashboard_viewing_promo_method = models.ForeignKey('PromotionMethod',null=True,blank=True,related_name="organizations_dashboards")
    dashboard_viewing_vertical = models.ForeignKey('PublisherVertical',null=True,blank=True,related_name="organizations_dashboards")
    dashboard_viewing_group = models.ForeignKey('PublisherGroup',null=True,blank=True,related_name="organizations_dashboards")
    dashboard_viewing_programtype =  models.PositiveIntegerField(default=DASHBOARDVIEWINGPROGRAMTYPE_ALL, choices=DASHBOARDVIEWINGPROGRAMTYPE_CHOICES)
    dashboard_variable1 = models.PositiveIntegerField(default=DASHBOARDMETRIC_CLICKS, choices=DASHBOARDMETRIC_CHOICES)
    dashboard_variable2 = models.PositiveIntegerField(default=DASHBOARDMETRIC_CLICKS, choices=DASHBOARDMETRIC_CHOICES)
    pywik_token_auth_key = models.CharField(blank=True, null=True, max_length=50)
    pywik_siteId = models.IntegerField(blank=True, null=True)
    publisher_approval = models.IntegerField(default=0,choices = ((0, 'Manual Approve'),(1,'Auto Approve')))
    ace_id = models.IntegerField(blank=True,null=True)
    is_adult = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)

    brandlock = models.BooleanField(default=False)
    brandlock_key = models.CharField(max_length=50,blank=True)
    adbuilder = models.BooleanField(default=False)

    api_key = models.CharField(blank=True, null=True,max_length=50)

    def get_orgstatus_display(self):
       '''Returns a string representing the current status of this Organization'''

       if self.is_publisher() == True:
          for i,name in PUBORGSTATUS_CHOICES:
             if i == self.status:
                return name
       else:
          for i,name in ORGSTATUS_CHOICES:
             if i == self.status:
                return name
                
    def get_seven_day_epc_display(self):
        for payment_info in self.organizationpaymentinfo_set.all():
            return payment_info.currency.convert_display(self.seven_day_epc)

    def get_three_month_epc_display(self):
        for payment_info in self.organizationpaymentinfo_set.all():
            return payment_info.currency.convert_display(self.three_month_epc)
       
    def get_dashboard_filtered_orgs(self):
       '''YYY: Returns a list of organizations which are visible on the respective Publisher
         or Advertiser Dashboard'''

       if self.is_advertiser():
          all_publishers = Organization.objects.filter(advertiser_relationships__status=RELATIONSHIP_ACCEPTED,
                                              advertiser_relationships__advertiser=self)
          all_advertisers = None
       else:
          all_advertisers = Organization.objects.filter(publisher_relationships__status=RELATIONSHIP_ACCEPTED,
                                        publisher_relationships__publisher=self)
          all_publishers = None

       aids = None
       pids = None
    
       if self.is_advertiser():
          if self.dashboard_viewing_settings == DASHBOARDVIEWING_ALL:
             pids = [i.id for i in all_publishers]
          elif self.dashboard_viewing_settings == DASHBOARDVIEWING_PUBLISHERTYPE and self.dashboard_viewing_promotion_type:
             pids = [i.id for i in all_publishers if self.dashboard_viewing_promo_method == i.promotion_method]
          elif self.dashboard_viewing_settings == DASHBOARDVIEWING_VERTICAL and self.dashboard_viewing_vertical:
             pids = [i.id for i in all_publishers if self.dashboard_viewing_vertical == i.vertical]
          elif self.dashboard_viewing_settings == DASHBOARDVIEWING_GROUP and self.dashboard_viewing_group:
             pids = [i.id for i in all_publishers if i in self.dashboard_viewing_group.publishers.all()]
       else:
          if self.dashboard_viewing_settings == DASHBOARDVIEWING_ALL:
             aids = [i.id for i in all_advertisers]
          elif self.dashboard_viewing_settings == DASHBOARDVIEWING_VERTICAL and self.dashboard_viewing_vertical:
             aids = [i.id for i in all_advertisers if self.dashboard_viewing_vertical == i.vertical]
          elif self.dashboard_viewing_settings == DASHBOARDVIEWING_PROGRAMTYPE:
             aids = [i.id for i in all_advertisers if i.get_advertiser_relationship(publisher=self).program_term.is_fixed_action() == self.dashboard_viewing_programtype_flatfee]
          elif self.dashboard_viewing_settings == DASHBOARDVIEWING_SMARTADS_ONLY:
             aids = [i.id for i in all_advertisers if i.smartad_banner_enabled or i.smartad_product_enabled]

       return pids,aids
    

    def generate_link_hash(self,link):
       import md5
       return md5.new("%s-SALTSTRING221295182381-%s" % (self.id,link.id)).hexdigest()

    def unread_messages(self):
       return self.received_messages.filter(read=False, is_active=True).count()

    def has_violations(self):
       if self.keyword_violation or self.trademark_violation:
          return True

       return False

    def get_default_website(self):
       ''' Returns the default Website for this Organiation'''

       p = Website.objects.filter(publisher=self,is_default=True)
       if p.count() > 0:
           return p[0]
       p = Website.objects.filter(publisher=self)
       if p.count() > 0:
           return p[0]
       return None

    def get_publisher_id(self):
       ''' Returns the default Website ID to be used as a Publisher ID '''

       p = self.get_default_website()
       if p:
          return p.id
       return None
    

    def get_metric(self,metric,time_period,aids=None,pids=None):
        ''' Reporting method which returns value calculations based on passed arguments'''
        time_offset = datetime.timedelta(hours=4)
        time_period = (time_period[0]+time_offset,time_period[1]+time_offset)
        if self.is_advertiser():
            if aids != "All":
                data_set = Report_Adv_Pub.objects.filter(advertiser=self)
                if pids:
                    data_set = data_set.filter(publisher__in=pids)
            else:
                if pids:
                    data_set = Report_Adv_Pub.objects.filter(publisher__in=pids)
        elif self.is_publisher():
            data_set = Report_Adv_Pub.objects.filter(publisher=self)
            if aids:
                data_set = data_set.filter(advertiser__in=aids)
                
        if metric == METRIC_IMPRESSIONS:
            total = 0
            for x in data_set.filter(impressions__gt=0,report_date__range=(time_period[0],time_period[1])):
                total+=x.impressions
            return total
        if metric == METRIC_CLICKS:
            total = 0
            for x in data_set.filter(clicks__gt=0,report_date__range=(time_period[0],time_period[1])):
                total+=x.clicks
            return total
        if metric == METRIC_LEADS:
            total = 0
            for x in data_set.filter(leads__gt=0,report_date__range=(time_period[0],time_period[1])):
                total+=x.leads
            return total
        if metric == METRIC_ORDERS:
            total = 0
            for x in data_set.filter(orders__gt=0,report_date__range=(time_period[0],time_period[1])):
                total+=x.orders
            return total
        if metric == METRIC_AMOUNT:
            return sum([(float(x.network_fee) + float(x.publisher_commission)) for x in data_set.filter(report_date__range=(time_period[0],time_period[1]))])

        return 0
          
    def current_link_count(self,link_type):
       '''Returns the number of Links of a given Type belonging to this Organiztion'''

       link_str = '_link_type_%i' % link_type
       if hasattr(self, link_str):
          return getattr(self, link_str)
       else:
          setattr(
             self,
             link_str,
             self.link_set.filter(link_type=link_type).count(),
          )
          return getattr(self, link_str)

    def current_banner(self):
       '''Returns the current number of BannerLinks for this Organization'''

       return self.current_link_count(LINKTYPE_BANNER)

    def can_add_banner(self):
       '''Returns a Boolean representing if this Organization has met or exceeded their BannerLink Quota'''

       return (self.current_link_count(LINKTYPE_BANNER) < self.allowed_banner)
    
    def current_rss(self):
       return self.current_link_count(LINKTYPE_RSS)

    def can_add_rss(self):
       return (self.current_link_count(LINKTYPE_RSS) < self.allowed_rss)
       
    def current_text(self):
       '''Returns the current number of TextLinks for this Organization'''
       return self.current_link_count(LINKTYPE_TEXT)

    def can_add_text(self):
       '''Returns a Boolean representing if this Organization has met or exceeded their TextLink Quota'''
       return (self.current_link_count(LINKTYPE_TEXT) < self.allowed_text)

    def current_keyword(self):
       '''Returns the current number of KeywordLinks for this Organization'''
       return self.current_link_count(LINKTYPE_KEYWORD)

    def can_add_keyword(self):
       '''Returns a Boolean representing if this Organization has met or exceeded their KeywordLink Quota'''
       return (self.current_link_count(LINKTYPE_KEYWORD) < self.allowed_keyword)

    def current_flash(self):
       '''Returns the current number of FlashLinks for this Organization'''
       return self.current_link_count(LINKTYPE_FLASH) + self.current_link_count(LINKTYPE_AB)

    def can_add_flash(self):
       '''Returns a Boolean representing if this Organization has met or exceeded their FlashLink Quota'''
       return ((self.current_link_count(LINKTYPE_FLASH) + self.current_link_count(LINKTYPE_AB)) < self.allowed_flash)

    def current_email_link(self):
       '''Returns the current number of EmailLinks for this Organization'''
       return self.current_link_count(LINKTYPE_EMAIL)

    def can_add_email_link(self):
       '''Returns a Boolean representing if this Organization has met or exceeded their EmailLink Quota'''
       return (self.current_link_count(LINKTYPE_EMAIL) < self.allowed_email_link)
       
    def can_add_html(self):
       '''Returns a Boolean representing if this Organization has met or exceeded their BannerLink Quota'''

       return (self.current_link_count(LINKTYPE_HTML) < self.allowed_html)
    
    def current_html(self):
       '''Returns the current number of EmailLinks for this Organization'''
       return self.current_link_count(LINKTYPE_HTML)   
       
    def current_datafeed(self):
       '''Returns the current number of DataFeeds for this Organization'''
       return self.datafeed_set.all().filter(status=STATUS_LIVE).count()
   
    def get_users(self):
       '''Returns a list of Users which belong to this Organization'''

       return User.objects.filter(userprofile__organizations=self)
 
    def get_groups(self,publisher=None):
       '''Returns a list of PublisherGroups that this Organization belongs to'''
       return [n.name for n in publisher.publishergroup_set.filter(advertiser=self)]

    def get_publisher_groups(self,advertiser=None):
       '''Returns a list of PublisherGroups which the specified Advertiser belongs to'''
       if advertiser == None:
          advertiser = Organization.objects.get(id=self.advertiser_id)
          
       return ",".join(advertiser.get_groups(self))

    def get_advertiser_relationship(self,publisher=None):
       '''Returns the PublisherRelationship which the specified Advertiser belongs to'''
        
       if publisher == None:
          publisher = Organization.objects.get(id=self.publisher_id)

       p = PublisherRelationship.objects.filter(publisher=publisher, advertiser=self)
       if p:
          return p[0]
        
       return None
       
    def get_relationship_date_accepted(self,publisher=None):
       '''Returns the Date which the PublisherRelationship was accepted. '''
        
       if publisher == None:
          publisher = Organization.objects.get(id=self.publisher_id)

       p = PublisherRelationship.objects.filter(publisher=publisher, advertiser=self)
       if p:
          if p[0].date_accepted == None:
              return p[0].date_initiated
          else:
              return p[0].date_accepted
        
       return None
        
    

    def get_network_rating(self):
       '''Returns the display value for this Organizations Network Rating'''
       if self.network_rating == "0.00":
          return "New"
       return self.network_rating

    def is_advertiser(self):
       '''Returns True of this Organization is an Advertiser'''
       if self.org_type == ORGTYPE_ADVERTISER:
          return True
       return False

    def is_publisher(self):
       '''Returns True of this Organization is an Publisher'''
       if self.org_type == ORGTYPE_PUBLISHER:
          return True
       return False

    def get_default_program_term(self):
       '''Returns the default ProgramTerm for this Organization'''

       try:
          return self.programterm_set.filter(is_default=True)[0]
       except:
          try:
             return self.programterm_set.filter()[0]
          except:
             pass

       return None

    def available_links(self):
       '''Returns the all available Links for this Organization'''
       available = Link.objects.filter(
          Q(assigned_to = LINKASSIGNED_ALL) |
          (Q(assigned_to = LINKASSIGNED_PROGRAM_TERM) & Q(assigned_to_program_term__publisherrelationship__publisher=self)) |
          (Q(assigned_to = LINKASSIGNED_GROUP) & Q(assigned_to_group__publishers=self)) |
          (Q(assigned_to = LINKASSIGNED_INDIVIDUAL) & Q(assigned_to_individual=self)) |
          (Q(assigned_to = LINKASSIGNED_MINIMUM_RATING) & Q(assigned_to_minimum_rating__lte=self.network_rating))
          ,advertiser__publisher_relationships__publisher=self, advertiser__status=ORGSTATUS_LIVE, advertiser__publisher_relationships__status=RELATIONSHIP_ACCEPTED

          )
       #if settings.HIDE_UNSYNCED_LINKS:
          #available = available.exclude(invite_id__isnull=True)

       return available
          
                             

    def send_email(self,email_type,subject,from_email,text_content,html_content,attachment=None):
       '''Helper Function for sending Email to this Organization'''
       from django.core.mail import EmailMultiAlternatives
       ## filter based on email_type
       contact = OrganizationContacts.objects.get(organization=self)
       try:
           profiles = self.userprofile_set.all()
           destinations = set([x.user.email for x in profiles if x.user.is_active==True] + [contact.email])
       except:
           destinations = [contact.email]
       
       for dest in destinations:
          try:
             msg = EmailMultiAlternatives(subject,text_content,from_email,[dest])
             msg.attach_alternative(html_content,"text/html")
             if attachment:
                msg.attach(attachment[0],attachment[1])
             msg.send()
          except:
             pass
       
    def save(self, force_insert=False, force_update=False):
       '''Overrides default model save() to set default ProgramTerm for this Organization'''
       super(Organization, self).save(force_insert, force_update)

       if self.has_program_term == True and self.programterm_set.all().count() == 0:
          self.has_program_term = False
          self.save()
       elif self.has_program_term == False and self.programterm_set.all().count() > 0:
          self.has_program_term = True
          self.save()
          
    def get_chart_vars(self,metric,time_period,group_data_by,aids=None,pids=None):
       ''' return data by day requested by the graph'''
       from django.db import connection, transaction
       temp_start_date = datetime.datetime(*time_period[0].timetuple()[:3])
       temp_end_date = datetime.datetime(*time_period[1].timetuple()[:3])
       start_time = temp_start_date + datetime.timedelta(hours=4)
       end_time = temp_end_date + datetime.timedelta(hours=4)
       time_period = (start_time,end_time)
       if group_data_by == 0:
          query_start = "SELECT DATE(date), "
          query_end = "DATE(date)"
       elif group_data_by == 1:
          query_start = "SELECT WEEK(date), "
          query_end = "WEEK(date)"
       elif group_data_by == 2:
          query_start = "SELECT MONTH(date), "
          query_end = "MONTH(date)"
       elif group_data_by == 3:
          query_start = "SELECT QUARTER(date), "
          query_end = "QUARTER(date)"
       if self.is_advertiser():
          query_relation = " advertiser_id = "+str(int(self.id))
       elif self.is_publisher():
          query_relation = " publisher_id = "+str(int(self.id))
          
       query_mid = None    
       if metric == METRIC_IMPRESSIONS:
          query_mid = "sum(impression) FROM base_impression WHERE date BETWEEN '"+time_period[0].strftime("%Y-%m-%d %H:%M:%S")+"' and '"+time_period[1].strftime("%Y-%m-%d %H:%M:%S")+"' and impression > 0 and "+str(query_relation)+" GROUP BY "
       if metric == METRIC_CLICKS:
          query_mid = "sum(click) FROM base_impression WHERE date BETWEEN '"+time_period[0].strftime("%Y-%m-%d %H:%M:%S")+"' and '"+time_period[1].strftime("%Y-%m-%d %H:%M:%S")+"' and click > 0 and "+str(query_relation)+" GROUP BY "
       if metric == METRIC_LEADS:
          query_mid = "sum(lead) FROM base_conversion WHERE date BETWEEN '"+time_period[0].strftime("%Y-%m-%d %H:%M:%S")+"' and '"+time_period[1].strftime("%Y-%m-%d %H:%M:%S")+"' and lead > 0 and "+str(query_relation)+" GROUP BY "
       if metric == METRIC_ORDERS:
          query_mid = "sum(a.order) FROM base_conversion a WHERE date BETWEEN '"+time_period[0].strftime("%Y-%m-%d %H:%M:%S")+"' and '"+time_period[1].strftime("%Y-%m-%d %H:%M:%S")+"' and a.order > 0 and "+str(query_relation)+" GROUP BY " 
       if metric == 'YESTERDAY':
          end_time = end_time + datetime.timedelta(days=1)
          time_period = (start_time,end_time)
          query_mid = "sum(lead) FROM base_conversion WHERE date BETWEEN '"+time_period[0].strftime("%Y-%m-%d %H:%M:%S")+"' and '"+time_period[1].strftime("%Y-%m-%d %H:%M:%S")+"' and lead > 0 and "+str(query_relation) 
          query_end=""	
       if metric == 5:
          query_mid = "sum(client_revenue) FROM base_conversion a WHERE date BETWEEN '"+time_period[0].strftime("%Y-%m-%d %H:%M:%S")+"' and '"+time_period[1].strftime("%Y-%m-%d %H:%M:%S")+"' and "+str(query_relation)+" GROUP BY "
       if query_mid != None:
          cursor = connection.cursor()
          query = query_start+query_mid+query_end
         
          cursor.execute(query)
          return cursor.fetchall()
       else:
          return []
          
    def get_special_terms(self):
        try:
            return ProgramTermSpecialAction.objects.filter(organization = self)
        except:
            return None
            
    def get_ticker_symbol(self):
       ''' Help Method that Returns the CDN URL for this AdvertiserImage'''
       token = "/images/user_images/"
       try:
           b = self.ticker_symbol.url.find(token)
           if b == -1:
              return self.ticker_symbol.url
    
           url = self.ticker_symbol.url[b+len(token):]
           
           return settings.CDN_HOST + url
       except:
           return ""
       
    def __unicode__(self):
       return "%s: %s" % (self.get_org_type_display(),self.name)

class OrganizationContacts(models.Model):
    '''This Model represents all Organizational Contacts (Publishers and Advertisers)'''
    
    organization = models.ForeignKey(Organization)
    
    payeename = models.CharField(max_length=255,blank=False)
    firstname = models.CharField(max_length=255,blank=False)
    lastname = models.CharField(max_length=255,blank=False)
    title = models.CharField(max_length=255,blank=True)
    email = models.EmailField(blank=False, null=False)
    phone = models.CharField(max_length=255,blank=False, null=False)
    fax = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    address2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    state = StateField(null=True, blank=True)
    province = ProvinceField(null=True, blank=True)
    country = CountryField(null=True, blank=True)
    zipcode = models.CharField(max_length=255, null=True, blank=True)
    ace_contact_id = models.IntegerField(blank=True,null=True)

class OrganizationPaymentInfo(models.Model):
    
    organization = models.ForeignKey("Organization")
    
    account_name = models.CharField('Account Holder Name', max_length=255, blank=True,null=True)
    bank_name = models.CharField(max_length=255,blank=True,null=True)
    routing_number = models.CharField(max_length=50, blank=True,null=True)
    account_number = models.CharField(max_length=50, blank=True,null=True)
    account_type = models.PositiveIntegerField(default=1, choices=((1, 'Checking'), (2, 'Savings')),blank=True,null=True)
    min_payment = models.DecimalField(max_digits=9, decimal_places=2,blank=True,null=True)
    currency = models.ForeignKey('Currency', blank=False, null=True, default=0)
    payment_method = models.PositiveIntegerField(default=PAYMENT_CHECK, choices=PAYMENT_CHOICES,null=True)
    paypal_email = models.EmailField(blank=True,null=True)
    tax_classification = models.PositiveIntegerField(default=TAXTYPE_INDIVIDUAL,choices=TAXTYPE_CHOICES,null=True,blank=True)
    tax_id = models.CharField(max_length=255,blank=True,null=True)
    vat_number = models.CharField(max_length=255,blank=True,null=True)
    iban_code = models.CharField('IBAN Code',max_length=30,blank=True,null=True)
    

class PublisherRelationship(models.Model):
    '''This model represents relationships between Publisher and Advertiser Organizations'''

    advertiser = models.ForeignKey("Organization",related_name="publisher_relationships")
    publisher = models.ForeignKey("Organization",related_name="advertiser_relationships")
    status = models.PositiveIntegerField(default=RELATIONSHIP_NONE, choices=RELATIONSHIP_CHOICES)
    
    date_initiated = models.DateTimeField(auto_now_add=True)
    date_accepted = models.DateTimeField(blank=True,null=True)
    expires = models.DateTimeField(blank=True,null=True)
    
    program_term = models.ForeignKey('ProgramTerm', null=False)

    poId = models.IntegerField(blank=True,null=True)   
    poDetailId = models.IntegerField(blank=True,null=True) 
    poSymbol = models.CharField(blank=True, max_length=20)
      
    show_history = models.IntegerField(default=1) 
    def approve(self):
       '''Method to approve the relationship between Organizations.  This method sends a notification
         e-mail which uses the publisher's Welcome Mail as the content.'''

       # send email
       self.status = RELATIONSHIP_ACCEPTED
       self.date_accepted = datetime.datetime.today().strftime("%Y-%m-%d %H:%S")
       self.save()

       if self.advertiser.publisher_welcome_mail and self.advertiser.publisher_welcome_mail_html:
          from atrinsic.util.mail import render_text,render_html
          try:
            from_email_name = self.advertiser.name
            from_email_addr = self.advertiser.pub_program_email
          except:
            from_email_name = 'Atrinsic Affiliate Network'
            from_email_addr = 'admin@network.atrinsic.com'  
          
          
          self.publisher.send_email(EMAILTYPE_ADVERTISER_MESSAGE,
                               self.advertiser.publisher_welcome_mail_subject,
                               "%s <%s>" % (self.advertiser.name,self.advertiser.pub_program_email),
                               render_text(self.advertiser.publisher_welcome_mail,self.advertiser,self.publisher),
                               render_html(self.advertiser.publisher_welcome_mail_html,self.advertiser,self.publisher))

    def decline(self):
       '''Method to decline the relationship between Organizations. This method send a notification
         e-mail which uses a stock message'''
       self.status = RELATIONSHIP_DECLINED
       self.save()

       from django.template.loader import render_to_string
       text_body = render_to_string("misc/email/decline.txt",{'advertiser':self.advertiser,
                                               'publisher':self.publisher,
                                               'contact_email':self.advertiser.pub_program_email or self.advertiser.organizationcontacts_set.all()[0].email})

       html_body = render_to_string("misc/email/decline.html",{'advertiser':self.advertiser,
                                               'publisher':self.publisher,
                                               'contact_email':self.advertiser.pub_program_email or self.advertiser.organizationcontacts_set.all()[0].email})

       self.publisher.send_email(EMAILTYPE_ADVERTISER_MESSAGE,'Application status with %s' % self.advertiser.name,
                            "%s <%s>" % (self.advertiser.name,self.advertiser.pub_program_email or self.advertiser.organizationcontacts_set.all()[0].email),text_body,html_body)
       
    def __unicode__(self):
       return "%s - %s : %s" % (self.advertiser,self.publisher,self.get_status_display())
    
class PublisherGroup(models.Model):
    '''Model representing groups of Organizations'''

    advertiser = models.ForeignKey(Organization,related_name="publisher_groups")
    name = models.CharField(max_length=255)
    publishers = models.ManyToManyField(Organization,blank=True,null=True)
  
    def add_publisher(self, p):
       '''Method that adds a Publisher Organization from this PublisherGroup'''

       if isinstance(p, int):
          try:
             p = self.publishers.get(id=p)
          except Organization.DoesNotExist:
             return False

       self.publishers.add(p)
       return True

    def remove_publisher(self, p):
       '''Method that removes a Publisher Organization from this PublisherGroup'''

       if isinstance(p, int):
          try:
             p = self.publishers.get(id=p)
          except Organization.DoesNotExist:
             return False
      
       self.publishers.remove(p)
       
       return True

    def __unicode__(self):
       return self.name
        
    
class Website(models.Model):
    '''Model for web sites which belong to Organizations'''

    publisher = models.ForeignKey(Organization)
    url = models.URLField('URL')
    desc = models.TextField('Description',blank=True,null=True)
    promo_method = models.ForeignKey('PromotionMethod',null=True,blank=True)
    vertical = models.ForeignKey('PublisherVertical',null=True,blank=True)

    is_incentive = models.BooleanField('Incentive Site', default=False)
    incentive_desc = models.CharField('Incentive Description', max_length=255, blank=True,null=True)
    
    invite_id = models.IntegerField(blank=True,null=True)    

    is_default = models.BooleanField('Default Web Site',default=False)
    
    def __unicode__(self):
       return self.url

class AdbuilderTemplates(models.Model):
    ad_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    
class DataFeed(models.Model):
    '''Model that defines an Advertiser Organizations Data Feeds'''

    status = models.PositiveIntegerField(choices=STATUS_CHOICES,default=STATUS_PENDING)
    advertiser = models.ForeignKey(Organization)
    name = models.CharField(max_length=255)
    landing_page_url = models.CharField(max_length=255)
    datafeed_type = models.PositiveIntegerField(default=DATAFEEDTYPE_NONE, choices=DATAFEEDTYPE_CHOICES)
    datafeed_format = models.PositiveIntegerField(default=DATAFEEDFORMAT_NONE, choices=DATAFEEDFORMAT_CHOICES)
    ape_url_id = models.IntegerField(blank=True,null=True)
    username = models.CharField(max_length=255, blank=True)
    password = models.CharField(max_length=255, blank=True)
    server = models.TextField(null=True,blank=True) # if datefeed_type == DATAFEEDTYPE_HTTP, server is a url

    invite_id = models.IntegerField(blank=True,null=True)

class PublisherDataFeed(models.Model): 
    '''Model that defines a Publisher Organizations Data Feeds'''

    publisher = models.ForeignKey(Organization)
    advertiser = models.ForeignKey(Organization,related_name="publisherdatafeed_advertisers")
    datafeed_type = models.PositiveIntegerField(default=DATAFEEDTYPE_NONE, choices=PUB_DATAFEEDTYPE_CHOICES)
    datafeed_format = models.PositiveIntegerField(default=DATAFEEDFORMAT_NONE, choices=PUB_DATAFEEDFORMAT_CHOICES)
    username = models.CharField(max_length=255, blank=True)
    password = models.CharField(max_length=255, blank=True)
    server = models.TextField(null=True,blank=True)
    status = models.PositiveIntegerField()

class DataTransfer(models.Model):
    ''' Model that defines a Publisher Organization's DataFeed formats, types, and status.'''

    publisher = models.ForeignKey(Organization)
    format = models.PositiveIntegerField('Transfer Format', default=DATAFEEDFORMAT_CSV, choices=PUB_DATAFEEDFORMAT_CHOICES,null=True,blank=True)
    datafeed_type = models.PositiveIntegerField(default=DATAFEEDTYPE_NONE, choices=PUB_DATAFEEDTYPE_CHOICES,null=True,blank=True)
    username = models.CharField(max_length=255, blank=True)
    password = models.CharField(max_length=255, blank=True)
    server = models.TextField(null=True,blank=True) # if datefeed_type == DATAFEEDTYPE_HTTP, server is a url
    status = models.PositiveIntegerField(choices=STATUS_CHOICES,default=STATUS_PENDING)
   
 
class AdvertiserImage(models.Model):
    ''' An Image Model for all Advertiser Images with methods for obtaining Image URLs, links, etc. '''

    advertiser = models.ForeignKey(Organization)
    image = models.ImageField(upload_to="user_images/%Y/%m/%d")
    original_filename = models.CharField(max_length=100, blank=True)
    banner_size = models.ForeignKey("BannerSize",null=True,blank=True)

    def size(self):
       ''' Returns a String representing the dimensions of this AdvertiserImage'''
       return "%sx%s" % (self.image.width,self.image.height)
       #return '1x1'
    def can_delete(self):
       ''' Returns a Boolean that specifies if this AdvertiserImage can be deleted'''
       return (self.link_set.count() == 0)

    def get_url(self):
       ''' Help Method that Returns the CDN URL for this AdvertiserImage'''

       token = "/images/user_images/"
       b = self.image.url.find(token)

       if b == -1:
          return self.image.url

       url = self.image.url[b+len(token):]
       
       return settings.CDN_HOST + url

    def get_link_id(self):
       ''' Property Method to return this AdvertiserImage's Link ID '''

       if not hasattr(self, '_link_id'):
          try:
             self._link_id = self.link_set.all()[0].link_id
          except IndexError:
             self._link_id = None

       return self._link_id

    link_id = property(get_link_id)

    def save(self, force_insert=False, force_update=False):
       ''' Overrides the default model save() method to calculate and create BannerSizes'''
       super(AdvertiserImage, self).save(force_insert, force_update)

       size = self.size()

       try:
          bs = BannerSize.objects.get(name=size)
       except BannerSize.DoesNotExist:
          bs = BannerSize.objects.get(name="Other")

       if self.banner_size != bs:
          self.banner_size = bs
          self.save()


class Link(models.Model):
    ''' Base Model specifying Advertiser Link objects (Banner, Email, Keyword, Text, or Link)'''

    advertiser = models.ForeignKey(Organization)
    name = models.CharField(max_length=100)
    start_date = models.DateField(default=datetime.datetime.now)
    end_date = models.DateField(default=datetime.datetime.now,null=True,blank=True)
    link_type = models.PositiveIntegerField(default=LINKTYPE_BANNER,choices=LINKTYPE_CHOICES)
    link_promotion_type = models.ForeignKey("LinkPromotionType",null=True,blank=True)
    link_content = models.TextField(null=True, blank=True)

    # banner ads
    banner = models.ForeignKey(AdvertiserImage, null=True, blank=True)
    banner_url = models.ImageField(upload_to="user_images/%Y/%m/%d")
    #banner_url = models.URLField(null=True,blank=True) # if the banner is self-hosted this field will be filled

    # email content
    html_content = models.TextField(null=True,blank=True)
    suppression_list = models.FileField(upload_to="suppression/%Y/%m/%d",null=True,blank=True)

    # flash link
    swf_file= models.FileField(upload_to="swf/%Y/%m/%d",null=True,blank=True)
    swf_width = models.IntegerField(blank=True,null=True)
    swf_height = models.IntegerField(blank=True,null=True)
    
    # keyword link
    protected_keyword_list = models.TextField(null=True,blank=True) # protected list
    usage_recommendations = models.TextField(null=True, blank=True)
    recommended_keywords = models.TextField(null=True, blank=True)
    noncompete_keywords = models.TextField(null=True, blank=True)
    
    assigned_to = models.PositiveIntegerField(default=LINKASSIGNED_ALL,choices=LINKASSIGNED_CHOICES)
    assigned_to_program_term = models.ForeignKey("ProgramTerm",null=True,blank=True)
    assigned_to_group = models.ForeignKey('PublisherGroup',null=True,blank=True)
    assigned_to_individual = models.ForeignKey('Organization',null=True,blank=True,related_name="private_links")
    assigned_to_minimum_rating =  models.DecimalField(max_digits=10, decimal_places=2, default='0.00',null=True,blank=True)
    assigned_to_promotion_method = models.ForeignKey("PromotionMethod",null=True,blank=True)
    assigned_to_publisher_vertical = models.ForeignKey("PublisherVertical",null=True,blank=True)

    edit_landing_page_url = models.BooleanField(default=False) # if this is set the publisher can modify where the redirect goes
    
    landing_page_url = models.CharField(blank=True,null=True,max_length=4096)
    landing_page = models.CharField(blank=True,null=True,max_length=4096)
    
    link_id = models.CharField(max_length=255, null=True, blank=True)
    invite_id = models.IntegerField(blank=True,null=True)
    invite_smartad_id = models.IntegerField(blank=True,null=True)
    invite_smartad_targeting = models.CharField(max_length=255,blank=True,null=True)
    
    #Ape ID's returned for tracking purposes
    ape_url_id = models.IntegerField(blank=True,null=True)
    ape_banner_id = models.IntegerField(blank=True,null=True)
    
    byo = models.BooleanField(default=False)
    publisher = models.ForeignKey(Organization,related_name="custom_publisher")

    def get_link_type(self):
        return LINKTYPE_CHOICES[self.link_type][1]
        
    def height(self):
        if self.banner:
            return self.banner.image.height
        return 100

    def width(self):
        if self.banner:
            return self.banner.image.width
        return 100
    
    def get_banner_url(self):
       '''Returns the URL for this BannerLink'''
       if self.banner_url:
          return self.banner_url
       if self.banner:
          return self.banner.get_url()
       return None
    
    # Property Functions
    def get_assignment(self):
       ''' Returns a String representing property function assignments for the base Link Model'''

       if self.assigned_to == LINKASSIGNED_ALL:
          return "All"
       elif self.assigned_to == LINKASSIGNED_PROGRAM_TERM:
          return "Program Term: %s" % (self.assigned_to_program_term.name, )
       elif self.assigned_to == LINKASSIGNED_INDIVIDUAL:
          return self.assigned_to_individual.name
       elif self.assigned_to == LINKASSIGNED_GROUP:
          return "Group: %s" % (self.assigned_to_group.name, )
       elif self.assigned_to == LINKASSIGNED_PROMOTION_METHOD:
          return "Promotion: %s" % (self.assigned_to_promotion_method.name, )
       elif self.assigned_to == LINKASSIGNED_PUBLISHER_VERTICAL:
          return "Vertical: %s" % (self.assigned_to_publisher_vertical.name, )
       elif self.assigned_to == LINKASSIGNED_MINIMUM_RATING:
          return "Minimum Rating: %.2f" % (self.assigned_to_minimum_rating, )
     
       return "Unknown"

    
    # Properties
    assignment = property(get_assignment)

    def track_html(self,website):
       ''' Returns the tracking HTML for this Link'''
       from django.conf import settings 
       track_click_url = settings.INVITE_CLICK_TRACKER_HOST + "track_click?igCode=%s&partnerID=%s&crID=%s&campID=%s" % (website.id,settings.INVITE_PARTNER_ID,self.invite_id,self.advertiser.invite_campid)
       if self.link_type == LINKTYPE_BANNER:
           return """<a href="%s"><img src="%s"/></a>""" % (track_click_url,self.get_banner_url())
       elif self.link_type == LINKTYPE_RSS:
           link_id = base36_encode(self.pk)
           website_id = base36_encode(website.pk)
           return  "%s/RSS/%s/%s" %(settings.SITE_URL,link_id,website_id)
       elif self.link_type == LINKTYPE_FLASH:
          flashOutput = """<object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000" codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=10,0,0,0" width="%WIDTH%" height="%HEIGHT%" align="middle"><param name="allowScriptAccess" value="sameDomain" />
<param name="allowFullScreen" value="false" /><param name="movie" value="%SWFURL%?clickTAG=%LINK%" /><param name="quality" value="high" /><param name="bgcolor" value="#ffffff" /> <embed src="%SWFURL%?clickTAG=%LINK%" quality="high" bgcolor="#ffffff" width="88" height="31" name="Insurance_88x31_Flash" align="middle" allowScriptAccess="sameDomain" allowFullScreen="false" type="application/x-shockwave-flash" pluginspage="http://www.adobe.com/go/getflashplayer" /> </object>"""
          return flashOutput.replace("%LINK%",track_click_url).replace("%SWFURL%",self.get_flash_link()).replace("%WIDTH%",str(self.swf_width)).replace("%HEIGHT%",str(self.swf_height))
          #return self.html_content.replace("%LINK%",track_click_url).replace("%SWFURL%",self.get_flash_link())
       elif self.link_type == LINKTYPE_AB:
          return ""
       else:
          return """<a href="%s">%s</a>""" % (track_click_url,self.link_content)
          
    def track_html_ape(self,website,link_only=False, layout_only=False,noImp=False):   	
        ''' Returns the tracking HTML for this Link '''
        from django.conf import settings 
        from atrinsic.util.ApeApi import Ape

        # Commission Junction Mapping:
        # A CJ_PID is assigned if the publisher does not have one mapped.
        try:
            cj_record = CJ_Mapping.objects.get(publisher=website.publisher.id)
            
            #if cj_record.verify != True:
            apeClient = Ape()
            success, ape_data = apeClient.execute_cj_get(pub_id=website.publisher_id, active=True)
            
            ##If present on the APE platform, confirm verification:
            #if ape_data['cj']['cj_id']:
            #    #cj_record.verified = True
            #    #cj_record.save()
            ##Else, create it:
            #else:
            #    apeClient = Ape()
            #    success, ape_data = apeClient.execute_cj_create(pub_id=cj_record.publisher_id,cj_pid=cj_record.cj_pid)                
        except Exception, e:
            print e.message
            try:
                #Assign AAN - CJ Mapping:
                cj_record = CJ_Mapping.objects.filter(publisher=None,date_assigned=None)[0]
                cj_record.publisher_id = website.publisher.id
                cj_record.date_assigned = datetime.datetime.now()
                cj_record.save()
                # Sync CJ Mapping - APE:
                apeClient = Ape()
                success, ape_data = apeClient.execute_cj_create(pub_id=cj_record.publisher_id,cj_pid=cj_record.cj_pid)
            except Exception, e:
                from django.core.mail import EmailMultiAlternatives
                EMAIL_SUBJECT = "AAN ERROR - Get Link Missing Commission Junction ID"
                EMAIL_MSG = "An Error has occured. No Commission Junction IDs could be assigned to a Publisher requesting a link. More Commission Junction IDs required"
                EMAIL_FROM = "cj_id_list@atrinsic.com"
                EMAIL_TO = ["matthew.sartain@atrinsic.com","luc.chevarie@atrinsic.com","philippe.hache@atrinsic.com"]
                #,"samantha.morris@atrinsic.com"
        
                msg = EmailMultiAlternatives(EMAIL_SUBJECT, EMAIL_MSG, EMAIL_FROM, EMAIL_TO)
                msg.send()
            

        # This is for links that are embedded in the Welcome email. 

        if layout_only:
            if self.link_type == LINKTYPE_BANNER:            
                return """<img src="%s" border="0"/>""" % self.banner_url
            else:
                return """<a href="">%s</a>""" % self.link_content
        relationship = PublisherRelationship.objects.get(advertiser=self.advertiser,publisher=website.publisher)
        # below relationship = PublisherRelationship.objects.get(advertiser=self.advertiser,publisher=website.publisher)
        ptAction = ProgramTermAction.objects.select_related("action").filter(program_term=relationship.program_term_id)

        if (self.ape_url_id == None or self.ape_url_id == 0) or (self.ape_banner_id == None or self.ape_banner_id == 0):        
            apeClient = Ape()            
            for pta in ptAction:
                apeClient.execute_url_create(pta.action, self)   

        
        for pta in ptAction:
            try:
                PublisherTracking.objects.get_or_create(
                    link = self
                    , advertiser = self.advertiser
                    , publisher = website.publisher
                    , program_term = relationship.program_term
                    , website = website
                    , ape_redirect_id = pta.action.ape_redirect_id
                    , ape_url_id = self.ape_url_id)
            except:
                """Crashes when theirs a dupe data"""
        websiteID = base36_encode(website.pk)
        ape_redirect = base36_encode(ptAction[0].action.ape_redirect_id)
        publisherID = base36_encode(website.publisher_id)
        ape_url = self.ape_url_id
        if(ape_url == None):
            ape_url = ""
        if(ape_redirect == None):
            ape_redirect = ""
        # and above strBannerID = base36_encode(self.ape_banner_id)
        strBannerID = base36_encode(self.ape_banner_id)
        
        
        track_imp_url = """<img src="%s%s/%s.jpg?subid=2&websiteid=%s" border=0 width=1 height=1>""" % (settings.APE_IMPRESSION_TRACKING,str(publisherID),str(strBannerID),str(website.pk) )
        track_click_url = settings.APE_TRACKER_URL + ape_redirect + "/" + str(publisherID) + "/" + str(websiteID) + "/?url_id=" + str(ape_url)
        
        
        integration = KenshooIntegration.objects.filter(
            advertiser=self.advertiser
            , publisher=website.publisher
            , pixel_type = PIXEL_TYPE_IMAGE
        )
        
        if (integration):
            track_click_url = track_click_url + "&kid=" + str(integration[0].content)
        
        
        if link_only:
            return track_click_url
        if self.link_type == LINKTYPE_BANNER:
            #track_click_url = settings.APE_TRACKER_URL + ape_redirect + "/" + str(publisherID) + "/" + str(websiteID) + "/"    
            track_impression = "http://imps.acetrk.com/i/" + str(publisherID) + "/" + str(strBannerID) + ".jpg?subid=2&websiteid=" +  str(website.pk)
            return """<a href="%s"><img src="%s" border="0"/></a>""" % (track_click_url,track_impression)
        elif self.link_type == LINKTYPE_RSS:
           link_id = base36_encode(self.pk)
           website_id = base36_encode(website.pk)
           return  "%s/RSS/%s/%s" %(settings.SITE_URL,link_id,website_id)
        elif self.link_type == LINKTYPE_FLASH:
            flashOutput = """%TRACKIMP%<object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000" codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=10,0,0,0" width="%WIDTH%" height="%HEIGHT%" align="middle"><param name="allowScriptAccess" value="sameDomain" />
<param name="allowFullScreen" value="false" /><param name="movie" value="%SWFURL%?clickTAG=%LINK%" /><param name="quality" value="high" /><param name="bgcolor" value="#ffffff" /> <embed src="%SWFURL%?clickTAG=%LINK%" quality="high" bgcolor="#ffffff" width="%WIDTH%" height="%HEIGHT%" align="middle" allowScriptAccess="sameDomain" allowFullScreen="false" type="application/x-shockwave-flash" pluginspage="http://www.adobe.com/go/getflashplayer" /> </object>"""
            print '** phil last one of thse is a bad link: link > self.id %s', self.id
            flashOutput = flashOutput.replace("%LINK%",track_click_url).replace("%SWFURL%",self.get_flash_link())
            if self.swf_width == None:
                self.swf_width = 0
            if self.swf_height == None:
                self.swf_height = 0
            flashOutput = flashOutput.replace("%WIDTH%",str(self.swf_width)).replace("%HEIGHT%",str(self.swf_height))
            flashOutput = flashOutput.replace("%TRACKIMP%", str(track_imp_url))
            return flashOutput
            #return flashOutput.replace("%LINK%",track_click_url).replace("%SWFURL%",self.get_flash_link()).replace("%WIDTH%",self.swf_width).replace("%HEIGHT%",self.swf_height)
        elif self.link_type == LINKTYPE_AB:
            flashOutput = """%TRACKIMP%<object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000" codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=10,0,0,0" width="%WIDTH%" height="%HEIGHT%" align="middle"><param name="allowScriptAccess" value="sameDomain" /><param name="allowFullScreen" value="false" /><param name="movie" value="%SWFURL%?clickTAG=%LINK%" /><param name="quality" value="high" /><param name="bgcolor" value="#ffffff" /> <embed src="%SWFURL%?clickTAG=%LINK%" quality="high" bgcolor="#ffffff" width="%WIDTH%" height="%HEIGHT%" align="middle" allowScriptAccess="sameDomain" allowFullScreen="false" type="application/x-shockwave-flash" pluginspage="http://www.adobe.com/go/getflashplayer" /> </object>"""
            flashOutput = flashOutput.replace("%LINK%",track_click_url).replace("%SWFURL%",self.swf_file.url)
            return flashOutput   
        elif self.link_type == LINKTYPE_HTML:
            strBannerReturn = self.link_content
            strBannerLink = track_click_url
            import urllib
            strBannerReturn = strBannerReturn.replace('[url_id]', str(self.ape_url_id))
            strBannerReturn = strBannerReturn.replace('[publisherwebsiteid]', str(websiteID))
            strBannerReturn = strBannerReturn.replace('[publisherid]', str(publisherID))
            strBannerReturn = strBannerReturn.replace('[clicktag]', urllib.urlencode({'x':strBannerLink})[2:])
            if noImp:
                return strBannerReturn
            strBannerReturn = track_imp_url + strBannerReturn
            return strBannerReturn
        else:
            return """%s<a href="%s">%s</a>""" % (track_imp_url,track_click_url,self.link_content)

    def track_text(self,website):
       from django.conf import settings 
       # XXX: track_click_url = settings.INVITE_CLICK_TRACKER_HOST + "track_click?igCode=IG-%s&partnerID=%s&crID=%s&campID=%s" % (website.id,settings.INVITE_PARTNER_ID,self.invite_id,self.advertiser.invite_campid)
       track_click_url = settings.INVITE_CLICK_TRACKER_HOST + "track_click?igCode=%s&partnerID=%s&crID=%s&campID=%s" % (website.id,settings.INVITE_PARTNER_ID,self.invite_id,self.advertiser.invite_campid)

       return """%s""" % (track_click_url)

    # Methods
    def save(self, force_insert=False, force_update=False):
       ''' Overrides the default Model save() method to calculate an MD5 checksum of this link for the Link ID '''
       super(Link, self).save(force_insert, force_update)

       if self.link_id is None:
          m = md5.new()
          m.update(str(self.id))
          self.link_id = m.hexdigest()
          self.save()

    def get_flash_link(self):
       a_token = "/user_images/swf/"
       a = self.swf_file.url.find(a_token)
       b_token = "/images/swf/"
       b = self.swf_file.url.find(b_token)
       
       
       url = self.swf_file.url
       if a != -1:
           url = url.replace("/user_images/swf","/swf")

       if b != -1:
           url = url.replace("/images/swf","/swf")
       return url
    
class OrderManager(models.Manager):
    ''' Model Manager to return a default QuerySet ordering results by their "name" '''

    def get_query_set(self):
       ''' Returns a QuerySet for this Model ordering results by "name" '''
       return super(OrderManager, self).get_query_set().order_by("name")
      
 
class BannerSize(models.Model):
    ''' Model representing the size of an AdvertiserImage for a BannerLink '''
    order = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    
    objects = OrderManager()
    
    def __unicode__(self):
       return self.name


class PromotionMethod(models.Model):
    ''' Model that specifies the default Promotion Method '''
    order = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    
    objects = OrderManager()

    def __unicode__(self):
       return self.name

       
class LinkPromotionType(models.Model):
    ''' Model specifying the type of promotion this Link represents '''
    order = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    
    objects = OrderManager()

    def __unicode__(self):
       return self.name

       
class PublisherVertical(models.Model):
    ''' Model containing categories for Organization's Business Vertical/Category '''
    order = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    icon = models.CharField(max_length=255)
    description = models.CharField(max_length=512)
    showicon = models.SmallIntegerField()
    is_adult = models.BooleanField(default=False)
    objects = OrderManager()

    def __unicode__(self):
       return self.name

class MsgStatus(models.Model):
    ''' Model to handle private messaging between Organizations '''
    name = models.CharField(max_length=255)
    
    def __unicode__(self):
       return "statusName : %s" % (self.name)  

class PrivateMessage(models.Model):
    ''' Model to handle private messaging between Organizations '''

    class Meta:
       ordering = ('-date_sent',)

    is_active = models.BooleanField(default=False)
    del_trash = models.BooleanField(default=False)
    folder = models.CharField(max_length=255)
    date_sent = models.DateTimeField(default=datetime.datetime.now)
    sender = models.ForeignKey(Organization,related_name="sent_messages")
    receiver = models.ForeignKey(Organization,related_name="received_messages")
    read = models.BooleanField(default=False)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    sender_status = models.ForeignKey(MsgStatus,related_name="sender_status")
    receiver_status = models.ForeignKey(MsgStatus,related_name="receiver_status")

    def __unicode__(self):
       return "%s to %s : %s" % (self.sender,self.receiver,self.subject)         

class ExchangeRate(models.Model):
    created = models.DateField(auto_now_add=True)

    from_currency = models.ForeignKey('Currency', related_name='exchangerate_from')
    to_currency = models.ForeignKey('Currency', related_name='exchangerate_to')

    rate = models.DecimalField(max_digits=10, decimal_places=6, default='1.00')

    def __unicode__(self):
        return "%s -> %s @ %s" % (self.from_currency.name, self.to_currency.name, self.rate, )


# use babeldjango
class Currency(models.Model):
    order = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    rate = models.DecimalField(max_digits=10, decimal_places=6, default='1.00')
    
    objects = OrderManager()

    def convert_to(self, c):
       r = ExchangeRate.objects.filter(from_currency=self, to_currency=Currency.objects.get(name=c)).order_by('-created')

       if r:
          return float(r[0].rate)

       return 1.0

    def convert(self, val, c='USD'):
       if val == None:
           val = 0.0	
       return float(float(str(val)) * self.convert_to(c))
       
    def convert_v2(self, val,c,e):
       if val == None:
           val = 0.0	
       return float(float(str(val)) * self.convert_to(c))   
       
    def get_exchange_rate(self,org_currency_type):
        r = ExchangeRate.objects.filter(from_currency=self, to_currency=org_currency_type).order_by('-created')

        if len(r) > 0:
            return float(r[0].rate)
        
        return 1.0
        
    def convert_display(self, val, c='USD'):
        if self.name == 'GBP':
            return mark_safe(u"&pound; %.2f" % self.convert(val))
        elif self.name == 'EUR':
            return mark_safe(u"&#8364; %.2f" % self.convert(val))
        elif self.name == 'CDN':
            return mark_safe(u"C$ %.2f" % self.convert(val))
        elif self.name == 'USD':
            return mark_safe(u"$%.2f" % self.convert(val))
        else:
            return mark_safe(u"%.2f (%s)" % self.convert(val), self.name)
        
    def convert_display_v2(self,val,exchange_rage,currency):
        if str(currency) == 'GBP':
            return mark_safe(u"&pound; %.2f" % (float(str(val)) * exchange_rage))
        elif str(currency) == 'EUR':
            return mark_safe(u"&#8364; %.2f" % (float(str(val)) * exchange_rage))
        elif str(currency) == 'CDN':
            return mark_safe(u"C$ %.2f" % (float(str(val)) * exchange_rage))
        elif str(currency) == 'USD':
            return mark_safe(u"$%.2f" % (float(str(val)) * exchange_rage))
        else:
            return mark_safe(u"%.2f (%s)" % (float(str(val)) * exchange_rage))
    def in_usd(self):
       return self.convert_to('USD')
       

    def __unicode__(self):
       return self.name

    


class ProgramTerm(models.Model):
    ''' Model that specifies an Advetiser's terms for their programs '''

    advertiser = models.ForeignKey(Organization)
    name = models.CharField(max_length=255)
    date_created = models.DateTimeField(default=datetime.datetime.now)
    is_default = models.BooleanField(default=False) # only 1 default amongst all a advertiser's program terms
    is_archived = models.BooleanField(default=False)

    cpm = models.DecimalField(max_digits=10, decimal_places=2, default='0.00')
    cpc = models.DecimalField(max_digits=10, decimal_places=2, default='0.00') 
    
    ace_iodetailid = models.IntegerField(blank=True,null=True)

    
    def number_enrolled(self):
       ''' Returns the number of enrolled Organizations in this Program '''

       return Organization.objects.filter(advertiser_relationships__status=RELATIONSHIP_ACCEPTED,
                                   advertiser_relationships__advertiser=self.advertiser,
                                   advertiser_relationships__program_term=self,
                                   status=ORGSTATUS_LIVE).count()
    def number_program_term_actions(self):
       ''' Returns the number of enrolled Organizations in this Program '''

       return ProgramTermAction.objects.filter(program_term = self).count()

    def is_fixed_action(self):
       ''' Returns Boolean representing if this ProgramTerm contains a Fixed ProgramTermAction'''

       pta = self.programtermaction_set.all()

       if pta and pta[0]:
          if pta[0].is_fixed_commission:
             return True

       return False

       
    def display_term(self):
       ''' Returns a String for displaying this Program Term'''

       pta = self.programtermaction_set.all()

       if pta and pta[0]:
          if pta[0].is_fixed_commission:
             return "$%s" % pta[0].commission
          else:
             return "%s%%" % pta[0].commission

       return ""
    
    def __unicode__(self):
        return ""
        return "%s %s" % (self.advertiser,self.name)

    def save(self, force_insert=False, force_update=False):
       super(ProgramTerm, self).save(force_insert, force_update)
       self.advertiser.save()

class ProgramTermSpecialAction(models.Model):
    organization = models.ForeignKey(Organization)
    special_action = models.TextField(blank=True, null=True)
    
class ProgramTermAction(models.Model):
    ''' Association of Actions and Advertiser Program Terms'''

    program_term = models.ForeignKey('ProgramTerm',blank=True,null=True)
    action = models.ForeignKey('Action',blank=True,null=True) # each program term can only contain an action once

    is_custom_action_lifecycle = models.BooleanField(default=False) # locks on the 10th of the month if not custom
    
    custom_action_lifecycle = models.PositiveIntegerField(default=7,null=True,blank=True) # actions lock this many days after the event happens if is_custom_action_lifecycle = True
    
    is_fixed_commission = models.BooleanField(default=True) # if false, commission is a % of total sale
    commission = models.DecimalField(max_digits=10, decimal_places=2, default='0.00') # either a percent or a cash amount (refer to advertiser's currency for what this is represented in)
    action_referral_period = models.PositiveIntegerField(default=45) # how many days the "cookie" lasts for
    
    def __unicode__(self):
       return "%s : %s" % (self.program_term,self.action)


    
class ProgramTerm_Historical_Data(models.Model):
    ''' Association of Actions and Advertiser Program Terms'''
    advertiser = models.ForeignKey("Organization",related_name="advertiser_history")
    publisher = models.ForeignKey("Organization",related_name="publisher_history")
    program_term = models.ForeignKey('ProgramTerm',blank=False,null=False)    
    effective_date = models.DateField()
    end_date = models.DateField()
    create_date = models.DateTimeField(auto_now_add=True)

       
class CommissionTier(models.Model):
    ''' Model of commission tier payouts for a ProgramTerm's Actions '''

    program_term_action = models.ForeignKey('ProgramTermAction')
    incentive_type = models.PositiveIntegerField(choices=INCENTIVETYPE_CHOICES,default=INCENTIVETYPE_TOTALSALES)
    threshold = models.DecimalField(max_digits=10, decimal_places=2, default='0.00')
    new_commission = models.DecimalField(max_digits=10, decimal_places=2, default='0.00')
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default='0.00')

    def get_new_commission_display(self):
       if self.program_term_action.is_fixed_commission:
          return "$%s" % self.new_commission
       else:
          return "%s%%" % self.new_commission

    def get_threshold_display(self):
       if self.incentive_type in [INCENTIVETYPE_TOTALSALES,INCENTIVETYPE_TOTALCOMMISSIONS]:
          return "$%s" % self.threshold
       else:
          return int(round(self.threshold))

    def __unicode__(self):
       return "%s : %s > %s" % (self.program_term_action,self.get_incentive_type_display(),self.threshold)
    

class Action(models.Model):
    ''' Model specifying items to be performed for this Advertiser Organization '''

    name = models.CharField(max_length=255)
    advertiser = models.ForeignKey(Organization)
    status = models.PositiveIntegerField(choices=STATUS_CHOICES,default=STATUS_TEST)
    
    network_fee = models.DecimalField(max_digits=10, decimal_places=2, default='0.00') # revshare, multiplied against the order size
    network_flat_fee = models.DecimalField(max_digits=10, decimal_places=2, default='0.00') # fixed amount
    
    network_action_payout = models.DecimalField(max_digits=10,decimal_places=2,default='0.00') # how much atrinsic gets paid for each action, only for cpa programs
      
    tracking_id = models.CharField(max_length=255,blank=True,null=True)

    secure_url = models.CharField(max_length=255,null=True,blank=True)
    unsecure_url = models.CharField(max_length=255,null=True,blank=True)

    invite_id = models.IntegerField(blank=True,null=True)
    invite_client_goal_id = models.IntegerField(blank=True,null=True)

    advertiser_payout_type = models.PositiveIntegerField(choices=ADVERTISER_PAYOUT_TYPE_CHOICES,default=ADVERTISER_PAYOUT_TYPE_REVSHARE)
    advertiser_payout_amount = models.DecimalField(max_digits=10,decimal_places=2,default='0.00')  

    ape_redirect_id = models.IntegerField(blank=True,null=True)
    ape_action_id = models.IntegerField(blank=True,null=True)
    def __unicode__(self):
       return "%s %s" % (self.advertiser,self.name)
    

class Alert(models.Model):
    ''' Model to specify Alerts which are configured for Publishers and Advertisers'''

    organization = models.ForeignKey('Organization')
    time_period = models.PositiveIntegerField(choices=ALERTTIMEPERIOD_CHOICES,default=ALERTTIMEPERIOD_DAY)
    alert_field = models.PositiveIntegerField(choices=METRIC_CHOICES,default=METRIC_IMPRESSIONS)
    change = models.DecimalField(max_digits=10, decimal_places=2, default='0.00')
    date = models.DateField(default=datetime.datetime.today)
    def __unicode__(self):
       if self.change > 0:
          change_str = "increases at least %s%%" % self.change
       else:
          change_str = "decreases over %s%%" % (-self.change)
          
       return "Notify when %s %s over the last %s." % (self.get_alert_field_display().lower(),change_str,self.get_time_period_display().lower())

    def check_alert(self):
       ''' Maintenance Function to determine metric values for Alerts'''

       import datetime
       now = datetime.datetime.now()
       if self.time_period == ALERTTIMEPERIOD_DAY:
          # compare time period is 48 hours to 24 hours ago
          # current time period is 24 hours ago to now
          compare_window = (now-datetime.timedelta(2,0,0),now-datetime.timedelta(1,0,0))
          current_window = (now-datetime.timedelta(1,0,0),now)
       elif self.time_period == ALERTTIMEPERIOD_WEEK:
          compare_window = (now-datetime.timedelta(14,0,0),now-datetime.timedelta(7,0,0))
          current_window = (now-datetime.timedelta(7,0,0),now)
       elif self.time_period == ALERTTIMEPERIOD_MONTH:
          compare_window = (now-datetime.timedelta(60,0,0),now-datetime.timedelta(30,0,0))
          current_window = (now-datetime.timedelta(30,0,0),now)
       elif self.time_period == ALERTTIMEPERIOD_QUARTER:
          compare_window = (now-datetime.timedelta(180,0,0),now-datetime.timedelta(90,0,0))
          current_window = (now-datetime.timedelta(90,0,0),now)
       elif self.time_period == ALERTTIMEPERIOD_COMPARABLE_MONTH:
          compare_window = (now-datetime.timedelta(365+30,0,0),now-datetime.timedelta(365,0,0))
          current_window = (now-datetime.timedelta(30,0,0),now)
       elif self.time_period == ALERTTIMEPERIOD_COMPARABLE_QUARTER:
          compare_window = (now-datetime.timedelta(365+90,0,0),now-datetime.timedelta(365,0,0))
          current_window = (now-datetime.timedelta(90,0,0),now)

       compare = self.organization.get_metric(self.alert_field,compare_window)
       current = self.organization.get_metric(self.alert_field,current_window)

       if compare == 0:
          return 0.0

       return 100*((float(current) / float(compare)) - 1.0)
       
       

class AutoDeclineCriteria(models.Model):
    ''' This is a bit more complicated than the other models,

    Advertiser autorejects all publishers that apply that have <FIELD> (one of a list defined in choices.py)"
        equal to <VALUE>
    '''
    
    advertiser = models.ForeignKey('Organization')
    field = models.PositiveIntegerField(choices=AUTODECLINEFIELD_CHOICES,default=AUTODECLINEFIELD_COUNTRY)
    value = models.TextField(null=True,blank=True)
    promotion_method = models.ForeignKey('PromotionMethod',null=True,blank=True) # if field == AUTODECLINEFIELD_PROMOTION_METHOD use this field instead of value
    publisher_vertical = models.ForeignKey('PublisherVertical',null=True,blank=True) # if field == AUTODECLINEFIELD_PUBLISHER_VERTICAL use this field instead of value

    def get_display_value(self):
       ''' Returns a String that represents this Criteria '''

       if self.field == AUTODECLINEFIELD_PROMOTION_METHOD:
          return self.promotion_method.name
       if self.field == AUTODECLINEFIELD_PUBLISHER_VERTICAL:
          return self.publisher_vertical.name

       return self.value

    def test_publisher(self,publisher):
       ''' Retunrs a Boolean representing if this Publisher should be accepted or rejected '''

       if self.field == AUTODECLINEFIELD_COUNTRY and publisher.country != None and publisher.country.lower() == self.value.lower():
          return False
       elif self.field == AUTODECLINEFIELD_STATE and publisher.state != None and publisher.state.lower() == self.value.lower():
          return False
       elif self.field == AUTODECLINEFIELD_PUBLISHER_ID and str(publisher.id) == self.value:
          return False
       elif self.field == AUTODECLINEFIELD_PROMOTION_METHOD and publisher.promotion_method == self.promotion_method:
          return False
       elif self.field == AUTODECLINEFIELD_WEBSITE and Website.objects.filter(publisher=publisher,url__iequal=self.value).count() > 0:
          return False
       elif self.field == AUTODECLINEFIELD_PUBLISHER_VERTICAL and publisher.vertical == self.publisher_vertical:
          return False

       return True
          
    
    def __unicode__(self):
       return "%s %s = %s" % (self.advertiser,self.get_field_display(),self.get_display_value())

       
class EmailCampaign(models.Model):
    ''' Model containing an Advertiser's Email Campaign '''

    is_active = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)

    date_send = models.DateField(default=datetime.date.today) # send an email campaign in the future
    
    date_created = models.DateField(default=datetime.date.today)
    advertiser = models.ForeignKey('Organization')
    name = models.CharField(max_length=255)

    program_term = models.ManyToManyField("ProgramTerm",null=True,blank=True)
    publisher_group = models.ManyToManyField('PublisherGroup',null=True,blank=True)
    promotion_method = models.ManyToManyField(PromotionMethod,null=True,blank=True)
    publisher_vertical = models.ManyToManyField("PublisherVertical",null=True,blank=True)

    subject = models.CharField(max_length=255)
    body = models.TextField(null=True,blank=True)
    html_body = models.TextField(null=True,blank=True)

    email_from = models.CharField(max_length=255)
    reply_to_address = models.CharField(max_length=255)    
    

class EmailCampaignCriteria(models.Model):
    ''' Model to specify criteria that is to be met for this Email Campaign

       if <field_is_less_than_threshold> is true:
          will match publishers that during time period <TIME_PERIOD> have <ALERT_FIELD> less than <THRESHOLD>
       else
          will match publishers that during time period <TIME_PERIOD> have <ALERT_FILE> greater than or equal <THRESHOLD>
    '''
    
    email_campaign = models.ForeignKey('EmailCampaign')
    time_period = models.PositiveIntegerField(choices=CAMPAIGNCRITERIAPERIOD_CHOICES,default=CAMPAIGNCRITERIAPERIOD_YESTERDAY)
    alert_field = models.PositiveIntegerField(choices=METRIC_CHOICES,default=METRIC_IMPRESSIONS)

    field_is_less_than_threshold = models.BooleanField(default=False)
    threshold = models.DecimalField(max_digits=10, decimal_places=2, default='0.00')

    def check_publisher(self,publisher):
       import datetime
       current_window = compute_date_range(self.time_period)
       current = publisher.get_metric(self.alert_field,current_window)
       if field_is_less_than_threshold:
          return current < threshold
       return current > threshold
    


class Impression(models.Model):
    ''' Model to specify and track Link Impressions '''
    
    date = models.DateTimeField()
    gmt_date = models.DateTimeField()
    ip = models.CharField(max_length=255)
    invite_auction_id = models.CharField(max_length=255)
    invite_user_id = models.CharField(max_length=255)
    
    advertiser = models.ForeignKey('Organization',related_name="advertiser_impressions")
    publisher = models.ForeignKey('Organization',related_name="publisher_impressions")
    link = models.ForeignKey('Link')
    site = models.ForeignKey('Website')
    sub_id = models.CharField(max_length=1024)
    impression = models.IntegerField()
    click = models.IntegerField()
    
    amount = models.DecimalField(max_digits=10, decimal_places=10, default='0.00')  # for cpm or cpc

class Conversion(models.Model):
    ''' Model that represents an Advertiser or Publisher Organizations Link Conversions'''

    date = models.DateTimeField()
    gmt_date = models.DateTimeField()
    ip = models.CharField(max_length=255)
    invite_auction_id = models.CharField(max_length=255)
    invite_user_id = models.CharField(max_length=255)
    invite_conversion_id = models.CharField(max_length=255)

    advertiser = models.ForeignKey('Organization',related_name="advertiser_conversions")
    publisher = models.ForeignKey('Organization',related_name="publisher_conversions")

    lead = models.IntegerField()
    order = models.IntegerField() # lead or order is determined by the action
    
    link = models.ForeignKey('Link')
    site = models.ForeignKey('Website')
    sub_id = models.CharField(max_length=1024)
    order_id = models.CharField(max_length=1024)
 
    conversion_days = models.IntegerField(blank=True,null=True)

    client_revenue = models.DecimalField(max_digits=10,decimal_places=2,default='0.00') # column 32 of conversion log


    # old fees
    #publisher_commission = models.DecimalField(max_digits=10,decimal_places=2,default='0.00')
    #network_fee = models.DecimalField(max_digits=10,decimal_places=2,default='0.00')

    # new fees
    advertiser_payout = models.DecimalField(max_digits=10,decimal_places=2,default='0.00') # new fee
    transaction_fee = models.DecimalField(max_digits=10,decimal_places=2,default='0.00') # was known as network_fee
    publisher_payout = models.DecimalField(max_digits=10,decimal_places=2,default='0.00') # was known as publisher_commission


    total_fee = models.DecimalField(max_digits=10,decimal_places=2,default='0.00')

    skus = models.CharField(max_length=4096,blank=True,null=True) # comma separated list of skus

class SmartAd(models.Model):
    ''' A SmartAd Link '''

    publisher = models.ForeignKey(Organization)
    name = models.CharField(max_length=1024)
    smartad_type = models.PositiveIntegerField(choices=SMARTADTYPE_CHOICES,default=SMARTADTYPE_PRODUCT)
    is_auto_optimizing = models.BooleanField(default=True)
    vertical = models.ManyToManyField('PublisherVertical',null=True,blank=True)
    website = models.ForeignKey(Website,null=True,blank=True)

    advertisers = models.ManyToManyField(Organization,related_name="smartad_publishers")

    banner_size = models.ForeignKey("BannerSize",null=True,blank=True)
    invite_unit_id = models.IntegerField(blank=True,null=True)
    invite_invsize_id = models.IntegerField(blank=True,null=True)
    invite_publineitem_id = models.IntegerField(blank=True,null=True)

    def height(self):
        width,height = self.banner_size.name.split("x")
        return height
    

    def width(self):
        width,height = self.banner_size.name.split("x")
        return width
    
    def advertiser_links(self):
        return self.publisher.available_links().filter(advertiser__in=[adv.id for adv in self.advertisers.all()])
        
    def advertiser_choices(self):
       ''' Returns a QuerySet representing the list of Publishers this SmartAd is directed towards '''

       qs = Organization.objects.filter(org_type=ORGTYPE_ADVERTISER,
                                 publisher_relationships__status=RELATIONSHIP_ACCEPTED,
                                 publisher_relationships__publisher=self.publisher)

       if self.vertical.all().count() > 0:
          qs = qs.filter(vertical__in=[v for v in self.vertical.all()])

       b = list(qs)
       for c in b:
          if c in self.advertisers.all():
             c.checked = True

       return b

    def code(self):
       if self.invite_invsize_id == None:
          return "Generating code, please try again in a few minutes"
       return """<iframe FRAMEBORDER=0 MARGINWIDTH=0 MARGINHEIGHT=0 SCROLLING=NO WIDTH=%s HEIGHT=%s src="http://optimizedby.invitemedia.com/bidding?interface=web&ad_type=iframe&isize=%s&width=%s&height=%s" > </iframe> """ % (self.width(),self.height(),self.invite_invsize_id,self.width(),self.height())

    

class PublisherInquiry(models.Model):
    ''' Model representing a Publisher's inquiry to an Advertiser '''

    publisher = models.ForeignKey(Organization)
    advertiser = models.ForeignKey(Organization,related_name="paymentinquiry_advertiser_set")

    is_transaction_inquiry = models.BooleanField(default=False) # if true, it's a transaction inquiry, if false, it's a payment inquiry
    
    date_created = models.DateTimeField(default=datetime.datetime.now)
    date_resolved = models.DateTimeField(null=True,blank=True)
    amount_due = models.DecimalField(max_digits=10,decimal_places=2,default='0.00')

    period_beginning = models.DateField(default=datetime.datetime.now,blank=True,null=True)
    period_ending = models.DateField(default=datetime.datetime.now,blank=True,null=True)
    comments = models.TextField(null=True,blank=True)
    response = models.TextField(null=True,blank=True)

    status = models.PositiveIntegerField(choices=INQUIRYSTATUS_CHOICES,default=INQUIRYSTATUS_UNRESOLVED)
    order_id = models.CharField(max_length=255,null=True,blank=True)
    transaction_amount = models.DecimalField(max_digits=10,decimal_places=2,default='0.00')
    member_id = models.CharField(max_length=255,null=True,blank=True)
    transaction_date = models.DateField(null=True,blank=True)
    advertiser_reason = models.CharField(blank=True, null=True, max_length=100)
    advertiser_reason_comment = models.CharField(blank=True,null=True, max_length=500)
    advNew = models.BooleanField(default=False)
    pubNew = models.BooleanField(default=False)
    #is_partial_order = models.BooleanField(default=False)

class InquiryMessage(models.Model):
    
    inquiry = models.ForeignKey(PublisherInquiry)
    sentby_publisher = models.BooleanField(default=True)
    msg = models.TextField(null=True,blank=True)

class ProcessedLog(models.Model):
    ''' Model that tracks the downloading and processing of Log Files'''

    name = models.CharField(max_length=255)
    log_type = models.CharField(max_length=255)

    claimed = models.BooleanField(default=True)
    state = models.PositiveIntegerField(choices=LOGSTATE_CHOICES,default=LOGSTATE_NEEDS_GRAB)

class AdvertiserApplication(models.Model):
    ''' Model to handle the signup application for an Advertiser Organization '''

    contact_firstname = models.CharField(max_length=255,blank=True)
    contact_lastname = models.CharField(max_length=255,blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=255)
    contact_fax = models.CharField(max_length=255)
    contact_title = models.CharField(max_length=255)

    organization_name = models.CharField(max_length=255,null=True,blank=True)
    website_url = models.CharField(max_length=4096,null=True,blank=True)
    
    address = models.CharField(max_length=255, null=True, blank=True)
    address2 = models.CharField(max_length=255, null=True, blank=True)

    city = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    
    zipcode = models.CharField(max_length=255, null=True, blank=True)
    country = CountryField(null=True, blank=True)
    
    tax_classification = models.PositiveIntegerField(default=TAXTYPE_INDIVIDUAL,choices=TAXTYPE_CHOICES)
    tax_id = models.CharField(max_length=255,blank=True,null=True)

    date_site_launched = models.DateField(blank=True)
    products_on_site = models.PositiveIntegerField(blank=True,null=True)

    technical_team_type = models.PositiveIntegerField(default=TEAM_INHOUSE,choices=TEAM_CHOICES)
    creative_team_type = models.PositiveIntegerField(default=TEAM_INHOUSE,choices=TEAM_CHOICES)

    has_existing_affiliate_program = models.BooleanField(default=False)

    participates_in_ppc = models.BooleanField(default=False)
    ppc_working_with_agency = models.PositiveIntegerField(default=AGENCY_INHOUSE,choices=AGENCY_CHOICES)
    ppc_contact_desired = models.BooleanField(default=False)

    participates_in_seo = models.BooleanField(default=False)
    seo_working_with_agency = models.PositiveIntegerField(default=AGENCY_INHOUSE,choices=AGENCY_CHOICES)
    seo_contact_desired = models.BooleanField(default=False)

    participates_in_email = models.BooleanField(default=False)
    email_working_with_agency = models.PositiveIntegerField(default=AGENCY_INHOUSE,choices=AGENCY_CHOICES)
    email_contact_desired = models.BooleanField(default=False)


class AqWidget(models.Model):
    widget_name = models.CharField(blank=True, null=True, max_length=100)
    widget_type = models.IntegerField(blank=True, null=True, max_length=25, choices = WIDGET_TYPES)
    widget_style = models.CharField(blank=True, null=True, max_length=25, choices = CHART_STYLES)
    widget_function = models.CharField(blank=True, null=True, max_length=150, choices = WIDGET_FUNCTIONS)
    widget_date_range = models.CharField(blank=True, null=True, max_length=50)
    widget_date_period = models.CharField(blank=True, null=True,max_length=50)
    data_columns = models.CharField(blank=True, null=True, max_length=250)
    headers = models.CharField(blank=True, null=True, max_length=250)
    Active = models.IntegerField(blank=True, null=True, default=0)
    def getDataTable(self, **args):
       from pywik import TableWidget
       from pywik import prep_date
       calc_date = prep_date(self.widget_date_range)
       access = TableWidget(auth = args['auth'], headers = args['headers'], data_columns = args['data_columns'])
       status, code, response = access(self.widget_function, date = calc_date, idSite = args['idSite'], period = 'day')
       widget = access.execute()
       html=""
       try:
           if (isinstance(widget['data'], type([]))) and (len(widget['data']) > 0):
               if isinstance(widget['data'][0],int):
                   html="""<table class="widget_table" border="0" cellspacing="0" cellpading="0"> """
                   for header in self.headers.split(","):
                      html+="""<th><div class="widget_table_headers">"""+str(header)+"""</div></th>"""
                   html+="""</tr></thead>"""
                   for index in range(len(widget['headers'])):
                      html+="""<tr>"""
                      html+="""<td>"""+unicode(widget['headers'][index])+"""</td>"""
                      html+="""<td>"""+unicode(widget['data'][index])+"""</td>"""
                      html+="""</tr>"""
                   html+="""</tbody>"""
                   html+="""</table>"""
               else:
                   html="""<table class="widget_table" border="0" cellspacing="0" cellpading="0"> """
                   html+="""<thead><tr>"""
                   for header in widget['headers']:
                      html+="""<th>"""+str(header)+"""</th>"""
                   html+="""</tr></thead>"""
                   html+="""<tbody>"""
                   counter=0
                   for row in widget['data']:
                      if (isinstance(row,type([]))) & (row != None):
                          html+="""<tr>"""
                          for field in row:
                              html+="""<td>"""+unicode(field)+"""</td>"""
                          html+="""</tr>"""
                      else:
                          if counter==0:
                              html+="""<tr>"""
                          html+="""<td>"""+unicode(row)+"""</td>"""
                          if counter==len(widget['data']):
                              html+="""</tr>"""
                          counter+=1
                      
                   html+="""</tbody>"""
                   html+="""</table>"""
       except:
           pass
       return html
       
    def getAqDataTable(self,request,chart_style,**args):
        module = __import__("AqWidgets")
        args['request']	= request
        widget_class_name,widget_method = self.widget_function.split("_")
        widget_class = getattr(module, widget_class_name)(**args)
        #if widget_method == "getOrgSalesReport":
        #data = getattr(widget_class,widget_method)(request=request, chart_style = chart_style, publisher_set = args["ids"])
        #else:    
        data = getattr(widget_class,widget_method)(request=request, chart_style = chart_style)
        return str(data)
       
    @staticmethod
    def prep(z):
        from atrinsic.web import openFlashChart
        widget_list = { 'types' : {}}
        for widget in z:
            w_type,w_function = widget.widget_function.split("_")
            if widget_list['types'].has_key(w_type):
                widget_list['types'][w_type].append({"function":widget.widget_name,"widget_id":widget.id, "widget_type":widget.widget_type})
            else:
                widget_list['types'][w_type] = []
                widget_list['types'][w_type].append({"function":widget.widget_name,"widget_id":widget.id})
        return widget_list
       
class UserAqWidget(models.Model):    
    organization = models.ForeignKey(Organization)
    widget = models.ForeignKey(AqWidget)
    page = models.CharField(blank=True, max_length=140)
    zone = models.IntegerField(blank=True, null=True)
    sort_order = models.IntegerField(blank=True, null=True)
    custom_style = models.CharField(blank=True, null=True, max_length=25, choices = CHART_STYLES)
    custom_columns = models.CharField(blank=True, null=True, max_length=300)
    custom_group = models.CharField(blank=True, null=True, max_length=50, default=0)
    custom_date_range = models.CharField(blank=True, null=True, max_length=50)
    @staticmethod
    def prep(x,request, ids):
       from atrinsic.web import openFlashChart
       from atrinsic.web.forms import WidgetSettingsForm
       from pywik import prep_date
       widgets = []
       """
       widgets = {
          'zone1':[],
          'zone2':[],
          'zone3':[],
          'zone4':[],
          'zone5':[],
       }"""

       for user_widget in x:
          my_widget = {}
          if ((user_widget.custom_style != None) & (user_widget.custom_style != '')):
             widget_style = user_widget.custom_style
          else:
             widget_style = user_widget.widget.widget_style
             
          if user_widget.custom_date_range != None:
              calc_date = user_widget.custom_date_range
              if calc_date.find(",") > 0:
                  my_widget['start_date'],my_widget['end_date'] = calc_date.split(",")
              else:
                  my_widget['start_date'] = ''
                  my_widget['end_date'] = ''
          elif (request.GET.has_key('start_date')) & (request.GET.has_key('end_date')):
              calc_date = str(request.GET['start_date'])+","+str(request.GET['end_date'])  
              my_widget['start_date'] = str(request.GET['start_date'])
              my_widget['end_date'] = str(request.GET['end_date'])
          elif (request.POST.has_key('start_date')) & (request.POST.has_key('end_date')):
              calc_date = str(request.POST['start_date'])+","+str(request.POST['end_date'])
              my_widget['start_date'] =str(request.POST['start_date'])
              my_widget['end_date'] = str(request.POST.has_key('end_date'))
          else:
              calc_date = prep_date(user_widget.widget.widget_date_range)
              if calc_date.find(",") > 0:
                  my_widget['start_date'],my_widget['end_date'] = calc_date.split(",")	
              else:
                  my_widget['start_date'] = ''
                  my_widget['end_date'] = ''
          try: 
              dstart = datetime.datetime.strptime(my_widget['start_date'],"%Y-%m-%d")
              dend = datetime.datetime.strptime(my_widget['end_date'],"%Y-%m-%d")
              my_widget['start_date'] = dstart.strftime('%m/%d/%Y')
              my_widget['end_date'] = dend.strftime('%m/%d/%Y')
          except:
              pass
          var_group_by = ''
          
          d = { }
          d['start_date'] = my_widget['start_date']
          d['end_date'] = my_widget['end_date']
          my_widget['widget_id'] = user_widget.id
          my_widget['header'] = user_widget.widget.widget_name
          
          if user_widget.custom_group != None:
            var_group_by = "|group_by="+str(user_widget.custom_group)
            d['group_data_by'] = user_widget.custom_group
          if user_widget.custom_columns != None:
            custom_columns = "|custom_columns="+str(user_widget.custom_columns)
            x,y = user_widget.custom_columns.split(",")
            d['variable1'] = x
            d['variable2'] = y
          else:
            custom_columns = ""
          if widget_style != 'table':
             if user_widget.widget.widget_type == 2:
                my_widget['html'] = openFlashChart.flashHTML('100%', '300', '/api/'+str(user_widget.widget.id)+'/'+str(widget_style)+'/?data=idSite='+str(request.organization.pywik_siteId)+'|date='+str(calc_date)+'|period=day', '/ofc/')
             else:
                my_widget['html'] = openFlashChart.flashHTML('100%', '300', '/api/'+str(user_widget.widget.id)+'/'+str(widget_style)+'/?data=date='+str(calc_date)+str(var_group_by)+str(custom_columns), '/ofc/')
          else:
             if user_widget.widget.widget_type == 2:
                var_headers = []
                if user_widget.widget.headers.find(',') > 0:
                    xx,yy=user_widget.widget.headers.split(',')
                    var_headers.append(xx)
                    var_headers.append(yy)
                else:
                    var_headers.append(user_widget.widget.headers)
                my_widget['html'] = user_widget.widget.getDataTable(auth=request.organization.pywik_token_auth_key, idSite=request.organization.pywik_siteId, period='day', date_range=calc_date, data_columns = user_widget.widget.data_columns.split(','), headers = var_headers)
             else:
                my_widget['html'] = user_widget.widget.getAqDataTable(request = request, date_range = calc_date, chart_style = widget_style,group_by=user_widget.custom_group, ids = ids,user_widget_id = user_widget.id, widget_id=user_widget.widget.id)
             my_widget['header'] = user_widget.widget.widget_name
          my_widget['form'] = WidgetSettingsForm(initial=d)
          widgets.append(my_widget)

       return widgets


class ProductList(models.Model):
    advertiser = models.ForeignKey('Organization')
    created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)
    url_id = models.IntegerField(blank=True,null=True)
    invite_id = models.IntegerField(blank=True,null=True)
    
    def get_product_url(self,datafeed, product_list, product_url, website):
        #################################################
        
        ''' Returns the tracking HTML for this Link ''' 
        import urllib
        from django.conf import settings
        from atrinsic.util.ApeApi import Ape
        print "%s with %s" % (datafeed.advertiser, datafeed.publisher)
        relationship = PublisherRelationship.objects.get(advertiser=datafeed.advertiser,publisher=datafeed.publisher)
        # below relationship = PublisherRelationship.objects.get(advertiser=self.advertiser,publisher=website.publisher)
        ptAction = ProgramTermAction.objects.select_related("action").filter(program_term=relationship.program_term_id)
        
        for pta in ptAction:
            #PublisherTracking.objects.get_or_create(advertiser = datafeed.advertiser, publisher = datafeed.publisher, program_term = relationship.program_term, website = website, ape_redirect_id = pta.action.ape_redirect_id, ape_url_id = product_list.url_id)
            pass
        websiteID = base36_encode(website.pk)
        ape_redirect = base36_encode(ptAction[0].action.ape_redirect_id)
        publisherID = base36_encode(website.publisher_id)
        ape_url = product_list.url_id

        track_click_url = settings.APE_TRACKER_URL + ape_redirect + "/" + str(publisherID) + "/" + str(websiteID) + "/?url_id=" + str(ape_url) + "&url=" + urllib.quote(product_url,"")
        return track_click_url
        
        #################################################
        
        
        """
        import urllib
        track_click_url = settings.INVITE_CLICK_TRACKER_HOST + "track_click?igCode=%s&partnerID=%s&crID=%s&campID=%s&redirectURL=%s" % (website.id,settings.INVITE_PARTNER_ID,self.invite_id,self.advertiser.invite_campid,urllib.quote(product_url,""))
        return track_click_url
        """

class ProductItem(models.Model):
    product_list = models.ForeignKey(ProductList)
    
    name = models.CharField(max_length=160)
    keywords = models.CharField(max_length=300)
    description = models.TextField()
    sku = models.CharField(max_length=100,null=True,blank=True)
    buyurl = models.CharField(max_length=500)
    available = models.CharField(max_length=3)
    imageurl = models.CharField(max_length=300,null=True,blank=True)
    price = models.DecimalField(max_digits=10,decimal_places=2,default='0.00')
    retailprice = models.DecimalField(max_digits=10,decimal_places=2,default='0.00',null=True)
    saleprice = models.DecimalField(max_digits=10,decimal_places=2,default='0.00',null=True)
    currency = models.CharField(max_length=3,null=True,blank=True)
    upc = models.CharField(max_length=100,null=True,blank=True)
    promotionaltext = models.CharField(max_length=300,null=True,blank=True)
    advertisercategory = models.CharField(max_length=300,null=True,blank=True)
    manufacturer = models.CharField(max_length=160,null=True,blank=True)
    manufacturerid = models.CharField(max_length=64,null=True,blank=True)
    isbn = models.CharField(max_length=64,null=True,blank=True)
    author = models.CharField(max_length=130,null=True,blank=True)
    artist = models.CharField(max_length=130,null=True,blank=True)
    publisher = models.CharField(max_length=130,null=True,blank=True)
    title = models.CharField(max_length=130,null=True,blank=True)
    label = models.CharField(max_length=130,null=True,blank=True)
    format = models.CharField(max_length=64,null=True,blank=True)
    special = models.CharField(max_length=3,null=True,blank=True)
    gift = models.CharField(max_length=3,null=True,blank=True)
    thirdpartyid = models.CharField(max_length=64,null=True,blank=True)
    thirdpartycategory = models.CharField(max_length=300,null=True,blank=True)
    offline = models.CharField(max_length=3,null=True,blank=True)
    online = models.CharField(max_length=3,null=True,blank=True)
    fromprice = models.CharField(max_length=3,null=True,blank=True)
    startdate = models.CharField(max_length=64,null=True,blank=True)
    enddate = models.CharField(max_length=64,null=True,blank=True)
    instock = models.CharField(max_length=3,null=True,blank=True)
    condition = models.CharField(max_length=11,null=True,blank=True)
    warranty = models.CharField(max_length=300,null=True,blank=True)
    standardshippingcost = models.DecimalField(max_digits=10,decimal_places=2,default='0.00',null=True)
    merchandisetype = models.CharField(max_length=100,null=True,blank=True)

    sku_list = models.CharField(max_length=100,null=True,blank=True)
    sku_commission_level = models.DecimalField(max_digits=10,decimal_places=2,default='0.00',null=True)
    sales_rank = models.PositiveIntegerField(default=1)


class PublisherApplication(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    
    validation_code = models.CharField(max_length=10)
    
    email = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

    def set_password(self,raw_password):
        """ copied from User model in django.contrib.auth.models. """
        from django.contrib.auth.models import get_hexdigest
        import random
        algo = 'sha1'
        salt = get_hexdigest(algo, str(random.random()), str(random.random()))[:5]
        hsh = get_hexdigest(algo, salt, raw_password)
        self.password = '%s$%s$%s' % (algo, salt, hsh)
       
class TermsCopy(models.Model):
    text_copy = models.TextField(blank=True)

class Terms_Accepted_Log(models.Model):
    name = models.CharField(blank=True, max_length=100)
    ip = models.IPAddressField(blank=True, null=True)
    term = models.ForeignKey(TermsCopy)
    date_in = models.DateField(default=datetime.datetime.today)
    organization = models.ForeignKey(Organization,blank=True, null=True)

class Countries(models.Model):
    abreviation = models.CharField(blank=True, max_length=2)
    name = models.CharField(blank=True, max_length=125)

class States(models.Model):
    abreviation = models.CharField(blank=True, max_length=2)
    name = models.CharField(blank=True, max_length=125)


class Organization_Status(models.Model):
    organization = models.ForeignKey('Organization',blank=True, null=True)
    message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    
class Organization_Followers(models.Model):
    stalker = models.ForeignKey('Organization',blank=True, null=True, related_name='the organisation following')
    followed = models.ForeignKey('Organization',blank=True, null=True, related_name='the one posting the news')
    created = models.DateTimeField(auto_now_add=True)
    
    def code(self):
        return followed;

    
class Organization_FilterTypes(models.Model):
    organization = models.ForeignKey('Organization',blank=False, null=False)
    filterchoice = models.IntegerField(blank=False, null=False)
    created = models.DateTimeField(auto_now_add=True)

class Organization_IO(models.Model):
    '''This Model represents Insertion orders per organization'''
    
    organization = models.ForeignKey("Organization")
    ace_id = models.IntegerField(blank=False,null=False)    
    ace_ioid = models.IntegerField(blank=False,null=False)  
    ace_iosymbol = models.CharField(blank=True, max_length=20)
    salesrep = models.PositiveIntegerField(default=0)
        
    transaction_fee_type = models.PositiveIntegerField(choices=TRANSACTION_FEE_TYPE_CHOICES,default=TRANSACTION_FEE_TYPE_REVSHARE)
    transaction_fee_amount = models.DecimalField(max_digits=10,decimal_places=2,default='0.00')
    
class Notifications(models.Model):
    """Used to keep track of what notification was removed and shouldnt be shown again."""
    original_id = models.IntegerField(blank=False, null=False)
    notification_type = models.CharField(blank=False, max_length=20)
    date_deleted = models.DateTimeField(default=datetime.datetime.today)
    organization = models.ForeignKey("Organization")
    def __unicode__(self):
        return u"Notification"

class PublisherTracking(models.Model):
    link = models.ForeignKey('Link')
    creative_id = models.IntegerField(null=True,default=0)
    website = models.ForeignKey('Website')
    advertiser = models.ForeignKey('Organization',related_name="advertiser_tracking")
    publisher = models.ForeignKey('Organization',related_name="publisher_tracking")
    program_term = models.ForeignKey('ProgramTerm')
    create_date = models.DateTimeField(default=datetime.datetime.today)
    ape_redirect_id = models.IntegerField(blank=True, null=True)
    ape_url_id = models.IntegerField(blank=True, null=True)

class PiggybackPixel(models.Model):
    publisher = models.ForeignKey('Organization')
    advertiser = models.ForeignKey('Organization', related_name="advertiser")
    #type = models.ForeignKey('Organization') #TODO Change to choice field 
    pixel_type = models.PositiveIntegerField(choices=PIXEL_TYPE_CHOICES,default=PIXEL_TYPE_IMAGE)  
    ape_redirect_id = models.IntegerField(blank=True, null=True) 
    ape_content_pixel_id = models.IntegerField(blank=True, null=True)    
    ape_include_pixel_id = models.IntegerField(blank=True, null=True)    
    jsinclude = models.CharField(max_length=250,null=True,blank=True)  
    content = models.TextField(blank=False, null=False)
    create_date = models.DateTimeField(default=datetime.datetime.today)

class KenshooIntegration(models.Model):
    publisher = models.ForeignKey('Organization')
    advertiser = models.ForeignKey('Organization', related_name="publisher_kenshoo_integration")
    pixel_type = models.PositiveIntegerField(choices=PIXEL_TYPE_CHOICES,default=PIXEL_TYPE_IMAGE)
    ape_redirect_id = models.IntegerField(blank=True, null=True)
    ape_content_pixel_id = models.IntegerField(blank=True, null=True)
    ape_include_pixel_id = models.IntegerField(blank=True, null=True) 
    content = models.CharField(max_length=250,null=True,blank=True)
    create_date = models.DateTimeField(default=datetime.datetime.today)

class KenshooDataFeed_Orders(models.Model):
    datein = models.DateTimeField(blank=True, null=True)
    redirect_id = models.IntegerField(blank=True, null=True)
    advertiser_id = models.IntegerField(blank=True, null=True)
    publisher_id = models.IntegerField(blank=True, null=True)
    website_id = models.IntegerField(blank=True, null=True)
    url_id = models.IntegerField(blank=True, null=True)
    order_id = models.IntegerField(blank=True, null=True)
    amount = models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=2) 
    currency = models.CharField(max_length=3,null=True,blank=True)
    import_id = models.IntegerField(blank=True, null=True)

"""
class KenshooAdvertiserIntegration(models.Model):
    advertiser = models.ForeignKey('Organization', related_name="transfer_id")
    token_id = models.IntegerField(blank=True, null=True)
    integration_type = models.PositiveIntegerField(choices=PIXEL_TYPE_CHOICES,default=PIXEL_TYPE_IMAGE)
    format = models.PositiveIntegerField('Format', default=KENSHOO_FORMAT_CSV, choices=KENSHOO_FORMAT_CHOICES,null=False,blank=False)
"""                     
class W9Status(models.Model):
    organization = models.OneToOneField('Organization')
    status = models.PositiveIntegerField(choices=W9_STATUS_CHOICES)
    filename = models.CharField(max_length=250,null=True,blank=True)  
    datereceived = models.DateTimeField()

class Offline_Leads(models.Model):
    datein = models.DateTimeField(blank=True, null=True)
    redirect_id = models.IntegerField(blank=True, null=True)
    publisher_id = models.IntegerField(blank=True, null=True)
    advertiser_id = models.IntegerField(blank=True, null=True)
    website_id = models.IntegerField(blank=True, null=True)
    url_id = models.IntegerField(blank=True, null=True)
    total_amount = models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=2)
    total_orders = models.IntegerField(blank=True, null=True)
    currency = models.CharField(max_length=3,null=True,blank=True)

class Report_Adv_Pub(models.Model):
    report_date = models.DateTimeField(blank=True, null=True)
    advertiser = models.ForeignKey(Organization,related_name = 'advertiser1')
    advertiser_name = models.CharField(blank=True, null=True, max_length=255)
    publisher = models.ForeignKey(Organization,related_name = 'publisher1')
    publisher_name = models.CharField(blank=True, null=True, max_length=255)
    impressions = models.IntegerField(blank=True, null=True)
    clicks = models.IntegerField(blank=True, null=True)
    new_impressions = models.IntegerField(blank=True, null=True)
    leads = models.IntegerField(blank=True, null=True)
    orders = models.IntegerField(blank=True, null=True)
    amount = models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=2)
    publisher_commission = models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=2)
    network_fee= models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=2)
    relationship_status = models.IntegerField(blank=True, null=True)

class Report_Link(models.Model):
    report_date = models.DateTimeField(blank=True, null=True)
    advertiser = models.ForeignKey(Organization,related_name = 'advertiser2')
    advertiser_name = models.CharField(blank=True, null=True, max_length=255)
    publisher = models.ForeignKey(Organization,related_name = 'publisher2')
    publisher_name = models.CharField(blank=True, null=True, max_length=255)
    impressions = models.IntegerField(blank=True, null=True)
    clicks = models.IntegerField(blank=True, null=True)
    new_impressions = models.IntegerField(blank=True, null=True)
    leads = models.IntegerField(blank=True, null=True)
    orders = models.IntegerField(blank=True, null=True)
    amount = models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=2)
    promotion_type = models.CharField(blank=True, null=True, max_length=255)
    creative = models.ForeignKey(Link)
    creative_size = models.CharField(blank=True, null=True, max_length=255)
    publisher_commission = models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=2)
    network_fee= models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=2)
    relationship_status = models.IntegerField(blank=True, null=True)

class Report_OrderDetail(models.Model):
    report_date = models.DateTimeField(blank=True, null=True)
    advertiser = models.ForeignKey(Organization,related_name = 'advertiser3')
    advertiser_name = models.CharField(blank=True, null=True, max_length=255)
    publisher = models.ForeignKey(Organization,related_name = 'publisher3')
    publisher_name = models.CharField(blank=True, null=True, max_length=255)
    order_id = models.IntegerField(blank=True, null=True)
    product_sku = models.IntegerField(blank=True, null=True)
    product_name = models.IntegerField(blank=True, null=True)
    product_quantity = models.IntegerField(blank=True, null=True)
    product_price = models.IntegerField(blank=True, null=True)
    publisher_commission = models.IntegerField(blank=True, null=True)
    impressions = models.IntegerField(blank=True, null=True)
    clicks = models.IntegerField(blank=True, null=True)
    new_impressions = models.IntegerField(blank=True, null=True)
    leads = models.IntegerField(blank=True, null=True)
    orders = models.IntegerField(blank=True, null=True)
    amount = models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=2)
    network_fee = models.DecimalField(max_digits=19, decimal_places=2)
    relationship_status = models.IntegerField(blank=True, null=True)

class Report_OrderDetail_UpdateLog(models.Model):
    report_date = models.DateTimeField(blank=True, null=True)
    modified = models.DateTimeField(blank=True, null=True)
    advertiser = models.ForeignKey(Organization,related_name = 'advertiser4')
    advertiser_name = models.CharField(blank=True, null=True, max_length=255)
    publisher = models.ForeignKey(Organization,related_name = 'publisher4')
    publisher_name = models.CharField(blank=True, null=True, max_length=255)
    order_id = models.CharField(blank=True, null=True, max_length=255)
    product_sku = models.CharField(blank=True, null=True, max_length=255)
    product_name = models.CharField(blank=True, null=True, max_length=255)
    product_quantity = models.IntegerField(blank=True, null=True)
    product_price = models.CharField(blank=True, null=True, max_length=255)
    publisher_commission = models.CharField(blank=True, null=True, max_length=255)
    impressions = models.IntegerField(blank=True, null=True)
    clicks = models.IntegerField(blank=True, null=True)
    new_impressions = models.IntegerField(blank=True, null=True)
    leads = models.IntegerField(blank=True, null=True)
    orders = models.IntegerField(blank=True, null=True)
    amount = models.CharField(blank=True, null=True, max_length=255)
    network_fee = models.CharField(blank=True, null=True, max_length=255)
    relationship_status = models.IntegerField(blank=True, null=True)
    order_cancelled = models.BooleanField(default=False)
    def save(self, force_insert=False, force_update=True):
        self.modified = datetime.datetime.now()
        super(Report_OrderDetail_UpdateLog, self).save()

class Ace_SalesPeople(models.Model):
    sales_person_id = models.IntegerField(blank=False, null=False)
    sales_person_name = models.CharField(blank=False, null=False, max_length=255)

#####################################################################################
############################# Commission Junction Models ############################

class CJ_Mapping(models.Model):
    cj_pid = models.IntegerField(blank=False, null=False)
    publisher = models.ForeignKey(Organization, related_name="Publisher", null=True, blank=True)
    date_created = models.DateField(default=datetime.datetime.today, blank=False, null=False)
    date_assigned = models.DateField(blank=True, null=True)
    verified = models.BooleanField(default=False)

#####################################################################################
############################## Google Analytics Models ##############################    
class GA_Account(models.Model):
    organization = models.ForeignKey(Organization, related_name="org")
    email = models.EmailField(blank=False, max_length=100)
    password = models.CharField(blank=False, max_length=16)
    is_active = models.BooleanField(default=True)
    created = models.DateField(default=datetime.datetime.today)
    def __unicode__(self):
        return self.organization.name
    
    def get_connection(self):
        from googleanalytics import Connection
        """googleanalytics Connection using the specified account credentials"""
        return Connection(self.email, self.password)
    
    def get_ga_sites(self, profile_id = None):
        """retrieve all google analytics sites available for this account. Profile_id is present, retrieve it."""
        if(self.is_active):
            connection = self.get_connection()
            sites = connection.get_accounts() 
            
            if(profile_id != None):
                for site in sites:
                    if(site.profile_id == profile_id):
                        return site
            return sites
    
    def get_sites(self):
        """retrieve all sites setup for this account"""
        return GA_Site.objects.filter(account = self) or None
    

class GA_Category(models.Model):
    name = models.CharField(blank=False, max_length=128)
    is_active = models.BooleanField(default=True)
    create = models.DateField(default=datetime.datetime.today)
    def __unicode__(self):
        return self.name
    
    def metrics(self):
        """All metrics in current category"""
        return GA_Metric.objects.filter(category = self)
    
    def dimensions(self):
        """All dimensions in current category"""
        return GA_Dimension.objects.filter(category = self)
    

class GA_Metric(models.Model):
    name = models.CharField(blank=False, max_length=128)
    description = models.CharField(null=True, max_length=256)
    category = models.ForeignKey(GA_Category)
    attribute = models.CharField(blank=False, max_length=128)
    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ['attribute']
    

class GA_Dimension(models.Model):
    name = models.CharField(blank=False, max_length=128)
    description = models.CharField(null=True, max_length=256)
    category = models.ForeignKey(GA_Category)    
    attribute = models.CharField(blank=False, max_length=128)
    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ['attribute']
    

class GA_Site(models.Model):
    account = models.ForeignKey(GA_Account)
    name = models.CharField(blank=False, max_length=128)
    profile_id = models.IntegerField(blank=False)
    is_active = models.BooleanField(default=True)
    created = models.DateField(default=datetime.datetime.today)

    objects = GA_SiteManager()

    def __unicode__(self):
        return self.name
    
    def get_site(self):
        connection = self.account.get_connection()
        return connection.get_account(str(self.profile_id)) or None
        
class GA_Report(models.Model):
    name = models.CharField(blank=False, max_length=128)
    description = models.CharField(null=True, max_length=256)
    
    category = models.ForeignKey(GA_Category)
    site = models.ForeignKey(GA_Site)
    metric = models.ManyToManyField(GA_Metric, related_name='metric')
    dimension = models.ManyToManyField(GA_Dimension, related_name='dimension')
    
    is_active = models.BooleanField(default=True)
    created = models.DateField(default=datetime.datetime.today)
    
    def __unicode__(self):
        return self.name
        
    def get_dimensions(self):
        """Dimensions used for current report, Array"""
        return [str(dimension['attribute']) for dimension in self.dimension.values()]
        
    def get_dimensions_byTier(self, tier):
        """Dimensions used for current report, Array"""
        counter = 0
        trackDimensions = []
        for dimension in self.dimension.values():
            print "Counter = %s, Tier = %s" % (counter, tier)
            print str(dimension['attribute'])
            trackDimensions.append(str(dimension['attribute']))
            if counter == int(tier):
                break
            counter += 1
        return trackDimensions        
        #    print self.dimension[x + 1]
        #return [str(dimension['attribute']) for dimension in self.dimension.values()]
        
    def get_metrics(self):
        """Metrics used for current report, Array"""
        return [str(metric['attribute']) for metric in self.metric.values()]
    
    def get_report(self, start_date, end_date, tier, tier_filters, max_results=0):
        """Generate a report using the specified site, start_date and end_date"""
        ga_interface = self.site.get_site()

        useFilter = []
        if tier_filters != None:
            filters = tier_filters.split("|")
            # Create List of Lists, ** non-mutable
            useFilter = [None]*len(filters)
            for i in range(len(filters)):
                useFilter[i] = []
                
            for f in range(len(filters)):
                fName,fExpression = filters[f].split(":")
                useFilter[f].append("%s" % fName)
                useFilter[f].append("==")
                useFilter[f].append("%s" % fExpression)  
                print useFilter[f]
                
            #if tier > 0 and tier_filter != "":
            #    useFilter[0].append("%s" % self.get_dimensions_byTier(tier)[int(tier) - 1])
            #    useFilter[0].append("==")
            #    useFilter[0].append("%s" % tier_filter)  
    
        print "FILTERS---%s" % useFilter
        print "Dimensions:%s" % self.get_dimensions_byTier(tier)
        ga_data = ga_interface.get_data(start_date=start_date, end_date=end_date, dimensions=self.get_dimensions_byTier(tier), metrics=self.get_metrics(), filters=useFilter, max_results=max_results)
        return ga_data 
#####################################################################################    
class Users(models.Model):
        
    from atrinsic.base.models import Organization    
        
    email = models.EmailField(blank=False, max_length=100)
    password = models.CharField(blank=False, max_length=16)
    date_joined = models.DateField(default=datetime.datetime.today)
    last_login = models.DateField(default=datetime.datetime.today)
    organization = models.ForeignKey(Organization)
##########################################################################################################################      
class MailDotComAddress(models.Model):
    domainname = models.CharField(blank=False, max_length=100)
    date_found = models.DateField(default=datetime.datetime.today)
    
    
class Payout_Approval_Log(models.Model):
    '''This model represents relationships between Publisher and Advertiser Organizations'''

    advertiser = models.ForeignKey("Organization",related_name="advertiser_payoutlog")
    advertiser_ace_id = models.IntegerField(blank=True,null=True)
    publisher = models.ForeignKey("Organization",related_name="publisher_payoutlog")
    publisher_ace_id = models.IntegerField(blank=True,null=True)
    program_term = models.ForeignKey('ProgramTerm',blank=True,null=True)
    report_date = models.DateTimeField(blank=False, null=False)
    datein = models.DateTimeField(auto_now_add=True)
          